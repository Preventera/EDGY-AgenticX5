"""
PerceptionAgent - Agent de collecte et perception de données
Inspire de DC01 (Capteurs IoT) et A2 (Observations terrain)
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from .base_agent import BaseAgent, AgentCapability, AgentStatus
from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, XSD


# Namespaces
EDG = Namespace("http://example.org/edg-schema#")
SA = Namespace("http://safety-agentic.preventera.ai/ontology#")
EX = Namespace("http://example.org/data#")


class PerceptionAgent(BaseAgent):
    """
    Agent de perception pour collecter et normaliser les données
    
    Fonctions:
    - Collecte données capteurs IoT
    - Observations terrain
    - Enrichissement contextuel
    - Normalisation format RDF
    """
    
    def __init__(
        self,
        agent_id: str = "perception_001",
        config: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            agent_id=agent_id,
            name="PerceptionAgent",
            config=config or {}
        )
        
        # Configuration spécifique
        self.supported_sensors = config.get("sensors", [
            "temperature", "humidity", "noise", "vibration",
            "air_quality", "light_level", "gas_detector"
        ]) if config else [
            "temperature", "humidity", "noise", "vibration",
            "air_quality", "light_level", "gas_detector"
        ]
        
        # Seuils d'alerte par défaut
        self.alert_thresholds = config.get("thresholds", {
            "temperature": {"min": 5, "max": 35},
            "humidity": {"min": 30, "max": 70},
            "noise": {"max": 85},  # dB
            "vibration": {"max": 5},  # m/s²
            "air_quality": {"min": 0, "max": 50},  # AQI
            "light_level": {"min": 300, "max": 1000}  # lux
        }) if config else {
            "temperature": {"min": 5, "max": 35},
            "humidity": {"min": 30, "max": 70},
            "noise": {"max": 85},
            "vibration": {"max": 5},
            "air_quality": {"min": 0, "max": 50},
            "light_level": {"min": 300, "max": 1000}
        }
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Traiter les données de perception
        
        Args:
            input_data: {
                "source": str,  # "iot_sensor" | "manual_observation"
                "sensor_type": str,
                "value": float,
                "unit": str,
                "location": str,
                "timestamp": str (ISO format)
            }
        
        Returns:
            {
                "observation_id": str,
                "normalized_data": dict,
                "alert_level": str,  # "normal" | "warning" | "critical"
                "rdf_graph": Graph,
                "recommendations": list
            }
        """
        self.update_state(AgentStatus.RUNNING)
        
        try:
            # Valider input
            if not self._validate_input(input_data):
                raise ValueError("Invalid input data format")
            
            # Créer ID observation
            obs_id = f"obs_{self.agent_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # Normaliser données
            normalized = self._normalize_data(input_data)
            
            # Détecter alertes
            alert_level = self._detect_alert(normalized)
            
            # Convertir en RDF
            rdf_graph = self._to_rdf(obs_id, normalized)
            
            # Générer recommandations si alerte
            recommendations = []
            if alert_level != "normal":
                recommendations = self._generate_recommendations(normalized, alert_level)
            
            # Mettre à jour métriques
            self.update_metrics("observations_processed", 
                               self.state.metrics.get("observations_processed", 0) + 1)
            if alert_level != "normal":
                self.update_metrics("alerts_detected",
                                   self.state.metrics.get("alerts_detected", 0) + 1)
            
            self.update_state (AgentStatus.COMPLETED)
            
            return {
                "observation_id": obs_id,
                "normalized_data": normalized,
                "alert_level": alert_level,
                "rdf_graph": rdf_graph,
                "recommendations": recommendations,
                "agent_id": self.agent_id,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.update_state(AgentStatus.ERROR)
            return {
                "error": str(e),
                "agent_id": self.agent_id,
                "status": "failed"
            }
    
    def _validate_input(self, data: Dict[str, Any]) -> bool:
        """Valider format des données d'entrée"""
        required_fields = ["source", "sensor_type", "value", "location"]
        return all(field in data for field in required_fields)
    
    def _normalize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normaliser les données selon le type de capteur"""
        normalized = {
            "source": data["source"],
            "sensor_type": data["sensor_type"],
            "raw_value": data["value"],
            "unit": data.get("unit", ""),
            "location": data["location"],
            "timestamp": data.get("timestamp", datetime.now().isoformat())
        }
        
        # Normaliser la valeur selon le type
        sensor_type = data["sensor_type"]
        value = float(data["value"])
        
        # Ajouter des métadonnées contextuelles
        normalized["context"] = {
            "is_supported": sensor_type in self.supported_sensors,
            "has_threshold": sensor_type in self.alert_thresholds
        }
        
        return normalized
    
    def _detect_alert(self, data: Dict[str, Any]) -> str:
        """Détecter niveau d'alerte"""
        sensor_type = data["sensor_type"]
        value = data["raw_value"]
        
        if sensor_type not in self.alert_thresholds:
            return "normal"
        
        thresholds = self.alert_thresholds[sensor_type]
        
        # Vérifier min/max
        if "min" in thresholds and value < thresholds["min"]:
            return "warning" if value > thresholds["min"] * 0.8 else "critical"
        
        if "max" in thresholds and value > thresholds["max"]:
            return "warning" if value < thresholds["max"] * 1.2 else "critical"
        
        return "normal"
    
    def _to_rdf(self, obs_id: str, data: Dict[str, Any]) -> Graph:
        """Convertir observation en RDF"""
        g = Graph()
        
        # URI observation
        obs_uri = EX[obs_id]
        
        # Triples RDF
        g.add((obs_uri, RDF.type, SA.Observation))
        g.add((obs_uri, SA.observedBy, EX[self.agent_id]))
        g.add((obs_uri, SA.hasConfidence, Literal(0.95, datatype=XSD.float)))
        g.add((obs_uri, EDG.hasName, Literal(f"Observation {data['sensor_type']}")))
        
        # Données capteur
        g.add((obs_uri, SA.sensorType, Literal(data["sensor_type"])))
        g.add((obs_uri, SA.rawValue, Literal(data["raw_value"], datatype=XSD.float)))
        g.add((obs_uri, SA.location, Literal(data["location"])))
        g.add((obs_uri, SA.timestamp, Literal(data["timestamp"], datatype=XSD.dateTime)))
        
        return g
    
    def _generate_recommendations(
        self,
        data: Dict[str, Any],
        alert_level: str
    ) -> List[str]:
        """Générer recommandations selon le type d'alerte"""
        recommendations = []
        sensor_type = data["sensor_type"]
        value = data["raw_value"]
        
        if sensor_type == "temperature":
            if value > self.alert_thresholds["temperature"]["max"]:
                recommendations.append("Température excessive détectée. Vérifier ventilation.")
                recommendations.append("Prévoir pauses fréquentes pour travailleurs.")
            elif value < self.alert_thresholds["temperature"]["min"]:
                recommendations.append("Température trop basse. Vérifier chauffage.")
        
        elif sensor_type == "noise":
            if value > self.alert_thresholds["noise"]["max"]:
                recommendations.append("Niveau sonore dangereux. Port de protection auditive obligatoire.")
                recommendations.append("Considérer insonorisation de la zone.")
        
        elif sensor_type == "air_quality":
            if value > self.alert_thresholds["air_quality"]["max"]:
                recommendations.append("Qualité d'air dégradée. Augmenter ventilation.")
                recommendations.append("Vérifier sources de pollution.")
        
        # Recommandation générique
        if alert_level == "critical":
            recommendations.append("ALERTE CRITIQUE: Évacuer la zone immédiatement.")
        
        return recommendations