import threading
from typing import Dict


class Metricas:
    """Almacena en memoria las métricas de comportamiento de la API.

    Cumple con el mínimo de 5 métricas que pide la guía:
    1. total_peticiones
    2. peticiones_por_endpoint
    3. operaciones_exitosas
    4. operaciones_fallidas
    5. tasa_error_porcentaje
    6. tiempo_respuesta_promedio_ms  (bono)
    """

    def __init__(self):
        self._lock = threading.Lock()
        self.total_peticiones = 0
        self.peticiones_por_endpoint: Dict[str, int] = {}
        self.operaciones_exitosas = 0
        self.operaciones_fallidas = 0
        self.tiempos_respuesta_ms = []

    def registrar(self, endpoint: str, exitosa: bool, duracion_ms: float) -> None:
        with self._lock:
            self.total_peticiones += 1
            self.peticiones_por_endpoint[endpoint] = (
                self.peticiones_por_endpoint.get(endpoint, 0) + 1
            )
            if exitosa:
                self.operaciones_exitosas += 1
            else:
                self.operaciones_fallidas += 1
            self.tiempos_respuesta_ms.append(duracion_ms)

    def resumen(self) -> dict:
        with self._lock:
            total = self.total_peticiones
            tasa_error = (
                (self.operaciones_fallidas / total * 100) if total else 0.0
            )
            tiempo_promedio = (
                sum(self.tiempos_respuesta_ms) / len(self.tiempos_respuesta_ms)
                if self.tiempos_respuesta_ms
                else 0.0
            )
            return {
                "total_peticiones": total,
                "peticiones_por_endpoint": dict(self.peticiones_por_endpoint),
                "operaciones_exitosas": self.operaciones_exitosas,
                "operaciones_fallidas": self.operaciones_fallidas,
                "tasa_error_porcentaje": round(tasa_error, 2),
                "tiempo_respuesta_promedio_ms": round(tiempo_promedio, 2),
            }


metricas = Metricas()