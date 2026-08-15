from django.db import transaction
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
        if self.user_model.objects.filter(email=email).exists():
            raise ValueError('El correo ya está registrado')

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
        return user
