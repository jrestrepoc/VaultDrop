from abc import ABC, abstractmethod


class IUserRepository(ABC):
    @abstractmethod
    def create(self, **kwargs):
        pass

    @abstractmethod
    def get_by_email(self, email):
        pass

    @abstractmethod
    def get_by_username(self, username):
        pass

    @abstractmethod
    def exists_by_username(self, username: str) -> bool:
        pass

    @abstractmethod
    def exists_by_email(self, email: str) -> bool:
        pass


class DjangoUserRepository(IUserRepository):
    def __init__(self, user_model):
        self.user_model = user_model

    def create(self, **kwargs):
        return self.user_model.objects.create(**kwargs)

    def get_by_email(self, email):
        try:
            return self.user_model.objects.get(email=email)
        except self.user_model.DoesNotExist:
            return None

    def get_by_username(self, username):
        try:
            return self.user_model.objects.get(username=username)
        except self.user_model.DoesNotExist:
            return None

    def exists_by_username(self, username: str) -> bool:
        return self.user_model.objects.filter(username=username).exists()

    def exists_by_email(self, email: str) -> bool:
        return self.user_model.objects.filter(email=email).exists()

