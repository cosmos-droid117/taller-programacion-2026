# Documentación de Endpoints — API de Productos

Documentación interactiva generada automáticamente por FastAPI disponible en:
`http://127.0.0.1:8000/docs`

## Recurso: Producto

| Campo     | Tipo    | Regla de validación              |
|-----------|---------|-----------------------------------|
| id        | Entero  | Único, obligatorio al crear       |
| nombre    | Texto   | Obligatorio (no puede ir vacío)   |
| categoria | Texto   | Obligatorio                       |
| precio    | Decimal | Debe ser mayor que 0              |
| stock     | Entero  | No puede ser negativo (≥ 0)       |

---

## GET /productos

Consulta todos los productos registrados.

**Respuesta exitosa — 200 OK**
```json
[
  {
    "id": 1,
    "nombre": "Laptop",
    "categoria": "Tecnología",
    "precio": 2500000,
    "stock": 10
  }
]
```

---

## GET /productos/{id}

Consulta un producto específico por su id.

**Parámetros de ruta**
- `id` (entero, requerido): identificador del producto.

**Respuesta exitosa — 200 OK**
```json
{
  "id": 1,
  "nombre": "Laptop",
  "categoria": "Tecnología",
  "precio": 2500000,
  "stock": 10
}
```

**Respuesta de error — 404 Not Found** (el producto no existe)
```json
{
  "detail": "No existe un producto con id 99"
}
```

---

## POST /productos

Registra un nuevo producto.

**Cuerpo de la solicitud (JSON)**
```json
{
  "id": 3,
  "nombre": "Teclado",
  "categoria": "Tecnología",
  "precio": 80000,
  "stock": 15
}
```

**Respuesta exitosa — 201 Created**
Devuelve el producto creado.

**Respuesta de error — 400 Bad Request** (el id ya existe)
```json
{
  "detail": "Ya existe un producto con id 3"
}
```

**Respuesta de error — 422 Unprocessable Entity** (datos inválidos, ej. precio ≤ 0, nombre vacío, stock negativo)
```json
{
  "detail": [
    {
      "loc": ["body", "precio"],
      "msg": "Input should be greater than 0",
      "type": "greater_than"
    }
  ]
}
```

---

## PUT /productos/{id}

Actualiza un producto existente. El id se especifica en la URL y no puede modificarse.

**Parámetros de ruta**
- `id` (entero, requerido): identificador del producto a actualizar.

**Cuerpo de la solicitud (JSON)**
```json
{
  "nombre": "Laptop Pro",
  "categoria": "Tecnología",
  "precio": 3000000,
  "stock": 8
}
```

**Respuesta exitosa — 200 OK**
Devuelve el producto actualizado.

**Respuesta de error — 404 Not Found** (el producto no existe)
```json
{
  "detail": "No existe un producto con id 99"
}
```

---

## DELETE /productos/{id}

Elimina un producto existente.

**Parámetros de ruta**
- `id` (entero, requerido): identificador del producto a eliminar.

**Respuesta exitosa — 204 No Content**
Sin cuerpo de respuesta.

**Respuesta de error — 404 Not Found** (el producto no existe)
```json
{
  "detail": "No existe un producto con id 99"
}
```

---

## Resumen de códigos HTTP utilizados

| Código | Significado           | Cuándo ocurre                                      |
|--------|------------------------|-----------------------------------------------------|
| 200    | OK                     | Consulta o actualización exitosa                    |
| 201    | Created                | Producto creado exitosamente                        |
| 204    | No Content             | Producto eliminado exitosamente                      |
| 400    | Bad Request            | Intento de crear un producto con un id repetido     |
| 404    | Not Found              | Se intenta consultar/actualizar/eliminar un id que no existe |
| 422    | Unprocessable Entity   | Los datos enviados no cumplen las validaciones (precio, nombre, stock) |
