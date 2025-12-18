"""
OmniCore Platform v10 - Service Orchestrator
Manages service lifecycle for all deployment modes
"""

import asyncio
import subprocess
import sys
import os
import signal
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum
import json

from common.config import get_settings
from common.logging_config import get_logger

logger = get_logger("orchestrator")


class DeploymentMode(str, Enum):
    """Supported deployment modes"""
    VENV = "venv"           # Pure Python with virtual environment
    DOCKER = "docker"       # Docker Compose
    PODMAN = "podman"       # Podman Compose (PARAM BILIM)


class ServiceStatus(str, Enum):
    """Service status states"""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    ERROR = "error"


@dataclass
class ServiceConfig:
    """Service configuration"""
    name: str
    module: str              # Python module path
    port: int
    depends_on: List[str] = field(default_factory=list)
    gpu_required: bool = False
    gpu_fraction: float = 0.0
    health_endpoint: str = "/health"
    startup_timeout: int = 30


@dataclass
class ServiceInstance:
    """Running service instance"""
    config: ServiceConfig
    status: ServiceStatus = ServiceStatus.STOPPED
    process: Optional[subprocess.Popen] = None
    pid: Optional[int] = None
    error: Optional[str] = None


class ServiceManager:
    """
    Manages individual service processes.

    Supports:
    - Starting/stopping services
    - Health checking
    - Dependency management
    - Graceful shutdown
    """

    # v10 Service definitions
    SERVICES: Dict[str, ServiceConfig] = {
        "roots": ServiceConfig(
            name="Roots Service",
            module="core.roots.api:app",
            port=8001,
            depends_on=[],
            health_endpoint="/health"
        ),
        "causality": ServiceConfig(
            name="Causality Service",
            module="core.causality.api:app",
            port=8002,
            depends_on=["roots"],
            gpu_required=True,
            gpu_fraction=0.25,
            health_endpoint="/health"
        ),
        "epistemic": ServiceConfig(
            name="Epistemic Service",
            module="core.epistemic.api:app",
            port=8003,
            depends_on=["roots", "causality"],
            health_endpoint="/health"
        ),
        "mmo": ServiceConfig(
            name="MMO Service",
            module="core.mmo.api:app",
            port=8004,
            depends_on=[],
            health_endpoint="/health"
        ),
        "global": ServiceConfig(
            name="Global Ontology Service",
            module="core.global_srv.api:app",
            port=8005,
            depends_on=["roots", "causality", "epistemic", "mmo"],
            health_endpoint="/health"
        ),
        "slm": ServiceConfig(
            name="SLM Service",
            module="ai.slm.api:app",
            port=8006,
            depends_on=[],
            gpu_required=True,
            gpu_fraction=0.25,
            health_endpoint="/health"
        ),
        "gateway": ServiceConfig(
            name="API Gateway",
            module="core.gateway.api:app",
            port=8000,
            depends_on=["roots", "causality", "epistemic", "mmo", "global"],
            health_endpoint="/health"
        ),
    }

    def __init__(self, project_root: Optional[Path] = None):
        self.settings = get_settings()
        self.project_root = project_root or Path.cwd()
        self.instances: Dict[str, ServiceInstance] = {}
        self._shutdown_event = asyncio.Event()

    def _get_service_order(self) -> List[str]:
        """Get services in dependency order"""
        order = []
        visited = set()

        def visit(name: str):
            if name in visited:
                return
            visited.add(name)
            config = self.SERVICES.get(name)
            if config:
                for dep in config.depends_on:
                    visit(dep)
                order.append(name)

        for name in self.SERVICES:
            visit(name)

        return order

    async def start_service(self, name: str, wait_healthy: bool = True) -> bool:
        """Start a single service"""
        if name not in self.SERVICES:
            logger.error(f"Unknown service: {name}")
            return False

        config = self.SERVICES[name]

        # Check dependencies
        for dep in config.depends_on:
            if dep not in self.instances or self.instances[dep].status not in [ServiceStatus.RUNNING, ServiceStatus.HEALTHY]:
                logger.info(f"Starting dependency: {dep}")
                if not await self.start_service(dep, wait_healthy):
                    return False

        # Skip if already running
        if name in self.instances and self.instances[name].status in [ServiceStatus.RUNNING, ServiceStatus.HEALTHY]:
            logger.info(f"{name} already running")
            return True

        logger.info(f"Starting {config.name} on port {config.port}...")

        # Build environment
        env = os.environ.copy()
        env["OMNICORE_SERVICE"] = name
        env["OMNICORE_PORT"] = str(config.port)

        if config.gpu_required and self.settings.gpu_enabled:
            env["CUDA_VISIBLE_DEVICES"] = self.settings.gpu_device_ordinal

        # Start uvicorn process
        cmd = [
            sys.executable, "-m", "uvicorn",
            config.module,
            "--host", "0.0.0.0",
            "--port", str(config.port),
            "--log-level", "info"
        ]

        try:
            process = subprocess.Popen(
                cmd,
                cwd=str(self.project_root),
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            instance = ServiceInstance(
                config=config,
                status=ServiceStatus.STARTING,
                process=process,
                pid=process.pid
            )
            self.instances[name] = instance

            # Wait for healthy
            if wait_healthy:
                healthy = await self._wait_healthy(name, config.startup_timeout)
                instance.status = ServiceStatus.HEALTHY if healthy else ServiceStatus.ERROR
                if not healthy:
                    logger.error(f"{name} failed to become healthy")
                    return False

            instance.status = ServiceStatus.RUNNING
            logger.info(f"{config.name} started (PID: {process.pid})")
            return True

        except Exception as e:
            logger.error(f"Failed to start {name}: {e}")
            return False

    async def _wait_healthy(self, name: str, timeout: int) -> bool:
        """Wait for service to become healthy"""
        import httpx

        config = self.SERVICES[name]
        url = f"http://localhost:{config.port}{config.health_endpoint}"

        start = asyncio.get_event_loop().time()
        while asyncio.get_event_loop().time() - start < timeout:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(url, timeout=2)
                    if response.status_code == 200:
                        return True
            except Exception:
                pass
            await asyncio.sleep(1)

        return False

    async def stop_service(self, name: str) -> bool:
        """Stop a single service"""
        if name not in self.instances:
            return True

        instance = self.instances[name]
        if instance.process:
            logger.info(f"Stopping {name}...")
            instance.process.terminate()
            try:
                instance.process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                instance.process.kill()

        instance.status = ServiceStatus.STOPPED
        del self.instances[name]
        logger.info(f"{name} stopped")
        return True

    async def start_all(self) -> bool:
        """Start all services in dependency order"""
        order = self._get_service_order()
        logger.info(f"Starting services: {order}")

        for name in order:
            if not await self.start_service(name):
                logger.error(f"Failed to start {name}, stopping all")
                await self.stop_all()
                return False

        logger.info("All services started successfully")
        return True

    async def stop_all(self):
        """Stop all services in reverse order"""
        order = list(reversed(self._get_service_order()))
        logger.info(f"Stopping services: {order}")

        for name in order:
            await self.stop_service(name)

        logger.info("All services stopped")

    def get_status(self) -> Dict[str, Any]:
        """Get status of all services"""
        status = {}
        for name, config in self.SERVICES.items():
            instance = self.instances.get(name)
            status[name] = {
                "name": config.name,
                "port": config.port,
                "status": instance.status.value if instance else "stopped",
                "pid": instance.pid if instance else None,
                "gpu_required": config.gpu_required
            }
        return status


class OmniCoreOrchestrator:
    """
    Main orchestrator for OmniCore Platform v10.

    Supports deployment modes:
    - VENV: Pure Python with uvicorn
    - DOCKER: Docker Compose
    - PODMAN: Podman Compose (for PARAM BILIM)
    """

    def __init__(self, mode: DeploymentMode = DeploymentMode.VENV):
        self.mode = mode
        self.settings = get_settings()
        self.project_root = Path.cwd()
        self.service_manager = ServiceManager(self.project_root)
        self._running = False

    async def start(self) -> bool:
        """Start the platform"""
        logger.info(f"Starting OmniCore v10 in {self.mode.value} mode...")

        if self.mode == DeploymentMode.VENV:
            return await self._start_venv()
        elif self.mode == DeploymentMode.DOCKER:
            return self._start_docker()
        elif self.mode == DeploymentMode.PODMAN:
            return self._start_podman()

        return False

    async def stop(self):
        """Stop the platform"""
        logger.info("Stopping OmniCore v10...")
        self._running = False

        if self.mode == DeploymentMode.VENV:
            await self.service_manager.stop_all()
        elif self.mode == DeploymentMode.DOCKER:
            self._stop_docker()
        elif self.mode == DeploymentMode.PODMAN:
            self._stop_podman()

    async def _start_venv(self) -> bool:
        """Start in venv mode (pure Python)"""
        # Ensure directories exist
        self._ensure_directories()

        # Start all services
        success = await self.service_manager.start_all()
        if success:
            self._running = True
            logger.info("OmniCore v10 started successfully!")
            logger.info(f"API Gateway: http://localhost:{self.settings.api_gateway_port}")
            logger.info(f"Dashboard: http://localhost:{self.settings.dashboard_port}")

        return success

    def _start_docker(self) -> bool:
        """Start with Docker Compose"""
        compose_file = self.project_root / "docker-compose.yml"
        if not compose_file.exists():
            logger.error("docker-compose.yml not found")
            return False

        try:
            subprocess.run(
                ["docker-compose", "up", "-d"],
                cwd=str(self.project_root),
                check=True
            )
            self._running = True
            logger.info("OmniCore v10 started with Docker Compose")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Docker Compose failed: {e}")
            return False

    def _start_podman(self) -> bool:
        """Start with Podman Compose (PARAM BILIM)"""
        compose_file = self.project_root / "podman-compose.yml"
        if not compose_file.exists():
            compose_file = self.project_root / "docker-compose.yml"

        if not compose_file.exists():
            logger.error("podman-compose.yml or docker-compose.yml not found")
            return False

        try:
            subprocess.run(
                ["podman-compose", "-f", str(compose_file), "up", "-d"],
                cwd=str(self.project_root),
                check=True
            )
            self._running = True
            logger.info("OmniCore v10 started with Podman Compose")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Podman Compose failed: {e}")
            return False

    def _stop_docker(self):
        """Stop Docker Compose"""
        subprocess.run(
            ["docker-compose", "down"],
            cwd=str(self.project_root),
            check=False
        )

    def _stop_podman(self):
        """Stop Podman Compose"""
        compose_file = self.project_root / "podman-compose.yml"
        if not compose_file.exists():
            compose_file = self.project_root / "docker-compose.yml"

        subprocess.run(
            ["podman-compose", "-f", str(compose_file), "down"],
            cwd=str(self.project_root),
            check=False
        )

    def _ensure_directories(self):
        """Ensure required directories exist"""
        dirs = [
            self.project_root / "data",
            self.project_root / "data" / "ontologies",
            self.project_root / "data" / "snapshots",
            self.project_root / "logs",
        ]
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)

    def get_status(self) -> Dict[str, Any]:
        """Get platform status"""
        return {
            "mode": self.mode.value,
            "running": self._running,
            "services": self.service_manager.get_status(),
            "settings": {
                "gateway_port": self.settings.api_gateway_port,
                "dashboard_port": self.settings.dashboard_port,
                "slm_provider": self.settings.slm_provider.value,
                "slm_model": self.settings.slm_model_name,
                "gpu_enabled": self.settings.gpu_enabled
            }
        }

    async def health_check(self) -> Dict[str, bool]:
        """Check health of all services"""
        import httpx

        results = {}
        for name, config in ServiceManager.SERVICES.items():
            url = f"http://localhost:{config.port}{config.health_endpoint}"
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(url, timeout=5)
                    results[name] = response.status_code == 200
            except Exception:
                results[name] = False

        return results

    async def run_forever(self):
        """Run until interrupted"""
        # Set up signal handlers
        loop = asyncio.get_event_loop()

        def handle_signal(signum, frame):
            logger.info(f"Received signal {signum}")
            asyncio.create_task(self.stop())

        signal.signal(signal.SIGINT, handle_signal)
        signal.signal(signal.SIGTERM, handle_signal)

        # Start platform
        if not await self.start():
            return

        # Keep running
        while self._running:
            await asyncio.sleep(1)
