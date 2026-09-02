from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models


class Caja(models.Model):
    nombre = models.CharField(max_length=120, unique=True)
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=12, decimal_places=2)
    activa = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Item(models.Model):
    RAREZA_COMUN = 'COMUN'
    RAREZA_RARO = 'RARO'
    RAREZA_EPICO = 'EPICO'
    RAREZA_LEGENDARIO = 'LEGENDARIO'

    RAREZA_CHOICES = (
        (RAREZA_COMUN, 'Comun'),
        (RAREZA_RARO, 'Raro'),
        (RAREZA_EPICO, 'Epico'),
        (RAREZA_LEGENDARIO, 'Legendario'),
    )

    nombre = models.CharField(max_length=120, unique=True)
    rareza = models.CharField(max_length=20, choices=RAREZA_CHOICES, default=RAREZA_COMUN)
    valor_estimado = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))

    class Meta:
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class CajaItem(models.Model):
    caja = models.ForeignKey(Caja, on_delete=models.CASCADE, related_name='caja_items')
    item = models.ForeignKey(Item, on_delete=models.PROTECT, related_name='caja_items')
    probabilidad = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        ordering = ['caja_id', 'item_id']
        unique_together = ('caja', 'item')

    def clean(self):
        if self.probabilidad <= 0 or self.probabilidad > 100:
            raise ValidationError('La probabilidad debe estar entre 0 y 100.')

    def __str__(self):
        return f'{self.caja} - {self.item} ({self.probabilidad}%)'

    @classmethod
    def total_probabilidad(cls, caja):
        total = cls.objects.filter(caja=caja).aggregate(total=models.Sum('probabilidad'))['total']
        return total or Decimal('0.00')

    @classmethod
    def validar_probabilidades(cls, caja):
        total = cls.total_probabilidad(caja)
        if total != Decimal('100.00'):
            raise ValueError('Las probabilidades de la caja deben sumar 100%')

