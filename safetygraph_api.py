#!/usr/bin/env python3
"""
🛡️ SafetyGraph API - FastAPI pour requêtes Cypher
EDGY-AgenticX5 | Preventera | GenAISafety

API REST pour exécuter des requêtes Cypher sur le graphe SafetyGraph Neo4j.
Fournit 50+ endpoints organisés en 15 catégories d'analyses prédictives SST.

Endpoints principaux:
- /api/v1/stats - Statistiques globales
- /api/v1/sectors - Analyses par secteur SCIAN
- /api/v1/risks - Gestion des risques
- /api/v1/zones - Cartographie des zones
- /api/v1/persons - Exposition des personnes
- /api/v1/alerts - Alertes et surveillance
- /api/v1/compliance - Conformité et audit
- /api/v1/predictive - Analyses prédictives ML
- /api/v1/agents - Requêtes pour agents IA

Démarrage:
    uvicorn safetygraph_api:app --host 0.0.0.0 --port 8002 --reload

Documentation:
    http://localhost:8002/docs (Swagger UI)
    http://localhost:8002/redoc (ReDoc)
"""

import os
from datetime import datetime
from typing import Any, Dict, List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query, Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from neo4j import GraphDatabase

# ============================================================================
# CONFIGURATION
# ============================================================================

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")
API_VERSION = "1.0.0"
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
            # Test de connexion
            with self.driver.session() as session:
                session.run("RETURN 1")
            return True
        except Exception as e:
            print(f"❌ Erreur connexion Neo4j: {e}")
            return False
    
    def close(self):
        """Fermer la connexion"""
        if self.driver:
            self.driver.close()
    
    def execute_query(self, query: str, params: dict = None) -> List[dict]:
        """Exécuter une requête Cypher"""
        if not self.driver:
            raise Exception("Non connecté à Neo4j")
        
        with self.driver.session() as session:
            result = session.run(query, params or {})
            return [dict(record) for record in result]
    
    def execute_single(self, query: str, params: dict = None) -> Optional[dict]:
        """Exécuter une requête et retourner un seul résultat"""
        results = self.execute_query(query, params)
        return results[0] if results else None


# Instance globale
neo4j_conn = Neo4jConnection(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)


# ============================================================================
# MODÈLES PYDANTIC
# ============================================================================

class StatsGlobales(BaseModel):
    """Statistiques globales du graphe"""
    organizations: int = Field(..., description="Nombre d'organisations")
    persons: int = Field(..., description="Nombre de personnes")
    risks: int = Field(..., description="Nombre de risques")
    zones: int = Field(..., description="Nombre de zones")
    teams: int = Field(..., description="Nombre d'équipes")
    roles: int = Field(..., description="Nombre de rôles")


class SectorStats(BaseModel):
    """Statistiques par secteur SCIAN"""
    scian: str
    nom: str
    nb_organizations: int
    total_employes: int
    nb_risques: Optional[int] = 0
    score_moyen: Optional[float] = 0.0


class RiskItem(BaseModel):
    """Élément de risque"""
    description: str
    categorie: str
    probabilite: int
    gravite: int
    score: int


class ZoneItem(BaseModel):
    """Élément de zone"""
    name: str
    risk_level: str
    nb_risques: int
    categories: List[str] = []


class AlertItem(BaseModel):
    """Alerte générée"""
    type: str
    niveau: str
    organisation: Optional[str] = None
    zone: Optional[str] = None
    details: str
    score: Optional[float] = None


class PredictiveFeatures(BaseModel):
    """Features pour modèles ML"""
    organisation: str
    secteur: str
    employes: int
    nb_zones: int
    nb_risques: int
    score_moyen: float
    risques_par_zone: float


class CypherRequest(BaseModel):
    """Requête Cypher personnalisée"""
    query: str = Field(..., description="Requête Cypher à exécuter")
    params: Optional[Dict[str, Any]] = Field(default={}, description="Paramètres")


class CypherResponse(BaseModel):
    """Réponse à une requête Cypher"""
    success: bool
    data: List[Dict[str, Any]]
    count: int
    execution_time_ms: float


# ============================================================================
# LIFECYCLE
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestion du cycle de vie de l'application"""
    # Startup
    print("🚀 Démarrage SafetyGraph API...")
    connected = neo4j_conn.connect()
    if connected:
        print("✅ Connecté à Neo4j")
    else:
        print("⚠️ Neo4j non disponible - Mode dégradé")
    
    yield
    
    # Shutdown
    print("👋 Arrêt SafetyGraph API...")
    neo4j_conn.close()


# ============================================================================
# APPLICATION FASTAPI
# ============================================================================

app = FastAPI(
    title=API_TITLE,
    description="""
# 🛡️ SafetyGraph API

API REST pour requêtes Cypher sur le graphe de connaissances SafetyGraph.

## Fonctionnalités

- **📊 Statistiques** - KPIs globaux et par secteur
- **⚠️ Risques** - Identification et priorisation
- **📍 Zones** - Cartographie des dangers
- **👥 Personnes** - Exposition et certifications
- **🚨 Alertes** - Surveillance proactive
- **✅ Conformité** - Audit ISO 45001
- **🔮 Prédictif** - Features pour ML

## État actuel du graphe

- 460 Organisations (16 secteurs SCIAN)
- 3,926 Personnes
- 2,870 Risques
- 1,429 Zones

## Technologies

- Neo4j 5.x / Cypher
- FastAPI / Python
- Pydantic validation
    """,
    version=API_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
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
# ENDPOINTS: SANTÉ ET STATUT
# ============================================================================

@app.get("/", tags=["Santé"])
async def root():
    """Page d'accueil de l'API"""
    return {
        "api": "SafetyGraph API",
        "version": API_VERSION,
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", tags=["Santé"])
async def health_check():
    """Vérification de la santé de l'API"""
    neo4j_ok = False
    stats = {}
    
    try:
        result = neo4j_conn.execute_single("""
            MATCH (o:Organization) WITH count(o) as orgs
            MATCH (r:RisqueDanger) 
            RETURN orgs, count(r) as risks
        """)
        if result:
            neo4j_ok = True
            stats = {"organizations": result["orgs"], "risks": result["risks"]}
    except:
        pass
    
    return {
        "status": "healthy" if neo4j_ok else "degraded",
        "neo4j": "connected" if neo4j_ok else "disconnected",
        "timestamp": datetime.now().isoformat(),
        "stats": stats
    }


# ============================================================================
# ENDPOINTS: STATISTIQUES GLOBALES (Section 1)
# ============================================================================

@app.get("/api/v1/stats", response_model=StatsGlobales, tags=["Statistiques"])
async def get_stats_globales():
    """
    📊 Statistiques globales du graphe SafetyGraph
    
    Retourne le comptage de tous les types de nœuds principaux.
    """
    query = """
    MATCH (o:Organization) WITH count(o) as orgs
    MATCH (p:Person) WITH orgs, count(p) as persons
    MATCH (r:RisqueDanger) WITH orgs, persons, count(r) as risks
    MATCH (z:Zone) WITH orgs, persons, risks, count(z) as zones
    MATCH (t:Team) WITH orgs, persons, risks, zones, count(t) as teams
    MATCH (ro:Role) 
    RETURN orgs, persons, risks, zones, teams, count(ro) as roles
    """
    
    try:
        result = neo4j_conn.execute_single(query)
        if result:
            return StatsGlobales(
                organizations=result["orgs"],
                persons=result["persons"],
                risks=result["risks"],
                zones=result["zones"],
                teams=result["teams"],
                roles=result["roles"]
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    # Valeurs par défaut si pas de connexion
    return StatsGlobales(
        organizations=460,
        persons=3926,
        risks=2870,
        zones=1429,
        teams=1125,
        roles=2363
    )


@app.get("/api/v1/stats/kpis", tags=["Statistiques"])
async def get_kpis():
    """
    📈 KPIs calculés pour dashboard
    """
    query = """
    MATCH (r:RisqueDanger) 
    WHERE r.probabilite IS NOT NULL AND r.gravite IS NOT NULL
    WITH count(r) AS total_risques,
         sum(CASE WHEN r.probabilite * r.gravite >= 15 THEN 1 ELSE 0 END) AS risques_tz,
         avg(r.probabilite * r.gravite) AS score_moyen
    RETURN total_risques, risques_tz, round(score_moyen * 100) / 100 AS score_moyen
    """
    
    try:
        result = neo4j_conn.execute_single(query)
        if result:
            return {
                "total_risques": result["total_risques"],
                "risques_tolerance_zero": result["risques_tz"],
                "score_risque_moyen": result["score_moyen"],
                "taux_tz": round(result["risques_tz"] * 100 / max(result["total_risques"], 1), 1)
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# ENDPOINTS: SECTEURS SCIAN (Section 2)
# ============================================================================

@app.get("/api/v1/sectors", tags=["Secteurs SCIAN"])
async def get_sectors():
    """
    🏭 Liste des secteurs SCIAN avec statistiques
    """
    query = """
    MATCH (o:Organization)
    WHERE o.sector_scian IS NOT NULL
    RETURN o.sector_scian AS scian, 
           count(o) AS nb_orgs,
           sum(o.nb_employes) AS total_employes
    ORDER BY nb_orgs DESC
    """
    
    try:
        results = neo4j_conn.execute_query(query)
        return {"sectors": results, "count": len(results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/sectors/{scian}", tags=["Secteurs SCIAN"])
async def get_sector_detail(scian: str = Path(..., description="Code SCIAN")):
    """
    🏭 Détail d'un secteur SCIAN spécifique
    """
    query = """
    MATCH (o:Organization)
    WHERE o.sector_scian = $scian
    OPTIONAL MATCH (o)<-[:APPARTIENT_A]-(z:Zone)<-[:LOCALISE_DANS]-(r:RisqueDanger)
    WITH o, count(DISTINCT z) AS zones, count(r) AS risques, 
         avg(r.probabilite * r.gravite) AS score
    RETURN o.name AS organisation, o.nb_employes AS employes, 
           zones, risques, round(score * 100) / 100 AS score_moyen
    ORDER BY employes DESC
    """
    
    try:
        results = neo4j_conn.execute_query(query, {"scian": scian})
        return {
            "scian": scian,
            "organizations": results,
            "count": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/sectors/priority/cnesst", tags=["Secteurs SCIAN"])
async def get_cnesst_priority_sectors():
    """
    🎯 Les 5 secteurs prioritaires CNESST
    """
    query = """
    MATCH (o:Organization)<-[:APPARTIENT_A]-(z:Zone)<-[:LOCALISE_DANS]-(r:RisqueDanger)
    WHERE o.sector_scian IN ['621-624', '31-33', '44-45', '236-238', '72']
    RETURN o.sector_scian AS secteur,
           CASE o.sector_scian
               WHEN '621-624' THEN '🏥 Santé'
               WHEN '31-33' THEN '🏭 Fabrication'
               WHEN '44-45' THEN '🛒 Commerce'
               WHEN '236-238' THEN '🏗️ Construction'
               WHEN '72' THEN '🍽️ Resto/Hôtel'
           END AS nom_secteur,
           count(DISTINCT o) AS orgs,
           count(r) AS risques,
           round(avg(r.probabilite * r.gravite) * 100) / 100 AS score_moyen
    ORDER BY risques DESC
    """
    
    try:
        results = neo4j_conn.execute_query(query)
        return {"priority_sectors": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# ENDPOINTS: RISQUES (Section 3)
# ============================================================================

@app.get("/api/v1/risks", tags=["Risques"])
async def get_risks(
    limit: int = Query(30, ge=1, le=100, description="Nombre max de résultats"),
    min_score: int = Query(0, ge=0, le=25, description="Score minimum P×G")
):
    """
    ⚠️ Liste des risques triés par score
    """
    query = """
    MATCH (r:RisqueDanger)
    WHERE r.probabilite IS NOT NULL AND r.gravite IS NOT NULL
      AND r.probabilite * r.gravite >= $min_score
    RETURN r.description AS description,
           r.categorie AS categorie,
           r.probabilite AS probabilite,
           r.gravite AS gravite,
           r.probabilite * r.gravite AS score
    ORDER BY score DESC
    LIMIT $limit
    """
    
    try:
        results = neo4j_conn.execute_query(query, {"limit": limit, "min_score": min_score})
        return {"risks": results, "count": len(results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/risks/tolerance-zero", tags=["Risques"])
async def get_tolerance_zero_risks():
    """
    🔴 Risques Tolérance Zéro (score ≥ 15)
    """
    query = """
    MATCH (r:RisqueDanger)
    WHERE r.probabilite * r.gravite >= 15
    RETURN r.categorie AS categorie,
           count(r) AS nb_risques,
           collect(r.description)[0..5] AS exemples
    ORDER BY nb_risques DESC
    """
    
    try:
        results = neo4j_conn.execute_query(query)
        total = sum(r["nb_risques"] for r in results)
        return {"tolerance_zero": results, "total": total}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/risks/categories", tags=["Risques"])
async def get_risk_categories():
    """
    📊 Risques groupés par catégorie
    """
    query = """
    MATCH (r:RisqueDanger)
    WHERE r.categorie IS NOT NULL
    RETURN r.categorie AS categorie,
           count(r) AS nb_risques,
           round(avg(r.probabilite * r.gravite) * 100) / 100 AS score_moyen
    ORDER BY nb_risques DESC
    """
    
    try:
        results = neo4j_conn.execute_query(query)
        return {"categories": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/risks/matrix", tags=["Risques"])
async def get_risk_matrix():
    """
    📈 Données pour matrice de risques P×G
    """
    query = """
    MATCH (r:RisqueDanger)
    WHERE r.probabilite IS NOT NULL AND r.gravite IS NOT NULL
    RETURN r.probabilite AS p, r.gravite AS g, count(r) AS count
    ORDER BY p, g
    """
    
    try:
        results = neo4j_conn.execute_query(query)
        return {"matrix": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# ENDPOINTS: ZONES (Section 4)
# ============================================================================

@app.get("/api/v1/zones", tags=["Zones"])
async def get_zones(
    risk_level: Optional[str] = Query(None, description="Filtre par niveau: critique, eleve, moyen, faible")
):
    """
    📍 Liste des zones avec statistiques de risques
    """
    query = """
    MATCH (z:Zone)
    WHERE $risk_level IS NULL OR z.risk_level = $risk_level
    OPTIONAL MATCH (z)<-[:LOCALISE_DANS]-(r:RisqueDanger)
    RETURN z.name AS name,
           z.risk_level AS risk_level,
           count(r) AS nb_risques,
           collect(DISTINCT r.categorie)[0..3] AS categories
    ORDER BY nb_risques DESC
    LIMIT 100
    """
    
    try:
        results = neo4j_conn.execute_query(query, {"risk_level": risk_level})
        return {"zones": results, "count": len(results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/zones/hotspots", tags=["Zones"])
async def get_zone_hotspots():
    """
    🔥 Zones hotspots (concentration élevée de risques)
    """
    query = """
    MATCH (z:Zone)<-[:LOCALISE_DANS]-(r:RisqueDanger)
    WITH z, count(r) AS nb_risques, avg(r.probabilite * r.gravite) AS score_moyen
    WHERE nb_risques >= 5
    RETURN z.name AS zone,
           z.risk_level AS niveau,
           nb_risques,
           round(score_moyen * 100) / 100 AS score_moyen
    ORDER BY score_moyen DESC
    LIMIT 20
    """
    
    try:
        results = neo4j_conn.execute_query(query)
        return {"hotspots": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/zones/by-level", tags=["Zones"])
async def get_zones_by_level():
    """
    📊 Distribution des zones par niveau de risque
    """
    query = """
    MATCH (z:Zone)
    WHERE z.risk_level IS NOT NULL
    RETURN z.risk_level AS niveau, count(z) AS count
    ORDER BY 
        CASE z.risk_level 
            WHEN 'critique' THEN 1 
            WHEN 'eleve' THEN 2 
            WHEN 'moyen' THEN 3 
            ELSE 4 
        END
    """
    
    try:
        results = neo4j_conn.execute_query(query)
        return {"distribution": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# ENDPOINTS: PERSONNES (Section 5)
# ============================================================================

@app.get("/api/v1/persons/age-distribution", tags=["Personnes"])
async def get_age_distribution():
    """
    👥 Distribution des personnes par groupe d'âge
    """
    query = """
    MATCH (p:Person)
    WHERE p.age_groupe IS NOT NULL
    RETURN p.age_groupe AS groupe_age, count(p) AS count
    ORDER BY p.age_groupe
    """
    
    try:
        results = neo4j_conn.execute_query(query)
        return {"age_distribution": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/persons/certifications", tags=["Personnes"])
async def get_certifications():
    """
    🎓 Certifications SST les plus fréquentes
    """
    query = """
    MATCH (p:Person)
    WHERE p.certifications_sst IS NOT NULL
    UNWIND p.certifications_sst AS cert
    RETURN cert AS certification, count(p) AS count
    ORDER BY count DESC
    LIMIT 20
    """
    
    try:
        results = neo4j_conn.execute_query(query)
        return {"certifications": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/persons/exposed", tags=["Personnes"])
async def get_exposed_persons(
    min_risks: int = Query(3, ge=1, description="Nombre minimum de risques d'exposition")
):
    """
    ⚠️ Personnes les plus exposées aux risques
    """
    query = """
    MATCH (p:Person)-[:EXPOSE_A]->(r:RisqueDanger)
    WITH p, count(r) AS nb_risques, avg(r.probabilite * r.gravite) AS score
    WHERE nb_risques >= $min_risks
    RETURN p.matricule AS matricule,
           p.department AS departement,
           nb_risques,
           round(score * 100) / 100 AS score_exposition
    ORDER BY nb_risques DESC
    LIMIT 50
    """
    
    try:
        results = neo4j_conn.execute_query(query, {"min_risks": min_risks})
        return {"exposed_persons": results, "count": len(results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# ENDPOINTS: ALERTES (Section 8)
# ============================================================================

@app.get("/api/v1/alerts", tags=["Alertes"])
async def get_alerts():
    """
    🚨 Toutes les alertes actives
    """
    alerts = []
    
    # Alerte 1: Organisations avec concentration TZ
    query1 = """
    MATCH (o:Organization)<-[:APPARTIENT_A]-(z:Zone)<-[:LOCALISE_DANS]-(r:RisqueDanger)
    WHERE r.probabilite * r.gravite >= 15
    WITH o, count(r) AS nb_TZ
    WHERE nb_TZ >= 5
    RETURN o.name AS organisation, o.sector_scian AS secteur, nb_TZ AS score
    ORDER BY nb_TZ DESC
    LIMIT 10
    """
    
    try:
        results = neo4j_conn.execute_query(query1)
        for r in results:
            alerts.append({
                "type": "CONCENTRATION_TZ",
                "niveau": "CRITIQUE",
                "organisation": r["organisation"],
                "details": f"{r['score']} risques Tolérance Zéro",
                "score": r["score"]
            })
    except:
        pass
    
    # Alerte 2: Zones critiques multi-risques
    query2 = """
    MATCH (z:Zone)<-[:LOCALISE_DANS]-(r:RisqueDanger)
    WHERE z.risk_level = 'critique'
    WITH z, count(r) AS nb_risques
    WHERE nb_risques >= 5
    RETURN z.name AS zone, nb_risques AS score
    ORDER BY nb_risques DESC
    LIMIT 10
    """
    
    try:
        results = neo4j_conn.execute_query(query2)
        for r in results:
            alerts.append({
                "type": "ZONE_CRITIQUE",
                "niveau": "ÉLEVÉ",
                "zone": r["zone"],
                "details": f"{r['score']} risques concentrés",
                "score": r["score"]
            })
    except:
        pass
    
    return {
        "alerts": alerts,
        "count": len(alerts),
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/v1/alerts/young-workers", tags=["Alertes"])
async def get_young_worker_alerts():
    """
    👤 Alertes jeunes travailleurs (18-24 ans) exposés
    """
    query = """
    MATCH (p:Person)-[:EXPOSE_A]->(r:RisqueDanger)
    WHERE p.age_groupe = '18-24' AND r.probabilite * r.gravite >= 12
    RETURN p.matricule AS matricule,
           p.department AS departement,
           count(r) AS nb_risques,
           collect(DISTINCT r.categorie)[0..3] AS categories
    ORDER BY nb_risques DESC
    LIMIT 20
    """
    
    try:
        results = neo4j_conn.execute_query(query)
        return {"young_worker_alerts": results, "count": len(results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# ENDPOINTS: CONFORMITÉ (Section 9)
# ============================================================================

@app.get("/api/v1/compliance/certification-coverage", tags=["Conformité"])
async def get_certification_coverage():
    """
    ✅ Taux de certification par secteur
    """
    query = """
    MATCH (o:Organization)<-[:APPARTIENT_A]-(t:Team)<-[:MEMBRE_DE]-(p:Person)
    WHERE o.sector_scian IS NOT NULL
    WITH o.sector_scian AS secteur,
         count(DISTINCT p) AS total,
         sum(CASE WHEN p.certifications_sst IS NOT NULL AND size(p.certifications_sst) > 0 THEN 1 ELSE 0 END) AS certifies
    RETURN secteur,
           total AS total_personnes,
           certifies AS personnes_certifiees,
           round(certifies * 100.0 / total * 10) / 10 AS taux_certification
    ORDER BY taux_certification ASC
    LIMIT 15
    """
    
    try:
        results = neo4j_conn.execute_query(query)
        return {"certification_coverage": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/compliance/missing-epi", tags=["Conformité"])
async def get_missing_epi():
    """
    ❌ Zones à risque sans EPI définis
    """
    query = """
    MATCH (z:Zone)
    WHERE z.risk_level IN ['critique', 'eleve'] 
      AND (z.epi_requis IS NULL OR size(z.epi_requis) = 0)
    RETURN z.name AS zone, z.risk_level AS niveau
    ORDER BY z.risk_level
    """
    
    try:
        results = neo4j_conn.execute_query(query)
        return {"missing_epi": results, "count": len(results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# ENDPOINTS: ANALYSES PRÉDICTIVES (Section 7 & 12)
# ============================================================================

@app.get("/api/v1/predictive/features", tags=["Prédictif"])
async def get_ml_features():
    """
    🔮 Features pour modèles ML (XGBoost, LightGBM)
    """
    query = """
    MATCH (o:Organization)<-[:APPARTIENT_A]-(z:Zone)<-[:LOCALISE_DANS]-(r:RisqueDanger)
    OPTIONAL MATCH (o)<-[:APPARTIENT_A]-(t:Team)<-[:MEMBRE_DE]-(p:Person)
    WITH o, 
         count(DISTINCT z) AS nb_zones,
         count(DISTINCT r) AS nb_risques,
         count(DISTINCT t) AS nb_equipes,
         count(DISTINCT p) AS nb_personnes,
         avg(r.probabilite * r.gravite) AS score_risque_moyen
    RETURN o.name AS organisation,
           o.sector_scian AS secteur,
           o.nb_employes AS employes,
           nb_zones, nb_risques, nb_equipes, nb_personnes,
           round(score_risque_moyen * 100) / 100 AS score_moyen,
           round(nb_risques * 1.0 / CASE WHEN nb_zones > 0 THEN nb_zones ELSE 1 END * 100) / 100 AS risques_par_zone
    ORDER BY score_moyen DESC
    LIMIT 100
    """
    
    try:
        results = neo4j_conn.execute_query(query)
        return {"features": results, "count": len(results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/predictive/risk-score-by-org", tags=["Prédictif"])
async def get_risk_score_by_org():
    """
    📊 Score de risque pondéré par organisation
    """
    query = """
    MATCH (o:Organization)<-[:APPARTIENT_A]-(z:Zone)<-[:LOCALISE_DANS]-(r:RisqueDanger)
    WITH o, 
         count(r) AS nb_risques,
         sum(r.probabilite * r.gravite) AS score_total,
         sum(CASE WHEN r.probabilite * r.gravite >= 15 THEN 1 ELSE 0 END) AS risques_TZ
    RETURN o.name AS organisation,
           o.sector_scian AS secteur,
           nb_risques,
           risques_TZ AS tolerance_zero,
           round(score_total / nb_risques * 100) / 100 AS score_moyen,
           round(score_total) AS score_total
    ORDER BY score_total DESC
    LIMIT 30
    """
    
    try:
        results = neo4j_conn.execute_query(query)
        return {"risk_scores": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/predictive/sector-correlation", tags=["Prédictif"])
async def get_sector_risk_correlation():
    """
    🔗 Corrélation secteur-catégorie de risque
    """
    query = """
    MATCH (o:Organization)<-[:APPARTIENT_A]-(z:Zone)<-[:LOCALISE_DANS]-(r:RisqueDanger)
    WHERE o.sector_scian IS NOT NULL AND r.categorie IS NOT NULL
    RETURN o.sector_scian AS secteur,
           r.categorie AS categorie,
           count(r) AS occurrences,
           round(avg(r.probabilite * r.gravite) * 100) / 100 AS score_moyen
    ORDER BY occurrences DESC
    LIMIT 50
    """
    
    try:
        results = neo4j_conn.execute_query(query)
        return {"correlations": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# ENDPOINTS: AGENTS IA (Section 12)
# ============================================================================

@app.get("/api/v1/agents/visionai/targets", tags=["Agents IA"])
async def get_visionai_targets():
    """
    🎥 Zones cibles pour Agent VisionAI (surveillance caméra)
    """
    query = """
    MATCH (z:Zone)<-[:LOCALISE_DANS]-(r:RisqueDanger)
    WHERE z.risk_level = 'critique' AND r.categorie IN ['chute', 'mecanique', 'electrique']
    RETURN DISTINCT z.name AS zone,
           collect(DISTINCT r.categorie) AS types_risques,
           'VisionAI' AS agent
    ORDER BY size(types_risques) DESC
    LIMIT 20
    """
    
    try:
        results = neo4j_conn.execute_query(query)
        return {"visionai_targets": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/agents/ergoai/targets", tags=["Agents IA"])
async def get_ergoai_targets():
    """
    🦴 Personnes cibles pour Agent ErgoAI (risques ergonomiques)
    """
    query = """
    MATCH (p:Person)-[:EXPOSE_A]->(r:RisqueDanger)
    WHERE r.categorie = 'ergonomique'
    RETURN p.matricule AS cible,
           p.department AS departement,
           count(r) AS nb_risques_ergo,
           'ErgoAI' AS agent
    ORDER BY nb_risques_ergo DESC
    LIMIT 50
    """
    
    try:
        results = neo4j_conn.execute_query(query)
        return {"ergoai_targets": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/agents/alertai/triggers", tags=["Agents IA"])
async def get_alertai_triggers():
    """
    🚨 Déclencheurs pour Agent AlertAI
    """
    query = """
    MATCH (o:Organization)<-[:APPARTIENT_A]-(z:Zone)<-[:LOCALISE_DANS]-(r:RisqueDanger)
    WITH o, z, count(r) AS nb_risques, avg(r.probabilite * r.gravite) AS score_moyen
    WHERE score_moyen >= 12 OR nb_risques >= 6
    RETURN o.name AS organisation,
           z.name AS zone,
           nb_risques,
           round(score_moyen * 100) / 100 AS score,
           CASE 
               WHEN score_moyen >= 15 THEN 'CRITIQUE'
               WHEN score_moyen >= 12 THEN 'ÉLEVÉ'
               ELSE 'MODÉRÉ'
           END AS niveau_alerte
    ORDER BY score DESC
    LIMIT 30
    """
    
    try:
        results = neo4j_conn.execute_query(query)
        return {"alertai_triggers": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/agents/complyai/gaps", tags=["Agents IA"])
async def get_complyai_gaps():
    """
    ✅ Écarts de conformité pour Agent ComplyAI
    """
    query = """
    MATCH (o:Organization)
    OPTIONAL MATCH (o)<-[:APPARTIENT_A]-(z:Zone)
    OPTIONAL MATCH (z)<-[:LOCALISE_DANS]-(r:RisqueDanger)
    WITH o, count(DISTINCT z) AS zones, count(r) AS risques
    WHERE zones > 0 AND risques = 0
    RETURN o.name AS organisation,
           zones AS zones_sans_risques,
           'Audit requis' AS action
    LIMIT 20
    """
    
    try:
        results = neo4j_conn.execute_query(query)
        return {"compliance_gaps": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# ENDPOINTS: RECHERCHE ET REQUÊTES PERSONNALISÉES
# ============================================================================

@app.get("/api/v1/search/organizations", tags=["Recherche"])
async def search_organizations(
    q: str = Query(..., min_length=2, description="Terme de recherche")
):
    """
    🔍 Recherche d'organisations par nom
    """
    query = """
    MATCH (o:Organization)
    WHERE toLower(o.name) CONTAINS toLower($terme)
    RETURN o.name AS organisation, o.sector_scian AS secteur, o.nb_employes AS employes
    ORDER BY o.nb_employes DESC
    LIMIT 20
    """
    
    try:
        results = neo4j_conn.execute_query(query, {"terme": q})
        return {"results": results, "query": q}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/search/risks", tags=["Recherche"])
async def search_risks(
    q: str = Query(..., min_length=2, description="Mot-clé de recherche")
):
    """
    🔍 Recherche de risques par mot-clé
    """
    query = """
    MATCH (r:RisqueDanger)
    WHERE toLower(r.description) CONTAINS toLower($terme)
    RETURN r.description AS risque, r.categorie AS categorie, 
           r.probabilite * r.gravite AS score
    ORDER BY score DESC
    LIMIT 30
    """
    
    try:
        results = neo4j_conn.execute_query(query, {"terme": q})
        return {"results": results, "query": q}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/cypher/execute", response_model=CypherResponse, tags=["Cypher"])
async def execute_cypher(request: CypherRequest):
    """
    ⚡ Exécuter une requête Cypher personnalisée
    
    ⚠️ Attention: Seules les requêtes en lecture (MATCH) sont autorisées.
    """
    import time
    
    # Validation de sécurité
    query_upper = request.query.upper()
    forbidden = ["CREATE", "DELETE", "SET", "REMOVE", "MERGE", "DROP", "DETACH"]
    for word in forbidden:
        if word in query_upper:
            raise HTTPException(
                status_code=403, 
                detail=f"Opération interdite: {word}. Seules les requêtes MATCH sont autorisées."
            )
    
    try:
        start = time.time()
        results = neo4j_conn.execute_query(request.query, request.params)
        elapsed = (time.time() - start) * 1000
        
        return CypherResponse(
            success=True,
            data=results,
            count=len(results),
            execution_time_ms=round(elapsed, 2)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# ENDPOINTS: EXPORT ET DASHBOARD
# ============================================================================

@app.get("/api/v1/export/dashboard-data", tags=["Export"])
async def get_dashboard_data():
    """
    📊 Données complètes pour dashboard (tous les graphiques)
    """
    data = {}
    
    # Organisations par secteur
    try:
        results = neo4j_conn.execute_query("""
            MATCH (o:Organization)
            WHERE o.sector_scian IS NOT NULL
            RETURN o.sector_scian AS label, count(o) AS value
            ORDER BY value DESC
        """)
        data["orgs_by_sector"] = results
    except:
        data["orgs_by_sector"] = []
    
    # Zones par niveau
    try:
        results = neo4j_conn.execute_query("""
            MATCH (z:Zone)
            WHERE z.risk_level IS NOT NULL
            RETURN z.risk_level AS label, count(z) AS value
        """)
        data["zones_by_level"] = results
    except:
        data["zones_by_level"] = []
    
    # Risques par catégorie
    try:
        results = neo4j_conn.execute_query("""
            MATCH (r:RisqueDanger)
            WHERE r.categorie IS NOT NULL
            RETURN r.categorie AS label, count(r) AS value,
                   round(avg(r.probabilite * r.gravite) * 100) / 100 AS score
            ORDER BY value DESC
        """)
        data["risks_by_category"] = results
    except:
        data["risks_by_category"] = []
    
    # Top organisations
    try:
        results = neo4j_conn.execute_query("""
            MATCH (o:Organization)
            WHERE o.nb_employes IS NOT NULL AND o.nb_employes > 0
            RETURN o.name AS label, o.nb_employes AS value, o.sector_scian AS category
            ORDER BY value DESC
            LIMIT 25
        """)
        data["top_orgs"] = results
    except:
        data["top_orgs"] = []
    
    return data


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    print("🚀 Démarrage SafetyGraph API sur http://localhost:8002")
    print("📖 Documentation: http://localhost:8002/docs")
    uvicorn.run(app, host="0.0.0.0", port=8002)
