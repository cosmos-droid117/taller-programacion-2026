from typing import Dict

from application.producto_service import ProductoService
from application.rag import construir_prompt, recuperar_productos
from domain.exceptions import LLMError
from domain.ports import LLMPort, LlamadaLogPort


class AIService:
    def __init__(self, llm: LLMPort, productos: ProductoService, registro: LlamadaLogPort):
        self._llm = llm
        self._productos = productos
        self._registro = registro

    def consultar(self, pregunta: str, tecnica: str, usar_rag: bool) -> Dict:
        contexto = recuperar_productos(pregunta, self._productos.listar()) if usar_rag else []
        prompt = construir_prompt(tecnica, pregunta, contexto)
        base = {"pregunta": pregunta, "tecnica": tecnica, "usar_rag": usar_rag, "prompt": prompt}
        try:
            resultado = self._llm.generar(prompt)
        except LLMError as exc:
            self._registro.registrar({**base, "error": type(exc).__name__})
            raise
        self._registro.registrar({**base, **resultado})
        return {**resultado, "productos_contexto": [p.id for p in contexto]}