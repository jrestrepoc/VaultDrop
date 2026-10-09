class CatalogError(Exception):
    status_code = 500
    code = 'CATALOG_ERROR'
    message = 'No se pudo completar la operacion.'

    def __init__(self, message=None):
        self.message = message or self.message
        super().__init__(self.message)


class BadRequestError(CatalogError):
    status_code = 400
    code = 'BAD_REQUEST'
    message = 'La solicitud no es valida.'


class NotFoundError(CatalogError):
    status_code = 404
    code = 'RESOURCE_NOT_FOUND'
    message = 'El recurso solicitado no existe.'


class DataAccessError(CatalogError):
    status_code = 500
    code = 'DATA_ACCESS_ERROR'
    message = 'No se pudo leer el catalogo.'
