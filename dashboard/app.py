import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

API_URL = "http://localhost:8000"

st.set_page_config(page_title="TaxBot Chile", page_icon="🧾", layout="wide")

if "token" not in st.session_state:
    st.session_state.token = None
if "usuario" not in st.session_state:
    st.session_state.usuario = None


def api_get(path):
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    return requests.get(f"{API_URL}{path}", headers=headers, timeout=10)


def api_post(path, json=None):
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    return requests.post(f"{API_URL}{path}", json=json, headers=headers, timeout=10)


def api_delete(path):
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    return requests.delete(f"{API_URL}{path}", headers=headers, timeout=10)


st.sidebar.title("🧾 TaxBot Chile")
st.sidebar.caption("Asistente Tributario para Freelancers")

if not st.session_state.token:
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
else:
    st.sidebar.success(f"👤 {st.session_state.usuario}")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.token = None
        st.session_state.usuario = None
        st.rerun()

    menu = st.sidebar.radio("Menú", ["📊 Dashboard", "➕ Registrar Ingreso", "📋 Mis Ingresos", "🧮 Calcular Boleta", "📈 Proyección", "💡 Recomendaciones"])

    if menu == "📊 Dashboard":
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

    elif menu == "➕ Registrar Ingreso":
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

    elif menu == "📋 Mis Ingresos":
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

    elif menu == "🧮 Calcular Boleta":
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
                st.info(f"Esta retención cubre tu cotización de salud y pensión. El monto líquido es lo que realmente recibirás.")

    elif menu == "📈 Proyección":
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

    elif menu == "💡 Recomendaciones":
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
