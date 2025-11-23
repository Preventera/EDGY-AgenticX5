"""
Modèles Pydantic pour entités EDGY
Définit les structures de données pour Entity, Process, RiskArea
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from enum import Enum
from datetime import datetime


# ============================================================
# ENUMS
# ============================================================

class EDGYEntityType(str, Enum):
    """Types d'entités EDGY"""
    PERSON = "Person"
    TEAM = "Team"
    ROLE = "Role"
    ORGANIZATION = "Organization"


class RiskLevel(str, Enum):
    """Niveaux de risque"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# ============================================================
# MODÈLES PRINCIPAUX
# ============================================================

class EDGYEntity(BaseModel):
    """
    Modèle Pydantic pour entité EDGY
    Représente une personne, équipe, rôle ou organisation
    """
    id: str = Field(..., description="ID unique entité", min_length=1)
    type: EDGYEntityType = Field(..., description="Type d'entité EDGY")
    name: str = Field(..., description="Nom de l'entité", min_length=1)
    description: Optional[str] = Field(None, description="Description détaillée")
    supervisor_id: Optional[str] = Field(None, description="ID du superviseur")
    properties: Dict[str, str] = Field(default_factory=dict, description="Propriétés supplémentaires")
    created_at: Optional[datetime] = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = Field(default_factory=datetime.now)
    
    class Config:
        use_enum_values = True
        json_schema_extra = {
            "example": {
                "id": "E001",
                "type": "Team",
                "name": "Équipe HSE",
                "description": "Équipe santé et sécurité",
                "supervisor_id": "E002",
                "properties": {"department": "SST"}
            }
        }


class EDGYProcess(BaseModel):
    """
    Modèle Pydantic pour processus EDGY
    Représente un processus métier ou opérationnel
    """
    id: str = Field(..., description="ID unique processus")
    name: str = Field(..., description="Nom du processus", min_length=1)
    description: Optional[str] = Field(None, description="Description du processus")
    owner_id: Optional[str] = Field(None, description="ID du propriétaire du processus")
    inputs: List[str] = Field(default_factory=list, description="IDs des flux d'entrée")
    outputs: List[str] = Field(default_factory=list, description="IDs des flux de sortie")
    properties: Dict[str, str] = Field(default_factory=dict)
    created_at: Optional[datetime] = Field(default_factory=datetime.now)
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "P001",
                "name": "Inspection régulière",
                "description": "Inspection hebdomadaire des équipements",
                "owner_id": "E001",
                "inputs": ["DF001"],
                "outputs": ["DF002"]
            }
        }


class EDGYRiskArea(BaseModel):
    """
    Modèle Pydantic pour zone de risque EDGY
    Représente une zone identifiée avec risques SST
    """
    id: str = Field(..., description="ID unique zone de risque")
    name: str = Field(..., description="Nom de la zone", min_length=1)
    risk_level: RiskLevel = Field(..., description="Niveau de risque")
    description: Optional[str] = Field(None, description="Description des risques")
    mitigations: List[str] = Field(
        default_factory=list, 
        description="IDs des mesures d'atténuation"
    )
    affected_entities: List[str] = Field(
        default_factory=list,
        description="IDs des entités exposées"
    )
    properties: Dict[str, str] = Field(default_factory=dict)
    created_at: Optional[datetime] = Field(default_factory=datetime.now)
    
    class Config:
        use_enum_values = True
        json_schema_extra = {
            "example": {
                "id": "R001",
                "name": "Zone travaux en hauteur",
                "risk_level": "high",
                "description": "Risque de chute > 3m",
                "mitigations": ["P002", "P003"],
                "affected_entities": ["E001", "E005"]
            }
        }


class EDGYDataFlow(BaseModel):
    """
    Modèle Pydantic pour flux de données EDGY
    Représente un flux d'information entre entités/processus
    """
    id: str = Field(..., description="ID unique flux de données")
    name: str = Field(..., description="Nom du flux")
    source_id: Optional[str] = Field(None, description="ID source du flux")
    target_id: Optional[str] = Field(None, description="ID cible du flux")
    data_type: Optional[str] = Field(None, description="Type de données")
    properties: Dict[str, str] = Field(default_factory=dict)
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "DF001",
                "name": "Rapport inspection",
                "source_id": "P001",
                "target_id": "E001",
                "data_type": "document"
            }
        }


# ============================================================
# FONCTIONS UTILITAIRES
# ============================================================

def validate_entity(entity_data: dict) -> EDGYEntity:
    """Valide et crée une entité EDGY depuis dict"""
    return EDGYEntity(**entity_data)


def validate_process(process_data: dict) -> EDGYProcess:
    """Valide et crée un processus EDGY depuis dict"""
    return EDGYProcess(**process_data)


def validate_risk_area(risk_data: dict) -> EDGYRiskArea:
    """Valide et crée une zone de risque depuis dict"""
    return EDGYRiskArea(**risk_data)