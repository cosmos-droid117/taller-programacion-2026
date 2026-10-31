from typing import Any, Dict, Optional

from domain.ports import AnaliticaPort, DatosAbiertosPort


class AnalisisService:
    """Obtiene registros de una fuente de datos abiertos y los analiza con una herramienta de analítica.

    Sin columna numérica, las estadísticas se calculan sobre el número de registros por grupo.
    """

    def __init__(self, nombre: str, fuente: DatosAbiertosPort, analitica: AnaliticaPort,
                 columna_grupo: str, columna_numerica: Optional[str] = None):
        self._nombre = nombre
        self._fuente = fuente
        self._analitica = analitica
        self._grupo = columna_grupo
        self._numerica = columna_numerica

    def analizar(self, limite: Optional[int] = None) -> Dict[str, Any]:
        registros = self._fuente.obtener_registros(limite)
        grupos = self._analitica.por_grupo(registros, self._grupo, self._numerica)
        if self._numerica:
            metrica = self._numerica
            estadisticas = self._analitica.estadisticas(registros, self._numerica)
        else:
            metrica = f"registros por {self._grupo}"
            estadisticas = self._analitica.estadisticas(grupos, "n")
        return {
            "fuente": self._nombre,
            "total_registros": len(registros),
            "metrica": metrica,
            "estadisticas": estadisticas,
            "grupos": grupos,
        }