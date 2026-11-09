from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext as _, gettext_lazy


class Caja(models.Model):
    nombre = models.CharField(max_length=120, unique=True, verbose_name=gettext_lazy('nombre'))
    imagen_url = models.CharField(max_length=1000, blank=True, default='', verbose_name=gettext_lazy('imagen'))
    descripcion = models.TextField(blank=True, verbose_name=gettext_lazy('descripción'))
    precio = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))], verbose_name=gettext_lazy('precio'))
    activa = models.BooleanField(default=True, verbose_name=gettext_lazy('activa'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=gettext_lazy('fecha de creación'))

    class Meta:
        verbose_name = gettext_lazy('caja')
        verbose_name_plural = gettext_lazy('cajas')
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Item(models.Model):
    RAREZA_COMUN = 'COMUN'
    RAREZA_RARO = 'RARO'
    RAREZA_EPICO = 'EPICO'
    RAREZA_LEGENDARIO = 'LEGENDARIO'

    RAREZA_CHOICES = (
        (RAREZA_COMUN, gettext_lazy('Comun')),
        (RAREZA_RARO, gettext_lazy('Raro')),
        (RAREZA_EPICO, gettext_lazy('Epico')),
        (RAREZA_LEGENDARIO, gettext_lazy('Legendario')),
    )

    nombre = models.CharField(max_length=120, unique=True, verbose_name=gettext_lazy('nombre'))
    imagen_url = models.CharField(max_length=1000, blank=True, default='', verbose_name=gettext_lazy('imagen'))
    rareza = models.CharField(max_length=20, choices=RAREZA_CHOICES, default=RAREZA_COMUN, verbose_name=gettext_lazy('rareza'))
    valor_estimado = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), validators=[MinValueValidator(Decimal('0.01'))], verbose_name=gettext_lazy('valor estimado'))

    class Meta:
        verbose_name = gettext_lazy('objeto')
        verbose_name_plural = gettext_lazy('objetos')
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class CajaItem(models.Model):
    caja = models.ForeignKey(Caja, on_delete=models.CASCADE, related_name='caja_items', verbose_name=gettext_lazy('caja'))
    item = models.ForeignKey(Item, on_delete=models.PROTECT, related_name='caja_items', verbose_name=gettext_lazy('objeto'))
    probabilidad = models.DecimalField(max_digits=5, decimal_places=2, verbose_name=gettext_lazy('probabilidad'))

    class Meta:
        verbose_name = gettext_lazy('objeto de la caja')
        verbose_name_plural = gettext_lazy('objetos de la caja')
        ordering = ['caja_id', 'item_id']
        unique_together = ('caja', 'item')

    def clean(self):
        if self.probabilidad <= 0 or self.probabilidad > 100:
            raise ValidationError(_('La probabilidad debe estar entre 0 y 100.'))

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
            raise ValueError(_('Las probabilidades de la caja deben sumar 100%'))

