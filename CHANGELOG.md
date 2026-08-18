# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-08-18

### Added
- **CI/CD Pipeline**: GitHub Actions workflow (`.github/workflows/ci.yml`) for automated linting (Ruff), type-checking (Mypy), and testing (Pytest with coverage).
- **Centralized Database Layer**: Added `backend/app/database.py` with SQLAlchemy 2.0 `DeclarativeBase` and single-source `SessionLocal`.
- **QA Automation Testing Suite**: Expanded test suite to 27 tests covering edge cases, negative scenarios (HTTP 400, 401, 404), multi-tenant isolation, and dashboard smoke tests. 99% code coverage achieved.

### Fixed
- **Database Connection Leaks**: Injected DB session into `get_usuario_from_token` using FastAPI dependency `Depends(get_db)`.
- **Docker Compose Integration**: Configured `API_URL` environment variable support in `dashboard/utils.py`.
- **Single Source of Truth (SSOT)**: Dashboard `1_Dashboard.py` now queries backend API for retention calculations instead of duplicating client-side constants.
- **Type Annotations**: Resolved 28 Mypy strict mode type warnings and 10 Ruff lint violations.

### Refactored
- Extracted `_obtener_montos_mensuales` in `income_router.py` to eliminate code duplication (DRY).
