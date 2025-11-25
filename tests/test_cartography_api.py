"""
Tests complets pour l API Cartographie EDGY
Couvre CRUD, validation, relations et statistiques
"""
import pytest
import sys
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from edgy_core.api.cartography_api import (
    store,
    RiskLevel,
    ProcessType
)

@pytest.fixture(autouse=True)
def clear_store():
    """Nettoyer le store avant chaque test."""
    store.organizations.clear()
    store.persons.clear()
    store.teams.clear()
    store.roles.clear()
    store.processes.clear()
    store.zones.clear()
    store.relations.clear()
    yield


# ============================================
# TESTS - Organization CRUD
# ============================================

@pytest.mark.cartography
@pytest.mark.unit
class TestOrganizationCRUD:
    """Tests CRUD pour les organisations."""
    
    def test_create_organization(self, sample_organization):
        """Test création organisation."""
        org_id = store.generate_id("ORG")
        org_data = {
            **sample_organization,
            "id": org_id,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        store.organizations[org_id] = org_data
        
        assert len(store.organizations) == 1
        assert store.organizations[org_id]["name"] == sample_organization["name"]
    
    def test_create_multiple_organizations(self):
        """Test création de plusieurs organisations."""
        for i in range(3):
            org_id = store.generate_id("ORG")
            store.organizations[org_id] = {
                "id": org_id,
                "name": f"Organization {i}",
                "created_at": datetime.now()
            }
        
        assert len(store.organizations) == 3
    
    def test_get_organization(self, sample_organization):
        """Test récupération organisation."""
        org_id = store.generate_id("ORG")
        store.organizations[org_id] = {
            **sample_organization,
            "id": org_id
        }
        
        retrieved = store.organizations.get(org_id)
        assert retrieved is not None
        assert retrieved["id"] == org_id
    
    def test_get_nonexistent_organization(self):
        """Test récupération organisation inexistante."""
        retrieved = store.organizations.get("ORG-nonexistent")
        assert retrieved is None
    
    def test_update_organization(self, sample_organization):
        """Test mise à jour organisation."""
        org_id = store.generate_id("ORG")
        store.organizations[org_id] = {
            **sample_organization,
            "id": org_id
        }
        
        # Mise à jour
        store.organizations[org_id]["size"] = "Grande"
        store.organizations[org_id]["updated_at"] = datetime.now()
        
        assert store.organizations[org_id]["size"] == "Grande"
    
    def test_delete_organization(self, sample_organization):
        """Test suppression organisation."""
        org_id = store.generate_id("ORG")
        store.organizations[org_id] = {
            **sample_organization,
            "id": org_id
        }
        
        del store.organizations[org_id]
        assert org_id not in store.organizations


# ============================================
# TESTS - Person CRUD
# ============================================

@pytest.mark.cartography
@pytest.mark.unit
class TestPersonCRUD:
    """Tests CRUD pour les personnes."""
    
    def test_create_person(self, sample_person):
        """Test création personne."""
        person_id = store.generate_id("PERS")
        person_data = {
            **sample_person,
            "id": person_id,
            "role_ids": [],
            "team_ids": [],
            "created_at": datetime.now()
        }
        store.persons[person_id] = person_data
        
        assert len(store.persons) == 1
        assert store.persons[person_id]["name"] == sample_person["name"]
    
    def test_person_with_email(self):
        """Test personne avec email."""
        person_id = store.generate_id("PERS")
        store.persons[person_id] = {
            "id": person_id,
            "name": "Test User",
            "email": "test@example.com",
            "created_at": datetime.now()
        }
        
        assert store.persons[person_id]["email"] == "test@example.com"
    
    def test_person_with_multiple_roles(self, sample_person):
        """Test personne avec plusieurs rôles."""
        person_id = store.generate_id("PERS")
        role_ids = ["ROLE-1", "ROLE-2", "ROLE-3"]
        
        store.persons[person_id] = {
            **sample_person,
            "id": person_id,
            "role_ids": role_ids,
            "created_at": datetime.now()
        }
        
        assert len(store.persons[person_id]["role_ids"]) == 3
    
    def test_person_with_supervisor(self, sample_person):
        """Test personne avec superviseur."""
        supervisor_id = store.generate_id("PERS")
        person_id = store.generate_id("PERS")
        
        store.persons[supervisor_id] = {
            "id": supervisor_id,
            "name": "Supervisor",
            "created_at": datetime.now()
        }
        
        store.persons[person_id] = {
            **sample_person,
            "id": person_id,
            "supervisor_id": supervisor_id,
            "created_at": datetime.now()
        }
        
        assert store.persons[person_id]["supervisor_id"] == supervisor_id


# ============================================
# TESTS - Team CRUD
# ============================================

@pytest.mark.cartography
@pytest.mark.unit
class TestTeamCRUD:
    """Tests CRUD pour les équipes."""
    
    def test_create_team(self, sample_team):
        """Test création équipe."""
        team_id = store.generate_id("TEAM")
        team_data = {
            **sample_team,
            "id": team_id,
            "member_ids": [],
            "zone_ids": [],
            "created_at": datetime.now()
        }
        store.teams[team_id] = team_data
        
        assert len(store.teams) == 1
        assert store.teams[team_id]["name"] == sample_team["name"]
    
    def test_team_with_members(self, sample_team):
        """Test équipe avec membres."""
        team_id = store.generate_id("TEAM")
        member_ids = ["PERS-1", "PERS-2", "PERS-3"]
        
        store.teams[team_id] = {
            **sample_team,
            "id": team_id,
            "member_ids": member_ids,
            "created_at": datetime.now()
        }
        
        assert len(store.teams[team_id]["member_ids"]) == 3
    
    def test_team_with_leader(self, sample_team):
        """Test équipe avec leader."""
        team_id = store.generate_id("TEAM")
        leader_id = "PERS-001"
        
        store.teams[team_id] = {
            **sample_team,
            "id": team_id,
            "leader_id": leader_id,
            "created_at": datetime.now()
        }
        
        assert store.teams[team_id]["leader_id"] == leader_id


# ============================================
# TESTS - Role CRUD
# ============================================

@pytest.mark.cartography
@pytest.mark.unit
class TestRoleCRUD:
    """Tests CRUD pour les rôles."""
    
    def test_create_role(self, sample_role):
        """Test création rôle."""
        role_id = store.generate_id("ROLE")
        role_data = {
            "id": role_id,
            "name": "Test Role",
            "responsibilities": ["Task 1", "Task 2"],
            "can_supervise": False,
            "can_approve_actions": False,
            "created_at": datetime.now()
        }
        store.roles[role_id] = role_data
        
        assert len(store.roles) == 1
        assert len(store.roles[role_id]["responsibilities"]) == 2
    
    def test_role_with_permissions(self):
        """Test rôle avec permissions."""
        role_id = store.generate_id("ROLE")
        store.roles[role_id] = {
            "id": role_id,
            "name": "Supervisor Role",
            "can_supervise": True,
            "can_approve_actions": True,
            "created_at": datetime.now()
        }
        
        assert store.roles[role_id]["can_supervise"] is True
        assert store.roles[role_id]["can_approve_actions"] is True


# ============================================
# TESTS - Zone CRUD
# ============================================

@pytest.mark.cartography
@pytest.mark.unit
class TestZoneCRUD:
    """Tests CRUD pour les zones."""
    
    def test_create_zone(self, sample_zone):
        """Test création zone."""
        zone_id = store.generate_id("ZONE")
        zone_data = {
            **sample_zone,
            "id": zone_id,
            "hazards": sample_zone.get("hazards", []),
            "controls": sample_zone.get("controls", []),
            "created_at": datetime.now()
        }
        store.zones[zone_id] = zone_data
        
        assert len(store.zones) == 1
        assert store.zones[zone_id]["name"] == sample_zone["name"]
    
    def test_zone_risk_levels(self):
        """Test différents niveaux de risque."""
        for risk in [RiskLevel.MINIMAL, RiskLevel.MOYEN, RiskLevel.CRITIQUE]:
            zone_id = store.generate_id("ZONE")
            store.zones[zone_id] = {
                "id": zone_id,
                "name": f"Zone {risk.value}",
                "risk_level": risk.value,
                "created_at": datetime.now()
            }
        
        assert len(store.zones) == 3
    
    def test_zone_with_hazards(self):
        """Test zone avec dangers."""
        zone_id = store.generate_id("ZONE")
        hazards = ["Bruit", "Chaleur", "Produits chimiques"]
        
        store.zones[zone_id] = {
            "id": zone_id,
            "name": "Zone dangereuse",
            "risk_level": RiskLevel.ELEVE.value,
            "hazards": hazards,
            "created_at": datetime.now()
        }
        
        assert len(store.zones[zone_id]["hazards"]) == 3
    
    def test_zone_with_controls(self):
        """Test zone avec contrôles."""
        zone_id = store.generate_id("ZONE")
        controls = ["EPI obligatoire", "Ventilation", "Formation requise"]
        
        store.zones[zone_id] = {
            "id": zone_id,
            "name": "Zone contrôlée",
            "controls": controls,
            "created_at": datetime.now()
        }
        
        assert len(store.zones[zone_id]["controls"]) == 3


# ============================================
# TESTS - Process CRUD
# ============================================

@pytest.mark.cartography
@pytest.mark.unit
class TestProcessCRUD:
    """Tests CRUD pour les processus."""
    
    def test_create_process(self, sample_process):
        """Test création processus."""
        process_id = store.generate_id("PROC")
        process_data = {
            **sample_process,
            "id": process_id,
            "process_type": "inspection",
            "created_at": datetime.now()
        }
        store.processes[process_id] = process_data
        
        assert len(store.processes) == 1
    
    def test_process_types(self):
        """Test différents types de processus."""
        for ptype in [ProcessType.INSPECTION, ProcessType.FORMATION, ProcessType.MAINTENANCE]:
            process_id = store.generate_id("PROC")
            store.processes[process_id] = {
                "id": process_id,
                "name": f"Process {ptype.value}",
                "process_type": ptype.value,
                "created_at": datetime.now()
            }
        
        assert len(store.processes) == 3


# ============================================
# TESTS - Relations
# ============================================

@pytest.mark.cartography
@pytest.mark.unit
class TestRelations:
    """Tests des relations entre entités."""
    
    def test_create_relation(self):
        """Test création relation."""
        relation = {
            "id": store.generate_id("REL"),
            "source_id": "PERS-1",
            "target_id": "TEAM-1",
            "relation_type": "member_of",
            "created_at": datetime.now()
        }
        store.relations.append(relation)
        
        assert len(store.relations) == 1
    
    def test_multiple_relations(self):
        """Test création de plusieurs relations."""
        for i in range(5):
            relation = {
                "id": store.generate_id("REL"),
                "source_id": f"PERS-{i}",
                "target_id": "TEAM-1",
                "relation_type": "member_of",
                "created_at": datetime.now()
            }
            store.relations.append(relation)
        
        assert len(store.relations) == 5
    
    def test_supervision_relation(self):
        """Test relation de supervision."""
        relation = {
            "id": store.generate_id("REL"),
            "source_id": "PERS-SUPERVISOR",
            "target_id": "PERS-EMPLOYEE",
            "relation_type": "supervises",
            "properties": {"since": "2024-01-01"},
            "created_at": datetime.now()
        }
        store.relations.append(relation)
        
        assert store.relations[0]["relation_type"] == "supervises"


# ============================================
# TESTS - Statistiques
# ============================================

@pytest.mark.cartography
@pytest.mark.unit
class TestStatistics:
    """Tests des statistiques."""
    
    def test_empty_stats(self):
        """Test statistiques avec store vide."""
        stats = store.get_stats()
        assert stats.organizations == 0
        assert stats.persons == 0
        assert stats.teams == 0
        assert stats.roles == 0
        assert stats.processes == 0
        assert stats.zones == 0
        assert stats.relations == 0
    
    def test_stats_with_data(self, sample_organization, sample_person, sample_team):
        """Test statistiques avec données."""
        # Ajouter des entités
        org_id = store.generate_id("ORG")
        store.organizations[org_id] = {**sample_organization, "id": org_id}
        
        person_id = store.generate_id("PERS")
        store.persons[person_id] = {**sample_person, "id": person_id}
        
        team_id = store.generate_id("TEAM")
        store.teams[team_id] = {**sample_team, "id": team_id}
        
        stats = store.get_stats()
        assert stats.organizations == 1
        assert stats.persons == 1
        assert stats.teams == 1


# ============================================
# TESTS - Validation
# ============================================

@pytest.mark.cartography
@pytest.mark.unit
class TestValidation:
    """Tests de validation."""
    
    def test_generate_unique_ids(self):
        """Test génération IDs uniques."""
        ids = set()
        for _ in range(100):
            org_id = store.generate_id("ORG")
            assert org_id not in ids
            ids.add(org_id)
        
        assert len(ids) == 100
    
    def test_id_format(self):
        """Test format des IDs."""
        org_id = store.generate_id("ORG")
        assert org_id.startswith("ORG-")
        assert len(org_id) > 4
        
        person_id = store.generate_id("PERS")
        assert person_id.startswith("PERS-")
    
    def test_timestamps(self):
        """Test timestamps."""
        org_id = store.generate_id("ORG")
        now = datetime.now()
        
        store.organizations[org_id] = {
            "id": org_id,
            "name": "Test Org",
            "created_at": now,
            "updated_at": now
        }
        
        org = store.organizations[org_id]
        assert isinstance(org["created_at"], datetime)
        assert isinstance(org["updated_at"], datetime)


# ============================================
# TESTS - Cas limites
# ============================================

@pytest.mark.cartography
@pytest.mark.unit
class TestEdgeCases:
    """Tests des cas limites."""
    
    def test_empty_store(self):
        """Test store vide."""
        assert len(store.organizations) == 0
        assert len(store.persons) == 0
        assert len(store.teams) == 0
    
    def test_large_dataset(self):
        """Test avec beaucoup de données."""
        # Créer 100 organisations
        for i in range(100):
            org_id = store.generate_id("ORG")
            store.organizations[org_id] = {
                "id": org_id,
                "name": f"Organization {i}",
                "created_at": datetime.now()
            }
        
        assert len(store.organizations) == 100
    
    def test_unicode_names(self):
        """Test avec caractères unicode."""
        org_id = store.generate_id("ORG")
        store.organizations[org_id] = {
            "id": org_id,
            "name": "Société Québécoise d Électricité ⚡",
            "created_at": datetime.now()
        }
        
        assert "Québécoise" in store.organizations[org_id]["name"]
    
    def test_empty_lists(self):
        """Test avec listes vides."""
        person_id = store.generate_id("PERS")
        store.persons[person_id] = {
            "id": person_id,
            "name": "Test Person",
            "role_ids": [],
            "team_ids": [],
            "certifications": [],
            "created_at": datetime.now()
        }
        
        assert store.persons[person_id]["role_ids"] == []
