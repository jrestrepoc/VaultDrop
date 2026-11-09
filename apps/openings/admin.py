from django.contrib import admin

from apps.core.admin import SoloLecturaAdmin
from apps.openings.models import AperturaCaja, ItemInventario, Mejora


@admin.register(AperturaCaja)
class AperturaCajaAdmin(SoloLecturaAdmin):
    list_display = ('user', 'caja', 'item', 'costo', 'created_at')
    list_filter = ('caja',)
    search_fields = ('user__username', 'item__nombre')
    date_hierarchy = 'created_at'
    list_select_related = ('user', 'caja', 'item')


@admin.register(ItemInventario)
class ItemInventarioAdmin(SoloLecturaAdmin):
    list_display = ('user', 'item', 'estado', 'created_at')
    list_filter = ('estado',)
    search_fields = ('user__username', 'item__nombre')
    list_select_related = ('user', 'item')


@admin.register(Mejora)
class MejoraAdmin(SoloLecturaAdmin):
    list_display = ('user', 'objetivo', 'valor_entregado', 'valor_objetivo', 'probabilidad', 'exito', 'created_at')
    list_filter = ('exito',)
    search_fields = ('user__username', 'objetivo__nombre')
    date_hierarchy = 'created_at'
    list_select_related = ('user', 'objetivo')
