"""
Ejecuta las 3 situaciones de falla controlada que pide el Paso 3 de la guía.
Corre el servidor primero (uvicorn main:app --reload) y luego este script.
"""
import requests

BASE_URL = "http://127.0.0.1:8000"

print("=== Falla 1: consultar un registro inexistente ===")
r = requests.get(f"{BASE_URL}/productos/9999")
print(r.status_code, r.json())

print("\n=== Falla 2: enviar información incompleta ===")
r = requests.post(f"{BASE_URL}/productos", json={"id": 99, "nombre": "Teclado"})
print(r.status_code, r.json())

print("\n=== Falla 3: error de conexión con la base de datos (simulado) ===")
r = requests.get(f"{BASE_URL}/productos/500")
print(r.status_code, r.json())

print("\n=== Métricas acumuladas ===")
r = requests.get(f"{BASE_URL}/metricas")
print(r.json())