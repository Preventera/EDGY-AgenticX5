"""
Module de configuration centralisée pour EDGY-AgenticX5.

Gère toutes les configurations du système via variables d'environnement
et fichiers de configuration.
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AgentConfig(BaseModel):
    """Configuration d'un agent."""
    
    role_description: str
    capabilities: List[str] = Field(default_factory=list)
    max_concurrent_tasks: int = 3
    timeout_seconds: int = 300
    retry_attempts: int = 3
    priority: str = "normal"  # low, normal, high, critical


class SecurityConfig(BaseModel):
    """Configuration de sécurité."""
    
    enable_human_validation: bool = True
    validation_timeout_seconds: int = 300
    require_encryption: bool = True
    audit_logging: bool = True
    max_action_attempts: int = 3
    blocked_actions: List[str] = Field(default_factory=list)


class MonitoringConfig(BaseModel):
    """Configuration du monitoring."""
    
    enable_metrics: bool = True
    metrics_interval_seconds: int = 60
    enable_alerting: bool = True
    alert_channels: List[str] = Field(default_factory=lambda: ["log", "email"])
    log_level: str = "INFO"


class EDGYConfig(BaseModel):
    """Configuration de la cartographie EDGY."""
    
    enable_visualization: bool = True
    auto_update_interval_seconds: int = 3600
    max_map_depth: int = 5
    include_metadata: bool = True


class DatabaseConfig(BaseModel):
    """Configuration base de données."""
    
    type: str = "postgresql"
    host: str = "localhost"
    port: int = 5432
    database: str = "edgy_agentic"
    username: str = "edgy_user"
    password: str = ""
    pool_size: int = 10


class Settings(BaseSettings):
    """
    Configuration principale de l'application.
    
    Les valeurs peuvent être surchargées par variables d'environnement.
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    # Application
    app_name: str = "EDGY-AgenticX5"
    app_version: str = "0.1.0"
    environment: str = Field(default="development", alias="EDGY_ENV")
    debug: bool = False
    
    # API Keys
    anthropic_api_key: str = Field(default="", alias="ANTHROPIC_API_KEY")
    
    # Chemins
    base_dir: Path = Field(default_factory=lambda: Path(__file__).parent.parent.parent)
    data_dir: Path = Field(default_factory=lambda: Path("data"))
    logs_dir: Path = Field(default_factory=lambda: Path("logs"))
    config_dir: Path = Field(default_factory=lambda: Path("configs"))
    
    # Logging
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_format: str = "json"  # json, text
    
    # Agents
    max_agents: int = 10
    agent_timeout_seconds: int = 300
    
    # Claude API
    claude_model: str = "claude-sonnet-4-20250514"
    claude_max_tokens: int = 4096
    claude_temperature: float = 0.7
    claude_timeout_seconds: int = 60
    
    # Security
    enable_security_guardrails: bool = True
    require_human_validation_critical: bool = True
    
    # Database
    database_url: Optional[str] = Field(default=None, alias="DATABASE_URL")
    
    # Redis (pour message bus)
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")
    
    # Monitoring
    enable_prometheus: bool = True
    prometheus_port: int = 9090
    
    # SHACL
    shacl_rules_dir: Path = Field(default_factory=lambda: Path("configs/shacl"))
    enable_shacl_validation: bool = True
    
    def get_agent_config(self, agent_type: str) -> AgentConfig:
        """
        Retourne la configuration pour un type d'agent spécifique.
        
        Args:
            agent_type: Type d'agent (monitoring, decision, orchestrator)
            
        Returns:
            Configuration de l'agent
        """
        configs = {
            "monitoring": AgentConfig(
                role_description="Surveillance continue des risques SST",
                capabilities=[
                    "continuous_monitoring",
                    "anomaly_detection",
                    "alert_generation"
                ],
                max_concurrent_tasks=5
            ),
            "decision": AgentConfig(
                role_description="Analyse et décision sur les risques critiques",
                capabilities=[
                    "risk_analysis",
                    "decision_making",
                    "recommendation_generation"
                ],
                max_concurrent_tasks=3,
                priority="high"
            ),
            "orchestrator": AgentConfig(
                role_description="Orchestration multi-agents",
                capabilities=[
                    "workflow_orchestration",
                    "task_distribution",
                    "result_consolidation"
                ],
                max_concurrent_tasks=10,
                priority="high"
            )
        }
        
        return configs.get(
            agent_type,
            AgentConfig(role_description="Agent générique")
        )
    
    def get_security_config(self) -> SecurityConfig:
        """Retourne la configuration de sécurité."""
        return SecurityConfig(
            enable_human_validation=self.require_human_validation_critical,
            require_encryption=True,
            audit_logging=True
        )
    
    def get_monitoring_config(self) -> MonitoringConfig:
        """Retourne la configuration de monitoring."""
        return MonitoringConfig(
            enable_metrics=self.enable_prometheus,
            log_level=self.log_level
        )
    
    def get_edgy_config(self) -> EDGYConfig:
        """Retourne la configuration EDGY."""
        return EDGYConfig(
            enable_visualization=True,
            max_map_depth=5
        )
    
    def ensure_directories(self):
        """Crée les répertoires nécessaires s'ils n'existent pas."""
        directories = [
            self.data_dir,
            self.logs_dir,
            self.logs_dir / "agents",
            self.logs_dir / "security",
            self.logs_dir / "audit",
            self.config_dir,
            self.shacl_rules_dir
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)


# Instance globale des settings
settings = Settings()

# Créer les répertoires au démarrage
settings.ensure_directories()


def get_settings() -> Settings:
    """
    Retourne l'instance des settings.
    
    Returns:
        Instance Settings
    """
    return settings


def reload_settings():
    """Recharge les settings depuis les fichiers."""
    global settings
    settings = Settings()
    settings.ensure_directories()
