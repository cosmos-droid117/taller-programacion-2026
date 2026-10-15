from openapi_spec_validator import validate

from main import app


def test_openapi_es_valido_3_0():
    """El contrato generado debe ser OpenAPI 3.0 válido (lo que pide la guía)."""
    esquema = app.openapi()
    assert esquema["openapi"].startswith("3.0")
    validate(esquema)
