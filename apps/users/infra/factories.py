import logging
import os
from abc import ABC, abstractmethod

from django.core.mail import send_mail

logger = logging.getLogger(__name__)


class INotificador(ABC):
    @abstractmethod
    def enviar_bienvenida(self, user):
        pass


class NotificadorConsola(INotificador):
    """Modo MOCK: no depende de servicios externos. Ideal para desarrollo y tests."""

    def enviar_bienvenida(self, user):
        mensaje = f"[MOCK] Bienvenido/a {user.username}, tu billetera inicial ya está lista."
        logger.info(mensaje)
        print(mensaje)


class NotificadorEmail(INotificador):
    """Modo REAL: envía un correo real usando django.core.mail.send_mail."""

    def enviar_bienvenida(self, user):
        send_mail(
            subject='¡Bienvenido/a a VaultDrop!',
            message=(
                f'Hola {user.username}, tu cuenta fue creada exitosamente '
                'y tu billetera inicial ya está disponible.'
            ),
            from_email=None,
            recipient_list=[user.email],
            fail_silently=True,
        )


class NotificadorFactory:
    """Factory que decide, según la variable de entorno NOTIFICACION_MODE,
    qué implementación de INotificador instanciar (MOCK vs REAL)."""

    @staticmethod
    def crear(modo=None):
        modo = (modo or os.environ.get('NOTIFICACION_MODE', 'MOCK')).upper()
        if modo == 'REAL':
            return NotificadorEmail()
        return NotificadorConsola()
