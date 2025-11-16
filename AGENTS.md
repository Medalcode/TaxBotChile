# TaxBotChile — Agent Guide

## Commands
```bash
pytest tests/ -v            # all tests (run from repo root)
pytest tests/test_api.py::test_health -v  # single test
ruff check .                # lint
mypy .                      # typecheck
bash run.sh                 # start backend + dashboard locally
docker-compose up --build   # or via Docker
```

## Critical Quirks

- **bcrypt must be <4.1** (`requirements.txt` pins `bcrypt>=4.0,<4.1`). Do NOT upgrade — passlib breaks with >=4.1.
- **No `__init__.py`** in `backend/app/`, `routers/`, `services/`, or `tests/`. Python 3.3+ namespace packages work but agents adding new packages must NOT create `__init__.py` or imports will break.
- **JWT tokens last 30 days** — no refresh or revoke mechanism.
- **Tests use global mutable state** (`_test_email` module variable) — must run sequentially (`-n auto` / xdist will fail).
- **Tests modify `sys.path`** at import time — run `pytest tests/` only from repo root.
- **Model tables created at import time** (`Base.metadata.create_all()` in `models.py`). Importing models triggers DDL.
- **`run.sh`** starts both services locally. Must have deps installed in `backend/` and `dashboard/` separately.
- **`.env`** file: copy `.env.example` and set `SECRET_KEY` + `DATABASE_URL`.
- **UTM=66205 CLP** hardcoded (2025-2026 value). Update yearly.
