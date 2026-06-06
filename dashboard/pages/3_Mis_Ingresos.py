import streamlit as st
import pandas as pd
from utils import api_get, api_delete, require_auth

require_auth()
st.title("📋 Mis Ingresos")

r = api_get("/api/ingresos")
if r.status_code == 200:
    data = r.json()
    if data:
        df = pd.DataFrame(data)
        df["fecha_emision"] = pd.to_datetime(df["fecha_emision"]).dt.strftime("%d-%m-%Y")
        df["líquido"] = (df["monto_bruto"] * 0.8625).round(0).astype(int)
        df["retención"] = (df["monto_bruto"] * 0.1375).round(0).astype(int)

        for _, row in df.iterrows():
            with st.expander(f"${row['monto_bruto']:,.0f} - {row['fecha_emision']}"):
                col1, col2, col3 = st.columns(3)
                col1.write(f"**Bruto:** ${row['monto_bruto']:,.0f}")
                col2.write(f"**Retención:** ${row['retención']:,.0f}")
                col3.write(f"**Líquido:** ${row['líquido']:,.0f}")
                if row.get("cliente"):
                    st.write(f"**Cliente:** {row['cliente']}")
                if row.get("descripcion"):
                    st.write(f"**Concepto:** {row['descripcion']}")
                if st.button(f"🗑️ Eliminar", key=f"del_{row['id']}"):
                    api_delete(f"/api/ingresos/{row['id']}")
                    st.rerun()
    else:
        st.info("No hay ingresos registrados")
else:
    st.error("Error al cargar ingresos")
