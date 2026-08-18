import streamlit as st
from utils import api_post, require_auth

require_auth()
st.title("🧮 Calcular Retención de Boleta")

monto = st.number_input("Monto Bruto de la Boleta ($)", min_value=1, step=10000, value=500000)
if monto > 0:
    r = api_post(f"/api/calcular/boleta?monto={monto}")
    if r.status_code == 200:
        d = r.json()
        col1, col2, col3 = st.columns(3)
        col1.metric("Monto Bruto", f"${d['monto_bruto']:,.0f}")
        col2.metric("Retención (13,75%)", f"${d['retencion']:,.0f}", delta_color="inverse")
        col3.metric("Líquido a Recibir", f"${d['liquido_a_recibir']:,.0f}")
        st.info(
            "Esta retención cubre tu cotización de salud y pensión. "
            "El monto líquido es lo que realmente recibirás."
        )

