from decimal import Decimal, InvalidOperation
from django.core.cache import cache
from django.db import transaction
from django.utils.translation import gettext as _
from apps.core.domain import BusinessError, ExternalServiceError, InsufficientBalanceError, NotFoundError
from apps.wallet.infra.exchange_rates import ExchangeRateApiAdapter
from apps.wallet.repositories import DjangoBilleteraRepository

SIN_TASA = 'no-disponible'


class CotizacionService:
    def __init__(self, proveedor=None):
        self.proveedor = proveedor or ExchangeRateApiAdapter()

    def tasa(self, moneda):
        # shortcut: la cache es por proceso, cada worker consulta la API una vez por hora; pasar a Redis si crecen los workers.
        clave = f'tasa-usd-{moneda}'
        guardada = cache.get(clave)
        if guardada == SIN_TASA:
            raise ExternalServiceError(_('No se pudo consultar la tasa de cambio.'))
        if guardada is not None:
            return guardada
        try:
            tasa = self.proveedor.obtener_tasa(moneda)
        except ExternalServiceError:
            # Evita que cada pagina espere el timeout mientras la API siga caida.
            cache.set(clave, SIN_TASA, 60)
            raise
        cache.set(clave, tasa, 3600)
        return tasa


def positive_amount(value):
    try:
        amount = Decimal(str(value))
        if not amount.is_finite() or amount <= 0 or amount > Decimal('9999999999.99'):
            raise BusinessError(_('El monto debe ser positivo y estar dentro del límite permitido.'))
        if amount != amount.quantize(Decimal('0.01')):
            raise BusinessError(_('El monto admite como máximo dos decimales.'))
        return amount
    except (InvalidOperation, TypeError) as exc:
        raise BusinessError(_('Monto inválido.')) from exc

class WalletService:
    def __init__(self, billetera_repository=None):
        self.billetera_repository = billetera_repository or DjangoBilleteraRepository()

    def create_initial_wallet(self, user, amount: Decimal):
        amount = positive_amount(amount)
        with transaction.atomic():
            wallet = self.billetera_repository.create_for_user(user, amount)
            self.billetera_repository.record(wallet, 'INICIAL', amount, Decimal('0.00'))
            return wallet

    def acreditar(self, user, monto, tipo='RECARGA'):
        monto = positive_amount(monto)
        with transaction.atomic():
            wallet = self.billetera_repository.adjust(user, monto)
            if wallet is None:
                raise BusinessError(_('No se pudo acreditar: billetera inexistente o límite de saldo alcanzado.'))
            self.billetera_repository.record(wallet, tipo, monto, wallet.saldo - monto)
            return wallet

    def debitar(self, user, monto):
        monto = positive_amount(monto)
        with transaction.atomic():
            wallet = self.billetera_repository.adjust(user, -monto)
            if wallet is None:
                raise InsufficientBalanceError(_('Saldo insuficiente'))
            self.billetera_repository.record(wallet, 'DEBITO', monto, wallet.saldo + monto)
            return wallet

    def get_billetera(self, user):
        wallet = self.billetera_repository.get_by_user(user)
        if wallet is None:
            raise NotFoundError(_('El usuario no posee una billetera activa'))
        return wallet
