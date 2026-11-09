import random
from decimal import Decimal

from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext as _

from apps.cases.repositories import DjangoCajaRepository
from apps.core.domain import ConflictError
from apps.openings.domain.builders import AperturaCajaBuilder
from apps.openings.exceptions import (
    CajaNoDisponibleError,
    CajaNoEncontradaError,
    CajaSinItemsError,
    ProbabilidadesInvalidasError,
)
from apps.openings.repositories import DjangoAperturaCajaRepository
from apps.wallet.services import WalletService


class AperturaCajaService:
    def __init__(
        self,
        caja_repository=None,
        apertura_repository=None,
        wallet_service=None,
        randomizer=None,
    ):
        self.caja_repository = caja_repository or DjangoCajaRepository()
        self.apertura_repository = apertura_repository or DjangoAperturaCajaRepository()
        self.wallet_service = wallet_service or WalletService()
        self.randomizer = randomizer or random.SystemRandom()

    def abrir(self, user, caja_id):
        caja, caja_items = self._caja_lista(caja_id)
        with transaction.atomic():
            self.wallet_service.debitar(user, caja.precio)
            return self._registrar(user, caja, caja_items, caja.precio)

    def abrir_gratis(self, user):
        gratis = self.caja_repository.get_caja_gratis()
        if gratis is None:
            raise CajaNoDisponibleError(_('La caja no esta disponible'))
        caja, caja_items = self._caja_lista(gratis.pk)
        with transaction.atomic():
            if not self.apertura_repository.reclamar_caja_gratis(user, timezone.localdate()):
                raise ConflictError(_('Ya reclamaste tu caja gratis de hoy.'))
            return self._registrar(user, caja, caja_items, Decimal('0.00'))

    def estado_caja_gratis(self, user):
        caja = self.caja_repository.get_caja_gratis()
        if caja is None:
            return None
        return {'id': caja.pk, 'disponible': not self.apertura_repository.caja_gratis_reclamada(user, timezone.localdate())}

    def _caja_lista(self, caja_id):
        caja = self.caja_repository.get_by_id(caja_id)
        if caja is None:
            raise CajaNoEncontradaError(_('Caja no encontrada'))
        if not caja.activa:
            raise CajaNoDisponibleError(_('La caja no esta disponible'))

        caja_items = self.caja_repository.list_items_for_caja(caja)
        self._validar_items(caja_items)
        return caja, caja_items

    def _registrar(self, user, caja, caja_items, costo):
        item_obtenido = self._seleccionar_item(caja_items)
        datos_apertura = (
            AperturaCajaBuilder()
            .con_usuario(user)
            .con_caja(caja)
            .con_item(item_obtenido)
            .con_costo(costo)
            .build()
        )
        apertura = self.apertura_repository.create_apertura(**datos_apertura)
        inventario_item = self.apertura_repository.create_inventario_item(
            user=user,
            item=item_obtenido,
            apertura=apertura,
        )
        return apertura, inventario_item

    def _validar_items(self, caja_items):
        if not caja_items:
            raise CajaSinItemsError(_('La caja no tiene items configurados'))
        total = sum((caja_item.probabilidad for caja_item in caja_items), Decimal('0.00'))
        if any(ci.probabilidad <= 0 for ci in caja_items) or total != Decimal('100.00'):
            raise ProbabilidadesInvalidasError(_('Las probabilidades de la caja deben sumar 100%'))

    def _seleccionar_item(self, caja_items):
        acumulado = Decimal('0.00')
        ticket = Decimal(str(self.randomizer.uniform(0, 100)))
        for caja_item in caja_items:
            acumulado += caja_item.probabilidad
            if ticket <= acumulado:
                return caja_item.item
        return caja_items[-1].item
