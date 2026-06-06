import streamlit as st
import plotly.graph_objects as go
from utils import api_get, require_auth

require_auth()
st.title("📈 Proyección Anual")

r = api_get("/api/proyeccion")
if r.status_code == 200:
    d = r.json()
    gc = d["global_complementario"]

    kpi_cols = st.columns(4)
    kpi_cols[0].metric("Proyectado Anual", f"${d['proyeccion_anual']:,.0f}")
    kpi_cols[1].metric("Promedio Mensual", f"${d['promedio_mensual']:,.0f}")
    kpi_cols[2].metric("Retención Promedio", f"${d['retencion_promedio_mensual']:,.0f}")
    kpi_cols[3].metric("Ahorro Sugerido/mes", f"${d['ahorro_sugerido_mensual']:,.0f}")

    st.subheader("Global Complementario Estimado")
    gc_cols = st.columns(4)
    gc_cols[0].metric("Impuesto Calculado", f"${gc['impuesto_calculado']:,.0f}")
    gc_cols[1].metric("Total Retenido", f"${gc['total_retenido_anual']:,.0f}")
    if gc["saldo_a_pagar"] > 0:
        gc_cols[2].metric("Saldo a Pagar", f"${gc['saldo_a_pagar']:,.0f}", delta="⚠️")
    else:
        gc_cols[2].metric("Saldo a Pagar", "$0")
    if gc["saldo_a_favor"] > 0:
        gc_cols[3].metric("Saldo a Favor", f"${gc['saldo_a_favor']:,.0f}", delta="✅")
    else:
        gc_cols[3].metric("Saldo a Favor", "$0")

    fig = go.Figure()
    fig.add_trace(go.Bar(name="Ingreso Bruto", x=["Anual"], y=[gc["ingreso_bruto_anual"]],
                         marker_color="#00b4d8"))
    fig.add_trace(go.Bar(name="Retenido", x=["Anual"], y=[gc["total_retenido_anual"]],
                         marker_color="#ef476f"))
    fig.add_trace(go.Bar(name="Impuesto", x=["Anual"], y=[gc["impuesto_calculado"]],
                         marker_color="#ffd166"))
    fig.update_layout(title="Comparativa: Ingreso vs Retención vs Impuesto", barmode="group")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Registra al menos un ingreso para ver la proyección.")
