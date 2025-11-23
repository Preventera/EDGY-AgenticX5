"""
Tests unitaires pour les modèles EDGY
"""

import pytest
from datetime import datetime
from src.edgy_core.models.edgy_entity import (
    EDGYEntity, 
    EDGYProcess, 
    EDGYRiskArea,
    EDGYEntityType,
    RiskLevel
)


def test_edgy_entity_creation():
    """Test création entité EDGY basique"""
    entity = EDGYEntity(
        id="E001",
        type=EDGYEntityType.TEAM,
        name="Équipe HSE"
    )
    
    assert entity.id == "E001"
    assert entity.type == "Team"
    assert entity.name == "Équipe HSE"
    assert entity.supervisor_id is None
    assert isinstance(entity.created_at, datetime)


def test_edgy_entity_with_supervisor():
    """Test entité avec superviseur"""
    entity = EDGYEntity(
        id="E002",
        type=EDGYEntityType.PERSON,
        name="Chef SST",
        supervisor_id="E001"
    )
    
    assert entity.supervisor_id == "E001"


def test_edgy_entity_validation_error():
    """Test validation erreur (nom vide)"""
    with pytest.raises(ValueError):
        EDGYEntity(
            id="E003",
            type=EDGYEntityType.TEAM,
            name=""  # Nom vide = erreur
        )


def test_edgy_process_creation():
    """Test création processus"""
    process = EDGYProcess(
        id="P001",
        name="Inspection régulière",
        owner_id="E001"
    )
    
    assert process.id == "P001"
    assert process.name == "Inspection régulière"
    assert process.inputs == []
    assert process.outputs == []


def test_edgy_risk_area_creation():
    """Test création zone de risque"""
    risk = EDGYRiskArea(
        id="R001",
        name="Zone hauteur",
        risk_level=RiskLevel.HIGH
    )
    
    assert risk.id == "R001"
    assert risk.risk_level == "high"
    assert risk.mitigations == []


def test_risk_level_enum():
    """Test énumération niveaux de risque"""
    assert RiskLevel.LOW.value == "low"
    assert RiskLevel.MEDIUM.value == "medium"
    assert RiskLevel.HIGH.value == "high"
    assert RiskLevel.CRITICAL.value == "critical"