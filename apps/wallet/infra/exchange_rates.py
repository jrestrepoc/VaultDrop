import http.client
import json
import logging
from abc import ABC, abstractmethod
from decimal import Decimal, InvalidOperation
from urllib.request import urlopen

from django.utils.translation import gettext as _

from apps.core.domain import ExternalServiceError

logger = logging.getLogger(__name__)


class IProveedorTasaCambio(ABC):
    """Contrato del que depende la aplicacion; no conoce ninguna API concreta."""

    @abstractmethod
    def obtener_tasa(self, moneda):
        """Devuelve cuantas unidades de `moneda` equivalen a 1 USD, como Decimal."""


class ExchangeRateApiAdapter(IProveedorTasaCambio):
    """Adapta la respuesta JSON de ExchangeRate-API al contrato de la aplicacion."""

    URL = 'https://open.er-api.com/v6/latest/USD'

    def obtener_tasa(self, moneda):
        try:
            with urlopen(self.URL, timeout=3) as respuesta:
                tasa = Decimal(str(json.load(respuesta)['rates'][moneda]))
            if not tasa.is_finite() or tasa <= 0:
                raise ValueError(f'tasa invalida: {tasa}')
        except (OSError, http.client.HTTPException, ValueError, KeyError, TypeError, InvalidOperation) as exc:
            logger.warning('Tasa de cambio no disponible: %s', exc)
            raise ExternalServiceError(_('No se pudo consultar la tasa de cambio.')) from exc
        return tasa
