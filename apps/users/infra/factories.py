import os
from abc import ABC, abstractmethod

from django.core.mail import send_mail
from django.utils.translation import gettext as _


class INotificador(ABC):
    @abstractmethod
    def enviar_bienvenida(self, user):
        pass

    @abstractmethod
    def enviar_envio_simulado(self, user, nombre_item):
        pass


class NotificadorConsola(INotificador):
    """Modo MOCK: no depende de servicios externos. Ideal para desarrollo y tests."""

    def enviar_bienvenida(self, user):
        self._mostrar(_('[MOCK] Bienvenido/a %(usuario)s, tu billetera inicial ya está lista.') % {'usuario': user.username})

    def enviar_envio_simulado(self, user, nombre_item):
        self._mostrar(_('[MOCK] %(usuario)s, registramos el envío simulado de %(item)s.') % {'usuario': user.username, 'item': nombre_item})

    def _mostrar(self, mensaje):
        print(mensaje)


class NotificadorEmail(INotificador):
    """Modo REAL: envía un correo real usando django.core.mail.send_mail."""

    def enviar_bienvenida(self, user):
        send_mail(
            subject=_('¡Bienvenido/a a VaultDrop!'),
            message=_('Hola %(usuario)s, tu cuenta fue creada exitosamente y tu billetera inicial ya está disponible.') % {'usuario': user.username},
            from_email=None,
            recipient_list=[user.email],
        )

    def enviar_envio_simulado(self, user, nombre_item):
        send_mail(
            subject=_('Envío simulado registrado en VaultDrop'),
            message=_('Hola %(usuario)s, registramos el envío simulado de %(item)s. Es una simulación académica: no se transfirió ningún objeto a Steam.') % {'usuario': user.username, 'item': nombre_item},
            from_email=None,
            recipient_list=[user.email],
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
