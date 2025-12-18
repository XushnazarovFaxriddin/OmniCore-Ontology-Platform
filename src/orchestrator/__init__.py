"""
OmniCore Platform v10 - Orchestrator Module
Unified deployment for Podman, Docker, and Python venv
"""

from .runner import OmniCoreOrchestrator, ServiceManager
from .cli import main as cli_main

__all__ = ["OmniCoreOrchestrator", "ServiceManager", "cli_main"]
