"""
OmniCore Platform v10 - SLM (Small Language Model) Service
Supports Ollama, HuggingFace, and local model inference
"""

from .client import SLMClient, get_slm_client
from .service import SLMService
from .prompts import PromptTemplates

__all__ = ["SLMClient", "get_slm_client", "SLMService", "PromptTemplates"]
