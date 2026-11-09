from django.contrib import admin
from django.utils.translation import gettext_lazy as _

admin.site.site_header = _('Administración de VaultDrop')
admin.site.site_title = _('Administración de VaultDrop')
admin.site.index_title = _('Administración')


class SoloLecturaAdmin(admin.ModelAdmin):
    """Historial contable: se consulta, pero solo los servicios pueden escribirlo."""

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
