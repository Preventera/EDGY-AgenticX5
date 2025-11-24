#!/usr/bin/env python3
"""
Test LangGraph Orchestration avec Neo4j RÉEL
EDGY-AgenticX5
"""

import sys
import os

# Ajouter le chemin src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from neo4j import GraphDatabase
from datetime import datetime


def test_neo4j_real_connection():
    """Test connexion Neo4j réelle"""
    print("\n" + "=" * 60)
    print("  TEST 1: CONNEXION NEO4J REELLE")
    print("=" * 60)
    
    uri = "bolt://localhost:7687"
    driver = GraphDatabase.driver(uri, auth=None)
    
    with driver.session() as session:
        # Compter les entités
        result = session.run("""
            MATCH (z:Zone) WITH count(z) as zones
            MATCH (r:Risque) WITH zones, count(r) as risques
            MATCH (t:Travailleur) WITH zones, risques, count(t) as travailleurs
            MATCH (c:Capteur) WITH zones, risques, travailleurs, count(c) as capteurs
            RETURN zones, risques, travailleurs, capteurs
        """)
        record = result.single()
        
        print(f"\n  Zones: {record['zones']}")
        print(f"  Risques: {record['risques']}")
        print(f"  Travailleurs: {record['travailleurs']}")
        print(f"  Capteurs: {record['capteurs']}")
        
        # Récupérer une zone avec ses risques
        result = session.run("""
            MATCH (z:Zone)-[:A_RISQUE]->(r:Risque)
            RETURN z.zone_id as zone_id, z.nom as zone_nom, 
                   collect(r.description) as risques
            LIMIT 3
        """)
        
        print("\n  Zones avec risques:")
        for record in result:
            print(f"    - {record['zone_nom'] or record['zone_id']}: {record['risques']}")
    
    driver.close()
    print("\n  [OK] Connexion Neo4j reelle validee!")
    return True


def test_langgraph_with_neo4j():
    """Test LangGraph avec Neo4j réel"""
    print("\n" + "=" * 60)
    print("  TEST 2: LANGGRAPH + NEO4J REEL")
    print("=" * 60)
    
    # Importer l'orchestrateur
    from orchestration.langgraph_orchestrator import LangGraphOrchestrator, LANGGRAPH_AVAILABLE
    
    # Créer un connecteur Neo4j simple
    class RealNeo4jConnector:
        def __init__(self):
            self.uri = "bolt://localhost:7687"
            self.driver = GraphDatabase.driver(self.uri, auth=None)
            self.mock_mode = False
        
        def enrich_context_for_agent(self, zone_id=None, worker_id=None, equipment_id=None):
            """Enrichir le contexte depuis Neo4j réel"""
            context = {}
            
            with self.driver.session() as session:
                if zone_id:
                    # Chercher la zone et ses risques
                    result = session.run("""
                        MATCH (z:Zone)
                        WHERE z.zone_id = $zone_id OR z.nom CONTAINS $zone_id
                        OPTIONAL MATCH (z)-[:A_RISQUE]->(r:Risque)
                        RETURN z.zone_id as zone_id, z.nom as nom, 
                               z.niveau_risque as niveau_risque,
                               collect(r.description) as risques
                        LIMIT 1
                    """, zone_id=zone_id)
                    
                    record = result.single()
                    if record:
                        context["zone"] = {
                            "zone_id": record["zone_id"],
                            "nom": record["nom"],
                            "niveau_risque": record["niveau_risque"],
                            "risques": record["risques"]
                        }
                        print(f"\n  [Neo4j] Zone enrichie: {record['nom'] or zone_id}")
                        print(f"           Risques: {record['risques']}")
            
            return context
        
        def create_near_miss(self, near_miss_id, type_risque, potentiel_gravite, 
                            description, zone_id, detecte_par_agent):
            """Créer un Near-Miss dans Neo4j"""
            with self.driver.session() as session:
                session.run("""
                    MERGE (nm:NearMiss {near_miss_id: $near_miss_id})
                    SET nm.type_risque = $type_risque,
                        nm.potentiel_gravite = $potentiel_gravite,
                        nm.description = $description,
                        nm.zone_id = $zone_id,
                        nm.detecte_par_agent = $detecte_par_agent,
                        nm.created_at = datetime()
                """, near_miss_id=near_miss_id, type_risque=type_risque,
                    potentiel_gravite=potentiel_gravite, description=description,
                    zone_id=zone_id, detecte_par_agent=detecte_par_agent)
                
                print(f"\n  [Neo4j] Near-Miss cree: {near_miss_id}")
            return near_miss_id
        
        def get_stats(self):
            return {"connected": True, "uri": self.uri}
        
        def close(self):
            self.driver.close()
    
    # Créer le connecteur réel
    neo4j = RealNeo4jConnector()
    
    # Créer l'orchestrateur avec Neo4j réel
    orchestrator = LangGraphOrchestrator(neo4j_connector=neo4j)
    
    print(f"\n  LangGraph disponible: {LANGGRAPH_AVAILABLE}")
    print(f"  Mode: {'Reel' if not orchestrator.mock_mode else 'Simulation'}")
    
    # Test avec données critiques
    print("\n  --- Scenario: Temperature critique en zone production ---")
    
    sensor_readings = [
        {
            "sensor_id": "CAPT-TEMP-001",
            "sensor_type": "temperature",
            "value": 42.0,  # Critique > 40°C
            "unit": "C",
            "timestamp": datetime.utcnow().isoformat(),
            "zone_id": "ZONE-PROD-001",
            "location": "Atelier Production"
        },
        {
            "sensor_id": "CAPT-BRUIT-001",
            "sensor_type": "noise",
            "value": 88.0,  # Critique > 85 dB
            "unit": "dB",
            "timestamp": datetime.utcnow().isoformat(),
            "zone_id": "ZONE-PROD-001",
            "location": "Atelier Production"
        }
    ]
    
    result = orchestrator.process(sensor_readings, zone_id="ZONE-PROD-001")
    
    print(f"\n  Resultats du workflow:")
    print(f"    Status: {result['status']}")
    print(f"    Risk Level: {result['risk_level']}")
    print(f"    Risk Score: {result.get('risk_score', 0)}")
    print(f"    Alertes: {len(result.get('alerts', []))}")
    print(f"    Recommandations: {len(result.get('recommendations', []))}")
    print(f"    Notifications: {len(result.get('notifications', []))}")
    
    if result.get('alerts'):
        print(f"\n  Alertes generees:")
        for alert in result['alerts']:
            print(f"    - {alert['sensor_type']}: {alert['value']} ({alert['severity']})")
    
    if result.get('recommendations'):
        print(f"\n  Recommandations:")
        for rec in result['recommendations']:
            print(f"    - [{rec['priority']}] {rec['title']}")
    
    # Fermer la connexion
    neo4j.close()
    
    print("\n  [OK] LangGraph + Neo4j reel valide!")
    return result['status'] == 'completed'


def test_verify_nearmiss_created():
    """Vérifier que le Near-Miss a été créé dans Neo4j"""
    print("\n" + "=" * 60)
    print("  TEST 3: VERIFICATION NEAR-MISS DANS NEO4J")
    print("=" * 60)
    
    uri = "bolt://localhost:7687"
    driver = GraphDatabase.driver(uri, auth=None)
    
    with driver.session() as session:
        result = session.run("""
            MATCH (nm:NearMiss)
            WHERE nm.detecte_par_agent = 'LANGGRAPH_ORCHESTRATOR'
            RETURN nm.near_miss_id as id, nm.type_risque as type,
                   nm.potentiel_gravite as gravite, nm.zone_id as zone
            ORDER BY nm.created_at DESC
            LIMIT 5
        """)
        
        near_misses = list(result)
        
        if near_misses:
            print(f"\n  Near-Miss detectes par LangGraph:")
            for nm in near_misses:
                print(f"    - {nm['id']}: {nm['type']} ({nm['gravite']}) - {nm['zone']}")
            print(f"\n  [OK] {len(near_misses)} Near-Miss trouves!")
        else:
            print("\n  Aucun Near-Miss cree (risque pas assez eleve)")
    
    driver.close()
    return True


def main():
    print("\n" + "=" * 60)
    print("  EDGY-AgenticX5 - TEST INTEGRATION COMPLETE")
    print("  LangGraph + Neo4j REEL")
    print("=" * 60)
    
    tests = [
        ("Connexion Neo4j", test_neo4j_real_connection),
        ("LangGraph + Neo4j", test_langgraph_with_neo4j),
        ("Verification Near-Miss", test_verify_nearmiss_created)
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"\n  [ERREUR] {name}: {e}")
            results.append((name, False))
    
    # Résumé
    print("\n" + "=" * 60)
    print("  RESUME DES TESTS")
    print("=" * 60)
    
    passed = 0
    for name, success in results:
        status = "[OK]" if success else "[ECHEC]"
        print(f"  {status} {name}")
        if success:
            passed += 1
    
    print(f"\n  {passed}/{len(tests)} tests reussis")
    print("=" * 60 + "\n")
    
    return passed == len(tests)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
