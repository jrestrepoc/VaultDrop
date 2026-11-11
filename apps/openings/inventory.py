from django.db import transaction
from django.utils.translation import gettext as _
from apps.core.domain import ConflictError, NotFoundError
from apps.openings.repositories import DjangoAperturaCajaRepository
from apps.users.notifications import INotificador
from apps.wallet.services import WalletService

class InventoryService:
    def __init__(self, repository=None, wallet_service=None, *, notificador: INotificador):
        self.repository = repository or DjangoAperturaCajaRepository()
        self.wallet_service = wallet_service or WalletService()
        self.notificador = notificador

    def list_for_user(self, user):
        return self.repository.list_inventory(user)

    def change_status(self, user, item_id, status):
        return self.change_status_many(user, [item_id], status)[0]

    def change_status_many(self, user, item_ids, status):
        if status not in ('VENDIDO', 'ENVIADO'):
            raise ConflictError(_('Estado de inventario no permitido.'))
        with transaction.atomic():
            items = self.reclamar(user, item_ids, status)
            if status == 'VENDIDO':
                self.wallet_service.acreditar(user, sum(item.item.valor_estimado for item in items), tipo='VENTA')
            else:
                nombres = ', '.join(item.item.nombre for item in items)
                transaction.on_commit(lambda: self.notificador.enviar_envio_simulado(user, nombres), robust=True)
            return items

    def reclamar(self, user, item_ids, status):
        """Todo o nada: quien llama debe estar en una transaccion para revertir si falla."""
        ids = set(item_ids)
        cambiados = self.repository.claim_inventory(user, ids, status)
        items = self.repository.get_inventory(user, ids)
        if len(items) != len(ids):
            raise NotFoundError(_('Objeto no encontrado en tu inventario.'))
        if cambiados != len(ids):
            raise ConflictError(_('Este objeto ya no está disponible.'))
        return items
