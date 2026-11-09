from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class AperturaCaja(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='aperturas', verbose_name=_('usuario'))
    caja = models.ForeignKey('cases.Caja', on_delete=models.PROTECT, related_name='aperturas', verbose_name=_('caja'))
    item = models.ForeignKey('cases.Item', on_delete=models.PROTECT, related_name='aperturas', verbose_name=_('objeto'))
    costo = models.DecimalField(max_digits=12, decimal_places=2, verbose_name=_('costo'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('fecha de creación'))

    class Meta:
        verbose_name = _('apertura')
        verbose_name_plural = _('aperturas')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user} abrio {self.caja} y obtuvo {self.item}'


class ItemInventario(models.Model):
    ESTADO_DISPONIBLE = 'DISPONIBLE'
    ESTADO_CHOICES = ((ESTADO_DISPONIBLE, _('Disponible')), ('VENDIDO', _('Vendido')), ('ENVIADO', _('Enviado (simulación)')), ('CONSUMIDO', _('Usado en una mejora')))

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='inventario', verbose_name=_('usuario'))
    item = models.ForeignKey('cases.Item', on_delete=models.PROTECT, related_name='inventarios', verbose_name=_('objeto'))
    apertura = models.OneToOneField(AperturaCaja, on_delete=models.CASCADE, related_name='inventario_item', null=True, blank=True, verbose_name=_('apertura'))
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default=ESTADO_DISPONIBLE, verbose_name=_('estado'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('fecha de creación'))

    class Meta:
        verbose_name = _('objeto del inventario')
        verbose_name_plural = _('objetos del inventario')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.item} en inventario de {self.user}'


class Mejora(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='mejoras', verbose_name=_('usuario'))
    entregados = models.ManyToManyField(ItemInventario, related_name='mejoras', verbose_name=_('objetos entregados'))
    objetivo = models.ForeignKey('cases.Item', on_delete=models.PROTECT, related_name='mejoras', verbose_name=_('objetivo'))
    premio = models.OneToOneField(ItemInventario, on_delete=models.SET_NULL, related_name='mejora_ganada', null=True, blank=True, verbose_name=_('premio'))
    valor_entregado = models.DecimalField(max_digits=12, decimal_places=2, verbose_name=_('valor entregado'))
    valor_objetivo = models.DecimalField(max_digits=12, decimal_places=2, verbose_name=_('valor del objetivo'))
    probabilidad = models.DecimalField(max_digits=5, decimal_places=2, verbose_name=_('probabilidad'))
    exito = models.BooleanField(verbose_name=_('éxito'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('fecha de creación'))

    class Meta:
        verbose_name = _('mejora')
        verbose_name_plural = _('mejoras')
        ordering = ['-created_at']


class ReclamoCajaGratis(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reclamos_gratis')
    fecha = models.DateField()

    class Meta:
        constraints = [models.UniqueConstraint(fields=['user', 'fecha'], name='unique_daily_free_case')]
