# Guía 4 - Observabilidad y DevOps inteligente con IA

API REST de gestión de productos (construida en una guía anterior) a la que se le agregaron mecanismos de observabilidad: logs, métricas y manejo de errores, más un análisis de esos datos usando IA.

## Qué hay en esta carpeta

- `main.py` - endpoints de la API + middleware de logging/métricas + manejo global de errores
- `models.py` - esquemas de Producto con Pydantic
- `database.py` - "base de datos" en memoria (un diccionario)
- `logging_config.py` - configuración de logs (consola + archivo)
- `metrics.py` - conteo de peticiones, errores y tiempos de respuesta
- `pruebas_fallas.py` - script para provocar las 3 fallas controladas y generar evidencia
- `app.log` - logs generados durante las pruebas
- `requirements.txt` - dependencias del proyecto
- Informe técnico (PDF/Word) con todo el desarrollo completo de la guía

## Cómo correrlo

1. Crear el entorno virtual e instalar dependencias:

```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Levantar el servidor:

```bash
python -m uvicorn main:app --reload
```

3. Abrir la documentación interactiva en `http://127.0.0.1:8000/docs`

4. (Opcional) Con el servidor corriendo, en otra terminal ejecutar `python pruebas_fallas.py` para generar las 3 fallas controladas y ver las métricas.

## Endpoints

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/productos` | Lista todos los productos |
| GET | `/productos/{id}` | Consulta un producto por id |
| POST | `/productos` | Crea un producto |
| PUT | `/productos/{id}` | Actualiza un producto |
| DELETE | `/productos/{id}` | Elimina un producto |
| GET | `/metricas` | Muestra las métricas acumuladas |

## Fallas controladas para observabilidad

- `GET /productos/9999` → 404, producto que no existe
- `POST /productos` sin todos los campos requeridos → 422
- `GET /productos/500` → 500, simula una caída de la conexión a la base de datos (id reservado a propósito para esta prueba)

## Análisis con IA

El análisis de los logs usando IA (prompt, resultados y análisis crítico) está documentado completo en el informe técnico de esta entrega.
