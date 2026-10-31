import json
import os
from datetime import datetime, timezone
from typing import Dict, Optional

from domain.ports import LlamadaLogPort


class JsonlLlamadaLog(LlamadaLogPort):
    """Agrega una línea por llamada al .jsonl (evidencia y base para estimar costos)."""

    def __init__(self, ruta: Optional[str] = None):
        self._ruta = ruta or os.getenv("LLM_LOG_PATH", "llamadas_llm.jsonl")

    def registrar(self, registro: Dict) -> None:
        registro = {"fecha": datetime.now(timezone.utc).isoformat(), **registro}
        with open(self._ruta, "a", encoding="utf-8") as f:
            f.write(json.dumps(registro, ensure_ascii=False) + "\n")