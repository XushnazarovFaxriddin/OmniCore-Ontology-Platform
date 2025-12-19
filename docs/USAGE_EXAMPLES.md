# OmniCore Platform v10 - Usage Examples

Quick start guide with practical examples for using OmniCore's AI-powered ontology management features.

## Table of Contents
1. [Quick Start](#quick-start)
2. [AI Chat Examples](#ai-chat-examples)
3. [Root Type Classification](#root-type-classification)
4. [Causality Extraction](#causality-extraction)
5. [Epistemic Annotations](#epistemic-annotations)
6. [Model Management](#model-management)
7. [Dashboard Usage](#dashboard-usage)

---

## Quick Start

### 1. Start the Platform

```bash
# Option 1: Using Podman Compose (recommended for production)
cd /path/to/OmniCore-Ontology-Platform
podman-compose -f infra/podman-compose.yml up -d

# Option 2: Using Python directly (development)
python -m src.orchestrator.cli start --foreground
```

### 2. Initialize Sample Data

```bash
python scripts/init_sample_data.py
```

### 3. Access the Dashboard

Open your browser:
- **Local**: http://localhost:3000
- **Remote**: http://192.168.1.3:3000 (via VPN)

### 4. Check API Health

```bash
curl http://localhost:18000/health
```

---

## AI Chat Examples

### Basic Chat with OmniCore AI

```bash
curl -X POST http://localhost:18006/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "What are the four root types in OmniCore?"}
    ],
    "include_omnicore_context": true
  }'
```

**Response:**
```json
{
  "response": "OmniCore uses four root types for ontological classification:\n\n1. **EXTANT** - Physical, observable entities (e.g., mountains, atoms, organisms)\n2. **ABSTRACT** - Non-physical concepts (e.g., mathematics, justice, algorithms)\n3. **MENTAL** - Mind-dependent entities (e.g., emotions, dreams, beliefs)\n4. **FICTIVE** - Fictional entities (e.g., Sherlock Holmes, Hogwarts, unicorns)",
  "model_used": "llama3.2:1b",
  "confidence": 0.85
}
```

### Multi-turn Conversation

```bash
curl -X POST http://localhost:18006/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "What is causality in OmniCore?"},
      {"role": "assistant", "content": "Causality in OmniCore tracks cause-effect relationships between entities using five types."},
      {"role": "user", "content": "Can you explain the EMERGENT type?"}
    ]
  }'
```

---

## Root Type Classification

### Classify a Single Entity

```bash
curl -X POST http://localhost:18006/infer-root-type \
  -H "Content-Type: application/json" \
  -d '{
    "entity_name": "Quantum Entanglement",
    "description": "A quantum mechanical phenomenon where particles become correlated",
    "context": "Physics research",
    "source": "Scientific Journal"
  }'
```

**Response:**
```json
{
  "entity_name": "Quantum Entanglement",
  "root_type": "ABSTRACT",
  "confidence": 0.87,
  "reasoning": "Quantum entanglement is a theoretical physics concept describing particle correlations. While it has observable effects, the phenomenon itself is non-physical and mathematical in nature."
}
```

### Batch Classification

```bash
curl -X POST http://localhost:18006/batch-infer-root-types \
  -H "Content-Type: application/json" \
  -d '[
    {"entity_name": "Mount Fuji", "description": "Volcanic mountain in Japan"},
    {"entity_name": "Democracy", "description": "System of government by the people"},
    {"entity_name": "Fear", "description": "An emotional response to perceived danger"},
    {"entity_name": "Gandalf", "description": "Wizard from Lord of the Rings"}
  ]'
```

**Response:**
```json
[
  {"entity_name": "Mount Fuji", "root_type": "EXTANT", "confidence": 0.98},
  {"entity_name": "Democracy", "root_type": "ABSTRACT", "confidence": 0.92},
  {"entity_name": "Fear", "root_type": "MENTAL", "confidence": 0.95},
  {"entity_name": "Gandalf", "root_type": "FICTIVE", "confidence": 0.99}
]
```

---

## Causality Extraction

### Extract Causal Relationships

```bash
curl -X POST http://localhost:18006/extract-causality \
  -H "Content-Type: application/json" \
  -d '{
    "entities": ["Sun", "Photosynthesis", "Plant Growth"],
    "descriptions": [
      "The star at the center of our solar system",
      "Process by which plants convert light to energy",
      "The increase in size and complexity of plants"
    ],
    "context": "Biology and ecology"
  }'
```

**Response:**
```json
{
  "relationships": [
    {
      "source": "Sun",
      "target": "Photosynthesis",
      "causality_type": "EFFICIENT",
      "confidence": 0.95,
      "reasoning": "Sunlight directly causes photosynthesis to occur"
    },
    {
      "source": "Photosynthesis",
      "target": "Plant Growth",
      "causality_type": "EFFICIENT",
      "confidence": 0.92,
      "reasoning": "Photosynthesis produces energy that enables plant growth"
    },
    {
      "source": "Plant Growth",
      "target": "Photosynthesis",
      "causality_type": "FINAL",
      "confidence": 0.78,
      "reasoning": "Growth is a purpose/goal that photosynthesis serves"
    }
  ]
}
```

---

## Epistemic Annotations

### Annotate Knowledge Certainty

```bash
curl -X POST http://localhost:18006/annotate-epistemic \
  -H "Content-Type: application/json" \
  -d '{
    "entity_name": "Black Hole",
    "claim": "Black holes emit Hawking radiation",
    "source": "Stephen Hawking, 1974",
    "context": "Theoretical physics"
  }'
```

**Response:**
```json
{
  "certainty": 0.75,
  "basis": "empirical",
  "reasoning": "Hawking radiation is a theoretical prediction with strong mathematical support, but direct observation remains challenging due to the extremely weak nature of the radiation.",
  "supporting_evidence": [
    "Mathematical derivation from quantum field theory",
    "Consistent with thermodynamic principles"
  ],
  "source_reliability": 0.95
}
```

### Epistemic Basis Types

| Basis | Description | Example |
|-------|-------------|---------|
| `axiomatic` | Self-evident truths | Mathematical axioms |
| `empirical` | Based on observation | Scientific measurements |
| `consensus` | Expert agreement | Medical guidelines |
| `speculative` | Hypothetical | Unproven theories |

---

## Model Management

### Check Model Status

```bash
curl http://localhost:18006/models/status
```

**Response:**
```json
{
  "ollama_available": true,
  "models_available": ["llama3.2:1b", "gemma2:2b"],
  "primary_model": "llama3.2:1b",
  "fallback_model": "gemma2:2b",
  "ready": true,
  "message": "Ready with 2 model(s) available."
}
```

### Auto-Setup Models

```bash
# This downloads required models automatically
curl -X POST http://localhost:18006/models/setup
```

### Download a Specific Model

```bash
# Download Mistral 7B
curl -X POST http://localhost:18006/models/pull/mistral:7b
```

### List All Available Models

```bash
curl http://localhost:18006/models
```

---

## Dashboard Usage

### AI Chat Page (http://localhost:3000/ai/chat)

1. **Quick Prompts**: Click predefined prompts to ask common questions
2. **Context Toggle**: Enable/disable OmniCore project knowledge
3. **Message History**: View and continue conversations

### AI Assistant Page (http://localhost:3000/ai/assistant)

Tabs available:
- **Root Type**: Classify entities into EXTANT/ABSTRACT/MENTAL/FICTIVE
- **Causality**: Extract cause-effect relationships
- **Epistemic**: Annotate knowledge certainty
- **Conflict**: Resolve ontological conflicts via AI debate
- **Enhancement**: AI-enhance entity metadata
- **Quality**: Assess ontology quality for import

### AI Search Page (http://localhost:3000/ai/search)

1. **Semantic Search**: AI understands your intent
2. **Exact Match**: Find specific terms
3. **Filters**: Filter by root type (EXTANT, ABSTRACT, etc.)

### AI Models Page (http://localhost:3000/ai/models)

- View installed models and status
- Download new models
- Test models in playground
- Monitor usage statistics

---

## CRUD Operations via API Gateway

### Create a Root Entity

```bash
curl -X POST http://localhost:18000/api/roots \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Artificial Intelligence",
    "root_type": "ABSTRACT",
    "description": "The simulation of human intelligence by machines",
    "source": "Computer Science"
  }'
```

### List Root Entities

```bash
# List all
curl http://localhost:18000/api/roots

# Filter by type
curl "http://localhost:18000/api/roots?root_type=ABSTRACT"

# Paginate
curl "http://localhost:18000/api/roots?offset=0&limit=10"
```

### Create Causality Link

```bash
curl -X POST http://localhost:18000/api/causality-links \
  -H "Content-Type: application/json" \
  -d '{
    "source_entity_id": "uuid-of-source",
    "target_entity_id": "uuid-of-target",
    "causality_type": "EFFICIENT",
    "description": "Direct causal relationship",
    "confidence": 0.85
  }'
```

### Create Epistemic Annotation

```bash
curl -X POST http://localhost:18000/api/annotations \
  -H "Content-Type: application/json" \
  -d '{
    "entity_id": "uuid-of-entity",
    "basis": "empirical",
    "certainty": 0.9,
    "source": "Scientific study",
    "note": "Verified through experiments"
  }'
```

---

## Python Client Example

```python
import httpx
import asyncio

async def omnicore_example():
    base_url = "http://localhost:18006"

    async with httpx.AsyncClient() as client:
        # Chat with OmniCore AI
        response = await client.post(f"{base_url}/chat", json={
            "messages": [
                {"role": "user", "content": "Explain root types"}
            ]
        })
        print("Chat:", response.json()["response"])

        # Classify an entity
        response = await client.post(f"{base_url}/infer-root-type", json={
            "entity_name": "Love",
            "description": "A deep affection for someone"
        })
        result = response.json()
        print(f"Root Type: {result['root_type']} ({result['confidence']:.0%})")

asyncio.run(omnicore_example())
```

---

## Troubleshooting

### Ollama Not Available

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama
ollama serve

# Pull default model
ollama pull llama3.2:1b
```

### Check Service Health

```bash
# All services
curl http://localhost:18000/health

# SLM service specifically
curl http://localhost:18006/health

# Model status
curl http://localhost:18006/models/status
```

### View Logs

```bash
# Podman
podman-compose -f infra/podman-compose.yml logs -f slm-service

# Direct Python
tail -f logs/omnicore.log
```

---

## Quick Reference

| Service | Port | Endpoint |
|---------|------|----------|
| API Gateway | 18000 | http://localhost:18000 |
| Roots | 18001 | http://localhost:18001 |
| Causality | 18002 | http://localhost:18002 |
| Epistemic | 18003 | http://localhost:18003 |
| MMO | 18004 | http://localhost:18004 |
| Global | 18005 | http://localhost:18005 |
| SLM/AI | 18006 | http://localhost:18006 |
| Dashboard | 3000 | http://localhost:3000 |
| Ollama | 11434 | http://localhost:11434 |

**API Documentation**: http://localhost:18000/docs (Swagger UI)
