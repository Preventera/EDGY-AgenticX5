"""
Agent d'Orchestration pour la coordination multi-agent.

Cet agent orchestre les interactions entre les différents agents autonomes,
répartit les tâches, et consolide les résultats.
"""

import asyncio
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Set

from pydantic import BaseModel, Field

from .base_agent import BaseAgent, AgentMessage
from ..utils.config import AgentConfig
from ..utils.logger import get_logger


class Task(BaseModel):
    """Modèle de tâche dans le workflow."""
    
    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    agent_id: str
    dependencies: List[str] = Field(default_factory=list)
    status: str = "pending"  # pending, running, completed, failed
    input_data: Dict[str, Any] = Field(default_factory=dict)
    output_data: Optional[Dict[str, Any]] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None


class Workflow(BaseModel):
    """Modèle de workflow agentique."""
    
    workflow_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    tasks: List[Task]
    status: str = "pending"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    human_validation_points: List[str] = Field(default_factory=list)


class OrchestratorAgent(BaseAgent):
    """
    Agent d'orchestration multi-agents.
    
    Responsabilités:
    - Ordonnancer les agents en pipeline
    - Répartir les tâches selon les dépendances
    - Consolider les résultats multi-agents
    - Maintenir la cohérence du contexte global
    - Gérer les conflits entre agents
    - Superviser l'exécution des workflows
    """
    
    def __init__(
        self,
        agent_id: str = "orchestrator_agent_01",
        name: str = "SST Orchestrator",
        config: Optional[AgentConfig] = None,
        anthropic_api_key: Optional[str] = None
    ):
        """
        Initialise l'orchestrateur.
        
        Args:
            agent_id: Identifiant unique
            name: Nom de l'agent
            config: Configuration
            anthropic_api_key: Clé API Anthropic
        """
        if config is None:
            config = AgentConfig(
                role_description=(
                    "Agent d'orchestration multi-agents. Coordonne les agents, "
                    "répartit les tâches, consolide les résultats et maintient "
                    "la cohérence du contexte global."
                ),
                capabilities=[
                    "workflow_orchestration",
                    "task_distribution",
                    "result_consolidation",
                    "conflict_resolution",
                    "context_management"
                ],
                max_concurrent_tasks=10
            )
        
        super().__init__(
            agent_id=agent_id,
            name=name,
            config=config,
            anthropic_api_key=anthropic_api_key
        )
        
        # Registre des agents disponibles
        self.registered_agents: Dict[str, BaseAgent] = {}
        
        # Workflows actifs
        self.active_workflows: Dict[str, Workflow] = {}
        
        # Contexte global partagé
        self.global_context: Dict[str, Any] = {}
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Traite une demande d'orchestration.
        
        Args:
            input_data: Données d'entrée avec instructions d'orchestration
            
        Returns:
            Résultats consolidés
        """
        self.update_state(
            status="active",
            current_task="orchestrating_workflow"
        )
        
        try:
            # Analyser la demande et créer le workflow
            workflow = await self._create_workflow(input_data)
            
            # Exécuter le workflow
            results = await self._execute_workflow(workflow)
            
            # Consolider les résultats
            consolidated = await self._consolidate_results(results)
            
            self.state.success_count += 1
            self.update_state(status="idle", current_task=None)
            
            return {
                "status": "success",
                "workflow_id": workflow.workflow_id,
                "results": consolidated,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Erreur orchestration: {e}")
            self.state.error_count += 1
            self.update_state(status="error")
            raise
    
    async def _create_workflow(
        self,
        input_data: Dict[str, Any]
    ) -> Workflow:
        """
        Crée un workflow basé sur les données d'entrée.
        
        Args:
            input_data: Spécifications du workflow
            
        Returns:
            Workflow créé
        """
        # Utiliser Claude pour analyser et structurer le workflow
        prompt = f"""Analyse cette demande SST et crée un plan d'action multi-agent:

Demande:
{input_data.get('description', '')}

Contexte:
{input_data.get('context', {})}

Agents disponibles:
{list(self.registered_agents.keys())}

Crée un workflow structuré avec cette format JSON exact:
{{
    "name": "nom du workflow",
    "description": "description",
    "tasks": [
        {{
            "name": "nom de la tâche",
            "agent_id": "id de l'agent à utiliser",
            "dependencies": ["liste des task_ids prérequis"],
            "input_data": {{"données pour l'agent"}}
        }}
    ],
    "human_validation_points": ["noms des tâches nécessitant validation humaine"]
}}

IMPORTANT: Réponds UNIQUEMENT avec du JSON valide."""

        response = await self.call_claude(
            prompt=prompt,
            max_tokens=2000,
            temperature=0.6
        )
        
        # Parser et créer le workflow
        try:
            import json
            clean_response = response.strip()
            if clean_response.startswith("```json"):
                clean_response = clean_response[7:]
            if clean_response.endswith("```"):
                clean_response = clean_response[:-3]
            workflow_data = json.loads(clean_response.strip())
            
            # Créer les tâches
            tasks = []
            for task_data in workflow_data.get("tasks", []):
                task = Task(
                    name=task_data["name"],
                    agent_id=task_data["agent_id"],
                    dependencies=task_data.get("dependencies", []),
                    input_data=task_data.get("input_data", {})
                )
                tasks.append(task)
            
            workflow = Workflow(
                name=workflow_data["name"],
                description=workflow_data["description"],
                tasks=tasks,
                human_validation_points=workflow_data.get("human_validation_points", [])
            )
            
            self.active_workflows[workflow.workflow_id] = workflow
            self.logger.info(
                f"Workflow créé: {workflow.name} avec {len(tasks)} tâches"
            )
            
            return workflow
            
        except Exception as e:
            self.logger.error(f"Erreur création workflow: {e}")
            # Workflow par défaut en cas d'erreur
            return Workflow(
                name="Default Workflow",
                description="Workflow généré automatiquement",
                tasks=[]
            )
    
    async def _execute_workflow(
        self,
        workflow: Workflow
    ) -> Dict[str, Any]:
        """
        Exécute un workflow en respectant les dépendances.
        
        Args:
            workflow: Workflow à exécuter
            
        Returns:
            Résultats de toutes les tâches
        """
        workflow.status = "running"
        workflow.started_at = datetime.utcnow()
        
        results = {}
        completed_tasks: Set[str] = set()
        
        while len(completed_tasks) < len(workflow.tasks):
            # Trouver les tâches prêtes à être exécutées
            ready_tasks = [
                task for task in workflow.tasks
                if task.status == "pending" and
                all(dep in completed_tasks for dep in task.dependencies)
            ]
            
            if not ready_tasks:
                if len(completed_tasks) < len(workflow.tasks):
                    self.logger.error("Deadlock détecté dans le workflow")
                    break
                break
            
            # Exécuter les tâches prêtes en parallèle
            tasks_futures = [
                self._execute_task(task, workflow, results)
                for task in ready_tasks
            ]
            
            task_results = await asyncio.gather(*tasks_futures, return_exceptions=True)
            
            # Traiter les résultats
            for task, result in zip(ready_tasks, task_results):
                if isinstance(result, Exception):
                    task.status = "failed"
                    task.error = str(result)
                    self.logger.error(f"Tâche {task.name} échouée: {result}")
                else:
                    task.status = "completed"
                    task.completed_at = datetime.utcnow()
                    task.output_data = result
                    results[task.task_id] = result
                    completed_tasks.add(task.task_id)
                    self.logger.info(f"Tâche {task.name} complétée")
        
        workflow.status = "completed"
        workflow.completed_at = datetime.utcnow()
        
        return results
    
    async def _execute_task(
        self,
        task: Task,
        workflow: Workflow,
        previous_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Exécute une tâche individuelle.
        
        Args:
            task: Tâche à exécuter
            workflow: Workflow parent
            previous_results: Résultats des tâches précédentes
            
        Returns:
            Résultat de la tâche
        """
        task.status = "running"
        task.started_at = datetime.utcnow()
        
        # Vérifier si validation humaine nécessaire
        if task.name in workflow.human_validation_points:
            validated = await self.request_human_validation(
                decision=f"Exécuter la tâche: {task.name}",
                context={
                    "task": task.dict(),
                    "workflow": workflow.name
                }
            )
            if not validated:
                raise Exception("Validation humaine refusée")
        
        # Préparer les données d'entrée avec contexte des tâches précédentes
        input_data = task.input_data.copy()
        for dep_id in task.dependencies:
            if dep_id in previous_results:
                input_data[f"dependency_{dep_id}"] = previous_results[dep_id]
        
        # Récupérer l'agent assigné
        agent = self.registered_agents.get(task.agent_id)
        if not agent:
            raise Exception(f"Agent {task.agent_id} non trouvé")
        
        # Exécuter la tâche via l'agent
        result = await agent.process(input_data)
        
        return result
    
    async def _consolidate_results(
        self,
        results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Consolide les résultats de toutes les tâches.
        
        Args:
            results: Résultats individuels des tâches
            
        Returns:
            Résultats consolidés
        """
        # Utiliser Claude pour synthétiser
        prompt = f"""Consolide ces résultats multi-agents en un rapport SST cohérent:

Résultats:
{results}

Crée une synthèse structurée avec:
- Vue d'ensemble
- Points clés identifiés
- Recommandations consolidées
- Actions prioritaires

Format JSON:
{{
    "summary": "synthèse générale",
    "key_findings": ["point 1", "point 2", ...],
    "consolidated_recommendations": ["rec 1", "rec 2", ...],
    "priority_actions": ["action 1", "action 2", ...],
    "confidence_level": "high|medium|low"
}}
"""
        
        response = await self.call_claude(
            prompt=prompt,
            max_tokens=2000,
            temperature=0.5
        )
        
        try:
            import json
            clean_response = response.strip()
            if clean_response.startswith("```json"):
                clean_response = clean_response[7:]
            if clean_response.endswith("```"):
                clean_response = clean_response[:-3]
            consolidated = json.loads(clean_response.strip())
            return consolidated
        except:
            return {
                "summary": "Consolidation automatique",
                "raw_results": results
            }
    
    def register_agent(self, agent_id: str, agent: BaseAgent):
        """
        Enregistre un agent dans l'orchestrateur.
        
        Args:
            agent_id: ID de l'agent
            agent: Instance de l'agent
        """
        self.registered_agents[agent_id] = agent
        self.logger.info(f"Agent {agent_id} enregistré")
    
    def unregister_agent(self, agent_id: str):
        """Désenregistre un agent."""
        if agent_id in self.registered_agents:
            del self.registered_agents[agent_id]
            self.logger.info(f"Agent {agent_id} désenregistré")
    
    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """
        Retourne le statut d'un workflow.
        
        Args:
            workflow_id: ID du workflow
            
        Returns:
            Statut du workflow
        """
        workflow = self.active_workflows.get(workflow_id)
        if not workflow:
            return None
        
        return {
            "workflow_id": workflow_id,
            "name": workflow.name,
            "status": workflow.status,
            "tasks_total": len(workflow.tasks),
            "tasks_completed": sum(
                1 for t in workflow.tasks if t.status == "completed"
            ),
            "tasks_failed": sum(
                1 for t in workflow.tasks if t.status == "failed"
            ),
            "started_at": workflow.started_at,
            "completed_at": workflow.completed_at
        }
