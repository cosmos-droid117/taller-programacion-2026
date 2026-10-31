"""Demo para las Figuras 7 y 8: genera los logs del circuit breaker y de los reintentos.
Usa fallos simulados y esperas reales cortas. Ejecutar: python demo_resiliencia.py"""
import time

from infrastructure.resilience import CircuitBreaker, CircuitOpenError, con_reintentos


def falla():
    raise ConnectionError("API no disponible (simulado)")


def main():
    print("\n=== FIGURA 8: reintentos con backoff exponencial ===")
    intentos = []

    def inestable():
        intentos.append(1)
        if len(intentos) < 3:
            raise ConnectionError("fallo transitorio (simulado)")
        return "ok"

    print("Resultado:", con_reintentos(inestable, nombre="demo"))

    print("\n--- Reintentos agotados ---")
    try:
        con_reintentos(falla, nombre="demo")
    except ConnectionError:
        print("Se agotaron los reintentos y se propagó el error")

    print("\n=== FIGURA 7: estados del circuit breaker ===")
    breaker = CircuitBreaker("demo", max_fallos=3, enfriamiento=3.0)

    print("\n--- 3 fallos seguidos: CLOSED -> OPEN ---")
    for _ in range(3):
        try:
            breaker.call(falla)
        except ConnectionError:
            pass
    print("Estado:", breaker.estado.value)

    print("\n--- Circuito abierto: rechaza sin llamar a la API ---")
    try:
        breaker.call(lambda: "ok")
    except CircuitOpenError as exc:
        print("Rechazada:", exc)

    print("\n--- Esperando el enfriamiento (3 s) ---")
    time.sleep(3.1)

    print("\n--- Llamada de prueba exitosa: OPEN -> HALF_OPEN -> CLOSED ---")
    print("Resultado:", breaker.call(lambda: "ok"))
    print("Estado:", breaker.estado.value)


if __name__ == "__main__":
    main()