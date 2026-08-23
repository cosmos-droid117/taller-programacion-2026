# API de Productos — Guía 2 (Taller de Programación, UMB)

API REST desarrollada en Python con FastAPI para administrar productos de una empresa, aplicando operaciones CRUD (crear, consultar, actualizar y eliminar).

## Tecnologías utilizadas

- Python 3.9+
- FastAPI
- Uvicorn
- Pydantic

## Estructura del proyecto

```
├── main.py              # Endpoints de la API
├── models.py             # Modelos de datos (Producto) con validaciones
├── database.py            # Almacenamiento en memoria de los productos
├── requirements.txt        # Dependencias del proyecto
├── docs/
│   └── endpoints.md        # Documentación detallada de cada endpoint
└── evidencias/            # Capturas de las pruebas realizadas en Swagger UI
```

## Instalación

1. Clonar el repositorio:
   ```bash
   git clone <url-del-repositorio>
   cd <nombre-carpeta>
   ```

2. Crear y activar un entorno virtual:

   **Windows (PowerShell):**
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

   **Linux / macOS:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Instalar las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

## Ejecución

Levantar el servidor con Uvicorn:

```bash
python -m uvicorn main:app --reload
```

El servidor quedará disponible en: `http://127.0.0.1:8000`

## Documentación interactiva

Con el servidor corriendo, la documentación interactiva (Swagger UI) está disponible en:

```
http://127.0.0.1:8000/docs
```

Desde ahí se pueden probar los 5 endpoints directamente (GET, POST, PUT, DELETE) sin necesidad de herramientas externas. Los estilos de esta interfaz se cargan de forma local (no dependen de conexión a internet).

## Endpoints disponibles

| Método | Endpoint            | Función                     |
|--------|----------------------|------------------------------|
| GET    | /productos            | Consultar todos los productos |
| GET    | /productos/{id}        | Consultar un producto         |
| POST   | /productos            | Registrar un producto         |
| PUT    | /productos/{id}        | Actualizar un producto         |
| DELETE | /productos/{id}        | Eliminar un producto           |

Detalle completo de cada endpoint (parámetros, ejemplos de body, respuestas y códigos HTTP) en [`docs/endpoints.md`](docs/endpoints.md).

## Validaciones implementadas

- El nombre del producto es obligatorio.
- El precio debe ser mayor que 0.
- El stock no puede ser negativo.
- El id debe ser único al crear un producto.
- Los productos inexistentes generan una respuesta HTTP 404.

## Uso de Inteligencia Artificial

Como apoyo durante el desarrollo se utilizaron las herramientas de inteligencia artificial generativa **Claude** y **Devin.ai**, evaluando de forma crítica cada recomendación antes de incorporarla al proyecto. El detalle de este proceso se encuentra en el informe técnico entregado junto con este repositorio.

## Autor(es)

- Daniel Chaves Muñoz
- Angel Samuel Peña Camargo
- Universidad Manuela Beltrán (UMB) — Taller de Programación
