"""
Module de sécurité et guardrails pour EDGY-AgenticX5.

Implémente les mécanismes de sécurité, validation, et protection
pour tous les agents autonomes.
"""

import hashlib
import re
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set

from cryptography.fernet import Fernet
from pydantic import BaseModel

from .logger import get_logger, get_audit_logger
from .config import get_settings


class SecurityViolation(Exception):
    """Exception levée lors d'une violation de sécurité."""
    pass


class ActionAttempt(BaseModel):
    """Modèle d'une tentative d'action."""
    
    agent_id: str
    action: str
    timestamp: datetime
    blocked: bool
    reason: Optional[str] = None


class SecurityGuard:
    """
    Garde de sécurité pour les agents.
    
    Implémente les guardrails, validations, et protections
    pour assurer la sécurité des opérations agentiques.
    """
    
    # Actions bloquées par défaut
    BLOCKED_ACTIONS = {
        "delete_production_data",
        "modify_critical_config",
        "execute_system_command",
        "access_credentials",
        "bypass_validation"
    }
    
    # Patterns de données sensibles à détecter
    SENSITIVE_PATTERNS = [
        r'\b\d{16}\b',  # Numéros de carte
        r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
        r'\b(?:\d{1,3}\.){3}\d{1,3}\b',  # IP addresses
    ]
    
    def __init__(self, agent_id: str):
        """
        Initialise le security guard.
        
        Args:
            agent_id: ID de l'agent à protéger
        """
        self.agent_id = agent_id
        self.logger = get_logger(f"security.{agent_id}")
        self.audit = get_audit_logger()
        self.settings = get_settings()
        
        # Historique des actions
        self.action_history: List[ActionAttempt] = []
        
        # Actions bloquées pour cet agent
        self.blocked_actions: Set[str] = self.BLOCKED_ACTIONS.copy()
        
        # Encryption key (en prod, devrait venir d'un vault sécurisé)
        self.encryption_key = Fernet.generate_key()
        self.cipher = Fernet(self.encryption_key)
        
        self.logger.info(f"Security guard initialisé pour {agent_id}")
    
    def validate_action(
        self,
        agent_id: str,
        action: str,
        data: Dict[str, Any]
    ) -> bool:
        """
        Valide qu'une action est autorisée.
        
        Args:
            agent_id: ID de l'agent demandeur
            action: Action à valider
            data: Données associées
            
        Returns:
            True si autorisé, False sinon
            
        Raises:
            SecurityViolation: Si violation détectée
        """
        # Vérifier que l'agent correspond
        if agent_id != self.agent_id:
            self._log_violation(
                action=action,
                reason="Agent ID mismatch",
                data=data
            )
            return False
        
        # Vérifier si l'action est bloquée
        if action in self.blocked_actions:
            self._log_violation(
                action=action,
                reason="Action explicitement bloquée",
                data=data
            )
            return False
        
        # Vérifier le rate limiting
        if not self._check_rate_limit(action):
            self._log_violation(
                action=action,
                reason="Rate limit dépassé",
                data=data
            )
            return False
        
        # Vérifier les données sensibles
        if self._contains_sensitive_data(data):
            self.logger.warning(
                f"Données sensibles détectées dans action {action}"
            )
            # Ne pas bloquer mais logger
        
        # Enregistrer la tentative réussie
        attempt = ActionAttempt(
            agent_id=agent_id,
            action=action,
            timestamp=datetime.utcnow(),
            blocked=False
        )
        self.action_history.append(attempt)
        
        self.audit.log_action(
            agent_id=agent_id,
            action=action,
            details={"validation": "passed"},
            result="approved"
        )
        
        return True
    
    def _check_rate_limit(self, action: str) -> bool:
        """
        Vérifie le rate limiting pour une action.
        
        Args:
            action: Action à vérifier
            
        Returns:
            True si dans les limites
        """
        # Compter les actions dans la dernière minute
        one_minute_ago = datetime.utcnow() - timedelta(minutes=1)
        recent_actions = [
            a for a in self.action_history
            if a.action == action and a.timestamp > one_minute_ago
        ]
        
        # Limite: 10 actions identiques par minute
        max_per_minute = 10
        
        if len(recent_actions) >= max_per_minute:
            self.logger.warning(
                f"Rate limit dépassé pour action {action}: "
                f"{len(recent_actions)}/{max_per_minute}"
            )
            return False
        
        return True
    
    def _contains_sensitive_data(self, data: Dict[str, Any]) -> bool:
        """
        Détecte si les données contiennent des informations sensibles.
        
        Args:
            data: Données à vérifier
            
        Returns:
            True si données sensibles détectées
        """
        # Convertir en string pour pattern matching
        data_str = str(data)
        
        for pattern in self.SENSITIVE_PATTERNS:
            if re.search(pattern, data_str):
                return True
        
        return False
    
    def _log_violation(
        self,
        action: str,
        reason: str,
        data: Dict[str, Any]
    ):
        """
        Enregistre une violation de sécurité.
        
        Args:
            action: Action tentée
            reason: Raison du blocage
            data: Données associées
        """
        attempt = ActionAttempt(
            agent_id=self.agent_id,
            action=action,
            timestamp=datetime.utcnow(),
            blocked=True,
            reason=reason
        )
        self.action_history.append(attempt)
        
        self.audit.log_security_event(
            agent_id=self.agent_id,
            event_type="action_blocked",
            details={
                "action": action,
                "reason": reason,
                "data_hash": self._hash_data(data)
            },
            blocked=True
        )
        
        self.logger.warning(
            f"Action {action} bloquée pour {self.agent_id}: {reason}"
        )
    
    def encrypt_data(self, data: str) -> bytes:
        """
        Chiffre des données sensibles.
        
        Args:
            data: Données à chiffrer
            
        Returns:
            Données chiffrées
        """
        return self.cipher.encrypt(data.encode())
    
    def decrypt_data(self, encrypted_data: bytes) -> str:
        """
        Déchiffre des données.
        
        Args:
            encrypted_data: Données chiffrées
            
        Returns:
            Données déchiffrées
        """
        return self.cipher.decrypt(encrypted_data).decode()
    
    def _hash_data(self, data: Any) -> str:
        """
        Génère un hash des données pour logging sécurisé.
        
        Args:
            data: Données à hasher
            
        Returns:
            Hash SHA256
        """
        data_str = str(data)
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    def add_blocked_action(self, action: str):
        """
        Ajoute une action à la liste des actions bloquées.
        
        Args:
            action: Action à bloquer
        """
        self.blocked_actions.add(action)
        self.logger.info(f"Action {action} ajoutée aux actions bloquées")
    
    def remove_blocked_action(self, action: str):
        """
        Retire une action de la liste des actions bloquées.
        
        Args:
            action: Action à débloquer
        """
        if action in self.blocked_actions:
            self.blocked_actions.remove(action)
            self.logger.info(f"Action {action} retirée des actions bloquées")
    
    def get_violation_report(self) -> Dict[str, Any]:
        """
        Génère un rapport des violations de sécurité.
        
        Returns:
            Rapport de violations
        """
        blocked_attempts = [
            a for a in self.action_history if a.blocked
        ]
        
        return {
            "agent_id": self.agent_id,
            "total_attempts": len(self.action_history),
            "blocked_attempts": len(blocked_attempts),
            "blocked_actions": list(self.blocked_actions),
            "recent_violations": [
                {
                    "action": a.action,
                    "timestamp": a.timestamp.isoformat(),
                    "reason": a.reason
                }
                for a in blocked_attempts[-10:]  # 10 dernières
            ]
        }


class InputSanitizer:
    """Sanitize et valide les inputs utilisateur."""
    
    @staticmethod
    def sanitize_text(text: str) -> str:
        """
        Nettoie un texte des caractères dangereux.
        
        Args:
            text: Texte à nettoyer
            
        Returns:
            Texte nettoyé
        """
        # Retirer les caractères de contrôle
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
        
        # Retirer les scripts potentiels
        text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL)
        
        return text.strip()
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Valide un format d'email.
        
        Args:
            email: Email à valider
            
        Returns:
            True si valide
        """
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_json(data: str) -> bool:
        """
        Valide qu'une chaîne est du JSON valide.
        
        Args:
            data: Chaîne à valider
            
        Returns:
            True si JSON valide
        """
        import json
        try:
            json.loads(data)
            return True
        except:
            return False


class PermissionManager:
    """Gestionnaire de permissions pour les agents."""
    
    def __init__(self):
        """Initialise le gestionnaire de permissions."""
        self.logger = get_logger("security.permissions")
        
        # Permissions par défaut pour chaque type d'agent
        self.default_permissions = {
            "monitoring": [
                "read_data",
                "detect_anomalies",
                "generate_alerts",
                "read_config"
            ],
            "decision": [
                "read_data",
                "analyze_risks",
                "generate_recommendations",
                "request_validation"
            ],
            "orchestrator": [
                "read_data",
                "coordinate_agents",
                "distribute_tasks",
                "consolidate_results",
                "manage_workflows"
            ]
        }
        
        # Permissions par agent
        self.agent_permissions: Dict[str, Set[str]] = {}
    
    def grant_permission(self, agent_id: str, permission: str):
        """
        Accorde une permission à un agent.
        
        Args:
            agent_id: ID de l'agent
            permission: Permission à accorder
        """
        if agent_id not in self.agent_permissions:
            self.agent_permissions[agent_id] = set()
        
        self.agent_permissions[agent_id].add(permission)
        self.logger.info(f"Permission {permission} accordée à {agent_id}")
    
    def revoke_permission(self, agent_id: str, permission: str):
        """
        Révoque une permission d'un agent.
        
        Args:
            agent_id: ID de l'agent
            permission: Permission à révoquer
        """
        if agent_id in self.agent_permissions:
            self.agent_permissions[agent_id].discard(permission)
            self.logger.info(f"Permission {permission} révoquée de {agent_id}")
    
    def has_permission(self, agent_id: str, permission: str) -> bool:
        """
        Vérifie si un agent a une permission.
        
        Args:
            agent_id: ID de l'agent
            permission: Permission à vérifier
            
        Returns:
            True si l'agent a la permission
        """
        if agent_id not in self.agent_permissions:
            return False
        
        return permission in self.agent_permissions[agent_id]
