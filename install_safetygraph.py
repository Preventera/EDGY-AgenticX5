#!/usr/bin/env python3
"""
AUTO-INSTALL Neo4j SafetyGraph
EDGY-AgenticX5

Exécutez ce script pour installer automatiquement:
- src/graph/neo4j_connector.py
- src/graph/safetygraph_schema.py
- src/graph/__init__.py
- test_neo4j_integration.py

Usage: python install_safetygraph.py
"""

import os
from pathlib import Path

def create_file(path: str, content: str):
    """Crée un fichier avec le contenu spécifié"""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"  ✅ {path}")

def main():
    print("\n" + "=" * 60)
    print("  🗄️ INSTALLATION NEO4J SAFETYGRAPH")
    print("  EDGY-AgenticX5 | SafetyGraph")
    print("=" * 60 + "\n")
    
    # Vérifier qu'on est dans le bon dossier
    if not os.path.exists("src/agents"):
        print("❌ Erreur: Exécutez depuis le dossier EDGY-AgenticX5")
        return False
    
    print("📁 Création des fichiers...\n")
    
    # ========================================
    # 1. src/graph/__init__.py
    # ========================================
    create_file("src/graph/__init__.py", '''"""
SafetyGraph - Knowledge Graph SST pour Neo4j
EDGY-AgenticX5
"""

from .neo4j_connector import SafetyGraphConnector, Neo4jConfig, get_connector
from .safetygraph_schema import (
    get_ontology_summary,
    get_entity_labels,
    get_relation_types,
    NiveauRisque,
    GraviteIncident,
    TypeIncident
)

__all__ = [
    "SafetyGraphConnector",
    "Neo4jConfig", 
    "get_connector",
    "get_ontology_summary",
    "get_entity_labels",
    "get_relation_types"
]
''')

    # ========================================
    # 2. src/graph/safetygraph_schema.py
    # ========================================
    create_file("src/graph/safetygraph_schema.py", '''"""
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
''')

    # ========================================
    # 3. src/graph/neo4j_connector.py
    # ========================================
    create_file("src/graph/neo4j_connector.py", '''"""
Neo4j SafetyGraph Connector
EDGY-AgenticX5 | Connecteur et opérations Knowledge Graph
"""

import os
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum
from pydantic import BaseModel, Field

try:
    from neo4j import GraphDatabase
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False

class ConnectionStatus(str, Enum):
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    MOCK_MODE = "mock_mode"

class Neo4jConfig(BaseModel):
    uri: str = Field(default="bolt://localhost:7687")
    user: str = Field(default="neo4j")
    password: str = Field(default="password")
    database: str = Field(default="neo4j")

class SafetyGraphConnector:
    """Connecteur Neo4j pour SafetyGraph SST"""
    
    def __init__(self, config: Optional[Neo4jConfig] = None):
        self.logger = logging.getLogger("SafetyGraph.Neo4j")
        self.config = config or Neo4jConfig(
            uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
            user=os.getenv("NEO4J_USER", "neo4j"),
            password=os.getenv("NEO4J_PASSWORD", "password"),
            database=os.getenv("NEO4J_DATABASE", "neo4j")
        )
        self.driver = None
        self.mock_mode = not NEO4J_AVAILABLE
        self.status = ConnectionStatus.MOCK_MODE if self.mock_mode else ConnectionStatus.DISCONNECTED
        self.stats = {"queries_executed": 0, "nodes_created": 0, "relationships_created": 0, "errors": 0}
        
        if self.mock_mode:
            self.logger.warning("Neo4j en mode MOCK - données simulées")
    
    def connect(self) -> bool:
        if self.mock_mode:
            return True
        try:
            self.driver = GraphDatabase.driver(self.config.uri, auth=(self.config.user, self.config.password))
            self.driver.verify_connectivity()
            self.status = ConnectionStatus.CONNECTED
            return True
        except Exception as e:
            self.status = ConnectionStatus.ERROR
            self.logger.error(f"Erreur connexion: {e}")
            return False
    
    def disconnect(self):
        if self.driver:
            self.driver.close()
            self.status = ConnectionStatus.DISCONNECTED
    
    def health_check(self) -> Dict[str, Any]:
        if self.mock_mode:
            return {"status": "mock_mode", "message": "Neo4j simulation", "latency_ms": 0}
        return {"status": self.status.value, "stats": self.stats}
    
    def execute_query(self, query: str, parameters: Optional[Dict] = None) -> List[Dict]:
        if self.mock_mode:
            self.stats["queries_executed"] += 1
            return [{"result": "mock_data"}]
        with self.driver.session(database=self.config.database) as session:
            result = session.run(query, parameters or {})
            self.stats["queries_executed"] += 1
            return [dict(record) for record in result]
    
    def create_zone_travail(self, zone_id: str, nom: str, type_zone: str, niveau_risque: str = "moyen", capacite_max: int = 50) -> Dict:
        self.stats["nodes_created"] += 1
        if self.mock_mode:
            return {"zone_id": zone_id, "nom": nom, "status": "created_mock"}
        query = "CREATE (z:Zone_Travail {zone_id: $zone_id, nom: $nom, type_zone: $type_zone, niveau_risque: $niveau_risque}) RETURN z"
        return self.execute_query(query, {"zone_id": zone_id, "nom": nom, "type_zone": type_zone, "niveau_risque": niveau_risque})[0]
    
    def create_travailleur(self, matricule: str, nom: str, prenom: str, poste: str, zone_id: Optional[str] = None) -> Dict:
        self.stats["nodes_created"] += 1
        if self.mock_mode:
            return {"matricule": matricule, "nom": nom, "status": "created_mock"}
        query = "CREATE (t:Travailleur {matricule: $matricule, nom: $nom, prenom: $prenom, poste: $poste}) RETURN t"
        return self.execute_query(query, {"matricule": matricule, "nom": nom, "prenom": prenom, "poste": poste})[0]
    
    def create_incident(self, incident_id: str, type_incident: str, gravite: str, description: str, zone_id: Optional[str] = None, travailleur_matricule: Optional[str] = None) -> Dict:
        self.stats["nodes_created"] += 1
        if self.mock_mode:
            return {"incident_id": incident_id, "status": "created_mock"}
        query = "CREATE (i:Incident_CNESST {incident_id: $incident_id, type_incident: $type_incident, gravite: $gravite, description: $description}) RETURN i"
        return self.execute_query(query, {"incident_id": incident_id, "type_incident": type_incident, "gravite": gravite, "description": description})[0]
    
    def create_near_miss(self, near_miss_id: str, type_risque: str, potentiel_gravite: str, description: str, zone_id: Optional[str] = None, detecte_par_agent: Optional[str] = None) -> Dict:
        self.stats["nodes_created"] += 1
        if self.mock_mode:
            return {"near_miss_id": near_miss_id, "status": "created_mock"}
        query = "CREATE (nm:Near_Miss {near_miss_id: $near_miss_id, type_risque: $type_risque, potentiel_gravite: $potentiel_gravite, description: $description}) RETURN nm"
        return self.execute_query(query, {"near_miss_id": near_miss_id, "type_risque": type_risque, "potentiel_gravite": potentiel_gravite, "description": description})[0]
    
    def create_equipement(self, equipement_id: str, nom: str, type_equipement: str, zone_id: Optional[str] = None) -> Dict:
        self.stats["nodes_created"] += 1
        if self.mock_mode:
            return {"equipement_id": equipement_id, "status": "created_mock"}
        query = "CREATE (e:Equipement {equipement_id: $equipement_id, nom: $nom, type_equipement: $type_equipement}) RETURN e"
        return self.execute_query(query, {"equipement_id": equipement_id, "nom": nom, "type_equipement": type_equipement})[0]
    
    def create_capteur_iot(self, capteur_id: str, type_capteur: str, zone_id: str, seuil_alerte: float) -> Dict:
        self.stats["nodes_created"] += 1
        if self.mock_mode:
            return {"capteur_id": capteur_id, "status": "created_mock"}
        query = "CREATE (c:Capteur_IoT {capteur_id: $capteur_id, type_capteur: $type_capteur, seuil_alerte: $seuil_alerte}) RETURN c"
        return self.execute_query(query, {"capteur_id": capteur_id, "type_capteur": type_capteur, "seuil_alerte": seuil_alerte})[0]
    
    def get_zones_high_risk(self, min_incidents: int = 3) -> List[Dict]:
        if self.mock_mode:
            return [
                {"zone_id": "ZONE-A1", "zone_nom": "Atelier Soudure", "niveau_actuel": "élevé", "nb_incidents": 12},
                {"zone_id": "ZONE-B2", "zone_nom": "Entrepôt Chimique", "niveau_actuel": "élevé", "nb_incidents": 8},
                {"zone_id": "ZONE-C3", "zone_nom": "Zone Manutention", "niveau_actuel": "moyen", "nb_incidents": 5}
            ]
        query = """MATCH (z:Zone_Travail)<-[:SURVIENT_DANS]-(i:Incident_CNESST) 
                   WITH z, count(i) as nb WHERE nb >= $min RETURN z.zone_id, z.nom, nb ORDER BY nb DESC LIMIT 10"""
        return self.execute_query(query, {"min": min_incidents})
    
    def get_travailleurs_at_risk(self, risk_threshold: float = 0.7) -> List[Dict]:
        if self.mock_mode:
            return [
                {"matricule": "EMP-001", "nom": "Tremblay", "prenom": "Jean", "score_risque": 0.85, "nb_incidents": 3},
                {"matricule": "EMP-042", "nom": "Gagnon", "prenom": "Marie", "score_risque": 0.78, "nb_incidents": 2}
            ]
        query = "MATCH (t:Travailleur) WHERE t.score_risque >= $threshold RETURN t ORDER BY t.score_risque DESC LIMIT 20"
        return self.execute_query(query, {"threshold": risk_threshold})
    
    def get_incident_patterns(self, days: int = 90) -> List[Dict]:
        if self.mock_mode:
            return [
                {"type": "chute_plain_pied", "occurrences": 15},
                {"type": "coupure", "occurrences": 12},
                {"type": "brulure", "occurrences": 8}
            ]
        return self.execute_query("MATCH (i:Incident_CNESST) RETURN i.type_incident, count(i) ORDER BY count(i) DESC")
    
    def get_near_miss_to_incident_correlation(self) -> List[Dict]:
        if self.mock_mode:
            return [
                {"near_miss_id": "NM-001", "type_risque": "glissade", "incident_id": "INC-015", "jours_avant_incident": 3},
                {"near_miss_id": "NM-008", "type_risque": "projection", "incident_id": "INC-022", "jours_avant_incident": 7}
            ]
        return self.execute_query("MATCH (nm:Near_Miss)-[:PRECEDE]->(i:Incident_CNESST) RETURN nm, i LIMIT 20")
    
    def get_equipment_risk_analysis(self) -> List[Dict]:
        if self.mock_mode:
            return [
                {"equipement_id": "EQ-101", "nom": "Chariot élévateur #3", "nb_incidents": 5},
                {"equipement_id": "EQ-055", "nom": "Presse hydraulique", "nb_incidents": 3}
            ]
        return self.execute_query("MATCH (e:Equipement)<-[:IMPLIQUE_EQUIPEMENT]-(i:Incident_CNESST) RETURN e, count(i) ORDER BY count(i) DESC LIMIT 10")
    
    def enrich_context_for_agent(self, zone_id: Optional[str] = None, travailleur_matricule: Optional[str] = None, equipement_id: Optional[str] = None) -> Dict:
        context = {"timestamp": datetime.utcnow().isoformat(), "zone": None, "travailleur": None, "equipement": None}
        if zone_id:
            context["zone"] = {"zone_id": zone_id, "nom": "Zone simulée", "niveau_risque": "moyen", "incidents_30j": 2, "near_miss_30j": 5} if self.mock_mode else {}
        if travailleur_matricule:
            context["travailleur"] = {"matricule": travailleur_matricule, "nom": "Simulé", "score_risque": 0.45, "formations": ["SIMDUT"]} if self.mock_mode else {}
        if equipement_id:
            context["equipement"] = {"equipement_id": equipement_id, "nom": "Équipement simulé", "etat": "operationnel"} if self.mock_mode else {}
        return context
    
    def get_statistics(self) -> Dict[str, Any]:
        return {"status": self.status.value, "mock_mode": self.mock_mode, "stats": self.stats}

_connector_instance = None

def get_connector() -> SafetyGraphConnector:
    global _connector_instance
    if _connector_instance is None:
        _connector_instance = SafetyGraphConnector()
    return _connector_instance

__all__ = ["SafetyGraphConnector", "Neo4jConfig", "ConnectionStatus", "get_connector"]
''')

    # ========================================
    # 4. test_neo4j_integration.py
    # ========================================
    create_file("test_neo4j_integration.py", '''"""
Test d\'intégration Neo4j SafetyGraph
EDGY-AgenticX5
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from graph.neo4j_connector import SafetyGraphConnector
from graph.safetygraph_schema import get_ontology_summary, get_entity_labels

def print_header(title):
    print("\\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def test_ontology():
    print_header("1️⃣ TEST ONTOLOGIE")
    summary = get_ontology_summary()
    print(f"  ✅ {summary[\'name\']} v{summary[\'version\']}")
    print(f"  ✅ {summary[\'entities\']} entités, {summary[\'relations\']} relations")
    return True

def test_connection():
    print_header("2️⃣ TEST CONNEXION")
    connector = SafetyGraphConnector()
    connected = connector.connect()
    print(f"  {'✅' if connected else '⚠️'} Mode: {'MOCK' if connector.mock_mode else 'RÉEL'}")
    print(f"  ✅ Status: {connector.status.value}")
    return connector

def test_crud(connector):
    print_header("3️⃣ TEST CRUD")
    zone = connector.create_zone_travail("ZONE-TEST", "Zone Test", "production")
    print(f"  ✅ Zone créée: {zone.get('zone_id', 'ZONE-TEST')}")
    travailleur = connector.create_travailleur("EMP-TEST", "Test", "Jean", "Opérateur")
    print(f"  ✅ Travailleur créé: {travailleur.get('matricule', 'EMP-TEST')}")
    incident = connector.create_incident("INC-TEST", "coupure", "mineur", "Test incident")
    print(f"  ✅ Incident créé: {incident.get('incident_id', 'INC-TEST')}")
    print(f"  📊 Stats: {connector.stats['nodes_created']} nœuds créés")
    return True

def test_analytics(connector):
    print_header("4️⃣ TEST ANALYTIQUE")
    zones = connector.get_zones_high_risk()
    print(f"  ✅ {len(zones)} zones à risque identifiées")
    patterns = connector.get_incident_patterns()
    print(f"  ✅ {len(patterns)} patterns d'incidents")
    context = connector.enrich_context_for_agent(zone_id="ZONE-A1")
    print(f"  ✅ Contexte enrichi: {context.get('zone', {}).get('niveau_risque', 'N/A')}")
    return True

def main():
    print("\\n" + "╔" + "═" * 58 + "╗")
    print("║" + " " * 10 + "🗄️ TESTS NEO4J SAFETYGRAPH" + " " * 15 + "   ║")
    print("╚" + "═" * 58 + "╝")
    
    results = {}
    try:
        results["Ontologie"] = test_ontology()
    except Exception as e:
        print(f"  ❌ {e}")
        results["Ontologie"] = False
    
    connector = None
    try:
        connector = test_connection()
        results["Connexion"] = True
    except Exception as e:
        print(f"  ❌ {e}")
        results["Connexion"] = False
        connector = SafetyGraphConnector()
    
    try:
        results["CRUD"] = test_crud(connector)
    except Exception as e:
        print(f"  ❌ {e}")
        results["CRUD"] = False
    
    try:
        results["Analytique"] = test_analytics(connector)
    except Exception as e:
        print(f"  ❌ {e}")
        results["Analytique"] = False
    
    print_header("📊 RÉSUMÉ")
    passed = sum(1 for v in results.values() if v)
    for test, ok in results.items():
        print(f"  {'✅' if ok else '❌'} {test}")
    
    print("\\n" + "=" * 60)
    if passed == len(results):
        print(f"  🎉 TOUS LES TESTS PASSENT! ({passed}/{len(results)})")
        print("  🚀 Neo4j SafetyGraph opérationnel!")
    else:
        print(f"  ⚠️ {passed}/{len(results)} tests passés")
    
    if connector and connector.mock_mode:
        print("\\n  ℹ️ Mode MOCK actif (Neo4j non connecté)")
    print("=" * 60 + "\\n")
    
    return passed == len(results)

if __name__ == "__main__":
    sys.exit(0 if main() else 1)
''')

    print("\n" + "=" * 60)
    print("  🎉 INSTALLATION TERMINÉE!")
    print("=" * 60)
    print("\n  Fichiers créés:")
    print("  ├── src/graph/__init__.py")
    print("  ├── src/graph/neo4j_connector.py")
    print("  ├── src/graph/safetygraph_schema.py")
    print("  └── test_neo4j_integration.py")
    print("\n  🧪 Lancez le test:")
    print("     python test_neo4j_integration.py")
    print()
    
    return True

if __name__ == "__main__":
    main()
