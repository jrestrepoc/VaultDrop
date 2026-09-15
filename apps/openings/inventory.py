from django.db import transaction
from apps.core.domain import ConflictError, NotFoundError
from apps.openings.repositories import DjangoAperturaCajaRepository
from apps.wallet.services import WalletService

class InventoryService:
    def __init__(self, repository=None, wallet_service=None):
        self.repository = repository or DjangoAperturaCajaRepository()
        self.wallet_service = wallet_service or WalletService()

    def list_for_user(self, user):
        return self.repository.list_inventory(user)

    def change_status(self, user, item_id, status):
        if status not in ('VENDIDO', 'ENVIADO'):
            raise ConflictError('Estado de inventario no permitido.')
        with transaction.atomic():
            changed = self.repository.claim_inventory(user, item_id, status)
            item = self.repository.get_inventory(user, item_id)
            if item is None:
                raise NotFoundError('Objeto no encontrado en tu inventario.')
            if not changed:
                raise ConflictError('Este objeto ya fue vendido o enviado.')
            if status == 'VENDIDO':
                self.wallet_service.acreditar(user, item.item.valor_estimado, tipo='VENTA')
            return item
