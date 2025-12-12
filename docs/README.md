# OmniCore Ontology Platform – Full Documentation

## Table of Contents
- Introduction
- Architecture and Components
- Data Models
- API Gateway
- Frontend (React Dashboard)
- Local Development (Windows)
- Manual Service Control
- Configuration Reference
- Testing
- Project Structure
- Troubleshooting
- Quick Usage Examples

## Introduction
OmniCore is a modular ontology platform that unifies heterogeneous ontologies, captures causality and epistemic annotations, computes meta-metrics, and exposes them through a unified API gateway and React dashboard. It is designed for researchers, data engineers, and application teams who need structured ontology CRUD, provenance, and health/metrics visibility.

## Architecture and Components
- Roots Service (:8001): CRUD for fundamental ontology roots (EXTANT, ABSTRACT, MENTAL, FICTIVE) and summaries.
- Causality Service (:8002): CRUD for causality links (EFFICIENT, FINAL, MATERIAL, FORMAL, EMERGENT), filtering, and summaries.
- Epistemic Service (:8003): CRUD for epistemic annotations (certainty, basis, source), filtering, and summaries.
- MMO Service (:8004): Meta-Meta-Ontology classes and slots, metrics view/recalculation, and schema aggregation.
- Global Service (:8005): Aggregates stats, samples, and health across all services.
- API Gateway (:8000): Single entry point; proxies to all services, provides auth stubs, health aggregation, and docs.
- Frontend Dashboard (:3000): Vite/React app for visualization and management.

Infrastructure notes:
- Storage: SQLite per service (created under `./data` by default); configurable via `DATABASE_PATH`.
- Configuration: environment-driven (`.env`), loaded through `common/config.py`.
- Networking: Services listen on localhost ports in dev; gateway proxies via the configured service URLs.

## Data Models
Roots:
- id, name, root_type (EXTANT, ABSTRACT, MENTAL, FICTIVE), description, metadata, timestamps.

Causality:
- id, source_entity_id, target_entity_id, causality_type (EFFICIENT, FINAL, MATERIAL, FORMAL, EMERGENT), confidence, description, metadata, timestamps.

Epistemic:
- id, entity_id, certainty, basis (axiomatic, empirical, consensus, speculative), source, metadata, timestamps.

MMO:
- Classes and slots with metadata, plus computed metrics (completeness, coverage, coherence, utility, inclusivity).

## API Gateway
- Proxies `/api/...` routes to backend services using URLs from environment variables.
- Auth stub: `/api/auth/token` issues a bearer token for dev scenarios (no real user store).
- Health: `/health` for gateway, `/api/health/overview` for aggregated service health.
- Docs: `/docs`, `/redoc`, `/openapi.json`.

## Frontend (React Dashboard)
- Location: `src/frontend/omnicloud-ui`.
- Dev server: `npm run dev` (via run-dev.ps1) on http://localhost:3000.
- Consumes gateway APIs (ensure `VITE_API_BASE_URL` points to http://localhost:8000/api in `.env`).

## Local Development (Windows)
Prerequisites:
- Python 3.11+, Node 18+, PowerShell, Git; optional Redis for rate limiting.

Setup:
1) Create venv and install backend deps:
   - `python -m venv .venv`
   - `.\.venv\Scripts\Activate.ps1`
   - `pip install -r requirements.txt`
2) Install frontend deps:
   - `cd src\frontend\omnicloud-ui`
   - `npm install`
   - `cd ..\..\..`
3) Environment:
   - `.env` already present; defaults point services to `http://127.0.0.1:8001-8005`.
   - `DATABASE_PATH=./data` (auto-created).
4) Run all services plus frontend:
   - `.\run-dev.ps1`
   - Opens PowerShell windows for each backend and the frontend.

Verification:
- Gateway health: `curl http://localhost:8000/health`
- System health: `curl http://localhost:8000/api/health/overview`
- Docs: `http://localhost:8000/docs`
- Dashboard: `http://localhost:3000`

## Manual Service Control
Environment (PowerShell from repo root):
- `$env:PYTHONPATH="$(Get-Location)\src"`
- `$env:DATABASE_PATH="$(Get-Location)\data"`
- Optional service URLs:
  - `$env:ROOTS_SERVICE_URL="http://127.0.0.1:8001"` (similar for others)

Start a service:
- Roots: `.\.venv\Scripts\python -m uvicorn core.roots.api:app --host 127.0.0.1 --port 8001 --reload`
- Repeat for causality/epistemic/mmo/global/gateway with their ports.

Frontend only:
- `cd src\frontend\omnicloud-ui`
- `npm run dev`

## Configuration Reference
Key variables (see `.env`):
- OMNICORE_ENV (development|production)
- OMNICORE_LOG_LEVEL (DEBUG|INFO|WARNING|ERROR)
- DATABASE_PATH (directory for SQLite files)
- ROOTS_SERVICE_URL, CAUSALITY_SERVICE_URL, EPISTEMIC_SERVICE_URL, MMO_SERVICE_URL, GLOBAL_SERVICE_URL (gateway targets)
- JWT_SECRET_KEY, JWT_ALGORITHM, JWT_EXPIRATION_HOURS (gateway auth stub)
- API_KEY_HEADER, VALID_API_KEYS (optional API key support)
- REDIS_URL, RATE_LIMIT_REQUESTS, RATE_LIMIT_WINDOW (optional rate limiting)
- CORS_ORIGINS
- Frontend: NODE_ENV, VITE_API_BASE_URL

Defaults in `.env` are suitable for local development; adjust for containers or remote deployments.

## Testing
- Activate venv: `.\.venv\Scripts\Activate.ps1`
- Run all tests: `pytest tests -q`
- Tests use temp SQLite directories and do not require external services.

## Project Structure (key paths)
- `src/common` – shared config, logging, auth, database utilities, models.
- `src/core/roots|causality|epistemic|mmo|global_srv` – service APIs, business logic, storage.
- `src/core/gateway` – API gateway proxy, middleware, routing.
- `src/frontend/omnicloud-ui` – React dashboard (Vite).
- `infra` – podman-compose template and env example.
- `tests` – service-level tests.
- `run-dev.ps1` – Windows multi-service launcher.

## Troubleshooting
- 500s from gateway: ensure backend services are running and service URLs point to the correct host/ports (in `.env` and `run-dev.ps1`).
- Port conflicts: change port or stop conflicting process; then rerun.
- SQLite “unable to open” or “no such table”: confirm `DATABASE_PATH` exists; remove stale DB files in `data/` to reset.
- CORS issues: set `CORS_ORIGINS` to `*` in dev or to your frontend origin.
- Docs not loading: confirm gateway is up (`/health`) and reload `/docs`.

## Quick Usage Examples (via Gateway)
- Create root:
  - `POST http://localhost:8000/api/roots`
  - Body: `{ "name": "Entity", "root_type": "EXTANT" }`
- Create causality link:
  - `POST http://localhost:8000/api/causality-links`
  - Body: `{ "source_entity_id": "a", "target_entity_id": "b", "causality_type": "EFFICIENT" }`
- List annotations:
  - `GET http://localhost:8000/api/annotations`
- Recalculate MMO metrics:
  - `POST http://localhost:8000/api/metrics/recalculate`
- System health:
  - `GET http://localhost:8000/api/health/overview`

This document provides the complete overview, setup, and operational guidance for OmniCore. For day-to-day development, rely on `run-dev.ps1`, the `.env` defaults, and the gateway docs at `http://localhost:8000/docs`.
