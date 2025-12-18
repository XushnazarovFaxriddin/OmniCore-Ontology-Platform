"""
OmniCore Platform v10 - SLM Client
Unified interface for Ollama, HuggingFace, and local model inference
"""

import asyncio
import hashlib
import json
import time
from typing import Optional, Dict, Any, List
from datetime import datetime
import httpx
from functools import lru_cache
from abc import ABC, abstractmethod

from common.config import Settings, get_settings, SLMProvider
from common.logging_config import get_logger
from common.models import SLMRequest, SLMResponse

logger = get_logger("slm.client")


class BaseSLMClient(ABC):
    """Abstract base class for SLM clients"""

    @abstractmethod
    async def generate(self, request: SLMRequest) -> SLMResponse:
        """Generate response from SLM"""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if SLM service is available"""
        pass

    @abstractmethod
    async def list_models(self) -> List[str]:
        """List available models"""
        pass


class OllamaClient(BaseSLMClient):
    """
    Ollama SLM Client
    Supports Llama, Gemma, Mistral, and other models via Ollama
    """

    def __init__(self, settings: Settings):
        self.base_url = settings.slm_base_url
        self.model = settings.slm_model_name
        self.fallback_model = settings.slm_fallback_model
        self.max_tokens = settings.slm_max_tokens
        self.temperature = settings.slm_temperature
        self.timeout = settings.slm_timeout
        self.retry_attempts = settings.slm_retry_attempts
        self.enable_caching = settings.slm_enable_caching
        self.cache_ttl = settings.slm_cache_ttl
        self._cache: Dict[str, tuple] = {}  # (response, timestamp)

    def _get_cache_key(self, request: SLMRequest) -> str:
        """Generate cache key from request"""
        data = f"{request.prompt}:{request.model}:{request.temperature}"
        return hashlib.sha256(data.encode()).hexdigest()

    def _get_cached(self, key: str) -> Optional[SLMResponse]:
        """Get cached response if valid"""
        if not self.enable_caching or key not in self._cache:
            return None
        response, timestamp = self._cache[key]
        if time.time() - timestamp > self.cache_ttl:
            del self._cache[key]
            return None
        return response

    def _set_cache(self, key: str, response: SLMResponse):
        """Cache response"""
        if self.enable_caching:
            self._cache[key] = (response, time.time())

    async def generate(self, request: SLMRequest) -> SLMResponse:
        """Generate response using Ollama API"""
        cache_key = self._get_cache_key(request)
        cached = self._get_cached(cache_key)
        if cached:
            cached.cached = True
            return cached

        model = request.model or self.model
        start_time = time.time()

        for attempt in range(self.retry_attempts):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(
                        f"{self.base_url}/api/generate",
                        json={
                            "model": model,
                            "prompt": request.prompt,
                            "stream": False,
                            "options": {
                                "num_predict": request.max_tokens,
                                "temperature": request.temperature,
                            }
                        }
                    )

                    if response.status_code == 200:
                        data = response.json()
                        latency_ms = (time.time() - start_time) * 1000

                        # Extract confidence from response if available
                        confidence = self._extract_confidence(data.get("response", ""))

                        result = SLMResponse(
                            response=data.get("response", ""),
                            model_used=model,
                            confidence=confidence,
                            rationale=None,
                            tokens_used=data.get("eval_count", 0),
                            latency_ms=latency_ms,
                            cached=False
                        )

                        self._set_cache(cache_key, result)
                        return result

                    elif response.status_code == 404 and model != self.fallback_model:
                        logger.warning(f"Model {model} not found, trying fallback")
                        model = self.fallback_model
                        continue

                    else:
                        logger.error(f"Ollama API error: {response.status_code}")

            except httpx.TimeoutException:
                logger.warning(f"Ollama timeout, attempt {attempt + 1}/{self.retry_attempts}")
                await asyncio.sleep(1 * (attempt + 1))
            except Exception as e:
                logger.error(f"Ollama error: {e}")
                await asyncio.sleep(1 * (attempt + 1))

        # Return error response
        return SLMResponse(
            response="Error: Failed to generate response",
            model_used=model,
            confidence=0.0,
            rationale="Service unavailable",
            tokens_used=0,
            latency_ms=(time.time() - start_time) * 1000,
            cached=False
        )

    def _extract_confidence(self, response: str) -> float:
        """Extract confidence score from response if mentioned"""
        # Look for explicit confidence mentions
        import re
        patterns = [
            r"confidence[:\s]+(\d+\.?\d*)%?",
            r"(\d+\.?\d*)%?\s*confident",
            r"certainty[:\s]+(\d+\.?\d*)%?"
        ]
        for pattern in patterns:
            match = re.search(pattern, response.lower())
            if match:
                conf = float(match.group(1))
                return conf / 100 if conf > 1 else conf
        return 0.75  # Default confidence

    async def health_check(self) -> bool:
        """Check if Ollama is available"""
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                return response.status_code == 200
        except Exception:
            return False

    async def list_models(self) -> List[str]:
        """List available Ollama models"""
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                if response.status_code == 200:
                    data = response.json()
                    return [m["name"] for m in data.get("models", [])]
        except Exception as e:
            logger.error(f"Failed to list models: {e}")
        return []

    async def pull_model(self, model_name: str) -> bool:
        """Pull a model from Ollama registry"""
        try:
            async with httpx.AsyncClient(timeout=600) as client:
                response = await client.post(
                    f"{self.base_url}/api/pull",
                    json={"name": model_name},
                    timeout=600  # Models can take a while to download
                )
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Failed to pull model {model_name}: {e}")
            return False


class HuggingFaceClient(BaseSLMClient):
    """
    HuggingFace Inference API Client
    For cloud-based inference when Ollama is not available
    """

    def __init__(self, settings: Settings):
        self.api_key = settings.hf_token
        self.model_id = settings.hf_model_id
        self.base_url = "https://api-inference.huggingface.co/models"
        self.timeout = settings.slm_timeout
        self.max_tokens = settings.slm_max_tokens
        self.temperature = settings.slm_temperature

    async def generate(self, request: SLMRequest) -> SLMResponse:
        """Generate response using HuggingFace Inference API"""
        if not self.api_key:
            return SLMResponse(
                response="Error: HuggingFace API key not configured",
                model_used=self.model_id,
                confidence=0.0,
                tokens_used=0,
                latency_ms=0,
                cached=False
            )

        model = request.model or self.model_id
        start_time = time.time()

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/{model}",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json={
                        "inputs": request.prompt,
                        "parameters": {
                            "max_new_tokens": request.max_tokens,
                            "temperature": request.temperature,
                            "return_full_text": False
                        }
                    }
                )

                latency_ms = (time.time() - start_time) * 1000

                if response.status_code == 200:
                    data = response.json()
                    text = data[0].get("generated_text", "") if isinstance(data, list) else ""

                    return SLMResponse(
                        response=text,
                        model_used=model,
                        confidence=0.75,
                        tokens_used=len(text.split()),
                        latency_ms=latency_ms,
                        cached=False
                    )
                else:
                    logger.error(f"HuggingFace API error: {response.status_code}")

        except Exception as e:
            logger.error(f"HuggingFace error: {e}")

        return SLMResponse(
            response="Error: Failed to generate response",
            model_used=model,
            confidence=0.0,
            tokens_used=0,
            latency_ms=(time.time() - start_time) * 1000,
            cached=False
        )

    async def health_check(self) -> bool:
        """Check if HuggingFace API is available"""
        if not self.api_key:
            return False
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(
                    f"{self.base_url}/{self.model_id}",
                    headers={"Authorization": f"Bearer {self.api_key}"}
                )
                return response.status_code in [200, 503]  # 503 = model loading
        except Exception:
            return False

    async def list_models(self) -> List[str]:
        """Return configured model"""
        return [self.model_id]


class LocalTransformersClient(BaseSLMClient):
    """
    Local Transformers Client
    For direct model inference using transformers library
    """

    def __init__(self, settings: Settings):
        self.model_id = settings.hf_model_id
        self.device = "cuda" if settings.gpu_enabled else "cpu"
        self._model = None
        self._tokenizer = None

    async def _load_model(self):
        """Lazy load model"""
        if self._model is None:
            try:
                from transformers import AutoModelForCausalLM, AutoTokenizer
                import torch

                self._tokenizer = AutoTokenizer.from_pretrained(self.model_id)
                self._model = AutoModelForCausalLM.from_pretrained(
                    self.model_id,
                    torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                    device_map="auto" if self.device == "cuda" else None
                )
                if self.device == "cpu":
                    self._model = self._model.to(self.device)
                logger.info(f"Loaded model {self.model_id} on {self.device}")
            except Exception as e:
                logger.error(f"Failed to load model: {e}")
                raise

    async def generate(self, request: SLMRequest) -> SLMResponse:
        """Generate response using local transformers"""
        start_time = time.time()

        try:
            await self._load_model()

            inputs = self._tokenizer(request.prompt, return_tensors="pt")
            if self.device == "cuda":
                inputs = {k: v.cuda() for k, v in inputs.items()}

            import torch
            with torch.no_grad():
                outputs = self._model.generate(
                    **inputs,
                    max_new_tokens=request.max_tokens,
                    temperature=request.temperature,
                    do_sample=True,
                    pad_token_id=self._tokenizer.eos_token_id
                )

            response_text = self._tokenizer.decode(
                outputs[0][inputs["input_ids"].shape[1]:],
                skip_special_tokens=True
            )

            latency_ms = (time.time() - start_time) * 1000

            return SLMResponse(
                response=response_text,
                model_used=self.model_id,
                confidence=0.75,
                tokens_used=len(outputs[0]) - inputs["input_ids"].shape[1],
                latency_ms=latency_ms,
                cached=False
            )

        except Exception as e:
            logger.error(f"Local inference error: {e}")
            return SLMResponse(
                response=f"Error: {str(e)}",
                model_used=self.model_id,
                confidence=0.0,
                tokens_used=0,
                latency_ms=(time.time() - start_time) * 1000,
                cached=False
            )

    async def health_check(self) -> bool:
        """Check if local model can be loaded"""
        try:
            await self._load_model()
            return self._model is not None
        except Exception:
            return False

    async def list_models(self) -> List[str]:
        """Return configured model"""
        return [self.model_id]


class SLMClient:
    """
    Unified SLM Client with automatic fallback
    Tries providers in order: Ollama -> HuggingFace -> Local
    """

    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or get_settings()
        self._clients: Dict[SLMProvider, BaseSLMClient] = {}
        self._primary_provider = self.settings.slm_provider
        self._initialize_clients()

    def _initialize_clients(self):
        """Initialize available clients"""
        self._clients[SLMProvider.OLLAMA] = OllamaClient(self.settings)
        if self.settings.hf_token:
            self._clients[SLMProvider.HUGGINGFACE] = HuggingFaceClient(self.settings)
        # Local client is heavy, only initialize if explicitly requested
        if self._primary_provider == SLMProvider.LOCAL:
            self._clients[SLMProvider.LOCAL] = LocalTransformersClient(self.settings)

    async def generate(
        self,
        request: SLMRequest,
        fallback: bool = True
    ) -> SLMResponse:
        """
        Generate response with automatic fallback.
        v10 Safety: If confidence < threshold, marks for human review
        """
        providers = [self._primary_provider]
        if fallback:
            # Add fallback providers
            if self._primary_provider != SLMProvider.OLLAMA:
                providers.append(SLMProvider.OLLAMA)
            if SLMProvider.HUGGINGFACE in self._clients and self._primary_provider != SLMProvider.HUGGINGFACE:
                providers.append(SLMProvider.HUGGINGFACE)

        for provider in providers:
            if provider not in self._clients:
                continue

            client = self._clients[provider]
            response = await client.generate(request)

            if response.confidence > 0:  # Success
                # v10: Check confidence threshold
                if response.confidence < self.settings.slm_confidence_threshold:
                    response.rationale = f"Low confidence ({response.confidence:.2f}), flagged for review"
                    logger.warning(f"Low confidence response: {response.confidence}")

                return response

            logger.warning(f"Provider {provider} failed, trying next")

        # All providers failed
        return SLMResponse(
            response="Error: All SLM providers failed",
            model_used="none",
            confidence=0.0,
            rationale="All providers unavailable",
            tokens_used=0,
            latency_ms=0,
            cached=False
        )

    async def health_check(self) -> Dict[str, bool]:
        """Check health of all providers"""
        results = {}
        for provider, client in self._clients.items():
            results[provider.value] = await client.health_check()
        return results

    async def list_models(self) -> Dict[str, List[str]]:
        """List models from all providers"""
        results = {}
        for provider, client in self._clients.items():
            results[provider.value] = await client.list_models()
        return results

    def get_client(self, provider: SLMProvider) -> Optional[BaseSLMClient]:
        """Get specific provider client"""
        return self._clients.get(provider)


# Global client instance
_slm_client: Optional[SLMClient] = None


def get_slm_client() -> SLMClient:
    """Get or create global SLM client"""
    global _slm_client
    if _slm_client is None:
        _slm_client = SLMClient()
    return _slm_client
