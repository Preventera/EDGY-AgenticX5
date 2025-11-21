"""
Système de logging centralisé pour EDGY-AgenticX5.

Fournit un logging structuré avec support JSON, niveaux multiples,
et intégration avec les systèmes de monitoring.
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import structlog
from pythonjsonlogger import jsonlogger

from .config import get_settings


def setup_logging():
    """Configure le système de logging pour toute l'application."""
    settings = get_settings()
    
    # Configuration de base
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
    
    # Format pour logs JSON
    if settings.log_format == "json":
        log_handler = logging.StreamHandler(sys.stdout)
        formatter = jsonlogger.JsonFormatter(
            fmt='%(asctime)s %(name)s %(levelname)s %(message)s',
            datefmt='%Y-%m-%dT%H:%M:%S'
        )
        log_handler.setFormatter(formatter)
    else:
        # Format texte standard
        log_handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        log_handler.setFormatter(formatter)
    
    # Configuration du logger root
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.handlers = []
    root_logger.addHandler(log_handler)
    
    # Configuration structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer() if settings.log_format == "json" 
            else structlog.dev.ConsoleRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.BoundLogger:
    """
    Récupère un logger structuré pour un module.
    
    Args:
        name: Nom du module/agent
        
    Returns:
        Logger configuré
    """
    return structlog.get_logger(name)


class AuditLogger:
    """
    Logger spécialisé pour l'audit des actions critiques.
    
    Enregistre toutes les actions des agents avec traçabilité complète
    pour conformité et analyse.
    """
    
    def __init__(self):
        """Initialise l'audit logger."""
        settings = get_settings()
        self.audit_dir = settings.logs_dir / "audit"
        self.audit_dir.mkdir(parents=True, exist_ok=True)
        
        # Logger dédié pour l'audit
        self.logger = logging.getLogger("audit")
        self.logger.setLevel(logging.INFO)
        
        # Handler fichier pour persistance
        log_file = self.audit_dir / f"audit_{datetime.now():%Y%m%d}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(
            jsonlogger.JsonFormatter(
                fmt='%(asctime)s %(name)s %(levelname)s %(message)s'
            )
        )
        self.logger.addHandler(file_handler)
    
    def log_action(
        self,
        agent_id: str,
        action: str,
        details: Dict[str, Any],
        result: str = "success",
        user_id: Optional[str] = None
    ):
        """
        Enregistre une action dans l'audit trail.
        
        Args:
            agent_id: ID de l'agent ayant effectué l'action
            action: Type d'action
            details: Détails de l'action
            result: Résultat (success, failure, pending)
            user_id: ID utilisateur si validation humaine
        """
        self.logger.info(
            "audit_event",
            extra={
                "timestamp": datetime.utcnow().isoformat(),
                "agent_id": agent_id,
                "action": action,
                "details": details,
                "result": result,
                "user_id": user_id,
                "event_type": "agent_action"
            }
        )
    
    def log_validation(
        self,
        agent_id: str,
        decision: str,
        user_id: str,
        approved: bool,
        justification: Optional[str] = None
    ):
        """
        Enregistre une validation humaine.
        
        Args:
            agent_id: ID de l'agent
            decision: Décision demandée
            user_id: ID de l'utilisateur validant
            approved: Si approuvé ou non
            justification: Justification de la décision
        """
        self.logger.info(
            "human_validation",
            extra={
                "timestamp": datetime.utcnow().isoformat(),
                "agent_id": agent_id,
                "decision": decision,
                "user_id": user_id,
                "approved": approved,
                "justification": justification,
                "event_type": "human_validation"
            }
        )
    
    def log_alert(
        self,
        agent_id: str,
        alert_type: str,
        severity: str,
        details: Dict[str, Any]
    ):
        """
        Enregistre une alerte critique.
        
        Args:
            agent_id: ID de l'agent émetteur
            alert_type: Type d'alerte
            severity: Sévérité
            details: Détails de l'alerte
        """
        self.logger.warning(
            "critical_alert",
            extra={
                "timestamp": datetime.utcnow().isoformat(),
                "agent_id": agent_id,
                "alert_type": alert_type,
                "severity": severity,
                "details": details,
                "event_type": "critical_alert"
            }
        )
    
    def log_security_event(
        self,
        agent_id: str,
        event_type: str,
        details: Dict[str, Any],
        blocked: bool = False
    ):
        """
        Enregistre un événement de sécurité.
        
        Args:
            agent_id: ID de l'agent
            event_type: Type d'événement
            details: Détails
            blocked: Si l'action a été bloquée
        """
        self.logger.warning(
            "security_event",
            extra={
                "timestamp": datetime.utcnow().isoformat(),
                "agent_id": agent_id,
                "event_type": event_type,
                "details": details,
                "blocked": blocked,
                "event_category": "security"
            }
        )


class PerformanceLogger:
    """Logger pour les métriques de performance."""
    
    def __init__(self):
        """Initialise le performance logger."""
        self.logger = logging.getLogger("performance")
        self.logger.setLevel(logging.INFO)
    
    def log_execution_time(
        self,
        agent_id: str,
        operation: str,
        duration_ms: float,
        success: bool = True
    ):
        """
        Enregistre le temps d'exécution d'une opération.
        
        Args:
            agent_id: ID de l'agent
            operation: Opération effectuée
            duration_ms: Durée en millisecondes
            success: Si l'opération a réussi
        """
        self.logger.info(
            "execution_time",
            extra={
                "timestamp": datetime.utcnow().isoformat(),
                "agent_id": agent_id,
                "operation": operation,
                "duration_ms": duration_ms,
                "success": success,
                "metric_type": "performance"
            }
        )
    
    def log_resource_usage(
        self,
        agent_id: str,
        cpu_percent: float,
        memory_mb: float
    ):
        """
        Enregistre l'utilisation des ressources.
        
        Args:
            agent_id: ID de l'agent
            cpu_percent: Utilisation CPU en %
            memory_mb: Mémoire utilisée en MB
        """
        self.logger.info(
            "resource_usage",
            extra={
                "timestamp": datetime.utcnow().isoformat(),
                "agent_id": agent_id,
                "cpu_percent": cpu_percent,
                "memory_mb": memory_mb,
                "metric_type": "resources"
            }
        )


# Initialiser le logging au démarrage
setup_logging()

# Instances globales
audit_logger = AuditLogger()
performance_logger = PerformanceLogger()


def get_audit_logger() -> AuditLogger:
    """Retourne l'audit logger."""
    return audit_logger


def get_performance_logger() -> PerformanceLogger:
    """Retourne le performance logger."""
    return performance_logger
