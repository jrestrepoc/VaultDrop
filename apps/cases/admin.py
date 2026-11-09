from decimal import Decimal

from django.contrib import admin
from django.core.exceptions import ValidationError
from django.db.models import Count, Sum
from django.forms import BaseInlineFormSet
from django.utils.formats import number_format
from django.utils.html import format_html, format_html_join
from django.utils.translation import gettext, gettext_lazy as _

from apps.cases.models import Caja, CajaItem, Item
from apps.openings.models import AperturaCaja


class CajaItemFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        if any(self.errors):
            return
        activos = [form.cleaned_data for form in self.forms if form.cleaned_data and not form.cleaned_data.get('DELETE')]
        if sum((datos['probabilidad'] for datos in activos), Decimal('0')) != Decimal('100'):
            raise ValidationError(gettext('Las probabilidades de la caja deben sumar 100%'))


class CajaItemInline(admin.TabularInline):
    model = CajaItem
    formset = CajaItemFormSet
    extra = 1
    autocomplete_fields = ('item',)


@admin.register(Caja)
class CajaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'activa', 'total_aperturas', 'ingresos', 'valor_entregado', 'retorno')
    list_filter = ('activa',)
    ordering = ('nombre',)
    search_fields = ('nombre',)
    inlines = (CajaItemInline,)
    actions = ('activar', 'desactivar')
    readonly_fields = ('estadisticas',)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            _aperturas=Count('aperturas'),
            _ingresos=Sum('aperturas__costo'),
            _valor=Sum('aperturas__item__valor_estimado'),
        )

    @admin.display(description=_('Aperturas'), ordering='_aperturas')
    def total_aperturas(self, obj):
        return obj._aperturas

    @admin.display(description=_('Ingresos'), ordering='_ingresos')
    def ingresos(self, obj):
        return obj._ingresos

    @admin.display(description=_('Valor entregado'), ordering='_valor')
    def valor_entregado(self, obj):
        return obj._valor

    @admin.display(description=_('Retorno'))
    def retorno(self, obj):
        return f'{number_format(obj._valor / obj._ingresos * 100, 1)}%' if obj._ingresos else None

    @admin.display(description=_('Estadísticas'))
    def estadisticas(self, obj):
        aperturas = AperturaCaja.objects.filter(caja=obj)
        total = aperturas.count()
        if not total:
            return gettext('Todavía no hay aperturas.')
        obtenidos = dict(aperturas.order_by().values_list('item').annotate(veces=Count('id')))
        filas = (
            (ci.item.nombre, number_format(ci.probabilidad, 2), obtenidos.get(ci.item_id, 0), number_format(obtenidos.get(ci.item_id, 0) / total * 100, 2))
            for ci in obj.caja_items.select_related('item')
        )
        return format_html(
            '<table><thead><tr><th>{}</th><th>{}</th><th>{}</th><th>{}</th></tr></thead><tbody>{}</tbody></table>',
            gettext('Objeto'), gettext('Probabilidad configurada'), gettext('Veces obtenido'), gettext('Probabilidad real'),
            format_html_join('', '<tr><td>{}</td><td>{}%</td><td>{}</td><td>{}%</td></tr>', filas),
        )

    @admin.action(description=_('Activar cajas seleccionadas'))
    def activar(self, request, queryset):
        self.message_user(request, gettext('Registros actualizados: %(n)s') % {'n': queryset.update(activa=True)})

    @admin.action(description=_('Desactivar cajas seleccionadas'))
    def desactivar(self, request, queryset):
        self.message_user(request, gettext('Registros actualizados: %(n)s') % {'n': queryset.update(activa=False)})


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'rareza', 'valor_estimado', 'veces_obtenido')
    list_filter = ('rareza',)
    ordering = ('nombre',)
    search_fields = ('nombre',)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(_veces=Count('aperturas'))

    @admin.display(description=_('Veces obtenido'), ordering='_veces')
    def veces_obtenido(self, obj):
        return obj._veces
