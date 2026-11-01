# ADR 0001: Hexagonal architecture, bounded contexts and resilient open-data integration

- **Status:** Accepted
- **Date:** 2026-10-31
- **Authors:** Ángel Samuel Peña Camargo and Daniel Chaves Muñoz
- **Project:** Taller de Programación, Guide 6 (Sessions 11 and 12), UMB

## Context

The semester project is a FastAPI service that manages a product catalog (CRUD). Across Guides 2, 4 and 5 it grew incrementally: it gained logging and metrics, and then an endpoint that answers questions about the catalog with an LLM (prompting techniques and RAG). During that growth, business rules, HTTP handling and access to external systems ended up mixed in `main.py`. This made it hard to test each part in isolation and to replace any external component.

Guide 6 adds new requirements: a hexagonal architecture with constructor-based dependency injection, explicit bounded contexts, integration of Colombian open-data APIs protected with a circuit breaker and retries with exponential backoff, and analytical processing of the JSON data with DuckDB. Throughout the work the CI/CD pipeline had to stay green.

## Decision drivers

- Test each layer in isolation, without network access or real external services.
- Keep the observable behavior of the existing API unchanged while refactoring.
- A failure of an external API must not take the application down.
- Keep the domain free of framework and infrastructure details.

## Considered options

1. **Keep the flat structure** and add the new features to it. Rejected: coupling would keep growing and the external APIs could not be isolated for testing.
2. **Hexagonal architecture (ports and adapters)** with four layers. Chosen.
3. **Use existing resilience libraries** (for example `tenacity` or `pybreaker`) instead of our own code. Rejected: a small implementation with an injectable clock and sleep function lets the tests cover all three circuit states without waiting, and it keeps the behavior transparent for the course.

## Decision

### Layers and dependency rule

Dependencies always point towards the domain.

```mermaid
flowchart LR
    main["main.py (composition root)"] -.-> api
    main -.-> application
    main -.-> infrastructure
    api --> application
    application --> domain
    infrastructure --> domain
    api --> observability
    infrastructure --> observability
```

| Layer | Responsibility | Main elements |
|---|---|---|
| `domain` | Business concepts and the contracts the application needs | `Producto`, domain exceptions, ports: `ProductoRepositoryPort`, `LLMPort`, `LlamadaLogPort`, `DatosAbiertosPort`, `AnaliticaPort` |
| `application` | Use cases | `ProductoService`, `AIService` (with RAG), `AnalisisService` |
| `api` | Driving adapter: HTTP | Routers, schemas, dashboard, translation of domain errors to HTTP status codes |
| `infrastructure` | Driven adapters | In-memory repository, Gemini client, JSONL call log, circuit breaker and retries, Socrata adapters for datos.gov.co, DuckDB analytics |
| `observability` | Cross-cutting logging and metrics | Logger configuration, request metrics |

`main.py` is the composition root: it is the only place that chooses the concrete implementations and wires them into the services. The API layer receives the services through FastAPI `Depends` and `app.state`, so tests can replace any of them with `dependency_overrides`.

### Bounded contexts

- **Catalog:** the `Producto` entity and its CRUD rules (unique id, price greater than zero, stock not negative).
- **AI Assistant:** prompting techniques, RAG and the LLM call. It consumes the Catalog only through `ProductoService`, never through its repository.
- **Open Data Analytics:** retrieval of external datasets and descriptive statistics. It has no dependency on the Catalog. SECOP II (dataset `p6dx-8zbt`) and DIVIPOLA published by DANE (dataset `gdxc-w37w`) are consumed through datos.gov.co.
- **Observability** is cross-cutting and is shared by the three contexts. It lives outside `infrastructure` so that the API layer never has to import it.

### Error handling

Domain exceptions carry no HTTP information. The API layer translates them in one place: `ProductoNoEncontrado` to 404, `ProductoDuplicado` to 400, LLM errors to 504, 429, 503 or 502, and `FuenteDatosNoDisponible` to 503.

### Resilience for external APIs

- One `CircuitBreaker` per external API, created once at startup because its state lives in the process. Three states: CLOSED, OPEN and HALF_OPEN. It opens after 3 consecutive failures and tries again after a 30 s cooldown.
- Retries with exponential backoff (0.5 s, 1 s) for up to 3 attempts. An open circuit is never retried.
- Any final failure is translated to the domain error `FuenteDatosNoDisponible`. The dashboard shows a notice for the affected source and keeps working with the others.

### Analytics

DuckDB is used as an embedded analytical engine behind `AnaliticaPort`, with two SQL queries: descriptive statistics (count, mean, median, standard deviation, minimum and maximum) and counts per group. Text values and decimal commas are converted to numbers before the analysis. The results are exposed at `GET /analisis/{fuente}` and shown on `/dashboard`.

## Consequences

### Positive

- Each layer can be tested without network access: the application services are tested with mocks of the ports, and the API is tested by injecting fake services. The full test suite passes locally and in the CI pipeline.
- The existing API tests kept passing with minimal changes (`test_openapi.py` is unchanged and `test_api.py` only needed a one-line import change), which is evidence that the observable behavior was preserved by the refactoring.
- External systems (LLM provider, datasets, database) can be replaced by writing a new adapter, with no change to the domain or the application layer.
- The failure of an external API is contained: clients get a 503 and the rest of the application keeps working.
- The dependency rule can be checked mechanically: neither `domain` nor `api` imports `infrastructure`.

### Negative and trade-offs

- More files and indirection for a small application.
- `Producto` inherits from Pydantic inside the domain. This is a conscious concession: the validation rules are business rules, and separating them would cost more than it gives.
- Services are delivered through `app.state`, which is less explicit than pure constructor injection and depends on `main.py` setting them up correctly.
- The circuit breaker state is per process: it is not shared between several workers.
- The dashboard queries the APIs on every visit, in the request thread, with no cache.
- The in-memory repository loses its data when the server restarts.
- DIVIPOLA is published by DANE but is served through datos.gov.co, so both sources use the same platform. We did not find an independent DANE JSON endpoint.
- Test code had to be adapted: `test_ai.py` was rewritten because the injection point of the LLM service moved, and `test_api.py` needed a one-line import change because the seed data moved to `main.py`.
- One log line from the previous version disappeared: the "simulated connection failure" message for product id 500 (the generic internal-error log is still emitted).

## Verification

- Automated test suite and the CI pipeline (GitHub Actions) on every push.
- Static checks of the dependency rule with `Select-String` on the `domain` and `api` folders.
- Manual check of the resilience behavior by running the server and disconnecting the network.