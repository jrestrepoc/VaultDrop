from django.conf import settings
from django.db import models


class AperturaCaja(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='aperturas')
    caja = models.ForeignKey('cases.Caja', on_delete=models.PROTECT, related_name='aperturas')
    item = models.ForeignKey('cases.Item', on_delete=models.PROTECT, related_name='aperturas')
    costo = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user} abrio {self.caja} y obtuvo {self.item}'


class ItemInventario(models.Model):
    ESTADO_DISPONIBLE = 'DISPONIBLE'
    ESTADO_CHOICES = ((ESTADO_DISPONIBLE, 'Disponible'),)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='inventario')
    item = models.ForeignKey('cases.Item', on_delete=models.PROTECT, related_name='inventarios')
    apertura = models.OneToOneField(AperturaCaja, on_delete=models.CASCADE, related_name='inventario_item')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default=ESTADO_DISPONIBLE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.item} en inventario de {self.user}'

