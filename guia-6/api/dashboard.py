from html import escape
from typing import Any, Dict, List

from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse

from api.dependencies import get_analisis_services
from application.analisis_service import AnalisisService
from domain.exceptions import FuenteDatosNoDisponible
from observability.logging_config import logger

router = APIRouter()

TOP_GRUPOS = 10
ETIQUETAS = {
    "n": "Count", "promedio": "Mean", "mediana": "Median",
    "desviacion": "Std. deviation", "minimo": "Minimum", "maximo": "Maximum",
}

CSS = """
:root{color-scheme:light dark;--bg:#fff;--fg:#1c1c1c;--muted:#666;--card:#f6f6f6;--line:#ddd;--bar:#2f6fed;--warn-bg:#fff4e5;--warn-fg:#7a4b00}
@media (prefers-color-scheme:dark){:root{--bg:#161616;--fg:#eee;--muted:#aaa;--card:#202020;--line:#333;--bar:#6c9bff;--warn-bg:#3a2b10;--warn-fg:#ffd699}}
body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,"Segoe UI",Arial,sans-serif}
main{max-width:860px;margin:0 auto;padding:24px 16px}
section{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:16px;margin:20px 0}
h1{font-size:1.5rem;margin:0 0 4px}
h2{font-size:1.15rem;margin:0 0 4px}
h3{font-size:1rem;margin:16px 0 4px}
.muted{color:var(--muted);margin:0 0 12px}
table{border-collapse:collapse;width:100%;max-width:480px}
th,td{text-align:left;padding:4px 10px;border-bottom:1px solid var(--line)}
td.num,th.num{text-align:right;font-variant-numeric:tabular-nums}
.chart{overflow-x:auto;margin-top:8px}
svg{width:100%;min-width:520px;height:auto}
.lbl,.val{font-size:12px;fill:var(--fg)}
.bar{fill:var(--bar)}
.warn{background:var(--warn-bg);color:var(--warn-fg);border-radius:8px;padding:10px 12px}
"""


def _fmt(valor: Any) -> str:
    if valor is None:
        return "-"
    if isinstance(valor, bool):
        return str(valor)
    if isinstance(valor, int):
        return f"{valor:,}"
    if isinstance(valor, float):
        return f"{valor:,.2f}"
    return escape(str(valor))


def _recortar(texto: str, maximo: int = 30) -> str:
    return texto if len(texto) <= maximo else texto[: maximo - 1] + "..."


def _tabla_estadisticas(estadisticas: Dict[str, Any]) -> str:
    filas = "".join(
        f'<tr><th scope="row">{escape(ETIQUETAS.get(clave, clave))}</th><td class="num">{_fmt(valor)}</td></tr>'
        for clave, valor in estadisticas.items()
    )
    return f"<table>{filas}</table>"


def _grafica(grupos: List[Dict[str, Any]]) -> str:
    top = grupos[:TOP_GRUPOS]
    if not top:
        return '<p class="muted">No groups to display.</p>'
    maximo = max(g["n"] for g in top) or 1
    x0, ancho_barra, alto_fila = 230, 320, 26
    filas = []
    for i, g in enumerate(top):
        y = i * alto_fila
        largo = max(2, round(g["n"] / maximo * ancho_barra))
        filas.append(
            f'<text x="{x0 - 8}" y="{y + 17}" text-anchor="end" class="lbl">{escape(_recortar(str(g["grupo"])))}</text>'
            f'<rect x="{x0}" y="{y + 4}" width="{largo}" height="16" rx="3" class="bar"/>'
            f'<text x="{x0 + largo + 6}" y="{y + 17}" class="val">{_fmt(g["n"])}</text>'
        )
    ancho, alto = x0 + ancho_barra + 60, len(top) * alto_fila
    return (
        f'<div class="chart"><svg viewBox="0 0 {ancho} {alto}" role="img" '
        f'aria-label="Records per group">{"".join(filas)}</svg></div>'
    )


def _tabla_grupos(grupos: List[Dict[str, Any]]) -> str:
    top = grupos[:TOP_GRUPOS]
    con_promedio = any("promedio" in g for g in top)
    encabezado = '<th>Group</th><th class="num">Count</th>' + ('<th class="num">Mean</th>' if con_promedio else "")
    filas = "".join(
        f'<tr><td>{escape(str(g["grupo"]))}</td><td class="num">{_fmt(g["n"])}</td>'
        + (f'<td class="num">{_fmt(g.get("promedio"))}</td>' if con_promedio else "")
        + "</tr>"
        for g in top
    )
    return f"<table><tr>{encabezado}</tr>{filas}</table>"


def _seccion(resultado: Dict[str, Any]) -> str:
    return (
        f'<section><h2>{escape(str(resultado["fuente"]))}</h2>'
        f'<p class="muted">{_fmt(resultado["total_registros"])} records analysed. '
        f'Metric: {escape(str(resultado["metrica"]))}</p>'
        f"<h3>Descriptive statistics</h3>{_tabla_estadisticas(resultado['estadisticas'])}"
        f"<h3>Top {TOP_GRUPOS} groups</h3>{_grafica(resultado['grupos'])}{_tabla_grupos(resultado['grupos'])}</section>"
    )


def _seccion_no_disponible(nombre: str) -> str:
    return (
        f"<section><h2>{escape(nombre)}</h2>"
        '<p class="warn">This data source is currently unavailable. The retry policy and the circuit breaker '
        "are protecting the application; reload in a few seconds.</p></section>"
    )


@router.get("/dashboard", response_class=HTMLResponse, include_in_schema=False)
def dashboard(servicios: Dict[str, AnalisisService] = Depends(get_analisis_services)):
    secciones = []
    for clave, servicio in servicios.items():
        try:
            secciones.append(_seccion(servicio.analizar()))
        except FuenteDatosNoDisponible as exc:
            nombre = getattr(exc, "fuente", clave)
            logger.warning(f"GET /dashboard - fuente no disponible: {nombre}")
            secciones.append(_seccion_no_disponible(nombre))
    logger.info(f"GET /dashboard - {len(servicios)} fuentes procesadas")
    return HTMLResponse(
        "<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\">"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
        f"<title>Open data dashboard</title><style>{CSS}</style></head><body><main>"
        "<h1>Open data dashboard</h1>"
        '<p class="muted">Statistics computed with DuckDB over live data from datos.gov.co.</p>'
        f"{''.join(secciones)}</main></body></html>"
    )