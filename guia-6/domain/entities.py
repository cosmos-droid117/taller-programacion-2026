from pydantic import BaseModel, ConfigDict, Field

class ProductoBase(BaseModel):
    """Common fields to create or update a product."""
    nombre: str = Field(..., min_length=1, description="Product name (required)")
    categoria: str = Field(..., min_length=1, description="Product category")
    precio: float = Field(..., gt=0, description="Product price (must be greater than 0)")
    stock: int = Field(..., ge=0, description="Units available (cannot be negative)")


class Producto(ProductoBase):
    """Full representation of a stored product."""
    id: int = Field(..., description="Unique product identifier")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"id": 1, "nombre": "Laptop", "categoria": "Tecnología", "precio": 2500000, "stock": 10}
        }
    )