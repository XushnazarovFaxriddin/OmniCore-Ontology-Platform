# OmniCore Ontology Platform v10

## Complete Guide and Documentation

---

## Table of Contents

1. [Introduction](#introduction)
2. [What is OmniCore?](#what-is-omnicore)
3. [Key Features](#key-features)
4. [Architecture Overview](#architecture-overview)
5. [Core Concepts](#core-concepts)
6. [Installation](#installation)
7. [Quick Start](#quick-start)
8. [Services Overview](#services-overview)
9. [API Reference](#api-reference)
10. [CLI Commands](#cli-commands)
11. [SLM Integration](#slm-integration)
12. [Ontology Import](#ontology-import)
13. [AI Features](#ai-features)
14. [Configuration](#configuration)
15. [Deployment Options](#deployment-options)
16. [Troubleshooting](#troubleshooting)
17. [FAQ](#faq)

---

## Introduction

**OmniCore Ontology Platform** is a cutting-edge, AI-orchestrated ontological computing system designed to manage, analyze, and enhance knowledge representations at scale. Built with modern microservices architecture, it leverages Small Language Models (SLM) to provide intelligent ontology processing while maintaining human oversight and safety controls.

### Why OmniCore?

Traditional ontology management systems lack intelligent automation and require extensive manual curation. OmniCore bridges this gap by:

- **Automating** ontology import, classification, and enhancement
- **Preserving** semantic integrity through rule-based and AI-assisted processing
- **Scaling** to handle thousands of ontologies with consistent quality
- **Ensuring** safety through provenance tracking and human oversight

---

## What is OmniCore?

OmniCore is a complete platform for ontological computing that combines:

```
┌─────────────────────────────────────────────────────────────────┐
│                    OmniCore Platform v10                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │  Roots   │  │Causality │  │Epistemic │  │   MMO    │        │
│  │ Service  │  │ Service  │  │ Service  │  │ Service  │        │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘        │
│       │             │             │             │               │
│       └─────────────┴──────┬──────┴─────────────┘               │
│                            │                                    │
│                    ┌───────┴───────┐                            │
│                    │ Global Service│                            │
│                    └───────┬───────┘                            │
│                            │                                    │
│  ┌─────────────────────────┴─────────────────────────┐          │
│  │                  API Gateway                       │          │
│  └─────────────────────────┬─────────────────────────┘          │
│                            │                                    │
│  ┌─────────────────────────┴─────────────────────────┐          │
│  │               SLM Service (Ollama)                │          │
│  │           Llama 3.2-1B / Gemma 2B                 │          │
│  └───────────────────────────────────────────────────┘          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Core Philosophy

> **"Start deterministic, augment intelligently"**

OmniCore follows a hybrid approach:
1. **Deterministic Processing**: All structured data (RDF/OWL) is parsed losslessly
2. **AI Enhancement**: SLM augments where natural-language context fills gaps
3. **Human Oversight**: Critical changes require human approval

---

## Key Features

### 1. Ontology Management

| Feature | Description |
|---------|-------------|
| **Multi-format Support** | Import RDF, OWL, Turtle, N3, N-Triples, JSON-LD |
| **Automatic Classification** | AI-powered root type inference |
| **Causality Extraction** | Detect implicit causal relationships |
| **Epistemic Annotation** | Track certainty and knowledge basis |
| **Conflict Resolution** | AI debate system for resolving disagreements |

### 2. Four Root Types (v10 Spec)

```
┌─────────────────────────────────────────────────────────────┐
│                     ROOT TYPES                              │
├─────────────┬───────────────────────────────────────────────┤
│   EXTANT    │ Entities with spatiotemporal location        │
│             │ Examples: Person, Building, Event            │
├─────────────┼───────────────────────────────────────────────┤
│  ABSTRACT   │ Atemporal, mind-independent structures       │
│             │ Examples: Number, Property, Relation         │
├─────────────┼───────────────────────────────────────────────┤
│   MENTAL    │ Subjective, first-person accessible states   │
│             │ Examples: Pain, Belief, Emotion              │
├─────────────┼───────────────────────────────────────────────┤
│   FICTIVE   │ Context-dependent representations            │
│             │ Examples: Sherlock Holmes, Unicorn           │
└─────────────┴───────────────────────────────────────────────┘
```

### 3. Five Causality Types (Aristotelian + Emergent)

| Type | Predicate | Example |
|------|-----------|---------|
| **EFFICIENT** | causesDirectly | Hammer → Nail driving |
| **FINAL** | servesPurpose | Nest → Offspring protection |
| **MATERIAL** | constitutedBy | Statue → Bronze |
| **FORMAL** | structuredAs | Organism → Genome |
| **EMERGENT** | emergesFrom | Consciousness → Neural activity |

### 4. AI-Powered Features

- **SLM Integration**: Ollama with Llama 3.2-1B or Gemma 2B
- **Ontology Harvesting**: Autonomous discovery from academic and web sources
- **Strategic Meta-AI**: Quarterly self-evaluation and planning
- **Conflict Debate**: Multi-agent philosophical debate for resolution (Visualized in Debate Lab)
- **Strategic Dashboard**: Real-time monitoring of AI goals and oversight

### 5. Safety & Oversight

- **Provenance Tracking**: Every entity retains import source and AI trace
- **Human Oversight Interface**: Strategic Dashboard for approving AI plans
- **Rollback Support**: Revert to any previous MO version
- **Ethical Alerts**: Automatic flagging of bias or concerning patterns
- **SIGUSR1 Halt**: Emergency stop signal for autonomous operations

---

## Architecture Overview

### Microservices

```
Port    Service              Description
────    ───────              ───────────
18000   API Gateway          Unified entry point, auth, rate limiting
18001   Roots Service        Root type management (EXTANT/ABSTRACT/MENTAL/FICTIVE)
18002   Causality Service    Causal relationship management
18003   Epistemic Service    Knowledge certainty and basis tracking
18004   MMO Service          Meta-Meta-Ontology classes and metrics
18005   Global Service       Aggregation and system health
18006   SLM Service          Small Language Model inference
3000    Dashboard            React-based web interface
```

### Technology Stack

| Layer | Technology |
|-------|------------|
| **API Framework** | FastAPI + Pydantic v2 |
| **Database** | SQLite with WAL mode |
| **Caching** | Redis |
| **RDF Processing** | RDFLib 7.0 |
| **SLM Runtime** | Ollama |
| **Models** | Llama 3.2-1B, Gemma 2B |
| **Containerization** | Docker / Podman |
| **GPU Support** | NVIDIA CUDA (A100 compatible) |

---

## Core Concepts

### Meta-Ontology (MO)

The central knowledge structure that stores:
- **Roots**: Fundamental entity classifications
- **Causality Links**: Causal relationships between entities
- **Epistemic Annotations**: Certainty and basis of knowledge claims

### Meta-Meta-Ontology (MMO)

The schema that defines MO structure:
- **Classes**: Categories of entities
- **Slots**: Properties and relationships
- **Metrics**: Self-calibrating quality scores

### MMO Metrics

```
Metric          Target    Description
──────          ──────    ───────────
Completeness    ≥0.85     Coverage of required elements
Coverage        ≥0.70     Breadth across domains
Coherence       ≥0.95     Internal consistency
Utility         ≥0.80     Practical usefulness
Inclusivity     ≥0.65     Diversity of perspectives
```

**Score Formula**: `MMO_Score = w₁·C + w₂·Cv + w₃·Ch + w₄·U + w₅·I`

---

## Installation

### Prerequisites

- Python 3.10+
- 4GB+ RAM (8GB+ recommended)
- 10GB disk space
- (Optional) NVIDIA GPU for accelerated inference

### Method 1: Python Virtual Environment

```bash
# Clone the repository
git clone https://github.com/XushnazarovFaxriddin/OmniCore-Ontology-Platform.git
cd OmniCore-Ontology-Platform

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Install package in development mode
pip install -e .
```

### Method 2: Docker

```bash
# Clone and build
git clone https://github.com/XushnazarovFaxriddin/OmniCore-Ontology-Platform.git
cd OmniCore-Ontology-Platform

# Start with Docker Compose
docker-compose -f infra/podman-compose.yml up -d
```

### Method 3: Podman (PARAM BILIM Supercomputer)

```bash
# For AlmaLinux 8.9 / Rocky Linux
module load podman

# Start services
podman-compose -f infra/podman-compose.yml up -d
```

### Install Ollama (SLM Runtime)

```bash
# Linux/macOS
curl -fsSL https://ollama.com/install.sh | sh

# Pull models
ollama pull llama3.2:1b
ollama pull gemma2:2b  # fallback
```

---

## Quick Start

### Start All Services

```bash
# Using CLI
PYTHONPATH=src python -m orchestrator.cli start --foreground

# Or with installed package
omnicore start -f
```

### Verify Installation

```bash
# Check service health
omnicore health

# Expected output:
# Service Health Check
# ========================================
#   roots: ✓ healthy
#   causality: ✓ healthy
#   epistemic: ✓ healthy
#   mmo: ✓ healthy
#   global: ✓ healthy
#   slm: ✓ healthy
#   gateway: ✓ healthy
```

### Create Your First Root

```bash
curl -X POST http://localhost:18000/api/roots \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Eiffel Tower",
    "root_type": "EXTANT",
    "description": "Iron lattice tower in Paris, France"
  }'
```

### Import an Ontology

```bash
omnicore import http://purl.obolibrary.org/obo/bfo.owl --use-slm
```

---

## Services Overview

### 1. Roots Service (Port 18001)

Manages fundamental ontological root types.

**Endpoints:**
```
GET    /roots              List all roots (paginated)
GET    /roots/{id}         Get specific root
GET    /roots/summary      Get statistics by type
POST   /roots              Create new root
PUT    /roots/{id}         Update root
DELETE /roots/{id}         Delete root
```

**Example: Create Root**
```bash
curl -X POST http://localhost:18001/roots \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Happiness",
    "root_type": "MENTAL",
    "description": "A positive emotional state"
  }'
```

### 2. Causality Service (Port 18002)

Manages causal relationships between entities.

**Endpoints:**
```
GET    /causality-links           List all links
GET    /causality-links/{id}      Get specific link
GET    /causality-summary         Get statistics
POST   /causality-links           Create link
PUT    /causality-links/{id}      Update link
DELETE /causality-links/{id}      Delete link
```

**Example: Create Causal Link**
```bash
curl -X POST http://localhost:18002/causality-links \
  -H "Content-Type: application/json" \
  -d '{
    "source_entity_id": "entity-1",
    "target_entity_id": "entity-2",
    "causality_type": "EFFICIENT",
    "confidence": 0.85,
    "description": "Direct causal relationship"
  }'
```

### 3. Epistemic Service (Port 18003)

Tracks knowledge certainty and basis.

**Epistemic Basis Types:**
- `axiomatic` - Self-evident truths
- `empirical` - Evidence-based knowledge
- `consensus` - Community agreement
- `speculative` - Hypothetical

**Endpoints:**
```
GET    /annotations              List annotations
GET    /annotations/{id}         Get specific annotation
GET    /annotations/summary      Get statistics
POST   /annotations              Create annotation
PUT    /annotations/{id}         Update annotation
DELETE /annotations/{id}         Delete annotation
```

### 4. MMO Service (Port 18004)

Manages Meta-Meta-Ontology structure.

**Endpoints:**
```
GET    /classes                  List MMO classes
POST   /classes                  Create class
GET    /slots                    List MMO slots
POST   /slots                    Create slot
GET    /metrics                  Get current metrics
POST   /metrics/recalculate      Recalculate metrics
GET    /schema                   Get full schema
```

### 5. Global Service (Port 18005)

Aggregates data from all services.

**Endpoints:**
```
GET    /global/stats             Global statistics
GET    /global/sample            Sample data
GET    /global/summary           Comprehensive summary
GET    /system/health            System-wide health
```

### 6. SLM Service (Port 18006)

AI inference for ontology processing.

**Endpoints:**
```
GET    /health                   Provider status
GET    /models                   List available models
POST   /generate                 Direct SLM generation
POST   /infer-root-type          Classify entity
POST   /extract-causality        Find causal relations
POST   /annotate-epistemic       Generate annotations
POST   /resolve-conflict         AI debate resolution
POST   /assess-quality           Evaluate ontology
POST   /strategic-plan           Generate strategic plan
```

### 7. API Gateway (Port 18000)

Unified entry point with authentication and rate limiting.

**Features:**
- JWT authentication
- API key support
- Rate limiting (Redis-backed)
- Request logging
- CORS support

**Auth Endpoints:**
```
POST   /api/auth/token           Get JWT token
GET    /api/health/overview      All services health
```

---

## API Reference

### Authentication

**Get JWT Token:**
```bash
curl -X POST http://localhost:18000/api/auth/token \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "scopes": ["read", "write"]}'
```

**Use Token:**
```bash
curl -H "Authorization: Bearer <token>" \
  http://localhost:18000/api/roots
```

**Use API Key:**
```bash
curl -H "X-API-Key: your-api-key" \
  http://localhost:18000/api/roots
```

### Pagination

All list endpoints support pagination:

```bash
GET /roots?offset=0&limit=50
```

**Response Format:**
```json
{
  "items": [...],
  "total": 100,
  "offset": 0,
  "limit": 50,
  "has_more": true
}
```

### Error Responses

```json
{
  "error": "Not found",
  "detail": "Root with id 'xyz' not found",
  "status_code": 404
}
```

---

## CLI Commands

### Service Management

```bash
# Start platform
omnicore start                    # Background
omnicore start -f                 # Foreground
omnicore start -m docker          # Docker mode
omnicore start -m podman          # Podman mode
omnicore start -s roots           # Single service

# Stop platform
omnicore stop

# Check status
omnicore status
omnicore status --json

# Health check
omnicore health

# List services
omnicore services
```

### Ontology Operations

```bash
# Import from URL
omnicore import http://example.org/ontology.owl

# Import from file
omnicore import ./my-ontology.ttl --format turtle

# Import with SLM enhancement
omnicore import ./data.owl --use-slm
```

### SLM Operations

```bash
# Check SLM providers
omnicore slm status

# List available models
omnicore slm models

# Pull new model
omnicore slm pull llama3.2:1b
```

### Strategic Operations

```bash
# Run strategic review
omnicore strategic review

# Check oversight status
omnicore strategic status
```

### Rollback

```bash
# Dry run
omnicore rollback mo:v1.2.0 --dry-run

# Execute rollback
omnicore rollback mo:v1.2.0
```

### Strategic Meta-AI API

**Trigger Review:**
```bash
curl -X POST http://localhost:18000/api/strategic/evaluate
```

**Check Status:**
```bash
curl http://localhost:18000/api/strategic/oversight
```

**Response:**
```json
{
  "pending_approvals": 0,
  "unresolved_alerts": 1,
  "halt_active": false
}
```

---

## SLM Integration

### Supported Providers

| Provider | Status | Configuration |
|----------|--------|---------------|
| **Ollama** | Primary | Local deployment |
| **HuggingFace** | Fallback | Cloud API |
| **Local Transformers** | Optional | Direct inference |

### Recommended Models

| Model | Size | Use Case |
|-------|------|----------|
| `llama3.2:1b` | 1.3GB | Primary (fast) |
| `gemma2:2b` | 1.6GB | Fallback |
| `mistral:7b` | 4.1GB | High quality |

### Configure SLM

**Environment Variables:**
```bash
export SLM_PROVIDER=ollama
export SLM_MODEL_NAME=llama3.2:1b
export SLM_BASE_URL=http://localhost:11434
export SLM_CONFIDENCE_THRESHOLD=0.6
```

**Direct API Call:**
```bash
curl -X POST http://localhost:18006/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Classify this entity: Electron",
    "task_type": "root_mapping",
    "max_tokens": 512
  }'
```

### Root Type Inference

```bash
curl -X POST http://localhost:18006/infer-root-type \
  -H "Content-Type: application/json" \
  -d '{
    "entity_name": "Sherlock Holmes",
    "description": "A fictional detective character",
    "context": "Literature"
  }'
```

**Response:**
```json
{
  "entity_name": "Sherlock Holmes",
  "root_type": "FICTIVE",
  "confidence": 0.92,
  "reasoning": "Existence depends on narrative context"
}
```

---

## Ontology Import

### Import Pipeline

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ 1. Parse    │───▶│ 2. Extract  │───▶│ 3. Map Root │
│ RDF/OWL     │    │ Entities    │    │ Types       │
└─────────────┘    └─────────────┘    └─────────────┘
                                             │
┌─────────────┐    ┌─────────────┐    ┌──────▼──────┐
│ 6. Commit   │◀───│ 5. Resolve  │◀───│ 4. Detect   │
│ to MO       │    │ Conflicts   │    │ Conflicts   │
└─────────────┘    └─────────────┘    └─────────────┘
```

### Supported Formats

| Format | Extension | Content-Type |
|--------|-----------|--------------|
| RDF/XML | .owl, .rdf | application/rdf+xml |
| Turtle | .ttl | text/turtle |
| N-Triples | .nt | application/n-triples |
| N3 | .n3 | text/n3 |
| JSON-LD | .jsonld | application/ld+json |

### Import Examples

**From URL:**
```bash
omnicore import http://purl.obolibrary.org/obo/go.owl --use-slm
```

**From File:**
```bash
omnicore import ./ontologies/domain.ttl --format turtle
```

**Via API:**
```bash
curl -X POST http://localhost:18000/api/import \
  -H "Content-Type: application/json" \
  -d '{
    "source_url": "http://example.org/onto.owl",
    "format": "xml",
    "use_slm": true,
    "conflict_resolution": "auto"
  }'
```

### Import Result

```json
{
  "success": true,
  "ontology_id": "op_abc123_1702900000",
  "version": "mo:v1.0.0-20231218T120000Z",
  "triples_imported": 5432,
  "entities_created": 234,
  "causality_links_created": 89,
  "epistemic_annotations_created": 156,
  "conflicts_detected": 3,
  "conflicts_resolved": 3,
  "slm_enhancements": 45,
  "processing_time_ms": 2340.5
}
```

---

## AI Features

### 1. Ontology Harvesting Swarm

Autonomous discovery from configured sources:

**Sources:**
- Academic: arXiv, PubMed, ACL Anthology
- Web: DBpedia, Wikidata, Schema.org
- Standards: BFO 2.0, DOLCE, SUMO
- Domain: Gene Ontology, SNOMED CT, LKIF

**Quality Threshold:** 0.7 (70%)

### 2. Conflict Resolution via AI Debate

When ontologies disagree, three AI agents debate:

| Agent | Philosophy | Tendency |
|-------|------------|----------|
| **Platonist** | Forms exist independently | Prefers ABSTRACT |
| **Nominalist** | Only particulars exist | Prefers EXTANT |
| **Pragmatist** | Truth is what works | Context-dependent |

**Consensus Threshold:** 75% (3/4 agents agree)

**Debate Protocol:**
1. 5 rounds of argumentation
2. Each agent presents position
3. Moderator synthesizes
4. If consensus: Apply resolution
5. If no consensus: Create contextual axiom

### 3. Strategic Meta-AI

Quarterly self-evaluation against goals:

| Goal | Target |
|------|--------|
| Ontology Coverage | ≥1000 integrated |
| MMO Accuracy | ≥0.90 R² |
| AI Task Success | ≥0.92 |
| Human Interventions | ≤20/quarter |
| Ethical Flags | 0 unresolved |

**Run Manual Review:**
```bash
omnicore strategic review
```

---

## Configuration

### Environment Variables

```bash
# Application
OMNICORE_ENV=development          # development|staging|production
OMNICORE_LOG_LEVEL=INFO           # DEBUG|INFO|WARNING|ERROR

# Service Ports
API_GATEWAY_PORT=18000
ROOTS_SERVICE_PORT=18001
CAUSALITY_SERVICE_PORT=18002
EPISTEMIC_SERVICE_PORT=18003
MMO_SERVICE_PORT=18004
GLOBAL_SERVICE_PORT=18005
SLM_SERVICE_PORT=18006

# Database
DATABASE_PATH=./data/omnicore.db

# Redis
REDIS_URL=redis://localhost:6379/0
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# Authentication
JWT_SECRET_KEY=your-secret-key
JWT_EXPIRATION_HOURS=24

# SLM
SLM_PROVIDER=ollama
SLM_MODEL_NAME=llama3.2:1b
SLM_BASE_URL=http://localhost:11434
SLM_CONFIDENCE_THRESHOLD=0.6

# GPU (PARAM BILIM)
GPU_ENABLED=true
CUDA_VISIBLE_DEVICES=0
GPU_MEMORY_FRACTION=0.25
```

### Configuration File (.env)

Create `.env` in project root:

```env
OMNICORE_ENV=development
DATABASE_PATH=./data/omnicore.db
SLM_PROVIDER=ollama
SLM_MODEL_NAME=llama3.2:1b
```

---

## Deployment Options

### 1. Development (venv)

```bash
# Start
PYTHONPATH=src python -m orchestrator.cli start -f

# Access
http://localhost:18000/docs  # API documentation
http://localhost:3000       # Dashboard (if running)
```

### 2. Docker Compose

```bash
# Start all services
docker-compose -f infra/podman-compose.yml up -d

# View logs
docker-compose -f infra/podman-compose.yml logs -f

# Stop
docker-compose -f infra/podman-compose.yml down
```

### 3. Podman (HPC/PARAM BILIM)

```bash
# Load module
module load podman

# Start with GPU support
podman-compose -f infra/podman-compose.yml up -d

# Allocate resources
# - 0.25 A100 GPU for Causality Service
# - 0.25 A100 GPU for SLM Service
```

### 4. Kubernetes (Production)

```yaml
# Example deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: omnicore-gateway
spec:
  replicas: 3
  selector:
    matchLabels:
      app: omnicore-gateway
  template:
    spec:
      containers:
      - name: gateway
        image: omnicore/gateway:v10
        ports:
        - containerPort: 8000
```

---

## Troubleshooting

### Common Issues

#### 1. Import Error: Module Not Found

```bash
# Ensure PYTHONPATH is set
export PYTHONPATH=src
python -m orchestrator.cli start
```

#### 2. Ollama Connection Failed

```bash
# Check Ollama status
curl http://localhost:11434/api/tags

# Restart Ollama
systemctl restart ollama
# or
ollama serve
```

#### 3. Database Locked

```bash
# Check for stale processes
lsof ./data/*.db

# Kill if necessary
kill -9 <PID>
```

#### 4. Rate Limit Exceeded

```bash
# Check Redis
redis-cli ping

# Clear rate limits
redis-cli FLUSHDB
```

#### 5. GPU Not Detected

```bash
# Check CUDA
nvidia-smi

# Set device
export CUDA_VISIBLE_DEVICES=0
```

### Logs

```bash
# View service logs
tail -f logs/omnicore.log

# Docker logs
docker-compose logs -f gateway
```

### Health Checks

```bash
# All services
omnicore health

# Specific service
curl http://localhost:18001/health
```

---

## FAQ

### General

**Q: What makes OmniCore different from other ontology tools?**

A: OmniCore combines deterministic RDF parsing with AI-powered enhancement, providing both reliability and intelligence. The SLM integration enables automatic classification while maintaining human oversight.

**Q: What size ontologies can OmniCore handle?**

A: Default limit is 100,000 triples per import. For larger ontologies, increase `ontology_max_triples` in configuration.

**Q: Is OmniCore production-ready?**

A: v10 is designed for production use with proper deployment (Docker/Kubernetes). Development mode should not be used in production.

### Technical

**Q: Why SQLite instead of PostgreSQL?**

A: SQLite with WAL mode provides sufficient performance for most use cases while simplifying deployment. For high-concurrency scenarios, PostgreSQL can be configured.

**Q: Can I use my own LLM?**

A: Yes! Configure `SLM_PROVIDER=huggingface` with your model ID, or use `SLM_PROVIDER=local` with a transformers-compatible model.

**Q: How does conflict resolution work?**

A: When two ontologies disagree on entity classification, three AI agents (Platonist, Nominalist, Pragmatist) debate for 5 rounds. A moderator synthesizes the arguments and determines consensus.

### Integration

**Q: Can I integrate OmniCore with my existing system?**

A: Yes! All services expose REST APIs. Use the API Gateway (port 18000) for authenticated access.

**Q: Is there a Python SDK?**

A: The platform includes `HttpClient` for inter-service communication. External SDK is planned for future releases.

---

## Support & Resources

- **Documentation**: This guide + API docs at `/docs`
- **Issues**: GitHub Issues
- **Source**: [GitHub Repository](https://github.com/XushnazarovFaxriddin/OmniCore-Ontology-Platform)

---

## License

MIT License - See LICENSE file for details.

---

## Version History

| Version | Date       | Highlights |
|---------|------------|------------|
| v10.0.0 | 2025.12.19 | Initial v10 release with SLM integration |

---

*OmniCore Ontology Platform - Empowering Knowledge Through Intelligent Automation*
