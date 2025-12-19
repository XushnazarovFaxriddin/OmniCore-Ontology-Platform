#!/bin/bash
# OmniCore Platform v10 - Setup Script
# Usage: ./scripts/setup.sh [--mode venv|docker|podman]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default mode
MODE="venv"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --mode|-m)
            MODE="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: $0 [--mode venv|docker|podman]"
            echo ""
            echo "Options:"
            echo "  --mode, -m    Deployment mode (default: venv)"
            echo "                venv   - Python virtual environment"
            echo "                docker - Docker Compose"
            echo "                podman - Podman Compose (PARAM BILIM)"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║       OmniCore Ontology Platform v10 - Setup               ║${NC}"
echo -e "${BLUE}║       AI-Orchestrated Ontological Computing System         ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}Deployment Mode: ${MODE}${NC}"
echo ""

# Get project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# Create directories
echo -e "${BLUE}Creating directories...${NC}"
mkdir -p data logs snapshots ontologies

# Setup based on mode
case $MODE in
    venv)
        echo -e "${BLUE}Setting up Python virtual environment...${NC}"

        # Check Python version
        PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
        REQUIRED_VERSION="3.11"

        if [[ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]]; then
            echo -e "${RED}Error: Python 3.11+ required (found $PYTHON_VERSION)${NC}"
            exit 1
        fi

        # Create virtual environment
        if [ ! -d "venv" ]; then
            echo -e "${YELLOW}Creating virtual environment...${NC}"
            python3 -m venv venv
        fi

        # Activate and install
        source venv/bin/activate
        pip install --upgrade pip
        pip install -r requirements.txt

        echo -e "${GREEN}✓ Virtual environment ready${NC}"
        echo ""
        echo -e "${YELLOW}To activate: source venv/bin/activate${NC}"
        echo -e "${YELLOW}To start:    python -m src.orchestrator.cli start${NC}"
        ;;

    docker)
        echo -e "${BLUE}Setting up Docker...${NC}"

        # Check Docker
        if ! command -v docker &> /dev/null; then
            echo -e "${RED}Error: Docker not found${NC}"
            exit 1
        fi

        if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
            echo -e "${RED}Error: Docker Compose not found${NC}"
            exit 1
        fi

        # Create .env file if not exists
        if [ ! -f ".env" ]; then
            echo -e "${YELLOW}Creating .env file...${NC}"
            cp infra/env/.env.example .env
            echo -e "${YELLOW}Please edit .env with your configuration${NC}"
        fi

        # Build image
        echo -e "${BLUE}Building Docker image...${NC}"
        docker build -t omnicore:v10 .

        echo -e "${GREEN}✓ Docker setup complete${NC}"
        echo ""
        echo -e "${YELLOW}To start: docker-compose -f infra/podman-compose.yml up -d${NC}"
        ;;

    podman)
        echo -e "${BLUE}Setting up Podman (PARAM BILIM)...${NC}"

        # Check Podman
        if ! command -v podman &> /dev/null; then
            echo -e "${RED}Error: Podman not found${NC}"
            exit 1
        fi

        if ! command -v podman-compose &> /dev/null; then
            echo -e "${RED}Error: podman-compose not found${NC}"
            echo -e "${YELLOW}Install with: pip install podman-compose${NC}"
            exit 1
        fi

        # Check GPU (optional)
        if command -v nvidia-smi &> /dev/null; then
            echo -e "${GREEN}✓ NVIDIA GPU detected${NC}"
            nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
        else
            echo -e "${YELLOW}⚠ No NVIDIA GPU detected (SLM will use CPU)${NC}"
        fi

        # Create .env file if not exists
        if [ ! -f ".env" ]; then
            echo -e "${YELLOW}Creating .env file...${NC}"
            cat > .env << EOF
# OmniCore v10 Environment Configuration
JWT_SECRET_KEY=$(openssl rand -base64 64 | tr -d '\n')
HF_TOKEN=
OMNICORE_DATA_PATH=./data
OMNICORE_LOGS_PATH=./logs
OMNICORE_SNAPSHOTS_PATH=./snapshots
OMNICORE_ONTOLOGIES_PATH=./ontologies
EOF
            echo -e "${YELLOW}Please edit .env with your HuggingFace token${NC}"
        fi

        # Build image
        echo -e "${BLUE}Building Podman image...${NC}"
        podman build -t localhost/omnicore:v10 .

        echo -e "${GREEN}✓ Podman setup complete${NC}"
        echo ""
        echo -e "${YELLOW}To start: podman-compose -f infra/podman-compose.yml up -d${NC}"
        ;;

    *)
        echo -e "${RED}Unknown mode: $MODE${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                    Setup Complete!                         ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "Services will be available at:"
echo -e "  ${BLUE}API Gateway:${NC}  http://localhost:18000"
echo -e "  ${BLUE}Dashboard:${NC}    http://localhost:3000"
echo -e "  ${BLUE}SLM Service:${NC}  http://localhost:18006"
echo -e "  ${BLUE}Ollama:${NC}       http://localhost:11434"
echo ""
echo -e "Next steps:"
echo -e "  1. Start Ollama and pull model: ollama pull llama3.2:1b"
echo -e "  2. Start the platform using the appropriate command above"
echo -e "  3. Check health: curl http://localhost:18000/health"
