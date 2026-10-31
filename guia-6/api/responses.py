from models import ErrorResponse, ValidationErrorResponse


def error(descripcion: str, ejemplo: str) -> dict:
    return {
        "model": ErrorResponse,
        "description": descripcion,
        "content": {"application/json": {"example": {"detail": ejemplo}}},
    }


RESPUESTA_404 = {404: error("Product not found", "No product with id 999 exists")}
RESPUESTA_422 = {
    422: {
        "model": ValidationErrorResponse,
        "description": "Invalid or incomplete input data",
        "content": {
            "application/json": {
                "example": {
                    "detail": "Invalid or incomplete input data",
                    "errors": [
                        {
                            "type": "greater_than",
                            "loc": ["body", "precio"],
                            "msg": "Input should be greater than 0",
                            "input": -5,
                            "ctx": {"gt": 0.0},
                        }
                    ],
                }
            }
        },
    }
}
RESPUESTA_500 = {500: error("Unexpected server error", "Internal server error")}