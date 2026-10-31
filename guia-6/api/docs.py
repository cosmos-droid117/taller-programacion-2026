from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.staticfiles import StaticFiles
from swagger_ui_bundle import swagger_ui_path


def _a_openapi_30(nodo):
    """Pydantic v2 emits JSON Schema 2020-12 keywords. OpenAPI 3.0 needs the boolean form
    of exclusiveMinimum/exclusiveMaximum, so convert them in place."""
    if isinstance(nodo, dict):
        for clave, limite in (("exclusiveMinimum", "minimum"), ("exclusiveMaximum", "maximum")):
            valor = nodo.get(clave)
            if isinstance(valor, (int, float)) and not isinstance(valor, bool):
                nodo[limite] = valor
                nodo[clave] = True
        for valor in nodo.values():
            _a_openapi_30(valor)
    elif isinstance(nodo, list):
        for valor in nodo:
            _a_openapi_30(valor)


def registrar_docs(app: FastAPI) -> None:
    def openapi_personalizado():
        # El swagger-ui-bundle local no soporta OpenAPI 3.1, por eso se fija 3.0.2
        if app.openapi_schema:
            return app.openapi_schema
        esquema = get_openapi(
            title=app.title,
            version=app.version,
            openapi_version="3.0.2",
            description=app.description,
            routes=app.routes,
            tags=app.openapi_tags,
        )
        _a_openapi_30(esquema)
        app.openapi_schema = esquema
        return esquema

    app.openapi = openapi_personalizado
    app.mount("/swagger-static", StaticFiles(directory=swagger_ui_path), name="swagger-static")

    @app.get("/docs", include_in_schema=False)
    def docs_local():
        """Documentación interactiva Swagger UI, cargada con archivos locales."""
        return get_swagger_ui_html(
            openapi_url=app.openapi_url,
            title=f"{app.title} - Docs",
            swagger_js_url="/swagger-static/swagger-ui-bundle.js",
            swagger_css_url="/swagger-static/swagger-ui.css",
        )