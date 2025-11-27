# src/cartography/routes.py
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum

from .models import Organization, Person, Team, Role, Zone, Process, Risk, RiskLevel, RelationType
from .connector import SafetyGraphCartographyConnector

class RiskLevelEnum(str, Enum):
    MINIMAL = 'minimal'
    FAIBLE = 'faible'
    MOYEN = 'moyen'
    ELEVE = 'eleve'
    CRITIQUE = 'critique'

class OrganizationCreate(BaseModel):
    name: str = Field(..., min_length=2)
    sector_scian: Optional[str] = None
    nb_employes: Optional[int] = None

class PersonCreate(BaseModel):
    matricule: str
    department: Optional[str] = None
    team_id: Optional[str] = None
    certifications_sst: List[str] = []

class TeamCreate(BaseModel):
    name: str
    department: Optional[str] = None
    leader_id: Optional[str] = None

class RoleCreate(BaseModel):
    name: str
    niveau_hierarchique: int = 1
    autorite_arret_travail: bool = False

class ZoneCreate(BaseModel):
    name: str
    risk_level: RiskLevelEnum = RiskLevelEnum.MOYEN
    dangers_identifies: List[str] = []
    epi_requis: List[str] = []

class RiskCreate(BaseModel):
    description: str
    categorie: str
    zone_id: Optional[str] = None
    probabilite: int = Field(3, ge=1, le=5)
    gravite: int = Field(3, ge=1, le=5)

class RelationCreate(BaseModel):
    source_id: str
    target_id: str
    relation_type: str

class EntityResponse(BaseModel):
    id: str
    status: str = 'created'
    message: str

_connector: Optional[SafetyGraphCartographyConnector] = None

def get_connector() -> SafetyGraphCartographyConnector:
    global _connector
    if _connector is None:
        _connector = SafetyGraphCartographyConnector()
        try:
            _connector.connect()
        except Exception as e:
            raise HTTPException(503, f'Neo4j unavailable: {e}')
    return _connector

cartography_router = APIRouter()

@cartography_router.get('/health')
async def health_check():
    try:
        conn = get_connector()
        return {'status': 'healthy', 'neo4j': 'connected' if conn.is_connected else 'disconnected'}
    except:
        return {'status': 'degraded', 'neo4j': 'disconnected'}

@cartography_router.get('/stats')
async def get_stats(connector = Depends(get_connector)):
    return connector.get_graph_stats()

@cartography_router.post('/organizations', response_model=EntityResponse)
async def create_organization(data: OrganizationCreate, connector = Depends(get_connector)):
    org = Organization(name=data.name, sector_scian=data.sector_scian, nb_employes=data.nb_employes)
    org_id = connector.inject_organization(org)
    return EntityResponse(id=org_id, message=f'Organization {data.name} created')

@cartography_router.post('/persons', response_model=EntityResponse)
async def create_person(data: PersonCreate, anonymize: bool = Query(True), connector = Depends(get_connector)):
    person = Person(matricule=data.matricule, department=data.department, team_id=data.team_id,
                    certifications_sst=data.certifications_sst)
    person_id = connector.inject_person(person, anonymize=anonymize)
    return EntityResponse(id=person_id, message=f'Person created (anonymized: {anonymize})')

@cartography_router.post('/teams', response_model=EntityResponse)
async def create_team(data: TeamCreate, connector = Depends(get_connector)):
    team = Team(name=data.name, department=data.department, leader_id=data.leader_id)
    team_id = connector.inject_team(team)
    return EntityResponse(id=team_id, message=f'Team {data.name} created')

@cartography_router.post('/roles', response_model=EntityResponse)
async def create_role(data: RoleCreate, connector = Depends(get_connector)):
    role = Role(name=data.name, niveau_hierarchique=data.niveau_hierarchique,
                autorite_arret_travail=data.autorite_arret_travail)
    role_id = connector.inject_role(role)
    return EntityResponse(id=role_id, message=f'Role {data.name} created')

@cartography_router.post('/zones', response_model=EntityResponse)
async def create_zone(data: ZoneCreate, connector = Depends(get_connector)):
    zone = Zone(name=data.name, risk_level=RiskLevel(data.risk_level.value),
                dangers_identifies=data.dangers_identifies, epi_requis=data.epi_requis)
    zone_id = connector.inject_zone(zone)
    return EntityResponse(id=zone_id, message=f'Zone {data.name} created')

@cartography_router.get('/zones/risk-summary')
async def get_zones_risk_summary(connector = Depends(get_connector)):
    return {'zones': connector.get_zones_risk_summary()}

@cartography_router.post('/risks', response_model=EntityResponse)
async def create_risk(data: RiskCreate, connector = Depends(get_connector)):
    risk = Risk(description=data.description, categorie=data.categorie, zone_id=data.zone_id,
                probabilite=data.probabilite, gravite=data.gravite)
    risk_id = connector.inject_risk(risk)
    return EntityResponse(id=risk_id, message=f'Risk created (score: {risk.score_edgy})')

@cartography_router.post('/relations')
async def create_relation(data: RelationCreate, connector = Depends(get_connector)):
    try:
        rel_type = RelationType(data.relation_type)
    except ValueError:
        raise HTTPException(400, f'Invalid relation type. Valid: {[r.value for r in RelationType]}')
    success = connector.create_relation(data.source_id, data.target_id, rel_type)
    if not success:
        raise HTTPException(404, 'Source or target entity not found')
    return {'status': 'created', 'relation': data.relation_type}
