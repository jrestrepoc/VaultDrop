from abc import ABC, abstractmethod

from apps.cases.models import Caja


class ICajaRepository(ABC):
    @abstractmethod
    def list_activas(self):
        pass

    @abstractmethod
    def get_by_id(self, caja_id):
        pass

    @abstractmethod
    def list_items_for_caja(self, caja):
        pass


class DjangoCajaRepository(ICajaRepository):
    def list_activas(self):
        return Caja.objects.filter(activa=True).prefetch_related('caja_items__item')

    def get_by_id(self, caja_id):
        try:
            return Caja.objects.prefetch_related('caja_items__item').get(id=caja_id)
        except Caja.DoesNotExist:
            return None

    def list_items_for_caja(self, caja):
        return list(caja.caja_items.select_related('item'))

