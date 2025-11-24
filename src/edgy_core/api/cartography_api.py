#!/usr/bin/env python3
"""
API de Cartographie EDGY - EDGY-AgenticX5
Interface pour saisir, gérer et visualiser la cartographie organisationnelle

Endpoints:
- /cartography/organization : Gérer l'organisation
- /cartography/persons : Gérer les personnes
- /cartography/teams : Gérer les équipes
- /cartography/roles : Gérer les rôles
- /cartography/processes : Gérer les processus SST
- /cartography/zones : Gérer les zones de risque
- /cartography/export : Exporter en RDF/JSON-LD
- /cartography/validate : Valider avec SHACL
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import uuid
import json

# ============================================================
# ÉNUMÉRATIONS
# ============================================================

class RiskLevel(str, Enum):
    """Niveaux de risque SST"""
    MINIMAL = "minimal"
    FAIBLE = "faible"
    MOYEN = "moyen"
    ELEVE = "élevé"
    CRITIQUE = "critique"


class EntityType(str, Enum):
    """Types d'entités EDGY"""
    ORGANIZATION = "organization"
    PERSON = "person"
    TEAM = "team"
    ROLE = "role"
    PROCESS = "process"
    ZONE = "zone"
    CAPABILITY = "capability"
    ASSET = "asset"


class ProcessType(str, Enum):
    """Types de processus SST"""
    INSPECTION = "inspection"
    AUDIT = "audit"
    FORMATION = "formation"
    INCIDENT = "incident"
    MAINTENANCE = "maintenance"
    PREVENTION = "prevention"
    INTERVENTION = "intervention"


# ============================================================
# MODÈLES DE DONNÉES
# ============================================================

class OrganizationCreate(BaseModel):
    """Créer une organisation"""
    name: str = Field(..., min_length=2, max_length=200)
    description: Optional[str] = None
    sector: Optional[str] = Field(None, description="Code SCIAN du secteur")
    size: Optional[str] = Field(None, description="PME, Moyenne, Grande")
    address: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class OrganizationResponse(BaseModel):
    """Réponse organisation"""
    id: str
    name: str
    description: Optional[str]
    sector: Optional[str]
    size: Optional[str]
    address: Optional[str]
    created_at: datetime
    updated_at: datetime
    entities_count: int = 0


class PersonCreate(BaseModel):
    """Créer une personne"""
    name: str = Field(..., min_length=2, max_length=100)
    email: Optional[str] = None
    phone: Optional[str] = None
    employee_id: Optional[str] = None
    department: Optional[str] = None
    role_ids: Optional[List[str]] = []
    team_ids: Optional[List[str]] = []
    supervisor_id: Optional[str] = None
    certifications: Optional[List[str]] = []
    metadata: Optional[Dict[str, Any]] = None


class PersonResponse(BaseModel):
    """Réponse personne"""
    id: str
    name: str
    email: Optional[str]
    employee_id: Optional[str]
    department: Optional[str]
    roles: List[str] = []
    teams: List[str] = []
    supervisor_id: Optional[str]
    created_at: datetime


class TeamCreate(BaseModel):
    """Créer une équipe"""
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None
    department: Optional[str] = None
    leader_id: Optional[str] = None
    member_ids: Optional[List[str]] = []
    zone_ids: Optional[List[str]] = []
    metadata: Optional[Dict[str, Any]] = None


class TeamResponse(BaseModel):
    """Réponse équipe"""
    id: str
    name: str
    description: Optional[str]
    department: Optional[str]
    leader_id: Optional[str]
    members_count: int = 0
    zones: List[str] = []
    created_at: datetime


class RoleCreate(BaseModel):
    """Créer un rôle"""
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None
    responsibilities: Optional[List[str]] = []
    required_certifications: Optional[List[str]] = []
    sst_level: Optional[str] = Field(None, description="Niveau SST requis")
    can_supervise: bool = False
    can_approve_actions: bool = False
    metadata: Optional[Dict[str, Any]] = None


class RoleResponse(BaseModel):
    """Réponse rôle"""
    id: str
    name: str
    description: Optional[str]
    responsibilities: List[str]
    sst_level: Optional[str]
    can_supervise: bool
    can_approve_actions: bool
    persons_count: int = 0
    created_at: datetime


class ProcessCreate(BaseModel):
    """Créer un processus SST"""
    name: str = Field(..., min_length=2, max_length=200)
    description: Optional[str] = None
    process_type: ProcessType
    owner_id: Optional[str] = Field(None, description="ID de la personne responsable")
    team_id: Optional[str] = Field(None, description="ID de l'équipe responsable")
    zone_ids: Optional[List[str]] = []
    frequency: Optional[str] = Field(None, description="Fréquence: quotidien, hebdomadaire, mensuel...")
    steps: Optional[List[str]] = []
    documents: Optional[List[str]] = []
    kpis: Optional[List[str]] = []
    metadata: Optional[Dict[str, Any]] = None


class ProcessResponse(BaseModel):
    """Réponse processus"""
    id: str
    name: str
    description: Optional[str]
    process_type: ProcessType
    owner_id: Optional[str]
    team_id: Optional[str]
    zones: List[str]
    frequency: Optional[str]
    steps_count: int = 0
    created_at: datetime


class ZoneCreate(BaseModel):
    """Créer une zone de risque"""
    name: str = Field(..., min_length=2, max_length=200)
    description: Optional[str] = None
    location: Optional[str] = None
    zone_type: Optional[str] = Field(None, description="Intérieur, Extérieur, Mixte")
    risk_level: RiskLevel = RiskLevel.MOYEN
    hazards: Optional[List[str]] = []
    controls: Optional[List[str]] = []
    required_ppe: Optional[List[str]] = []
    max_occupancy: Optional[int] = None
    responsible_team_id: Optional[str] = None
    sensors: Optional[List[str]] = []
    metadata: Optional[Dict[str, Any]] = None


class ZoneResponse(BaseModel):
    """Réponse zone"""
    id: str
    name: str
    description: Optional[str]
    location: Optional[str]
    zone_type: Optional[str]
    risk_level: RiskLevel
    hazards: List[str]
    controls: List[str]
    required_ppe: List[str]
    responsible_team_id: Optional[str]
    sensors_count: int = 0
    created_at: datetime


class RelationCreate(BaseModel):
    """Créer une relation entre entités"""
    source_id: str
    target_id: str
    relation_type: str = Field(..., description="supervises, belongsTo, responsibleFor, locatedIn...")
    properties: Optional[Dict[str, Any]] = None


class ValidationResult(BaseModel):
    """Résultat de validation SHACL"""
    conforms: bool
    violations_count: int = 0
    violations: List[Dict[str, Any]] = []
    warnings: List[str] = []


class ExportRequest(BaseModel):
    """Requête d'export"""
    format: str = Field("turtle", description="turtle, json-ld, n3, xml")
    include_entities: List[EntityType] = []
    include_relations: bool = True


class CartographyStats(BaseModel):
    """Statistiques de la cartographie"""
    organizations: int = 0
    persons: int = 0
    teams: int = 0
    roles: int = 0
    processes: int = 0
    zones: int = 0
    relations: int = 0
    last_updated: datetime


# ============================================================
# STOCKAGE EN MÉMOIRE (pour démo - à remplacer par Neo4j)
# ============================================================

class CartographyStore:
    """Stockage temporaire de la cartographie"""
    
    def __init__(self):
        self.organizations: Dict[str, dict] = {}
        self.persons: Dict[str, dict] = {}
        self.teams: Dict[str, dict] = {}
        self.roles: Dict[str, dict] = {}
        self.processes: Dict[str, dict] = {}
        self.zones: Dict[str, dict] = {}
        self.relations: List[dict] = []
    
    def generate_id(self, prefix: str) -> str:
        """Génère un ID unique"""
        return f"{prefix}-{uuid.uuid4().hex[:8]}"
    
    def get_stats(self) -> CartographyStats:
        """Retourne les statistiques"""
        return CartographyStats(
            organizations=len(self.organizations),
            persons=len(self.persons),
            teams=len(self.teams),
            roles=len(self.roles),
            processes=len(self.processes),
            zones=len(self.zones),
            relations=len(self.relations),
            last_updated=datetime.now()
        )


# Instance globale du store
store = CartographyStore()


# ============================================================
# ROUTER API
# ============================================================

router = APIRouter(prefix="/cartography", tags=["Cartographie EDGY"])


# --- STATISTIQUES ---

@router.get("/stats", response_model=CartographyStats)
async def get_cartography_stats():
    """Obtenir les statistiques de la cartographie"""
    return store.get_stats()


# --- ORGANISATIONS ---

@router.post("/organizations", response_model=OrganizationResponse)
async def create_organization(org: OrganizationCreate):
    """Créer une nouvelle organisation"""
    org_id = store.generate_id("ORG")
    now = datetime.now()
    
    org_data = {
        "id": org_id,
        "name": org.name,
        "description": org.description,
        "sector": org.sector,
        "size": org.size,
        "address": org.address,
        "metadata": org.metadata or {},
        "created_at": now,
        "updated_at": now
    }
    
    store.organizations[org_id] = org_data
    
    return OrganizationResponse(
        **org_data,
        entities_count=0
    )


@router.get("/organizations", response_model=List[OrganizationResponse])
async def list_organizations():
    """Lister toutes les organisations"""
    return [
        OrganizationResponse(**org, entities_count=0)
        for org in store.organizations.values()
    ]


@router.get("/organizations/{org_id}", response_model=OrganizationResponse)
async def get_organization(org_id: str):
    """Obtenir une organisation par ID"""
    if org_id not in store.organizations:
        raise HTTPException(status_code=404, detail="Organisation non trouvée")
    return OrganizationResponse(**store.organizations[org_id], entities_count=0)


# --- PERSONNES ---

@router.post("/persons", response_model=PersonResponse)
async def create_person(person: PersonCreate):
    """Créer une nouvelle personne"""
    person_id = store.generate_id("PERS")
    now = datetime.now()
    
    person_data = {
        "id": person_id,
        "name": person.name,
        "email": person.email,
        "phone": person.phone,
        "employee_id": person.employee_id,
        "department": person.department,
        "role_ids": person.role_ids or [],
        "team_ids": person.team_ids or [],
        "supervisor_id": person.supervisor_id,
        "certifications": person.certifications or [],
        "metadata": person.metadata or {},
        "created_at": now
    }
    
    store.persons[person_id] = person_data
    
    return PersonResponse(
        id=person_id,
        name=person.name,
        email=person.email,
        employee_id=person.employee_id,
        department=person.department,
        roles=person.role_ids or [],
        teams=person.team_ids or [],
        supervisor_id=person.supervisor_id,
        created_at=now
    )


@router.get("/persons", response_model=List[PersonResponse])
async def list_persons(
    department: Optional[str] = None,
    role_id: Optional[str] = None,
    team_id: Optional[str] = None
):
    """Lister les personnes avec filtres optionnels"""
    persons = list(store.persons.values())
    
    if department:
        persons = [p for p in persons if p.get("department") == department]
    if role_id:
        persons = [p for p in persons if role_id in p.get("role_ids", [])]
    if team_id:
        persons = [p for p in persons if team_id in p.get("team_ids", [])]
    
    return [
        PersonResponse(
            id=p["id"],
            name=p["name"],
            email=p.get("email"),
            employee_id=p.get("employee_id"),
            department=p.get("department"),
            roles=p.get("role_ids", []),
            teams=p.get("team_ids", []),
            supervisor_id=p.get("supervisor_id"),
            created_at=p["created_at"]
        )
        for p in persons
    ]


@router.get("/persons/{person_id}", response_model=PersonResponse)
async def get_person(person_id: str):
    """Obtenir une personne par ID"""
    if person_id not in store.persons:
        raise HTTPException(status_code=404, detail="Personne non trouvée")
    p = store.persons[person_id]
    return PersonResponse(
        id=p["id"],
        name=p["name"],
        email=p.get("email"),
        employee_id=p.get("employee_id"),
        department=p.get("department"),
        roles=p.get("role_ids", []),
        teams=p.get("team_ids", []),
        supervisor_id=p.get("supervisor_id"),
        created_at=p["created_at"]
    )


# --- ÉQUIPES ---

@router.post("/teams", response_model=TeamResponse)
async def create_team(team: TeamCreate):
    """Créer une nouvelle équipe"""
    team_id = store.generate_id("TEAM")
    now = datetime.now()
    
    team_data = {
        "id": team_id,
        "name": team.name,
        "description": team.description,
        "department": team.department,
        "leader_id": team.leader_id,
        "member_ids": team.member_ids or [],
        "zone_ids": team.zone_ids or [],
        "metadata": team.metadata or {},
        "created_at": now
    }
    
    store.teams[team_id] = team_data
    
    return TeamResponse(
        id=team_id,
        name=team.name,
        description=team.description,
        department=team.department,
        leader_id=team.leader_id,
        members_count=len(team.member_ids or []),
        zones=team.zone_ids or [],
        created_at=now
    )


@router.get("/teams", response_model=List[TeamResponse])
async def list_teams(department: Optional[str] = None):
    """Lister les équipes"""
    teams = list(store.teams.values())
    
    if department:
        teams = [t for t in teams if t.get("department") == department]
    
    return [
        TeamResponse(
            id=t["id"],
            name=t["name"],
            description=t.get("description"),
            department=t.get("department"),
            leader_id=t.get("leader_id"),
            members_count=len(t.get("member_ids", [])),
            zones=t.get("zone_ids", []),
            created_at=t["created_at"]
        )
        for t in teams
    ]


# --- RÔLES ---

@router.post("/roles", response_model=RoleResponse)
async def create_role(role: RoleCreate):
    """Créer un nouveau rôle"""
    role_id = store.generate_id("ROLE")
    now = datetime.now()
    
    role_data = {
        "id": role_id,
        "name": role.name,
        "description": role.description,
        "responsibilities": role.responsibilities or [],
        "required_certifications": role.required_certifications or [],
        "sst_level": role.sst_level,
        "can_supervise": role.can_supervise,
        "can_approve_actions": role.can_approve_actions,
        "metadata": role.metadata or {},
        "created_at": now
    }
    
    store.roles[role_id] = role_data
    
    return RoleResponse(
        id=role_id,
        name=role.name,
        description=role.description,
        responsibilities=role.responsibilities or [],
        sst_level=role.sst_level,
        can_supervise=role.can_supervise,
        can_approve_actions=role.can_approve_actions,
        persons_count=0,
        created_at=now
    )


@router.get("/roles", response_model=List[RoleResponse])
async def list_roles():
    """Lister les rôles"""
    return [
        RoleResponse(
            id=r["id"],
            name=r["name"],
            description=r.get("description"),
            responsibilities=r.get("responsibilities", []),
            sst_level=r.get("sst_level"),
            can_supervise=r.get("can_supervise", False),
            can_approve_actions=r.get("can_approve_actions", False),
            persons_count=len([p for p in store.persons.values() if r["id"] in p.get("role_ids", [])]),
            created_at=r["created_at"]
        )
        for r in store.roles.values()
    ]


# --- PROCESSUS SST ---

@router.post("/processes", response_model=ProcessResponse)
async def create_process(process: ProcessCreate):
    """Créer un nouveau processus SST"""
    process_id = store.generate_id("PROC")
    now = datetime.now()
    
    process_data = {
        "id": process_id,
        "name": process.name,
        "description": process.description,
        "process_type": process.process_type,
        "owner_id": process.owner_id,
        "team_id": process.team_id,
        "zone_ids": process.zone_ids or [],
        "frequency": process.frequency,
        "steps": process.steps or [],
        "documents": process.documents or [],
        "kpis": process.kpis or [],
        "metadata": process.metadata or {},
        "created_at": now
    }
    
    store.processes[process_id] = process_data
    
    return ProcessResponse(
        id=process_id,
        name=process.name,
        description=process.description,
        process_type=process.process_type,
        owner_id=process.owner_id,
        team_id=process.team_id,
        zones=process.zone_ids or [],
        frequency=process.frequency,
        steps_count=len(process.steps or []),
        created_at=now
    )


@router.get("/processes", response_model=List[ProcessResponse])
async def list_processes(process_type: Optional[ProcessType] = None):
    """Lister les processus SST"""
    processes = list(store.processes.values())
    
    if process_type:
        processes = [p for p in processes if p.get("process_type") == process_type]
    
    return [
        ProcessResponse(
            id=p["id"],
            name=p["name"],
            description=p.get("description"),
            process_type=p["process_type"],
            owner_id=p.get("owner_id"),
            team_id=p.get("team_id"),
            zones=p.get("zone_ids", []),
            frequency=p.get("frequency"),
            steps_count=len(p.get("steps", [])),
            created_at=p["created_at"]
        )
        for p in processes
    ]


# --- ZONES DE RISQUE ---

@router.post("/zones", response_model=ZoneResponse)
async def create_zone(zone: ZoneCreate):
    """Créer une nouvelle zone de risque"""
    zone_id = store.generate_id("ZONE")
    now = datetime.now()
    
    zone_data = {
        "id": zone_id,
        "name": zone.name,
        "description": zone.description,
        "location": zone.location,
        "zone_type": zone.zone_type,
        "risk_level": zone.risk_level,
        "hazards": zone.hazards or [],
        "controls": zone.controls or [],
        "required_ppe": zone.required_ppe or [],
        "max_occupancy": zone.max_occupancy,
        "responsible_team_id": zone.responsible_team_id,
        "sensors": zone.sensors or [],
        "metadata": zone.metadata or {},
        "created_at": now
    }
    
    store.zones[zone_id] = zone_data
    
    return ZoneResponse(
        id=zone_id,
        name=zone.name,
        description=zone.description,
        location=zone.location,
        zone_type=zone.zone_type,
        risk_level=zone.risk_level,
        hazards=zone.hazards or [],
        controls=zone.controls or [],
        required_ppe=zone.required_ppe or [],
        responsible_team_id=zone.responsible_team_id,
        sensors_count=len(zone.sensors or []),
        created_at=now
    )


@router.get("/zones", response_model=List[ZoneResponse])
async def list_zones(risk_level: Optional[RiskLevel] = None):
    """Lister les zones de risque"""
    zones = list(store.zones.values())
    
    if risk_level:
        zones = [z for z in zones if z.get("risk_level") == risk_level]
    
    return [
        ZoneResponse(
            id=z["id"],
            name=z["name"],
            description=z.get("description"),
            location=z.get("location"),
            zone_type=z.get("zone_type"),
            risk_level=z.get("risk_level", RiskLevel.MOYEN),
            hazards=z.get("hazards", []),
            controls=z.get("controls", []),
            required_ppe=z.get("required_ppe", []),
            responsible_team_id=z.get("responsible_team_id"),
            sensors_count=len(z.get("sensors", [])),
            created_at=z["created_at"]
        )
        for z in zones
    ]


@router.get("/zones/{zone_id}", response_model=ZoneResponse)
async def get_zone(zone_id: str):
    """Obtenir une zone par ID"""
    if zone_id not in store.zones:
        raise HTTPException(status_code=404, detail="Zone non trouvée")
    z = store.zones[zone_id]
    return ZoneResponse(
        id=z["id"],
        name=z["name"],
        description=z.get("description"),
        location=z.get("location"),
        zone_type=z.get("zone_type"),
        risk_level=z.get("risk_level", RiskLevel.MOYEN),
        hazards=z.get("hazards", []),
        controls=z.get("controls", []),
        required_ppe=z.get("required_ppe", []),
        responsible_team_id=z.get("responsible_team_id"),
        sensors_count=len(z.get("sensors", [])),
        created_at=z["created_at"]
    )


# --- RELATIONS ---

@router.post("/relations")
async def create_relation(relation: RelationCreate):
    """Créer une relation entre deux entités"""
    relation_data = {
        "id": store.generate_id("REL"),
        "source_id": relation.source_id,
        "target_id": relation.target_id,
        "relation_type": relation.relation_type,
        "properties": relation.properties or {},
        "created_at": datetime.now()
    }
    
    store.relations.append(relation_data)
    
    return {
        "status": "created",
        "relation": relation_data
    }


@router.get("/relations")
async def list_relations(
    source_id: Optional[str] = None,
    target_id: Optional[str] = None,
    relation_type: Optional[str] = None
):
    """Lister les relations avec filtres"""
    relations = store.relations
    
    if source_id:
        relations = [r for r in relations if r["source_id"] == source_id]
    if target_id:
        relations = [r for r in relations if r["target_id"] == target_id]
    if relation_type:
        relations = [r for r in relations if r["relation_type"] == relation_type]
    
    return relations


# --- EXPORT RDF ---

@router.post("/export/rdf")
async def export_to_rdf(request: ExportRequest):
    """Exporter la cartographie en RDF"""
    try:
        from rdflib import Graph, Namespace, Literal, URIRef
        from rdflib.namespace import RDF, RDFS, XSD
        
        # Namespaces
        EDG = Namespace("http://example.org/edg-schema#")
        EDGY = Namespace("http://edgy.preventera.ai/core#")
        DATA = Namespace("http://edgy.preventera.ai/data#")
        
        graph = Graph()
        graph.bind("edg", EDG)
        graph.bind("edgy", EDGY)
        graph.bind("data", DATA)
        
        # Exporter les organisations
        for org_id, org in store.organizations.items():
            org_uri = DATA[org_id]
            graph.add((org_uri, RDF.type, EDG.Organization))
            graph.add((org_uri, EDG.hasName, Literal(org["name"])))
            if org.get("description"):
                graph.add((org_uri, RDFS.comment, Literal(org["description"])))
            if org.get("sector"):
                graph.add((org_uri, EDG.hasSector, Literal(org["sector"])))
        
        # Exporter les personnes
        for person_id, person in store.persons.items():
            person_uri = DATA[person_id]
            graph.add((person_uri, RDF.type, EDG.Person))
            graph.add((person_uri, EDG.hasName, Literal(person["name"])))
            if person.get("email"):
                graph.add((person_uri, EDG.hasEmail, Literal(person["email"])))
            if person.get("department"):
                graph.add((person_uri, EDG.hasDepartment, Literal(person["department"])))
            
            # Relations avec rôles
            for role_id in person.get("role_ids", []):
                graph.add((person_uri, EDG.hasRole, DATA[role_id]))
            
            # Relations avec équipes
            for team_id in person.get("team_ids", []):
                graph.add((person_uri, EDG.belongsTo, DATA[team_id]))
            
            # Relation superviseur
            if person.get("supervisor_id"):
                graph.add((DATA[person["supervisor_id"]], EDG.supervises, person_uri))
        
        # Exporter les équipes
        for team_id, team in store.teams.items():
            team_uri = DATA[team_id]
            graph.add((team_uri, RDF.type, EDG.Team))
            graph.add((team_uri, EDG.hasName, Literal(team["name"])))
            if team.get("description"):
                graph.add((team_uri, RDFS.comment, Literal(team["description"])))
            
            # Relations avec zones
            for zone_id in team.get("zone_ids", []):
                graph.add((team_uri, EDG.responsibleFor, DATA[zone_id]))
        
        # Exporter les rôles
        for role_id, role in store.roles.items():
            role_uri = DATA[role_id]
            graph.add((role_uri, RDF.type, EDG.Role))
            graph.add((role_uri, EDG.hasName, Literal(role["name"])))
            if role.get("description"):
                graph.add((role_uri, RDFS.comment, Literal(role["description"])))
        
        # Exporter les processus
        for process_id, process in store.processes.items():
            process_uri = DATA[process_id]
            graph.add((process_uri, RDF.type, EDG.Process))
            graph.add((process_uri, EDG.hasName, Literal(process["name"])))
            graph.add((process_uri, EDG.hasProcessType, Literal(process["process_type"])))
            
            # Relations avec zones
            for zone_id in process.get("zone_ids", []):
                graph.add((process_uri, EDG.appliesTo, DATA[zone_id]))
        
        # Exporter les zones
        for zone_id, zone in store.zones.items():
            zone_uri = DATA[zone_id]
            graph.add((zone_uri, RDF.type, EDG.RiskArea))
            graph.add((zone_uri, EDG.hasName, Literal(zone["name"])))
            graph.add((zone_uri, EDG.hasRiskLevel, Literal(zone.get("risk_level", "moyen"))))
            if zone.get("location"):
                graph.add((zone_uri, EDG.hasLocation, Literal(zone["location"])))
            
            # Dangers
            for hazard in zone.get("hazards", []):
                graph.add((zone_uri, EDG.hasHazard, Literal(hazard)))
        
        # Sérialiser
        format_map = {
            "turtle": "turtle",
            "json-ld": "json-ld",
            "n3": "n3",
            "xml": "xml"
        }
        
        output_format = format_map.get(request.format, "turtle")
        rdf_content = graph.serialize(format=output_format)
        
        return {
            "status": "success",
            "format": request.format,
            "triples_count": len(graph),
            "content": rdf_content
        }
        
    except ImportError:
        raise HTTPException(
            status_code=500,
            detail="rdflib non installé. Installez avec: pip install rdflib"
        )


# --- VALIDATION SHACL ---

@router.post("/validate", response_model=ValidationResult)
async def validate_cartography():
    """Valider la cartographie avec les règles SHACL"""
    try:
        from rdflib import Graph
        from pyshacl import validate
        
        # Exporter les données en RDF
        export_result = await export_to_rdf(ExportRequest(format="turtle"))
        
        # Charger le graphe de données
        data_graph = Graph()
        data_graph.parse(data=export_result["content"], format="turtle")
        
        # Charger les shapes SHACL
        shapes_graph = Graph()
        shapes_graph.parse("ontologies/shacl_shapes.ttl", format="turtle")
        
        # Valider
        conforms, results_graph, results_text = validate(
            data_graph,
            shacl_graph=shapes_graph,
            inference='rdfs',
            abort_on_first=False
        )
        
        # Parser les violations
        violations = []
        if not conforms:
            # Extraire les violations du résultat
            for line in results_text.split('\n'):
                if 'Violation' in line or 'violation' in line:
                    violations.append({"message": line.strip()})
        
        return ValidationResult(
            conforms=conforms,
            violations_count=len(violations),
            violations=violations,
            warnings=[]
        )
        
    except FileNotFoundError:
        return ValidationResult(
            conforms=True,
            violations_count=0,
            violations=[],
            warnings=["Fichier SHACL non trouvé, validation ignorée"]
        )
    except ImportError:
        raise HTTPException(
            status_code=500,
            detail="pyshacl non installé. Installez avec: pip install pyshacl"
        )


# --- DONNÉES DE DÉMONSTRATION ---

@router.post("/demo/populate")
async def populate_demo_data():
    """Peupler avec des données de démonstration"""
    
    # Organisation
    org = await create_organization(OrganizationCreate(
        name="Usine Manufacturière ABC",
        description="Usine de fabrication métallique",
        sector="31-33",
        size="Moyenne",
        address="1234 Rue Industrielle, Montréal, QC"
    ))
    
    # Rôles
    role_superviseur = await create_role(RoleCreate(
        name="Superviseur SST",
        description="Responsable de la sécurité d'une zone",
        responsibilities=["Inspections quotidiennes", "Formation équipe", "Rapport incidents"],
        sst_level="Avancé",
        can_supervise=True,
        can_approve_actions=True
    ))
    
    role_operateur = await create_role(RoleCreate(
        name="Opérateur Machine",
        description="Opérateur de machines industrielles",
        responsibilities=["Opération machines", "Contrôle qualité", "Signalement anomalies"],
        sst_level="Base",
        can_supervise=False,
        can_approve_actions=False
    ))
    
    role_technicien = await create_role(RoleCreate(
        name="Technicien Maintenance",
        description="Maintenance préventive et corrective",
        responsibilities=["Maintenance préventive", "Réparations", "Calibration équipements"],
        sst_level="Intermédiaire",
        can_supervise=False,
        can_approve_actions=False
    ))
    
    # Zones
    zone_prod = await create_zone(ZoneCreate(
        name="Zone Production A",
        description="Ligne de production principale",
        location="Bâtiment 1 - Niveau 1",
        zone_type="Intérieur",
        risk_level=RiskLevel.ELEVE,
        hazards=["Bruit > 85dB", "Machines rotatives", "Chaleur"],
        controls=["Protecteurs auditifs obligatoires", "Barrières de sécurité", "Ventilation"],
        required_ppe=["Casque", "Lunettes", "Bouchons", "Chaussures sécurité"],
        max_occupancy=20
    ))
    
    zone_entrepot = await create_zone(ZoneCreate(
        name="Entrepôt Matières",
        description="Stockage matières premières et produits finis",
        location="Bâtiment 2",
        zone_type="Intérieur",
        risk_level=RiskLevel.MOYEN,
        hazards=["Chariots élévateurs", "Chutes d'objets", "Produits chimiques"],
        controls=["Voies piétons séparées", "Rayonnages sécurisés", "Fiches SIMDUT"],
        required_ppe=["Casque", "Gilet haute visibilité", "Chaussures sécurité"]
    ))
    
    zone_exterieur = await create_zone(ZoneCreate(
        name="Zone Chargement",
        description="Quai de chargement/déchargement",
        location="Extérieur - Côté Nord",
        zone_type="Extérieur",
        risk_level=RiskLevel.MOYEN,
        hazards=["Circulation véhicules", "Intempéries", "Manutention lourde"],
        controls=["Signalisation", "Éclairage adéquat", "Formation conducteurs"],
        required_ppe=["Gilet haute visibilité", "Chaussures sécurité"]
    ))
    
    # Équipes
    equipe_prod = await create_team(TeamCreate(
        name="Équipe Production Jour",
        description="Équipe de production - Quart de jour",
        department="Production",
        zone_ids=[zone_prod.id]
    ))
    
    equipe_maint = await create_team(TeamCreate(
        name="Équipe Maintenance",
        description="Maintenance industrielle",
        department="Maintenance",
        zone_ids=[zone_prod.id, zone_entrepot.id]
    ))
    
    # Personnes
    superviseur = await create_person(PersonCreate(
        name="Marie Tremblay",
        email="marie.tremblay@abc.com",
        employee_id="EMP-001",
        department="Production",
        role_ids=[role_superviseur.id],
        team_ids=[equipe_prod.id],
        certifications=["ASP Construction", "Secourisme", "SIMDUT"]
    ))
    
    operateur1 = await create_person(PersonCreate(
        name="Jean Lavoie",
        email="jean.lavoie@abc.com",
        employee_id="EMP-002",
        department="Production",
        role_ids=[role_operateur.id],
        team_ids=[equipe_prod.id],
        supervisor_id=superviseur.id,
        certifications=["Opérateur pont roulant", "SIMDUT"]
    ))
    
    operateur2 = await create_person(PersonCreate(
        name="Sophie Martin",
        email="sophie.martin@abc.com",
        employee_id="EMP-003",
        department="Production",
        role_ids=[role_operateur.id],
        team_ids=[equipe_prod.id],
        supervisor_id=superviseur.id,
        certifications=["SIMDUT"]
    ))
    
    technicien = await create_person(PersonCreate(
        name="Pierre Gagnon",
        email="pierre.gagnon@abc.com",
        employee_id="EMP-004",
        department="Maintenance",
        role_ids=[role_technicien.id],
        team_ids=[equipe_maint.id],
        certifications=["Électricien", "Cadenassage", "Travail en hauteur"]
    ))
    
    # Processus SST
    await create_process(ProcessCreate(
        name="Inspection quotidienne Zone Production",
        description="Vérification quotidienne des équipements et conditions",
        process_type=ProcessType.INSPECTION,
        owner_id=superviseur.id,
        team_id=equipe_prod.id,
        zone_ids=[zone_prod.id],
        frequency="Quotidien",
        steps=[
            "Vérifier état des machines",
            "Contrôler EPI disponibles",
            "Inspecter voies de circulation",
            "Vérifier extincteurs",
            "Compléter checklist"
        ],
        kpis=["Taux conformité", "Anomalies détectées"]
    ))
    
    await create_process(ProcessCreate(
        name="Maintenance préventive mensuelle",
        description="Programme de maintenance préventive des équipements",
        process_type=ProcessType.MAINTENANCE,
        owner_id=technicien.id,
        team_id=equipe_maint.id,
        zone_ids=[zone_prod.id, zone_entrepot.id],
        frequency="Mensuel",
        steps=[
            "Révision calendrier maintenance",
            "Inspection visuelle équipements",
            "Lubrification",
            "Remplacement pièces d'usure",
            "Tests fonctionnels",
            "Mise à jour registre"
        ],
        kpis=["Taux disponibilité équipements", "MTBF"]
    ))
    
    await create_process(ProcessCreate(
        name="Formation accueil SST",
        description="Formation SST pour nouveaux employés",
        process_type=ProcessType.FORMATION,
        owner_id=superviseur.id,
        zone_ids=[zone_prod.id, zone_entrepot.id, zone_exterieur.id],
        frequency="À l'embauche",
        steps=[
            "Présentation politique SST",
            "Visite des installations",
            "Identification des risques",
            "Utilisation EPI",
            "Procédures d'urgence",
            "Évaluation des connaissances"
        ],
        kpis=["Taux réussite formation", "Incidents nouveaux employés"]
    ))
    
    # Relations
    await create_relation(RelationCreate(
        source_id=superviseur.id,
        target_id=operateur1.id,
        relation_type="supervises"
    ))
    
    await create_relation(RelationCreate(
        source_id=superviseur.id,
        target_id=operateur2.id,
        relation_type="supervises"
    ))
    
    await create_relation(RelationCreate(
        source_id=equipe_prod.id,
        target_id=zone_prod.id,
        relation_type="responsibleFor"
    ))
    
    return {
        "status": "success",
        "message": "Données de démonstration créées",
        "stats": store.get_stats().model_dump()
    }


# ============================================================
# INTÉGRATION API PRINCIPALE
# ============================================================

def get_cartography_router():
    """Retourne le router pour intégration dans l'API principale"""
    return router


# Test standalone
if __name__ == "__main__":
    import uvicorn
    from fastapi import FastAPI
    
    app = FastAPI(
        title="EDGY Cartography API",
        description="API de cartographie organisationnelle EDGY pour SST",
        version="1.0.0"
    )
    
    app.include_router(router)
    
    @app.get("/")
    async def root():
        return {
            "name": "EDGY Cartography API",
            "version": "1.0.0",
            "endpoints": [
                "/cartography/stats",
                "/cartography/organizations",
                "/cartography/persons",
                "/cartography/teams",
                "/cartography/roles",
                "/cartography/processes",
                "/cartography/zones",
                "/cartography/relations",
                "/cartography/export/rdf",
                "/cartography/validate",
                "/cartography/demo/populate"
            ]
        }
    
    uvicorn.run(app, host="0.0.0.0", port=8001)
