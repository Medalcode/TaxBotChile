# TaxBot Chile 🧾

Asistente Tributario inteligente para Freelancers Chilenos.

## MVP Features

- ✅ Cálculo de retención de boletas de honorarios (13,75%)
- ✅ Proyección de Impuesto Global Complementario
- ✅ Dashboard de ingresos mensuales con gráficos
- ✅ Recomendaciones personalizadas de ahorro
- ✅ Registro y autenticación de usuarios

## Stack

- **Backend:** FastAPI + SQLAlchemy + SQLite
- **Dashboard:** Streamlit + Plotly + Pandas
- **Auth:** JWT + bcrypt

## Quick Start

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# Dashboard (otra terminal)
cd dashboard
pip install -r requirements.txt
streamlit run app.py
```

## API Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/auth/registro` | Registrar usuario |
| POST | `/auth/login` | Iniciar sesión |
| POST | `/api/ingresos` | Registrar ingreso |
| GET  | `/api/ingresos` | Listar ingresos |
| DELETE | `/api/ingresos/{id}` | Eliminar ingreso |
| POST | `/api/calcular/boleta?monto=X` | Calcular retención |
| GET  | `/api/proyeccion` | Proyección anual |
| GET  | `/api/recomendaciones` | Recomendaciones |
