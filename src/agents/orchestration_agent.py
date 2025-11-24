"""
OrchestrationAgent - Agent d'Orchestration Multi-Agents
EDGY-AgenticX5 | SafetyGraph

Responsabilités:
- Coordonner le flux entre tous les agents
- Gérer le pipeline Perception → Normalization → Analysis → Recommendation
- Router les données vers les agents appropriés
- Gérer les erreurs et reprises
- Collecter les métriques globales
- Fournir une interface unifiée
"""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Callable
from enum import Enum

from pydantic import BaseModel, Field

from agents.base_agent import BaseAgent, AgentStatus, AgentCapability
from agents.perception_agent import PerceptionAgent
from agents.normalization_agent import NormalizationAgent
from agents.analysis_agent import AnalysisAgent
from agents.recommendation_agent import RecommendationAgent


class WorkflowStatus(str, Enum):
    """Status du workflow d'orchestration"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"  # Certaines étapes ont échoué


class PipelineStage(str, Enum):
    """Étapes du pipeline AgenticX5"""
    PERCEPTION = "perception"
    NORMALIZATION = "normalization"
    ANALYSIS = "analysis"
    RECOMMENDATION = "recommendation"
    ORCHESTRATION = "orchestration"


class WorkflowResult(BaseModel):
    """Résultat d'un workflow complet"""
    
    workflow_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    status: WorkflowStatus
    stages_completed: List[str]
    stages_failed: List[str]
    
    # Résultats par étape
    perception_result: Optional[Dict[str, Any]] = None
    normalization_result: Optional[Dict[str, Any]] = None
    analysis_result: Optional[Dict[str, Any]] = None
    recommendation_result: Optional[Dict[str, Any]] = None
    
    # Métriques
    total_duration_ms: float = 0.0
    risk_score: Optional[float] = None
    recommendations_count: int = 0
    
    # Métadonnées
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    orchestrated_by: str = ""
    
    # Erreurs
    errors: List[Dict[str, Any]] = Field(default_factory=list)


class OrchestrationAgent(BaseAgent):
    """
    Agent d'Orchestration - Architecture AgenticX5
    
    Cet agent est le chef d'orchestre qui:
    1. Reçoit les données brutes des capteurs
    2. Coordonne le flux à travers tous les agents
    3. Gère les erreurs et reprises
    4. Agrège les résultats
    5. Fournit une interface unifiée pour le système
    
    Pipeline complet:
    [Input] → Perception → Normalization → Analysis → Recommendation → [Output]
    """
    
    def __init__(
        self,
        agent_id: str = "orchestrator_001",
        config: Optional[Dict[str, Any]] = None
    ):
        """Initialise l'OrchestrationAgent avec tous les agents du pipeline"""
        super().__init__(
            agent_id=agent_id,
            name="OrchestrationAgent",
            config=config or {}
        )
        
        # Initialiser les agents du pipeline
        self.perception_agent = PerceptionAgent(
            agent_id="perception_orch_001"
        )
        self.normalization_agent = NormalizationAgent(
            agent_id="normalization_orch_001"
        )
        self.analysis_agent = AnalysisAgent(
            agent_id="analysis_orch_001"
        )
        self.recommendation_agent = RecommendationAgent(
            agent_id="recommendation_orch_001"
        )
        
        # Configuration du pipeline
        self.pipeline_stages = [
            PipelineStage.PERCEPTION,
            PipelineStage.NORMALIZATION,
            PipelineStage.ANALYSIS,
            PipelineStage.RECOMMENDATION
        ]
        
        # Options
        self.continue_on_error = False  # Arrêter ou continuer en cas d'erreur
        self.collect_metrics = True
        
        # Métriques globales
        self.state.metrics = {
            "workflows_executed": 0,
            "workflows_successful": 0,
            "workflows_failed": 0,
            "average_duration_ms": 0,
            "total_alerts_generated": 0,
            "total_recommendations_generated": 0
        }
        
        # Historique des workflows
        self.workflow_history: List[WorkflowResult] = []
        self.max_history_size = 100
        
        self.logger.info(f"OrchestrationAgent {agent_id} initialisé avec pipeline complet")
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Exécute le pipeline complet sur les données d'entrée.
        
        Args:
            input_data: Données brutes du capteur
                - source: Source des données
                - sensor_type: Type de capteur
                - value: Valeur mesurée
                - unit: Unité de mesure
                - location: Localisation (optionnel)
                - timestamp: Horodatage (optionnel)
        
        Returns:
            WorkflowResult avec tous les résultats du pipeline
        """
        self.update_state(AgentStatus.RUNNING)
        start_time = datetime.utcnow()
        
        # Initialiser le résultat
        result = WorkflowResult(
            status=WorkflowStatus.PENDING,
            stages_completed=[],
            stages_failed=[],
            orchestrated_by=self.agent_id
        )
        
        try:
            # ========== ÉTAPE 1: PERCEPTION ==========
            self.logger.info("🔍 Étape 1: Perception")
            perception_result = self._execute_stage(
                PipelineStage.PERCEPTION,
                self.perception_agent,
                input_data,
                result
            )
            
            if not perception_result or perception_result.get("status") == "error":
                if not self.continue_on_error:
                    return self._finalize_workflow(result, start_time, failed=True)
            
            result.perception_result = perception_result
            
            # ========== ÉTAPE 2: NORMALIZATION ==========
            self.logger.info("📊 Étape 2: Normalisation")
            
            # Préparer les données pour la normalisation
            norm_input = {
                "value": perception_result.get("value", input_data.get("value")),
                "unit": perception_result.get("unit", input_data.get("unit")),
                "sensor_type": input_data.get("sensor_type"),
                "source_agent_id": self.perception_agent.agent_id,
                "location": input_data.get("location", "unknown")
            }
            
            normalization_result = self._execute_stage(
                PipelineStage.NORMALIZATION,
                self.normalization_agent,
                norm_input,
                result
            )
            
            if not normalization_result or normalization_result.get("status") == "error":
                if not self.continue_on_error:
                    return self._finalize_workflow(result, start_time, failed=True)
            
            # Vérifier si données rejetées pour qualité
            if normalization_result.get("status") == "rejected":
                self.logger.warning("⚠️ Données rejetées pour qualité insuffisante")
                result.normalization_result = normalization_result
                return self._finalize_workflow(result, start_time, partial=True)
            
            result.normalization_result = normalization_result
            
            # ========== ÉTAPE 3: ANALYSIS ==========
            self.logger.info("🔬 Étape 3: Analyse")
            
            # Préparer les données pour l'analyse
            analysis_input = {
                "normalized_value": normalization_result.get("normalized_value"),
                "normalized_unit": normalization_result.get("normalized_unit"),
                "sensor_type": input_data.get("sensor_type"),
                "quality_score": normalization_result.get("quality_score", 0.8),
                "location": input_data.get("location", "unknown")
            }
            
            analysis_result = self._execute_stage(
                PipelineStage.ANALYSIS,
                self.analysis_agent,
                analysis_input,
                result
            )
            
            if not analysis_result or analysis_result.get("status") == "error":
                if not self.continue_on_error:
                    return self._finalize_workflow(result, start_time, failed=True)
            
            result.analysis_result = analysis_result
            result.risk_score = analysis_result.get("risk_score", 0)
            
            # Collecter les alertes
            alerts_count = analysis_result.get("alerts_count", 0)
            self.state.metrics["total_alerts_generated"] += alerts_count
            
            # ========== ÉTAPE 4: RECOMMENDATION ==========
            # Seulement si des recommandations sont nécessaires
            if analysis_result.get("recommendations_needed", False):
                self.logger.info("💡 Étape 4: Recommandations")
                
                # Préparer les données pour les recommandations
                rec_input = {
                    "risk_score": analysis_result.get("risk_score"),
                    "risk_level": analysis_result.get("risk_level"),
                    "hazard_category": analysis_result.get("hazard_category"),
                    "alerts": analysis_result.get("alerts", []),
                    "contributing_factors": analysis_result.get("contributing_factors", []),
                    "location": input_data.get("location", "unknown"),
                    "sensor_type": input_data.get("sensor_type")
                }
                
                recommendation_result = self._execute_stage(
                    PipelineStage.RECOMMENDATION,
                    self.recommendation_agent,
                    rec_input,
                    result
                )
                
                result.recommendation_result = recommendation_result
                
                if recommendation_result:
                    rec_count = recommendation_result.get("recommendations_count", 0)
                    result.recommendations_count = rec_count
                    self.state.metrics["total_recommendations_generated"] += rec_count
            else:
                self.logger.info("ℹ️ Pas de recommandations nécessaires (risque faible)")
                result.stages_completed.append(PipelineStage.RECOMMENDATION.value)
            
            # Finaliser avec succès
            return self._finalize_workflow(result, start_time)
            
        except Exception as e:
            self.logger.error(f"Erreur critique dans l'orchestration: {str(e)}")
            result.errors.append({
                "stage": "orchestration",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            })
            return self._finalize_workflow(result, start_time, failed=True)
    
    def _execute_stage(
        self,
        stage: PipelineStage,
        agent: BaseAgent,
        input_data: Dict[str, Any],
        result: WorkflowResult
    ) -> Optional[Dict[str, Any]]:
        """Exécute une étape du pipeline"""
        try:
            stage_result = agent.process(input_data)
            
            if stage_result.get("status") == "success":
                result.stages_completed.append(stage.value)
            elif stage_result.get("status") == "error":
                result.stages_failed.append(stage.value)
                result.errors.append({
                    "stage": stage.value,
                    "error": stage_result.get("error", "Unknown error"),
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            return stage_result
            
        except Exception as e:
            self.logger.error(f"Erreur dans l'étape {stage.value}: {str(e)}")
            result.stages_failed.append(stage.value)
            result.errors.append({
                "stage": stage.value,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            })
            return None
    
    def _finalize_workflow(
        self,
        result: WorkflowResult,
        start_time: datetime,
        failed: bool = False,
        partial: bool = False
    ) -> Dict[str, Any]:
        """Finalise le workflow et met à jour les métriques"""
        
        end_time = datetime.utcnow()
        duration_ms = (end_time - start_time).total_seconds() * 1000
        
        result.completed_at = end_time
        result.total_duration_ms = duration_ms
        
        if failed:
            result.status = WorkflowStatus.FAILED
            self.state.metrics["workflows_failed"] += 1
        elif partial:
            result.status = WorkflowStatus.PARTIAL
        else:
            result.status = WorkflowStatus.COMPLETED
            self.state.metrics["workflows_successful"] += 1
        
        # Mettre à jour les métriques globales
        self.state.metrics["workflows_executed"] += 1
        
        # Calculer la moyenne de durée
        total = self.state.metrics["workflows_executed"]
        current_avg = self.state.metrics["average_duration_ms"]
        self.state.metrics["average_duration_ms"] = (
            (current_avg * (total - 1) + duration_ms) / total
        )
        
        # Ajouter à l'historique
        self.workflow_history.append(result)
        if len(self.workflow_history) > self.max_history_size:
            self.workflow_history = self.workflow_history[-self.max_history_size:]
        
        # Mettre à jour le status de l'agent
        self.update_state(
            AgentStatus.ERROR if failed else AgentStatus.COMPLETED
        )
        
        self.logger.info(
            f"Workflow {result.workflow_id} terminé - "
            f"Status: {result.status.value} - "
            f"Durée: {duration_ms:.2f}ms"
        )
        
        return result.dict()
    
    def process_batch(
        self, 
        data_list: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Traite un lot de données en série.
        
        Args:
            data_list: Liste de données capteurs
            
        Returns:
            Liste des résultats de workflow
        """
        results = []
        
        for i, data in enumerate(data_list):
            self.logger.info(f"Traitement batch {i+1}/{len(data_list)}")
            result = self.process(data)
            results.append(result)
        
        return results
    
    def get_pipeline_status(self) -> Dict[str, Any]:
        """Retourne le status de tous les agents du pipeline"""
        return {
            "orchestrator": {
                "agent_id": self.agent_id,
                "status": self.state.status
            },
            "perception": {
                "agent_id": self.perception_agent.agent_id,
                "status": self.perception_agent.state.status
            },
            "normalization": {
                "agent_id": self.normalization_agent.agent_id,
                "status": self.normalization_agent.state.status
            },
            "analysis": {
                "agent_id": self.analysis_agent.agent_id,
                "status": self.analysis_agent.state.status
            },
            "recommendation": {
                "agent_id": self.recommendation_agent.agent_id,
                "status": self.recommendation_agent.state.status
            }
        }
    
    def get_global_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques globales du système"""
        return {
            "orchestrator": {
                "agent_id": self.agent_id,
                "workflows_executed": self.state.metrics["workflows_executed"],
                "workflows_successful": self.state.metrics["workflows_successful"],
                "workflows_failed": self.state.metrics["workflows_failed"],
                "success_rate": (
                    self.state.metrics["workflows_successful"] / 
                    max(1, self.state.metrics["workflows_executed"])
                ) * 100,
                "average_duration_ms": self.state.metrics["average_duration_ms"],
                "total_alerts": self.state.metrics["total_alerts_generated"],
                "total_recommendations": self.state.metrics["total_recommendations_generated"]
            },
            "agents": {
                "perception": self.perception_agent.get_statistics() if hasattr(self.perception_agent, 'get_statistics') else {},
                "normalization": self.normalization_agent.get_statistics(),
                "analysis": self.analysis_agent.get_statistics(),
                "recommendation": self.recommendation_agent.get_statistics()
            }
        }
    
    def get_recent_workflows(self, n: int = 10) -> List[Dict[str, Any]]:
        """Retourne les n derniers workflows"""
        return [w.dict() for w in self.workflow_history[-n:]]
    
    def reset_metrics(self):
        """Réinitialise toutes les métriques"""
        self.state.metrics = {
            "workflows_executed": 0,
            "workflows_successful": 0,
            "workflows_failed": 0,
            "average_duration_ms": 0,
            "total_alerts_generated": 0,
            "total_recommendations_generated": 0
        }
        self.workflow_history = []
        self.logger.info("Métriques réinitialisées")


# Export
__all__ = [
    "OrchestrationAgent",
    "WorkflowResult",
    "WorkflowStatus",
    "PipelineStage"
]
