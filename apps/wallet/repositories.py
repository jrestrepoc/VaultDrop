from abc import ABC, abstractmethod
from decimal import Decimal
from django.db.models import F
from apps.wallet.models import Billetera, Transaccion

class IBilleteraRepository(ABC):
    @abstractmethod
    def create_for_user(self, user, saldo): ...

    @abstractmethod
    def get_by_user(self, user): ...

    @abstractmethod
    def adjust(self, user, delta): ...

    @abstractmethod
    def record(self, wallet, kind, amount, previous): ...

class DjangoBilleteraRepository(IBilleteraRepository):
    def __init__(self, billetera_model=Billetera):
        self.model = billetera_model

    def create_for_user(self, user, saldo):
        return self.model.objects.create(user=user, saldo=saldo)

    def get_by_user(self, user):
        return self.model.objects.filter(user=user).first()

    def adjust(self, user, delta):
        query = self.model.objects.filter(user=user)
        if delta < 0:
            query = query.filter(saldo__gte=-delta)
        else:
            query = query.filter(saldo__lte=Decimal('9999999999.99') - delta)
        changed = query.update(saldo=F('saldo') + delta)
        return self.get_by_user(user) if changed else None

    def record(self, wallet, kind, amount, previous):
        return Transaccion.objects.create(billetera=wallet, tipo=kind, monto=amount,
                                         saldo_anterior=previous, saldo_posterior=wallet.saldo)
