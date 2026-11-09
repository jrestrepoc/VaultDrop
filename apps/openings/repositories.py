from abc import ABC, abstractmethod

from apps.openings.models import AperturaCaja, ItemInventario, Mejora, ReclamoCajaGratis


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
    def claim_inventory(self, user, item_ids, status): ...

    @abstractmethod
    def get_inventory(self, user, item_ids): ...

    @abstractmethod
    def create_mejora(self, user, entregados, **datos): ...

    @abstractmethod
    def reclamar_caja_gratis(self, user, fecha): ...

    @abstractmethod
    def caja_gratis_reclamada(self, user, fecha): ...

    @abstractmethod
    def historial_aperturas(self, user, limite): ...

    @abstractmethod
    def historial_mejoras(self, user, limite): ...

    @abstractmethod
    def mejores_premios(self, limite): ...


class DjangoAperturaCajaRepository(IAperturaCajaRepository):
    def create_apertura(self, user, caja, item, costo):
        return AperturaCaja.objects.create(user=user, caja=caja, item=item, costo=costo)

    def create_inventario_item(self, user, item, apertura):
        return ItemInventario.objects.create(user=user, item=item, apertura=apertura)


    def list_inventory(self, user):
        return ItemInventario.objects.filter(user=user).select_related('item', 'apertura__caja')

    def claim_inventory(self, user, item_ids, status):
        return ItemInventario.objects.filter(pk__in=item_ids, user=user, estado='DISPONIBLE').update(estado=status)

    def get_inventory(self, user, item_ids):
        return list(self.list_inventory(user).filter(pk__in=item_ids))

    def create_mejora(self, user, entregados, **datos):
        mejora = Mejora.objects.create(user=user, **datos)
        mejora.entregados.set(entregados)
        return mejora

    def reclamar_caja_gratis(self, user, fecha):
        return ReclamoCajaGratis.objects.get_or_create(user=user, fecha=fecha)[1]

    def caja_gratis_reclamada(self, user, fecha):
        return ReclamoCajaGratis.objects.filter(user=user, fecha=fecha).exists()

    def historial_aperturas(self, user, limite):
        return AperturaCaja.objects.filter(user=user).select_related('caja', 'item')[:limite]

    def historial_mejoras(self, user, limite):
        return Mejora.objects.filter(user=user).select_related('objetivo')[:limite]

    def mejores_premios(self, limite):
        return ItemInventario.objects.select_related('user', 'item', 'apertura__caja').order_by('-item__valor_estimado', '-created_at')[:limite]
