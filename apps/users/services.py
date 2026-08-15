from django.db import transaction, IntegrityError
from django.contrib.auth import get_user_model
from decimal import Decimal

from apps.wallet.services import WalletService
from apps.users.domain.builders import UserBuilder
from apps.users.infra.factories import NotificadorFactory


class UserService:
    def __init__(self, user_repository=None, wallet_service=None, notificador=None):
        self.user_model = get_user_model()
        self.user_repository = user_repository or None
        self.wallet_service = wallet_service or WalletService()
        self.notificador = notificador or NotificadorFactory.crear()

    def register(self, username, email, password, initial_credit=Decimal('1000.00')):
        if self.user_model.objects.filter(username=username).exists():
            raise ValueError('El nombre de usuario ya está en uso')
        if self.user_model.objects.filter(email=email).exists():
            raise ValueError('El correo ya está registrado')

        try:
            with transaction.atomic():
                user = (
                    UserBuilder(self.user_model)
                    .con_username(username)
                    .con_email(email)
                    .con_password(password)
                    .build()
                )
                user.save()
                self.wallet_service.create_initial_wallet(user, initial_credit)
                self.notificador.enviar_bienvenida(user)
        except IntegrityError:
            # Red de seguridad ante condiciones de carrera: dos registros
            # concurrentes con el mismo username/email pasan las validaciones
            # de arriba y solo chocan al guardar. Se traduce a un error de
            # negocio legible en vez de dejar propagar el 500 de la BD.
            raise ValueError('El nombre de usuario o el correo ya están registrados')
        return user
