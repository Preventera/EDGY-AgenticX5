"""
RecommendationAgent (R1) - Agent de Recommandations SST
EDGY-AgenticX5 | SafetyGraph

Responsabilités:
- Générer des recommandations basées sur les analyses de risques
- Prioriser les actions correctives
- Proposer des mesures préventives conformes CNESST
- Évaluer le ROI des recommandations
- Générer des plans d'action structurés
"""

import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum

from pydantic import BaseModel, Field
from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, XSD

from agents.base_agent import BaseAgent, AgentStatus, AgentCapability


# Namespaces RDF
SA = Namespace("http://safetyagentic.org/ontology#")
EDGY = Namespace("http://edgy.org/schema#")


class ActionPriority(str, Enum):
    """Priorité des actions recommandées"""
    IMMEDIATE = "immediate"     # Action dans l'heure
    URGENT = "urgent"           # Action dans les 24h
    HIGH = "high"               # Action dans la semaine
    MEDIUM = "medium"           # Action dans le mois
    LOW = "low"                 # Action planifiable


class ActionType(str, Enum):
    """Types d'actions recommandées"""
    ELIMINATION = "elimination"           # Éliminer le danger
    SUBSTITUTION = "substitution"         # Remplacer par moins dangereux
    ENGINEERING = "engineering_control"   # Contrôles techniques
    ADMINISTRATIVE = "administrative"     # Procédures, formation
    PPE = "ppe"                          # Équipements de protection
    MONITORING = "monitoring"             # Surveillance continue
    INVESTIGATION = "investigation"       # Enquête approfondie


class RecommendationStatus(str, Enum):
    """Statut des recommandations"""
    PROPOSED = "proposed"
    APPROVED = "approved"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REJECTED = "rejected"
    DEFERRED = "deferred"


class Recommendation(BaseModel):
    """Modèle de recommandation SST"""
    
    recommendation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    action_type: ActionType
    priority: ActionPriority
    status: RecommendationStatus = RecommendationStatus.PROPOSED
    
    # Détails
    risk_addressed: str
    affected_zones: List[str] = Field(default_factory=list)
    target_audience: List[str] = Field(default_factory=list)
    
    # Planning
    deadline: Optional[datetime] = None
    estimated_duration: Optional[str] = None
    estimated_cost: Optional[float] = None
    
    # Conformité
    regulatory_reference: Optional[str] = None
    compliance_impact: Optional[str] = None
    
    # ROI
    risk_reduction: float = Field(ge=0.0, le=100.0, default=0.0)
    roi_score: float = Field(ge=0.0, default=0.0)
    
    # Métadonnées
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str = ""
    confidence: float = Field(ge=0.0, le=1.0, default=0.8)


class ActionPlan(BaseModel):
    """Plan d'action complet"""
    
    plan_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    recommendations: List[Recommendation]
    total_risk_reduction: float
    total_estimated_cost: float
    implementation_timeline: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class RecommendationAgent(BaseAgent):
    """
    Agent de Recommandations (R1) - Architecture AgenticX5
    
    Cet agent est responsable de:
    1. Recevoir les analyses de risques de l'AnalysisAgent
    2. Générer des recommandations adaptées au contexte
    3. Prioriser selon la hiérarchie des contrôles
    4. Évaluer le ROI des actions proposées
    5. Créer des plans d'action structurés
    
    Position dans le pipeline:
    AnalysisAgent → [RecommendationAgent] → OrchestrationAgent
    """
    
    # Base de connaissances des recommandations par type de risque
    RECOMMENDATION_TEMPLATES = {
        "temperature_high": [
            {
                "title": "Installation de climatisation industrielle",
                "action_type": ActionType.ENGINEERING,
                "description": "Installer un système de climatisation dans la zone affectée pour maintenir une température < 30°C",
                "risk_reduction": 70,
                "estimated_cost": 15000,
                "duration": "2-4 semaines",
                "regulatory": "RSST art. 116-120"
            },
            {
                "title": "Rotation des travailleurs",
                "action_type": ActionType.ADMINISTRATIVE,
                "description": "Implémenter un système de rotation pour limiter l'exposition à la chaleur à 2h maximum",
                "risk_reduction": 40,
                "estimated_cost": 500,
                "duration": "1-2 jours",
                "regulatory": "RSST art. 120"
            },
            {
                "title": "Hydratation et pauses obligatoires",
                "action_type": ActionType.ADMINISTRATIVE,
                "description": "Fournir de l'eau fraîche et imposer des pauses de 15 min toutes les heures",
                "risk_reduction": 30,
                "estimated_cost": 200,
                "duration": "Immédiat",
                "regulatory": "RSST art. 120"
            }
        ],
        "noise_high": [
            {
                "title": "Encoffrement des machines bruyantes",
                "action_type": ActionType.ENGINEERING,
                "description": "Installer des capots insonorisés sur les équipements générant > 85 dB",
                "risk_reduction": 60,
                "estimated_cost": 8000,
                "duration": "1-2 semaines",
                "regulatory": "RSST art. 130-141"
            },
            {
                "title": "Protection auditive obligatoire",
                "action_type": ActionType.PPE,
                "description": "Fournir et imposer le port de protecteurs auditifs (NRR ≥ 25 dB)",
                "risk_reduction": 50,
                "estimated_cost": 50,
                "duration": "Immédiat",
                "regulatory": "RSST art. 141"
            },
            {
                "title": "Signalisation zones bruyantes",
                "action_type": ActionType.ADMINISTRATIVE,
                "description": "Installer une signalisation 'Protection auditive obligatoire' aux entrées des zones > 85 dB",
                "risk_reduction": 20,
                "estimated_cost": 100,
                "duration": "1-2 jours",
                "regulatory": "RSST art. 136"
            }
        ],
        "chemical_exposure": [
            {
                "title": "Ventilation locale par aspiration",
                "action_type": ActionType.ENGINEERING,
                "description": "Installer un système d'aspiration à la source des émissions chimiques",
                "risk_reduction": 75,
                "estimated_cost": 12000,
                "duration": "2-3 semaines",
                "regulatory": "RSST art. 101-108"
            },
            {
                "title": "Substitution par produit moins toxique",
                "action_type": ActionType.SUBSTITUTION,
                "description": "Remplacer le produit chimique par une alternative moins dangereuse",
                "risk_reduction": 80,
                "estimated_cost": 2000,
                "duration": "1-2 semaines",
                "regulatory": "RSST Annexe I"
            },
            {
                "title": "Équipements de protection respiratoire",
                "action_type": ActionType.PPE,
                "description": "Fournir des masques respiratoires adaptés (FFP2/FFP3 ou cartouches)",
                "risk_reduction": 45,
                "estimated_cost": 200,
                "duration": "Immédiat",
                "regulatory": "RSST art. 45"
            }
        ],
        "ergonomic_risk": [
            {
                "title": "Réaménagement du poste de travail",
                "action_type": ActionType.ENGINEERING,
                "description": "Ajuster la hauteur et disposition du poste selon les principes ergonomiques",
                "risk_reduction": 60,
                "estimated_cost": 3000,
                "duration": "1 semaine",
                "regulatory": "RSST art. 170"
            },
            {
                "title": "Aide mécanique à la manutention",
                "action_type": ActionType.ENGINEERING,
                "description": "Installer un équipement d'aide (chariot, palan, table élévatrice)",
                "risk_reduction": 70,
                "estimated_cost": 5000,
                "duration": "1-2 semaines",
                "regulatory": "RSST art. 166-168"
            },
            {
                "title": "Formation gestes et postures",
                "action_type": ActionType.ADMINISTRATIVE,
                "description": "Former les travailleurs aux techniques de manutention sécuritaires",
                "risk_reduction": 30,
                "estimated_cost": 1000,
                "duration": "1 jour",
                "regulatory": "LSST art. 51"
            }
        ],
        "general_risk": [
            {
                "title": "Investigation approfondie",
                "action_type": ActionType.INVESTIGATION,
                "description": "Mener une analyse détaillée pour identifier la cause racine du risque",
                "risk_reduction": 20,
                "estimated_cost": 500,
                "duration": "1-2 jours",
                "regulatory": "LSST art. 51"
            },
            {
                "title": "Surveillance renforcée",
                "action_type": ActionType.MONITORING,
                "description": "Augmenter la fréquence de surveillance et d'inspection de la zone",
                "risk_reduction": 25,
                "estimated_cost": 200,
                "duration": "Continu",
                "regulatory": "LSST art. 51"
            }
        ]
    }
    
    # Hiérarchie des contrôles (ordre de préférence)
    CONTROL_HIERARCHY = [
        ActionType.ELIMINATION,
        ActionType.SUBSTITUTION,
        ActionType.ENGINEERING,
        ActionType.ADMINISTRATIVE,
        ActionType.PPE,
        ActionType.MONITORING
    ]
    
    def __init__(
        self,
        agent_id: str = "recommendation_001",
        config: Optional[Dict[str, Any]] = None
    ):
        """Initialise le RecommendationAgent"""
        super().__init__(
            agent_id=agent_id,
            name="RecommendationAgent",
            config=config or {}
        )
        
        # Configuration
        self.min_risk_for_recommendation = 20.0  # Score minimum
        self.max_recommendations_per_analysis = 5
        self.prioritize_by_roi = True
        
        # Métriques
        self.state.metrics = {
            "recommendations_generated": 0,
            "action_plans_created": 0,
            "total_risk_reduction_proposed": 0,
            "recommendations_by_type": {}
        }
        
        self.logger.info(f"RecommendationAgent {agent_id} initialisé")
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Génère des recommandations basées sur l'analyse de risques.
        
        Args:
            input_data: Données de l'AnalysisAgent
                - risk_score: Score de risque (0-100)
                - risk_level: Niveau de risque
                - hazard_category: Catégorie de danger
                - alerts: Alertes générées
                - contributing_factors: Facteurs contributifs
                - location: Localisation
                - sensor_type: Type de capteur
        
        Returns:
            Dict contenant:
                - recommendations: Liste des recommandations
                - action_plan: Plan d'action structuré
                - total_risk_reduction: Réduction totale potentielle
                - rdf_graph: Graphe RDF
        """
        self.update_state(AgentStatus.RUNNING)
        
        try:
            # Extraire les données
            risk_score = input_data.get("risk_score", 0)
            risk_level = input_data.get("risk_level", "minimal")
            hazard_category = input_data.get("hazard_category", "physical")
            alerts = input_data.get("alerts", [])
            location = input_data.get("location", "unknown")
            sensor_type = input_data.get("sensor_type", "unknown")
            
            # Vérifier si des recommandations sont nécessaires
            if risk_score < self.min_risk_for_recommendation:
                self.update_state(AgentStatus.COMPLETED)
                return {
                    "status": "no_action_needed",
                    "message": f"Risk score ({risk_score}) below threshold ({self.min_risk_for_recommendation})",
                    "recommendations": [],
                    "agent_id": self.agent_id
                }
            
            # 1. Identifier le type de risque
            risk_type = self._identify_risk_type(
                sensor_type, hazard_category, alerts
            )
            
            # 2. Générer les recommandations
            recommendations = self._generate_recommendations(
                risk_type, risk_score, risk_level, location
            )
            
            # 3. Prioriser les recommandations
            prioritized = self._prioritize_recommendations(
                recommendations, risk_level
            )
            
            # 4. Calculer le ROI de chaque recommandation
            for rec in prioritized:
                rec.roi_score = self._calculate_roi(rec, risk_score)
            
            # 5. Limiter le nombre de recommandations
            final_recommendations = prioritized[:self.max_recommendations_per_analysis]
            
            # 6. Créer le plan d'action
            action_plan = self._create_action_plan(
                final_recommendations, risk_level
            )
            
            # 7. Générer RDF
            rdf_graph = self._generate_rdf(final_recommendations, action_plan)
            
            # 8. Métriques
            self._update_metrics(final_recommendations)
            
            self.update_state(AgentStatus.COMPLETED)
            
            return {
                "status": "success",
                "recommendations": [r.dict() for r in final_recommendations],
                "recommendations_count": len(final_recommendations),
                "action_plan": action_plan.dict(),
                "total_risk_reduction": action_plan.total_risk_reduction,
                "total_estimated_cost": action_plan.total_estimated_cost,
                "rdf_graph": rdf_graph,
                "agent_id": self.agent_id,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.update_state(AgentStatus.ERROR)
            self.logger.error(f"Erreur de génération de recommandations: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "agent_id": self.agent_id
            }
    
    def _identify_risk_type(
        self, 
        sensor_type: str, 
        hazard_category: str, 
        alerts: List[Dict]
    ) -> str:
        """Identifie le type de risque pour sélectionner les templates"""
        
        # Mapping basé sur le type de capteur et alertes
        if sensor_type in ["temperature"] and any(
            a.get("type") == "threshold_exceeded" for a in alerts
        ):
            return "temperature_high"
        
        if sensor_type in ["noise"] and any(
            a.get("type") == "threshold_exceeded" for a in alerts
        ):
            return "noise_high"
        
        if hazard_category == "chemical":
            return "chemical_exposure"
        
        if hazard_category == "ergonomic":
            return "ergonomic_risk"
        
        return "general_risk"
    
    def _generate_recommendations(
        self,
        risk_type: str,
        risk_score: float,
        risk_level: str,
        location: str
    ) -> List[Recommendation]:
        """Génère des recommandations à partir des templates"""
        
        templates = self.RECOMMENDATION_TEMPLATES.get(
            risk_type, 
            self.RECOMMENDATION_TEMPLATES["general_risk"]
        )
        
        recommendations = []
        
        for template in templates:
            # Déterminer la priorité en fonction du niveau de risque
            priority = self._determine_priority(risk_level, template["action_type"])
            
            # Calculer la deadline
            deadline = self._calculate_deadline(priority)
            
            rec = Recommendation(
                title=template["title"],
                description=template["description"],
                action_type=template["action_type"],
                priority=priority,
                risk_addressed=risk_type,
                affected_zones=[location] if location != "unknown" else [],
                target_audience=self._determine_audience(template["action_type"]),
                deadline=deadline,
                estimated_duration=template.get("duration"),
                estimated_cost=template.get("estimated_cost", 0),
                regulatory_reference=template.get("regulatory"),
                risk_reduction=template.get("risk_reduction", 0),
                created_by=self.agent_id
            )
            recommendations.append(rec)
        
        return recommendations
    
    def _determine_priority(
        self, 
        risk_level: str, 
        action_type: ActionType
    ) -> ActionPriority:
        """Détermine la priorité d'une action"""
        
        # Priorité basée sur le niveau de risque
        if risk_level == "critical":
            return ActionPriority.IMMEDIATE
        elif risk_level == "high":
            return ActionPriority.URGENT
        elif risk_level == "medium":
            return ActionPriority.HIGH
        elif risk_level == "low":
            return ActionPriority.MEDIUM
        else:
            return ActionPriority.LOW
    
    def _calculate_deadline(self, priority: ActionPriority) -> datetime:
        """Calcule la deadline en fonction de la priorité"""
        now = datetime.utcnow()
        
        deadlines = {
            ActionPriority.IMMEDIATE: timedelta(hours=1),
            ActionPriority.URGENT: timedelta(hours=24),
            ActionPriority.HIGH: timedelta(days=7),
            ActionPriority.MEDIUM: timedelta(days=30),
            ActionPriority.LOW: timedelta(days=90)
        }
        
        return now + deadlines.get(priority, timedelta(days=30))
    
    def _determine_audience(self, action_type: ActionType) -> List[str]:
        """Détermine le public cible pour une action"""
        audiences = {
            ActionType.ELIMINATION: ["Direction", "Ingénierie"],
            ActionType.SUBSTITUTION: ["Direction", "Achats", "HSE"],
            ActionType.ENGINEERING: ["Ingénierie", "Maintenance", "HSE"],
            ActionType.ADMINISTRATIVE: ["RH", "Formation", "Superviseurs"],
            ActionType.PPE: ["HSE", "Achats", "Superviseurs"],
            ActionType.MONITORING: ["HSE", "Superviseurs"],
            ActionType.INVESTIGATION: ["HSE", "Direction"]
        }
        return audiences.get(action_type, ["HSE"])
    
    def _prioritize_recommendations(
        self, 
        recommendations: List[Recommendation],
        risk_level: str
    ) -> List[Recommendation]:
        """Priorise les recommandations selon la hiérarchie des contrôles"""
        
        def sort_key(rec: Recommendation) -> Tuple:
            # Priorité par hiérarchie des contrôles
            hierarchy_index = (
                self.CONTROL_HIERARCHY.index(rec.action_type)
                if rec.action_type in self.CONTROL_HIERARCHY
                else len(self.CONTROL_HIERARCHY)
            )
            
            # Priorité par réduction de risque (inversé pour tri descendant)
            risk_reduction = -rec.risk_reduction
            
            # Priorité par ROI si activé
            if self.prioritize_by_roi and rec.estimated_cost:
                roi = rec.risk_reduction / max(1, rec.estimated_cost / 1000)
            else:
                roi = 0
            
            return (hierarchy_index, risk_reduction, -roi)
        
        return sorted(recommendations, key=sort_key)
    
    def _calculate_roi(
        self, 
        recommendation: Recommendation, 
        risk_score: float
    ) -> float:
        """Calcule le score ROI d'une recommandation"""
        
        if not recommendation.estimated_cost or recommendation.estimated_cost == 0:
            return recommendation.risk_reduction * 10  # Bonus si gratuit
        
        # ROI = (Réduction de risque * Facteur de risque) / Coût normalisé
        risk_factor = risk_score / 50  # Normaliser autour de 50
        cost_normalized = recommendation.estimated_cost / 1000
        
        roi = (recommendation.risk_reduction * risk_factor) / max(0.1, cost_normalized)
        
        return round(roi, 2)
    
    def _create_action_plan(
        self, 
        recommendations: List[Recommendation],
        risk_level: str
    ) -> ActionPlan:
        """Crée un plan d'action structuré"""
        
        # Calculer les totaux
        total_reduction = sum(r.risk_reduction for r in recommendations)
        # Ajuster pour éviter > 100% (effets non cumulatifs)
        total_reduction = min(95, total_reduction * 0.7)
        
        total_cost = sum(r.estimated_cost or 0 for r in recommendations)
        
        # Déterminer le timeline
        if risk_level == "critical":
            timeline = "Immédiat - Actions prioritaires dans l'heure"
        elif risk_level == "high":
            timeline = "Court terme - Actions dans les 24-48h"
        elif risk_level == "medium":
            timeline = "Moyen terme - Actions dans la semaine"
        else:
            timeline = "Planifié - Actions dans le mois"
        
        return ActionPlan(
            title=f"Plan d'action SST - Risque {risk_level}",
            recommendations=recommendations,
            total_risk_reduction=total_reduction,
            total_estimated_cost=total_cost,
            implementation_timeline=timeline
        )
    
    def _generate_rdf(
        self, 
        recommendations: List[Recommendation],
        action_plan: ActionPlan
    ) -> str:
        """Génère un graphe RDF pour les recommandations"""
        g = Graph()
        g.bind("sa", SA)
        g.bind("edgy", EDGY)
        
        # URI du plan d'action
        plan_uri = SA[f"ActionPlan_{action_plan.plan_id}"]
        g.add((plan_uri, RDF.type, SA.ActionPlan))
        g.add((plan_uri, SA.hasPlanId, Literal(action_plan.plan_id)))
        g.add((plan_uri, SA.hasTitle, Literal(action_plan.title)))
        g.add((plan_uri, SA.hasTotalRiskReduction, Literal(action_plan.total_risk_reduction, datatype=XSD.float)))
        g.add((plan_uri, SA.hasTotalCost, Literal(action_plan.total_estimated_cost, datatype=XSD.float)))
        g.add((plan_uri, SA.createdBy, Literal(self.agent_id)))
        
        # Ajouter chaque recommandation
        for rec in recommendations:
            rec_uri = SA[f"Recommendation_{rec.recommendation_id}"]
            g.add((rec_uri, RDF.type, SA.Recommendation))
            g.add((rec_uri, SA.hasTitle, Literal(rec.title)))
            g.add((rec_uri, SA.hasActionType, Literal(rec.action_type.value)))
            g.add((rec_uri, SA.hasPriority, Literal(rec.priority.value)))
            g.add((rec_uri, SA.hasRiskReduction, Literal(rec.risk_reduction, datatype=XSD.float)))
            
            # Lier au plan
            g.add((plan_uri, SA.hasRecommendation, rec_uri))
        
        return g.serialize(format="turtle")
    
    def _update_metrics(self, recommendations: List[Recommendation]):
        """Met à jour les métriques"""
        self.state.metrics["recommendations_generated"] += len(recommendations)
        self.state.metrics["action_plans_created"] += 1
        
        total_reduction = sum(r.risk_reduction for r in recommendations)
        self.state.metrics["total_risk_reduction_proposed"] += total_reduction
        
        for rec in recommendations:
            action_type = rec.action_type.value
            if action_type not in self.state.metrics["recommendations_by_type"]:
                self.state.metrics["recommendations_by_type"][action_type] = 0
            self.state.metrics["recommendations_by_type"][action_type] += 1
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques de recommandations"""
        return {
            "agent_id": self.agent_id,
            "recommendations_generated": self.state.metrics["recommendations_generated"],
            "action_plans_created": self.state.metrics["action_plans_created"],
            "total_risk_reduction_proposed": self.state.metrics["total_risk_reduction_proposed"],
            "recommendations_by_type": self.state.metrics["recommendations_by_type"]
        }


# Export
__all__ = [
    "RecommendationAgent",
    "Recommendation",
    "ActionPlan",
    "ActionPriority",
    "ActionType",
    "RecommendationStatus"
]
