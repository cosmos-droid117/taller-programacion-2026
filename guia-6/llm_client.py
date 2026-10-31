import json
import os
import time
from datetime import datetime, timezone
from typing import Optional

import requests

BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"
RUTA_LOG = os.getenv("LLM_LOG_PATH", "llamadas_llm.jsonl")


class LLMError(Exception):
    status_code = 502
    detalle = "The LLM provider returned an error"


class LLMTimeout(LLMError):
    status_code = 504
    detalle = "The LLM provider did not respond in time"


class LLMRateLimit(LLMError):
    status_code = 429
    detalle = "LLM rate limit reached, try again later"


class LLMSinClave(LLMError):
    status_code = 503
    detalle = "LLM API key is not configured"


class GeminiClient:
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None, timeout: float = 20.0):
        self.api_key = api_key if api_key is not None else os.getenv("GEMINI_API_KEY")
        self.model = model or os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
        self.timeout = timeout

    def generar(self, prompt: str) -> dict:
        if not self.api_key:
            raise LLMSinClave()
        inicio = time.perf_counter()
        try:
            r = requests.post(
                f"{BASE_URL}/{self.model}:generateContent",
                headers={"x-goog-api-key": self.api_key, "Content-Type": "application/json"},
                json={"contents": [{"parts": [{"text": prompt}]}]},
                timeout=self.timeout,
            )
        except requests.Timeout:
            raise LLMTimeout()
        except requests.RequestException:
            raise LLMError()
        if r.status_code == 429:
            raise LLMRateLimit()
        if r.status_code >= 400:
            raise LLMError()
        datos = r.json()
        try:
            partes = datos["candidates"][0]["content"]["parts"]
            texto = "".join(p.get("text", "") for p in partes)
        except (KeyError, IndexError, TypeError):
            raise LLMError()
        uso = datos.get("usageMetadata", {})
        return {
            "respuesta": texto,
            "modelo": self.model,
            "tokens_entrada": uso.get("promptTokenCount", 0),
            "tokens_salida": uso.get("candidatesTokenCount", 0),
            "tokens_razonamiento": uso.get("thoughtsTokenCount", 0),
            "latencia_ms": round((time.perf_counter() - inicio) * 1000, 1),
        }


def registrar_llamada(registro: dict) -> None:
    """Agrega una línea al archivo .jsonl (evidencia y base para estimar costos)."""
    registro = {"fecha": datetime.now(timezone.utc).isoformat(), **registro}
    with open(RUTA_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(registro, ensure_ascii=False) + "\n")    