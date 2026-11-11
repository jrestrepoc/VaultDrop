from apps.openings.inventory import InventoryService
from apps.users.tasks import NotificadorEnCola


def crear_servicio_inventario():
    return InventoryService(notificador=NotificadorEnCola())
