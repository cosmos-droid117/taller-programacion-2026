import os
import time
from typing import Dict, Optional

import requests

from domain.exceptions import LLMError, LLMRateLimit, LLMSinClave, LLMTimeout
from domain.ports import LLMPort

BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"


class GeminiClient(LLMPort):
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None, timeout: float = 20.0):
        self.api_key = api_key if api_key is not None else os.getenv("GEMINI_API_KEY")
        self.model = model or os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
        self.timeout = timeout

    def generar(self, prompt: str) -> Dict:
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