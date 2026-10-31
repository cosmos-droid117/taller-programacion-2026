from infrastructure.datos_abiertos_adapters import DaneAdapter, DatosGovCoAdapter
from infrastructure.resilience import CircuitBreaker


def main():
    adaptadores = (
        DatosGovCoAdapter(CircuitBreaker("SECOP II")),
        DaneAdapter(CircuitBreaker("DIVIPOLA")),
    )
    for adaptador in adaptadores:
        registros = adaptador.obtener_registros()
        print(f"\n{adaptador.nombre}: {len(registros)} registros")
        primero = registros[0]
        print("  Primer registro (5 campos):", {k: primero[k] for k in list(primero)[:5]})


if __name__ == "__main__":
    main()