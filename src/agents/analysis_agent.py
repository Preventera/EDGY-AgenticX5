"""
AnalysisAgent (AN1) - Agent d'Analyse des Risques
EDGY-AgenticX5 | SafetyGraph

Responsabilités:
- Analyser les données normalisées
- Détecter les anomalies et risques SST
- Calculer les scores de risque
- Identifier les patterns dangereux
- Générer des alertes pour le RecommendationAgent
"""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass

from pydantic import BaseModel, Field
from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, XSD

from agents.base_agent import BaseAgent, AgentStatus, AgentCapability


# Namespaces RDF
SA = Namespace("http://safetyagentic.org/ontology#")
EDGY = Namespace("http://edgy.org/schema#")


class RiskLevel(str, Enum):
    """Niveaux de risque SST"""
    CRITICAL = "critical"      # Action immédiate requise
    HIGH = "high"              # Action urgente (< 24h)
    MEDIUM = "medium"          # Action planifiée (< 1 semaine)
    LOW = "low"                # Surveillance continue
    MINIMAL = "minimal"        # Risque négligeable


class AlertType(str, Enum):
    """Types d'alertes générées"""
    THRESHOLD_EXCEEDED = "threshold_exceeded"
    ANOMALY_DETECTED = "anomaly_detected"
    PATTERN_IDENTIFIED = "pattern_identified"
    TREND_WARNING = "trend_warning"
    EQUIPMENT_FAILURE = "equipment_failure"
    REGULATORY_VIOLATION = "regulatory_violation"


class HazardCategory(str, Enum):
    """Catégories de dangers SST (CNESST)"""
    PHYSICAL = "physical"           # Bruit, vibration, température
    CHEMICAL = "chemical"           # Gaz, poussières, substances
    BIOLOGICAL = "biological"       # Agents biologiques
    ERGONOMIC = "ergonomic"         # Postures, mouvements répétitifs
    PSYCHOSOCIAL = "psychosocial"   # Stress, harcèlement
    MECHANICAL = "mechanical"       # Équipements, machines
    ELECTRICAL = "electrical"       # Risques électriques


class RiskAnalysis(BaseModel):
    """Résultat d'analyse de risque"""
    
    analysis_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    risk_score: float = Field(ge=0.0, le=100.0)
    risk_level: RiskLevel
    hazard_category: HazardCategory
    alerts: List[Dict[str, Any]] = Field(default_factory=list)
    contributing_factors: List[str] = Field(default_factory=list)
    affected_zones: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    confidence: float = Field(ge=0.0, le=1.0, default=0.8)


class AnalysisAgent(BaseAgent):
    """
    Agent d'Analyse (AN1) - Architecture AgenticX5
    
    Cet agent est responsable de:
    1. Analyser les données normalisées
    2. Détecter les dépassements de seuils réglementaires
    3. Identifier les anomalies statistiques
    4. Calculer les scores de risque multicritères
    5. Générer des alertes pour le RecommendationAgent
    
    Position dans le pipeline:
    NormalizationAgent → [AnalysisAgent] → RecommendationAgent
    """
    
    # Seuils réglementaires SST Québec (CNESST/RSST)
    REGULATORY_THRESHOLDS = {
        "temperature": {
            "min": 17,      # °C - Température minimale lieu de travail
            "max": 35,      # °C - Température maximale avant mesures
            "critical": 40, # °C - Arrêt de travail
            "unit": "°C",
            "regulation": "RSST art. 116-120",
            "hazard": HazardCategory.PHYSICAL
        },
        "noise": {
            "exposure_8h": 85,    # dB - Limite 8h
            "exposure_4h": 88,    # dB - Limite 4h
            "exposure_2h": 91,    # dB - Limite 2h
            "peak": 140,          # dB - Niveau crête max
            "critical": 100,      # dB - Protection obligatoire
            "unit": "dB",
            "regulation": "RSST art. 130-141",
            "hazard": HazardCategory.PHYSICAL
        },
        "vibration": {
            "daily_limit": 5.0,   # m/s² - Limite journalière
            "action_level": 2.5,  # m/s² - Niveau d'action
            "unit": "m/s²",
            "regulation": "Directive UE 2002/44/CE",
            "hazard": HazardCategory.PHYSICAL
        },
        "humidity": {
            "min": 30,      # % - Humidité minimale
            "max": 70,      # % - Humidité maximale
            "optimal_min": 40,
            "optimal_max": 60,
            "unit": "%",
            "regulation": "ASHRAE 55",
            "hazard": HazardCategory.PHYSICAL
        },
        "co2": {
            "acceptable": 1000,   # ppm - Niveau acceptable
            "elevated": 2000,     # ppm - Niveau élevé
            "critical": 5000,     # ppm - Danger immédiat
            "unit": "ppm",
            "regulation": "RSST art. 101",
            "hazard": HazardCategory.CHEMICAL
        },
        "co": {
            "twa_8h": 35,        # ppm - Moyenne 8h
            "ceiling": 200,       # ppm - Valeur plafond
            "critical": 400,      # ppm - Évacuation
            "unit": "ppm",
            "regulation": "RSST Annexe I",
            "hazard": HazardCategory.CHEMICAL
        },
        "light_level": {
            "office_min": 300,    # lux - Bureau minimum
            "industrial_min": 200, # lux - Industrie minimum
            "precision_min": 500,  # lux - Travail de précision
            "unit": "lux",
            "regulation": "RSST art. 125",
            "hazard": HazardCategory.PHYSICAL
        },
        "pressure": {
            "min": 95000,    # Pa - Pression minimale
            "max": 105000,   # Pa - Pression maximale
            "unit": "Pa",
            "hazard": HazardCategory.PHYSICAL
        }
    }
    
    # Pondération des facteurs de risque
    RISK_WEIGHTS = {
        "severity": 0.4,      # Gravité potentielle
        "probability": 0.3,   # Probabilité d'occurrence
        "exposure": 0.2,      # Niveau d'exposition
        "reversibility": 0.1  # Réversibilité des effets
    }
    
    def __init__(
        self,
        agent_id: str = "analysis_001",
        config: Optional[Dict[str, Any]] = None
    ):
        """Initialise l'AnalysisAgent"""
        super().__init__(
            agent_id=agent_id,
            name="AnalysisAgent",
            config=config or {}
        )
        
        # Configuration
        self.alert_threshold = 50.0  # Score minimum pour alerte
        self.anomaly_sensitivity = 2.0  # Écarts-types pour anomalie
        
        # Historique pour détection de tendances
        self.observation_history: Dict[str, List[Dict]] = {}
        self.max_history_size = 100
        
        # Métriques
        self.state.metrics = {
            "analyses_performed": 0,
            "alerts_generated": 0,
            "critical_risks_detected": 0,
            "risk_scores": []
        }
        
        self.logger.info(f"AnalysisAgent {agent_id} initialisé")
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyse les données normalisées et évalue les risques.
        
        Args:
            input_data: Données du NormalizationAgent
                - normalized_value: Valeur normalisée
                - normalized_unit: Unité SI
                - sensor_type: Type de capteur
                - quality_score: Score de qualité
                - location: Localisation (optionnel)
                - metadata: Métadonnées
        
        Returns:
            Dict contenant:
                - analysis_id: ID unique de l'analyse
                - risk_score: Score de risque (0-100)
                - risk_level: Niveau de risque
                - alerts: Liste des alertes générées
                - recommendations_needed: Bool
                - rdf_graph: Graphe RDF
        """
        self.update_state(AgentStatus.RUNNING)
        
        try:
            # Extraire les données
            value = input_data.get("normalized_value")
            unit = input_data.get("normalized_unit", "")
            sensor_type = input_data.get("sensor_type", "unknown")
            location = input_data.get("location", "unknown")
            quality_score = input_data.get("quality_score", 0.8)
            
            if value is None:
                raise ValueError("Valeur normalisée manquante")
            
            # 1. Analyse des seuils réglementaires
            threshold_analysis = self._analyze_thresholds(
                value, unit, sensor_type
            )
            
            # 2. Détection d'anomalies
            anomaly_analysis = self._detect_anomalies(
                value, sensor_type, location
            )
            
            # 3. Analyse de tendance
            trend_analysis = self._analyze_trend(
                value, sensor_type, location
            )
            
            # 4. Calcul du score de risque global
            risk_score, risk_level = self._calculate_risk_score(
                threshold_analysis,
                anomaly_analysis,
                trend_analysis,
                quality_score
            )
            
            # 5. Génération des alertes
            alerts = self._generate_alerts(
                threshold_analysis,
                anomaly_analysis,
                trend_analysis,
                risk_level,
                sensor_type,
                location
            )
            
            # 6. Déterminer la catégorie de danger
            hazard_category = self._get_hazard_category(sensor_type)
            
            # 7. Créer l'objet d'analyse
            analysis = RiskAnalysis(
                risk_score=risk_score,
                risk_level=risk_level,
                hazard_category=hazard_category,
                alerts=[a.__dict__ if hasattr(a, '__dict__') else a for a in alerts],
                contributing_factors=self._identify_factors(
                    threshold_analysis, anomaly_analysis
                ),
                affected_zones=[location] if location != "unknown" else [],
                confidence=quality_score * 0.9
            )
            
            # 8. Mettre à jour l'historique
            self._update_history(value, sensor_type, location)
            
            # 9. Générer RDF
            rdf_graph = self._generate_rdf(analysis, input_data)
            
            # 10. Métriques
            self.state.metrics["analyses_performed"] += 1
            self.state.metrics["alerts_generated"] += len(alerts)
            self.state.metrics["risk_scores"].append(risk_score)
            if risk_level == RiskLevel.CRITICAL:
                self.state.metrics["critical_risks_detected"] += 1
            
            self.update_state(AgentStatus.COMPLETED)
            
            return {
                "status": "success",
                "analysis_id": analysis.analysis_id,
                "risk_score": analysis.risk_score,
                "risk_level": analysis.risk_level.value,
                "hazard_category": analysis.hazard_category.value,
                "alerts": analysis.alerts,
                "alerts_count": len(alerts),
                "contributing_factors": analysis.contributing_factors,
                "recommendations_needed": risk_score >= self.alert_threshold,
                "confidence": analysis.confidence,
                "rdf_graph": rdf_graph,
                "agent_id": self.agent_id,
                "timestamp": analysis.timestamp.isoformat()
            }
            
        except Exception as e:
            self.update_state(AgentStatus.ERROR)
            self.logger.error(f"Erreur d'analyse: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "agent_id": self.agent_id
            }
    
    def _analyze_thresholds(
        self, 
        value: float, 
        unit: str, 
        sensor_type: str
    ) -> Dict[str, Any]:
        """Analyse les dépassements de seuils réglementaires"""
        result = {
            "exceeded": False,
            "violations": [],
            "severity": 0.0,
            "regulation": None
        }
        
        if sensor_type not in self.REGULATORY_THRESHOLDS:
            return result
        
        thresholds = self.REGULATORY_THRESHOLDS[sensor_type]
        result["regulation"] = thresholds.get("regulation")
        
        # Vérifier chaque seuil applicable
        if "max" in thresholds and value > thresholds["max"]:
            result["exceeded"] = True
            result["violations"].append({
                "type": "max_exceeded",
                "value": value,
                "threshold": thresholds["max"],
                "excess": value - thresholds["max"]
            })
            result["severity"] = min(1.0, (value - thresholds["max"]) / thresholds["max"])
        
        if "min" in thresholds and value < thresholds["min"]:
            result["exceeded"] = True
            result["violations"].append({
                "type": "min_exceeded",
                "value": value,
                "threshold": thresholds["min"],
                "deficit": thresholds["min"] - value
            })
            result["severity"] = min(1.0, (thresholds["min"] - value) / thresholds["min"])
        
        if "critical" in thresholds and value >= thresholds["critical"]:
            result["exceeded"] = True
            result["violations"].append({
                "type": "critical_level",
                "value": value,
                "threshold": thresholds["critical"]
            })
            result["severity"] = 1.0  # Sévérité maximale
        
        return result
    
    def _detect_anomalies(
        self, 
        value: float, 
        sensor_type: str, 
        location: str
    ) -> Dict[str, Any]:
        """Détecte les anomalies statistiques"""
        result = {
            "is_anomaly": False,
            "z_score": 0.0,
            "deviation_type": None
        }
        
        # Récupérer l'historique
        history_key = f"{sensor_type}_{location}"
        if history_key not in self.observation_history:
            return result
        
        history = self.observation_history[history_key]
        if len(history) < 5:  # Besoin d'un minimum d'historique
            return result
        
        # Calculer statistiques
        values = [h["value"] for h in history]
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        std_dev = variance ** 0.5
        
        if std_dev == 0:
            return result
        
        # Z-score
        z_score = (value - mean) / std_dev
        result["z_score"] = z_score
        
        # Détection d'anomalie
        if abs(z_score) > self.anomaly_sensitivity:
            result["is_anomaly"] = True
            result["deviation_type"] = "high" if z_score > 0 else "low"
        
        return result
    
    def _analyze_trend(
        self, 
        value: float, 
        sensor_type: str, 
        location: str
    ) -> Dict[str, Any]:
        """Analyse les tendances dans les données"""
        result = {
            "trend": "stable",
            "trend_strength": 0.0,
            "prediction": None
        }
        
        history_key = f"{sensor_type}_{location}"
        if history_key not in self.observation_history:
            return result
        
        history = self.observation_history[history_key]
        if len(history) < 3:
            return result
        
        # Analyse simple de tendance (dernières valeurs)
        recent_values = [h["value"] for h in history[-5:]]
        
        if len(recent_values) >= 3:
            # Calculer la pente moyenne
            slopes = [
                recent_values[i+1] - recent_values[i] 
                for i in range(len(recent_values)-1)
            ]
            avg_slope = sum(slopes) / len(slopes)
            
            # Déterminer la tendance
            if avg_slope > 0.5:
                result["trend"] = "increasing"
                result["trend_strength"] = min(1.0, avg_slope / 2)
            elif avg_slope < -0.5:
                result["trend"] = "decreasing"
                result["trend_strength"] = min(1.0, abs(avg_slope) / 2)
            else:
                result["trend"] = "stable"
                result["trend_strength"] = 0.0
        
        return result
    
    def _calculate_risk_score(
        self,
        threshold_analysis: Dict,
        anomaly_analysis: Dict,
        trend_analysis: Dict,
        quality_score: float
    ) -> Tuple[float, RiskLevel]:
        """Calcule le score de risque global (0-100)"""
        
        # Composantes du score
        threshold_score = 0.0
        if threshold_analysis["exceeded"]:
            threshold_score = 40 + (threshold_analysis["severity"] * 60)
        
        anomaly_score = 0.0
        if anomaly_analysis["is_anomaly"]:
            anomaly_score = min(30, abs(anomaly_analysis["z_score"]) * 10)
        
        trend_score = 0.0
        if trend_analysis["trend"] == "increasing":
            trend_score = trend_analysis["trend_strength"] * 20
        
        # Score brut
        raw_score = threshold_score + anomaly_score + trend_score
        
        # Ajustement par qualité des données
        adjusted_score = raw_score * quality_score
        
        # Limiter entre 0 et 100
        final_score = max(0.0, min(100.0, adjusted_score))
        
        # Déterminer le niveau de risque
        if final_score >= 80:
            risk_level = RiskLevel.CRITICAL
        elif final_score >= 60:
            risk_level = RiskLevel.HIGH
        elif final_score >= 40:
            risk_level = RiskLevel.MEDIUM
        elif final_score >= 20:
            risk_level = RiskLevel.LOW
        else:
            risk_level = RiskLevel.MINIMAL
        
        return final_score, risk_level
    
    def _generate_alerts(
        self,
        threshold_analysis: Dict,
        anomaly_analysis: Dict,
        trend_analysis: Dict,
        risk_level: RiskLevel,
        sensor_type: str,
        location: str
    ) -> List[Dict[str, Any]]:
        """Génère les alertes appropriées"""
        alerts = []
        
        # Alertes de dépassement de seuil
        if threshold_analysis["exceeded"]:
            for violation in threshold_analysis["violations"]:
                alerts.append({
                    "alert_id": str(uuid.uuid4()),
                    "type": AlertType.THRESHOLD_EXCEEDED.value,
                    "severity": risk_level.value,
                    "message": f"Seuil dépassé: {violation['type']} pour {sensor_type}",
                    "details": violation,
                    "regulation": threshold_analysis["regulation"],
                    "location": location,
                    "timestamp": datetime.utcnow().isoformat()
                })
        
        # Alertes d'anomalie
        if anomaly_analysis["is_anomaly"]:
            alerts.append({
                "alert_id": str(uuid.uuid4()),
                "type": AlertType.ANOMALY_DETECTED.value,
                "severity": "high" if abs(anomaly_analysis["z_score"]) > 3 else "medium",
                "message": f"Anomalie détectée: valeur {anomaly_analysis['deviation_type']}",
                "z_score": anomaly_analysis["z_score"],
                "location": location,
                "timestamp": datetime.utcnow().isoformat()
            })
        
        # Alertes de tendance
        if trend_analysis["trend"] == "increasing" and trend_analysis["trend_strength"] > 0.5:
            alerts.append({
                "alert_id": str(uuid.uuid4()),
                "type": AlertType.TREND_WARNING.value,
                "severity": "medium",
                "message": f"Tendance à la hausse détectée pour {sensor_type}",
                "trend_strength": trend_analysis["trend_strength"],
                "location": location,
                "timestamp": datetime.utcnow().isoformat()
            })
        
        return alerts
    
    def _get_hazard_category(self, sensor_type: str) -> HazardCategory:
        """Détermine la catégorie de danger pour un type de capteur"""
        if sensor_type in self.REGULATORY_THRESHOLDS:
            return self.REGULATORY_THRESHOLDS[sensor_type].get(
                "hazard", HazardCategory.PHYSICAL
            )
        
        # Mapping par défaut
        category_map = {
            "temperature": HazardCategory.PHYSICAL,
            "noise": HazardCategory.PHYSICAL,
            "vibration": HazardCategory.PHYSICAL,
            "humidity": HazardCategory.PHYSICAL,
            "co2": HazardCategory.CHEMICAL,
            "co": HazardCategory.CHEMICAL,
            "gas": HazardCategory.CHEMICAL,
            "dust": HazardCategory.CHEMICAL,
            "ergonomic": HazardCategory.ERGONOMIC,
            "stress": HazardCategory.PSYCHOSOCIAL,
        }
        
        return category_map.get(sensor_type, HazardCategory.PHYSICAL)
    
    def _identify_factors(
        self, 
        threshold_analysis: Dict, 
        anomaly_analysis: Dict
    ) -> List[str]:
        """Identifie les facteurs contribuant au risque"""
        factors = []
        
        if threshold_analysis["exceeded"]:
            for violation in threshold_analysis["violations"]:
                factors.append(f"Dépassement de seuil: {violation['type']}")
        
        if anomaly_analysis["is_anomaly"]:
            factors.append(f"Anomalie statistique (z={anomaly_analysis['z_score']:.2f})")
        
        return factors
    
    def _update_history(
        self, 
        value: float, 
        sensor_type: str, 
        location: str
    ):
        """Met à jour l'historique des observations"""
        history_key = f"{sensor_type}_{location}"
        
        if history_key not in self.observation_history:
            self.observation_history[history_key] = []
        
        self.observation_history[history_key].append({
            "value": value,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Limiter la taille de l'historique
        if len(self.observation_history[history_key]) > self.max_history_size:
            self.observation_history[history_key] = \
                self.observation_history[history_key][-self.max_history_size:]
    
    def _generate_rdf(
        self, 
        analysis: RiskAnalysis, 
        input_data: Dict
    ) -> str:
        """Génère un graphe RDF pour l'analyse"""
        g = Graph()
        g.bind("sa", SA)
        g.bind("edgy", EDGY)
        
        # URI de l'analyse
        analysis_uri = SA[f"RiskAnalysis_{analysis.analysis_id}"]
        
        # Type et propriétés
        g.add((analysis_uri, RDF.type, SA.RiskAnalysis))
        g.add((analysis_uri, SA.hasAnalysisId, Literal(analysis.analysis_id)))
        g.add((analysis_uri, SA.hasRiskScore, Literal(analysis.risk_score, datatype=XSD.float)))
        g.add((analysis_uri, SA.hasRiskLevel, Literal(analysis.risk_level.value)))
        g.add((analysis_uri, SA.hasHazardCategory, Literal(analysis.hazard_category.value)))
        g.add((analysis_uri, SA.hasConfidence, Literal(analysis.confidence, datatype=XSD.float)))
        g.add((analysis_uri, SA.hasTimestamp, Literal(analysis.timestamp.isoformat(), datatype=XSD.dateTime)))
        g.add((analysis_uri, SA.analyzedBy, Literal(self.agent_id)))
        
        # Alertes
        g.add((analysis_uri, SA.alertCount, Literal(len(analysis.alerts), datatype=XSD.integer)))
        
        return g.serialize(format="turtle")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques d'analyse"""
        scores = self.state.metrics.get("risk_scores", [])
        return {
            "agent_id": self.agent_id,
            "analyses_performed": self.state.metrics["analyses_performed"],
            "alerts_generated": self.state.metrics["alerts_generated"],
            "critical_risks_detected": self.state.metrics["critical_risks_detected"],
            "average_risk_score": sum(scores) / len(scores) if scores else 0,
            "max_risk_score": max(scores) if scores else 0
        }


# Export
__all__ = [
    "AnalysisAgent",
    "RiskAnalysis",
    "RiskLevel",
    "AlertType",
    "HazardCategory"
]
