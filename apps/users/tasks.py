from smtplib import SMTPException
from uuid import uuid4

from celery import shared_task
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import translation

from apps.users.infra.factories import NotificadorFactory
from apps.users.models import NotificacionEnvio
from apps.users.notifications import INotificador

REINTENTOS = {'autoretry_for': (SMTPException, OSError), 'retry_backoff': True, 'max_retries': 3}


@shared_task(**REINTENTOS)
def tarea_bienvenida(user_id, idioma=None):
    with translation.override(idioma):
        NotificadorFactory.crear().enviar_bienvenida(get_user_model().objects.get(pk=user_id))


@shared_task(bind=True, **REINTENTOS)
def tarea_envio_simulado(self, user_id, nombre_item, idioma=None):
    tarea_id = self.request.id or uuid4()
    with transaction.atomic(), translation.override(idioma):
        registro, creado = NotificacionEnvio.objects.get_or_create(
            tarea_id=tarea_id,
            defaults={'usuario_id': user_id, 'objetos': nombre_item},
        )
        if creado:
            enviados = NotificadorFactory.crear().enviar_envio_simulado(registro.usuario, nombre_item)
            if enviados == 0:
                raise OSError('El backend de correo no aceptó la notificación.')


class NotificadorEnCola(INotificador):
    """Publica la notificacion para que el worker la envie fuera de la peticion."""

    def enviar_bienvenida(self, user):
        tarea_bienvenida.delay(user.pk, translation.get_language())

    def enviar_envio_simulado(self, user, nombre_item):
        tarea_envio_simulado.delay(user.pk, nombre_item, translation.get_language())
