"""
Fixtures pytest pour EDGY-AgenticX5
Configuration et fixtures réutilisables pour tous les tests
"""
import pytest
import sys
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

# Ajouter src au path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

@pytest.fixture
def sample_organization() -> Dict[str, Any]:
    """Organisation exemple pour les tests."""
    return {
        "name": "Acme Manufacturing Inc.",
        "description": "Entreprise de fabrication industrielle",
        "industry": "Manufacturing",
        "size": "500-1000",
        "location": "Montréal, QC"
    }

@pytest.fixture
def sample_person() -> Dict[str, Any]:
    """Personne exemple pour les tests."""
    return {
        "name": "Jean Tremblay",
        "email": "jean.tremblay@acme.com",
        "role": "Superviseur SST",
        "department": "Santé et Sécurité",
        "phone": "+1-514-555-1234"
    }

@pytest.fixture
def sample_team() -> Dict[str, Any]:
    """Équipe exemple pour les tests."""
    return {
        "name": "Équipe SST",
        "description": "Équipe de santé et sécurité au travail",
        "department": "HSE",
        "member_count": 5
    }

@pytest.fixture
def sample_role() -> Dict[str, Any]:
    """Rôle exemple pour les tests."""
    return {
        "name": "Agent de Sécurité",
        "description": "Responsable de la surveillance et prévention",
        "responsibilities": [
            "Inspection quotidienne",
            "Formation personnel",
            "Rapport incidents"
        ],
        "required_certifications": ["SIMDUT", "Premiers soins"],
        "can_supervise": False,
        "can_approve_actions": False
    }

@pytest.fixture
def sample_zone() -> Dict[str, Any]:
    """Zone exemple pour les tests."""
    return {
        "name": "Atelier de Production",
        "risk_level": "élevé",
        "hazards": [
            "Machines en mouvement",
            "Bruit élevé (>85 dB)"
        ],
        "controls": [
            "Protecteurs de machines",
            "Équipements de protection individuelle"
        ]
    }

@pytest.fixture
def sample_process() -> Dict[str, Any]:
    """Processus exemple pour les tests."""
    return {
        "name": "Inspection Hebdomadaire SST",
        "description": "Inspection de sécurité systématique",
        "frequency": "hebdomadaire",
        "duration_minutes": 120,
        "steps": [
            "Vérification équipements",
            "Contrôle zones à risque",
            "Documentation anomalies",
            "Suivi correctifs"
        ],
        "process_type": "inspection"
    }

@pytest.fixture(autouse=True)
def clear_all_stores():
    """Nettoyer tous les stores avant chaque test."""
    yield
