from decimal import Decimal
from django.db import transaction
from django.contrib.auth import get_user_model

from apps.wallet.repositories import DjangoBilleteraRepository
from apps.wallet.models import Billetera, Transaccion


class WalletService:
    def __init__(self, billetera_repository=None):
        self.billetera_repository = billetera_repository or DjangoBilleteraRepository(Billetera)

    def create_initial_wallet(self, user, amount: Decimal):
        with transaction.atomic():
            saldo_anterior = Decimal('0.00')
            billetera = self.billetera_repository.create_for_user(user, amount)
            Transaccion.objects.create(
                billetera=billetera,
                tipo='INICIAL',
                monto=amount,
                saldo_anterior=saldo_anterior,
                saldo_posterior=amount,
            )
            return billetera

    def acreditar(self, user, monto: Decimal):
        with transaction.atomic():
            billetera = self.billetera_repository.get_by_user(user)
            saldo_anterior = billetera.saldo
            billetera.saldo += monto
            billetera.save()
            Transaccion.objects.create(
                billetera=billetera,
                tipo='RECARGA',
                monto=monto,
                saldo_anterior=saldo_anterior,
                saldo_posterior=billetera.saldo,
            )
            return billetera

    def tiene_saldo_suficiente(self, user, monto: Decimal):
        billetera = self.billetera_repository.get_by_user(user)
        return billetera.saldo >= monto

    def debitar(self, user, monto: Decimal):
        with transaction.atomic():
            billetera = self.billetera_repository.get_by_user(user)
            if billetera.saldo < monto:
                raise ValueError('Saldo insuficiente')
            saldo_anterior = billetera.saldo
            billetera.saldo -= monto
            billetera.save()
            Transaccion.objects.create(
                billetera=billetera,
                tipo='DEBITO',
                monto=monto,
                saldo_anterior=saldo_anterior,
                saldo_posterior=billetera.saldo,
            )
            return billetera
