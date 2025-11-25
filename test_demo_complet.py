"""
Test complet avec données de démo EDGY
Vérifie que les relations sont bien créées dans Neo4j
"""
import sys
from pathlib import Path
import asyncio

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from edgy_core.api.cartography_api import store
from edgy_core.transformers.neo4j_mapper import EDGYNeo4jMapper
from edgy_core.api.cartography_api import (
    OrganizationCreate,
    PersonCreate,
    TeamCreate,
    RoleCreate,
    ZoneCreate,
    ProcessCreate,
    RiskLevel,
    ProcessType
)

print("=" * 70)
print("🧪 TEST COMPLET - DONNÉES DÉMO + NEO4J")
print("=" * 70)

# Nettoyer le store
print("\n🧹 Nettoyage du store...")
store.organizations.clear()
store.persons.clear()
store.teams.clear()
store.roles.clear()
store.processes.clear()
store.zones.clear()
store.relations.clear()

# Créer mapper Neo4j
mapper = EDGYNeo4jMapper()

if not mapper.is_connected():
    print("❌ Neo4j non disponible")
    exit(1)

print("✅ Connecté à Neo4j")

# Nettoyer Neo4j
print("\n🧹 Nettoyage Neo4j...")
deleted = mapper.clear_edgy_entities()
print(f"   {deleted} entités supprimées")

# Créer données de démo
print("\n📝 Création données de démo...")

# 1. Organisation
org_id = store.generate_id("ORG")
org = {
    "id": org_id,
    "name": "Acme Manufacturing",
    "description": "Usine de fabrication",
    "sector": "31-33",
    "size": "Moyenne"
}
store.organizations[org_id] = org
print(f"   ✅ Organisation: {org['name']}")

# 2. Rôles
role_super_id = store.generate_id("ROLE")
role_super = {
    "id": role_super_id,
    "name": "Superviseur SST",
    "description": "Responsable sécurité",
    "can_supervise": True,
    "can_approve_actions": True
}
store.roles[role_super_id] = role_super

role_op_id = store.generate_id("ROLE")
role_op = {
    "id": role_op_id,
    "name": "Opérateur",
    "description": "Opérateur de production",
    "can_supervise": False,
    "can_approve_actions": False
}
store.roles[role_op_id] = role_op
print(f"   ✅ Rôles: 2 créés")

# 3. Équipes
team_id = store.generate_id("TEAM")
team = {
    "id": team_id,
    "name": "Équipe Production",
    "description": "Équipe de production principale",
    "department": "Production",
    "member_ids": []
}
store.teams[team_id] = team
print(f"   ✅ Équipe: {team['name']}")

# 4. Zones
zone_id = store.generate_id("ZONE")
zone = {
    "id": zone_id,
    "name": "Zone Production A",
    "description": "Ligne de production",
    "risk_level": "élevé",
    "hazards": ["Bruit", "Machines rotatives"],
    "controls": ["EPI obligatoire", "Formation"]
}
store.zones[zone_id] = zone
print(f"   ✅ Zone: {zone['name']}")

# 5. Personnes avec relations
person_super_id = store.generate_id("PERS")
person_super = {
    "id": person_super_id,
    "name": "Marie Tremblay",
    "email": "marie.t@acme.com",
    "department": "Production",
    "role_ids": [role_super_id],
    "team_ids": [team_id]
}
store.persons[person_super_id] = person_super

person_op1_id = store.generate_id("PERS")
person_op1 = {
    "id": person_op1_id,
    "name": "Jean Lavoie",
    "email": "jean.l@acme.com",
    "department": "Production",
    "role_ids": [role_op_id],
    "team_ids": [team_id],
    "supervisor_id": person_super_id
}
store.persons[person_op1_id] = person_op1

person_op2_id = store.generate_id("PERS")
person_op2 = {
    "id": person_op2_id,
    "name": "Sophie Martin",
    "email": "sophie.m@acme.com",
    "department": "Production",
    "role_ids": [role_op_id],
    "team_ids": [team_id],
    "supervisor_id": person_super_id
}
store.persons[person_op2_id] = person_op2
print(f"   ✅ Personnes: 3 créées")

# 6. Processus
process_id = store.generate_id("PROC")
process = {
    "id": process_id,
    "name": "Inspection quotidienne",
    "description": "Inspection de sécurité",
    "process_type": "inspection",
    "owner_id": person_super_id,
    "zone_ids": [zone_id],
    "frequency": "quotidien"
}
store.processes[process_id] = process
print(f"   ✅ Processus: {process['name']}")

# Statistiques store
print(f"\n📊 Statistiques Store:")
print(f"   Organizations: {len(store.organizations)}")
print(f"   Persons: {len(store.persons)}")
print(f"   Teams: {len(store.teams)}")
print(f"   Roles: {len(store.roles)}")
print(f"   Zones: {len(store.zones)}")
print(f"   Processes: {len(store.processes)}")

# Synchroniser vers Neo4j
print("\n🔄 Synchronisation vers Neo4j...")

sync_stats = {
    "organizations": 0,
    "persons": 0,
    "teams": 0,
    "roles": 0,
    "zones": 0,
    "processes": 0,
    "relations": 0
}

# Créer organisations
for org in store.organizations.values():
    if mapper.create_organization(org):
        sync_stats["organizations"] += 1

# Créer rôles
for role in store.roles.values():
    if mapper.create_role(role):
        sync_stats["roles"] += 1

# Créer équipes
for team in store.teams.values():
    if mapper.create_team(team):
        sync_stats["teams"] += 1

# Créer zones
for zone in store.zones.values():
    if mapper.create_zone(zone):
        sync_stats["zones"] += 1

# Créer personnes ET leurs relations
for person in store.persons.values():
    if mapper.create_person(person):
        sync_stats["persons"] += 1
        
        # Relations rôles
        for role_id in person.get("role_ids", []):
            if mapper.create_role_assignment(person["id"], role_id):
                sync_stats["relations"] += 1
        
        # Relations équipes
        for team_id in person.get("team_ids", []):
            if mapper.create_team_membership(person["id"], team_id):
                sync_stats["relations"] += 1
        
        # Relation superviseur
        if person.get("supervisor_id"):
            if mapper.create_supervision_relation(person["supervisor_id"], person["id"]):
                sync_stats["relations"] += 1

# Créer processus
for process in store.processes.values():
    if mapper.create_process(process):
        sync_stats["processes"] += 1
        
        # Relations zones
        for zone_id in process.get("zone_ids", []):
            if mapper.create_process_zone_link(process["id"], zone_id):
                sync_stats["relations"] += 1
        
        # Relation propriétaire
        if process.get("owner_id"):
            if mapper.create_process_owner(process["id"], process["owner_id"]):
                sync_stats["relations"] += 1

print("\n✅ Synchronisation terminée:")
for key, value in sync_stats.items():
    print(f"   {key}: {value}")

# Vérifier statistiques Neo4j
print("\n📊 Statistiques Neo4j:")
neo4j_stats = mapper.get_edgy_statistics()
for label, count in neo4j_stats.items():
    emoji = "🎯" if label == "Relations" and count > 0 else "  "
    print(f"   {emoji} {label}: {count}")

# Vérifier chaîne de supervision
print("\n👥 Vérification chaîne de supervision:")
chain = mapper.get_supervision_chain(person_op1_id)
if chain:
    print(f"   ✅ Chaîne trouvée pour {person_op1['name']}:")
    for person in chain:
        print(f"      → {person['name']}")
else:
    print(f"   ❌ Aucune chaîne trouvée")

# Tests de validation
print("\n✅ TESTS DE VALIDATION:")
success = True

if neo4j_stats.get("Relations", 0) == 0:
    print("   ❌ ÉCHEC: Aucune relation créée!")
    success = False
else:
    print(f"   ✅ Relations créées: {neo4j_stats.get('Relations', 0)}")

if neo4j_stats.get("Person", 0) != 3:
    print(f"   ❌ ÉCHEC: {neo4j_stats.get('Person', 0)} personnes au lieu de 3")
    success = False
else:
    print(f"   ✅ Personnes: {neo4j_stats.get('Person', 0)}")

if len(chain) == 0:
    print("   ❌ ÉCHEC: Chaîne de supervision vide")
    success = False
else:
    print(f"   ✅ Chaîne de supervision: OK")

mapper.close()

print("\n" + "=" * 70)
if success:
    print("🎉 SUCCÈS TOTAL - Le système fonctionne correctement!")
else:
    print("❌ ÉCHEC - Problèmes détectés")
print("=" * 70)
