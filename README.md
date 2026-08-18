# TaxBotChile 🇨🇱

Asistente tributario inteligente para freelancers chilenos. Calcula retención de boletas de honorarios, proyecta el Impuesto Global Complementario y entrega recomendaciones de ahorro personalizadas.

## Funcionalidades

- **Cálculo de retención** — 13,75% sobre boletas de honorarios (tasa vigente SII)
- **Proyección Global Complementario** — Estimación anual del impuesto según tramos UTM
- **Dashboard interactivo** — 6 vistas con gráficos Plotly (ingresos mensuales, comparativas)
- **Recomendaciones personalizadas** — Sugerencias de ahorro basadas en ingresos y proyección GC
- **Autenticación** — Registro e inicio de sesión con JWT + bcrypt
- **CRUD de ingresos** — Registrar, listar y eliminar ingresos con aislamiento por usuario

## Stack

| Capa | Tecnología |
|------|-----------|
| Backend | FastAPI + SQLAlchemy 2.0 + SQLite |
| Dashboard | Streamlit + Plotly + Pandas |
| Auth | JWT (python-jose) + bcrypt nativo |
| CI/CD & QA | GitHub Actions + pytest (99% coverage) + ruff + mypy |
| Deploy | Docker + docker-compose |

## Estructura

```
TaxBotChile/
├── .github/
│   └── workflows/
│       └── ci.yml               # GitHub Actions CI/CD Pipeline
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point + CORS
│   │   ├── database.py          # SQLAlchemy 2.0 engine, Base & SessionLocal
│   │   ├── models.py            # SQLAlchemy ORM (Usuario, Ingreso)
│   │   ├── schemas.py           # Pydantic models (DTOs)
│   │   ├── routers/
│   │   │   ├── auth_router.py   # /auth/registro, /auth/login
│   │   │   └── income_router.py # /api/ingresos, /api/calcular, etc.
│   │   └── services/
│   │       ├── auth.py          # JWT create/decode, password hash
│   │       └── tax_calculator.py # Lógica tributaria chilena
│   ├── Dockerfile
│   └── requirements.txt
├── dashboard/
│   ├── app.py                   # Streamlit entry point y routing
│   ├── utils.py                 # Utilidades API y sesión
│   ├── pages/                   # Vistas multipágina
│   │   ├── 1_Dashboard.py
│   │   ├── 2_Registrar_Ingreso.py
│   │   ├── 3_Mis_Ingresos.py
│   │   ├── 4_Calcular_Boleta.py
│   │   ├── 5_Proyeccion.py
│   │   └── 6_Recomendaciones.py
│   ├── Dockerfile
│   └── requirements.txt
├── tests/
│   ├── test_api.py              # Pruebas de integración API, auth y multitenancy
│   ├── test_tax_calculator.py   # Pruebas unitarias de cálculo fiscal y tramos UTM
│   └── test_smoke_and_utils.py  # Smoke tests y unit tests de utils de Dashboard
├── docker-compose.yml           # Orquestación backend + dashboard
├── run.sh                       # Script lanzamiento local
├── .env.example                 # Variables de entorno (SECRET_KEY, DB)
├── pyproject.toml               # ruff + mypy config
├── CHANGELOG.md                 # Historial de cambios
├── graphify-out/                # Knowledge graph (53 nodos, 52 aristas)
├── .agents/                     # skills.sh skills (tdd)
├── .gitignore
└── README.md
```

## Quick Start

### Local

```bash
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

### Docker

```bash
cp .env.example .env
docker compose up --build
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

## QA & Testing Suite

```bash
uv run pytest --cov=backend/app --cov-report=term-missing tests/ -v
```

27 tests (Integración API, Casos de Borde, Escenarios Negativos, Aislamiento Multiusuario y Smoke Tests) con **99% de cobertura en backend**.

## CI/CD Pipeline

El repositorio cuenta con integración continua vía GitHub Actions ([`.github/workflows/ci.yml`](.github/workflows/ci.yml)):
1. Linter: `uv run ruff check .`
2. Type Checker: `uv run mypy backend/app dashboard`
3. Test & Coverage: `uv run pytest --cov=backend/app tests/ -v`

## Variables de Entorno

| Variable | Default | Descripción |
|----------|---------|-------------|
| `SECRET_KEY` | `taxbot-secret-key-change-in-production` | Clave para firmar JWT |
| `DATABASE_URL` | `sqlite:///data/taxbot.db` | URL de conexión a BD |
| `VALOR_UTM` | `66205` | Valor de la UTM para cálculos |
| `API_URL` | `http://localhost:8000` | URL del Backend consumida por el Dashboard |

## Autor

**Jonatthan Medalla** — Ingeniería en Computación e Informática, Inacap

## Licencia

MIT
