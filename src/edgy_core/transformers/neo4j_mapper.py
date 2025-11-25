#!/usr/bin/env python3
"""
EDGY Neo4j Mapper - EDGY-AgenticX5
Connecteur pour injecter la cartographie EDGY dans Neo4j SafetyGraph

Fonctionnalités:
- Injection des entités EDGY (Organisation, Personnes, Équipes, Rôles, Zones, Processus)
- Création des relations organisationnelles
- Synchronisation bidirectionnelle
- Requêtes analytiques sur la structure organisationnelle
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from neo4j import GraphDatabase
import logging
import os
from enum import Enum

# Configuration logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("EDGY.Neo4jMapper")


class EntityLabel(str, Enum):
    """Labels Neo4j pour les entités EDGY"""
    ORGANIZATION = "Organization"
    PERSON = "Person"
    TEAM = "Team"
    ROLE = "Role"
    PROCESS = "Process"
    ZONE = "RiskArea"
    HAZARD = "Hazard"
    CONTROL = "Control"


class RelationType(str, Enum):
    """Types de relations EDGY dans Neo4j"""
    SUPERVISES = "SUPERVISES"
    BELONGS_TO = "BELONGS_TO"
    HAS_ROLE = "HAS_ROLE"
    RESPONSIBLE_FOR = "RESPONSIBLE_FOR"
    LOCATED_IN = "LOCATED_IN"
    APPLIES_TO = "APPLIES_TO"
    OWNS = "OWNS"
    WORKS_IN = "WORKS_IN"
    HAS_HAZARD = "HAS_HAZARD"
    HAS_CONTROL = "HAS_CONTROL"
    MITIGATES = "MITIGATES"
    PART_OF = "PART_OF"


class EDGYNeo4jMapper:
    """
    Connecteur pour mapper les entités EDGY vers Neo4j SafetyGraph
    """
    
    def __init__(
        self,
        uri: str = None,
        username: str = None,
        password: str = None
    ):
        """
        Initialise le connecteur Neo4j
        
        Args:
            uri: URI Neo4j (default: bolt://localhost:7687)
            username: Utilisateur Neo4j
            password: Mot de passe Neo4j
        """
        self.uri = uri or os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.username = username or os.getenv("NEO4J_USERNAME", "neo4j")
        self.password = password or os.getenv("NEO4J_PASSWORD", "password")
        
        self.driver = None
        self._connect()
    
    def _connect(self):
        """Établit la connexion Neo4j"""
        try:
            self.driver = GraphDatabase.driver(
                self.uri,
                auth=(self.username, self.password)
            )
            # Test connexion
            with self.driver.session() as session:
                session.run("RETURN 1")
            logger.info(f"✅ Connecté à Neo4j: {self.uri}")
        except Exception as e:
            logger.error(f"❌ Erreur connexion Neo4j: {e}")
            self.driver = None
    
    def close(self):
        """Ferme la connexion"""
        if self.driver:
            self.driver.close()
            logger.info("Connexion Neo4j fermée")
    
    def is_connected(self) -> bool:
        """Vérifie si la connexion est active"""
        return self.driver is not None
    
    # ============================================================
    # CRÉATION D'ENTITÉS
    # ============================================================
    
    def create_organization(self, data: Dict[str, Any]) -> Optional[str]:
        """
        Crée une organisation dans Neo4j
        
        Args:
            data: Données de l'organisation
            
        Returns:
            ID du nœud créé ou None si erreur
        """
        if not self.driver:
            logger.error("Non connecté à Neo4j")
            return None
        
        query = """
        MERGE (o:Organization:EDGYEntity {id: $id})
        SET o.name = $name,
            o.description = $description,
            o.sector = $sector,
            o.size = $size,
            o.address = $address,
            o.created_at = datetime($created_at),
            o.updated_at = datetime()
        RETURN o.id as id
        """
        
        try:
            with self.driver.session() as session:
                result = session.run(query, {
                    "id": data.get("id"),
                    "name": data.get("name"),
                    "description": data.get("description"),
                    "sector": data.get("sector"),
                    "size": data.get("size"),
                    "address": data.get("address"),
                    "created_at": data.get("created_at", datetime.now()).isoformat()
                })
                record = result.single()
                logger.info(f"✅ Organisation créée: {data.get('name')}")
                return record["id"] if record else None
        except Exception as e:
            logger.error(f"❌ Erreur création organisation: {e}")
            return None
    
    def create_person(self, data: Dict[str, Any]) -> Optional[str]:
        """
        Crée une personne dans Neo4j
        
        Args:
            data: Données de la personne
            
        Returns:
            ID du nœud créé ou None si erreur
        """
        if not self.driver:
            return None
        
        query = """
        MERGE (p:Person:EDGYEntity {id: $id})
        SET p.name = $name,
            p.email = $email,
            p.phone = $phone,
            p.employee_id = $employee_id,
            p.department = $department,
            p.certifications = $certifications,
            p.created_at = datetime($created_at),
            p.updated_at = datetime()
        RETURN p.id as id
        """
        
        try:
            with self.driver.session() as session:
                result = session.run(query, {
                    "id": data.get("id"),
                    "name": data.get("name"),
                    "email": data.get("email"),
                    "phone": data.get("phone"),
                    "employee_id": data.get("employee_id"),
                    "department": data.get("department"),
                    "certifications": data.get("certifications", []),
                    "created_at": data.get("created_at", datetime.now()).isoformat()
                })
                record = result.single()
                logger.info(f"✅ Personne créée: {data.get('name')}")
                return record["id"] if record else None
        except Exception as e:
            logger.error(f"❌ Erreur création personne: {e}")
            return None
    
    def create_team(self, data: Dict[str, Any]) -> Optional[str]:
        """
        Crée une équipe dans Neo4j
        
        Args:
            data: Données de l'équipe
            
        Returns:
            ID du nœud créé ou None si erreur
        """
        if not self.driver:
            return None
        
        query = """
        MERGE (t:Team:EDGYEntity {id: $id})
        SET t.name = $name,
            t.description = $description,
            t.department = $department,
            t.created_at = datetime($created_at),
            t.updated_at = datetime()
        RETURN t.id as id
        """
        
        try:
            with self.driver.session() as session:
                result = session.run(query, {
                    "id": data.get("id"),
                    "name": data.get("name"),
                    "description": data.get("description"),
                    "department": data.get("department"),
                    "created_at": data.get("created_at", datetime.now()).isoformat()
                })
                record = result.single()
                logger.info(f"✅ Équipe créée: {data.get('name')}")
                return record["id"] if record else None
        except Exception as e:
            logger.error(f"❌ Erreur création équipe: {e}")
            return None
    
    def create_role(self, data: Dict[str, Any]) -> Optional[str]:
        """
        Crée un rôle dans Neo4j
        
        Args:
            data: Données du rôle
            
        Returns:
            ID du nœud créé ou None si erreur
        """
        if not self.driver:
            return None
        
        query = """
        MERGE (r:Role:EDGYEntity {id: $id})
        SET r.name = $name,
            r.description = $description,
            r.responsibilities = $responsibilities,
            r.sst_level = $sst_level,
            r.can_supervise = $can_supervise,
            r.can_approve_actions = $can_approve_actions,
            r.created_at = datetime($created_at),
            r.updated_at = datetime()
        RETURN r.id as id
        """
        
        try:
            with self.driver.session() as session:
                result = session.run(query, {
                    "id": data.get("id"),
                    "name": data.get("name"),
                    "description": data.get("description"),
                    "responsibilities": data.get("responsibilities", []),
                    "sst_level": data.get("sst_level"),
                    "can_supervise": data.get("can_supervise", False),
                    "can_approve_actions": data.get("can_approve_actions", False),
                    "created_at": data.get("created_at", datetime.now()).isoformat()
                })
                record = result.single()
                logger.info(f"✅ Rôle créé: {data.get('name')}")
                return record["id"] if record else None
        except Exception as e:
            logger.error(f"❌ Erreur création rôle: {e}")
            return None
    
    def create_zone(self, data: Dict[str, Any]) -> Optional[str]:
        """
        Crée une zone de risque dans Neo4j
        
        Args:
            data: Données de la zone
            
        Returns:
            ID du nœud créé ou None si erreur
        """
        if not self.driver:
            return None
        
        query = """
        MERGE (z:RiskArea:Zone:EDGYEntity {id: $id})
        SET z.name = $name,
            z.description = $description,
            z.location = $location,
            z.zone_type = $zone_type,
            z.risk_level = $risk_level,
            z.hazards = $hazards,
            z.controls = $controls,
            z.required_ppe = $required_ppe,
            z.max_occupancy = $max_occupancy,
            z.created_at = datetime($created_at),
            z.updated_at = datetime()
        RETURN z.id as id
        """
        
        try:
            with self.driver.session() as session:
                result = session.run(query, {
                    "id": data.get("id"),
                    "name": data.get("name"),
                    "description": data.get("description"),
                    "location": data.get("location"),
                    "zone_type": data.get("zone_type"),
                    "risk_level": data.get("risk_level", "moyen"),
                    "hazards": data.get("hazards", []),
                    "controls": data.get("controls", []),
                    "required_ppe": data.get("required_ppe", []),
                    "max_occupancy": data.get("max_occupancy"),
                    "created_at": data.get("created_at", datetime.now()).isoformat()
                })
                record = result.single()
                logger.info(f"✅ Zone créée: {data.get('name')}")
                return record["id"] if record else None
        except Exception as e:
            logger.error(f"❌ Erreur création zone: {e}")
            return None
    
    def create_process(self, data: Dict[str, Any]) -> Optional[str]:
        """
        Crée un processus SST dans Neo4j
        
        Args:
            data: Données du processus
            
        Returns:
            ID du nœud créé ou None si erreur
        """
        if not self.driver:
            return None
        
        query = """
        MERGE (p:Process:EDGYEntity {id: $id})
        SET p.name = $name,
            p.description = $description,
            p.process_type = $process_type,
            p.frequency = $frequency,
            p.steps = $steps,
            p.documents = $documents,
            p.kpis = $kpis,
            p.created_at = datetime($created_at),
            p.updated_at = datetime()
        RETURN p.id as id
        """
        
        try:
            with self.driver.session() as session:
                result = session.run(query, {
                    "id": data.get("id"),
                    "name": data.get("name"),
                    "description": data.get("description"),
                    "process_type": data.get("process_type"),
                    "frequency": data.get("frequency"),
                    "steps": data.get("steps", []),
                    "documents": data.get("documents", []),
                    "kpis": data.get("kpis", []),
                    "created_at": data.get("created_at", datetime.now()).isoformat()
                })
                record = result.single()
                logger.info(f"✅ Processus créé: {data.get('name')}")
                return record["id"] if record else None
        except Exception as e:
            logger.error(f"❌ Erreur création processus: {e}")
            return None
    
    # ============================================================
    # CRÉATION DE RELATIONS
    # ============================================================
    
    def create_relation(
        self,
        source_id: str,
        target_id: str,
        relation_type: str,
        properties: Dict[str, Any] = None
    ) -> bool:
        """
        Crée une relation entre deux entités EDGY
        
        Args:
            source_id: ID de l'entité source
            target_id: ID de l'entité cible
            relation_type: Type de relation
            properties: Propriétés de la relation
            
        Returns:
            True si succès, False sinon
        """
        if not self.driver:
            return False
        
        # Normaliser le type de relation
        rel_type = relation_type.upper().replace(" ", "_")
        
        # Construire la clause SET pour les propriétés
        set_clause = "SET r.created_at = datetime()"
        if properties and len(properties) > 0:
            # Ajouter chaque propriété individuellement
            for key in properties.keys():
                set_clause += f", r.{key} = ${key}"
        
        query = f"""
        MATCH (source:EDGYEntity {{id: $source_id}})
        MATCH (target:EDGYEntity {{id: $target_id}})
        MERGE (source)-[r:{rel_type}]->(target)
        {set_clause}
        RETURN type(r) as rel_type
        """
        
        # Préparer les paramètres
        params = {
            "source_id": source_id,
            "target_id": target_id
        }
        
        # Ajouter les propriétés aux paramètres
        if properties:
            params.update(properties)
        
        try:
            with self.driver.session() as session:
                result = session.run(query, params)
                record = result.single()
                if record:
                    logger.info(f"✅ Relation créée: {source_id} -[{rel_type}]-> {target_id}")
                    return True
                return False
        except Exception as e:
            logger.error(f"❌ Erreur création relation: {e}")
            return False
    
    def create_supervision_relation(self, supervisor_id: str, subordinate_id: str) -> bool:
        """Crée une relation de supervision"""
        return self.create_relation(supervisor_id, subordinate_id, RelationType.SUPERVISES.value)
    
    def create_team_membership(self, person_id: str, team_id: str) -> bool:
        """Crée une relation d'appartenance à une équipe"""
        return self.create_relation(person_id, team_id, RelationType.BELONGS_TO.value)
    
    def create_role_assignment(self, person_id: str, role_id: str) -> bool:
        """Assigne un rôle à une personne"""
        return self.create_relation(person_id, role_id, RelationType.HAS_ROLE.value)
    
    def create_zone_responsibility(self, team_id: str, zone_id: str) -> bool:
        """Assigne la responsabilité d'une zone à une équipe"""
        return self.create_relation(team_id, zone_id, RelationType.RESPONSIBLE_FOR.value)
    
    def create_process_zone_link(self, process_id: str, zone_id: str) -> bool:
        """Lie un processus à une zone"""
        return self.create_relation(process_id, zone_id, RelationType.APPLIES_TO.value)
    
    def create_process_owner(self, process_id: str, person_id: str) -> bool:
        """Définit le propriétaire d'un processus"""
        return self.create_relation(person_id, process_id, RelationType.OWNS.value)
    
    # ============================================================
    # IMPORT EN MASSE
    # ============================================================
    
    def import_cartography(self, cartography_data: Dict[str, Any]) -> Dict[str, int]:
        """
        Importe une cartographie complète dans Neo4j
        
        Args:
            cartography_data: Données de cartographie (organisations, personnes, etc.)
            
        Returns:
            Statistiques d'import
        """
        stats = {
            "organizations": 0,
            "persons": 0,
            "teams": 0,
            "roles": 0,
            "processes": 0,
            "zones": 0,
            "relations": 0,
            "errors": 0
        }
        
        # Importer les organisations
        for org in cartography_data.get("organizations", {}).values():
            if self.create_organization(org):
                stats["organizations"] += 1
            else:
                stats["errors"] += 1
        
        # Importer les rôles (avant les personnes pour les relations)
        for role in cartography_data.get("roles", {}).values():
            if self.create_role(role):
                stats["roles"] += 1
            else:
                stats["errors"] += 1
        
        # Importer les équipes
        for team in cartography_data.get("teams", {}).values():
            if self.create_team(team):
                stats["teams"] += 1
            else:
                stats["errors"] += 1
        
        # Importer les zones
        for zone in cartography_data.get("zones", {}).values():
            if self.create_zone(zone):
                stats["zones"] += 1
            else:
                stats["errors"] += 1
        
        # Importer les personnes
        for person in cartography_data.get("persons", {}).values():
            if self.create_person(person):
                stats["persons"] += 1
                
                # Créer les relations rôles
                for role_id in person.get("role_ids", []):
                    if self.create_role_assignment(person["id"], role_id):
                        stats["relations"] += 1
                
                # Créer les relations équipes
                for team_id in person.get("team_ids", []):
                    if self.create_team_membership(person["id"], team_id):
                        stats["relations"] += 1
                
                # Créer relation superviseur
                if person.get("supervisor_id"):
                    if self.create_supervision_relation(person["supervisor_id"], person["id"]):
                        stats["relations"] += 1
            else:
                stats["errors"] += 1
        
        # Importer les processus
        for process in cartography_data.get("processes", {}).values():
            if self.create_process(process):
                stats["processes"] += 1
                
                # Relations zones
                for zone_id in process.get("zone_ids", []):
                    if self.create_process_zone_link(process["id"], zone_id):
                        stats["relations"] += 1
                
                # Relation propriétaire
                if process.get("owner_id"):
                    if self.create_process_owner(process["id"], process["owner_id"]):
                        stats["relations"] += 1
            else:
                stats["errors"] += 1
        
        # Importer les relations explicites
        for relation in cartography_data.get("relations", []):
            if self.create_relation(
                relation["source_id"],
                relation["target_id"],
                relation["relation_type"],
                relation.get("properties")
            ):
                stats["relations"] += 1
            else:
                stats["errors"] += 1
        
        logger.info(f"✅ Import terminé: {stats}")
        return stats
    
    # ============================================================
    # REQUÊTES ANALYTIQUES
    # ============================================================
    
    def get_organization_structure(self) -> Dict[str, Any]:
        """
        Récupère la structure organisationnelle complète
        
        Returns:
            Structure organisationnelle avec hiérarchies
        """
        if not self.driver:
            return {}
        
        query = """
        MATCH (p:Person)
        OPTIONAL MATCH (p)-[:HAS_ROLE]->(r:Role)
        OPTIONAL MATCH (p)-[:BELONGS_TO]->(t:Team)
        OPTIONAL MATCH (supervisor:Person)-[:SUPERVISES]->(p)
        RETURN p.id as person_id,
               p.name as person_name,
               p.department as department,
               collect(DISTINCT r.name) as roles,
               collect(DISTINCT t.name) as teams,
               supervisor.name as supervisor_name
        """
        
        try:
            with self.driver.session() as session:
                result = session.run(query)
                persons = []
                for record in result:
                    persons.append({
                        "id": record["person_id"],
                        "name": record["person_name"],
                        "department": record["department"],
                        "roles": record["roles"],
                        "teams": record["teams"],
                        "supervisor": record["supervisor_name"]
                    })
                return {"persons": persons, "count": len(persons)}
        except Exception as e:
            logger.error(f"❌ Erreur requête structure: {e}")
            return {}
    
    def get_zones_with_risks(self) -> List[Dict[str, Any]]:
        """
        Récupère les zones avec leurs niveaux de risque
        
        Returns:
            Liste des zones avec informations de risque
        """
        if not self.driver:
            return []
        
        query = """
        MATCH (z:RiskArea)
        OPTIONAL MATCH (t:Team)-[:RESPONSIBLE_FOR]->(z)
        OPTIONAL MATCH (p:Process)-[:APPLIES_TO]->(z)
        RETURN z.id as zone_id,
               z.name as zone_name,
               z.risk_level as risk_level,
               z.hazards as hazards,
               z.controls as controls,
               collect(DISTINCT t.name) as responsible_teams,
               collect(DISTINCT p.name) as related_processes
        ORDER BY 
            CASE z.risk_level
                WHEN 'critique' THEN 1
                WHEN 'élevé' THEN 2
                WHEN 'moyen' THEN 3
                WHEN 'faible' THEN 4
                ELSE 5
            END
        """
        
        try:
            with self.driver.session() as session:
                result = session.run(query)
                zones = []
                for record in result:
                    zones.append({
                        "id": record["zone_id"],
                        "name": record["zone_name"],
                        "risk_level": record["risk_level"],
                        "hazards": record["hazards"],
                        "controls": record["controls"],
                        "responsible_teams": record["responsible_teams"],
                        "related_processes": record["related_processes"]
                    })
                return zones
        except Exception as e:
            logger.error(f"❌ Erreur requête zones: {e}")
            return []
    
    def get_supervision_chain(self, person_id: str) -> List[Dict[str, Any]]:
        """
        Récupère la chaîne de supervision d'une personne
        
        Args:
            person_id: ID de la personne
            
        Returns:
            Chaîne de supervision (du plus proche au plus haut)
        """
        if not self.driver:
            return []
        
        query = """
        MATCH path = (p:Person {id: $person_id})<-[:SUPERVISES*]-(supervisor:Person)
        RETURN [node IN nodes(path) | {id: node.id, name: node.name}] as chain
        ORDER BY length(path) DESC
        LIMIT 1
        """
        
        try:
            with self.driver.session() as session:
                result = session.run(query, {"person_id": person_id})
                record = result.single()
                if record:
                    return record["chain"]
                return []
        except Exception as e:
            logger.error(f"❌ Erreur requête supervision: {e}")
            return []
    
    def get_edgy_statistics(self) -> Dict[str, int]:
        """
        Récupère les statistiques des entités EDGY dans Neo4j
        
        Returns:
            Comptage par type d'entité
        """
        if not self.driver:
            return {}
        
        query = """
        MATCH (n:EDGYEntity)
        WITH labels(n) as labels
        UNWIND labels as label
        WITH label WHERE label <> 'EDGYEntity'
        RETURN label, count(*) as count
        ORDER BY count DESC
        """
        
        try:
            with self.driver.session() as session:
                result = session.run(query)
                stats = {}
                for record in result:
                    stats[record["label"]] = record["count"]
                
                # Ajouter le total des relations
                rel_result = session.run("""
                    MATCH (:EDGYEntity)-[r]->(:EDGYEntity)
                    RETURN count(r) as relations
                """)
                rel_record = rel_result.single()
                if rel_record:
                    stats["Relations"] = rel_record["relations"]
                
                return stats
        except Exception as e:
            logger.error(f"❌ Erreur statistiques: {e}")
            return {}
    
    def find_persons_without_supervisor(self) -> List[Dict[str, Any]]:
        """
        Trouve les personnes sans superviseur assigné
        
        Returns:
            Liste des personnes sans superviseur
        """
        if not self.driver:
            return []
        
        query = """
        MATCH (p:Person)
        WHERE NOT (:Person)-[:SUPERVISES]->(p)
        RETURN p.id as id, p.name as name, p.department as department
        """
        
        try:
            with self.driver.session() as session:
                result = session.run(query)
                return [dict(record) for record in result]
        except Exception as e:
            logger.error(f"❌ Erreur requête: {e}")
            return []
    
    def find_zones_without_responsible(self) -> List[Dict[str, Any]]:
        """
        Trouve les zones sans équipe responsable
        
        Returns:
            Liste des zones sans responsable
        """
        if not self.driver:
            return []
        
        query = """
        MATCH (z:RiskArea)
        WHERE NOT (:Team)-[:RESPONSIBLE_FOR]->(z)
        RETURN z.id as id, z.name as name, z.risk_level as risk_level
        """
        
        try:
            with self.driver.session() as session:
                result = session.run(query)
                return [dict(record) for record in result]
        except Exception as e:
            logger.error(f"❌ Erreur requête: {e}")
            return []
    
    # ============================================================
    # NETTOYAGE
    # ============================================================
    
    def clear_edgy_entities(self) -> int:
        """
        Supprime toutes les entités EDGY (attention: irréversible!)
        
        Returns:
            Nombre de nœuds supprimés
        """
        if not self.driver:
            return 0
        
        query = """
        MATCH (n:EDGYEntity)
        DETACH DELETE n
        RETURN count(*) as deleted
        """
        
        try:
            with self.driver.session() as session:
                result = session.run(query)
                record = result.single()
                deleted = record["deleted"] if record else 0
                logger.warning(f"⚠️ {deleted} entités EDGY supprimées")
                return deleted
        except Exception as e:
            logger.error(f"❌ Erreur suppression: {e}")
            return 0


# ============================================================
# FONCTION D'INTÉGRATION AVEC L'API CARTOGRAPHY
# ============================================================

async def sync_cartography_to_neo4j(cartography_store) -> Dict[str, Any]:
    """
    Synchronise le store de cartographie vers Neo4j
    
    Args:
        cartography_store: Instance de CartographyStore
        
    Returns:
        Résultat de la synchronisation
    """
    mapper = EDGYNeo4jMapper()
    
    if not mapper.is_connected():
        return {
            "status": "error",
            "message": "Impossible de se connecter à Neo4j"
        }
    
    try:
        # Préparer les données
        cartography_data = {
            "organizations": cartography_store.organizations,
            "persons": cartography_store.persons,
            "teams": cartography_store.teams,
            "roles": cartography_store.roles,
            "processes": cartography_store.processes,
            "zones": cartography_store.zones,
            "relations": cartography_store.relations
        }
        
        # Importer
        stats = mapper.import_cartography(cartography_data)
        
        return {
            "status": "success",
            "message": "Synchronisation réussie",
            "stats": stats
        }
    finally:
        mapper.close()


# ============================================================
# TEST STANDALONE
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("TEST EDGY Neo4j Mapper")
    print("=" * 60)
    
    # Créer le mapper
    mapper = EDGYNeo4jMapper()
    
    if not mapper.is_connected():
        print("❌ Impossible de se connecter à Neo4j")
        print("   Vérifiez que Neo4j est démarré et accessible")
        exit(1)
    
    # Test création entités
    print("\n📝 Création d'entités de test...")
    
    # Organisation
    org_id = mapper.create_organization({
        "id": "TEST-ORG-001",
        "name": "Test Organisation",
        "description": "Organisation de test",
        "sector": "31-33"
    })
    
    # Rôle
    role_id = mapper.create_role({
        "id": "TEST-ROLE-001",
        "name": "Superviseur Test",
        "description": "Rôle de test",
        "can_supervise": True
    })
    
    # Zone
    zone_id = mapper.create_zone({
        "id": "TEST-ZONE-001",
        "name": "Zone Test",
        "risk_level": "moyen",
        "hazards": ["Test hazard 1", "Test hazard 2"]
    })
    
    # Personne
    person_id = mapper.create_person({
        "id": "TEST-PERS-001",
        "name": "Test Person",
        "email": "test@test.com",
        "department": "Test"
    })
    
    # Relations
    mapper.create_role_assignment("TEST-PERS-001", "TEST-ROLE-001")
    
    # Statistiques
    print("\n📊 Statistiques EDGY:")
    stats = mapper.get_edgy_statistics()
    for label, count in stats.items():
        print(f"   {label}: {count}")
    
    # Nettoyage optionnel
    # mapper.clear_edgy_entities()
    
    mapper.close()
    print("\n✅ Test terminé!")
