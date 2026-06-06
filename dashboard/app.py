import streamlit as st
from utils import init_session, api_post

st.set_page_config(page_title="TaxBot Chile", page_icon="🧾", layout="wide")
init_session()

def login_page():
    st.title("Bienvenido a TaxBot Chile")
    st.caption("Asistente Tributario para Freelancers")

    tab1, tab2 = st.tabs(["Iniciar Sesión", "Registrarse"])

    with tab1:
        with st.form("login"):
            email = st.text_input("Email")
            password = st.text_input("Contraseña", type="password")
            if st.form_submit_button("Entrar"):
                r = api_post("/auth/login", json={"email": email, "password": password})
                if r.status_code == 200:
                    st.session_state.token = r.json()["access_token"]
                    st.session_state.usuario = email
                    st.rerun()
                else:
                    st.error("Credenciales inválidas")

    with tab2:
        with st.form("registro"):
            nombre = st.text_input("Nombre")
            email_r = st.text_input("Email")
            password_r = st.text_input("Contraseña", type="password")
            rut = st.text_input("RUT (opcional)")
            if st.form_submit_button("Registrarse"):
                r = api_post("/auth/registro", json={
                    "nombre": nombre, "email": email_r, "password": password_r, "rut": rut or None,
                })
                if r.status_code == 200:
                    st.success("Registrado exitosamente. Inicia sesión.")
                else:
                    st.error(r.json().get("detail", "Error al registrar"))

if not st.session_state.token:
    login_page()
else:
    st.sidebar.success(f"👤 {st.session_state.usuario}")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.token = None
        st.session_state.usuario = None
        st.rerun()

    pages = {
        "Principal": [
            st.Page("pages/1_Dashboard.py", title="📊 Dashboard", default=True),
        ],
        "Operaciones": [
            st.Page("pages/2_Registrar_Ingreso.py", title="➕ Registrar Ingreso"),
            st.Page("pages/3_Mis_Ingresos.py", title="📋 Mis Ingresos"),
            st.Page("pages/4_Calcular_Boleta.py", title="🧮 Calcular Boleta"),
        ],
        "Análisis": [
            st.Page("pages/5_Proyeccion.py", title="📈 Proyección"),
            st.Page("pages/6_Recomendaciones.py", title="💡 Recomendaciones"),
        ]
    }

    pg = st.navigation(pages)
    pg.run()
