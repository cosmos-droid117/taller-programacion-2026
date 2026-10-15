# Guía 5: APIs REST Modernas e Integración de LLMs

**Estudiante:** Ángel Samuel Peña Camargo  
**Programa:** Ingeniería de Software — Universidad Manuela Beltrán  
**Materia:** Taller de Programación (Docente: Ing. Juan José Osorio Tabares)  
**Fecha de entrega:** 14 de octubre de 2026  
**Repositorio:** [cosmos-droid117/taller-programacion-2026](https://github.com/cosmos-droid117/taller-programacion-2026)  

---

## 📌 Descripción del Proyecto

Este proyecto corresponde al desarrollo de la **Guía 5 (Sesiones 9 y 10)** de Taller de Programación. Consiste en la evolución y extensión de una API REST basada en **FastAPI** para la gestión de un catálogo de productos, incorporando:

1. **5 Endpoints CRUD completos** con manejo estricto de códigos HTTP (`200`, `201`, `204`, `400`, `404`, `422`).
2. **Documentación interactiva en OpenAPI 3.0.2** (Swagger UI) completamente redactada en inglés.
3. **Integración de LLM (`gemini-3.5-flash-lite`)** en la ruta `/api/v1/ai` con manejo defensivo de errores (`504 Gateway Timeout`, `429 Rate Limit`, `503 Service Unavailable`).
4. **Arquitectura RAG Básica (Retrieval-Augmented Generation)** para inyectar dinámicamente el catálogo de productos como contexto.
5. **Comparación empírica de técnicas de Prompt Engineering** (*Zero-Shot*, *Few-Shot* y *Chain-of-Thought*).
6. **Suite de pruebas automatizadas (`pytest`)** e **Integración Continua (CI)** mediante GitHub Actions.

---

## 🛠️ Stack Tecnológico y Requisitos

- **Lenguaje:** Python 3.9.13 (Entorno local) / Python 3.12 (CI Pipeline)
- **Framework Web:** FastAPI `0.115.0`
- **Servidor ASGI:** Uvicorn `0.30.6`
- **Validación de Datos:** Pydantic `2.9.2`
- **Cliente HTTP:** requests `2.32.3`
- **Documentación OpenAPI:** swagger-ui-bundle `1.1.0`
- **Framework de Pruebas:** pytest `8.x`
- **Modelo de IA:** Google Gemini 3.5 Flash-Lite (API REST vía Google AI Studio)

---

## 📂 Estructura del Proyecto (`guia-5/`)

```text
guia-5/
├── main.py                  # Servidor principal FastAPI, endpoints CRUD y middleware
├── models.py                # Esquemas Pydantic para validación de datos
├── database.py              # Base de datos en memoria (diccionario de productos)
├── ai.py                    # Integración con la API de Gemini, RAG y técnicas de prompt
├── metrics.py               # Métricas de rendimiento de la API
├── logging_config.py        # Configuración de logs del sistema
├── llamadas_prompting.py    # Script de automatización para pruebas de prompting
├── llamadas_llm.jsonl       # Auditoría y registro histórico de llamadas al LLM
├── resultados_prompting.json# Métricas detalladas de latencia, tokens y respuestas
├── requirements.txt         # Dependencias del proyecto
└── tests/                   # Suite de pruebas automatizadas
    ├── test_api.py          # Pruebas de integración CRUD y errores HTTP
    ├── test_ai.py           # Pruebas del endpoint /api/v1/ai y simulación de errores
    └── test_openapi.py      # Validación de especificación OpenAPI 3.0.2
