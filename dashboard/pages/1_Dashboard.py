import streamlit as st
import pandas as pd
import plotly.express as px
from utils import api_get, require_auth

require_auth()
st.title("📊 Dashboard Tributario")

r = api_get("/api/ingresos")
if r.status_code == 200:
    data = r.json()
    if data:
        df = pd.DataFrame(data)
        df["fecha_emision"] = pd.to_datetime(df["fecha_emision"])
        df["mes"] = df["fecha_emision"].dt.strftime("%Y-%m")
        df["liquido"] = df["monto_bruto"] * 0.8625

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Bruto", f"${df['monto_bruto'].sum():,.0f}")
        col2.metric("Total Retenido", f"${(df['monto_bruto'].sum() * 0.1375):,.0f}")
        col3.metric("Total Líquido", f"${df['liquido'].sum():,.0f}")
        col4.metric("Boletas Emitidas", len(df))

        mensual = df.groupby("mes")["monto_bruto"].sum().reset_index()
        fig = px.bar(mensual, x="mes", y="monto_bruto",
                     title="Ingresos Mensuales (Bruto)",
                     labels={"mes": "Mes", "monto_bruto": "Monto Bruto ($)"},
                     color_discrete_sequence=["#00b4d8"])
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hay ingresos registrados. Ve a 'Registrar Ingreso' para comenzar.")
else:
    st.error("Error al cargar datos")
