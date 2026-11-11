from abc import ABC, abstractmethod


class INotificador(ABC):
    @abstractmethod
    def enviar_bienvenida(self, user):
        pass

    @abstractmethod
    def enviar_envio_simulado(self, user, nombre_item):
        pass
