import time
from typing import Any, Dict, List, Optional

import requests

from domain.exceptions import FuenteDatosNoDisponible
from domain.ports import DatosAbiertosPort
from infrastructure.resilience import CircuitBreaker, CircuitOpenError, con_reintentos

BASE_URL = "https://www.datos.gov.co/resource"


class _SocrataAdapter(DatosAbiertosPort):
    """Adaptador genérico para la API Socrata de datos.gov.co, con circuit breaker y reintentos."""

    def __init__(self, nombre: str, dataset_id: str, breaker: CircuitBreaker, limite_defecto: int,
                 orden: Optional[str] = None, http_get=requests.get, timeout: float = 10.0,
                 intentos: int = 3, base_espera: float = 0.5, dormir=time.sleep):
        self.nombre = nombre
        self._url = f"{BASE_URL}/{dataset_id}.json"
        self._breaker = breaker
        self._limite_defecto = limite_defecto
        self._orden = orden
        self._http_get = http_get
        self._timeout = timeout
        self._intentos = intentos
        self._base_espera = base_espera
        self._dormir = dormir

    def obtener_registros(self, limite: Optional[int] = None) -> List[Dict[str, Any]]:
        params = {"$limit": limite or self._limite_defecto}
        if self._orden:
            params["$order"] = self._orden

        def llamar():
            r = self._http_get(self._url, params=params, timeout=self._timeout)
            r.raise_for_status()
            datos = r.json()
            if not isinstance(datos, list):
                raise ValueError("Respuesta inesperada de la API (no es una lista)")
            return datos

        try:
            return con_reintentos(
                lambda: self._breaker.call(llamar),
                intentos=self._intentos, base=self._base_espera,
                dormir=self._dormir, nombre=self.nombre,
            )
        except (CircuitOpenError, requests.RequestException, ValueError) as exc:
            raise FuenteDatosNoDisponible(self.nombre) from exc


class DatosGovCoAdapter(_SocrataAdapter):
    """SECOP II - Procesos de Contratación (datos.gov.co, dataset p6dx-8zbt)."""

    def __init__(self, breaker: CircuitBreaker, **kwargs):
        super().__init__("SECOP II", "p6dx-8zbt", breaker, limite_defecto=100,
                         orden="fecha_de_publicacion_del DESC", **kwargs)


class DaneAdapter(_SocrataAdapter):
    """DIVIPOLA - Códigos de municipios, publicado por el DANE en datos.gov.co (dataset gdxc-w37w)."""

    def __init__(self, breaker: CircuitBreaker, **kwargs):
        super().__init__("DIVIPOLA (DANE)", "gdxc-w37w", breaker, limite_defecto=2000, **kwargs)