# OmniCore Ontology Platform v10

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![React 18](https://img.shields.io/badge/React-18-blue.svg)](https://reactjs.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**AI-Orchestrated Ontological Computing System**
**Deployment Target**: PARAM BILIM Supercomputer (AlmaLinux 8.9, Podman, NVIDIA A100 GPUs)

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Data Models](#data-models)
4. [Project Structure](#project-structure)
5. [Setup on Windows (Local Development)](#setup-on-windows-local-development)
6. [Setup on AlmaLinux 8.9 (PARAM BILIM)](#setup-on-almalinux-89-param-bilim)
7. [Running the Services](#running-the-services)
8. [API Documentation](#api-documentation)
9. [Testing](#testing)
10. [Configuration Reference](#configuration-reference)
11. [Troubleshooting](#troubleshooting)

---

## Overview

### Mission Statement

OmniCore is the world's first **self-evolving meta-ontological platform** designed to:

- ✅ **Unify** heterogeneous ontologies into a coherent Meta-Ontology (MO)
- ✅ **Evaluate** MO quality via a self-improving Meta-Meta-Ontology (MMO)
- ✅ **Support** explainable, auditable AI reasoning grounded in formal roots & causality
- ✅ **Scale** from student MVP → zero-human-intervention HPC service

### Architectural Philosophy (v10 Unified Principle)

> *"Start deterministic, augment intelligently, evolve autonomously — without sacrificing verifiability."*

1. **Deterministic Core (Horizon 1)**: All structured data (OWL/RDF) parsed losslessly
2. **AI-Augmented Layer (Horizon 2–3)**: LLMs used only where semantics outweigh syntax
3. **Autonomous Evolution (Horizon 4–5)**: Multi-agent AI operates under invariant constraints

### Three-Horizon Strategy

| Horizon | Timeline | Goal | Key Metrics |
|---------|----------|------|-------------|
| H0: Preparations | Week 1 | Infrastructure baseline | Podman, shared GPU pool |
| H1: Foundation | Weeks 2-5 | Student-built microservices | 80%+ test coverage |
| H2: Augmentation | Month 2 | Autonomous harvesting | 100+ ontologies, 95% conflict resolution |
| H3: Autonomy | Months 3-6 | Multi-AI orchestration | ≤2% human intervention |

---

## Architecture

The platform consists of **7 microservices** following a modular architecture:

```
┌─────────────────────────────────────────────────────────────────┐
│                    Human Oversight (v10)                        │
│  • Ethical halt (SIGUSR1)  • Monthly review  • Bias audit       │
└─────────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────────┐
│                 Core Ontological Engine                         │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐           │
│  │  Roots   │ │Causality │ │Epistemic │ │   MMO    │           │
│  │  :8001   │ │  :8002   │ │  :8003   │ │  :8004   │           │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘           │
└─────────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────────┐
│              Global Ontology Service (:8005)                    │
│  • MO Merge Engine  • Provenance tracking  • Versioned store    │
└─────────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────────┐
│                   API Gateway (:8000)                           │
│  • JWT Auth  • Rate limiting  • Request routing                 │
└─────────────────────────────────────────────────────────────────┘
                                │
         ┌──────────────────────┴──────────────────────┐
         │                                             │
┌─────────────────┐                          ┌─────────────────┐
│ React Dashboard │                          │   CLI / SDK     │
│     (:3000)     │                          │  (Python/JS)    │
└─────────────────┘                          └─────────────────┘
```

### Service Details

| Service | Port | GPU | Description |
|---------|------|-----|-------------|
| **API Gateway** (F) | 8000 | GPU 1 | Unified entry point with JWT/API key auth, rate limiting |
| **Roots Service** (A) | 8001 | - | Manages 4 ontological root types |
| **Causality Service** (B) | 8002 | GPU 0 | Manages 5 causality types (Aristotelian + Emergent) |
| **Epistemic Service** (C) | 8003 | - | Manages knowledge annotations with certainty |
| **MMO Service** (D) | 8004 | - | Meta-Meta-Ontology classes, slots, and quality metrics |
| **Global Service** (E) | 8005 | - | Aggregates data from all services, health monitoring |
| **React Dashboard** (G) | 3000 | - | Web-based management and visualization UI |

---

## Data Models

### Root Types (4 Fundamental Types)

Based on the v10 specification's formal ontological model:

| Type | Description | Example |
|------|-------------|---------|
| **EXTANT** | Entities with spatiotemporal location | Physical objects, events |
| **ABSTRACT** | Atemporal, mind-independent structures | Mathematical concepts, taxonomies |
| **MENTAL** | Subjective, first-person accessible states | Experienced pain, emotions |
| **FICTIVE** | Context-dependent representations | "Sherlock Holmes", simulations |

### Causality Framework (5 Types)

| Type | Predicate | Example |
|------|-----------|---------|
| **EFFICIENT** | `causesDirectly` | hammer → nail_driving |
| **FINAL** | `servesPurpose` | nest → offspring_protection |
| **MATERIAL** | `constitutedBy` | statue → bronze |
| **FORMAL** | `structuredAs` | organism → genome |
| **EMERGENT** | `emergesFrom` | consciousness → neural_network_activity |

### Epistemic Layer

```python
class EpistemicTag:
    certainty: float     # 0.0 - 1.0
    basis: Literal["axiomatic", "empirical", "consensus", "speculative"]
    source: Optional[str]  # DOI, ontology IRI, model ID
    timestamp: datetime
```

### MMO Metrics (Self-Calibrating)

| Metric | Target | Description |
|--------|--------|-------------|
| **Completeness** | ≥ 0.85 | Coverage of domain entities |
| **Coverage** | ≥ 0.70 | Distribution across domains |
| **Coherence** | ≥ 0.95 | Absence of contradictions |
| **Utility** | ≥ 0.80 | Query performance metric |
| **Inclusivity** | ≥ 0.65 | Bias-free representation |

---

## Project Structure

```
OmniCore-Ontology-Platform/
├── src/
│   ├── common/                     # Shared utilities
│   │   ├── __init__.py
│   │   ├── config.py               # Configuration management
│   │   ├── logging_config.py       # Centralized logging
│   │   ├── http_client.py          # Async HTTP client
│   │   ├── models.py               # Shared Pydantic models
│   │   ├── database.py             # SQLite utilities
│   │   ├── auth.py                 # JWT authentication
│   │   └── exceptions.py           # Custom exceptions
│   │
│   ├── core/
│   │   ├── roots/                  # Group A - Roots Service
│   │   │   ├── api.py              # FastAPI endpoints
│   │   │   ├── models.py           # Root-specific models
│   │   │   ├── store.py            # SQLite storage layer
│   │   │   └── service.py          # Business logic
│   │   │
│   │   ├── causality/              # Group B - Causality Service
│   │   ├── epistemic/              # Group C - Epistemic Service
│   │   ├── mmo/                    # Group D - MMO Service
│   │   ├── global_srv/             # Group E - Global Service
│   │   └── gateway/                # Group F - API Gateway
│   │
│   └── frontend/
│       └── omnicloud-ui/           # Group G - React Dashboard
│           ├── src/
│           │   ├── pages/          # Page components
│           │   ├── components/     # Reusable components
│           │   ├── api/            # API client
│           │   └── types/          # TypeScript types
│           ├── package.json
│           └── vite.config.ts
│
├── data/                           # SQLite databases (auto-created)
├── infra/
│   ├── podman-compose.yml          # Container orchestration
│   └── env/.env.example            # Environment template
├── tests/                          # Test suite
├── requirements.txt                # Python dependencies
└── README.md
```

---

## Setup on Windows (Local Development)

### Prerequisites

Before starting, ensure you have the following installed:

| Software | Version | Download Link |
|----------|---------|---------------|
| **Python** | 3.11+ | [python.org](https://www.python.org/downloads/) |
| **Node.js** | 18+ | [nodejs.org](https://nodejs.org/) |
| **Git** | Latest | [git-scm.com](https://git-scm.com/download/win) |
| **Redis** (optional) | 7+ | [Redis for Windows](https://github.com/microsoftarchive/redis/releases) or use Docker |

### Step 1: Clone the Repository

```powershell
# Open PowerShell or Command Prompt
git clone https://github.com/XushnazarovFaxriddin/OmniCore-Ontology-Platform.git
cd OmniCore-Ontology-Platform
```

### Step 2: Set Up Python Virtual Environment

```powershell
# Create virtual environment
python -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1    # PowerShell
# OR
.\.venv\Scripts\activate.bat     # Command Prompt

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Configure Environment

```powershell
# Copy environment template
copy infra\env\.env.example .env

# Create data directory
mkdir data
```

Edit `.env` file with your preferred settings (optional for development):
```ini
OMNICORE_ENV=development
OMNICORE_LOG_LEVEL=INFO
DATABASE_PATH=./data
JWT_SECRET_KEY=your-dev-secret-key-change-in-production
```

### Step 4: Install Frontend Dependencies

```powershell
cd src\frontend\omnicloud-ui
npm install
cd ..\..\..
```

### Step 5: Run Services (Development Mode)

**Option A: Run All Services with a Script**

Create `run-dev.ps1` in the project root:
```powershell
# run-dev.ps1 - Windows Development Launcher
$env:PYTHONPATH = (Get-Location).Path + "\src"
$env:DATABASE_PATH = (Get-Location).Path + "\data"
$env:OMNICORE_ENV = "development"

# Start backend services in separate terminals
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd src\core\roots; python -m uvicorn api:app --port 8001 --reload"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd src\core\causality; python -m uvicorn api:app --port 8002 --reload"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd src\core\epistemic; python -m uvicorn api:app --port 8003 --reload"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd src\core\mmo; python -m uvicorn api:app --port 8004 --reload"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd src\core\global_srv; python -m uvicorn api:app --port 8005 --reload"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd src\core\gateway; python -m uvicorn api:app --port 8000 --reload"

# Start frontend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd src\frontend\omnicloud-ui; npm run dev"

Write-Host "All services starting..."
Write-Host "API Gateway: http://localhost:8000"
Write-Host "Dashboard:   http://localhost:3000"
Write-Host "API Docs:    http://localhost:8000/docs"
```

Run with:
```powershell
.\run-dev.ps1
```

**Option B: Run Services Manually (One by One)**

Open separate terminal windows for each service:

```powershell
# Terminal 1 - Roots Service
$env:PYTHONPATH="C:\path\to\OmniCore-Ontology-Platform\src"
$env:DATABASE_PATH="C:\path\to\OmniCore-Ontology-Platform\data"
cd src\core\roots
python -m uvicorn api:app --port 8001 --reload

# Terminal 2 - Causality Service
$env:PYTHONPATH="C:\path\to\OmniCore-Ontology-Platform\src"
$env:DATABASE_PATH="C:\path\to\OmniCore-Ontology-Platform\data"
cd src\core\causality
python -m uvicorn api:app --port 8002 --reload

# Terminal 3 - Epistemic Service
$env:PYTHONPATH="C:\path\to\OmniCore-Ontology-Platform\src"
$env:DATABASE_PATH="C:\path\to\OmniCore-Ontology-Platform\data"
cd src\core\epistemic
python -m uvicorn api:app --port 8003 --reload

# Terminal 4 - MMO Service
$env:PYTHONPATH="C:\path\to\OmniCore-Ontology-Platform\src"
$env:DATABASE_PATH="C:\path\to\OmniCore-Ontology-Platform\data"
cd src\core\mmo
python -m uvicorn api:app --port 8004 --reload

# Terminal 5 - Global Service
$env:PYTHONPATH="C:\path\to\OmniCore-Ontology-Platform\src"
$env:DATABASE_PATH="C:\path\to\OmniCore-Ontology-Platform\data"
cd src\core\global_srv
python -m uvicorn api:app --port 8005 --reload

# Terminal 6 - API Gateway
$env:PYTHONPATH="C:\path\to\OmniCore-Ontology-Platform\src"
$env:DATABASE_PATH="C:\path\to\OmniCore-Ontology-Platform\data"
cd src\core\gateway
python -m uvicorn api:app --port 8000 --reload

# Terminal 7 - Frontend
cd src\frontend\omnicloud-ui
npm run dev
```

### Step 6: Verify Installation

```powershell
# Test API Gateway health
curl http://localhost:8000/health

# Test all services health
curl http://localhost:8000/api/health/overview

# Open Dashboard
start http://localhost:3000

# Open API Documentation
start http://localhost:8000/docs
```

### Windows with Docker Desktop (Alternative)

If you prefer containerized development:

```powershell
# Install Docker Desktop with WSL2 backend
# Enable Kubernetes in Docker Desktop settings

# Run with docker-compose (convert podman-compose)
cd infra
docker-compose -f podman-compose.yml up -d

# Note: You may need to adjust the compose file for Docker compatibility
```

---

## Setup on AlmaLinux 8.9 (PARAM BILIM)

### PARAM BILIM Environment Specifications

| Resource | Per Group | Shared Global |
|----------|-----------|---------------|
| CPU | 1 core (dev), 8 cores (batch) | 32-core orchestration node |
| GPU | 0.25 A100 (80GB) | 2 full A100s (SLM pool) |
| Storage | 10 GB `/home` | 1 TB `/scratch/omnicore` |
| Network | Ports 8000–8010 | Gateway (8000), Dashboard (3000) |

### Prerequisites

```bash
# Verify AlmaLinux version
cat /etc/redhat-release
# Expected: AlmaLinux release 8.9

# Check Podman installation
podman --version
# Expected: podman version 4.x+

# Check Python version
python3 --version
# Expected: Python 3.11+

# Check Node.js (if available)
node --version
# Expected: v18+
```

### Step 1: Clone Repository

```bash
# Navigate to scratch directory (recommended for PARAM BILIM)
cd /scratch/omnicore

# Clone repository
git clone https://github.com/XushnazarovFaxriddin/OmniCore-Ontology-Platform.git
cd OmniCore-Ontology-Platform

# Set permissions
chmod -R 755 .
```

### Step 2: Set Up Python Environment

```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Configure Environment

```bash
# Copy environment template
cp infra/env/.env.example infra/env/.env

# Edit configuration for production
vi infra/env/.env
```

Production `.env` configuration:
```ini
# Production settings for PARAM BILIM
OMNICORE_ENV=production
OMNICORE_LOG_LEVEL=INFO

# Database - use scratch storage
DATABASE_PATH=/scratch/omnicore/OmniCore-Ontology-Platform/data

# Service URLs (container hostnames)
ROOTS_SERVICE_URL=http://roots-service:8001
CAUSALITY_SERVICE_URL=http://causality-service:8002
EPISTEMIC_SERVICE_URL=http://epistemic-service:8003
MMO_SERVICE_URL=http://mmo-service:8004
GLOBAL_SERVICE_URL=http://global-ontology-service:8005

# Security - CHANGE THIS IN PRODUCTION!
JWT_SECRET_KEY=your-super-secure-production-key-minimum-32-chars
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Redis
REDIS_URL=redis://redis:6379/0
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# CORS - restrict in production
CORS_ORIGINS=http://localhost:3000,http://your-domain.com
```

### Step 4: Create Data Directory

```bash
mkdir -p /scratch/omnicore/OmniCore-Ontology-Platform/data
chmod 755 /scratch/omnicore/OmniCore-Ontology-Platform/data
```

### Step 5: Build Container Image (if not using pre-built)

```bash
# Create Containerfile for the base image
cat > Containerfile << 'EOF'
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js for frontend
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs

# Create non-root user
RUN useradd -m -u 10000 omnicore
USER omnicore

# Set working directory
WORKDIR /mnt/shared

# Default command
CMD ["bash"]
EOF

# Build the image
podman build -t localhost/omnicore:base -f Containerfile .
```

### Step 6: Deploy with Podman Compose

```bash
# Navigate to infra directory
cd infra

# Start all services
podman-compose up -d

# Verify all containers are running
podman-compose ps

# Check logs
podman-compose logs -f api-gateway
```

### Step 7: Configure Firewall (if needed)

```bash
# Allow required ports
sudo firewall-cmd --permanent --add-port=8000/tcp  # API Gateway
sudo firewall-cmd --permanent --add-port=3000/tcp  # Dashboard
sudo firewall-cmd --reload
```

### Step 8: Set Up as Systemd Service (Optional)

Create `/etc/systemd/system/omnicore.service`:

```ini
[Unit]
Description=OmniCore Ontology Platform
After=network.target

[Service]
Type=simple
User=omnicore
WorkingDirectory=/scratch/omnicore/OmniCore-Ontology-Platform/infra
ExecStart=/usr/bin/podman-compose up
ExecStop=/usr/bin/podman-compose down
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable omnicore
sudo systemctl start omnicore
sudo systemctl status omnicore
```

### Step 9: Verify Deployment

```bash
# Test API Gateway
curl http://localhost:8000/health

# Test service health overview
curl http://localhost:8000/api/health/overview

# Test creating a root entity
curl -X POST http://localhost:8000/api/roots \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Entity", "root_type": "EXTANT", "description": "Test"}'

# Access Dashboard (if GUI available)
firefox http://localhost:3000 &
```

### GPU Configuration (PARAM BILIM Specific)

For services requiring GPU access (Causality Service, API Gateway):

```bash
# Verify NVIDIA drivers
nvidia-smi

# Check GPU availability for Podman
podman run --rm --device nvidia.com/gpu=0 nvidia/cuda:11.8-base nvidia-smi
```

In `podman-compose.yml`, GPU services are configured with:
```yaml
devices:
  - nvidia.com/gpu=0  # For Causality Service
  - nvidia.com/gpu=1  # For API Gateway
```

---

## Running the Services

### Service URLs (After Deployment)

| Service | URL | Description |
|---------|-----|-------------|
| API Gateway | http://localhost:8000 | Main entry point |
| API Documentation | http://localhost:8000/docs | Swagger UI |
| ReDoc | http://localhost:8000/redoc | Alternative API docs |
| Dashboard | http://localhost:3000 | React management UI |
| Health Overview | http://localhost:8000/api/health/overview | All services status |

### Podman Commands Reference

```bash
# Start all services
podman-compose up -d

# Stop all services
podman-compose down

# View logs
podman-compose logs -f [service-name]

# Restart a specific service
podman-compose restart roots-service

# Check container status
podman-compose ps

# Execute command in container
podman exec -it omnicore-gateway bash

# View resource usage
podman stats
```

---

## API Documentation

### Authentication

The API Gateway supports two authentication methods:

**1. JWT Token (Recommended)**
```bash
# Get token
curl -X POST http://localhost:8000/api/auth/token \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "scopes": ["read", "write"]}'

# Response:
# {"access_token": "eyJ...", "token_type": "bearer", "expires_in": 86400}

# Use token in requests
curl http://localhost:8000/api/roots \
  -H "Authorization: Bearer eyJ..."
```

**2. API Key**
```bash
curl http://localhost:8000/api/roots \
  -H "X-API-Key: your-api-key"
```

### Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| **Roots** |||
| `/api/roots` | GET | List all roots (paginated) |
| `/api/roots` | POST | Create a new root |
| `/api/roots/{id}` | GET | Get root by ID |
| `/api/roots/{id}` | PUT | Update root |
| `/api/roots/{id}` | DELETE | Delete root |
| `/api/roots/summary` | GET | Get root statistics |
| `/api/roots/by-type/{type}` | GET | Filter by root type |
| **Causality** |||
| `/api/causality-links` | GET/POST | List/create causality links |
| `/api/causality-links/{id}` | GET/PUT/DELETE | CRUD operations |
| `/api/causality-summary` | GET | Get causality statistics |
| **Epistemic** |||
| `/api/annotations` | GET/POST | List/create annotations |
| `/api/annotations/{id}` | GET/PUT/DELETE | CRUD operations |
| `/api/annotations/summary` | GET | Get annotation statistics |
| **MMO** |||
| `/api/classes` | GET/POST | List/create MMO classes |
| `/api/slots` | GET/POST | List/create MMO slots |
| `/api/metrics` | GET | Get current MMO metrics |
| `/api/metrics/recalculate` | POST | Trigger metrics recalculation |
| `/api/schema` | GET | Get full MMO schema |
| **Global** |||
| `/api/global/stats` | GET | Global statistics |
| `/api/global/sample` | GET | Sample data from all services |
| `/api/global/summary` | GET | Comprehensive summary |
| `/api/system/health` | GET | All services health status |

### Example Requests

```bash
# Create a root entity
curl -X POST http://localhost:8000/api/roots \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Consciousness",
    "root_type": "MENTAL",
    "description": "Subjective awareness and experience"
  }'

# Create a causality link
curl -X POST http://localhost:8000/api/causality-links \
  -H "Content-Type: application/json" \
  -d '{
    "source_entity_id": "entity-uuid-1",
    "target_entity_id": "entity-uuid-2",
    "causality_type": "EMERGENT",
    "confidence": 0.85
  }'

# Create an epistemic annotation
curl -X POST http://localhost:8000/api/annotations \
  -H "Content-Type: application/json" \
  -d '{
    "entity_id": "entity-uuid-1",
    "certainty": 0.92,
    "basis": "empirical",
    "source": "DOI:10.1234/example"
  }'

# Get MMO metrics
curl http://localhost:8000/api/metrics
```

---

## Testing

### Run All Tests

```bash
# Activate virtual environment
source .venv/bin/activate  # Linux/Mac
.\.venv\Scripts\Activate.ps1  # Windows

# Run all tests with verbose output
pytest tests/ -v

# Run with coverage report
pytest tests/ -v --cov=src --cov-report=html

# Open coverage report
open htmlcov/index.html  # Mac
start htmlcov/index.html  # Windows
xdg-open htmlcov/index.html  # Linux
```

### Run Specific Service Tests

```bash
# Test Roots Service
pytest tests/test_roots.py -v

# Test Causality Service
pytest tests/test_causality.py -v

# Test Epistemic Service
pytest tests/test_epistemic.py -v

# Test MMO Service
pytest tests/test_mmo.py -v

# Test API Gateway
pytest tests/test_gateway.py -v

# Test Global Service
pytest tests/test_global.py -v
```

### Test Coverage Requirements

Per the v10 specification, target **80%+ test coverage** for Horizon 1 completion.

---

## Configuration Reference

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `OMNICORE_ENV` | Environment mode | `development` | No |
| `OMNICORE_LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | `INFO` | No |
| `OMNICORE_SERVICE` | Service identifier | - | Auto-set |
| `OMNICORE_PORT` | Service port | - | Auto-set |
| `DATABASE_PATH` | SQLite database directory | `/mnt/extra/omnicore-shared/data` | Yes |
| `JWT_SECRET_KEY` | JWT signing secret | - | **Yes (Production)** |
| `JWT_ALGORITHM` | JWT algorithm | `HS256` | No |
| `JWT_EXPIRATION_HOURS` | Token expiration | `24` | No |
| `REDIS_URL` | Redis connection URL | `redis://redis:6379/0` | No |
| `RATE_LIMIT_REQUESTS` | Requests per window | `100` | No |
| `RATE_LIMIT_WINDOW` | Rate limit window (seconds) | `60` | No |
| `CORS_ORIGINS` | Allowed CORS origins | `*` | No |
| `ROOTS_SERVICE_URL` | Roots service URL | `http://roots-service:8001` | No |
| `CAUSALITY_SERVICE_URL` | Causality service URL | `http://causality-service:8002` | No |
| `EPISTEMIC_SERVICE_URL` | Epistemic service URL | `http://epistemic-service:8003` | No |
| `MMO_SERVICE_URL` | MMO service URL | `http://mmo-service:8004` | No |
| `GLOBAL_SERVICE_URL` | Global service URL | `http://global-ontology-service:8005` | No |

---

## Troubleshooting

### Common Issues

**1. Port Already in Use**
```bash
# Find process using port
netstat -tlnp | grep 8000  # Linux
netstat -ano | findstr 8000  # Windows

# Kill process
kill -9 <PID>  # Linux
taskkill /PID <PID> /F  # Windows
```

**2. Database Locked Error**
```bash
# Remove lock file
rm data/*.db-journal

# Or restart services
podman-compose restart
```

**3. Python Module Not Found**
```bash
# Ensure PYTHONPATH is set
export PYTHONPATH=/path/to/OmniCore-Ontology-Platform/src

# Or add to virtual environment
echo 'export PYTHONPATH=/path/to/src' >> .venv/bin/activate
```

**4. Frontend Build Fails**
```bash
# Clear npm cache
npm cache clean --force

# Remove node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

**5. Podman Permission Denied**
```bash
# Run without root (rootless mode)
podman-compose --podman-run-args="--userns=keep-id" up -d

# Or adjust SELinux (AlmaLinux)
sudo setsebool -P container_manage_cgroup on
```

**6. Services Not Communicating**
```bash
# Check network
podman network ls
podman network inspect omnicore_default

# Verify DNS resolution
podman exec omnicore-gateway ping roots-service
```

### Health Check Commands

```bash
# Quick health check all services
for port in 8001 8002 8003 8004 8005 8000; do
  echo "Port $port: $(curl -s http://localhost:$port/health | jq -r .status)"
done

# Detailed system health
curl -s http://localhost:8000/api/health/overview | jq
```

### Logs Location

| Environment | Log Location |
|-------------|--------------|
| Development | Console (stdout) |
| Podman | `podman-compose logs [service]` |
| Production | `/var/log/omnicore/` (if configured) |

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make changes and add tests
4. Run tests (`pytest tests/ -v`)
5. Commit changes (`git commit -m 'Add amazing feature'`)
6. Push to branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Code Standards

- All code requires `REVIEWED_BY: <student_id>` signature
- Static analysis must pass (`ruff`, `bandit`)
- Minimum 80% test coverage
- Follow PEP 8 style guide

---

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

## Authors

- **Kaizen Group** - Initial development
- **Fakhriddin Khushnazarov** - Architectural synthesis & implementation
- **Supervisor**: KREMENCHUTSKIY A.

---

## Acknowledgments

- PARAM BILIM Supercomputer team for infrastructure support
- FastAPI and Pydantic communities for excellent frameworks
- The ontology research community for foundational concepts

---

**Version**: 10.0
**Status**: Finalized — Ready for Implementation
**Last Updated**: December 2025
