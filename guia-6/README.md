# Guía 6: Arquitectura Hexagonal e Integración de APIs de Datos Abiertos Colombianos

**Integrantes:** Ángel Samuel Peña Camargo y Daniel Chaves Muñoz
**Fecha de entrega:** según el calendario académico 2026-262
**Programa:** Ingeniería de Software — Universidad Manuela Beltrán  
**Materia:** Taller de Programación (Docente: Ing. Juan José Osorio Tabares)  
**Fecha de entrega:** 14 de octubre de 2026  
**Repositorio:** [cosmos-droid117/taller-programacion-2026](https://github.com/cosmos-droid117/taller-programacion-2026)  

---

## 📌 Descripción del Proyecto

Este proyecto corresponde al desarrollo de la **Guía 6 (Sesiones 11 y 12, PDA 2026-262)** de Taller de Programación. Consiste en la refactorización a **Arquitectura Hexagonal** de la API REST de productos de la Guía 5 (FastAPI) y en la integración de **dos fuentes de datos abiertos colombianos** con resiliencia y análisis estadístico. Se mantiene lo construido en la Guía 5 y se incorpora:
1. **5 Endpoints CRUD completos** con manejo estricto de códigos HTTP (`200`, `201`, `204`, `400`, `404`, `422`).
2. **Documentación interactiva en OpenAPI 3.0.2** (Swagger UI) completamente redactada en inglés.
3. **Integración de LLM (`gemini-3.5-flash-lite`)** en la ruta `/api/v1/ai` con manejo defensivo de errores (`504 Gateway Timeout`, `429 Rate Limit`, `503 Service Unavailable`).
4. **Arquitectura RAG Básica (Retrieval-Augmented Generation)** para inyectar dinámicamente el catálogo de productos como contexto.
5. **Comparación empírica de técnicas de Prompt Engineering** (*Zero-Shot*, *Few-Shot* y *Chain-of-Thought*).
6. **Suite de pruebas automatizadas (`pytest`)** e **Integración Continua (CI)** mediante GitHub Actions.
7. **Arquitectura Hexagonal** en 4 capas (`domain`, `application`, `api`, `infrastructure`) más un paquete transversal `observability`.
8. **Inyección de dependencias por constructor** en 3 servicios (`ProductoService`, `AIService`, `AnalisisService`), probados con `unittest.mock`.
9. **Integración de 2 fuentes de datos.gov.co** (SECOP II y DIVIPOLA del DANE) con **circuit breaker de 3 estados** y **reintentos con backoff exponencial**.
10. **Análisis con DuckDB**: dos consultas SQL con estadísticas descriptivas sobre los datos de cada fuente.
11. **ADR en inglés** con los bounded contexts y las decisiones de arquitectura.

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
- **Analítica:** DuckDB `1.4.5` y pandas `2.3.3`
- **Pruebas (extra):** httpx y openapi-spec-validator

---

## 📂 Estructura del Proyecto (`guia-6/`)

guia-6/
├── main.py                    # Composition root: elige las implementaciones concretas
├── domain/                    # Núcleo: entidades, excepciones y puertos (sin dependencias externas)
├── application/               # Casos de uso: ProductoService, AIService, AnalisisService, RAG
├── api/                       # Capa HTTP: rutas, esquemas, manejadores de error, docs y observabilidad
├── infrastructure/            # Adaptadores: repositorio, Gemini, JSONL, SECOP II, DIVIPOLA, DuckDB, resiliencia
├── observability/             # Logs y métricas (transversal)
├── docs/adr/                  # Architecture Decision Record (en inglés)
├── tests/                     # Suite de pruebas automatizadas
├── demo_resiliencia.py        # Evidencia: circuit breaker y reintentos (fallos simulados)
├── demo_apis.py               # Evidencia: respuesta real de las 2 APIs
├── demo_analisis.py           # Evidencia: consultas DuckDB sobre datos reales
├── llamadas_prompting.py      # Script de automatización para pruebas de prompting
├── pruebas_fallas.py          # Script de pruebas de fallas
├── llamadas_llm.jsonl         # Auditoría y registro histórico de llamadas al LLM
├── resultados_prompting.json  # Métricas detalladas de latencia, tokens y respuestas
├── pytest.ini                 # Configuración de pytest
└── requirements.txt           # Dependencias del proyecto

---

## 🧱 Arquitectura Hexagonal

| Capa | Responsabilidad | Depende de |
|---|---|---|
| `domain` | Entidades (`Producto`), excepciones sin códigos HTTP y puertos (interfaces) | Nada externo |
| `application` | Casos de uso: `ProductoService`, `AIService`, `AnalisisService` y RAG | `domain` |
| `api` | Rutas FastAPI, esquemas, traducción de errores de dominio a HTTP | `application`, `domain` |
| `infrastructure` | Adaptadores: repositorio en memoria, Gemini, JSONL, SECOP II, DIVIPOLA, DuckDB, resiliencia | `domain` |
| `observability` | Logs y métricas (transversal) | Nada del proyecto |

`main.py` es el **composition root**: el único lugar donde se eligen las implementaciones concretas y se inyectan por constructor. En las pruebas se reemplazan con `dependency_overrides` o con `Mock(spec=Puerto)`.

---

## 🌐 APIs de datos abiertos colombianos

| Fuente | Dataset (datos.gov.co) | Uso |
|---|---|---|
| SECOP II – Procesos de Contratación | `p6dx-8zbt` | `precio_base` agrupado por `departamento_entidad` |
| DIVIPOLA – Códigos de municipios (DANE) | `gdxc-w37w` | Número de municipios por departamento |

Cada fuente tiene su **propio circuit breaker** (CLOSED → OPEN → HALF_OPEN) y usa **reintentos con backoff exponencial** (0.5 s, 1 s, 2 s). Si una fuente falla, el sistema lanza `FuenteDatosNoDisponible`, y la capa `api` la traduce a HTTP.

Los valores numéricos llegan como texto (algunos con coma decimal), y DuckDB los convierte antes de calcular promedio, mediana, desviación, mínimo y máximo.

---

## ▶️ Cómo ejecutar

```powershell
cd guia-6
python -m pip install -r requirements.txt
$env:GEMINI_API_KEY = "tu-clave"   # solo para /api/v1/ai; nunca la subas al repositorio
python -m uvicorn main:app --reload
```

- Documentación interactiva: `http://127.0.0.1:8000/docs`
- Métricas: `http://127.0.0.1:8000/metricas`
- Pruebas: `python -m pytest`
- Evidencias: `python demo_resiliencia.py`, `python demo_apis.py` y `python demo_analisis.py`

---

## 🤖 Uso de herramientas de IA

Este proyecto se desarrolló con la asistencia de **Claude (Anthropic)**. No se usó GitHub Copilot. El código generado con IA se revisó, se ejecutó con la suite de pruebas y se corrigió cuando falló. Algunos ejemplos reales de errores detectados durante la refactorización:

- Bloques duplicados en `main.py` que producían un `NameError`.
- Rutas registradas dos veces, detectadas por los avisos de *Duplicate Operation ID* de `pytest`.
- Imports innecesarios de `observability` dentro de `domain`, detectados con `Select-String`.

`tests/test_ai.py` fue **adaptado** a la nueva arquitectura (usa `dependency_overrides[get_ai_service]`).

- Análisis de datos abiertos: `http://127.0.0.1:8000/analisis`
- Dashboard: `http://127.0.0.1:8000/dashboard`