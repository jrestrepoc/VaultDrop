from django.db import models
from django.conf import settings
from decimal import Decimal

from django.utils.translation import gettext_lazy as _


class Billetera(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='billetera', verbose_name=_('usuario'))
    saldo = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), verbose_name=_('saldo'))


    class Meta:
        verbose_name = _('billetera')
        verbose_name_plural = _('billeteras')
        constraints = [models.CheckConstraint(condition=models.Q(saldo__gte=0), name='wallet_nonnegative_balance')]

    def __str__(self):
        return str(self.user)


class Transaccion(models.Model):
    TIPO_CHOICES = (
        ('INICIAL', _('Inicial')),
        ('RECARGA', _('Recarga')),
        ('DEBITO', _('Debito')),
        ('VENTA', _('Venta de objeto')),
    )
    billetera = models.ForeignKey(Billetera, on_delete=models.CASCADE, related_name='transacciones', verbose_name=_('billetera'))
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, verbose_name=_('tipo'))
    monto = models.DecimalField(max_digits=12, decimal_places=2, verbose_name=_('monto'))
    saldo_anterior = models.DecimalField(max_digits=12, decimal_places=2, verbose_name=_('saldo anterior'))
    saldo_posterior = models.DecimalField(max_digits=12, decimal_places=2, verbose_name=_('saldo posterior'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('fecha de creación'))

    class Meta:
        verbose_name = _('movimiento')
        verbose_name_plural = _('movimientos')
        ordering = ['id']
