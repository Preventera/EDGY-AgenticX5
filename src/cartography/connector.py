# src/cartography/connector.py - CORRIGE
import os
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from neo4j import GraphDatabase, Driver
from neo4j.exceptions import ServiceUnavailable, AuthError

from .models import Organization, Person, Team, Role, Zone, Process, Risk, RelationType

logger = logging.getLogger('SafetyGraph.Cartography')

class SafetyGraphCartographyConnector:
    def __init__(self, uri=None, username=None, password=None, database=None):
        self.uri = uri or os.getenv('NEO4J_URI', 'bolt://localhost:7687')
        self.username = username or os.getenv('NEO4J_USERNAME', 'neo4j')
        self.password = password or os.getenv('NEO4J_PASSWORD', '')
        self.database = database or os.getenv('NEO4J_DATABASE', 'neo4j')
        self.driver = None
        self._stats = {'created': 0, 'relations': 0, 'errors': 0}
    
    def connect(self):
        try:
            self.driver = GraphDatabase.driver(self.uri, auth=(self.username, self.password))
            with self.driver.session(database=self.database) as session:
                session.run('RETURN 1')
            logger.info(f'Connected to SafetyGraph: {self.uri}')
            return True
        except (AuthError, ServiceUnavailable) as e:
            logger.error(f'Connection error: {e}')
            raise
    
    def close(self):
        if self.driver:
            self.driver.close()
            self.driver = None
    
    @property
    def is_connected(self):
        return self.driver is not None
    
    def _get_session(self):
        if not self.driver:
            self.connect()
        return self.driver.session(database=self.database)
    
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, *args):
        self.close()
    
    def inject_organization(self, org):
        props = org.to_neo4j_props()
        cypher = """
        MERGE (o:Organization:EDGYEntity {id: $id})
        SET o.name = $name, o.sector_scian = $sector_scian,
            o.nb_employes = $nb_employes, o.created_at = $created_at
        RETURN o.id AS id
        """
        with self._get_session() as session:
            result = session.run(cypher, **props)
            self._stats['created'] += 1
            return result.single()['id']
    
    def inject_person(self, person, anonymize=True):
        if anonymize and person.matricule:
            person.anonymize()
        props = person.to_neo4j_props()
        cypher = """
        MERGE (p:Person:EDGYEntity {id: $id})
        SET p.matricule_anonyme = $matricule_anonyme, p.department = $department,
            p.team_id = $team_id, p.created_at = $created_at
        RETURN p.id AS id
        """
        with self._get_session() as session:
            result = session.run(cypher, **props)
            self._stats['created'] += 1
            return result.single()['id']
    
    def inject_team(self, team):
        props = team.to_neo4j_props()
        cypher = """
        MERGE (t:Team:EDGYEntity {id: $id})
        SET t.name = $name, t.department = $department, t.created_at = $created_at
        RETURN t.id AS id
        """
        with self._get_session() as session:
            result = session.run(cypher, **props)
            self._stats['created'] += 1
            return result.single()['id']
    
    def inject_role(self, role):
        props = role.to_neo4j_props()
        cypher = """
        MERGE (r:Role:EDGYEntity {id: $id})
        SET r.name = $name, r.niveau_hierarchique = $niveau_hierarchique,
            r.created_at = $created_at
        RETURN r.id AS id
        """
        with self._get_session() as session:
            result = session.run(cypher, **props)
            self._stats['created'] += 1
            return result.single()['id']
    
    def inject_zone(self, zone):
        props = zone.to_neo4j_props()
        cypher = """
        MERGE (z:Zone:EDGYEntity {id: $id})
        SET z.name = $name, z.risk_level = $risk_level,
            z.dangers_identifies = $dangers_identifies, z.epi_requis = $epi_requis,
            z.created_at = $created_at
        RETURN z.id AS id
        """
        with self._get_session() as session:
            result = session.run(cypher, **props)
            self._stats['created'] += 1
            return result.single()['id']
    
    def inject_process(self, process):
        props = process.to_neo4j_props()
        cypher = """
        MERGE (p:Process:EDGYEntity {id: $id})
        SET p.name = $name, p.process_type = $process_type,
            p.created_at = $created_at
        RETURN p.id AS id
        """
        with self._get_session() as session:
            result = session.run(cypher, **props)
            self._stats['created'] += 1
            return result.single()['id']
    
    def inject_risk(self, risk):
        risk.calculate_score()
        props = risk.to_neo4j_props()
        cypher = """
        MERGE (r:RisqueDanger:EDGYEntity {id: $id})
        SET r.description = $description, r.categorie = $categorie,
            r.probabilite = $probabilite, r.gravite = $gravite,
            r.score_edgy = $score_edgy, r.created_at = $created_at
        RETURN r.id AS id
        """
        with self._get_session() as session:
            result = session.run(cypher, **props)
            self._stats['created'] += 1
            return result.single()['id']
    
    def create_relation(self, source_id, target_id, relation_type, properties=None):
        props = properties or {}
        props['created_at'] = datetime.now().isoformat()
        rel = relation_type.value if isinstance(relation_type, RelationType) else relation_type
        try:
            with self._get_session() as session:
                cypher = f"""
                MATCH (a:EDGYEntity {{id: $source_id}})
                MATCH (b:EDGYEntity {{id: $target_id}})
                MERGE (a)-[r:{rel}]->(b)
                SET r += $properties
                RETURN type(r) AS t
                """
                result = session.run(cypher, source_id=source_id, target_id=target_id, properties=props)
                if result.single():
                    self._stats['relations'] += 1
                    return True
        except Exception as e:
            logger.error(f'Relation error: {e}')
            self._stats['errors'] += 1
        return False
    
    def link_person_to_zone(self, person_id, zone_id):
        return self.create_relation(person_id, zone_id, RelationType.TRAVAILLE_DANS)
    
    def link_risk_to_zone(self, risk_id, zone_id):
        return self.create_relation(risk_id, zone_id, RelationType.LOCALISE_DANS)
    
    def get_graph_stats(self):
        cypher = """
        MATCH (n:EDGYEntity) WITH labels(n) AS lbls UNWIND lbls AS lbl
        WITH lbl WHERE lbl <> 'EDGYEntity' RETURN lbl AS label, count(*) AS total
        """
        stats = {}
        with self._get_session() as session:
            for record in session.run(cypher):
                stats[record['label']] = record['total']
        return stats
    
    def get_zones_risk_summary(self):
        cypher = """
        MATCH (z:Zone) OPTIONAL MATCH (z)<-[:LOCALISE_DANS]-(r:RisqueDanger)
        RETURN z.id AS zone_id, z.name AS zone_name, z.risk_level AS risk_level,
        count(r) AS nb_risques, coalesce(avg(r.score_edgy), 0) AS score_moyen
        ORDER BY score_moyen DESC
        """
        with self._get_session() as session:
            return [dict(r) for r in session.run(cypher)]
    
    def get_session_stats(self):
        return {**self._stats, 'timestamp': datetime.now().isoformat()}