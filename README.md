# TaxBotChile 🇨🇱

Asistente tributario inteligente para freelancers chilenos. Calcula retención de boletas de honorarios, proyecta el Impuesto Global Complementario y entrega recomendaciones de ahorro personalizadas.

## Funcionalidades

- **Cálculo de retención** — 13,75% sobre boletas de honorarios (tasa vigente SII)
- **Proyección Global Complementario** — Estimación anual del impuesto según tramos UTM
- **Dashboard interactivo** — Gráficos de ingresos mensuales con Plotly
- **Recomendaciones personalizadas** — Sugerencias de ahorro basadas en ingresos y proyección
- **Autenticación** — Registro e inicio de sesión con JWT + bcrypt
- **CRUD de ingresos** — Registrar, listar y eliminar ingresos

## Stack

| Capa | Tecnología |
|------|-----------|
| Backend | FastAPI + SQLAlchemy + SQLite |
| Dashboard | Streamlit + Plotly + Pandas |
| Auth | JWT (python-jose) + bcrypt (passlib) |
| Tests | pytest + httpx (TestClient) |

## Estructura

```
TaxBotChile/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point
│   │   ├── models.py            # SQLAlchemy ORM (Usuario, Ingreso)
│   │   ├── schemas.py           # Pydantic models
│   │   ├── routers/
│   │   │   ├── auth_router.py   # /auth/registro, /auth/login
│   │   │   └── income_router.py # /api/ingresos, /api/calcular, etc.
│   │   └── services/
│   │       ├── auth.py          # JWT create/decode, password hash
│   │       └── tax_calculator.py # Lógica tributaria chilena
│   └── requirements.txt
├── dashboard/
│   ├── app.py                   # Streamlit multivista
│   └── requirements.txt
├── tests/
│   ├── test_api.py              # 7 tests de integración
│   └── test_tax_calculator.py   # 6 tests unitarios
├── run.sh                       # Script lanzamiento backend + dashboard
├── pyproject.toml               # ruff + mypy config
├── .gitignore
└── README.md
```

## Quick Start

```bash
# Clonar
git clone https://github.com/Medalcode/TaxBotChile.git
cd TaxBotChile

# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Dashboard (otra terminal)
cd dashboard
pip install -r requirements.txt
streamlit run app.py --server.port 8501
```

O con el script todo-en-uno:

```bash
chmod +x run.sh && ./run.sh
```

## API Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/auth/registro` | Registrar usuario |
| POST | `/auth/login` | Iniciar sesión (devuelve JWT) |
| POST | `/api/ingresos` | Registrar ingreso |
| GET | `/api/ingresos` | Listar ingresos del usuario |
| DELETE | `/api/ingresos/{id}` | Eliminar ingreso |
| POST | `/api/calcular/boleta?monto=X` | Calcular retención 13,75% |
| GET | `/api/proyeccion` | Proyección Global Complementario |
| GET | `/api/recomendaciones` | Recomendaciones de ahorro |
| GET | `/health` | Health check |

## Tests

```bash
cd backend
pytest ../tests/ -v
```

## Autor

**Jonatthan Medalla** — Ingeniería en Computación e Informática, Inacap

## Licencia

MIT
