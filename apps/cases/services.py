from decimal import Decimal

from django.utils.translation import gettext as _


def validar_distribucion(probabilidades):
    if sum(probabilidades, Decimal('0.00')) != Decimal('100.00'):
        raise ValueError(_('Las probabilidades de la caja deben sumar 100%'))
