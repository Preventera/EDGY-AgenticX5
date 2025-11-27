# src/cartography/models.py
from dataclasses import dataclass, field, asdict
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from enum import Enum
from uuid import uuid4
import json
import hashlib
import os

ANON_SALT = os.getenv('ANON_SALT', 'SafetyGraph_Loi25_2025')

class RiskLevel(str, Enum):
    MINIMAL = 'minimal'
    FAIBLE = 'faible'
    MOYEN = 'moyen'
    ELEVE = 'eleve'
    CRITIQUE = 'critique'
    
    @property
    def score(self) -> int:
        return {'minimal': 1, 'faible': 2, 'moyen': 3, 'eleve': 4, 'critique': 5}[self.value]

class RelationType(str, Enum):
    MEMBRE_DE = 'MEMBRE_DE'
    OCCUPE_ROLE = 'OCCUPE_ROLE'
    SUPERVISE = 'SUPERVISE'
    TRAVAILLE_DANS = 'TRAVAILLE_DANS'
    EXPOSE_A = 'EXPOSE_A'
    LOCALISE_DANS = 'LOCALISE_DANS'
    APPARTIENT_A = 'APPARTIENT_A'
    RESPONSABLE_DE = 'RESPONSABLE_DE'

class SCIANSector(str, Enum):
    CONSTRUCTION = '23'
    FABRICATION = '31-33'
    SANTE = '62'
    TRANSPORT = '48-49'
    MINES = '21'

@dataclass
class Organization:
    name: str = ''
    id: str = field(default_factory=lambda: f'ORG-{uuid4().hex[:8]}')
    description: Optional[str] = None
    sector_scian: Optional[str] = None
    code_cnesst: Optional[str] = None
    size: Optional[str] = None
    nb_employes: Optional[int] = None
    region_ssq: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_neo4j_props(self) -> Dict[str, Any]:
        d = asdict(self)
        d['created_at'] = self.created_at.isoformat()
        return d

@dataclass
class Person:
    id: str = field(default_factory=lambda: f'PERS-{uuid4().hex[:8]}')
    matricule: Optional[str] = None
    matricule_anonyme: Optional[str] = None
    department: Optional[str] = None
    team_id: Optional[str] = None
    role_id: Optional[str] = None
    age_groupe: Optional[str] = None
    certifications_sst: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    
    def anonymize(self):
        if self.matricule:
            self.matricule_anonyme = hashlib.sha256(f'{self.matricule}{ANON_SALT}'.encode()).hexdigest()[:16]
            self.matricule = None
        return self
    
    def to_neo4j_props(self) -> Dict[str, Any]:
        d = asdict(self)
        d['created_at'] = self.created_at.isoformat()
        d['certifications_sst'] = json.dumps(self.certifications_sst)
        return d

@dataclass
class Team:
    name: str = ''
    id: str = field(default_factory=lambda: f'TEAM-{uuid4().hex[:8]}')
    department: Optional[str] = None
    leader_id: Optional[str] = None
    horaire: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_neo4j_props(self) -> Dict[str, Any]:
        d = asdict(self)
        d['created_at'] = self.created_at.isoformat()
        return d

@dataclass
class Role:
    name: str = ''
    id: str = field(default_factory=lambda: f'ROLE-{uuid4().hex[:8]}')
    niveau_hierarchique: int = 1
    autorite_arret_travail: bool = False
    formations_obligatoires: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_neo4j_props(self) -> Dict[str, Any]:
        d = asdict(self)
        d['created_at'] = self.created_at.isoformat()
        d['formations_obligatoires'] = json.dumps(self.formations_obligatoires)
        return d

@dataclass
class Zone:
    name: str = ''
    id: str = field(default_factory=lambda: f'ZONE-{uuid4().hex[:8]}')
    risk_level: RiskLevel = RiskLevel.MOYEN
    dangers_identifies: List[str] = field(default_factory=list)
    epi_requis: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_neo4j_props(self) -> Dict[str, Any]:
        d = asdict(self)
        d['risk_level'] = self.risk_level.value
        d['dangers_identifies'] = json.dumps(self.dangers_identifies)
        d['epi_requis'] = json.dumps(self.epi_requis)
        d['created_at'] = self.created_at.isoformat()
        return d

@dataclass
class Process:
    name: str = ''
    id: str = field(default_factory=lambda: f'PROC-{uuid4().hex[:8]}')
    process_type: str = 'prevention'
    criticite_sst: str = 'moyen'
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_neo4j_props(self) -> Dict[str, Any]:
        d = asdict(self)
        d['created_at'] = self.created_at.isoformat()
        return d

@dataclass
class Risk:
    description: str = ''
    categorie: str = ''
    id: str = field(default_factory=lambda: f'RISK-{uuid4().hex[:8]}')
    zone_id: Optional[str] = None
    probabilite: int = 3
    gravite: int = 3
    score_edgy: float = 0.0
    statut: str = 'actif'
    created_at: datetime = field(default_factory=datetime.now)
    
    def calculate_score(self) -> float:
        self.score_edgy = self.probabilite * self.gravite
        return self.score_edgy
    
    def get_niveau(self) -> str:
        if self.score_edgy == 0: self.calculate_score()
        if self.score_edgy >= 20: return 'CRITIQUE'
        elif self.score_edgy >= 15: return 'ELEVE'
        elif self.score_edgy >= 9: return 'MOYEN'
        return 'FAIBLE'
    
    def to_neo4j_props(self) -> Dict[str, Any]:
        self.calculate_score()
        d = asdict(self)
        d['created_at'] = self.created_at.isoformat()
        return d

@dataclass  
class Capability:
    name: str = ''
    id: str = field(default_factory=lambda: f'CAP-{uuid4().hex[:8]}')
    capability_type: str = 'certification'
    duree_validite_mois: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_neo4j_props(self) -> Dict[str, Any]:
        d = asdict(self)
        d['created_at'] = self.created_at.isoformat()
        return d
