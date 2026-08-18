import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.services.tax_calculator import (
    VALOR_UTM,
    calcular_global_complementario,
    calcular_proyeccion_anual,
    calcular_recomendaciones,
    calcular_retencion_boleta,
)


def test_calcular_retencion_boleta():
    res = calcular_retencion_boleta(500000)
    assert res["monto_bruto"] == 500000
    assert res["retencion"] == 68750
    assert res["liquido_a_recibir"] == 431250
    assert res["tasa_retencion"] == 0.1375


def test_calcular_retencion_boleta_zero_and_negative():
    res_zero = calcular_retencion_boleta(0)
    assert res_zero["retencion"] == 0
    assert res_zero["liquido_a_recibir"] == 0

    res_neg = calcular_retencion_boleta(-1000)
    assert res_neg["monto_bruto"] == -1000


def test_calcular_global_complementario_exento():
    res = calcular_global_complementario(500000)
    assert res["tasa_efectiva"] == 0
    assert res["impuesto_calculado"] == 0
    assert res["saldo_a_favor"] > 0


def test_calcular_global_complementario_tramos_limites():
    # Tramo 1: 10 UTM (Exento)
    res_10 = calcular_global_complementario(10 * VALOR_UTM)
    assert res_10["tasa_efectiva"] == 0.0

    # Tramo 2: 20 UTM (4%)
    res_20 = calcular_global_complementario(20 * VALOR_UTM)
    assert res_20["tasa_efectiva"] == 4.0

    # Tramo 3: 40 UTM (8%)
    res_40 = calcular_global_complementario(40 * VALOR_UTM)
    assert res_40["tasa_efectiva"] == 8.0

    # Tramo 4: 60 UTM (13.5%)
    res_60 = calcular_global_complementario(60 * VALOR_UTM)
    assert res_60["tasa_efectiva"] == 13.5

    # Tramo 5: 80 UTM (23%)
    res_80 = calcular_global_complementario(80 * VALOR_UTM)
    assert res_80["tasa_efectiva"] == 23.0

    # Tramo 6: 100 UTM (30%)
    res_100 = calcular_global_complementario(100 * VALOR_UTM)
    assert res_100["tasa_efectiva"] == 30.0

    # Tramo 7: 130 UTM (35%)
    res_130 = calcular_global_complementario(130 * VALOR_UTM)
    assert res_130["tasa_efectiva"] == 35.0

    # Tramo 8: 200 UTM (40%)
    res_200 = calcular_global_complementario(200 * VALOR_UTM)
    assert res_200["tasa_efectiva"] == 40.0


def test_calcular_global_complementario_alto():
    res = calcular_global_complementario(25000000)
    assert res["tasa_efectiva"] > 0
    assert res["impuesto_calculado"] > 0


def test_calcular_proyeccion_anual():
    res = calcular_proyeccion_anual([2000000, 2500000, 2200000])
    assert res["meses_activos"] == 3
    assert res["total_ingresado"] > 0
    assert res["promedio_mensual"] > 0
    assert res["proyeccion_anual"] > 0


def test_calcular_proyeccion_anual_vacia():
    res = calcular_proyeccion_anual([])
    assert res["meses_activos"] == 0
    assert res["total_ingresado"] == 0
    assert res["proyeccion_anual"] == 0


def test_calcular_recomendaciones():
    recs = calcular_recomendaciones([10000000] * 3)
    assert len(recs) > 0
    assert any(r["tipo"] == "alerta" for r in recs)


def test_calcular_recomendaciones_exentas():
    recs = calcular_recomendaciones([100000] * 3)
    assert len(recs) > 0
    assert any(r["tipo"] == "info" for r in recs)


def test_calcular_recomendaciones_alta_tasa():
    # Ingreso mensual muy alto para activar tasa > 20%
    recs = calcular_recomendaciones([10000000] * 12)
    assert any("Empresa (RUT)" in r["mensaje"] for r in recs)
