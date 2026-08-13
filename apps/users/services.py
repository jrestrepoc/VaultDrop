from django.db import transaction
from django.contrib.auth import get_user_model
from decimal import Decimal

from apps.wallet.services import WalletService


class UserService:
    def __init__(self, user_repository=None, wallet_service=None):
        self.user_model = get_user_model()
        self.user_repository = user_repository or None
        self.wallet_service = wallet_service or WalletService()

    def register(self, username, email, password, initial_credit=Decimal('1000.00')):
        if len(password) < 8:
            raise ValueError('La contraseña debe tener al menos 8 caracteres')
        if self.user_model.objects.filter(email=email).exists():
            raise ValueError('El correo ya está registrado')

        with transaction.atomic():
            user = self.user_model.objects.create_user(username=username, email=email, password=password)
            user.is_active = True
            user.save()
            self.wallet_service.create_initial_wallet(user, initial_credit)
        return user
