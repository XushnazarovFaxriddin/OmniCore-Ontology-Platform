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
import os
import shutil
import subprocess
from typing import Optional, List, Dict, Any, Callable
from dataclasses import dataclass
from enum import Enum
import time
from urllib.parse import urlparse

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
        self.base_url = (base_url or settings.slm_base_url).rstrip("/")
        self.timeout = 600  # 10 minutes for model downloads
        self._download_callbacks: Dict[str, List[Callable]] = {}

    def _candidate_base_urls(self) -> List[str]:
        """
        Generate candidate base URLs for contacting Ollama.

        Notes:
        - `0.0.0.0` is a bind address, not a valid client destination; map it to `127.0.0.1`.
        - `localhost` may resolve to IPv6 first on Windows; include an IPv4 fallback.
        """
        base_url = (self.base_url or "").strip().rstrip("/")
        if not base_url:
            return []

        # Ensure scheme so urlparse can extract hostname/port correctly.
        if "://" not in base_url:
            base_url = f"http://{base_url}"

        try:
            parsed = urlparse(base_url)
        except Exception:
            return [base_url]

        scheme = parsed.scheme or "http"
        hostname = parsed.hostname or ""
        port = parsed.port or (443 if scheme == "https" else 80)

        candidates: List[str] = []

        def add(host: str) -> None:
            url = f"{scheme}://{host}:{port}"
            if url not in candidates:
                candidates.append(url)

        if hostname in {"0.0.0.0", "::"}:
            add("127.0.0.1")
        else:
            add(hostname or "localhost")
            if hostname == "localhost":
                add("127.0.0.1")

        return candidates

    async def check_ollama_available(self, log: bool = True) -> bool:
        """Check if Ollama service is running (fast)."""
        last_error: Optional[Exception] = None
        for base_url in self._candidate_base_urls():
            try:
                async with httpx.AsyncClient(timeout=1.0) as client:
                    response = await client.get(f"{base_url}/api/tags")
                    if response.status_code == 200:
                        # Remember the working URL (e.g., swap localhost -> 127.0.0.1).
                        self.base_url = base_url.rstrip("/")
                        return True
            except Exception as e:
                last_error = e

        if log and last_error is not None:
            logger.warning(
                f"Ollama not available ({type(last_error).__name__}) at {self.base_url}: {last_error}"
            )
        return False

    def _is_local_base_url(self) -> bool:
        try:
            parsed = urlparse(self.base_url if "://" in self.base_url else f"http://{self.base_url}")
        except Exception:
            return False
        host = (parsed.hostname or "").lower()
        return host in {"localhost", "127.0.0.1", "0.0.0.0", "::1", "::"}

    def _start_local_ollama_daemon(self) -> bool:
        """
        Best-effort attempt to start Ollama locally (development only).

        This does NOT manage or stop the Ollama daemon; it just triggers startup.
        """
        if shutil.which("ollama") is None:
            return False

        try:
            creationflags = 0
            start_new_session = False

            if os.name == "nt":
                creationflags = (
                    getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
                    | getattr(subprocess, "DETACHED_PROCESS", 0)
                    | getattr(subprocess, "CREATE_NO_WINDOW", 0)
                )
            else:
                start_new_session = True

            subprocess.Popen(
                ["ollama", "serve"],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=creationflags,
                start_new_session=start_new_session,
            )
            return True
        except Exception as e:
            logger.warning(f"Failed to start local Ollama daemon: {e}")
            return False

    async def ensure_local_ollama_running(self, startup_timeout_s: float = 10.0) -> bool:
        """
        Ensure Ollama is reachable for local development.

        - Only attempts auto-start when `SLM_BASE_URL` points to localhost/loopback.
        - Intended for Windows/macOS dev where Ollama is installed but daemon isn't running yet.
        """
        settings = get_settings()
        if str(settings.omnicore_env).lower() != "development":
            return False

        if not self._is_local_base_url():
            return False

        if await self.check_ollama_available(log=False):
            return True

        logger.info("Ollama not reachable, attempting to start local Ollama (ollama serve)...")
        if not self._start_local_ollama_daemon():
            return False

        deadline = time.monotonic() + float(startup_timeout_s)
        while time.monotonic() < deadline:
            if await self.check_ollama_available(log=False):
                logger.info(f"Ollama is now available at {self.base_url}")
                return True
            await asyncio.sleep(0.5)

        logger.warning(f"Ollama still not reachable at {self.base_url} after {startup_timeout_s:.1f}s")
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
