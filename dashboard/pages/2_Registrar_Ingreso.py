import streamlit as st
from datetime import datetime
from utils import api_post, require_auth

require_auth()
st.title("➕ Registrar Ingreso por Boleta")

with st.form("nuevo_ingreso"):
    monto = st.number_input("Monto Bruto ($)", min_value=1, step=1000, value=100000)
    fecha = st.date_input("Fecha de Emisión", datetime.now())
    cliente = st.text_input("Cliente (opcional)")
    descripcion = st.text_input("Concepto (opcional)")
    if st.form_submit_button("Guardar"):
        r = api_post("/api/ingresos", json={
            "monto_bruto": float(monto),
            "fecha_emision": fecha.strftime("%Y-%m-%d"),
            "cliente": cliente or None,
            "descripcion": descripcion or None,
        })
        if r.status_code == 200:
            st.success("Ingreso registrado exitosamente")
            st.rerun()
        else:
            st.error(r.json().get("detail", "Error al registrar"))
