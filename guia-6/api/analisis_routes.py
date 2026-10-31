from typing import Any, Dict, List, Literal

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from api.dependencies import get_analisis_services
from api.responses import RESPUESTA_422, error
from application.analisis_service import AnalisisService
from observability.logging_config import logger

router = APIRouter()


class AnalisisRespuesta(BaseModel):
    """Descriptive statistics computed with DuckDB over a sample of an open-data source."""
    fuente: str = Field(..., description="Name of the data source")
    total_registros: int = Field(..., description="Number of records analysed")
    metrica: str = Field(..., description="Column (or derived measure) the statistics refer to")
    estadisticas: Dict[str, Any] = Field(..., description="Count, mean, median, standard deviation, minimum and maximum")
    grupos: List[Dict[str, Any]] = Field(..., description="Records per group, largest group first")


@router.get(
    "/analisis/{fuente}",
    response_model=AnalisisRespuesta,
    tags=["Open Data"],
    operation_id="analyze_open_data",
    summary="Analyze an open-data source",
    description=(
        "Fetches records from a Colombian open-data API (with retries and a circuit breaker) and computes "
        "descriptive statistics with DuckDB. `secop`: SECOP II contracting processes grouped by "
        "`departamento_entidad`, with statistics on `precio_base`. `dane`: DIVIPOLA municipalities "
        "(published by DANE) grouped by department."
    ),
    responses={
        503: error(
            "The data source is unavailable (retries exhausted or circuit breaker open)",
            "Data source 'SECOP II' is currently unavailable",
        ),
        **RESPUESTA_422,
    },
)
def analizar_fuente(
    fuente: Literal["secop", "dane"],
    servicios: Dict[str, AnalisisService] = Depends(get_analisis_services),
):
    resultado = servicios[fuente].analizar()
    logger.info(f"GET /analisis/{fuente} - OK ({resultado['total_registros']} registros)")
    return resultado