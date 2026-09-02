from abc import ABC, abstractmethod

from apps.openings.models import AperturaCaja, ItemInventario


class IAperturaCajaRepository(ABC):
    @abstractmethod
    def create_apertura(self, user, caja, item, costo):
        pass

    @abstractmethod
    def create_inventario_item(self, user, item, apertura):
        pass


class DjangoAperturaCajaRepository(IAperturaCajaRepository):
    def create_apertura(self, user, caja, item, costo):
        return AperturaCaja.objects.create(user=user, caja=caja, item=item, costo=costo)

    def create_inventario_item(self, user, item, apertura):
        return ItemInventario.objects.create(user=user, item=item, apertura=apertura)

