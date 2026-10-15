from typing import Dict
from models import Producto

# "Base de datos" en memoria: se reinicia cada vez que se reinicia el servidor.
productos_db: Dict[int, Producto] = {
    1: Producto(id=1, nombre="Laptop", categoria="Tecnología", precio=2500000, stock=10),
    2: Producto(id=2, nombre="Mouse inalámbrico", categoria="Tecnología", precio=45000, stock=50),
    3: Producto(id=3, nombre="Teclado", categoria="Tecnología", precio=90000, stock=30),
    4: Producto(id=4, nombre="Monitor", categoria="Tecnología", precio=780000, stock=12),
    5: Producto(id=5, nombre="Audífonos", categoria="Audio", precio=120000, stock=25),
}