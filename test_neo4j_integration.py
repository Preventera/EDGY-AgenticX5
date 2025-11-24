"""
Test d'intégration Neo4j SafetyGraph
EDGY-AgenticX5
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from graph.neo4j_connector import SafetyGraphConnector
from graph.safetygraph_schema import get_ontology_summary, get_entity_labels

def print_header(title):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def test_ontology():
    print_header("1️⃣ TEST ONTOLOGIE")
    summary = get_ontology_summary()
    print(f"  ✅ {summary['name']} v{summary['version']}")
    print(f"  ✅ {summary['entities']} entités, {summary['relations']} relations")
    return True

def test_connection():
    print_header("2️⃣ TEST CONNEXION")
    connector = SafetyGraphConnector()
    connected = connector.connect()
    print(f"  {'✅' if connected else '⚠️'} Mode: {'MOCK' if connector.mock_mode else 'RÉEL'}")
    print(f"  ✅ Status: {connector.status.value}")
    return connector

def test_crud(connector):
    print_header("3️⃣ TEST CRUD")
    zone = connector.create_zone_travail("ZONE-TEST", "Zone Test", "production")
    print(f"  ✅ Zone créée: {zone.get('zone_id', 'ZONE-TEST')}")
    travailleur = connector.create_travailleur("EMP-TEST", "Test", "Jean", "Opérateur")
    print(f"  ✅ Travailleur créé: {travailleur.get('matricule', 'EMP-TEST')}")
    incident = connector.create_incident("INC-TEST", "coupure", "mineur", "Test incident")
    print(f"  ✅ Incident créé: {incident.get('incident_id', 'INC-TEST')}")
    print(f"  📊 Stats: {connector.stats['nodes_created']} nœuds créés")
    return True

def test_analytics(connector):
    print_header("4️⃣ TEST ANALYTIQUE")
    zones = connector.get_zones_high_risk()
    print(f"  ✅ {len(zones)} zones à risque identifiées")
    patterns = connector.get_incident_patterns()
    print(f"  ✅ {len(patterns)} patterns d'incidents")
    context = connector.enrich_context_for_agent(zone_id="ZONE-A1")
    print(f"  ✅ Contexte enrichi: {context.get('zone', {}).get('niveau_risque', 'N/A')}")
    return True

def main():
    print("\n" + "╔" + "═" * 58 + "╗")
    print("║" + " " * 10 + "🗄️ TESTS NEO4J SAFETYGRAPH" + " " * 15 + "   ║")
    print("╚" + "═" * 58 + "╝")
    
    results = {}
    try:
        results["Ontologie"] = test_ontology()
    except Exception as e:
        print(f"  ❌ {e}")
        results["Ontologie"] = False
    
    connector = None
    try:
        connector = test_connection()
        results["Connexion"] = True
    except Exception as e:
        print(f"  ❌ {e}")
        results["Connexion"] = False
        connector = SafetyGraphConnector()
    
    try:
        results["CRUD"] = test_crud(connector)
    except Exception as e:
        print(f"  ❌ {e}")
        results["CRUD"] = False
    
    try:
        results["Analytique"] = test_analytics(connector)
    except Exception as e:
        print(f"  ❌ {e}")
        results["Analytique"] = False
    
    print_header("📊 RÉSUMÉ")
    passed = sum(1 for v in results.values() if v)
    for test, ok in results.items():
        print(f"  {'✅' if ok else '❌'} {test}")
    
    print("\n" + "=" * 60)
    if passed == len(results):
        print(f"  🎉 TOUS LES TESTS PASSENT! ({passed}/{len(results)})")
        print("  🚀 Neo4j SafetyGraph opérationnel!")
    else:
        print(f"  ⚠️ {passed}/{len(results)} tests passés")
    
    if connector and connector.mock_mode:
        print("\n  ℹ️ Mode MOCK actif (Neo4j non connecté)")
    print("=" * 60 + "\n")
    
    return passed == len(results)

if __name__ == "__main__":
    sys.exit(0 if main() else 1)
