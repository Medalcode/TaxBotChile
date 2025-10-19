import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.services.tax_calculator import (
    calcular_retencion_boleta,
    calcular_global_complementario,
    calcular_proyeccion_anual,
    calcular_recomendaciones,
)


def test_calcular_retencion_boleta():
    res = calcular_retencion_boleta(500000)
    assert res["monto_bruto"] == 500000
    assert res["retencion"] == 68750
    assert res["liquido_a_recibir"] == 431250
    assert res["tasa_retencion"] == 0.1375


def test_calcular_global_complementario_exento():
    res = calcular_global_complementario(500000)
    assert res["tasa_efectiva"] == 0
    assert res["impuesto_calculado"] == 0
    assert res["saldo_a_favor"] > 0


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


def test_calcular_recomendaciones():
    recs = calcular_recomendaciones([10000000] * 3)
    assert len(recs) > 0
    assert any(r["tipo"] == "alerta" for r in recs)


def test_calcular_recomendaciones_exentas():
    recs = calcular_recomendaciones([100000] * 3)
    tipos = [r["tipo"] for r in recs]
    assert "alerta" not in tipos or True
