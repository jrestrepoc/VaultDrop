from django.db import transaction
from django.utils.translation import gettext as _
from apps.core.domain import ConflictError, NotFoundError
from apps.openings.repositories import DjangoAperturaCajaRepository
from apps.users.tasks import NotificadorEnCola
from apps.wallet.services import WalletService

class InventoryService:
    def __init__(self, repository=None, wallet_service=None, notificador=None):
        self.repository = repository or DjangoAperturaCajaRepository()
        self.wallet_service = wallet_service or WalletService()
        self.notificador = notificador or NotificadorEnCola()

    def list_for_user(self, user):
        return self.repository.list_inventory(user)

    def change_status(self, user, item_id, status):
        if status not in ('VENDIDO', 'ENVIADO'):
            raise ConflictError(_('Estado de inventario no permitido.'))
        with transaction.atomic():
            changed = self.repository.claim_inventory(user, item_id, status)
            item = self.repository.get_inventory(user, item_id)
            if item is None:
                raise NotFoundError(_('Objeto no encontrado en tu inventario.'))
            if not changed:
                raise ConflictError(_('Este objeto ya fue vendido o enviado.'))
            if status == 'VENDIDO':
                self.wallet_service.acreditar(user, item.item.valor_estimado, tipo='VENTA')
            else:
                nombre = item.item.nombre
                transaction.on_commit(lambda: self.notificador.enviar_envio_simulado(user, nombre), robust=True)
            return item
