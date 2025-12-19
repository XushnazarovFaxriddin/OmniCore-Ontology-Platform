# OmniCore Ontology Platform v10

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Ollama](https://img.shields.io/badge/Ollama-SLM-orange.svg)](https://ollama.ai/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**AI-Orchestrated Ontological Computing System**
**Deployment Target**: PARAM BILIM Supercomputer (AlmaLinux 8.9, Podman, NVIDIA A100 GPUs)

> *"Start deterministic, augment intelligently, evolve autonomously — without sacrificing verifiability."*

---

## Table of Contents

1. [Overview](#overview)
2. [Key Features](#key-features)
3. [Architecture](#architecture)
4. [Quick Start](#quick-start)
5. [Installation](#installation)
6. [Usage](#usage)
7. [API Reference](#api-reference)
8. [SLM Integration](#slm-integration)
9. [Configuration](#configuration)
10. [Development](#development)
11. [Deployment](#deployment)
12. [Troubleshooting](#troubleshooting)

---

## Overview

OmniCore is the world's first **self-evolving meta-ontological platform** that:

- ✅ **Unifies** heterogeneous ontologies into a coherent Meta-Ontology (MO)
- ✅ **Evaluates** MO quality via self-calibrating Meta-Meta-Ontology (MMO) metrics
- ✅ **Augments** with Small Language Models (SLM) for intelligent inference
- ✅ **Evolves** through AI-driven harvesting, conflict resolution, and strategic planning
- ✅ **Maintains** full provenance tracking and human oversight capabilities

### Three-Horizon Strategy

| Horizon | Phase | Goal | Key Deliverables |
|---------|-------|------|------------------|
| **H1** | Foundation | Student-built microservices | 80%+ test coverage, live deployment |
| **H2** | Augmentation | AI-enhanced operations | 100+ ontologies, 95% auto-resolution |
| **H3** | Autonomy | Multi-AI orchestration | ≤2% human intervention |

---

## Key Features

### Core Services
- **Roots Service**: 4 ontological root types (EXTANT, ABSTRACT, MENTAL, FICTIVE)
- **Causality Service**: 5 causality types (Aristotelian + Emergent)
- **Epistemic Service**: Knowledge annotations with certainty tracking
- **MMO Service**: Self-calibrating quality metrics

### AI Capabilities (v10)
- **SLM Integration**: Ollama/HuggingFace for local inference
- **Root Type Inference**: AI-powered entity classification
- **Causality Extraction**: Implicit relationship discovery
- **Conflict Resolution**: Multi-agent philosophical debate
- **Strategic Planning**: Quarterly autonomous review

### Safety & Governance
- **Provenance Tracking**: Full audit trail for all entities
- **Human Oversight**: SIGUSR1 halt signal, approval workflows
- **Rollback Support**: Version-controlled MO snapshots
- **Ethical Alerts**: Bias detection and flagging

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                       Human Oversight Layer                          │
│  • SIGUSR1 Halt  • Quarterly Review  • Ethical Alerts  • Approvals  │
└──────────────────────────────────────────────────────────────────────┘
                                  │
┌──────────────────────────────────────────────────────────────────────┐
│                        AI Services Layer                             │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐    │
│  │ SLM Service │ │  Harvesting │ │  Conflict   │ │  Strategic  │    │
│  │   :18006    │ │    Swarm    │ │ Resolution  │ │   Meta-AI   │    │
│  │ Llama/Gemma │ │  (Async)    │ │  (Debate)   │ │ (Quarterly) │    │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘    │
└──────────────────────────────────────────────────────────────────────┘
                                  │
┌──────────────────────────────────────────────────────────────────────┐
│                     Core Ontological Engine                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐                │
│  │  Roots   │ │Causality │ │Epistemic │ │   MMO    │                │
│  │ :18001  │ │ :18002  │ │ :18003  │ │ :18004  │                │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘                │
└──────────────────────────────────────────────────────────────────────┘
                                  │
┌──────────────────────────────────────────────────────────────────────┐
│              Global Ontology Service (:18005)                        │
│  • MO Merge Engine  • RDFLib Parser  • Provenance  • Snapshots      │
└──────────────────────────────────────────────────────────────────────┘
                                  │
┌──────────────────────────────────────────────────────────────────────┐
│                      API Gateway (:8000)                             │
│  • JWT/API Key Auth  • Rate Limiting (Redis)  • Request Routing     │
└──────────────────────────────────────────────────────────────────────┘
                                  │
              ┌───────────────────┴───────────────────┐
              │                                       │
    ┌─────────────────┐                    ┌─────────────────┐
    │ React Dashboard │                    │   CLI / SDK     │
    │     (:3000)     │                    │    omnicore     │
    └─────────────────┘                    └─────────────────┘
```

### Service Ports

| Service | Port | GPU | Description |
|---------|------|-----|-------------|
| API Gateway | 8000 | - | Unified entry point |
| Roots | 18001 | - | Entity classification |
| Causality | 18002 | 0.25 A100 | Causal inference |
| Epistemic | 18003 | - | Knowledge annotations |
| MMO | 18004 | - | Quality metrics |
| Global | 18005 | - | MO core engine |
| SLM | 18006 | 0.25 A100 | Language model inference |
| Dashboard | 3000 | - | Web UI |
| Ollama | 11434 | 1 GPU | Local LLM server |

---

## Quick Start

### Option 1: Python Virtual Environment (Recommended for Development)

```bash
# Clone repository
git clone https://github.com/XushnazarovFaxriddin/OmniCore-Ontology-Platform.git
cd OmniCore-Ontology-Platform

# Run setup script
chmod +x scripts/setup.sh
./scripts/setup.sh --mode venv

# Activate environment
source venv/bin/activate

# Install Ollama and pull model (for SLM features)
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull llama3.2:1b

# Start platform
python -m src.orchestrator.cli start --foreground
```

### Option 2: Docker/Podman (Recommended for Production)

```bash
# Clone and setup
git clone https://github.com/XushnazarovFaxriddin/OmniCore-Ontology-Platform.git
cd OmniCore-Ontology-Platform
./scripts/setup.sh --mode podman

# Start all services
podman-compose -f infra/podman-compose.yml up -d

# Verify
curl http://localhost:8000/health
```

### Verify Installation

```bash
# Check all services
curl http://localhost:8000/health

# Open Dashboard
open http://localhost:3000  # macOS
xdg-open http://localhost:3000  # Linux
start http://localhost:3000  # Windows
```

---

## Installation

### Prerequisites

| Software | Version | Required For |
|----------|---------|--------------|
| Python | 3.11+ | Core services |
| Node.js | 18+ | Dashboard |
| Ollama | Latest | SLM inference |
| Podman/Docker | Latest | Container deployment |
| Redis | 7+ | Rate limiting |

### Windows Setup

```powershell
# 1. Clone repository
git clone https://github.com/XushnazarovFaxriddin/OmniCore-Ontology-Platform.git
cd OmniCore-Ontology-Platform

# 2. Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create data directory
mkdir data, logs, snapshots, ontologies

# 5. Install Ollama from https://ollama.ai
# Then pull model:
ollama pull llama3.2:1b

# 6. Start platform
python -m src.orchestrator.cli start
```

### Linux/macOS Setup

```bash
# 1. Clone repository
git clone https://github.com/XushnazarovFaxriddin/OmniCore-Ontology-Platform.git
cd OmniCore-Ontology-Platform

# 2. Run setup script
./scripts/setup.sh --mode venv

# 3. Activate environment
source venv/bin/activate

# 4. Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh
ollama serve &
ollama pull llama3.2:1b

# 5. Start platform
python -m src.orchestrator.cli start
```

### AlmaLinux 8.9 (PARAM BILIM)

```bash
# 1. Navigate to scratch directory
cd /scratch/omnicore

# 2. Clone and setup
git clone https://github.com/XushnazarovFaxriddin/OmniCore-Ontology-Platform.git
cd OmniCore-Ontology-Platform
./scripts/setup.sh --mode podman

# 3. Configure environment
cp infra/env/.env.example .env
vi .env  # Add HF_TOKEN, JWT_SECRET_KEY

# 4. Deploy with Podman
podman-compose -f infra/podman-compose.yml up -d

# 5. Verify GPU allocation
nvidia-smi
podman-compose ps
```

---

## Usage

### CLI Commands

```bash
# Start all services
python -m src.orchestrator.cli start

# Start specific service
python -m src.orchestrator.cli start --service roots

# Check status
python -m src.orchestrator.cli status

# Health check
python -m src.orchestrator.cli health

# List services
python -m src.orchestrator.cli services

# Import ontology
python -m src.orchestrator.cli import https://example.org/ontology.owl --use-slm

# SLM operations
python -m src.orchestrator.cli slm status
python -m src.orchestrator.cli slm models
python -m src.orchestrator.cli slm pull llama3.2:1b

# Strategic review
python -m src.orchestrator.cli strategic review

# Stop platform
python -m src.orchestrator.cli stop
```

### API Examples

```bash
# Create a root entity
curl -X POST http://localhost:8000/api/roots \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Consciousness",
    "root_type": "MENTAL",
    "description": "Subjective awareness",
    "use_slm": true
  }'

# Create causality link
curl -X POST http://localhost:8000/api/causality-links \
  -H "Content-Type: application/json" \
  -d '{
    "source_entity_id": "uuid-1",
    "target_entity_id": "uuid-2",
    "causality_type": "EMERGENT",
    "confidence": 0.85
  }'

# Import ontology with SLM enhancement
curl -X POST http://localhost:8000/api/ontologies/import \
  -H "Content-Type: application/json" \
  -d '{
    "source_url": "http://purl.obolibrary.org/obo/go.owl",
    "format": "xml",
    "use_slm": true,
    "conflict_resolution": "auto"
  }'

# Get MMO metrics
curl http://localhost:8000/api/metrics

# Infer root type with SLM
curl -X POST http://localhost:18006/infer-root-type \
  -H "Content-Type: application/json" \
  -d '{
    "entity_name": "Sherlock Holmes",
    "description": "Fictional detective character",
    "context": "Literature"
  }'
```

---

## API Reference

### Authentication

```bash
# Get JWT token
curl -X POST http://localhost:8000/api/auth/token \
  -d '{"username": "admin", "scopes": ["read", "write"]}'

# Use token
curl http://localhost:8000/api/roots \
  -H "Authorization: Bearer <token>"

# Or use API key
curl http://localhost:8000/api/roots \
  -H "X-API-Key: <api-key>"
```

### Endpoints Summary

| Category | Endpoint | Methods |
|----------|----------|---------|
| **Auth** | `/api/auth/token` | POST |
| **Roots** | `/api/roots` | GET, POST |
| **Roots** | `/api/roots/{id}` | GET, PUT, DELETE |
| **Causality** | `/api/causality-links` | GET, POST |
| **Epistemic** | `/api/annotations` | GET, POST |
| **MMO** | `/api/classes`, `/api/slots` | GET, POST |
| **MMO** | `/api/metrics` | GET |
| **Global** | `/api/global/stats` | GET |
| **Import** | `/api/ontologies/import` | POST |
| **SLM** | `/api/slm/infer-root-type` | POST |
| **Health** | `/health` | GET |

---

## SLM Integration

### Supported Models

| Provider | Models | Use Case |
|----------|--------|----------|
| Ollama | llama3.2:1b, gemma2:2b, mistral:7b | Local inference |
| HuggingFace | Llama-3.2-1B-Instruct | Cloud/local |

### SLM Tasks

1. **Root Type Inference**: Classify entities into EXTANT/ABSTRACT/MENTAL/FICTIVE
2. **Causality Extraction**: Discover implicit causal relationships
3. **Epistemic Annotation**: Generate certainty and basis
4. **Conflict Resolution**: Multi-agent philosophical debate
5. **Quality Assessment**: Score ontologies for integration

### Configuration

```bash
# Environment variables
SLM_BASE_URL=http://localhost:11434  # Ollama
SLM_MODEL_NAME=llama3.2:1b
SLM_FALLBACK_MODEL=gemma2:2b
SLM_CONFIDENCE_THRESHOLD=0.6
SLM_TEMPERATURE=0.1
```

### v10 Safety Rules

- SLM outputs include `ai_confidence` score
- If confidence < 0.6, fallback to rule-based mapping
- Low confidence results flagged for human review
- All enhancements tracked in provenance

---

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OMNICORE_ENV` | development | Environment mode |
| `DATABASE_PATH` | ./data | SQLite directory |
| `JWT_SECRET_KEY` | (required) | JWT signing key |
| `REDIS_URL` | redis://localhost:6379 | Redis connection |
| `SLM_BASE_URL` | http://localhost:11434 | Ollama URL |
| `SLM_MODEL_NAME` | llama3.2:1b | Default SLM model |
| `GPU_ENABLED` | false | Enable GPU acceleration |

### Example .env

```ini
OMNICORE_ENV=production
DATABASE_PATH=/scratch/omnicore/data
JWT_SECRET_KEY=your-secure-key-min-32-chars
REDIS_URL=redis://redis:6379/0
SLM_BASE_URL=http://ollama:11434
SLM_MODEL_NAME=llama3.2:1b
GPU_ENABLED=true
CUDA_VISIBLE_DEVICES=0,1
HF_TOKEN=hf_your_token_here
```

---

## Development

### Running Tests

```bash
# All tests
pytest tests/ -v

# With coverage
pytest tests/ -v --cov=src --cov-report=html

# Specific service
pytest tests/test_roots.py -v
```

### Code Quality

```bash
# Linting
ruff check src/

# Format check
ruff format --check src/
```

### Project Structure

```
OmniCore-Ontology-Platform/
├── src/
│   ├── common/          # Shared utilities
│   ├── core/            # Core microservices
│   │   ├── roots/       # Roots Service
│   │   ├── causality/   # Causality Service
│   │   ├── epistemic/   # Epistemic Service
│   │   ├── mmo/         # MMO Service
│   │   ├── global_srv/  # Global Service
│   │   └── gateway/     # API Gateway
│   ├── ai/              # AI services
│   │   ├── slm/         # SLM client & service
│   │   ├── harvesting/  # Ontology harvesting
│   │   └── strategic/   # Strategic Meta-AI
│   ├── rdf/             # RDF/OWL parser
│   ├── orchestrator/    # CLI & orchestration
│   └── frontend/        # React dashboard
├── infra/               # Infrastructure configs
├── scripts/             # Setup scripts
├── tests/               # Test suite
├── Dockerfile           # Container image
└── requirements.txt     # Dependencies
```

---

## Deployment

### Podman Compose (Production)

```bash
# Build and start
podman-compose -f infra/podman-compose.yml up -d

# View logs
podman-compose logs -f api-gateway

# Scale service
podman-compose up -d --scale roots-service=2

# Stop
podman-compose down
```

### Docker Compose

```bash
# Same commands, replace podman-compose with docker-compose
docker-compose -f infra/podman-compose.yml up -d
```

### Kubernetes (Advanced)

```bash
# Convert compose to k8s manifests
kompose convert -f infra/podman-compose.yml

# Apply to cluster
kubectl apply -f .
```

---

## Troubleshooting

### Common Issues

**SLM not responding:**
```bash
# Check Ollama is running
curl http://localhost:11434/api/tags

# Pull model if missing
ollama pull llama3.2:1b
```

**Port in use:**
```bash
# Find process
lsof -i :8000

# Kill process
kill -9 <PID>
```

**Database locked:**
```bash
# Remove lock files
rm data/*.db-journal
```

**GPU not detected:**
```bash
# Check NVIDIA driver
nvidia-smi

# Check container GPU access
podman run --rm --device nvidia.com/gpu=0 nvidia/cuda:11.8-base nvidia-smi
```

### Health Check

```bash
# All services
for port in 8000 18001 18002 18003 18004 18005 18006; do
  echo "Port $port: $(curl -s http://localhost:$port/health | jq -r .status 2>/dev/null || echo 'down')"
done
```

---

## License

MIT License - see [LICENSE](LICENSE) for details.

---

## Authors

- **Kaizen Group** - Core development
- **Fakhriddin Khushnazarov** - Architectural synthesis
- **Supervisor**: KREMENCHUTSKIY A.

---

**Version**: 10.0.0
**Status**: Ready for Implementation
**Target**: PARAM BILIM Supercomputer
