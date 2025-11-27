"""
EDGY-AgenticX5 API v2.0 - Avec Intégration CNESST
=================================================
API FastAPI incluant les données réelles CNESST (793K+ incidents)

Auteur: Mario Genest - GenAISafety/Preventera
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import uvicorn
import os

# Import du connecteur CNESST
from cnesst_connector import CNESSTConnector, create_cnesst_routes

# ============================================================
# CONFIGURATION
# ============================================================

app = FastAPI(
    title="EDGY-AgenticX5 API",
    description="API de cartographie organisationnelle avec données CNESST",
    version="2.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialiser le connecteur CNESST
cnesst_connector = CNESSTConnector(data_dir="data")

# Ajouter les routes CNESST
create_cnesst_routes(app, cnesst_connector)


# ============================================================
# MODÈLES PYDANTIC
# ============================================================

class Organization(BaseModel):
    id: Optional[str] = None
    name: str
    type: str = "enterprise"
    sector_scian: Optional[str] = None
    description: Optional[str] = None
    employee_count: Optional[int] = None
    
class Person(BaseModel):
    id: Optional[str] = None
    name: str
    role: str
    department: Optional[str] = None
    risk_level: str = "moyen"
    email: Optional[str] = None

class Team(BaseModel):
    id: Optional[str] = None
    name: str
    department: str
    manager_id: Optional[str] = None
    
class Zone(BaseModel):
    id: Optional[str] = None
    name: str
    type: str
    risk_level: str = "moyen"
    capacity: Optional[int] = None

class Process(BaseModel):
    id: Optional[str] = None
    name: str
    type: str
    risk_level: str = "moyen"
    zone_id: Optional[str] = None

class Relation(BaseModel):
    id: Optional[str] = None
    source_id: str
    target_id: str
    relation_type: str
    weight: float = 1.0


# ============================================================
# STOCKAGE EN MÉMOIRE
# ============================================================

data_store = {
    "organizations": [],
    "persons": [],
    "teams": [],
    "zones": [],
    "processes": [],
    "relations": []
}

id_counter = {"value": 1}

def generate_id(prefix: str) -> str:
    id_counter["value"] += 1
    return f"{prefix}_{id_counter['value']}"


# ============================================================
# ENDPOINTS RACINE
# ============================================================

@app.get("/")
async def root():
    """Point d'entrée de l'API"""
    cnesst_status = cnesst_connector.get_available_files()
    return {
        "name": "EDGY-AgenticX5 API",
        "version": "2.0.0",
        "status": "running",
        "cnesst_integration": {
            "enabled": True,
            "files_count": len(cnesst_status),
            "years": [f["year"] for f in cnesst_status]
        },
        "endpoints": {
            "cartography": "/cartography/*",
            "cnesst": "/cnesst/*",
            "health": "/health"
        }
    }

@app.get("/health")
async def health():
    """Vérification de santé"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "cnesst_connected": len(cnesst_connector.get_available_files()) > 0
    }


# ============================================================
# ENDPOINTS CARTOGRAPHIE - ORGANIZATIONS
# ============================================================

@app.get("/cartography/organizations")
async def list_organizations():
    return {"count": len(data_store["organizations"]), "data": data_store["organizations"]}

@app.post("/cartography/organizations")
async def create_organization(org: Organization):
    org_dict = org.dict()
    org_dict["id"] = generate_id("org")
    org_dict["created_at"] = datetime.now().isoformat()
    data_store["organizations"].append(org_dict)
    return org_dict


# ============================================================
# ENDPOINTS CARTOGRAPHIE - PERSONS
# ============================================================

@app.get("/cartography/persons")
async def list_persons():
    return {"count": len(data_store["persons"]), "data": data_store["persons"]}

@app.post("/cartography/persons")
async def create_person(person: Person):
    person_dict = person.dict()
    person_dict["id"] = generate_id("person")
    person_dict["created_at"] = datetime.now().isoformat()
    data_store["persons"].append(person_dict)
    return person_dict


# ============================================================
# ENDPOINTS CARTOGRAPHIE - TEAMS
# ============================================================

@app.get("/cartography/teams")
async def list_teams():
    return {"count": len(data_store["teams"]), "data": data_store["teams"]}

@app.post("/cartography/teams")
async def create_team(team: Team):
    team_dict = team.dict()
    team_dict["id"] = generate_id("team")
    team_dict["created_at"] = datetime.now().isoformat()
    data_store["teams"].append(team_dict)
    return team_dict


# ============================================================
# ENDPOINTS CARTOGRAPHIE - ZONES
# ============================================================

@app.get("/cartography/zones")
async def list_zones():
    return {"count": len(data_store["zones"]), "data": data_store["zones"]}

@app.post("/cartography/zones")
async def create_zone(zone: Zone):
    zone_dict = zone.dict()
    zone_dict["id"] = generate_id("zone")
    zone_dict["created_at"] = datetime.now().isoformat()
    data_store["zones"].append(zone_dict)
    return zone_dict


# ============================================================
# ENDPOINTS CARTOGRAPHIE - PROCESSES
# ============================================================

@app.get("/cartography/processes")
async def list_processes():
    return {"count": len(data_store["processes"]), "data": data_store["processes"]}

@app.post("/cartography/processes")
async def create_process(process: Process):
    process_dict = process.dict()
    process_dict["id"] = generate_id("process")
    process_dict["created_at"] = datetime.now().isoformat()
    data_store["processes"].append(process_dict)
    return process_dict


# ============================================================
# ENDPOINTS CARTOGRAPHIE - RELATIONS
# ============================================================

@app.get("/cartography/relations")
async def list_relations():
    return {"count": len(data_store["relations"]), "data": data_store["relations"]}

@app.post("/cartography/relations")
async def create_relation(relation: Relation):
    relation_dict = relation.dict()
    relation_dict["id"] = generate_id("rel")
    relation_dict["created_at"] = datetime.now().isoformat()
    data_store["relations"].append(relation_dict)
    return relation_dict


# ============================================================
# ENDPOINTS STATISTIQUES
# ============================================================

@app.get("/cartography/stats")
async def get_stats():
    """Statistiques de la cartographie"""
    risk_counts = {"faible": 0, "moyen": 0, "eleve": 0, "critique": 0}
    
    for person in data_store["persons"]:
        level = person.get("risk_level", "moyen").lower()
        if level in risk_counts:
            risk_counts[level] += 1
    
    for zone in data_store["zones"]:
        level = zone.get("risk_level", "moyen").lower()
        if level in risk_counts:
            risk_counts[level] += 1
            
    for process in data_store["processes"]:
        level = process.get("risk_level", "moyen").lower()
        if level in risk_counts:
            risk_counts[level] += 1
    
    return {
        "organizations": len(data_store["organizations"]),
        "persons": len(data_store["persons"]),
        "teams": len(data_store["teams"]),
        "zones": len(data_store["zones"]),
        "processes": len(data_store["processes"]),
        "relations": len(data_store["relations"]),
        "risk_distribution": risk_counts
    }


# ============================================================
# ENDPOINT DEMO - PEUPLER AVEC DONNÉES EXEMPLE
# ============================================================

@app.post("/cartography/demo/populate")
async def populate_demo_data():
    """Peuple avec des données de démonstration"""
    global data_store, id_counter
    
    # Reset
    data_store = {
        "organizations": [],
        "persons": [],
        "teams": [],
        "zones": [],
        "processes": [],
        "relations": []
    }
    id_counter = {"value": 0}
    
    # Organisation
    org = {
        "id": generate_id("org"),
        "name": "Firme Manufacturière ABC",
        "type": "enterprise",
        "sector_scian": "31-33",
        "description": "Entreprise manufacturière québécoise",
        "employee_count": 150,
        "created_at": datetime.now().isoformat()
    }
    data_store["organizations"].append(org)
    
    # Équipes
    teams = [
        {"name": "Production", "department": "Opérations"},
        {"name": "Maintenance", "department": "Technique"},
        {"name": "Qualité", "department": "Contrôle"}
    ]
    for t in teams:
        team = {"id": generate_id("team"), **t, "created_at": datetime.now().isoformat()}
        data_store["teams"].append(team)
    
    # Personnes
    persons = [
        {"name": "Jean Lavoie", "role": "Superviseur Production", "department": "Production", "risk_level": "moyen"},
        {"name": "Marie Tremblay", "role": "Technicienne Maintenance", "department": "Maintenance", "risk_level": "eleve"},
        {"name": "Sophie Martin", "role": "Opératrice", "department": "Production", "risk_level": "moyen"},
        {"name": "Pierre Gagnon", "role": "Contrôleur Qualité", "department": "Qualité", "risk_level": "faible"}
    ]
    for p in persons:
        person = {"id": generate_id("person"), **p, "created_at": datetime.now().isoformat()}
        data_store["persons"].append(person)
    
    # Zones
    zones = [
        {"name": "Atelier Principal", "type": "production", "risk_level": "moyen", "capacity": 50},
        {"name": "Zone Maintenance", "type": "technique", "risk_level": "eleve", "capacity": 10},
        {"name": "Entrepôt", "type": "stockage", "risk_level": "faible", "capacity": 100}
    ]
    for z in zones:
        zone = {"id": generate_id("zone"), **z, "created_at": datetime.now().isoformat()}
        data_store["zones"].append(zone)
    
    # Processus
    processes = [
        {"name": "Assemblage", "type": "fabrication", "risk_level": "moyen"},
        {"name": "Soudure", "type": "fabrication", "risk_level": "eleve"},
        {"name": "Emballage", "type": "logistique", "risk_level": "faible"}
    ]
    for pr in processes:
        process = {"id": generate_id("process"), **pr, "created_at": datetime.now().isoformat()}
        data_store["processes"].append(process)
    
    # Relations
    relations = [
        {"source_id": "person_2", "target_id": "team_1", "relation_type": "membre_de"},
        {"source_id": "person_3", "target_id": "team_2", "relation_type": "membre_de"},
        {"source_id": "zone_1", "target_id": "process_1", "relation_type": "contient"}
    ]
    for r in relations:
        rel = {"id": generate_id("rel"), **r, "weight": 1.0, "created_at": datetime.now().isoformat()}
        data_store["relations"].append(rel)
    
    return {
        "status": "success",
        "message": "Données de démonstration créées",
        "counts": {
            "organizations": len(data_store["organizations"]),
            "teams": len(data_store["teams"]),
            "persons": len(data_store["persons"]),
            "zones": len(data_store["zones"]),
            "processes": len(data_store["processes"]),
            "relations": len(data_store["relations"])
        }
    }


# ============================================================
# ENDPOINT COMBINÉ - CARTOGRAPHIE + CNESST
# ============================================================

@app.get("/dashboard/combined-stats")
async def combined_stats():
    """Statistiques combinées cartographie + CNESST"""
    
    # Stats cartographie
    carto_stats = await get_stats()
    
    # Stats CNESST
    cnesst_summary = cnesst_connector.get_summary_statistics()
    
    return {
        "cartography": carto_stats,
        "cnesst": {
            "total_incidents": cnesst_summary.get("total_incidents", 0),
            "years_available": cnesst_summary.get("years_available", []),
            "by_year": cnesst_summary.get("by_year", [])
        },
        "timestamp": datetime.now().isoformat()
    }


# ============================================================
# POINT D'ENTRÉE
# ============================================================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 EDGY-AgenticX5 API v2.0 avec CNESST")
    print("="*60)
    
    # Vérifier les données CNESST
    files = cnesst_connector.get_available_files()
    if files:
        print(f"✅ {len(files)} fichiers CNESST détectés")
        for f in files:
            print(f"   - {f['year']}: {f['size_mb']} Mo")
    else:
        print("⚠️ Aucun fichier CNESST trouvé dans data/cnesst/")
    
    print("\n📡 Démarrage du serveur...")
    print("   API: http://localhost:8000")
    print("   Docs: http://localhost:8000/docs")
    print("="*60 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
