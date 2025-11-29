#!/usr/bin/env python3
"""
🔧 Patch SafetyGraph API - Ajoute endpoint /api/v1/cartography/import
EDGY-AgenticX5 | Corrige le bug d'injection organisations

Usage:
    1. Arrêter l'API actuelle (CTRL+C)
    2. Copier ce fichier dans le projet
    3. Lancer: python safetygraph_api_patched.py
"""

import os
from datetime import datetime
from typing import Any, Dict, List, Optional
from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI, HTTPException, Query, Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from neo4j import GraphDatabase

# Configuration logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SafetyGraph.API")

# ============================================================================
# CONFIGURATION
# ============================================================================

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")
API_VERSION = "1.1.0"  # Version avec fix cartographie
API_TITLE = "🛡️ SafetyGraph API"


# ============================================================================
# CONNEXION NEO4J
# ============================================================================

class Neo4jConnection:
    """Gestionnaire de connexion Neo4j"""
    
    def __init__(self, uri: str, user: str, password: str):
        self.driver = None
        self.uri = uri
        self.user = user
        self.password = password
        
    def connect(self):
        """Établir la connexion"""
        try:
            self.driver = GraphDatabase.driver(
                self.uri, 
                auth=(self.user, self.password)
            )
            with self.driver.session() as session:
                session.run("RETURN 1")
            logger.info(f"✅ Connecté à Neo4j: {self.uri}")
            return True
        except Exception as e:
            logger.error(f"❌ Erreur connexion Neo4j: {e}")
            return False
    
    def close(self):
        if self.driver:
            self.driver.close()
    
    def execute_query(self, query: str, params: dict = None) -> List[dict]:
        if not self.driver:
            raise Exception("Non connecté à Neo4j")
        with self.driver.session() as session:
            result = session.run(query, params or {})
            return [dict(record) for record in result]
    
    def execute_write(self, query: str, params: dict = None) -> bool:
        """Exécuter une requête d'écriture"""
        if not self.driver:
            raise Exception("Non connecté à Neo4j")
        try:
            with self.driver.session() as session:
                session.run(query, params or {})
            return True
        except Exception as e:
            logger.error(f"Erreur écriture: {e}")
            return False


# Instance globale
neo4j_conn = Neo4jConnection(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)


# ============================================================================
# MODÈLES PYDANTIC
# ============================================================================

class StatsGlobales(BaseModel):
    organizations: int = Field(..., description="Nombre d'organisations")
    persons: int = Field(..., description="Nombre de personnes")
    risks: int = Field(..., description="Nombre de risques")
    zones: int = Field(..., description="Nombre de zones")
    teams: int = Field(..., description="Nombre d'équipes")
    roles: int = Field(..., description="Nombre de rôles")


class CartographyImportRequest(BaseModel):
    """Requête d'import cartographie - CORRIGÉ"""
    organizations: List[dict] = Field(default=[], description="Liste des organisations")
    zones: List[dict] = Field(default=[], description="Liste des zones")
    teams: List[dict] = Field(default=[], description="Liste des équipes")
    roles: List[dict] = Field(default=[], description="Liste des rôles")
    persons: List[dict] = Field(default=[], description="Liste des personnes")
    risks: List[dict] = Field(default=[], description="Liste des risques")
    processes: List[dict] = Field(default=[], description="Liste des processus")


# ============================================================================
# APPLICATION FASTAPI
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Démarrage SafetyGraph API...")
    neo4j_conn.connect()
    yield
    logger.info("🛑 Arrêt SafetyGraph API...")
    neo4j_conn.close()


app = FastAPI(
    title=API_TITLE,
    description="API REST pour SafetyGraph Neo4j avec import cartographie EDGY",
    version=API_VERSION,
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# ENDPOINTS DE BASE
# ============================================================================

@app.get("/", tags=["Système"])
async def root():
    return {
        "api": "SafetyGraph API",
        "version": API_VERSION,
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health", tags=["Système"])
async def health_check():
    neo4j_status = "connected" if neo4j_conn.driver else "disconnected"
    return {
        "status": "healthy",
        "neo4j": neo4j_status,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/v1/stats", response_model=StatsGlobales, tags=["Statistiques"])
async def get_stats():
    """Statistiques globales du graphe SafetyGraph"""
    try:
        query = """
            MATCH (o:Organization) WITH count(o) as orgs
            MATCH (p:Person) WITH orgs, count(p) as persons
            MATCH (r:RisqueDanger) WITH orgs, persons, count(r) as risks
            MATCH (z:Zone) WITH orgs, persons, risks, count(z) as zones
            MATCH (t:Team) WITH orgs, persons, risks, zones, count(t) as teams
            MATCH (ro:Role) 
            RETURN orgs, persons, risks, zones, teams, count(ro) as roles
        """
        result = neo4j_conn.execute_query(query)
        if result:
            r = result[0]
            return StatsGlobales(
                organizations=r.get("orgs", 0),
                persons=r.get("persons", 0),
                risks=r.get("risks", 0),
                zones=r.get("zones", 0),
                teams=r.get("teams", 0),
                roles=r.get("roles", 0)
            )
    except Exception as e:
        logger.error(f"Erreur stats: {e}")
    
    return StatsGlobales(
        organizations=0, persons=0, risks=0, zones=0, teams=0, roles=0
    )


# ============================================================================
# 🔧 ENDPOINT CARTOGRAPHY/IMPORT - CORRIGÉ
# ============================================================================

@app.post("/api/v1/cartography/import", tags=["Cartographie"])
async def import_cartography(data: CartographyImportRequest):
    """
    🔧 Importer des entités depuis la cartographie EDGY
    
    CORRECTIONS APPLIQUÉES:
    - region → region_ssq (mapping automatique)
    - probabilite/gravite string → int (conversion)
    - Gestion robuste des erreurs par entité
    """
    results = {
        "success": True,
        "imported": {
            "organizations": 0,
            "zones": 0,
            "teams": 0,
            "roles": 0,
            "persons": 0,
            "risks": 0,
            "processes": 0
        },
        "errors": []
    }
    
    # =========================================
    # IMPORT ORGANIZATIONS - CORRIGÉ
    # =========================================
    for org in data.organizations:
        try:
            org_id = org.get("id", f"ORG-{datetime.now().timestamp()}")
            name = org.get("name", "Sans nom")
            sector = str(org.get("sector_scian", org.get("sector", "000")))
            
            # Conversion nb_employes robuste
            nb_emp_raw = org.get("nb_employes", org.get("employees", 0))
            try:
                nb_emp = int(nb_emp_raw) if nb_emp_raw else 0
            except (ValueError, TypeError):
                nb_emp = 0
            
            # CORRECTION: region → region_ssq
            region = org.get("region_ssq", org.get("region", "Non spécifié"))
            
            query = """
                MERGE (o:Organization:EDGYEntity {id: $id})
                SET o.name = $name,
                    o.sector_scian = $sector,
                    o.nb_employes = $nb_employes,
                    o.region_ssq = $region,
                    o.created_at = datetime(),
                    o.source = 'cartographie_edgy'
                RETURN o.id as id
            """
            neo4j_conn.execute_write(query, {
                "id": org_id,
                "name": name,
                "sector": sector,
                "nb_employes": nb_emp,
                "region": region
            })
            results["imported"]["organizations"] += 1
            logger.info(f"✅ Organisation créée: {name}")
            
        except Exception as e:
            error_msg = f"Organization '{org.get('name', '?')}': {str(e)}"
            results["errors"].append(error_msg)
            logger.error(f"❌ {error_msg}")
    
    # =========================================
    # IMPORT ZONES
    # =========================================
    for zone in data.zones:
        try:
            zone_id = zone.get("id", f"ZONE-{datetime.now().timestamp()}")
            name = zone.get("name", "Sans nom")
            zone_type = zone.get("type", "general")
            niveau_risque = zone.get("niveau_risque", "moyen")
            
            query = """
                MERGE (z:Zone:EDGYEntity {id: $id})
                SET z.name = $name,
                    z.type = $type,
                    z.niveau_risque = $niveau_risque,
                    z.created_at = datetime(),
                    z.source = 'cartographie_edgy'
                RETURN z.id as id
            """
            neo4j_conn.execute_write(query, {
                "id": zone_id,
                "name": name,
                "type": zone_type,
                "niveau_risque": niveau_risque
            })
            results["imported"]["zones"] += 1
            
        except Exception as e:
            results["errors"].append(f"Zone '{zone.get('name', '?')}': {str(e)}")
    
    # =========================================
    # IMPORT TEAMS
    # =========================================
    for team in data.teams:
        try:
            team_id = team.get("id", f"TEAM-{datetime.now().timestamp()}")
            name = team.get("name", "Sans nom")
            nb_membres = int(team.get("nb_membres", 0) or 0)
            
            query = """
                MERGE (t:Team:EDGYEntity {id: $id})
                SET t.name = $name,
                    t.nb_membres = $nb_membres,
                    t.created_at = datetime(),
                    t.source = 'cartographie_edgy'
                RETURN t.id as id
            """
            neo4j_conn.execute_write(query, {
                "id": team_id,
                "name": name,
                "nb_membres": nb_membres
            })
            results["imported"]["teams"] += 1
            
        except Exception as e:
            results["errors"].append(f"Team '{team.get('name', '?')}': {str(e)}")
    
    # =========================================
    # IMPORT ROLES
    # =========================================
    for role in data.roles:
        try:
            role_id = role.get("id", f"ROLE-{datetime.now().timestamp()}")
            name = role.get("name", "Sans nom")
            niveau_risque = role.get("niveau_risque", "moyen")
            epi_requis = role.get("epi_requis", "")
            
            query = """
                MERGE (r:Role:EDGYEntity {id: $id})
                SET r.name = $name,
                    r.niveau_risque = $niveau_risque,
                    r.epi_requis = $epi_requis,
                    r.created_at = datetime(),
                    r.source = 'cartographie_edgy'
                RETURN r.id as id
            """
            neo4j_conn.execute_write(query, {
                "id": role_id,
                "name": name,
                "niveau_risque": niveau_risque,
                "epi_requis": epi_requis
            })
            results["imported"]["roles"] += 1
            
        except Exception as e:
            results["errors"].append(f"Role '{role.get('name', '?')}': {str(e)}")
    
    # =========================================
    # IMPORT PERSONS
    # =========================================
    for person in data.persons:
        try:
            person_id = person.get("id", f"PERS-{datetime.now().timestamp()}")
            matricule = person.get("matricule_anonyme", person_id)
            anciennete = int(person.get("anciennete", 0) or 0)
            
            query = """
                MERGE (p:Person:EDGYEntity {id: $id})
                SET p.matricule_anonyme = $matricule,
                    p.anciennete = $anciennete,
                    p.created_at = datetime(),
                    p.source = 'cartographie_edgy'
                RETURN p.id as id
            """
            neo4j_conn.execute_write(query, {
                "id": person_id,
                "matricule": matricule,
                "anciennete": anciennete
            })
            results["imported"]["persons"] += 1
            
        except Exception as e:
            results["errors"].append(f"Person '{person.get('id', '?')}': {str(e)}")
    
    # =========================================
    # IMPORT RISKS - CORRIGÉ (string → int)
    # =========================================
    for risk in data.risks:
        try:
            risk_id = risk.get("id", f"RISK-{datetime.now().timestamp()}")
            description = risk.get("description", "Sans description")
            categorie = risk.get("categorie", "autre")
            
            # CORRECTION: Conversion robuste string → int
            prob_raw = risk.get("probabilite", 3)
            grav_raw = risk.get("gravite", 3)
            
            try:
                probabilite = int(prob_raw) if prob_raw else 3
            except (ValueError, TypeError):
                probabilite = 3
            
            try:
                gravite = int(grav_raw) if grav_raw else 3
            except (ValueError, TypeError):
                gravite = 3
            
            score = probabilite * gravite
            tolerance_zero = score >= 15
            controles = risk.get("controles", "")
            
            query = """
                MERGE (r:RisqueDanger:EDGYEntity {id: $id})
                SET r.description = $description,
                    r.categorie = $categorie,
                    r.probabilite = $probabilite,
                    r.gravite = $gravite,
                    r.score = $score,
                    r.tolerance_zero = $tolerance_zero,
                    r.controles = $controles,
                    r.created_at = datetime(),
                    r.source = 'cartographie_edgy'
                RETURN r.id as id
            """
            neo4j_conn.execute_write(query, {
                "id": risk_id,
                "description": description,
                "categorie": categorie,
                "probabilite": probabilite,
                "gravite": gravite,
                "score": score,
                "tolerance_zero": tolerance_zero,
                "controles": controles
            })
            results["imported"]["risks"] += 1
            logger.info(f"✅ Risque créé: {description[:30]}...")
            
        except Exception as e:
            error_msg = f"Risk '{risk.get('description', '?')[:30]}': {str(e)}"
            results["errors"].append(error_msg)
            logger.error(f"❌ {error_msg}")
    
    # =========================================
    # IMPORT PROCESSES
    # =========================================
    for process in data.processes:
        try:
            proc_id = process.get("id", f"PROC-{datetime.now().timestamp()}")
            name = process.get("name", "Sans nom")
            criticite = process.get("criticite", "moyenne")
            frequence = process.get("frequence", "quotidienne")
            
            query = """
                MERGE (p:Process:EDGYEntity {id: $id})
                SET p.name = $name,
                    p.criticite = $criticite,
                    p.frequence = $frequence,
                    p.created_at = datetime(),
                    p.source = 'cartographie_edgy'
                RETURN p.id as id
            """
            neo4j_conn.execute_write(query, {
                "id": proc_id,
                "name": name,
                "criticite": criticite,
                "frequence": frequence
            })
            results["imported"]["processes"] += 1
            
        except Exception as e:
            results["errors"].append(f"Process '{process.get('name', '?')}': {str(e)}")
    
    # =========================================
    # RÉSUMÉ
    # =========================================
    total = sum(results["imported"].values())
    results["message"] = f"✅ {total} entités importées dans Neo4j"
    
    if results["errors"]:
        results["success"] = len(results["errors"]) < total
        logger.warning(f"⚠️ {len(results['errors'])} erreurs sur {total + len(results['errors'])} tentatives")
    
    logger.info(f"📊 Import terminé: {results['imported']}")
    
    return results


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    print("🚀 Démarrage SafetyGraph API PATCHED sur http://localhost:8000")
    print("📖 Documentation: http://localhost:8000/docs")
    print("🔧 Endpoint corrigé: POST /api/v1/cartography/import")
    uvicorn.run(app, host="0.0.0.0", port=8000)
