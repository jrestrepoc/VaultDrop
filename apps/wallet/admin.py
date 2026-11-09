from django.contrib import admin

from apps.core.admin import SoloLecturaAdmin
from apps.wallet.models import Billetera, Transaccion


@admin.register(Billetera)
class BilleteraAdmin(SoloLecturaAdmin):
    list_display = ('user', 'saldo')
    search_fields = ('user__username',)
    list_select_related = ('user',)


@admin.register(Transaccion)
class TransaccionAdmin(SoloLecturaAdmin):
    list_display = ('billetera', 'tipo', 'monto', 'saldo_anterior', 'saldo_posterior', 'created_at')
    list_filter = ('tipo',)
    search_fields = ('billetera__user__username',)
    date_hierarchy = 'created_at'
    list_select_related = ('billetera__user',)
