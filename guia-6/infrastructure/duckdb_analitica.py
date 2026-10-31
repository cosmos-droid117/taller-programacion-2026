from typing import Any, Dict, List, Optional

import duckdb
import pandas as pd

from domain.ports import AnaliticaPort

SQL_ESTADISTICAS = (
    'SELECT COUNT("{c}") AS n, AVG("{c}") AS promedio, MEDIAN("{c}") AS mediana, '
    'STDDEV("{c}") AS desviacion, MIN("{c}") AS minimo, MAX("{c}") AS maximo FROM datos'
)
SQL_POR_GRUPO = (
    "SELECT COALESCE(CAST(\"{g}\" AS VARCHAR), '(sin dato)') AS grupo, COUNT(*) AS n{extra} "
    "FROM datos GROUP BY 1 ORDER BY n DESC, grupo"
)
EXTRA_PROMEDIO = ', AVG("{c}") AS promedio'


def _a_numero(serie: pd.Series) -> pd.Series:
    """Las APIs entregan los números como texto (a veces con coma decimal)."""
    texto = serie.astype(str).str.replace(",", ".", regex=False)
    return pd.to_numeric(texto, errors="coerce")


class DuckDBAnalitica(AnaliticaPort):
    """Estadísticas descriptivas con SQL sobre los registros JSON, usando DuckDB en memoria.

    Los nombres de columna se insertan en el SQL: se validan contra las columnas reales y solo
    deben venir de la configuración propia, nunca de la entrada del usuario.
    """

    @staticmethod
    def _validar(df: pd.DataFrame, *columnas: str) -> None:
        for c in columnas:
            if c not in df.columns:
                raise ValueError(f"La columna '{c}' no existe en los registros")

    @staticmethod
    def _consultar(df: pd.DataFrame, sql: str) -> List[Dict[str, Any]]:
        con = duckdb.connect()
        try:
            con.register("datos", df)
            cursor = con.execute(sql)
            nombres = [d[0] for d in cursor.description]
            return [dict(zip(nombres, fila)) for fila in cursor.fetchall()]
        finally:
            con.close()

    @staticmethod
    def _redondear(valor: Any) -> Any:
        return round(valor, 2) if isinstance(valor, float) else valor

    def estadisticas(self, registros: List[Dict[str, Any]], columna: str) -> Dict[str, Any]:
        vacio = {"n": 0, "promedio": None, "mediana": None, "desviacion": None, "minimo": None, "maximo": None}
        if not registros:
            return vacio
        df = pd.DataFrame(registros)
        self._validar(df, columna)
        df[columna] = _a_numero(df[columna])
        df = df.dropna(subset=[columna])
        if df.empty:
            return vacio
        fila = self._consultar(df, SQL_ESTADISTICAS.format(c=columna))[0]
        return {k: self._redondear(v) for k, v in fila.items()}

    def por_grupo(self, registros: List[Dict[str, Any]], columna_grupo: str,
                  columna_numerica: Optional[str] = None) -> List[Dict[str, Any]]:
        if not registros:
            return []
        df = pd.DataFrame(registros)
        self._validar(df, columna_grupo)
        extra = ""
        if columna_numerica:
            self._validar(df, columna_numerica)
            df[columna_numerica] = _a_numero(df[columna_numerica]).astype(object).where(
                lambda s: s.notna(), None
            )
            extra = EXTRA_PROMEDIO.format(c=columna_numerica)
        filas = self._consultar(df, SQL_POR_GRUPO.format(g=columna_grupo, extra=extra))
        return [{k: self._redondear(v) for k, v in f.items()} for f in filas]