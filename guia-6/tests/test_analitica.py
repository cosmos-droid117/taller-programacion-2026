from unittest.mock import Mock

import pytest

from application.analisis_service import AnalisisService
from domain.ports import AnaliticaPort, DatosAbiertosPort
from infrastructure.duckdb_analitica import DuckDBAnalitica

analitica = DuckDBAnalitica()


def test_estadisticas_convierte_texto_a_numero_e_ignora_invalidos():
    registros = [{"p": "10"}, {"p": "20"}, {"p": "30"}, {"p": "x"}, {"p": None}]
    r = analitica.estadisticas(registros, "p")
    assert r == {"n": 3, "promedio": 20.0, "mediana": 20.0, "desviacion": 10.0, "minimo": 10.0, "maximo": 30.0}


def test_estadisticas_con_coma_decimal():
    r = analitica.estadisticas([{"lat": "6,5"}, {"lat": "7,5"}], "lat")
    assert r["promedio"] == 7.0


def test_estadisticas_sin_datos():
    assert analitica.estadisticas([], "p")["n"] == 0
    assert analitica.estadisticas([{"p": "x"}], "p")["promedio"] is None


def test_por_grupo_cuenta_ordena_y_promedia():
    registros = [
        {"d": "Bogotá", "p": "100"}, {"d": "Bogotá", "p": "300"},
        {"d": "Cali", "p": "50"}, {"d": None, "p": "x"},
    ]
    r = analitica.por_grupo(registros, "d", "p")
    assert r[0] == {"grupo": "Bogotá", "n": 2, "promedio": 200.0}
    assert {"grupo": "(sin dato)", "n": 1, "promedio": None} in r
    assert [g["n"] for g in r] == sorted([g["n"] for g in r], reverse=True)


def test_por_grupo_sin_columna_numerica():
    r = analitica.por_grupo([{"d": "A"}, {"d": "A"}, {"d": "B"}], "d")
    assert r == [{"grupo": "A", "n": 2}, {"grupo": "B", "n": 1}]


def test_columna_inexistente_falla():
    with pytest.raises(ValueError):
        analitica.estadisticas([{"a": 1}], "z")
    with pytest.raises(ValueError):
        analitica.por_grupo([{"a": 1}], "z")


def test_servicio_con_columna_numerica_usa_los_puertos():
    fuente = Mock(spec=DatosAbiertosPort)
    fuente.obtener_registros.return_value = [{"d": "A", "p": "1"}]
    an = Mock(spec=AnaliticaPort)
    an.por_grupo.return_value = [{"grupo": "A", "n": 1, "promedio": 1.0}]
    an.estadisticas.return_value = {"n": 1}

    res = AnalisisService("SECOP II", fuente, an, "d", "p").analizar(50)

    fuente.obtener_registros.assert_called_once_with(50)
    an.por_grupo.assert_called_once_with([{"d": "A", "p": "1"}], "d", "p")
    an.estadisticas.assert_called_once_with([{"d": "A", "p": "1"}], "p")
    assert res["metrica"] == "p" and res["total_registros"] == 1


def test_servicio_sin_numerica_calcula_estadisticas_sobre_conteos():
    fuente = Mock(spec=DatosAbiertosPort)
    fuente.obtener_registros.return_value = [{"dpto": "A"}] * 3 + [{"dpto": "B"}]
    res = AnalisisService("DIVIPOLA", fuente, analitica, "dpto").analizar()
    assert res["grupos"][0] == {"grupo": "A", "n": 3}
    assert res["estadisticas"]["maximo"] == 3 and res["estadisticas"]["minimo"] == 1
    assert res["estadisticas"]["n"] == 2