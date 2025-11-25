"""
Script de diagnostic pour le bug Relations Neo4j
Identifie pourquoi les relations ne sont pas créées
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from edgy_core.transformers.neo4j_mapper import EDGYNeo4jMapper
from edgy_core.api.cartography_api import store

print("=" * 70)
print("🔍 DIAGNOSTIC BUG RELATIONS NEO4J")
print("=" * 70)

# Créer mapper
mapper = EDGYNeo4jMapper()

if not mapper.is_connected():
    print("❌ Impossible de se connecter à Neo4j")
    exit(1)

print("\n✅ Connecté à Neo4j")

# Créer des entités de test
print("\n📝 Création d entités de test...")

# Créer 2 personnes
person1_id = store.generate_id("PERS")
person2_id = store.generate_id("PERS")

person1 = {
    "id": person1_id,
    "name": "Test Supervisor",
    "email": "supervisor@test.com",
    "department": "Test"
}

person2 = {
    "id": person2_id,
    "name": "Test Employee",
    "email": "employee@test.com",
    "department": "Test"
}

# Créer dans Neo4j
result1 = mapper.create_person(person1)
result2 = mapper.create_person(person2)

print(f"   Person 1 créé: {result1}")
print(f"   Person 2 créé: {result2}")

# Vérifier que les nœuds existent
print("\n🔍 Vérification des nœuds dans Neo4j...")

query_check = """
MATCH (p:Person {id: $id})
RETURN p.id as id, p.name as name
"""

with mapper.driver.session() as session:
    # Vérifier person1
    result = session.run(query_check, {"id": person1_id})
    record = result.single()
    if record:
        print(f"   ✅ Person 1 trouvé: {record['name']} (ID: {record['id']})")
    else:
        print(f"   ❌ Person 1 NOT FOUND! ID recherché: {person1_id}")
    
    # Vérifier person2
    result = session.run(query_check, {"id": person2_id})
    record = result.single()
    if record:
        print(f"   ✅ Person 2 trouvé: {record['name']} (ID: {record['id']})")
    else:
        print(f"   ❌ Person 2 NOT FOUND! ID recherché: {person2_id}")

# Tenter de créer relation
print("\n🔗 Tentative de création de relation...")
success = mapper.create_supervision_relation(person1_id, person2_id)
print(f"   Résultat: {'✅ SUCCESS' if success else '❌ FAILED'}")

# Vérifier si la relation existe
print("\n🔍 Vérification de la relation dans Neo4j...")

query_rel = """
MATCH (p1:Person {id: $id1})-[r:SUPERVISES]->(p2:Person {id: $id2})
RETURN type(r) as rel_type, p1.name as supervisor, p2.name as employee
"""

with mapper.driver.session() as session:
    result = session.run(query_rel, {"id1": person1_id, "id2": person2_id})
    record = result.single()
    if record:
        print(f"   ✅ Relation trouvée: {record['supervisor']} -> {record['employee']}")
    else:
        print(f"   ❌ Relation NOT FOUND!")
        print(f"      Source ID: {person1_id}")
        print(f"      Target ID: {person2_id}")

# Statistiques finales
print("\n📊 Statistiques Neo4j:")
stats = mapper.get_edgy_statistics()
for label, count in stats.items():
    print(f"   {label}: {count}")

# Cleanup
print("\n🧹 Nettoyage...")
mapper.clear_edgy_entities()

mapper.close()
print("\n✅ Diagnostic terminé!")
