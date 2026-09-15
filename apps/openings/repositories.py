from abc import ABC, abstractmethod

from apps.openings.models import AperturaCaja, ItemInventario


class IAperturaCajaRepository(ABC):
    @abstractmethod
    def create_apertura(self, user, caja, item, costo):
        pass

    @abstractmethod
    def create_inventario_item(self, user, item, apertura):
        pass


    @abstractmethod
    def list_inventory(self, user): ...

    @abstractmethod
    def claim_inventory(self, user, item_id, status): ...

    @abstractmethod
    def get_inventory(self, user, item_id): ...


class DjangoAperturaCajaRepository(IAperturaCajaRepository):
    def create_apertura(self, user, caja, item, costo):
        return AperturaCaja.objects.create(user=user, caja=caja, item=item, costo=costo)

    def create_inventario_item(self, user, item, apertura):
        return ItemInventario.objects.create(user=user, item=item, apertura=apertura)


    def list_inventory(self, user):
        return ItemInventario.objects.filter(user=user).select_related('item', 'apertura__caja')

    def claim_inventory(self, user, item_id, status):
        return ItemInventario.objects.filter(pk=item_id, user=user, estado='DISPONIBLE').update(estado=status)

    def get_inventory(self, user, item_id):
        return self.list_inventory(user).filter(pk=item_id).first()

    def count_openings(self, user):
        return AperturaCaja.objects.filter(user=user).count()
