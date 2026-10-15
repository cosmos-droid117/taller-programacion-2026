from pydantic import BaseModel, Field


class ProductoBase(BaseModel):
    """Campos comunes para crear o actualizar un producto."""
    nombre: str = Field(..., min_length=1, description="Nombre del producto (obligatorio)")
    categoria: str = Field(..., min_length=1, description="Categoría del producto")
    precio: float = Field(..., gt=0, description="Precio del producto (debe ser mayor que 0)")
    stock: int = Field(..., ge=0, description="Cantidad disponible (no puede ser negativa)")


class ProductoCrear(ProductoBase):
    """Datos requeridos para crear un producto. El id lo asigna el cliente."""
    id: int = Field(..., description="Identificador único del producto")


class ProductoActualizar(ProductoBase):
    """Datos para actualizar un producto existente (no incluye id, viene en la URL)."""
    pass


class Producto(ProductoBase):
    """Representación completa de un producto almacenado."""
    id: int