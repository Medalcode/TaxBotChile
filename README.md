# TaxBotChile 🇨🇱

Asistente tributario inteligente para freelancers chilenos. Calcula retención de boletas de honorarios, proyecta el Impuesto Global Complementario y entrega recomendaciones de ahorro personalizadas.

## Funcionalidades

- **Cálculo de retención** — 13,75% sobre boletas de honorarios (tasa vigente SII)
- **Proyección Global Complementario** — Estimación anual del impuesto según tramos UTM
- **Dashboard interactivo** — 6 vistas con gráficos Plotly (ingresos mensuales, comparativas)
- **Recomendaciones personalizadas** — Sugerencias de ahorro basadas en ingresos y proyección GC
- **Autenticación** — Registro e inicio de sesión con JWT + bcrypt
- **CRUD de ingresos** — Registrar, listar y eliminar ingresos

## Stack

| Capa | Tecnología |
|------|-----------|
| Backend | FastAPI + SQLAlchemy + SQLite |
| Dashboard | Streamlit + Plotly + Pandas |
| Auth | JWT (python-jose) + bcrypt nativo |
| Tests | pytest + httpx (TestClient) |
| Deploy | Docker + docker-compose |

## Estructura

```
TaxBotChile/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point + CORS
│   │   ├── models.py            # SQLAlchemy ORM (Usuario, Ingreso)
│   │   ├── schemas.py           # Pydantic models
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
│   ├── test_api.py              # 7 tests de integración (API)
│   └── test_tax_calculator.py   # 6 tests unitarios (core tributario)
├── docker-compose.yml           # Orquestación backend + dashboard
├── run.sh                       # Script lanzamiento local
├── .env.example                 # Variables de entorno (SECRET_KEY, DB)
├── pyproject.toml               # ruff + mypy config
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

## Tests

```bash
cd backend
pytest ../tests/ -v
```

13 tests (7 integración API + 6 unitarios). Todos pasan sin warnings.

## Knowledge Graph

`graphify-out/graph.json` contiene 53 nodos y 52 aristas del AST del proyecto, permitiendo a agentes AI comprender la arquitectura sin escanear archivos.

## Skills

- **tdd** (skills.sh) — patrones de testing para mantener y expandir la cobertura

## Variables de Entorno

| Variable | Default | Descripción |
|----------|---------|-------------|
| `SECRET_KEY` | `taxbot-secret-key-change-in-production` | Clave para firmar JWT |
| `DATABASE_URL` | `sqlite:///data/taxbot.db` | URL de conexión a BD |
| `VALOR_UTM` | `66205` | Valor de la UTM para cálculos |

## Autor

**Jonatthan Medalla** — Ingeniería en Computación e Informática, Inacap

## Licencia

MIT
