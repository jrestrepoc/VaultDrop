from decimal import Decimal, InvalidOperation
from django.db import transaction
from apps.core.domain import BusinessError, InsufficientBalanceError, NotFoundError
from apps.wallet.repositories import DjangoBilleteraRepository

def positive_amount(value):
    try:
        amount = Decimal(str(value))
        if not amount.is_finite() or amount <= 0 or amount > Decimal('9999999999.99'):
            raise BusinessError('El monto debe ser positivo y estar dentro del límite permitido.')
        if amount != amount.quantize(Decimal('0.01')):
            raise BusinessError('El monto admite como máximo dos decimales.')
        return amount
    except (InvalidOperation, TypeError) as exc:
        raise BusinessError('Monto inválido.') from exc

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
                raise BusinessError('No se pudo acreditar: billetera inexistente o límite de saldo alcanzado.')
            self.billetera_repository.record(wallet, tipo, monto, wallet.saldo - monto)
            return wallet

    def debitar(self, user, monto):
        monto = positive_amount(monto)
        with transaction.atomic():
            wallet = self.billetera_repository.adjust(user, -monto)
            if wallet is None:
                raise InsufficientBalanceError('Saldo insuficiente')
            self.billetera_repository.record(wallet, 'DEBITO', monto, wallet.saldo + monto)
            return wallet

    def tiene_saldo_suficiente(self, user, monto):
        return self.get_billetera(user).saldo >= positive_amount(monto)

    def get_billetera(self, user):
        wallet = self.billetera_repository.get_by_user(user)
        if wallet is None:
            raise NotFoundError('El usuario no posee una billetera activa')
        return wallet
