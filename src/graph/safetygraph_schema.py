"""
SafetyGraph Schema - Ontologie SST pour Neo4j
EDGY-AgenticX5 | 12 entités, 25+ relations
"""

from enum import Enum
from typing import Any, Dict, List
from dataclasses import dataclass

class NiveauRisque(str, Enum):
    CRITIQUE = "critique"
    ELEVE = "élevé"
    MOYEN = "moyen"
    FAIBLE = "faible"
    MINIMAL = "minimal"

class GraviteIncident(str, Enum):
    DECES = "décès"
    GRAVE = "grave"
    MODERE = "modéré"
    MINEUR = "mineur"
    SANS_ARRET = "sans_arrêt"

class TypeIncident(str, Enum):
    CHUTE_HAUTEUR = "chute_hauteur"
    CHUTE_PLAIN_PIED = "chute_plain_pied"
    COUPURE = "coupure"
    BRULURE = "brûlure"
    ECRASEMENT = "écrasement"
    TMS = "trouble_musculosquelettique"
    COLLISION = "collision"
    AUTRE = "autre"

class TypeZone(str, Enum):
    PRODUCTION = "production"
    ENTREPOT = "entrepôt"
    BUREAU = "bureau"
    CHANTIER = "chantier"

class TypeCapteur(str, Enum):
    TEMPERATURE = "temperature"
    HUMIDITE = "humidite"
    BRUIT = "bruit"
    VIBRATION = "vibration"
    GAZ = "gaz"

@dataclass
class RelationType:
    name: str
    from_label: str
    to_label: str
    properties: List[str]
    description: str

ENTITY_LABELS = [
    "Travailleur", "Zone_Travail", "Equipement", "Incident_CNESST",
    "Near_Miss", "Agent_IA", "Capteur_IoT", "Formation",
    "Procedure_SST", "Norme_ISO", "Document_IRSST", "Evenement"
]

RELATIONS = [
    RelationType("TRAVAILLE_DANS", "Travailleur", "Zone_Travail", ["depuis"], "Affectation"),
    RelationType("UTILISE", "Travailleur", "Equipement", ["frequence"], "Utilisation"),
    RelationType("SURVIENT_DANS", "Incident_CNESST", "Zone_Travail", [], "Lieu incident"),
    RelationType("IMPLIQUE", "Incident_CNESST", "Travailleur", ["role"], "Implication"),
    RelationType("DETECTE_PAR", "Near_Miss", "Agent_IA", ["confiance"], "Détection"),
    RelationType("SURVEILLE", "Capteur_IoT", "Zone_Travail", [], "Surveillance"),
    RelationType("PRECEDE", "Near_Miss", "Incident_CNESST", ["jours"], "Corrélation"),
    RelationType("SIMILAIRE_A", "Incident_CNESST", "Incident_CNESST", ["score"], "Similarité"),
]

def get_entity_labels() -> List[str]:
    return ENTITY_LABELS

def get_relation_types() -> List[str]:
    return [r.name for r in RELATIONS]

def get_ontology_summary() -> Dict[str, Any]:
    return {
        "name": "SafetyGraph SST Ontology",
        "version": "1.0.0",
        "entities": len(ENTITY_LABELS),
        "relations": len(RELATIONS),
        "entity_labels": ENTITY_LABELS,
        "relation_types": get_relation_types()
    }

def get_schema_creation_queries() -> List[str]:
    queries = []
    for label in ENTITY_LABELS:
        prop = "id" if label == "Evenement" else f"{label.lower()}_id"
        queries.append(f"CREATE CONSTRAINT IF NOT EXISTS FOR (n:{label}) REQUIRE n.{prop} IS UNIQUE")
    return queries

__all__ = ["NiveauRisque", "GraviteIncident", "TypeIncident", "TypeZone", "TypeCapteur",
           "get_entity_labels", "get_relation_types", "get_ontology_summary", "get_schema_creation_queries"]
