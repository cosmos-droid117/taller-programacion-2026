from fastapi import APIRouter, Body, Depends

from api.dependencies import get_ai_service
from api.responses import RESPUESTA_422, error as _error
from application.ai_service import AIService
from logging_config import logger
from models import AIConsulta, AIRespuesta

router = APIRouter()


@router.post(
    "/api/v1/ai",
    response_model=AIRespuesta,
    tags=["AI"],
    operation_id="ask_ai",
    summary="Ask the LLM about the product catalog",
    description=(
        "Builds a prompt with the chosen technique (`zero-shot`, `few-shot` or `cot`), optionally adds the "
        "catalog products that match the question as context (RAG) and queries the LLM. If no product "
        "matches, the whole catalog is sent. Every call is logged to `llamadas_llm.jsonl`."
    ),
    responses={
        429: _error("LLM rate limit reached", "LLM rate limit reached, try again later"),
        502: _error("The LLM provider returned an error", "The LLM provider returned an error"),
        503: _error("The LLM API key is not configured", "LLM API key is not configured"),
        504: _error("The LLM provider did not respond in time", "The LLM provider did not respond in time"),
        **RESPUESTA_422,
    },
)
def consultar_ai(
    consulta: AIConsulta = Body(
        ...,
        openapi_examples={
            "cot_with_rag": {
                "summary": "Chain-of-thought with RAG",
                "value": {"pregunta": "¿Cuánto cuestan en total 2 laptops y 3 mouse?", "tecnica": "cot", "usar_rag": True},
            },
            "few_shot": {
                "summary": "Few-shot with RAG",
                "value": {"pregunta": "¿Venden tablets?", "tecnica": "few-shot", "usar_rag": True},
            },
            "zero_shot_no_rag": {
                "summary": "Zero-shot without RAG (baseline)",
                "value": {"pregunta": "¿Cuál es el producto más barato?", "tecnica": "zero-shot", "usar_rag": False},
            },
        },
    ),
    servicio: AIService = Depends(get_ai_service),
):
    resultado = servicio.consultar(consulta.pregunta, consulta.tecnica, consulta.usar_rag)
    logger.info(f"POST /api/v1/ai - OK ({consulta.tecnica}, rag={consulta.usar_rag})")
    return AIRespuesta(tecnica=consulta.tecnica, usar_rag=consulta.usar_rag, **resultado)