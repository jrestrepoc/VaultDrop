from abc import ABC, abstractmethod


class IBilleteraRepository(ABC):
    @abstractmethod
    def create_for_user(self, user, saldo):
        pass

    @abstractmethod
    def get_by_user(self, user):
        pass


class DjangoBilleteraRepository(IBilleteraRepository):
    def __init__(self, billetera_model):
        self.model = billetera_model

    def create_for_user(self, user, saldo):
        return self.model.objects.create(user=user, saldo=saldo)

    def get_by_user(self, user):
        try:
            return self.model.objects.get(user=user)
        except self.model.DoesNotExist:
            return None
