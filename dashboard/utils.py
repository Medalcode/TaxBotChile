import streamlit as st
import requests

API_URL = "http://localhost:8000"

def init_session():
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

def require_auth():
    if not st.session_state.token:
        st.warning("Debes iniciar sesión para ver esta página.")
        st.stop()
