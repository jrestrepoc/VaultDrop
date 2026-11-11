import random
from decimal import Decimal

from django.db import transaction
from django.utils.translation import gettext as _

from apps.cases.repositories import DjangoCajaRepository
from apps.core.domain import BusinessError, NotFoundError
from apps.openings.composition import crear_servicio_inventario
from apps.openings.repositories import DjangoAperturaCajaRepository

PROBABILIDAD_MINIMA = Decimal('1.00')
PROBABILIDAD_MAXIMA = Decimal('80.00')


def probabilidad_de_mejora(entregado, objetivo):
    if entregado >= objetivo:
        raise BusinessError(_('El objetivo debe valer más que lo entregado.'))
    probabilidad = (entregado / objetivo * 100).quantize(Decimal('0.01'))
    if probabilidad < PROBABILIDAD_MINIMA:
        raise BusinessError(_('La probabilidad de esta mejora es demasiado baja.'))
    return min(probabilidad, PROBABILIDAD_MAXIMA)


class MejoraService:
    def __init__(self, repository=None, caja_repository=None, inventory_service=None, randomizer=None):
        self.repository = repository or DjangoAperturaCajaRepository()
        self.caja_repository = caja_repository or DjangoCajaRepository()
        self.inventory_service = inventory_service or crear_servicio_inventario()
        self.randomizer = randomizer or random.SystemRandom()

    def mejorar(self, user, item_ids, objetivo_id):
        objetivo = self.caja_repository.get_item(objetivo_id)
        if objetivo is None:
            raise NotFoundError(_('Objeto no encontrado.'))
        with transaction.atomic():
            entregados = self.inventory_service.reclamar(user, item_ids, 'CONSUMIDO')
            valor = sum(entregado.item.valor_estimado for entregado in entregados)
            probabilidad = probabilidad_de_mejora(valor, objetivo.valor_estimado)
            exito = Decimal(str(self.randomizer.uniform(0, 100))) < probabilidad
            premio = self.repository.create_inventario_item(user=user, item=objetivo, apertura=None) if exito else None
            return self.repository.create_mejora(
                user,
                entregados,
                objetivo=objetivo,
                premio=premio,
                valor_entregado=valor,
                valor_objetivo=objetivo.valor_estimado,
                probabilidad=probabilidad,
                exito=exito,
            )
