"""
OmniCore Platform v10 - Configuration Management
Comprehensive settings for all services including SLM integration
AI-Orchestrated Ontological Computing System
"""
from typing import Optional, List, Dict, Any
from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache
from enum import Enum


class DeploymentMode(str, Enum):
    """Deployment environment modes"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    PARAM_BILIM = "param_bilim"


class SLMProvider(str, Enum):
    """Supported SLM providers"""
    OLLAMA = "ollama"
    HUGGINGFACE = "huggingface"
    VLLM = "vllm"
    LOCAL = "local"


class Settings(BaseSettings):
    """
    OmniCore v10 Configuration
    Supports PARAM BILIM supercomputer deployment
    """
    # Application Settings
    app_name: str = "OmniCore Ontology Platform"
    app_version: str = "10.0.0"
    deployment_mode: DeploymentMode = DeploymentMode.DEVELOPMENT
    debug: bool = False

    # Service Ports (v10 Architecture)
    api_gateway_port: int = 18000
    roots_service_port: int = 18001
    causality_service_port: int = 18002
    epistemic_service_port: int = 18003
    mmo_service_port: int = 18004
    global_service_port: int = 18005
    slm_service_port: int = 18006
    ai_orchestrator_port: int = 18007
    dashboard_port: int = 3000

    # Service URLs
    roots_service_url: str = Field(
        default="http://localhost:18001", alias="ROOTS_SERVICE_URL"
    )
    causality_service_url: str = Field(
        default="http://localhost:18002", alias="CAUSALITY_SERVICE_URL"
    )
    epistemic_service_url: str = Field(
        default="http://localhost:18003", alias="EPISTEMIC_SERVICE_URL"
    )
    mmo_service_url: str = Field(
        default="http://localhost:18004", alias="MMO_SERVICE_URL"
    )
    global_service_url: str = Field(
        default="http://localhost:18005", alias="GLOBAL_SERVICE_URL"
    )
    slm_service_url: str = Field(
        default="http://localhost:18006", alias="SLM_SERVICE_URL"
    )

    # Database Configuration
    database_path: str = Field(
        default="./data/omnicore.db", alias="DATABASE_PATH"
    )
    database_pool_size: int = 10
    database_wal_mode: bool = True

    # Redis Configuration (Rate Limiting)
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")
    redis_password: Optional[str] = None
    rate_limit_requests: int = Field(default=100, alias="RATE_LIMIT_REQUESTS")
    rate_limit_window: int = Field(default=60, alias="RATE_LIMIT_WINDOW")

    # Authentication (JWT + Keycloak OIDC)
    jwt_secret_key: str = Field(
        default="omnicore-v10-secret-key-change-in-production",
        alias="JWT_SECRET_KEY"
    )
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    jwt_expiration_hours: int = Field(default=24, alias="JWT_EXPIRATION_HOURS")
    api_key_header: str = Field(default="X-API-Key", alias="API_KEY_HEADER")
    valid_api_keys: str = Field(default="", alias="VALID_API_KEYS")
    keycloak_url: Optional[str] = None
    keycloak_realm: Optional[str] = None
    keycloak_client_id: Optional[str] = None

    # SLM Configuration (v10 - Critical)
    slm_provider: SLMProvider = SLMProvider.OLLAMA
    slm_model_name: str = Field(
        default="llama3.2:1b", alias="SLM_MODEL_NAME"
    )  # Llama-3.2-1B
    slm_fallback_model: str = Field(
        default="gemma2:2b", alias="SLM_FALLBACK_MODEL"
    )  # Gemma-2-2B
    slm_base_url: str = Field(
        default="http://localhost:11434", alias="SLM_BASE_URL"
    )  # Ollama
    slm_api_key: Optional[str] = Field(default=None, alias="SLM_API_KEY")
    slm_max_tokens: int = 2048
    slm_temperature: float = 0.1  # Low for deterministic outputs
    slm_timeout: int = 60
    slm_confidence_threshold: float = 0.6  # Below this = fallback to rules
    slm_enable_caching: bool = True
    slm_cache_ttl: int = 3600
    slm_retry_attempts: int = 3

    # HuggingFace Configuration (Alternative to Ollama)
    hf_token: Optional[str] = Field(default=None, alias="HUGGINGFACE_TOKEN")
    hf_model_id: str = Field(
        default="meta-llama/Llama-3.2-1B-Instruct", alias="HF_MODEL_ID"
    )

    # GPU Configuration (PARAM BILIM)
    gpu_enabled: bool = Field(default=False, alias="GPU_ENABLED")
    gpu_device_ordinal: str = Field(default="0", alias="GPU_DEVICE_ORDINAL")
    gpu_memory_fraction: float = 0.25  # 0.25 A100 per group
    cuda_visible_devices: Optional[str] = Field(
        default=None, alias="CUDA_VISIBLE_DEVICES"
    )

    # RDF/Ontology Configuration
    rdf_default_format: str = "turtle"
    rdf_supported_formats: List[str] = ["xml", "turtle", "n3", "nt", "json-ld"]
    ontology_import_timeout: int = 70  # seconds (v10 spec)
    ontology_max_triples: int = 100000
    ontology_storage_path: str = "./data/ontologies"

    # MO/MMO Configuration
    mo_version_prefix: str = "mo:v"
    mo_snapshot_path: str = "./data/snapshots"
    mo_auto_snapshot: bool = True
    mo_snapshot_interval: int = 3600  # hourly
    mmo_completeness_threshold: float = 0.85
    mmo_coverage_threshold: float = 0.70
    mmo_coherence_threshold: float = 0.95
    mmo_utility_threshold: float = 0.80
    mmo_inclusivity_threshold: float = 0.65

    # AI Harvesting Configuration
    harvesting_enabled: bool = True
    harvesting_max_batch: int = 20
    harvesting_quality_threshold: float = 0.7
    harvesting_interval_hours: int = 24

    # Conflict Resolution
    conflict_debate_rounds: int = 5
    conflict_max_tokens_per_turn: int = 500
    conflict_consensus_threshold: float = 0.75  # 3/4 agents

    # Safety & Ethics (v10 - Critical)
    human_oversight_enabled: bool = True
    ethical_alert_threshold: float = 0.8
    max_human_intervention_quarterly: int = 20
    rollback_enabled: bool = True
    audit_trail_enabled: bool = True
    bias_audit_enabled: bool = True

    # Logging
    log_level: str = Field(default="INFO", alias="OMNICORE_LOG_LEVEL")
    log_format: str = "json"
    log_file: Optional[str] = "./logs/omnicore.log"

    # CORS
    cors_origins: str = Field(default="*", alias="CORS_ORIGINS")

    # PARAM BILIM Specific
    scratch_path: str = "/scratch/omnicore"
    home_storage_limit_gb: int = 10
    scratch_storage_limit_tb: int = 1
    infiniband_enabled: bool = False

    # Service identification
    omnicore_env: str = Field(default="development", alias="OMNICORE_ENV")
    omnicore_service: str = Field(default="unknown", alias="OMNICORE_SERVICE")
    omnicore_port: int = Field(default=18000, alias="OMNICORE_PORT")

    class Config:
        env_prefix = "OMNICORE_"
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"

    @property
    def omnicore_log_level(self) -> str:
        """Backward compatibility alias for logging level."""
        return self.log_level

    def get_cors_origins(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        if self.cors_origins == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_origins.split(",")]

    def get_valid_api_keys(self) -> List[str]:
        """Parse valid API keys from comma-separated string."""
        if not self.valid_api_keys:
            return []
        return [key.strip() for key in self.valid_api_keys.split(",") if key.strip()]


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Global settings instance
settings = Settings()


def get_service_url(service_name: str) -> str:
    """Get URL for a specific service"""
    s = get_settings()
    url_map = {
        "roots": s.roots_service_url,
        "causality": s.causality_service_url,
        "epistemic": s.epistemic_service_url,
        "mmo": s.mmo_service_url,
        "global": s.global_service_url,
        "slm": s.slm_service_url,
        "gateway": f"http://localhost:{s.api_gateway_port}",
    }
    return url_map.get(service_name, "")
