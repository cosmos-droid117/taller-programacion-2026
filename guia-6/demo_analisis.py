from application.analisis_service import AnalisisService
from infrastructure.datos_abiertos_adapters import DaneAdapter, DatosGovCoAdapter
from infrastructure.duckdb_analitica import SQL_ESTADISTICAS, SQL_POR_GRUPO, DuckDBAnalitica
from infrastructure.resilience import CircuitBreaker


def mostrar(resultado):
    print(f"\n=== {resultado['fuente']} ({resultado['total_registros']} registros) ===")
    print(f"Estadísticas descriptivas de: {resultado['metrica']}")
    for clave, valor in resultado["estadisticas"].items():
        print(f"  {clave}: {valor}")
    print("Top 5 grupos:")
    for g in resultado["grupos"][:5]:
        print(" ", g)


def main():
    print("Query 1:", SQL_ESTADISTICAS)
    print("Query 2:", SQL_POR_GRUPO)
    analitica = DuckDBAnalitica()
    servicios = (
        AnalisisService("SECOP II", DatosGovCoAdapter(CircuitBreaker("SECOP II")), analitica,
                        "departamento_entidad", "precio_base"),
        AnalisisService("DIVIPOLA (DANE)", DaneAdapter(CircuitBreaker("DIVIPOLA")), analitica, "dpto"),
    )
    for servicio in servicios:
        mostrar(servicio.analizar())


if __name__ == "__main__":
    main()