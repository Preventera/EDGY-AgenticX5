"""
Test d'intégration LangGraph Orchestration
EDGY-AgenticX5 | SafetyGraph

Tests:
1. Création orchestrateur
2. Workflow risque minimal
3. Workflow risque critique
4. Routage conditionnel
5. Intégration Neo4j
6. Statistiques
"""

import sys
from pathlib import Path
from datetime import datetime

# Ajouter src au path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def print_header(title: str):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def print_workflow_result(result: dict):
    """Affiche le résultat d'un workflow de manière formatée"""
    status = result.get("status", "unknown")
    status_icon = "✅" if status == "completed" else "❌"
    
    print(f"\n  {status_icon} Status: {status}")
    print(f"  📋 Workflow ID: {result.get('workflow_id', 'N/A')}")
    
    if status == "completed":
        print(f"  🎯 Risk Level: {result.get('risk_level', 'N/A')}")
        print(f"  📊 Risk Score: {result.get('risk_score', 0):.1f}")
        print(f"  🚨 Alertes: {len(result.get('alerts', []))}")
        print(f"  💡 Recommandations: {len(result.get('recommendations', []))}")
        print(f"  📤 Notifications: {len(result.get('notifications', []))}")
        
        times = result.get('processing_times', {})
        if times:
            print(f"\n  ⏱️ Temps de traitement:")
            for stage, time_ms in times.items():
                print(f"     - {stage}: {time_ms:.2f}ms")
        
        messages = result.get('messages', [])
        if messages:
            print(f"\n  📝 Messages ({len(messages)}):")
            for msg in messages[-5:]:  # Derniers 5 messages
                print(f"     → {msg}")
    else:
        print(f"  ❌ Erreur: {result.get('error', 'Inconnue')}")

def main():
    print("\n" + "╔" + "═" * 58 + "╗")
    print("║" + " " * 8 + "🔄 TESTS LANGGRAPH ORCHESTRATION" + " " * 10 + "  ║")
    print("║" + " " * 12 + "EDGY-AgenticX5 | SafetyGraph" + " " * 12 + "  ║")
    print("╚" + "═" * 58 + "╝")
    
    results = {}
    
    # ==========================================
    # TEST 1: Création orchestrateur
    # ==========================================
    print_header("1️⃣ TEST CRÉATION ORCHESTRATEUR")
    
    try:
        from orchestration.langgraph_orchestrator import (
            LangGraphOrchestrator,
            create_orchestrator,
            LANGGRAPH_AVAILABLE
        )
        
        orchestrator = create_orchestrator()
        
        print(f"  ✅ Orchestrateur créé")
        print(f"  📦 LangGraph disponible: {LANGGRAPH_AVAILABLE}")
        print(f"  🔧 Mode simulation: {orchestrator.mock_mode}")
        
        # Afficher le graphe
        print("\n" + orchestrator.get_graph_visualization())
        
        results["Création"] = True
    except Exception as e:
        print(f"  ❌ Erreur: {e}")
        results["Création"] = False
        return False
    
    # ==========================================
    # TEST 2: Workflow risque minimal
    # ==========================================
    print_header("2️⃣ TEST WORKFLOW RISQUE MINIMAL")
    
    try:
        # Données normales (pas de risque)
        normal_readings = [
            {
                "sensor_id": "TEMP-001",
                "sensor_type": "temperature",
                "value": 22.0,
                "unit": "°C",
                "timestamp": datetime.utcnow().isoformat(),
                "zone_id": "ZONE-BUREAU",
                "location": "Bureau principal"
            },
            {
                "sensor_id": "NOISE-001",
                "sensor_type": "noise",
                "value": 55.0,
                "unit": "dB",
                "timestamp": datetime.utcnow().isoformat(),
                "zone_id": "ZONE-BUREAU",
                "location": "Bureau principal"
            }
        ]
        
        result = orchestrator.process(normal_readings, zone_id="ZONE-BUREAU")
        print_workflow_result(result)
        
        # Vérifications
        assert result["status"] == "completed", "Workflow devrait être complété"
        assert result["risk_level"] == "minimal", f"Risk devrait être minimal, got {result['risk_level']}"
        assert len(result.get("alerts", [])) == 0, "Pas d'alertes attendues"
        
        print(f"\n  ✅ Test réussi: Risque minimal correctement détecté")
        results["Risque Minimal"] = True
        
    except Exception as e:
        print(f"  ❌ Erreur: {e}")
        results["Risque Minimal"] = False
    
    # ==========================================
    # TEST 3: Workflow risque critique
    # ==========================================
    print_header("3️⃣ TEST WORKFLOW RISQUE CRITIQUE")
    
    try:
        # Données critiques (température extrême + bruit excessif)
        critical_readings = [
            {
                "sensor_id": "TEMP-002",
                "sensor_type": "temperature",
                "value": 45.0,  # > 40°C = critique
                "unit": "°C",
                "timestamp": datetime.utcnow().isoformat(),
                "zone_id": "ZONE-FONDERIE",
                "location": "Atelier Fonderie"
            },
            {
                "sensor_id": "NOISE-002",
                "sensor_type": "noise",
                "value": 95.0,  # > 90 dB = critique
                "unit": "dB",
                "timestamp": datetime.utcnow().isoformat(),
                "zone_id": "ZONE-FONDERIE",
                "location": "Atelier Fonderie"
            }
        ]
        
        result = orchestrator.process(critical_readings, zone_id="ZONE-FONDERIE")
        print_workflow_result(result)
        
        # Vérifications
        assert result["status"] == "completed", "Workflow devrait être complété"
        assert result["risk_level"] == "critical", f"Risk devrait être critical, got {result['risk_level']}"
        assert len(result.get("alerts", [])) > 0, "Alertes attendues"
        assert len(result.get("recommendations", [])) > 0, "Recommandations attendues"
        assert len(result.get("notifications", [])) > 0, "Notifications attendues"
        
        print(f"\n  ✅ Test réussi: Risque critique correctement géré")
        results["Risque Critique"] = True
        
    except Exception as e:
        print(f"  ❌ Erreur: {e}")
        results["Risque Critique"] = False
    
    # ==========================================
    # TEST 4: Routage conditionnel (medium)
    # ==========================================
    print_header("4️⃣ TEST ROUTAGE CONDITIONNEL (MEDIUM)")
    
    try:
        # Données medium (légèrement au-dessus des seuils)
        medium_readings = [
            {
                "sensor_id": "TEMP-003",
                "sensor_type": "temperature",
                "value": 32.0,  # > 30°C warning
                "unit": "°C",
                "timestamp": datetime.utcnow().isoformat(),
                "zone_id": "ZONE-ENTREPOT",
                "location": "Entrepôt"
            }
        ]
        
        result = orchestrator.process(medium_readings, zone_id="ZONE-ENTREPOT")
        print_workflow_result(result)
        
        # Pour medium, on devrait avoir recommandations mais pas forcément notifications P1
        assert result["status"] == "completed"
        assert result["risk_level"] in ["medium", "low"], f"Expected medium/low, got {result['risk_level']}"
        
        print(f"\n  ✅ Test réussi: Routage medium fonctionne")
        results["Routage Medium"] = True
        
    except Exception as e:
        print(f"  ❌ Erreur: {e}")
        results["Routage Medium"] = False
    
    # ==========================================
    # TEST 5: Intégration Neo4j
    # ==========================================
    print_header("5️⃣ TEST INTÉGRATION NEO4J")
    
    try:
        from graph.neo4j_connector import SafetyGraphConnector
        
        # Créer connecteur Neo4j
        neo4j = SafetyGraphConnector()
        neo4j.connect()
        
        # Créer orchestrateur avec Neo4j
        orchestrator_neo4j = LangGraphOrchestrator(neo4j_connector=neo4j)
        
        # Exécuter workflow
        result = orchestrator_neo4j.process(
            [
                {
                    "sensor_id": "TEMP-NEO4J",
                    "sensor_type": "temperature",
                    "value": 38.0,
                    "unit": "°C",
                    "timestamp": datetime.utcnow().isoformat(),
                    "zone_id": "ZONE-A1",
                    "location": "Zone A1"
                }
            ],
            zone_id="ZONE-A1"
        )
        
        print_workflow_result(result)
        print(f"\n  ✅ Neo4j Mock Mode: {neo4j.mock_mode}")
        print(f"  ✅ Stats Neo4j: {neo4j.stats}")
        
        results["Neo4j Integration"] = True
        
    except Exception as e:
        print(f"  ❌ Erreur: {e}")
        results["Neo4j Integration"] = False
    
    # ==========================================
    # TEST 6: Statistiques
    # ==========================================
    print_header("6️⃣ TEST STATISTIQUES")
    
    try:
        stats = orchestrator.get_statistics()
        
        print(f"  📊 Workflows exécutés: {stats['workflows_executed']}")
        print(f"  ✅ Workflows réussis: {stats['workflows_successful']}")
        print(f"  ❌ Workflows échoués: {stats['workflows_failed']}")
        print(f"  📈 Taux de succès: {stats['success_rate']}%")
        print(f"  ⏱️ Temps moyen: {stats['average_processing_time_ms']:.2f}ms")
        print(f"  🚨 Alertes générées: {stats['alerts_generated']}")
        print(f"  💡 Recommandations: {stats['recommendations_generated']}")
        print(f"  🔧 LangGraph: {'Réel' if stats['langgraph_available'] else 'Simulé'}")
        
        assert stats['workflows_executed'] >= 3, "Au moins 3 workflows exécutés"
        assert stats['success_rate'] > 0, "Taux de succès > 0"
        
        results["Statistiques"] = True
        
    except Exception as e:
        print(f"  ❌ Erreur: {e}")
        results["Statistiques"] = False
    
    # ==========================================
    # RÉSUMÉ
    # ==========================================
    print_header("📊 RÉSUMÉ DES TESTS")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test, ok in results.items():
        status = "✅" if ok else "❌"
        print(f"  {status} {test}")
    
    print("\n" + "=" * 60)
    
    if passed == total:
        print(f"  🎉 TOUS LES TESTS PASSENT! ({passed}/{total})")
        print(f"  🚀 LangGraph Orchestration opérationnel!")
    else:
        print(f"  ⚠️ {passed}/{total} tests passés")
    
    if not LANGGRAPH_AVAILABLE:
        print(f"\n  ℹ️ Mode SIMULATION actif (LangGraph non installé)")
        print(f"  ℹ️ Pour activer LangGraph: pip install langgraph")
    
    print("=" * 60 + "\n")
    
    return passed == total


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
