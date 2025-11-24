"""
NormalizationAgent - Agent de Normalisation des Données
EDGY-AgenticX5 | SafetyGraph

Responsabilités:
- Normaliser les données brutes des capteurs
- Convertir les unités vers standards internationaux
- Valider la qualité des données
- Enrichir avec métadonnées contextuelles
- Générer RDF normalisé pour le Knowledge Graph
"""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum

from pydantic import BaseModel, Field
from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, XSD

# Import depuis le module agents
from agents.base_agent import BaseAgent, AgentStatus, AgentCapability


# Namespaces RDF
SA = Namespace("http://safetyagentic.org/ontology#")
EDGY = Namespace("http://edgy.org/schema#")
SSN = Namespace("http://www.w3.org/ns/ssn/")
SOSA = Namespace("http://www.w3.org/ns/sosa/")


class DataQuality(str, Enum):
    """Niveaux de qualité des données"""
    EXCELLENT = "excellent"      # > 95% fiabilité
    GOOD = "good"               # 80-95% fiabilité
    ACCEPTABLE = "acceptable"   # 60-80% fiabilité
    POOR = "poor"               # 40-60% fiabilité
    INVALID = "invalid"         # < 40% fiabilité


class UnitSystem(str, Enum):
    """Systèmes d'unités supportés"""
    SI = "SI"                   # Système International
    IMPERIAL = "imperial"       # Système Impérial
    CUSTOM = "custom"           # Unités personnalisées


class NormalizedData(BaseModel):
    """Modèle de données normalisées"""
    
    normalization_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    original_data: Dict[str, Any]
    normalized_value: float
    normalized_unit: str
    quality_score: float = Field(ge=0.0, le=1.0)
    quality_level: DataQuality
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source_agent_id: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class NormalizationAgent(BaseAgent):
    """
    Agent de Normalisation (N1) - Architecture AgenticX5
    
    Cet agent est responsable de:
    1. Recevoir les données brutes du PerceptionAgent
    2. Normaliser les valeurs selon le Système International (SI)
    3. Évaluer la qualité des données
    4. Enrichir avec métadonnées contextuelles
    5. Produire des triples RDF normalisés
    
    Position dans le pipeline:
    PerceptionAgent → [NormalizationAgent] → AnalysisAgent
    """
    
    # Tables de conversion d'unités vers SI
    UNIT_CONVERSIONS = {
        # Température
        "°F": {"to_si": lambda x: (x - 32) * 5/9, "si_unit": "°C"},
        "°C": {"to_si": lambda x: x, "si_unit": "°C"},
        "K": {"to_si": lambda x: x - 273.15, "si_unit": "°C"},
        
        # Pression
        "psi": {"to_si": lambda x: x * 6894.76, "si_unit": "Pa"},
        "bar": {"to_si": lambda x: x * 100000, "si_unit": "Pa"},
        "Pa": {"to_si": lambda x: x, "si_unit": "Pa"},
        "kPa": {"to_si": lambda x: x * 1000, "si_unit": "Pa"},
        "atm": {"to_si": lambda x: x * 101325, "si_unit": "Pa"},
        
        # Bruit
        "dB": {"to_si": lambda x: x, "si_unit": "dB"},
        "dBA": {"to_si": lambda x: x, "si_unit": "dB"},
        
        # Humidité
        "%": {"to_si": lambda x: x, "si_unit": "%"},
        "%RH": {"to_si": lambda x: x, "si_unit": "%"},
        
        # Vibration
        "mm/s": {"to_si": lambda x: x / 1000, "si_unit": "m/s"},
        "m/s": {"to_si": lambda x: x, "si_unit": "m/s"},
        "g": {"to_si": lambda x: x * 9.81, "si_unit": "m/s²"},
        
        # Qualité de l'air
        "ppm": {"to_si": lambda x: x, "si_unit": "ppm"},
        "ppb": {"to_si": lambda x: x / 1000, "si_unit": "ppm"},
        "mg/m³": {"to_si": lambda x: x, "si_unit": "mg/m³"},
        
        # Luminosité
        "lux": {"to_si": lambda x: x, "si_unit": "lux"},
        "lx": {"to_si": lambda x: x, "si_unit": "lux"},
        "fc": {"to_si": lambda x: x * 10.764, "si_unit": "lux"},  # foot-candles
    }
    
    # Plages valides par type de capteur (pour validation qualité)
    VALID_RANGES = {
        "temperature": {"min": -50, "max": 100, "unit": "°C"},
        "humidity": {"min": 0, "max": 100, "unit": "%"},
        "pressure": {"min": 80000, "max": 120000, "unit": "Pa"},
        "noise": {"min": 0, "max": 150, "unit": "dB"},
        "vibration": {"min": 0, "max": 100, "unit": "m/s"},
        "air_quality": {"min": 0, "max": 5000, "unit": "ppm"},
        "light_level": {"min": 0, "max": 100000, "unit": "lux"},
        "gas_concentration": {"min": 0, "max": 10000, "unit": "ppm"},
    }
    
    def __init__(
        self,
        agent_id: str = "normalization_001",
        config: Optional[Dict[str, Any]] = None
    ):
        """Initialise le NormalizationAgent"""
        super().__init__(
            agent_id=agent_id,
            name="NormalizationAgent",
            config=config or {}
        )
        
        # Configuration spécifique
        self.default_unit_system = UnitSystem.SI
        self.quality_threshold = 0.6  # Seuil minimum de qualité
        self.auto_reject_invalid = True
        
        # Métriques
        self.state.metrics = {
            "data_normalized": 0,
            "data_rejected": 0,
            "quality_scores": [],
            "conversion_errors": 0
        }
        
        self.logger.info(f"NormalizationAgent {agent_id} initialisé")
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Traite et normalise les données d'entrée.
        
        Args:
            input_data: Données brutes du PerceptionAgent
                - value: Valeur brute
                - unit: Unité d'origine
                - sensor_type: Type de capteur
                - source_agent_id: ID de l'agent source
                - timestamp: Horodatage (optionnel)
                - metadata: Métadonnées additionnelles (optionnel)
        
        Returns:
            Dict contenant:
                - normalization_id: ID unique
                - normalized_value: Valeur normalisée (SI)
                - normalized_unit: Unité SI
                - quality_score: Score de qualité (0-1)
                - quality_level: Niveau de qualité
                - rdf_graph: Graphe RDF sérialisé
                - status: Statut du traitement
        """
        self.update_state(AgentStatus.RUNNING)
        
        try:
            # Extraire les données
            raw_value = input_data.get("value")
            raw_unit = input_data.get("unit", "")
            sensor_type = input_data.get("sensor_type", "unknown")
            source_agent = input_data.get("source_agent_id", "unknown")
            
            # Validation basique
            if raw_value is None:
                raise ValueError("Valeur manquante dans les données d'entrée")
            
            # 1. Conversion d'unité vers SI
            normalized_value, normalized_unit = self._convert_to_si(
                raw_value, raw_unit
            )
            
            # 2. Évaluation de la qualité
            quality_score = self._evaluate_quality(
                normalized_value, normalized_unit, sensor_type
            )
            quality_level = self._get_quality_level(quality_score)
            
            # 3. Vérifier si données acceptables
            if self.auto_reject_invalid and quality_level == DataQuality.INVALID:
                self.state.metrics["data_rejected"] += 1
                self.update_state(AgentStatus.COMPLETED)
                return {
                    "status": "rejected",
                    "reason": "Data quality below threshold",
                    "quality_score": quality_score,
                    "quality_level": quality_level.value,
                    "agent_id": self.agent_id
                }
            
            # 4. Créer l'objet normalisé
            normalized = NormalizedData(
                original_data=input_data,
                normalized_value=normalized_value,
                normalized_unit=normalized_unit,
                quality_score=quality_score,
                quality_level=quality_level,
                source_agent_id=source_agent,
                metadata={
                    "sensor_type": sensor_type,
                    "conversion_applied": raw_unit != normalized_unit,
                    "original_unit": raw_unit,
                    "processing_agent": self.agent_id
                }
            )
            
            # 5. Générer RDF
            rdf_graph = self._generate_rdf(normalized, sensor_type)
            
            # 6. Mettre à jour les métriques
            self.state.metrics["data_normalized"] += 1
            self.state.metrics["quality_scores"].append(quality_score)
            
            self.update_state(AgentStatus.COMPLETED)
            
            return {
                "status": "success",
                "normalization_id": normalized.normalization_id,
                "normalized_value": normalized.normalized_value,
                "normalized_unit": normalized.normalized_unit,
                "quality_score": normalized.quality_score,
                "quality_level": normalized.quality_level.value,
                "rdf_graph": rdf_graph,
                "metadata": normalized.metadata,
                "agent_id": self.agent_id,
                "timestamp": normalized.timestamp.isoformat()
            }
            
        except Exception as e:
            self.state.metrics["conversion_errors"] += 1
            self.update_state(AgentStatus.ERROR)
            self.logger.error(f"Erreur de normalisation: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "agent_id": self.agent_id
            }
    
    def _convert_to_si(self, value: float, unit: str) -> tuple:
        """
        Convertit une valeur vers le Système International.
        
        Args:
            value: Valeur à convertir
            unit: Unité d'origine
            
        Returns:
            Tuple (valeur_si, unité_si)
        """
        if unit in self.UNIT_CONVERSIONS:
            conversion = self.UNIT_CONVERSIONS[unit]
            si_value = conversion["to_si"](value)
            si_unit = conversion["si_unit"]
            return si_value, si_unit
        else:
            # Unité inconnue, retourner telle quelle
            self.logger.warning(f"Unité non reconnue: {unit}")
            return value, unit
    
    def _evaluate_quality(
        self, 
        value: float, 
        unit: str, 
        sensor_type: str
    ) -> float:
        """
        Évalue la qualité des données normalisées.
        
        Critères:
        - Valeur dans les plages attendues
        - Cohérence avec le type de capteur
        - Absence d'anomalies statistiques
        
        Returns:
            Score de qualité entre 0.0 et 1.0
        """
        score = 1.0
        
        # Vérifier les plages valides
        if sensor_type in self.VALID_RANGES:
            range_info = self.VALID_RANGES[sensor_type]
            min_val = range_info["min"]
            max_val = range_info["max"]
            
            if value < min_val or value > max_val:
                # Hors plage - pénalité proportionnelle à l'écart
                if value < min_val:
                    deviation = (min_val - value) / (max_val - min_val)
                else:
                    deviation = (value - max_val) / (max_val - min_val)
                
                score -= min(0.5, deviation * 0.5)
            
            # Bonus si proche du centre de la plage (valeur "normale")
            center = (min_val + max_val) / 2
            normalized_position = abs(value - center) / (max_val - min_val)
            if normalized_position < 0.3:
                score += 0.1
        
        # Pénalité pour valeurs extrêmes (possibles erreurs de capteur)
        if value == 0 and sensor_type not in ["humidity"]:
            score -= 0.2
        
        # Limiter entre 0 et 1
        return max(0.0, min(1.0, score))
    
    def _get_quality_level(self, score: float) -> DataQuality:
        """Détermine le niveau de qualité à partir du score"""
        if score >= 0.95:
            return DataQuality.EXCELLENT
        elif score >= 0.80:
            return DataQuality.GOOD
        elif score >= 0.60:
            return DataQuality.ACCEPTABLE
        elif score >= 0.40:
            return DataQuality.POOR
        else:
            return DataQuality.INVALID
    
    def _generate_rdf(
        self, 
        normalized: NormalizedData, 
        sensor_type: str
    ) -> str:
        """
        Génère un graphe RDF pour les données normalisées.
        
        Returns:
            Graphe RDF sérialisé en Turtle
        """
        g = Graph()
        
        # Bindings des namespaces
        g.bind("sa", SA)
        g.bind("edgy", EDGY)
        g.bind("ssn", SSN)
        g.bind("sosa", SOSA)
        
        # URI de l'observation normalisée
        norm_uri = SA[f"NormalizedObservation_{normalized.normalization_id}"]
        
        # Type et propriétés de base
        g.add((norm_uri, RDF.type, SA.NormalizedObservation))
        g.add((norm_uri, SA.hasNormalizationId, Literal(normalized.normalization_id)))
        g.add((norm_uri, SA.hasNormalizedValue, Literal(normalized.normalized_value, datatype=XSD.float)))
        g.add((norm_uri, SA.hasNormalizedUnit, Literal(normalized.normalized_unit)))
        g.add((norm_uri, SA.hasQualityScore, Literal(normalized.quality_score, datatype=XSD.float)))
        g.add((norm_uri, SA.hasQualityLevel, Literal(normalized.quality_level.value)))
        g.add((norm_uri, SA.hasTimestamp, Literal(normalized.timestamp.isoformat(), datatype=XSD.dateTime)))
        g.add((norm_uri, SA.processedBy, Literal(self.agent_id)))
        g.add((norm_uri, SA.sourceAgent, Literal(normalized.source_agent_id)))
        
        # Lien avec le type de capteur
        sensor_uri = SA[f"SensorType_{sensor_type}"]
        g.add((norm_uri, SA.fromSensorType, sensor_uri))
        
        # Métadonnées de conversion
        if normalized.metadata.get("conversion_applied"):
            g.add((norm_uri, SA.originalUnit, Literal(normalized.metadata["original_unit"])))
            g.add((norm_uri, SA.conversionApplied, Literal(True, datatype=XSD.boolean)))
        
        return g.serialize(format="turtle")
    
    def get_average_quality(self) -> float:
        """Retourne le score de qualité moyen des données traitées"""
        scores = self.state.metrics.get("quality_scores", [])
        if not scores:
            return 0.0
        return sum(scores) / len(scores)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques de normalisation"""
        return {
            "agent_id": self.agent_id,
            "data_normalized": self.state.metrics["data_normalized"],
            "data_rejected": self.state.metrics["data_rejected"],
            "conversion_errors": self.state.metrics["conversion_errors"],
            "average_quality": self.get_average_quality(),
            "acceptance_rate": self._calculate_acceptance_rate()
        }
    
    def _calculate_acceptance_rate(self) -> float:
        """Calcule le taux d'acceptation des données"""
        total = (
            self.state.metrics["data_normalized"] + 
            self.state.metrics["data_rejected"]
        )
        if total == 0:
            return 1.0
        return self.state.metrics["data_normalized"] / total


# Export des classes
__all__ = [
    "NormalizationAgent",
    "NormalizedData", 
    "DataQuality",
    "UnitSystem"
]
