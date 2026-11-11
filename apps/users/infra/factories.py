import os

from django.core.mail import get_connection, send_mail
from django.utils.translation import gettext as _

from apps.users.notifications import INotificador


class NotificadorConsola(INotificador):
    """Modo MOCK: no depende de servicios externos. Ideal para desarrollo y tests."""

    def enviar_bienvenida(self, user):
        self._mostrar(_('[MOCK] Bienvenido/a %(usuario)s, tu billetera inicial ya está lista.') % {'usuario': user.username})

    def enviar_envio_simulado(self, user, nombre_item):
        self._mostrar(_('[MOCK] %(usuario)s, registramos el envío simulado de %(item)s.') % {'usuario': user.username, 'item': nombre_item})

    def _mostrar(self, mensaje):
        print(mensaje)


class NotificadorEmail(INotificador):
    """Genera el correo con el backend de Django seleccionado."""

    def __init__(self, backend=None):
        self.backend = backend

    def _enviar(self, **mensaje):
        if self.backend:
            mensaje['connection'] = get_connection(self.backend)
        return send_mail(**mensaje)

    def enviar_bienvenida(self, user):
        return self._enviar(
            subject=_('¡Bienvenido/a a VaultDrop!'),
            message=_('Hola %(usuario)s, tu cuenta fue creada exitosamente y tu billetera inicial ya está disponible. VaultDrop es una simulación académica sin dinero ni bienes reales.') % {'usuario': user.username},
            from_email=None,
            recipient_list=[user.email],
        )

    def enviar_envio_simulado(self, user, nombre_item):
        return self._enviar(
            subject=_('Envío simulado registrado en VaultDrop'),
            message=_('Hola %(usuario)s, registramos el envío simulado de %(item)s. Usuario de Steam: %(steam)s. Es una simulación académica: no se transfirió ningún objeto a Steam.') % {'usuario': user.username, 'item': nombre_item, 'steam': user.steam_username or _('Sin configurar')},
            from_email=None,
            recipient_list=[user.email],
        )


class NotificadorFactory:
    """Factory que decide, según la variable de entorno NOTIFICACION_MODE,
    qué implementación de INotificador instanciar (MOCK, SIMULADO o REAL)."""

    @staticmethod
    def crear(modo=None):
        modo = (modo or os.environ.get('NOTIFICACION_MODE', 'MOCK')).upper()
        if modo == 'SIMULADO':
            return NotificadorEmail('django.core.mail.backends.console.EmailBackend')
        if modo == 'REAL':
            return NotificadorEmail()
        return NotificadorConsola()
