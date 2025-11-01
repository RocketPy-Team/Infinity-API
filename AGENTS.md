# Repository Guidelines

## Project Structure & Module Organization
Source code lives in `src/`, with FastAPI entrypoints in `src/api.py` and domain layers grouped by concern (`controllers/`, `services/`, `repositories/`, `models/`, `routes/`, `views/`). Shared settings and helpers sit in `src/settings/` and `src/utils.py`. Tests mirror this layout under `tests/unit/` and `tests/integration/` for focused and end-to-end coverage. Deployment assets stay at the root (`Dockerfile`, `compose.yaml`, `Makefile`), while virtualenv tooling is kept in `infinity_env/`.

## Build, Test, and Development Commands
- `python3 -m pip install -r requirements.txt` prepares runtime dependencies; add `requirements-dev.txt` for local tooling.
- `make format` runs Black and Ruff autofixes across `src/` and `tests/`.
- `make lint` executes Flake8 and Pylint with the repository presets.
- `make test` wraps `pytest` with the configured `tests/` path.
- `make dev` starts Uvicorn on `http://localhost:3000` with hot reload.
- `docker-compose up --build -d` (from `compose.yaml`) builds and runs the API plus MongoDB in containers; use `make clean` to prune stacks.

## Coding Style & Naming Conventions
Target Python 3.12 and a 79-character line length (Black, Ruff, and Pylint enforce this). Prefer module-level functions in `snake_case`, classes in `PascalCase`, and constants in `UPPER_SNAKE_CASE`. Keep FastAPI routers named `<feature>_router` inside `src/routes/`, and align Pydantic models with `CamelCase` class names under `src/models/`. Run `make format` before opening a PR to avoid stylistic churn.

## Testing Guidelines
Pytest drives both unit and integration suites; name files `test_<feature>.py` and group fixtures near usage. Place pure-function tests in `tests/unit/` and API or database flows in `tests/integration/`. Execute `pytest tests/integration/test_environment.py -k simulate` to target scenarios while keeping `--import-mode=importlib` behavior intact. New features should include happy-path and failure-case coverage, plus integration smoke tests when touching MongoDB writes.

## Commit & Pull Request Guidelines
Git history favors concise, uppercase prefixes (`BUG:`, `ENH:`, `MNT:`) followed by a short imperative summary and optional issue reference, e.g. `ENH: streamline rocket encoders (#58)`. Squash commits that fix review feedback before merging. Pull requests should describe intent, list API or schema changes, link to tracking issues, and attach screenshots or sample responses when observable behavior shifts.

## Security & Configuration Tips
Never commit `.env` or credentials; instead, document required keys such as `MONGODB_CONNECTION_STRING` in the PR. Use `src/secrets.py` helpers for secret access rather than inlining values, and prefer Docker secrets or environment variables when deploying.
