from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    email = models.EmailField(unique=True)

    steam_username = models.CharField(max_length=100, blank=True, default='', verbose_name=_('usuario de Steam'))


class NotificacionEnvio(models.Model):
    tarea_id = models.UUIDField(unique=True, editable=False)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('Usuario'))
    objetos = models.TextField(verbose_name=_('Objetos'))
    fecha = models.DateTimeField(auto_now_add=True, verbose_name=_('Fecha'))

    class Meta:
        ordering = ('-fecha', '-pk')
        verbose_name = _('Notificación de envío')
        verbose_name_plural = _('Notificaciones de envío')
