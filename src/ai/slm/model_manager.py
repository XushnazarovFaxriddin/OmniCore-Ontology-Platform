"""
OmniCore Platform v10 - AI Model Manager
Handles automatic model downloading and management for Ollama

Features:
- Auto-detect and download required models
- Model health checking
- Fallback model management
- Progress tracking for downloads
"""

import asyncio
import httpx
from typing import Optional, List, Dict, Any, Callable
from dataclasses import dataclass
from enum import Enum
import time

from common.config import get_settings
from common.logging_config import get_logger

logger = get_logger("slm.model_manager")


class ModelStatus(str, Enum):
    """Model availability status"""
    AVAILABLE = "available"
    DOWNLOADING = "downloading"
    NOT_FOUND = "not_found"
    ERROR = "error"


@dataclass
class ModelInfo:
    """Information about a model"""
    name: str
    size: Optional[str] = None
    status: ModelStatus = ModelStatus.NOT_FOUND
    download_progress: float = 0.0
    modified_at: Optional[str] = None
    digest: Optional[str] = None


class OllamaModelManager:
    """
    Manages Ollama models with auto-download capability.

    Recommended models for OmniCore v10:
    - llama3.2:1b - Fast, efficient for simple tasks (1B params)
    - llama3.2:3b - Better quality, still fast (3B params)
    - gemma2:2b - Google's Gemma, good for reasoning
    - mistral:7b - High quality for complex tasks
    - phi3:mini - Microsoft's Phi-3, efficient
    """

    # Default models for OmniCore (in order of preference)
    RECOMMENDED_MODELS = [
        ("llama3.2:1b", "Primary model - fast and efficient"),
        ("gemma2:2b", "Fallback model - good reasoning"),
        ("phi3:mini", "Alternative - Microsoft Phi-3"),
    ]

    def __init__(self, base_url: Optional[str] = None):
        settings = get_settings()
        self.base_url = base_url or settings.slm_base_url
        self.timeout = 600  # 10 minutes for model downloads
        self._download_callbacks: Dict[str, List[Callable]] = {}

    async def check_ollama_available(self) -> bool:
        """Check if Ollama service is running"""
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                return response.status_code == 200
        except Exception as e:
            logger.warning(f"Ollama not available: {e}")
            return False

    async def list_local_models(self) -> List[ModelInfo]:
        """List all locally available models"""
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                if response.status_code == 200:
                    data = response.json()
                    return [
                        ModelInfo(
                            name=m["name"],
                            size=self._format_size(m.get("size", 0)),
                            status=ModelStatus.AVAILABLE,
                            modified_at=m.get("modified_at"),
                            digest=m.get("digest")
                        )
                        for m in data.get("models", [])
                    ]
        except Exception as e:
            logger.error(f"Failed to list models: {e}")
        return []

    async def is_model_available(self, model_name: str) -> bool:
        """Check if a specific model is available locally"""
        models = await self.list_local_models()
        return any(m.name == model_name or m.name.startswith(f"{model_name}:") for m in models)

    async def get_model_info(self, model_name: str) -> Optional[ModelInfo]:
        """Get detailed info about a model"""
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.post(
                    f"{self.base_url}/api/show",
                    json={"name": model_name}
                )
                if response.status_code == 200:
                    data = response.json()
                    return ModelInfo(
                        name=model_name,
                        size=self._format_size(data.get("size", 0)),
                        status=ModelStatus.AVAILABLE,
                        modified_at=data.get("modified_at")
                    )
        except Exception:
            pass
        return None

    async def pull_model(
        self,
        model_name: str,
        progress_callback: Optional[Callable[[str, float], None]] = None
    ) -> bool:
        """
        Pull/download a model from Ollama registry.

        Args:
            model_name: Name of model to pull (e.g., "llama3.2:1b")
            progress_callback: Optional callback(status, progress) for progress updates

        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Pulling model: {model_name}")

        if progress_callback:
            progress_callback(f"Starting download of {model_name}...", 0.0)

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Use streaming to track progress
                async with client.stream(
                    "POST",
                    f"{self.base_url}/api/pull",
                    json={"name": model_name},
                    timeout=self.timeout
                ) as response:
                    if response.status_code != 200:
                        logger.error(f"Failed to pull model: HTTP {response.status_code}")
                        return False

                    total_size = 0
                    downloaded = 0

                    async for line in response.aiter_lines():
                        if not line:
                            continue
                        try:
                            import json
                            data = json.loads(line)
                            status = data.get("status", "")

                            if "total" in data:
                                total_size = data["total"]
                            if "completed" in data:
                                downloaded = data["completed"]

                            if total_size > 0 and progress_callback:
                                progress = downloaded / total_size
                                progress_callback(status, progress)

                            if data.get("status") == "success":
                                logger.info(f"Successfully pulled {model_name}")
                                if progress_callback:
                                    progress_callback("Download complete!", 1.0)
                                return True

                        except Exception:
                            continue

                    return True

        except httpx.TimeoutException:
            logger.error(f"Timeout pulling model {model_name}")
            return False
        except Exception as e:
            logger.error(f"Error pulling model {model_name}: {e}")
            return False

    async def ensure_model_available(
        self,
        model_name: str,
        auto_download: bool = True,
        progress_callback: Optional[Callable[[str, float], None]] = None
    ) -> bool:
        """
        Ensure a model is available, downloading if necessary.

        Args:
            model_name: Model to ensure is available
            auto_download: Whether to automatically download if not found
            progress_callback: Optional progress callback

        Returns:
            True if model is available (or was downloaded)
        """
        # Check if already available
        if await self.is_model_available(model_name):
            logger.info(f"Model {model_name} is already available")
            return True

        if not auto_download:
            logger.warning(f"Model {model_name} not found and auto_download is disabled")
            return False

        # Download the model
        logger.info(f"Model {model_name} not found, downloading...")
        return await self.pull_model(model_name, progress_callback)

    async def ensure_recommended_models(
        self,
        progress_callback: Optional[Callable[[str, float], None]] = None
    ) -> Dict[str, bool]:
        """
        Ensure all recommended models are available.
        Downloads at least the primary and fallback models.

        Returns:
            Dict mapping model names to availability status
        """
        results = {}

        # Ensure at least primary model
        primary_model = self.RECOMMENDED_MODELS[0][0]
        results[primary_model] = await self.ensure_model_available(
            primary_model,
            auto_download=True,
            progress_callback=progress_callback
        )

        # Try to ensure fallback model
        if len(self.RECOMMENDED_MODELS) > 1:
            fallback_model = self.RECOMMENDED_MODELS[1][0]
            results[fallback_model] = await self.ensure_model_available(
                fallback_model,
                auto_download=True,
                progress_callback=progress_callback
            )

        return results

    async def auto_setup(
        self,
        progress_callback: Optional[Callable[[str, float], None]] = None
    ) -> Dict[str, Any]:
        """
        Automatic setup - check Ollama and download required models.

        Returns:
            Setup status report
        """
        report = {
            "ollama_available": False,
            "models_checked": [],
            "models_downloaded": [],
            "ready": False,
            "primary_model": None,
            "fallback_model": None,
        }

        # Check Ollama
        if progress_callback:
            progress_callback("Checking Ollama service...", 0.0)

        if not await self.check_ollama_available():
            report["error"] = "Ollama service not available. Please install and start Ollama first."
            return report

        report["ollama_available"] = True

        # Check/download models
        settings = get_settings()
        models_to_check = [
            settings.slm_model_name,
            settings.slm_fallback_model,
        ]

        for i, model_name in enumerate(models_to_check):
            if progress_callback:
                progress_callback(f"Checking model: {model_name}", (i / len(models_to_check)) * 0.5)

            report["models_checked"].append(model_name)

            was_available = await self.is_model_available(model_name)

            if not was_available:
                if progress_callback:
                    progress_callback(f"Downloading: {model_name}", 0.5 + (i / len(models_to_check)) * 0.5)

                success = await self.pull_model(model_name, progress_callback)
                if success:
                    report["models_downloaded"].append(model_name)

            # Set primary/fallback
            if await self.is_model_available(model_name):
                if i == 0:
                    report["primary_model"] = model_name
                elif i == 1 and report["fallback_model"] is None:
                    report["fallback_model"] = model_name

        report["ready"] = report["primary_model"] is not None

        if progress_callback:
            progress_callback("Setup complete!", 1.0)

        return report

    async def delete_model(self, model_name: str) -> bool:
        """Delete a model from local storage"""
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.delete(
                    f"{self.base_url}/api/delete",
                    json={"name": model_name}
                )
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Failed to delete model {model_name}: {e}")
            return False

    def _format_size(self, size_bytes: int) -> str:
        """Format size in human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"


# Global instance
_model_manager: Optional[OllamaModelManager] = None


def get_model_manager() -> OllamaModelManager:
    """Get or create global model manager"""
    global _model_manager
    if _model_manager is None:
        _model_manager = OllamaModelManager()
    return _model_manager


async def auto_setup_models() -> Dict[str, Any]:
    """
    Convenience function for automatic model setup.
    Call this on application startup.
    """
    manager = get_model_manager()
    return await manager.auto_setup()
