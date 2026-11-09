from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.utils.translation import gettext, gettext_lazy as _
from rest_framework.authtoken.models import TokenProxy

# Los tokens dan acceso a las cuentas: no deben verse en una lista.
admin.site.unregister(TokenProxy)
admin.site.unregister(Group)


@admin.register(get_user_model())
class VaultDropUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'is_active', 'is_staff', 'date_joined')
    fieldsets = UserAdmin.fieldsets + (('Steam', {'fields': ('steam_username',)}),)
    actions = ('activar', 'desactivar')

    def has_add_permission(self, request):
        # Solo UserService crea la billetera y el bono inicial.
        return False

    def has_delete_permission(self, request, obj=None):
        # Borrar una cuenta eliminaria su historial; se desactiva en su lugar.
        return False

    @admin.action(description=_('Activar cuentas seleccionadas'))
    def activar(self, request, queryset):
        self.message_user(request, gettext('Registros actualizados: %(n)s') % {'n': queryset.update(is_active=True)})

    @admin.action(description=_('Desactivar cuentas seleccionadas'))
    def desactivar(self, request, queryset):
        cambiados = queryset.exclude(pk=request.user.pk).update(is_active=False)
        self.message_user(request, gettext('Registros actualizados: %(n)s') % {'n': cambiados})
