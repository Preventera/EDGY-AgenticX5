"""
Agent de Monitoring pour la surveillance continue des risques SST.

Cet agent surveille en temps réel les flux de données SST, détecte les anomalies,
et alerte les superviseurs avec des recommandations préventives.
"""

import asyncio
import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from .base_agent import BaseAgent, AgentMessage
from ..utils.config import AgentConfig


class RiskAlert(BaseModel):
    """Modèle d'alerte de risque."""
    
    alert_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    severity: str  # low, medium, high, critical
    risk_type: str
    location: str
    description: str
    recommended_actions: List[str]
    affected_employees: List[str] = Field(default_factory=list)
    requires_immediate_action: bool = False


class MonitoringAgent(BaseAgent):
    """
    Agent de surveillance continue pour la SST.
    
    Responsabilités:
    - Surveillance continue des flux de données SST
    - Détection d'anomalies et de patterns de risque
    - Génération d'alertes proactives
    - Recommandations préventives immédiates
    - Coordination avec autres agents en cas d'incident
    """
    
    def __init__(
        self,
        agent_id: str = "monitoring_agent_01",
        name: str = "SST Monitor",
        config: Optional[AgentConfig] = None,
        anthropic_api_key: Optional[str] = None
    ):
        """
        Initialise l'agent de monitoring.
        
        Args:
            agent_id: Identifiant unique
            name: Nom de l'agent
            config: Configuration
            anthropic_api_key: Clé API Anthropic
        """
        # Configuration par défaut si non fournie
        if config is None:
            config = AgentConfig(
                role_description=(
                    "Agent de surveillance continue des risques SST. "
                    "Surveille les flux de données, détecte les anomalies, "
                    "et alerte les superviseurs avec recommandations préventives."
                ),
                capabilities=[
                    "continuous_monitoring",
                    "anomaly_detection",
                    "alert_generation",
                    "preventive_recommendations"
                ],
                max_concurrent_tasks=5
            )
        
        super().__init__(
            agent_id=agent_id,
            name=name,
            config=config,
            anthropic_api_key=anthropic_api_key
        )
        
        # État spécifique au monitoring
        self.monitored_sources: List[str] = []
        self.active_alerts: List[RiskAlert] = []
        self.monitoring_active = False
        
        # Seuils de détection
        self.thresholds = {
            "critical": 0.9,
            "high": 0.75,
            "medium": 0.5,
            "low": 0.3
        }
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Traite les données de monitoring.
        
        Args:
            input_data: Données à surveiller
            
        Returns:
            Résultats de l'analyse avec alertes si nécessaire
        """
        self.update_state(
            status="active",
            current_task="processing_monitoring_data"
        )
        
        try:
            # Analyser les données avec Claude
            analysis = await self._analyze_data(input_data)
            
            # Détecter les risques
            risks = await self._detect_risks(analysis)
            
            # Générer les alertes si nécessaire
            alerts = []
            for risk in risks:
                if risk["severity"] in ["high", "critical"]:
                    alert = await self._generate_alert(risk, input_data)
                    alerts.append(alert)
                    self.active_alerts.append(alert)
            
            # Préparer les recommandations
            recommendations = await self._generate_recommendations(
                risks, input_data
            )
            
            self.state.success_count += 1
            self.update_state(status="idle", current_task=None)
            
            return {
                "status": "success",
                "analysis": analysis,
                "risks_detected": len(risks),
                "risks": risks,
                "alerts": [alert.dict() for alert in alerts],
                "recommendations": recommendations,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Erreur lors du traitement: {e}")
            self.state.error_count += 1
            self.update_state(status="error")
            raise
    
    async def _analyze_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyse les données avec Claude.
        
        Args:
            data: Données à analyser
            
        Returns:
            Résultats de l'analyse
        """
        prompt = f"""Analyse les données SST suivantes et identifie tous les risques potentiels:

Données:
{json.dumps(data, indent=2, ensure_ascii=False)}

Ta réponse DOIT être un objet JSON valide avec cette structure exacte:
{{
    "summary": "résumé de l'analyse en français",
    "risk_indicators": [
        {{
            "indicator": "nom de l'indicateur",
            "value": "valeur observée",
            "threshold": "seuil normal",
            "deviation": "écart en %",
            "severity": "low|medium|high|critical"
        }}
    ],
    "anomalies_detected": [
        "liste des anomalies"
    ],
    "context_factors": [
        "facteurs contextuels importants"
    ]
}}

IMPORTANT: Réponds UNIQUEMENT avec du JSON valide, sans texte avant ou après."""

        response = await self.call_claude(
            prompt=prompt,
            max_tokens=2000,
            temperature=0.3  # Basse température pour analyse factuelle
        )
        
        # Parser la réponse JSON
        try:
            # Nettoyer la réponse si elle contient des balises markdown
            clean_response = response.strip()
            if clean_response.startswith("```json"):
                clean_response = clean_response[7:]
            if clean_response.endswith("```"):
                clean_response = clean_response[:-3]
            clean_response = clean_response.strip()
            
            analysis = json.loads(clean_response)
            return analysis
        except json.JSONDecodeError as e:
            self.logger.error(f"Erreur parsing JSON: {e}\nRéponse: {response}")
            # Retour par défaut en cas d'erreur
            return {
                "summary": "Erreur d'analyse",
                "risk_indicators": [],
                "anomalies_detected": [],
                "context_factors": []
            }
    
    async def _detect_risks(
        self,
        analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Détecte et classifie les risques.
        
        Args:
            analysis: Résultats de l'analyse
            
        Returns:
            Liste des risques détectés
        """
        risks = []
        
        # Extraire les indicateurs de risque
        for indicator in analysis.get("risk_indicators", []):
            severity = indicator.get("severity", "low")
            
            # Créer un risque pour chaque indicateur anormal
            if severity in ["medium", "high", "critical"]:
                risk = {
                    "type": indicator.get("indicator", "unknown"),
                    "severity": severity,
                    "value": indicator.get("value"),
                    "threshold": indicator.get("threshold"),
                    "deviation": indicator.get("deviation"),
                    "detected_at": datetime.utcnow().isoformat()
                }
                risks.append(risk)
        
        # Ajouter les anomalies comme risques
        for anomaly in analysis.get("anomalies_detected", []):
            risks.append({
                "type": "anomaly",
                "severity": "medium",
                "description": anomaly,
                "detected_at": datetime.utcnow().isoformat()
            })
        
        return risks
    
    async def _generate_alert(
        self,
        risk: Dict[str, Any],
        context: Dict[str, Any]
    ) -> RiskAlert:
        """
        Génère une alerte de risque.
        
        Args:
            risk: Risque détecté
            context: Contexte de détection
            
        Returns:
            Alerte générée
        """
        # Demander à Claude de générer des recommandations
        prompt = f"""Un risque SST a été détecté. Génère des recommandations d'action immédiate.

Risque:
{json.dumps(risk, indent=2, ensure_ascii=False)}

Contexte:
{json.dumps(context, indent=2, ensure_ascii=False)}

Réponds UNIQUEMENT avec un objet JSON:
{{
    "description": "description claire du risque en français",
    "recommended_actions": [
        "action 1 concrète et immédiate",
        "action 2 concrète et immédiate",
        "action 3 concrète et immédiate"
    ],
    "location": "localisation précise",
    "requires_immediate_action": true/false
}}
"""
        
        response = await self.call_claude(
            prompt=prompt,
            max_tokens=1000,
            temperature=0.4
        )
        
        # Parser la réponse
        try:
            clean_response = response.strip()
            if clean_response.startswith("```json"):
                clean_response = clean_response[7:]
            if clean_response.endswith("```"):
                clean_response = clean_response[:-3]
            alert_data = json.loads(clean_response.strip())
        except:
            alert_data = {
                "description": f"Risque {risk.get('type')} détecté",
                "recommended_actions": ["Enquête immédiate requise"],
                "location": "Unknown",
                "requires_immediate_action": risk.get("severity") == "critical"
            }
        
        alert = RiskAlert(
            severity=risk.get("severity", "medium"),
            risk_type=risk.get("type", "unknown"),
            location=alert_data.get("location", "Unknown"),
            description=alert_data.get("description", ""),
            recommended_actions=alert_data.get("recommended_actions", []),
            requires_immediate_action=alert_data.get("requires_immediate_action", False)
        )
        
        self.logger.warning(
            f"Alerte générée: {alert.severity} - {alert.risk_type}"
        )
        
        return alert
    
    async def _generate_recommendations(
        self,
        risks: List[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> List[str]:
        """
        Génère des recommandations préventives.
        
        Args:
            risks: Liste des risques détectés
            context: Contexte
            
        Returns:
            Liste de recommandations
        """
        if not risks:
            return ["Aucune action préventive immédiate nécessaire."]
        
        prompt = f"""Génère des recommandations préventives basées sur ces risques SST:

Risques détectés:
{json.dumps(risks, indent=2, ensure_ascii=False)}

Contexte:
{json.dumps(context, indent=2, ensure_ascii=False)}

Fournis 3-5 recommandations préventives concrètes et actionnables.
Réponds sous forme de liste JSON:
["recommandation 1", "recommandation 2", ...]
"""
        
        response = await self.call_claude(
            prompt=prompt,
            max_tokens=800,
            temperature=0.5
        )
        
        try:
            clean_response = response.strip()
            if clean_response.startswith("```json"):
                clean_response = clean_response[7:]
            if clean_response.endswith("```"):
                clean_response = clean_response[:-3]
            recommendations = json.loads(clean_response.strip())
            return recommendations if isinstance(recommendations, list) else []
        except:
            return [
                "Surveillance accrue recommandée",
                "Inspection des équipements concernés",
                "Formation supplémentaire des équipes"
            ]
    
    async def start_monitoring(
        self,
        data_sources: List[str],
        alert_threshold: str = "medium"
    ):
        """
        Démarre la surveillance continue.
        
        Args:
            data_sources: Sources de données à surveiller
            alert_threshold: Seuil minimum pour générer des alertes
        """
        self.monitored_sources = data_sources
        self.monitoring_active = True
        
        self.logger.info(
            f"Monitoring démarré sur {len(data_sources)} sources, "
            f"seuil: {alert_threshold}"
        )
        
        self.update_state(
            status="monitoring",
            context_update={
                "sources": data_sources,
                "threshold": alert_threshold
            }
        )
    
    async def stop_monitoring(self):
        """Arrête la surveillance."""
        self.monitoring_active = False
        self.logger.info("Monitoring arrêté")
        self.update_state(status="idle")
    
    def get_active_alerts(self) -> List[RiskAlert]:
        """Retourne les alertes actives."""
        return self.active_alerts
    
    def clear_alerts(self):
        """Efface les alertes traitées."""
        self.active_alerts = []
        self.logger.info("Alertes effacées")
