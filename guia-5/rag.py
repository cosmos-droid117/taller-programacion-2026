import re
import unicodedata
from typing import List

from models import Producto

STOPWORDS = {
    "que", "los", "las", "del", "con", "por", "para", "una", "uno", "unos", "unas",
    "cual", "cuales", "cuanto", "cuantos", "cuesta", "tiene", "tienen", "venden",
    "hay", "mas", "como", "puedo", "comprar",
}

INSTRUCCION = (
    "Eres el asistente de una tienda. Responde en español usando SOLO la información "
    "del catálogo. Si lo que se pregunta no está en el catálogo, dilo claramente y "
    "no inventes productos ni precios."
)

EJEMPLOS = """Ejemplos:
Catálogo:
- id 90 | Silla | Oficina | $200000 | stock 4
- id 91 | Escritorio | Oficina | $500000 | stock 2
Pregunta: ¿Cuánto cuestan 2 sillas?
Respuesta: 2 sillas cuestan $400000 (2 x $200000).

Catálogo:
- id 90 | Silla | Oficina | $200000 | stock 4
Pregunta: ¿Venden lámparas?
Respuesta: No, en el catálogo no hay lámparas."""


def _normalizar(texto: str) -> str:
    texto = unicodedata.normalize("NFD", texto.lower())
    return "".join(c for c in texto if unicodedata.category(c) != "Mn")


def _palabras(texto: str) -> set:
    palabras = re.findall(r"[a-z0-9]+", _normalizar(texto))
    return {p[:-1] if len(p) > 3 and p.endswith("s") else p for p in palabras if len(p) >= 3}


def recuperar_productos(pregunta: str, productos: List[Producto]) -> List[Producto]:
    """Recupera productos cuyo nombre o categoría comparte palabras con la pregunta.
    Si no hay coincidencias, devuelve todo el catálogo."""
    claves = _palabras(pregunta) - STOPWORDS
    coincidencias = [p for p in productos if claves & _palabras(f"{p.nombre} {p.categoria}")]
    return coincidencias if coincidencias else list(productos)


def formatear_catalogo(productos: List[Producto]) -> str:
    return "\n".join(
        f"- id {p.id} | {p.nombre} | {p.categoria} | ${p.precio:.0f} | stock {p.stock}"
        for p in productos
    )


def construir_prompt(tecnica: str, pregunta: str, productos: List[Producto]) -> str:
    partes = [INSTRUCCION]
    if tecnica == "few-shot":
        partes.append(EJEMPLOS)
    if productos:
        partes.append("Catálogo:\n" + formatear_catalogo(productos))
    else:
        partes.append("Catálogo: (no disponible)")
    partes.append(f"Pregunta: {pregunta}")
    if tecnica == "cot":
        partes.append("Razona paso a paso y termina con una línea que diga 'Respuesta final: ...'.")
    partes.append("Respuesta:")
    return "\n\n".join(partes)