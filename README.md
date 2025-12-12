# OmniCore Ontology Platform

A self-evolving meta-ontological platform for unified knowledge representation, designed to run on the PARAM BILIM supercomputer (AlmaLinux 8.9, Podman, NVIDIA A100 GPUs).

## Overview

OmniCore is a microservice-based system that:
- Unifies heterogeneous ontologies into a coherent Meta-Ontology (MO)
- Evaluates MO quality via a self-improving Meta-Meta-Ontology (MMO)
- Supports explainable, auditable AI reasoning grounded in formal roots and causality

## Architecture

The platform consists of 7 microservices:

| Service | Port | Description |
|---------|------|-------------|
| **API Gateway** (F) | 8000 | Unified entry point with auth, rate limiting |
| **Roots Service** (A) | 8001 | Manages 4 root types: EXTANT, ABSTRACT, MENTAL, FICTIVE |
| **Causality Service** (B) | 8002 | Manages 5 causality types (Aristotelian + Emergent) |
| **Epistemic Service** (C) | 8003 | Manages knowledge annotations with certainty |
| **MMO Service** (D) | 8004 | Meta-Meta-Ontology classes, slots, metrics |
| **Global Service** (E) | 8005 | Aggregates data from all services |
| **React Dashboard** (G) | 3000 | Web-based management UI |

## Project Structure

```
OmniCore-Ontology-Platform/
├── src/
│   ├── common/           # Shared utilities
│   ├── core/
│   │   ├── roots/        # Group A - Roots Service
│   │   ├── causality/    # Group B - Causality Service
│   │   ├── epistemic/    # Group C - Epistemic Service
│   │   ├── mmo/          # Group D - MMO Service
│   │   ├── global_srv/   # Group E - Global Service
│   │   └── gateway/      # Group F - API Gateway
│   └── frontend/
│       └── omnicloud-ui/ # Group G - React Dashboard
├── data/                 # SQLite databases
├── infra/                # Podman compose & env files
├── tests/                # Test suite
├── requirements.txt      # Python dependencies
└── README.md
```

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Podman & podman-compose
- Redis (for rate limiting)

### Local Development

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment:**
   ```bash
   cp infra/env/.env.example infra/env/.env
   # Edit .env with your settings
   ```

3. **Create data directory:**
   ```bash
   mkdir -p data
   ```

4. **Run individual services:**
   ```bash
   # Roots Service
   cd src/core/roots
   PYTHONPATH=../../.. uvicorn api:app --port 8001

   # Causality Service
   cd src/core/causality
   PYTHONPATH=../../.. uvicorn api:app --port 8002

   # ... similar for other services
   ```

5. **Run frontend:**
   ```bash
   cd src/frontend/omnicloud-ui
   npm install
   npm run dev
   ```

### Container Deployment

```bash
cd infra
podman-compose up -d
```

## API Documentation

Once running, API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Authentication

The gateway supports two authentication methods:

1. **JWT Token:**
   ```bash
   # Get token
   curl -X POST http://localhost:8000/api/auth/token \
     -H "Content-Type: application/json" \
     -d '{"username": "user", "scopes": ["read", "write"]}'

   # Use token
   curl http://localhost:8000/api/roots \
     -H "Authorization: Bearer <token>"
   ```

2. **API Key:**
   ```bash
   curl http://localhost:8000/api/roots \
     -H "X-API-Key: your-api-key"
   ```

### Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/roots` | GET/POST | List/create roots |
| `/api/roots/{id}` | GET/PUT/DELETE | Root CRUD |
| `/api/roots/summary` | GET | Root statistics |
| `/api/causality-links` | GET/POST | List/create causality links |
| `/api/annotations` | GET/POST | List/create epistemic annotations |
| `/api/classes` | GET/POST | List/create MMO classes |
| `/api/slots` | GET/POST | List/create MMO slots |
| `/api/metrics` | GET | Get MMO metrics |
| `/api/global/stats` | GET | Global statistics |
| `/api/health/overview` | GET | System health status |

## Data Models

### Root Types (v10 Spec)
- **EXTANT**: Entities with spatiotemporal location
- **ABSTRACT**: Atemporal, mind-independent structures
- **MENTAL**: Subjective, first-person accessible states
- **FICTIVE**: Context-dependent representations

### Causality Types
- **EFFICIENT**: causesDirectly
- **FINAL**: servesPurpose
- **MATERIAL**: constitutedBy
- **FORMAL**: structuredAs
- **EMERGENT**: emergesFrom

### Epistemic Basis
- **axiomatic**: Self-evident truths
- **empirical**: Evidence-based
- **consensus**: Community-agreed
- **speculative**: Hypothetical

### MMO Metrics
- **Completeness**: Target >= 0.85
- **Coverage**: Target >= 0.70
- **Coherence**: Target >= 0.95
- **Utility**: Target >= 0.80
- **Inclusivity**: Target >= 0.65

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific service tests
pytest tests/test_roots.py -v
pytest tests/test_causality.py -v
pytest tests/test_epistemic.py -v
pytest tests/test_mmo.py -v
```

## Configuration

Environment variables (see `infra/env/.env.example`):

| Variable | Description | Default |
|----------|-------------|---------|
| `OMNICORE_ENV` | Environment (development/production) | development |
| `OMNICORE_LOG_LEVEL` | Logging level | INFO |
| `DATABASE_PATH` | SQLite database directory | ./data |
| `JWT_SECRET_KEY` | JWT signing key | (change in production!) |
| `REDIS_URL` | Redis connection URL | redis://redis:6379/0 |
| `RATE_LIMIT_REQUESTS` | Requests per window | 100 |
| `RATE_LIMIT_WINDOW` | Rate limit window (seconds) | 60 |

## Technology Stack

- **Backend**: Python 3.11, FastAPI, Pydantic, SQLite
- **Frontend**: React 18, TypeScript, Vite, Recharts
- **Authentication**: JWT, API Keys
- **Deployment**: Podman, Redis
- **Testing**: Pytest

## License

MIT License
