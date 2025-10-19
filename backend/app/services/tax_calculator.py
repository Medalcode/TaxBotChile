VALOR_UTM = 66205
RETENCION_BOLETA = 0.1375

TRAMOS_GLOBAL_COMPLEMENTARIO = [
    (0, 13.5, 0, 0),
    (13.5, 30, 0.04, 0),
    (30, 50, 0.08, 0.54),
    (50, 70, 0.135, 2.14),
    (70, 90, 0.23, 5.34),
    (90, 120, 0.30, 11.14),
    (120, 150, 0.35, 17.14),
    (150, float("inf"), 0.40, 24.64),
]


def calcular_retencion_boleta(monto_bruto: float) -> dict:
    retencion = round(monto_bruto * RETENCION_BOLETA, 0)
    liquido = monto_bruto - retencion
    return {
        "monto_bruto": round(monto_bruto, 0),
        "retencion": retencion,
        "liquido_a_recibir": int(liquido),
        "tasa_retencion": RETENCION_BOLETA,
    }


def calcular_global_complementario(ingreso_bruto_anual: float) -> dict:
    utm = ingreso_bruto_anual / VALOR_UTM

    tasa = 0
    impuesto = 0
    descuento = 0
    for ini, fin, t, d in TRAMOS_GLOBAL_COMPLEMENTARIO:
        if ini <= utm < fin:
            tasa = t
            descuento = d * VALOR_UTM
            impuesto = max(0, ingreso_bruto_anual * tasa - descuento)
            break

    total_retenido_anual = ingreso_bruto_anual * RETENCION_BOLETA
    saldo_a_pagar = max(0, impuesto - total_retenido_anual)
    saldo_a_favor = max(0, total_retenido_anual - impuesto)

    return {
        "ingreso_bruto_anual": round(ingreso_bruto_anual, 0),
        "utm_equivalentes": round(utm, 1),
        "tasa_efectiva": round(tasa * 100, 2),
        "impuesto_calculado": round(impuesto, 0),
        "total_retenido_anual": round(total_retenido_anual, 0),
        "saldo_a_pagar": round(saldo_a_pagar, 0),
        "saldo_a_favor": round(saldo_a_favor, 0),
    }


def calcular_proyeccion_anual(ingresos_mensuales: list[float]) -> dict:
    total_bruto = sum(ingresos_mensuales)
    meses_con_datos = len([i for i in ingresos_mensuales if i > 0])
    promedio_mensual = total_bruto / max(meses_con_datos, 1)
    proyeccion_anual = promedio_mensual * 12

    gc = calcular_global_complementario(proyeccion_anual)

    retencion_mensual_promedio = promedio_mensual * RETENCION_BOLETA
    ahorro_sugerido_mensual = (
        gc["impuesto_calculado"] / 12
        if proyeccion_anual > 0
        else 0
    )

    return {
        "total_ingresado": round(total_bruto, 0),
        "meses_activos": meses_con_datos,
        "promedio_mensual": round(promedio_mensual, 0),
        "proyeccion_anual": round(proyeccion_anual, 0),
        "retencion_promedio_mensual": round(retencion_mensual_promedio, 0),
        "ahorro_sugerido_mensual": round(ahorro_sugerido_mensual, 0),
        "global_complementario": gc,
    }


def calcular_recomendaciones(ingresos_mensuales: list[float]) -> list[dict]:
    proy = calcular_proyeccion_anual(ingresos_mensuales)
    gc = proy["global_complementario"]
    recs = []

    if gc["saldo_a_pagar"] > 0:
        recs.append({
            "tipo": "alerta",
            "mensaje": (
                f"Proyectas pagar ${gc['saldo_a_pagar']:,.0f} en tu declaración anual. "
                f"Ahorra ${proy['ahorro_sugerido_mensual']:,.0f} adicional cada mes."
            ),
        })
    elif gc["saldo_a_favor"] > 0:
        recs.append({
            "tipo": "ok",
            "mensaje": (
                f"Tienes un saldo a favor estimado de ${gc['saldo_a_favor']:,.0f}. "
                "Revisa si puedes optar a devolución."
            ),
        })

    if proy["promedio_mensual"] < 500000:
        recs.append({
            "tipo": "info",
            "mensaje": "Estás en el tramo exento o bajo. Considera cotizar voluntariamente para mejorar tu pensión.",
        })

    if gc["tasa_efectiva"] > 20:
        recs.append({
            "tipo": "alerta",
            "mensaje": (
                f"Tu tasa efectiva es {gc['tasa_efectiva']}%. Evalúa constituir una "
                "Empresa (RUT) para optimizar tu carga tributaria."
            ),
        })

    return recs
