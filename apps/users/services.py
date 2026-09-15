from django.db import transaction, IntegrityError
from apps.core.domain import ConflictError
from django.contrib.auth import get_user_model
from decimal import Decimal

from apps.wallet.services import WalletService
from apps.users.domain.builders import UserBuilder
from apps.users.infra.factories import NotificadorFactory
from apps.users.repositories import DjangoUserRepository


class UserService:
    def __init__(self, user_repository=None, wallet_service=None, notificador=None):
        self.user_model = get_user_model()
        self.user_repository = user_repository or DjangoUserRepository(self.user_model)
        self.wallet_service = wallet_service or WalletService()
        self.notificador = notificador or NotificadorFactory.crear()

    def register(self, username, email, password, initial_credit=Decimal('1000.00')):
        if self.user_repository.exists_by_username(username):
            raise ConflictError('El nombre de usuario ya está en uso')
        if self.user_repository.exists_by_email(email):
            raise ConflictError('El correo ya está registrado')

        try:
            with transaction.atomic():
                user = (
                    UserBuilder(self.user_model)
                    .con_username(username)
                    .con_email(email)
                    .con_password(password)
                    .build()
                )
                self.user_repository.save(user)
                self.wallet_service.create_initial_wallet(user, initial_credit)
                transaction.on_commit(lambda: self.notificador.enviar_bienvenida(user), robust=True)
        except IntegrityError:
            # Red de seguridad ante condiciones de carrera: dos registros
            # concurrentes con el mismo username/email pasan las validaciones
            # de arriba y solo chocan al guardar. Se traduce a un error de
            # negocio legible en vez de dejar propagar el 500 de la BD.
            raise ConflictError('El nombre de usuario o el correo ya están registrados')
        return user

    def update_profile(self, user, username, email, steam_username=''):
        username_owner = self.user_repository.get_by_username(username)
        email_owner = self.user_repository.get_by_email(email)
        if (username_owner and username_owner.pk != user.pk) or (email_owner and email_owner.pk != user.pk):
            raise ConflictError('El nombre de usuario o el correo ya están registrados')
        try:
            with transaction.atomic():
                return self.user_repository.update_profile(user, username, email, steam_username)
        except IntegrityError as exc:
            raise ConflictError('El nombre de usuario o el correo ya están registrados') from exc
