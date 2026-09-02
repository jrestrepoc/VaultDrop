class AperturaCajaBuilder:
    """Construye una apertura validada sin conocer detalles de persistencia."""

    def __init__(self):
        self._user = None
        self._caja = None
        self._item = None
        self._costo = None

    def con_usuario(self, user):
        self._user = user
        return self

    def con_caja(self, caja):
        self._caja = caja
        return self

    def con_item(self, item):
        self._item = item
        return self

    def con_costo(self, costo):
        self._costo = costo
        return self

    def build(self):
        errores = []
        if self._user is None:
            errores.append('El usuario es obligatorio')
        if self._caja is None:
            errores.append('La caja es obligatoria')
        if self._item is None:
            errores.append('El item obtenido es obligatorio')
        if self._costo is None:
            errores.append('El costo es obligatorio')
        elif self._costo <= 0:
            errores.append('El costo debe ser mayor a cero')
        if errores:
            raise ValueError(' / '.join(errores))
        return {
            'user': self._user,
            'caja': self._caja,
            'item': self._item,
            'costo': self._costo,
        }

