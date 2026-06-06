import streamlit as st
from utils import api_get, require_auth

require_auth()
st.title("💡 Recomendaciones Personalizadas")

r = api_get("/api/recomendaciones")
if r.status_code == 200:
    recs = r.json()
    if recs:
        for rec in recs:
            if rec["tipo"] == "alerta":
                st.warning(f"⚠️ {rec['mensaje']}")
            elif rec["tipo"] == "ok":
                st.success(f"✅ {rec['mensaje']}")
            else:
                st.info(f"ℹ️ {rec['mensaje']}")
    else:
        st.info("No hay recomendaciones específicas para tu perfil actual.")
else:
    st.info("Registra al menos un ingreso para recibir recomendaciones.")
