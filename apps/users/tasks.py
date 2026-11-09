from smtplib import SMTPException

from celery import shared_task
from django.contrib.auth import get_user_model

from apps.users.infra.factories import INotificador, NotificadorFactory

REINTENTOS = {'autoretry_for': (SMTPException, OSError), 'retry_backoff': True, 'max_retries': 3}


@shared_task(**REINTENTOS)
def tarea_bienvenida(user_id):
    NotificadorFactory.crear().enviar_bienvenida(get_user_model().objects.get(pk=user_id))


@shared_task(**REINTENTOS)
def tarea_envio_simulado(user_id, nombre_item):
    NotificadorFactory.crear().enviar_envio_simulado(get_user_model().objects.get(pk=user_id), nombre_item)


class NotificadorEnCola(INotificador):
    """Publica la notificacion para que el worker la envie fuera de la peticion."""

    def enviar_bienvenida(self, user):
        tarea_bienvenida.delay(user.pk)

    def enviar_envio_simulado(self, user, nombre_item):
        tarea_envio_simulado.delay(user.pk, nombre_item)
