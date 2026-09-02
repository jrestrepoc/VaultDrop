import random
from decimal import Decimal

from django.db import transaction

from apps.cases.repositories import DjangoCajaRepository
from apps.openings.domain.builders import AperturaCajaBuilder
from apps.openings.exceptions import (
    CajaNoDisponibleError,
    CajaNoEncontradaError,
    CajaSinItemsError,
    ProbabilidadesInvalidasError,
    SaldoInsuficienteError,
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
        caja = self.caja_repository.get_by_id(caja_id)
        if caja is None:
            raise CajaNoEncontradaError('Caja no encontrada')
        if not caja.activa:
            raise CajaNoDisponibleError('La caja no esta disponible')

        caja_items = self.caja_repository.list_items_for_caja(caja)
        self._validar_items(caja_items)

        with transaction.atomic():
            if not self.wallet_service.tiene_saldo_suficiente(user, caja.precio):
                raise SaldoInsuficienteError('Saldo insuficiente')

            item_obtenido = self._seleccionar_item(caja_items)
            datos_apertura = (
                AperturaCajaBuilder()
                .con_usuario(user)
                .con_caja(caja)
                .con_item(item_obtenido)
                .con_costo(caja.precio)
                .build()
            )
            self.wallet_service.debitar(user, caja.precio)
            apertura = self.apertura_repository.create_apertura(**datos_apertura)
            inventario_item = self.apertura_repository.create_inventario_item(
                user=user,
                item=item_obtenido,
                apertura=apertura,
            )
        return apertura, inventario_item

    def _validar_items(self, caja_items):
        if not caja_items:
            raise CajaSinItemsError('La caja no tiene items configurados')
        total = sum((caja_item.probabilidad for caja_item in caja_items), Decimal('0.00'))
        if total != Decimal('100.00'):
            raise ProbabilidadesInvalidasError('Las probabilidades de la caja deben sumar 100%')

    def _seleccionar_item(self, caja_items):
        acumulado = Decimal('0.00')
        ticket = Decimal(str(self.randomizer.uniform(0, 100)))
        for caja_item in caja_items:
            acumulado += caja_item.probabilidad
            if ticket <= acumulado:
                return caja_item.item
        return caja_items[-1].item
