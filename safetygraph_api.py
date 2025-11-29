#!/usr/bin/env python3
"""
🛡️ SafetyGraph API - Version Cloud
EDGY-AgenticX5 | Preventera | GenAISafety

API REST pour SafetyGraph avec Neo4j Aura (Cloud)
Déploiement: Railway

Endpoints:
- /health - Health check
- /api/v1/stats - Statistiques globales
- /api/v1/sectors - Secteurs SCIAN
- /api/v1/risks - Risques
- /api/v1/zones - Zones
- /api/v1/alerts - Alertes
- /api/v1/cartography/* - Injection cartographie
"""

import os
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from neo4j import GraphDatabase, Driver
from neo4j.exceptions import ServiceUnavailable, AuthError

# ============================================================================
# CONFIGURATION
# ============================================================================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SafetyGraph.API")

# Variables d'environnement
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "")
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

# ============================================================================
# CONNEXION NEO4J
# ============================================================================

class Neo4jConnection:
    """Gestionnaire de connexion Neo4j"""
    
    def __init__(self):
        self.driver: Optional[Driver] = None
        self.connected = False
    
    def connect(self) -> bool:
        """Établir la connexion"""
        try:
            self.driver = GraphDatabase.driver(
                NEO4J_URI,
                auth=(NEO4J_USERNAME, NEO4J_PASSWORD)
            )
            # Test connexion
            with self.driver.session() as session:
                session.run("RETURN 1")
            self.connected = True
            logger.info(f"✅ Connecté à Neo4j: {NEO4J_URI}")
            return True
        except AuthError as e:
            logger.error(f"❌ Erreur authentification Neo4j: {e}")
            self.connected = False
            return False
        except ServiceUnavailable as e:
            logger.error(f"❌ Neo4j non disponible: {e}")
            self.connected = False
            return False
        except Exception as e:
            logger.error(f"❌ Erreur connexion Neo4j: {e}")
            self.connected = False
            return False
    
    def close(self):
        """Fermer la connexion"""
        if self.driver:
            self.driver.close()
            self.connected = False
    
    def execute_query(self, query: str, params: dict = None) -> List[Dict]:
        """Exécuter une requête et retourner les résultats"""
        if not self.connected:
            return []
        try:
            with self.driver.session() as session:
                result = session.run(query, params or {})
                return [dict(record) for record in result]
        except Exception as e:
            logger.error(f"Erreur requête: {e}")
            return []
    
    def execute_write(self, query: str, params: dict = None) -> bool:
        """Exécuter une requête d'écriture"""
        if not self.connected:
            return False
        try:
            with self.driver.session() as session:
                session.run(query, params or {})
                return True
        except Exception as e:
            logger.error(f"Erreur écriture: {e}")
            return False


# Instance globale
db = Neo4jConnection()

# ============================================================================
# MODÈLES PYDANTIC
# ============================================================================

class HealthResponse(BaseModel):
    status: str
    neo4j: str
    timestamp: str
    version: str = "2.0.0"

class StatsResponse(BaseModel):
    organizations: int = 0
    persons: int = 0
    risks: int = 0
    zones: int = 0
    teams: int = 0
    roles: int = 0

class SectorStats(BaseModel):
    scian: str
    nom: str
    nb_organizations: int
    total_employes: int
    nb_risques: int
    score_moyen: float

class RiskItem(BaseModel):
    id: str = ""
    description: str
    categorie: str
    probabilite: int
    gravite: int
    score: int
    zone: str = ""

class ZoneItem(BaseModel):
    id: str = ""
    name: str
    risk_level: str
    nb_risques: int = 0

class AlertItem(BaseModel):
    type: str
    niveau: str
    organisation: str = ""
    zone: str = ""
    details: str = ""
    score: int = 0

# Modèles pour cartographie
class OrganizationCreate(BaseModel):
    name: str
    sector_scian: str
    nb_employes: int = 0
    region_ssq: str = ""
    code_cnesst: str = ""

class ZoneCreate(BaseModel):
    name: str
    risk_level: str = "moyen"
    dangers_identifies: List[str] = []
    epi_requis: List[str] = []
    organization_id: str = ""

class PersonCreate(BaseModel):
    matricule: str
    department: str = ""
    age_groupe: str = ""
    anciennete_annees: int = 0
    certifications_sst: List[str] = []

class RiskCreate(BaseModel):
    description: str
    categorie: str
    probabilite: int = 1
    gravite: int = 1
    zone_id: str = ""

class CartographyImport(BaseModel):
    organizations: List[Dict] = []
    zones: List[Dict] = []
    teams: List[Dict] = []
    roles: List[Dict] = []
    persons: List[Dict] = []
    risks: List[Dict] = []
    processes: List[Dict] = []

# ============================================================================
# APPLICATION FASTAPI
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle: connexion au démarrage, déconnexion à l'arrêt"""
    logger.info("🚀 Démarrage SafetyGraph API...")
    db.connect()
    yield
    logger.info("🛑 Arrêt SafetyGraph API...")
    db.close()

app = FastAPI(
    title="🛡️ SafetyGraph API",
    description="API REST pour SafetyGraph - Plateforme d'analyse prédictive SST",
    version="2.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS if CORS_ORIGINS != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# ENDPOINTS - SANTÉ
# ============================================================================

@app.get("/", tags=["🏠 Accueil"])
async def root():
    """Page d'accueil de l'API"""
    return {
        "name": "🛡️ SafetyGraph API",
        "version": "2.0.0",
        "description": "API REST pour SafetyGraph - EDGY-AgenticX5",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health", response_model=HealthResponse, tags=["🏠 Accueil"])
async def health_check():
    """Vérification de santé de l'API"""
    return HealthResponse(
        status="healthy" if db.connected else "degraded",
        neo4j="connected" if db.connected else "disconnected",
        timestamp=datetime.now().isoformat()
    )

# ============================================================================
# ENDPOINTS - STATISTIQUES
# ============================================================================

@app.get("/api/v1/stats", response_model=StatsResponse, tags=["📊 Statistiques"])
async def get_stats():
    """Statistiques globales du graphe"""
    if not db.connected:
        return StatsResponse()
    
    query = """
    MATCH (o:Organization) WITH count(o) AS orgs
    MATCH (p:Person) WITH orgs, count(p) AS persons
    MATCH (r:RisqueDanger) WITH orgs, persons, count(r) AS risks
    MATCH (z:Zone) WITH orgs, persons, risks, count(z) AS zones
    MATCH (t:Team) WITH orgs, persons, risks, zones, count(t) AS teams
    MATCH (ro:Role) 
    RETURN orgs, persons, risks, zones, teams, count(ro) AS roles
    """
    
    result = db.execute_query(query)
    if result:
        r = result[0]
        return StatsResponse(
            organizations=r.get("orgs", 0),
            persons=r.get("persons", 0),
            risks=r.get("risks", 0),
            zones=r.get("zones", 0),
            teams=r.get("teams", 0),
            roles=r.get("roles", 0)
        )
    return StatsResponse()

@app.get("/api/v1/stats/kpis", tags=["📊 Statistiques"])
async def get_kpis():
    """KPIs calculés"""
    if not db.connected:
        return {"error": "Neo4j non connecté"}
    
    query = """
    MATCH (r:RisqueDanger)
    WITH count(r) AS total,
         sum(CASE WHEN r.probabilite * r.gravite >= 15 THEN 1 ELSE 0 END) AS tz,
         avg(r.probabilite * r.gravite) AS score_moy
    RETURN total AS total_risques,
           tz AS risques_tolerance_zero,
           round(score_moy * 100) / 100 AS score_moyen,
           round(tz * 100.0 / total) AS taux_tz
    """
    
    result = db.execute_query(query)
    return result[0] if result else {}

# ============================================================================
# ENDPOINTS - SECTEURS
# ============================================================================

@app.get("/api/v1/sectors", tags=["🏭 Secteurs"])
async def get_sectors():
    """Liste des secteurs SCIAN"""
    if not db.connected:
        return []
    
    query = """
    MATCH (o:Organization)
    WITH o.sector_scian AS scian, count(o) AS nb_orgs, sum(o.nb_employes) AS employes
    RETURN scian, nb_orgs, employes
    ORDER BY nb_orgs DESC
    """
    
    return db.execute_query(query)

@app.get("/api/v1/sectors/{scian}", tags=["🏭 Secteurs"])
async def get_sector_detail(scian: str):
    """Détail d'un secteur SCIAN"""
    if not db.connected:
        raise HTTPException(status_code=503, detail="Neo4j non connecté")
    
    query = """
    MATCH (o:Organization)
    WHERE o.sector_scian CONTAINS $scian
    OPTIONAL MATCH (o)<-[:APPARTIENT_A]-(z:Zone)<-[:LOCALISE_DANS]-(r:RisqueDanger)
    WITH o, count(DISTINCT z) AS zones, count(r) AS risques, avg(r.probabilite * r.gravite) AS score
    RETURN o.name AS organisation, o.nb_employes AS employes, zones, risques, 
           round(score * 100) / 100 AS score_moyen
    ORDER BY score_moyen DESC
    """
    
    return db.execute_query(query, {"scian": scian})

@app.get("/api/v1/sectors/priority/cnesst", tags=["🏭 Secteurs"])
async def get_priority_sectors():
    """5 secteurs prioritaires CNESST"""
    return [
        {"scian": "62", "nom": "Santé et services sociaux", "priorite": 1},
        {"scian": "31-33", "nom": "Fabrication", "priorite": 2},
        {"scian": "44-45", "nom": "Commerce de détail", "priorite": 3},
        {"scian": "23", "nom": "Construction", "priorite": 4},
        {"scian": "72", "nom": "Hébergement et restauration", "priorite": 5}
    ]

# ============================================================================
# ENDPOINTS - RISQUES
# ============================================================================

@app.get("/api/v1/risks", tags=["⚠️ Risques"])
async def get_risks(
    limit: int = Query(30, ge=1, le=100),
    min_score: int = Query(0, ge=0, le=25),
    categorie: Optional[str] = None
):
    """Liste des risques triés par score"""
    if not db.connected:
        return []
    
    query = """
    MATCH (r:RisqueDanger)
    WHERE r.probabilite * r.gravite >= $min_score
    """ + (f"AND r.categorie = $categorie" if categorie else "") + """
    OPTIONAL MATCH (r)-[:LOCALISE_DANS]->(z:Zone)
    RETURN r.id AS id, r.description AS description, r.categorie AS categorie,
           r.probabilite AS probabilite, r.gravite AS gravite,
           r.probabilite * r.gravite AS score, z.name AS zone
    ORDER BY score DESC
    LIMIT $limit
    """
    
    params = {"min_score": min_score, "limit": limit}
    if categorie:
        params["categorie"] = categorie
    
    return db.execute_query(query, params)

@app.get("/api/v1/risks/tolerance-zero", tags=["⚠️ Risques"])
async def get_tolerance_zero_risks():
    """Risques Tolérance Zéro (score >= 15)"""
    if not db.connected:
        return []
    
    query = """
    MATCH (r:RisqueDanger)
    WHERE r.probabilite * r.gravite >= 15
    OPTIONAL MATCH (r)-[:LOCALISE_DANS]->(z:Zone)
    OPTIONAL MATCH (z)-[:APPARTIENT_A]->(o:Organization)
    RETURN r.description AS description, r.categorie AS categorie,
           r.probabilite * r.gravite AS score,
           z.name AS zone, o.name AS organisation
    ORDER BY score DESC
    """
    
    return db.execute_query(query)

@app.get("/api/v1/risks/categories", tags=["⚠️ Risques"])
async def get_risk_categories():
    """Risques groupés par catégorie"""
    if not db.connected:
        return []
    
    query = """
    MATCH (r:RisqueDanger)
    RETURN r.categorie AS categorie,
           count(r) AS count,
           round(avg(r.probabilite * r.gravite) * 100) / 100 AS score_moyen,
           sum(CASE WHEN r.probabilite * r.gravite >= 15 THEN 1 ELSE 0 END) AS nb_tz
    ORDER BY count DESC
    """
    
    return db.execute_query(query)

@app.get("/api/v1/risks/matrix", tags=["⚠️ Risques"])
async def get_risk_matrix():
    """Données pour matrice de risques P×G"""
    if not db.connected:
        return []
    
    query = """
    MATCH (r:RisqueDanger)
    RETURN r.probabilite AS x, r.gravite AS y, count(r) AS count, 
           collect(DISTINCT r.categorie) AS categories
    ORDER BY x, y
    """
    
    return db.execute_query(query)

# ============================================================================
# ENDPOINTS - ZONES
# ============================================================================

@app.get("/api/v1/zones", tags=["📍 Zones"])
async def get_zones(risk_level: Optional[str] = None):
    """Liste des zones"""
    if not db.connected:
        return []
    
    query = """
    MATCH (z:Zone)
    """ + (f"WHERE z.risk_level = $risk_level" if risk_level else "") + """
    OPTIONAL MATCH (z)<-[:LOCALISE_DANS]-(r:RisqueDanger)
    RETURN z.id AS id, z.name AS name, z.risk_level AS risk_level,
           count(r) AS nb_risques
    ORDER BY nb_risques DESC
    """
    
    params = {"risk_level": risk_level} if risk_level else {}
    return db.execute_query(query, params)

@app.get("/api/v1/zones/hotspots", tags=["📍 Zones"])
async def get_zone_hotspots():
    """Zones avec concentration élevée de risques"""
    if not db.connected:
        return []
    
    query = """
    MATCH (z:Zone)<-[:LOCALISE_DANS]-(r:RisqueDanger)
    WITH z, count(r) AS nb_risques, avg(r.probabilite * r.gravite) AS score_moyen
    WHERE nb_risques >= 3
    OPTIONAL MATCH (z)-[:APPARTIENT_A]->(o:Organization)
    RETURN z.name AS zone, o.name AS organisation, nb_risques,
           round(score_moyen * 100) / 100 AS score_moyen,
           CASE WHEN score_moyen >= 12 THEN 'CRITIQUE'
                WHEN score_moyen >= 8 THEN 'ÉLEVÉ'
                ELSE 'MODÉRÉ' END AS niveau
    ORDER BY score_moyen DESC
    """
    
    return db.execute_query(query)

# ============================================================================
# ENDPOINTS - ALERTES
# ============================================================================

@app.get("/api/v1/alerts", tags=["🚨 Alertes"])
async def get_alerts():
    """Toutes les alertes actives"""
    if not db.connected:
        return []
    
    alerts = []
    
    # Risques TZ
    tz_query = """
    MATCH (r:RisqueDanger)
    WHERE r.probabilite * r.gravite >= 15
    OPTIONAL MATCH (r)-[:LOCALISE_DANS]->(z:Zone)-[:APPARTIENT_A]->(o:Organization)
    RETURN 'TOLERANCE_ZERO' AS type, 'CRITIQUE' AS niveau,
           o.name AS organisation, z.name AS zone,
           r.description AS details, r.probabilite * r.gravite AS score
    ORDER BY score DESC
    LIMIT 10
    """
    alerts.extend(db.execute_query(tz_query))
    
    # Hotspots
    hotspot_query = """
    MATCH (z:Zone)<-[:LOCALISE_DANS]-(r:RisqueDanger)
    WITH z, count(r) AS nb, avg(r.probabilite * r.gravite) AS score
    WHERE nb >= 5 OR score >= 12
    OPTIONAL MATCH (z)-[:APPARTIENT_A]->(o:Organization)
    RETURN 'HOTSPOT' AS type, 
           CASE WHEN score >= 12 THEN 'CRITIQUE' ELSE 'ÉLEVÉ' END AS niveau,
           o.name AS organisation, z.name AS zone,
           nb + ' risques, score ' + toString(round(score * 10) / 10) AS details,
           toInteger(score) AS score
    ORDER BY score DESC
    LIMIT 5
    """
    alerts.extend(db.execute_query(hotspot_query))
    
    return alerts

@app.get("/api/v1/alerts/young-workers", tags=["🚨 Alertes"])
async def get_young_worker_alerts():
    """Alertes jeunes travailleurs (18-24) exposés"""
    if not db.connected:
        return []
    
    query = """
    MATCH (p:Person)-[:TRAVAILLE_DANS]->(z:Zone)<-[:LOCALISE_DANS]-(r:RisqueDanger)
    WHERE p.age_groupe = '18-24' AND r.probabilite * r.gravite >= 10
    WITH p, z, collect(DISTINCT r.categorie) AS risques, max(r.probabilite * r.gravite) AS score_max
    RETURN p.matricule AS travailleur, z.name AS zone, risques, score_max
    ORDER BY score_max DESC
    """
    
    return db.execute_query(query)

# ============================================================================
# ENDPOINTS - AGENTS IA
# ============================================================================

@app.get("/api/v1/agents/visionai/targets", tags=["🤖 Agents IA"])
async def get_visionai_targets():
    """Zones cibles pour VisionAI (surveillance caméra)"""
    if not db.connected:
        return []
    
    query = """
    MATCH (z:Zone)<-[:LOCALISE_DANS]-(r:RisqueDanger)
    WHERE z.risk_level = 'critique' AND r.categorie IN ['chute', 'mecanique', 'electrique']
    WITH z, collect(DISTINCT r.categorie) AS risques
    RETURN z.name AS zone, risques, 'VisionAI' AS agent
    """
    
    return db.execute_query(query)

@app.get("/api/v1/agents/ergoai/targets", tags=["🤖 Agents IA"])
async def get_ergoai_targets():
    """Postes cibles pour ErgoAI (ergonomie)"""
    if not db.connected:
        return []
    
    query = """
    MATCH (z:Zone)<-[:LOCALISE_DANS]-(r:RisqueDanger)
    WHERE r.categorie = 'ergonomique'
    OPTIONAL MATCH (p:Person)-[:TRAVAILLE_DANS]->(z)
    WITH z, count(DISTINCT p) AS nb_exposes, avg(r.probabilite * r.gravite) AS score
    WHERE nb_exposes >= 2
    RETURN z.name AS poste, nb_exposes, round(score * 100) / 100 AS score_ergo
    ORDER BY score DESC
    """
    
    return db.execute_query(query)

# ============================================================================
# ENDPOINTS - CARTOGRAPHIE (INJECTION)
# ============================================================================

@app.post("/api/v1/cartography/organization", tags=["🗺️ Cartographie"])
async def create_organization(org: OrganizationCreate):
    """Créer une organisation"""
    if not db.connected:
        raise HTTPException(status_code=503, detail="Neo4j non connecté")
    
    query = """
    CREATE (o:Organization:EDGYEntity {
        id: 'ORG-' + toString(timestamp()),
        name: $name,
        sector_scian: $sector_scian,
        nb_employes: $nb_employes,
        region_ssq: $region_ssq,
        code_cnesst: $code_cnesst,
        created_at: datetime()
    })
    RETURN o.id AS id, o.name AS name
    """
    
    result = db.execute_query(query, org.dict())
    if result:
        return {"success": True, "data": result[0]}
    raise HTTPException(status_code=500, detail="Erreur création organisation")

@app.post("/api/v1/cartography/zone", tags=["🗺️ Cartographie"])
async def create_zone(zone: ZoneCreate):
    """Créer une zone"""
    if not db.connected:
        raise HTTPException(status_code=503, detail="Neo4j non connecté")
    
    query = """
    CREATE (z:Zone:EDGYEntity {
        id: 'ZONE-' + toString(timestamp()),
        name: $name,
        risk_level: $risk_level,
        dangers_identifies: $dangers_identifies,
        epi_requis: $epi_requis,
        created_at: datetime()
    })
    RETURN z.id AS id, z.name AS name
    """
    
    result = db.execute_query(query, zone.dict())
    if result:
        return {"success": True, "data": result[0]}
    raise HTTPException(status_code=500, detail="Erreur création zone")

@app.post("/api/v1/cartography/risk", tags=["🗺️ Cartographie"])
async def create_risk(risk: RiskCreate):
    """Créer un risque"""
    if not db.connected:
        raise HTTPException(status_code=503, detail="Neo4j non connecté")
    
    query = """
    CREATE (r:RisqueDanger:EDGYEntity {
        id: 'RISK-' + toString(timestamp()),
        description: $description,
        categorie: $categorie,
        probabilite: $probabilite,
        gravite: $gravite,
        score: $probabilite * $gravite,
        created_at: datetime()
    })
    RETURN r.id AS id, r.description AS description, r.score AS score
    """
    
    result = db.execute_query(query, risk.dict())
    if result:
        return {"success": True, "data": result[0]}
    raise HTTPException(status_code=500, detail="Erreur création risque")

@app.post("/api/v1/cartography/import", tags=["🗺️ Cartographie"])
async def import_cartography(data: CartographyImport):
    """Importer une cartographie complète (JSON du générateur web)"""
    if not db.connected:
        raise HTTPException(status_code=503, detail="Neo4j non connecté")
    
    counts = {"organizations": 0, "zones": 0, "teams": 0, "roles": 0, "persons": 0, "risks": 0}
    
    # Organisations
    for org in data.organizations:
        query = """
        CREATE (o:Organization:EDGYEntity {
            id: $id,
            name: $name,
            sector_scian: $sector_scian,
            nb_employes: $nb_employes,
            region_ssq: $region_ssq,
            created_at: datetime()
        })
        """
        params = {
            "id": org.get("id", "ORG-" + str(int(__import__('time').time()))),
            "name": org.get("name", ""),
            "sector_scian": org.get("sector_scian", ""),
            "nb_employes": int(str(org.get("nb_employes", 0) or 0)),
            "region_ssq": org.get("region_ssq", "")
        }
        if db.execute_write(query, params):
            counts["organizations"] += 1
    
    # Zones
    for zone in data.zones:
        query = """
        CREATE (z:Zone:EDGYEntity {
            id: $id,
            name: $name,
            risk_level: coalesce($risk_level, 'moyen'),
            dangers_identifies: coalesce($dangers_identifies, []),
            epi_requis: coalesce($epi_requis, []),
            created_at: datetime()
        })
        """
        if db.execute_write(query, zone):
            counts["zones"] += 1
    
    # Teams
    for team in data.teams:
        query = """
        CREATE (t:Team:EDGYEntity {
            id: $id,
            name: $name,
            department: coalesce($department, ''),
            created_at: datetime()
        })
        """
        if db.execute_write(query, team):
            counts["teams"] += 1
    
    # Roles
    for role in data.roles:
        query = """
        CREATE (r:Role:EDGYEntity {
            id: $id,
            name: $name,
            niveau_hierarchique: coalesce($niveau_hierarchique, 1),
            created_at: datetime()
        })
        """
        if db.execute_write(query, role):
            counts["roles"] += 1
    
    # Persons
    for person in data.persons:
        query = """
        CREATE (p:Person:EDGYEntity {
            id: $id,
            matricule: $matricule,
            department: coalesce($department, ''),
            age_groupe: coalesce($age_groupe, ''),
            certifications_sst: coalesce($certifications_sst, []),
            created_at: datetime()
        })
        """
        if db.execute_write(query, person):
            counts["persons"] += 1
    
    # Risks
    for risk in data.risks:
        query = """
        CREATE (r:RisqueDanger:EDGYEntity {
            id: $id,
            description: $description,
            categorie: $categorie,
            probabilite: $probabilite,
            gravite: $gravite,
            score: $score,
            created_at: datetime()
        })
        """
        try:
            prob = int(str(risk.get("probabilite", 1)))
        except:
            prob = 1
        try:
            grav = int(str(risk.get("gravite", 1)))
        except:
            grav = 1
        params = {
            "id": risk.get("id", "RISK-" + str(int(__import__('time').time()))),
            "description": risk.get("description", ""),
            "categorie": risk.get("categorie", ""),
            "probabilite": prob,
            "gravite": grav,
            "score": prob * grav
        }
        if db.execute_write(query, params):
            counts["risks"] += 1
    
    return {"success": True, "imported": counts}

# ============================================================================
# ENDPOINTS - EXPORT
# ============================================================================

@app.get("/api/v1/export/dashboard-data", tags=["📤 Export"])
async def export_dashboard_data():
    """Données complètes pour dashboard"""
    if not db.connected:
        return {"error": "Neo4j non connecté"}
    
    data = {}
    
    # Stats
    stats = await get_stats()
    data["stats"] = stats.dict()
    
    # Secteurs
    data["sectors"] = await get_sectors()
    
    # Risques par catégorie
    data["risks_by_category"] = await get_risk_categories()
    
    # Zones
    data["zones"] = await get_zones()
    
    # Alertes
    data["alerts"] = await get_alerts()
    
    return data

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
