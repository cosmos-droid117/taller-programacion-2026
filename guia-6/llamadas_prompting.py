"""Hace 16 llamadas al endpoint /api/v1/ai: 4 preguntas x 3 técnicas (con RAG)
+ 4 preguntas sin RAG (zero-shot) como línea base. Guarda los resultados en
resultados_prompting.json y resultados_prompting.md."""
import json
import re
import sys
import time

import requests

sys.stdout.reconfigure(encoding="utf-8")

URL = "http://127.0.0.1:8000/api/v1/ai"
PREGUNTAS = [
    ("Q1", "¿Cuánto cuestan en total 2 laptops y 3 mouse?"),
    ("Q2", "¿Cuál es el producto más barato y cuánto stock tiene?"),
    ("Q3", "¿Qué productos puedo comprar con 100000 pesos?"),
    ("Q4", "¿Venden tablets?"),
]
TECNICAS = ["zero-shot", "few-shot", "cot"]


def solo_digitos(texto):
    return re.sub(r"[.,$'\s]", "", texto)


def chequeo_auto(qid, texto):
    """Revisión automática solo donde la respuesta correcta es inequívoca."""
    t = texto.lower()
    if qid == "Q1":
        return "5135000" in solo_digitos(texto)
    if qid == "Q2":
        return "mouse" in t and "45000" in solo_digitos(texto) and bool(re.search(r"\b50\b", texto))
    return None  # Q3 y Q4: revisión manual


def llamar(pregunta, tecnica, usar_rag):
    cuerpo = {"pregunta": pregunta, "tecnica": tecnica, "usar_rag": usar_rag}
    for intento in range(3):
        r = requests.post(URL, json=cuerpo, timeout=60)
        if r.status_code == 429 and intento < 2:
            print("  429, espero 30 s y reintento...")
            time.sleep(30)
            continue
        return r
    return r


combinaciones = [(q, t, True) for q in PREGUNTAS for t in TECNICAS]
combinaciones += [(q, "zero-shot", False) for q in PREGUNTAS]

resultados = []
for (qid, pregunta), tecnica, usar_rag in combinaciones:
    print(f"{qid} | {tecnica} | rag={usar_rag}")
    r = llamar(pregunta, tecnica, usar_rag)
    fila = {"id": qid, "pregunta": pregunta, "tecnica": tecnica, "usar_rag": usar_rag, "status": r.status_code}
    if r.status_code == 200:
        d = r.json()
        fila.update(
            respuesta=d["respuesta"],
            tokens_entrada=d["tokens_entrada"],
            tokens_salida=d["tokens_salida"],
            tokens_razonamiento=d["tokens_razonamiento"],
            latencia_ms=d["latencia_ms"],
            ok_auto=chequeo_auto(qid, d["respuesta"]),
        )
    else:
        fila["error"] = r.text[:200]
    resultados.append(fila)
    time.sleep(4)  # evita golpear el rate limit

with open("resultados_prompting.json", "w", encoding="utf-8") as f:
    json.dump(resultados, f, ensure_ascii=False, indent=2)

with open("resultados_prompting.md", "w", encoding="utf-8") as f:
    f.write("| # | Pregunta | Técnica | RAG | Tokens in | Tokens out | ms | Auto | Evaluación manual (0-2) |\n")
    f.write("|---|---|---|---|---|---|---|---|---|\n")
    for i, x in enumerate(resultados, 1):
        auto = {True: "OK", False: "FALLA", None: "manual"}[x.get("ok_auto")] if x["status"] == 200 else f"HTTP {x['status']}"
        f.write(
            f"| {i} | {x['id']} | {x['tecnica']} | {'sí' if x['usar_rag'] else 'no'} | "
            f"{x.get('tokens_entrada', '-')} | {x.get('tokens_salida', '-')} | {x.get('latencia_ms', '-')} | {auto} |  |\n"
        )
    f.write("\n## Respuestas completas\n")
    for i, x in enumerate(resultados, 1):
        f.write(f"\n### {i}. {x['id']} | {x['tecnica']} | rag={x['usar_rag']}\n")
        f.write(f"**Pregunta:** {x['pregunta']}\n\n")
        f.write(f"**Respuesta:** {x.get('respuesta', x.get('error'))}\n")

print("Listo: resultados_prompting.json y resultados_prompting.md")