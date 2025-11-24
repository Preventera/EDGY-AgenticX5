"""
Neo4j SafetyGraph Connector
EDGY-AgenticX5 | Connecteur et opérations Knowledge Graph

CORRIGÉ: Basculement automatique en mode MOCK si Neo4j non disponible
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
    """Connecteur Neo4j pour SafetyGraph SST
    
    Fonctionnalités:
    - Connexion à Neo4j avec pool de connexions
    - Basculement automatique en mode MOCK si Neo4j indisponible
    - Opérations CRUD sur les entités SST
    - Requêtes analytiques prédéfinies
    - Enrichissement contextuel pour les agents IA
    """
    
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
        self.stats = {
            "queries_executed": 0, 
            "nodes_created": 0, 
            "relationships_created": 0, 
            "errors": 0
        }
        
        if self.mock_mode:
            self.logger.warning("Neo4j driver non installé - Mode MOCK activé")
    
    def connect(self) -> bool:
        """
        Établit la connexion à Neo4j.
        Bascule automatiquement en mode MOCK si la connexion échoue.
        
        Returns:
            True si connecté (réel ou mock), False uniquement en cas d'erreur critique
        """
        if self.mock_mode:
            self.logger.info("Mode MOCK actif - pas de connexion Neo4j")
            return True
        
        try:
            self.driver = GraphDatabase.driver(
                self.config.uri, 
                auth=(self.config.user, self.config.password)
            )
            self.driver.verify_connectivity()
            self.status = ConnectionStatus.CONNECTED
            self.logger.info(f"✅ Connecté à Neo4j: {self.config.uri}")
            return True
            
        except Exception as e:
            # CORRECTION: Basculer en mode MOCK au lieu d'échouer
            self.logger.warning(f"Neo4j non disponible, activation mode MOCK: {e}")
            self.mock_mode = True
            self.status = ConnectionStatus.MOCK_MODE
            self.driver = None
            return True  # Retourner True pour continuer en mock
    
    def disconnect(self):
        """Ferme la connexion Neo4j."""
        if self.driver:
            self.driver.close()
            self.driver = None
        self.status = ConnectionStatus.DISCONNECTED
    
    def health_check(self) -> Dict[str, Any]:
        """Vérifie l'état de la connexion."""
        if self.mock_mode:
            return {
                "status": "mock_mode", 
                "message": "Neo4j simulation - données mockées",
                "latency_ms": 0
            }
        return {"status": self.status.value, "stats": self.stats}
    
    def execute_query(self, query: str, parameters: Optional[Dict] = None) -> List[Dict]:
        """
        Exécute une requête Cypher.
        Utilise les données mockées si en mode MOCK.
        """
        # CORRECTION: Toujours vérifier mock_mode en premier
        if self.mock_mode:
            self.stats["queries_executed"] += 1
            return [{"result": "mock_data"}]
        
        # CORRECTION: Vérifier si driver existe
        if not self.driver:
            self.logger.warning("Pas de driver Neo4j, basculement en mock")
            self.mock_mode = True
            self.stats["queries_executed"] += 1
            return [{"result": "mock_data"}]
        
        try:
            with self.driver.session(database=self.config.database) as session:
                result = session.run(query, parameters or {})
                self.stats["queries_executed"] += 1
                return [dict(record) for record in result]
        except Exception as e:
            self.logger.error(f"Erreur requête Cypher: {e}")
            self.stats["errors"] += 1
            # Basculer en mock pour les prochaines requêtes
            self.mock_mode = True
            return [{"result": "mock_data", "error": str(e)}]
    
    # ==========================================
    # OPÉRATIONS CRUD
    # ==========================================
    
    def create_zone_travail(
        self, 
        zone_id: str, 
        nom: str, 
        type_zone: str, 
        niveau_risque: str = "moyen", 
        capacite_max: int = 50
    ) -> Dict:
        """Crée un nœud Zone_Travail"""
        self.stats["nodes_created"] += 1
        if self.mock_mode:
            return {"zone_id": zone_id, "nom": nom, "status": "created_mock"}
        query = """
        CREATE (z:Zone_Travail {
            zone_id: $zone_id, 
            nom: $nom, 
            type_zone: $type_zone, 
            niveau_risque: $niveau_risque,
            capacite_max: $capacite_max,
            date_creation: datetime()
        }) RETURN z
        """
        result = self.execute_query(query, {
            "zone_id": zone_id, 
            "nom": nom, 
            "type_zone": type_zone, 
            "niveau_risque": niveau_risque,
            "capacite_max": capacite_max
        })
        return result[0] if result else {}
    
    def create_travailleur(
        self, 
        matricule: str, 
        nom: str, 
        prenom: str, 
        poste: str, 
        zone_id: Optional[str] = None
    ) -> Dict:
        """Crée un nœud Travailleur"""
        self.stats["nodes_created"] += 1
        if self.mock_mode:
            return {"matricule": matricule, "nom": nom, "prenom": prenom, "status": "created_mock"}
        query = """
        CREATE (t:Travailleur {
            matricule: $matricule, 
            nom: $nom, 
            prenom: $prenom, 
            poste: $poste,
            score_risque: 0.0,
            actif: true,
            date_creation: datetime()
        }) RETURN t
        """
        result = self.execute_query(query, {
            "matricule": matricule, 
            "nom": nom, 
            "prenom": prenom, 
            "poste": poste
        })
        return result[0] if result else {}
    
    def create_incident(
        self, 
        incident_id: str, 
        type_incident: str, 
        gravite: str, 
        description: str, 
        zone_id: Optional[str] = None, 
        travailleur_matricule: Optional[str] = None
    ) -> Dict:
        """Crée un nœud Incident_CNESST"""
        self.stats["nodes_created"] += 1
        if self.mock_mode:
            return {"incident_id": incident_id, "type_incident": type_incident, "status": "created_mock"}
        query = """
        CREATE (i:Incident_CNESST {
            incident_id: $incident_id, 
            type_incident: $type_incident, 
            gravite: $gravite, 
            description: $description,
            date_incident: datetime(),
            statut: 'ouvert'
        }) RETURN i
        """
        result = self.execute_query(query, {
            "incident_id": incident_id, 
            "type_incident": type_incident, 
            "gravite": gravite, 
            "description": description
        })
        return result[0] if result else {}
    
    def create_near_miss(
        self, 
        near_miss_id: str, 
        type_risque: str, 
        potentiel_gravite: str, 
        description: str, 
        zone_id: Optional[str] = None, 
        detecte_par_agent: Optional[str] = None
    ) -> Dict:
        """Crée un nœud Near_Miss (quasi-accident)"""
        self.stats["nodes_created"] += 1
        if self.mock_mode:
            return {"near_miss_id": near_miss_id, "type_risque": type_risque, "status": "created_mock"}
        query = """
        CREATE (nm:Near_Miss {
            near_miss_id: $near_miss_id, 
            type_risque: $type_risque, 
            potentiel_gravite: $potentiel_gravite, 
            description: $description,
            date_detection: datetime(),
            statut: 'a_analyser'
        }) RETURN nm
        """
        result = self.execute_query(query, {
            "near_miss_id": near_miss_id, 
            "type_risque": type_risque, 
            "potentiel_gravite": potentiel_gravite, 
            "description": description
        })
        return result[0] if result else {}
    
    def create_equipement(
        self, 
        equipement_id: str, 
        nom: str, 
        type_equipement: str, 
        zone_id: Optional[str] = None
    ) -> Dict:
        """Crée un nœud Équipement"""
        self.stats["nodes_created"] += 1
        if self.mock_mode:
            return {"equipement_id": equipement_id, "nom": nom, "status": "created_mock"}
        query = """
        CREATE (e:Equipement {
            equipement_id: $equipement_id, 
            nom: $nom, 
            type_equipement: $type_equipement,
            etat: 'operationnel',
            date_installation: datetime()
        }) RETURN e
        """
        result = self.execute_query(query, {
            "equipement_id": equipement_id, 
            "nom": nom, 
            "type_equipement": type_equipement
        })
        return result[0] if result else {}
    
    def create_capteur_iot(
        self, 
        capteur_id: str, 
        type_capteur: str, 
        zone_id: str, 
        seuil_alerte: float
    ) -> Dict:
        """Crée un nœud Capteur_IoT"""
        self.stats["nodes_created"] += 1
        if self.mock_mode:
            return {"capteur_id": capteur_id, "type_capteur": type_capteur, "status": "created_mock"}
        query = """
        CREATE (c:Capteur_IoT {
            capteur_id: $capteur_id, 
            type_capteur: $type_capteur, 
            seuil_alerte: $seuil_alerte,
            actif: true,
            date_installation: datetime()
        }) RETURN c
        """
        result = self.execute_query(query, {
            "capteur_id": capteur_id, 
            "type_capteur": type_capteur, 
            "seuil_alerte": seuil_alerte
        })
        return result[0] if result else {}
    
    # ==========================================
    # REQUÊTES ANALYTIQUES
    # ==========================================
    
    def get_zones_high_risk(self, min_incidents: int = 3) -> List[Dict]:
        """Identifie les zones à haut risque basé sur le nombre d'incidents"""
        if self.mock_mode:
            return [
                {"zone_id": "ZONE-A1", "zone_nom": "Atelier Soudure", "niveau_actuel": "élevé", "nb_incidents": 12},
                {"zone_id": "ZONE-B2", "zone_nom": "Entrepôt Chimique", "niveau_actuel": "élevé", "nb_incidents": 8},
                {"zone_id": "ZONE-C3", "zone_nom": "Zone Manutention", "niveau_actuel": "moyen", "nb_incidents": 5}
            ]
        query = """
        MATCH (z:Zone_Travail)<-[:SURVIENT_DANS]-(i:Incident_CNESST) 
        WITH z, count(i) as nb_incidents
        WHERE nb_incidents >= $min_incidents
        RETURN z.zone_id as zone_id, z.nom as zone_nom, z.niveau_risque as niveau_actuel, nb_incidents
        ORDER BY nb_incidents DESC 
        LIMIT 10
        """
        return self.execute_query(query, {"min_incidents": min_incidents})
    
    def get_travailleurs_at_risk(self, risk_threshold: float = 0.7) -> List[Dict]:
        """Identifie les travailleurs à risque élevé"""
        if self.mock_mode:
            return [
                {"matricule": "EMP-001", "nom": "Tremblay", "prenom": "Jean", "score_risque": 0.85, "nb_incidents": 3},
                {"matricule": "EMP-042", "nom": "Gagnon", "prenom": "Marie", "score_risque": 0.78, "nb_incidents": 2}
            ]
        query = """
        MATCH (t:Travailleur)
        WHERE t.score_risque >= $threshold
        OPTIONAL MATCH (t)<-[:IMPLIQUE]-(i:Incident_CNESST)
        RETURN t.matricule as matricule, t.nom as nom, t.prenom as prenom, 
               t.score_risque as score_risque, count(i) as nb_incidents
        ORDER BY t.score_risque DESC 
        LIMIT 20
        """
        return self.execute_query(query, {"threshold": risk_threshold})
    
    def get_incident_patterns(self, days: int = 90) -> List[Dict]:
        """Analyse les patterns d'incidents sur une période"""
        if self.mock_mode:
            return [
                {"type": "chute_plain_pied", "occurrences": 15},
                {"type": "coupure", "occurrences": 12},
                {"type": "brulure", "occurrences": 8}
            ]
        query = """
        MATCH (i:Incident_CNESST)
        WHERE i.date_incident >= datetime() - duration({days: $days})
        RETURN i.type_incident as type, count(i) as occurrences
        ORDER BY occurrences DESC
        """
        return self.execute_query(query, {"days": days})
    
    def get_near_miss_to_incident_correlation(self) -> List[Dict]:
        """Analyse la corrélation entre near-miss et incidents"""
        if self.mock_mode:
            return [
                {"near_miss_id": "NM-001", "type_risque": "glissade", "incident_id": "INC-015", "jours_avant_incident": 3},
                {"near_miss_id": "NM-008", "type_risque": "projection", "incident_id": "INC-022", "jours_avant_incident": 7}
            ]
        query = """
        MATCH (nm:Near_Miss)-[:PRECEDE]->(i:Incident_CNESST)
        RETURN nm.near_miss_id as near_miss_id, nm.type_risque as type_risque,
               i.incident_id as incident_id, 
               duration.between(nm.date_detection, i.date_incident).days as jours_avant_incident
        LIMIT 20
        """
        return self.execute_query(query)
    
    def get_equipment_risk_analysis(self) -> List[Dict]:
        """Analyse des équipements à risque"""
        if self.mock_mode:
            return [
                {"equipement_id": "EQ-101", "nom": "Chariot élévateur #3", "nb_incidents": 5},
                {"equipement_id": "EQ-055", "nom": "Presse hydraulique", "nb_incidents": 3}
            ]
        query = """
        MATCH (e:Equipement)<-[:IMPLIQUE_EQUIPEMENT]-(i:Incident_CNESST)
        RETURN e.equipement_id as equipement_id, e.nom as nom, count(i) as nb_incidents
        ORDER BY nb_incidents DESC 
        LIMIT 10
        """
        return self.execute_query(query)
    
    def enrich_context_for_agent(
        self, 
        zone_id: Optional[str] = None, 
        travailleur_matricule: Optional[str] = None, 
        equipement_id: Optional[str] = None
    ) -> Dict:
        """
        Enrichit le contexte pour un agent IA.
        Récupère toutes les informations pertinentes du Knowledge Graph.
        """
        context = {
            "timestamp": datetime.utcnow().isoformat(), 
            "zone": None, 
            "travailleur": None, 
            "equipement": None,
            "source": "mock" if self.mock_mode else "neo4j"
        }
        
        if zone_id:
            if self.mock_mode:
                context["zone"] = {
                    "zone_id": zone_id, 
                    "nom": "Zone simulée", 
                    "niveau_risque": "moyen", 
                    "incidents_30j": 2, 
                    "near_miss_30j": 5
                }
            else:
                # Requête réelle Neo4j
                query = """
                MATCH (z:Zone_Travail {zone_id: $zone_id})
                OPTIONAL MATCH (z)<-[:SURVIENT_DANS]-(i:Incident_CNESST)
                WHERE i.date_incident >= datetime() - duration({days: 30})
                OPTIONAL MATCH (z)<-[:LOCALISE_DANS]-(nm:Near_Miss)
                WHERE nm.date_detection >= datetime() - duration({days: 30})
                RETURN z.zone_id as zone_id, z.nom as nom, z.niveau_risque as niveau_risque,
                       count(DISTINCT i) as incidents_30j, count(DISTINCT nm) as near_miss_30j
                """
                result = self.execute_query(query, {"zone_id": zone_id})
                if result:
                    context["zone"] = result[0]
        
        if travailleur_matricule:
            if self.mock_mode:
                context["travailleur"] = {
                    "matricule": travailleur_matricule, 
                    "nom": "Simulé", 
                    "score_risque": 0.45, 
                    "formations": ["SIMDUT", "Secourisme"]
                }
            else:
                query = """
                MATCH (t:Travailleur {matricule: $matricule})
                OPTIONAL MATCH (t)-[:PARTICIPE_A]->(f:Formation)
                RETURN t.matricule as matricule, t.nom as nom, t.score_risque as score_risque,
                       collect(f.type_formation) as formations
                """
                result = self.execute_query(query, {"matricule": travailleur_matricule})
                if result:
                    context["travailleur"] = result[0]
        
        if equipement_id:
            if self.mock_mode:
                context["equipement"] = {
                    "equipement_id": equipement_id, 
                    "nom": "Équipement simulé", 
                    "etat": "operationnel",
                    "nb_incidents": 0
                }
            else:
                query = """
                MATCH (e:Equipement {equipement_id: $equipement_id})
                OPTIONAL MATCH (e)<-[:IMPLIQUE_EQUIPEMENT]-(i:Incident_CNESST)
                RETURN e.equipement_id as equipement_id, e.nom as nom, e.etat as etat,
                       count(i) as nb_incidents
                """
                result = self.execute_query(query, {"equipement_id": equipement_id})
                if result:
                    context["equipement"] = result[0]
        
        return context
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques du connecteur"""
        return {
            "status": self.status.value, 
            "mock_mode": self.mock_mode, 
            "uri": self.config.uri if not self.mock_mode else "N/A (mock)",
            "stats": self.stats
        }


# Singleton pour accès global
_connector_instance = None

def get_connector() -> SafetyGraphConnector:
    """Retourne l'instance singleton du connecteur"""
    global _connector_instance
    if _connector_instance is None:
        _connector_instance = SafetyGraphConnector()
    return _connector_instance


__all__ = ["SafetyGraphConnector", "Neo4jConfig", "ConnectionStatus", "get_connector"]
