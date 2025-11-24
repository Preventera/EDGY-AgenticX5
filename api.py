#!/usr/bin/env python3
"""
API FastAPI - EDGY-AgenticX5
Endpoints REST pour le système de prévention SST

Endpoints:
- /health - Status du système
- /api/v1/workflow/process - Traiter des lectures capteurs
- /api/v1/zones - Lister les zones
- /api/v1/risks - Lister les risques
- /api/v1/alerts - Alertes actives
- /api/v1/near-misses - Near-misses détectés
- /api/v1/stats - Statistiques du système
"""

import os
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional
from contextlib import asynccontextmanager

# Ajouter le chemin src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from neo4j import GraphDatabase

# Import des modules internes
try:
    from orchestration.langgraph_orchestrator import LangGraphOrchestrator, LANGGRAPH_AVAILABLE
    ORCHESTRATOR_AVAILABLE = True
except ImportError:
    ORCHESTRATOR_AVAILABLE = False
    LANGGRAPH_AVAILABLE = False


# ============================================
# CONFIGURATION
# ============================================

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "")
API_VERSION = "1.0.0"


# ============================================
# MODÈLES PYDANTIC
# ============================================

class SensorReading(BaseModel):
    """Lecture d'un capteur"""
    sensor_id: str = Field(..., description="Identifiant du capteur")
    sensor_type: str = Field(..., description="Type: temperature, noise, gas, humidity")
    value: float = Field(..., description="Valeur mesurée")
    unit: str = Field(default="", description="Unité de mesure")
    timestamp: Optional[str] = Field(default=None, description="Horodatage ISO")
    zone_id: Optional[str] = Field(default=None, description="Zone concernée")
    location: Optional[str] = Field(default=None, description="Localisation")


class WorkflowRequest(BaseModel):
    """Requête de traitement workflow"""
    sensor_readings: List[SensorReading]
    zone_id: str = Field(default="ZONE-001", description="Zone à analyser")


class WorkflowResponse(BaseModel):
    """Réponse du workflow"""
    status: str
    workflow_id: str
    risk_level: Optional[str] = None
    risk_score: Optional[float] = None
    alerts: List[Dict[str, Any]] = []
    recommendations: List[Dict[str, Any]] = []
    notifications: List[Dict[str, Any]] = []
    processing_times: Dict[str, float] = {}


class ZoneResponse(BaseModel):
    """Zone SST"""
    zone_id: str
    nom: Optional[str] = None
    type: Optional[str] = None
    niveau_risque: Optional[str] = None
    risques: List[str] = []


class RiskResponse(BaseModel):
    """Risque identifié"""
    risque_id: str
    description: Optional[str] = None
    categorie: Optional[str] = None
    severite: Optional[str] = None
    zone_id: Optional[str] = None


class NearMissResponse(BaseModel):
    """Near-Miss détecté"""
    near_miss_id: str
    type_risque: Optional[str] = None
    potentiel_gravite: Optional[str] = None
    description: Optional[str] = None
    zone_id: Optional[str] = None
    detecte_par_agent: Optional[str] = None
    created_at: Optional[str] = None


class HealthResponse(BaseModel):
    """Status de santé du système"""
    status: str
    version: str
    timestamp: str
    components: Dict[str, bool]
    neo4j_stats: Dict[str, Any]


class StatsResponse(BaseModel):
    """Statistiques du système"""
    workflows_executed: int = 0
    workflows_successful: int = 0
    success_rate: float = 0.0
    alerts_generated: int = 0
    recommendations_generated: int = 0
    neo4j_nodes: int = 0
    neo4j_relationships: int = 0


# ============================================
# CONNECTEUR NEO4J
# ============================================

class Neo4jConnector:
    """Connecteur Neo4j pour l'API"""
    
    def __init__(self):
        self.uri = NEO4J_URI
        self.driver = None
        self.mock_mode = False
    
    def connect(self):
        """Établir la connexion"""
        try:
            if NEO4J_PASSWORD:
                self.driver = GraphDatabase.driver(self.uri, auth=(NEO4J_USER, NEO4J_PASSWORD))
            else:
                self.driver = GraphDatabase.driver(self.uri, auth=None)
            # Test connexion
            with self.driver.session() as session:
                session.run("RETURN 1")
            return True
        except Exception as e:
            print(f"Erreur connexion Neo4j: {e}")
            self.mock_mode = True
            return False
    
    def close(self):
        """Fermer la connexion"""
        if self.driver:
            self.driver.close()
    
    def get_zones(self) -> List[Dict]:
        """Récupérer toutes les zones"""
        if self.mock_mode:
            return [{"zone_id": "ZONE-DEMO", "nom": "Zone Demo", "type": None, "niveau_risque": "medium", "risques": []}]
        
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (z:Zone)
                    OPTIONAL MATCH (z)-[:A_RISQUE]->(r:Risque)
                    RETURN z.zone_id as zone_id, z.nom as nom, z.type as type,
                           z.niveau_risque as niveau_risque,
                           collect(COALESCE(r.description, '')) as risques
                """)
                zones = []
                for record in result:
                    zone = {
                        "zone_id": record["zone_id"] or "unknown",
                        "nom": record["nom"],
                        "type": record["type"],
                        "niveau_risque": record["niveau_risque"],
                        "risques": [r for r in record["risques"] if r]
                    }
                    zones.append(zone)
                return zones
        except Exception as e:
            print(f"Erreur get_zones: {e}")
            return []
    
    def get_risks(self) -> List[Dict]:
        """Récupérer tous les risques"""
        if self.mock_mode:
            return [{"risque_id": "RISK-DEMO", "description": "Risque Demo", "severite": "medium"}]
        
        with self.driver.session() as session:
            result = session.run("""
                MATCH (r:Risque)
                OPTIONAL MATCH (z:Zone)-[:A_RISQUE]->(r)
                RETURN r.risque_id as risque_id, r.description as description,
                       r.categorie as categorie, r.severite as severite,
                       z.zone_id as zone_id
            """)
            return [dict(record) for record in result]
    
    def get_near_misses(self, limit: int = 20) -> List[Dict]:
        """Récupérer les near-misses récents"""
        if self.mock_mode:
            return []
        
        with self.driver.session() as session:
            result = session.run("""
                MATCH (nm:NearMiss)
                RETURN nm.near_miss_id as near_miss_id,
                       nm.type_risque as type_risque,
                       nm.potentiel_gravite as potentiel_gravite,
                       nm.description as description,
                       nm.zone_id as zone_id,
                       nm.detecte_par_agent as detecte_par_agent,
                       toString(nm.created_at) as created_at
                ORDER BY nm.created_at DESC
                LIMIT $limit
            """, limit=limit)
            return [dict(record) for record in result]
    
    def get_stats(self) -> Dict:
        """Récupérer les statistiques Neo4j"""
        if self.mock_mode:
            return {"nodes": 0, "relationships": 0, "connected": False}
        
        with self.driver.session() as session:
            result = session.run("MATCH (n) RETURN count(n) as nodes")
            nodes = result.single()["nodes"]
            
            result = session.run("MATCH ()-[r]->() RETURN count(r) as rels")
            rels = result.single()["rels"]
            
            return {"nodes": nodes, "relationships": rels, "connected": True}
    
    def enrich_context_for_agent(self, zone_id=None, worker_id=None, equipment_id=None):
        """Enrichir le contexte pour les agents"""
        context = {}
        if self.mock_mode or not zone_id:
            return context
        
        with self.driver.session() as session:
            result = session.run("""
                MATCH (z:Zone)
                WHERE z.zone_id = $zone_id OR z.nom CONTAINS $zone_id
                OPTIONAL MATCH (z)-[:A_RISQUE]->(r:Risque)
                RETURN z.zone_id as zone_id, z.nom as nom,
                       z.niveau_risque as niveau_risque,
                       collect(r.description) as risques
                LIMIT 1
            """, zone_id=zone_id)
            
            record = result.single()
            if record:
                context["zone"] = dict(record)
        
        return context
    
    def create_near_miss(self, near_miss_id, type_risque, potentiel_gravite,
                        description, zone_id, detecte_par_agent):
        """Créer un Near-Miss"""
        if self.mock_mode:
            return near_miss_id
        
        with self.driver.session() as session:
            session.run("""
                MERGE (nm:NearMiss {near_miss_id: $near_miss_id})
                SET nm.type_risque = $type_risque,
                    nm.potentiel_gravite = $potentiel_gravite,
                    nm.description = $description,
                    nm.zone_id = $zone_id,
                    nm.detecte_par_agent = $detecte_par_agent,
                    nm.created_at = datetime()
            """, near_miss_id=near_miss_id, type_risque=type_risque,
                potentiel_gravite=potentiel_gravite, description=description,
                zone_id=zone_id, detecte_par_agent=detecte_par_agent)
        
        return near_miss_id


# ============================================
# APPLICATION FASTAPI
# ============================================

# Variables globales
neo4j_connector: Optional[Neo4jConnector] = None
orchestrator: Optional[LangGraphOrchestrator] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestion du cycle de vie de l'application"""
    global neo4j_connector, orchestrator
    
    # Startup
    print("=" * 50)
    print("  EDGY-AgenticX5 API - Demarrage")
    print("=" * 50)
    
    # Connexion Neo4j
    neo4j_connector = Neo4jConnector()
    if neo4j_connector.connect():
        print(f"  [OK] Neo4j connecte: {NEO4J_URI}")
    else:
        print(f"  [WARN] Neo4j non disponible - Mode demo")
    
    # Initialiser l'orchestrateur
    if ORCHESTRATOR_AVAILABLE:
        orchestrator = LangGraphOrchestrator(neo4j_connector=neo4j_connector)
        print(f"  [OK] LangGraph Orchestrator initialise")
    else:
        print(f"  [WARN] Orchestrator non disponible")
    
    print("=" * 50)
    print(f"  API prete sur http://localhost:8000")
    print(f"  Documentation: http://localhost:8000/docs")
    print("=" * 50)
    
    yield
    
    # Shutdown
    if neo4j_connector:
        neo4j_connector.close()
    print("  [OK] API arretee proprement")


# Créer l'application
app = FastAPI(
    title="EDGY-AgenticX5 API",
    description="API REST pour le système de prévention SST multi-agents",
    version=API_VERSION,
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================
# ENDPOINTS
# ============================================

@app.get("/", tags=["Root"])
async def root():
    """Page d'accueil de l'API"""
    return {
        "message": "EDGY-AgenticX5 API",
        "version": API_VERSION,
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Vérifier l'état de santé du système"""
    neo4j_stats = neo4j_connector.get_stats() if neo4j_connector else {"connected": False}
    
    return HealthResponse(
        status="healthy",
        version=API_VERSION,
        timestamp=datetime.utcnow().isoformat(),
        components={
            "neo4j": neo4j_stats.get("connected", False),
            "orchestrator": orchestrator is not None,
            "langgraph": LANGGRAPH_AVAILABLE
        },
        neo4j_stats=neo4j_stats
    )


@app.post("/api/v1/workflow/process", response_model=WorkflowResponse, tags=["Workflow"])
async def process_workflow(request: WorkflowRequest):
    """
    Traiter des lectures de capteurs via le workflow LangGraph
    
    Analyse les données, détecte les risques, génère des recommandations
    et crée des alertes si nécessaire.
    """
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator non disponible")
    
    # Convertir les lectures en dictionnaires
    readings = []
    for r in request.sensor_readings:
        reading = r.model_dump()
        if not reading.get("timestamp"):
            reading["timestamp"] = datetime.utcnow().isoformat()
        readings.append(reading)
    
    # Exécuter le workflow
    result = orchestrator.process(readings, zone_id=request.zone_id)
    
    return WorkflowResponse(
        status=result.get("status", "error"),
        workflow_id=result.get("workflow_id", "unknown"),
        risk_level=result.get("risk_level"),
        risk_score=result.get("risk_score"),
        alerts=result.get("alerts", []),
        recommendations=result.get("recommendations", []),
        notifications=result.get("notifications", []),
        processing_times=result.get("processing_times", {})
    )


@app.get("/api/v1/zones", response_model=List[ZoneResponse], tags=["Zones"])
async def get_zones():
    """Lister toutes les zones SST"""
    if not neo4j_connector:
        raise HTTPException(status_code=503, detail="Neo4j non disponible")
    
    zones = neo4j_connector.get_zones()
    return [ZoneResponse(**z) for z in zones]


@app.get("/api/v1/zones/{zone_id}", response_model=ZoneResponse, tags=["Zones"])
async def get_zone(zone_id: str):
    """Récupérer une zone spécifique"""
    if not neo4j_connector:
        raise HTTPException(status_code=503, detail="Neo4j non disponible")
    
    zones = neo4j_connector.get_zones()
    for z in zones:
        if z.get("zone_id") == zone_id:
            return ZoneResponse(**z)
    
    raise HTTPException(status_code=404, detail=f"Zone {zone_id} non trouvée")


@app.get("/api/v1/risks", response_model=List[RiskResponse], tags=["Risques"])
async def get_risks():
    """Lister tous les risques identifiés"""
    if not neo4j_connector:
        raise HTTPException(status_code=503, detail="Neo4j non disponible")
    
    risks = neo4j_connector.get_risks()
    return [RiskResponse(**r) for r in risks]


@app.get("/api/v1/near-misses", response_model=List[NearMissResponse], tags=["Near-Misses"])
async def get_near_misses(limit: int = 20):
    """Lister les near-misses détectés récemment"""
    if not neo4j_connector:
        raise HTTPException(status_code=503, detail="Neo4j non disponible")
    
    near_misses = neo4j_connector.get_near_misses(limit=limit)
    return [NearMissResponse(**nm) for nm in near_misses]


@app.get("/api/v1/stats", response_model=StatsResponse, tags=["Statistiques"])
async def get_stats():
    """Récupérer les statistiques du système"""
    neo4j_stats = neo4j_connector.get_stats() if neo4j_connector else {}
    orchestrator_stats = orchestrator.get_statistics() if orchestrator else {}
    
    return StatsResponse(
        workflows_executed=orchestrator_stats.get("workflows_executed", 0),
        workflows_successful=orchestrator_stats.get("workflows_successful", 0),
        success_rate=orchestrator_stats.get("success_rate", 0.0),
        alerts_generated=orchestrator_stats.get("alerts_generated", 0),
        recommendations_generated=orchestrator_stats.get("recommendations_generated", 0),
        neo4j_nodes=neo4j_stats.get("nodes", 0),
        neo4j_relationships=neo4j_stats.get("relationships", 0)
    )


@app.post("/api/v1/simulate/critical", response_model=WorkflowResponse, tags=["Simulation"])
async def simulate_critical_event():
    """
    Simuler un événement critique pour test
    
    Génère des lectures de capteurs critiques (température 45°C, bruit 92dB)
    """
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator non disponible")
    
    # Données critiques simulées
    readings = [
        {
            "sensor_id": "SIM-TEMP-001",
            "sensor_type": "temperature",
            "value": 45.0,
            "unit": "C",
            "timestamp": datetime.utcnow().isoformat(),
            "zone_id": "ZONE-PROD-001",
            "location": "Simulation"
        },
        {
            "sensor_id": "SIM-NOISE-001",
            "sensor_type": "noise",
            "value": 92.0,
            "unit": "dB",
            "timestamp": datetime.utcnow().isoformat(),
            "zone_id": "ZONE-PROD-001",
            "location": "Simulation"
        }
    ]
    
    result = orchestrator.process(readings, zone_id="ZONE-PROD-001")
    
    return WorkflowResponse(
        status=result.get("status", "error"),
        workflow_id=result.get("workflow_id", "unknown"),
        risk_level=result.get("risk_level"),
        risk_score=result.get("risk_score"),
        alerts=result.get("alerts", []),
        recommendations=result.get("recommendations", []),
        notifications=result.get("notifications", []),
        processing_times=result.get("processing_times", {})
    )


# ============================================
# POINT D'ENTRÉE
# ============================================

if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "=" * 50)
    print("  EDGY-AgenticX5 - API FastAPI")
    print("=" * 50 + "\n")
    
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
