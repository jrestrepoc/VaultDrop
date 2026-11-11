from abc import ABC, abstractmethod

from django.db import transaction


class IUnidadDeTrabajo(ABC):
    @abstractmethod
    def iniciar(self):
        pass

    @abstractmethod
    def confirmar(self):
        pass

    @abstractmethod
    def revertir(self, tipo_error, error, traceback):
        pass

    def __enter__(self):
        self.iniciar()
        return self

    def __exit__(self, tipo_error, error, traceback):
        if tipo_error is None:
            self.confirmar()
        else:
            self.revertir(tipo_error, error, traceback)


class UnidadDeTrabajoDjango(IUnidadDeTrabajo):
    def __init__(self):
        self.transaccion = transaction.atomic()

    def iniciar(self):
        self.transaccion.__enter__()

    def confirmar(self):
        self.transaccion.__exit__(None, None, None)

    def revertir(self, tipo_error, error, traceback):
        self.transaccion.__exit__(tipo_error, error, traceback)
