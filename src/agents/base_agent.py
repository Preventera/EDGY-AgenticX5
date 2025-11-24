"""
Module de base pour tous les agents EDGY-AgenticX5.

Ce module définit la classe abstraite BaseAgent qui sert de fondation
pour tous les agents autonomes du système.
"""

import abc
import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

import anthropic
from pydantic import BaseModel, Field
from enum import Enum


class AgentStatus(str, Enum):
    """Status possibles d'un agent"""
    IDLE = "idle"
    INITIALIZING = "initializing"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"
    COMPLETED = "completed"


class AgentCapability(str, Enum):
    """Capacités des agents AgenticX5"""
    PERCEPTION = "perception"
    NORMALIZATION = "normalization"
    ANALYSIS = "analysis"
    RECOMMENDATION = "recommendation"
    ORCHESTRATION = "orchestration"
from utils.logger import get_logger
from utils.config import AgentConfig
from utils.security import SecurityGuard


class AgentMessage(BaseModel):
    """Modèle pour les messages inter-agents."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    sender_id: str
    receiver_id: Optional[str] = None
    message_type: str
    content: Dict[str, Any]
    priority: str = "normal"  # low, normal, high, critical
    requires_human_validation: bool = False


class AgentState(BaseModel):
    """État interne d'un agent."""
    
    status: str = "idle"  # idle, active, paused, error
    current_task: Optional[str] = None
    last_action: Optional[str] = None
    last_action_timestamp: Optional[datetime] = None
    error_count: int = 0
    success_count: int = 0
    context: Dict[str, Any] = Field(default_factory=dict)


class BaseAgent(abc.ABC):
    """
    Classe de base abstraite pour tous les agents EDGY-AgenticX5.
    
    Cette classe fournit les fonctionnalités de base communes à tous les agents :
    - Communication avec Claude API
    - Gestion de l'état interne
    - Logging et traçabilité
    - Sécurité et guardrails
    - Communication inter-agents
    """
    
    def __init__(
        self,
        agent_id: str,
        name: str,
        config: AgentConfig,
        anthropic_api_key: Optional[str] = None
    ):
        """
        Initialise l'agent de base.
        
        Args:
            agent_id: Identifiant unique de l'agent
            name: Nom descriptif de l'agent
            config: Configuration de l'agent
            anthropic_api_key: Clé API Anthropic (optionnelle si dans env)
        """
        self.agent_id = agent_id
        self.name = name
        self.config = config
        
        # Initialisation du client Anthropic
        self.client = anthropic.Anthropic(api_key=anthropic_api_key)
        
        # État interne
        self.state = AgentState()
        
        # Logger dédié
        self.logger = get_logger(f"agent.{self.name}")
        
        # Garde de sécurité
        self.security = SecurityGuard(agent_id=self.agent_id)
        
        # Mémoire contextuelle
        self.conversation_history: List[Dict[str, Any]] = []
        
        self.logger.info(
            f"Agent {self.name} ({self.agent_id}) initialisé avec succès"
        )
    
    @abc.abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Méthode abstraite pour le traitement principal de l'agent.
        
        Args:
            input_data: Données d'entrée à traiter
            
        Returns:
            Résultats du traitement
        """
        pass
    
    async def call_claude(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7
    ) -> str:
        """
        Appelle l'API Claude pour obtenir une réponse.
        
        Args:
            prompt: Prompt utilisateur
            system_prompt: Prompt système (optionnel)
            max_tokens: Nombre maximum de tokens
            temperature: Température de génération
            
        Returns:
            Réponse de Claude
        """
        try:
            # Construire les messages
            messages = self.conversation_history.copy()
            messages.append({
                "role": "user",
                "content": prompt
            })
            
            # Appel API
            response = await self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt or self._get_system_prompt(),
                messages=messages
            )
            
            # Extraire la réponse
            assistant_message = response.content[0].text
            
            # Mettre à jour l'historique
            self.conversation_history.append({
                "role": "user",
                "content": prompt
            })
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_message
            })
            
            # Limiter la taille de l'historique (garder les 10 derniers échanges)
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]
            
            self.logger.debug(
                f"Réponse Claude reçue ({len(assistant_message)} chars)"
            )
            
            return assistant_message
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'appel Claude: {e}")
            self.state.error_count += 1
            raise
    
    def _get_system_prompt(self) -> str:
        """
        Génère le prompt système de base pour l'agent.
        
        Returns:
            Prompt système
        """
        return f"""Tu es un agent intelligent spécialisé en Santé et Sécurité au Travail (SST).

Ton rôle: {self.config.role_description}

Directives de sécurité:
- TOUJOURS demander une validation humaine pour les décisions critiques
- NE JAMAIS agir sur des données sensibles sans autorisation explicite
- Respecter les règles RGPD et la confidentialité
- Documenter toutes tes actions pour traçabilité
- En cas de doute, escalader vers un superviseur humain

Contexte organisationnel EDGY:
- L'organisation est cartographiée selon le framework EDGY
- Les processus sont interconnectés (identité, expérience, opérations)
- Maintenir l'alignement entre promesse stratégique et réalité opérationnelle

Tu dois être:
- Précis et factuel
- Transparent sur tes limitations
- Proactif dans la détection de risques
- Collaboratif avec les autres agents et les humains
"""
    
    async def send_message(
        self,
        receiver_id: str,
        message_type: str,
        content: Dict[str, Any],
        priority: str = "normal",
        requires_validation: bool = False
    ) -> AgentMessage:
        """
        Envoie un message à un autre agent.
        
        Args:
            receiver_id: ID de l'agent destinataire
            message_type: Type de message
            content: Contenu du message
            priority: Priorité (low, normal, high, critical)
            requires_validation: Si validation humaine requise
            
        Returns:
            Message créé
        """
        message = AgentMessage(
            sender_id=self.agent_id,
            receiver_id=receiver_id,
            message_type=message_type,
            content=content,
            priority=priority,
            requires_human_validation=requires_validation
        )
        
        self.logger.info(
            f"Message envoyé: {message_type} vers {receiver_id} "
            f"(priorité: {priority})"
        )
        
        # TODO: Intégrer avec le message bus
        return message
    
    def update_state(
        self,
        status: Optional[str] = None,
        current_task: Optional[str] = None,
        context_update: Optional[Dict[str, Any]] = None
    ):
        """
        Met à jour l'état de l'agent.
        
        Args:
            status: Nouveau statut
            current_task: Tâche en cours
            context_update: Mise à jour du contexte
        """
        if status:
            self.state.status = status
        if current_task:
            self.state.current_task = current_task
        if context_update:
            self.state.context.update(context_update)
        
        self.logger.debug(f"État mis à jour: {self.state.status}")
    
    def validate_action(self, action: str, data: Dict[str, Any]) -> bool:
        """
        Valide une action avant exécution (guardrails).
        
        Args:
            action: Action à valider
            data: Données associées
            
        Returns:
            True si l'action est autorisée
        """
        return self.security.validate_action(
            agent_id=self.agent_id,
            action=action,
            data=data
        )
    
    async def request_human_validation(
        self,
        decision: str,
        context: Dict[str, Any],
        timeout_seconds: int = 300
    ) -> bool:
        """
        Demande une validation humaine pour une décision critique.
        
        Args:
            decision: Décision à valider
            context: Contexte de la décision
            timeout_seconds: Timeout en secondes
            
        Returns:
            True si approuvé, False sinon
        """
        self.logger.warning(
            f"Validation humaine requise pour: {decision}"
        )
        
        # TODO: Implémenter le système de validation
        # Pour l'instant, on simule une validation automatique en dev
        return True
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Retourne les métriques de l'agent.
        
        Returns:
            Dictionnaire de métriques
        """
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "status": self.state.status,
            "current_task": self.state.current_task,
            "success_count": self.state.success_count,
            "error_count": self.state.error_count,
            "uptime": "calculated_uptime",  # TODO: Calculer réellement
            "last_action": self.state.last_action,
            "last_action_timestamp": self.state.last_action_timestamp
        }
    
    def reset_context(self):
        """Réinitialise le contexte conversationnel."""
        self.conversation_history = []
        self.logger.info("Contexte conversationnel réinitialisé")
    
    async def shutdown(self):
        """Arrête proprement l'agent."""
        self.logger.info(f"Arrêt de l'agent {self.name}")
        self.update_state(status="shutdown")
        # Nettoyage des ressources si nécessaire
