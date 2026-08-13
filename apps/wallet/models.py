from django.db import models
from django.conf import settings
from decimal import Decimal


class Billetera(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='billetera')
    saldo = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))


class Transaccion(models.Model):
    TIPO_CHOICES = (
        ('INICIAL', 'Inicial'),
        ('RECARGA', 'Recarga'),
        ('DEBITO', 'Debito'),
    )
    billetera = models.ForeignKey(Billetera, on_delete=models.CASCADE, related_name='transacciones')
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    saldo_anterior = models.DecimalField(max_digits=12, decimal_places=2)
    saldo_posterior = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
