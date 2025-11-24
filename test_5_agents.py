"""
Test complet des 5 Agents Fondamentaux AgenticX5
Exécution: python test_5_agents.py
"""

import sys
from pathlib import Path
from datetime import datetime

# Ajouter src au path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

# Imports des agents
from agents.base_agent import BaseAgent, AgentCapability, AgentStatus
from agents.perception_agent import PerceptionAgent
from agents.normalization_agent import NormalizationAgent, DataQuality
from agents.analysis_agent import AnalysisAgent, RiskLevel
from agents.recommendation_agent import RecommendationAgent, ActionPriority
from agents.orchestration_agent import OrchestrationAgent, WorkflowStatus

def print_header(title: str):
    """Affiche un header formaté"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def print_subheader(title: str):
    """Affiche un sous-header"""
    print(f"\n  📌 {title}")
    print("  " + "-" * 50)

def test_perception_agent():
    """Test du PerceptionAgent"""
    print_header("1️⃣ TEST PERCEPTIONAGENT")
    
    agent = PerceptionAgent(agent_id="test_perception_001")
    print(f"  ✅ Agent créé: {agent.agent_id}")
    print(f"  ✅ Capteurs supportés: {len(agent.supported_sensors)}")
    
    # Test avec données température
    data = {
        "source": "iot_sensor",
        "sensor_type": "temperature",
        "value": 28.5,
        "unit": "°C",
        "location": "Atelier A"
    }
    
    result = agent.process(data)
    print(f"  ✅ Traitement: {result.get('status', 'unknown')}")
    print(f"     Clés retournées: {list(result.keys())[:5]}...")
    
    return True

def test_normalization_agent():
    """Test du NormalizationAgent"""
    print_header("2️⃣ TEST NORMALIZATIONAGENT")
    
    agent = NormalizationAgent(agent_id="test_normalization_001")
    print(f"  ✅ Agent créé: {agent.agent_id}")
    
    # Test conversion Fahrenheit → Celsius
    print_subheader("Conversion °F → °C")
    data_f = {
        "value": 98.6,  # 98.6°F = 37°C
        "unit": "°F",
        "sensor_type": "temperature",
        "source_agent_id": "perception_001"
    }
    
    result = agent.process(data_f)
    print(f"  ✅ Status: {result.get('status')}")
    print(f"  ✅ Valeur originale: 98.6 °F")
    print(f"  ✅ Valeur normalisée: {result.get('normalized_value'):.2f} {result.get('normalized_unit')}")
    print(f"  ✅ Qualité: {result.get('quality_level')} ({result.get('quality_score', 0):.2f})")
    
    # Test avec pression en PSI
    print_subheader("Conversion PSI → Pa")
    data_psi = {
        "value": 14.7,  # ~101325 Pa (pression atmosphérique)
        "unit": "psi",
        "sensor_type": "pressure",
        "source_agent_id": "perception_001"
    }
    
    result_psi = agent.process(data_psi)
    print(f"  ✅ Valeur originale: 14.7 psi")
    print(f"  ✅ Valeur normalisée: {result_psi.get('normalized_value'):.0f} {result_psi.get('normalized_unit')}")
    
    # Statistiques
    stats = agent.get_statistics()
    print(f"\n  📊 Statistiques: {stats['data_normalized']} normalisées, {stats['data_rejected']} rejetées")
    
    return True

def test_analysis_agent():
    """Test de l'AnalysisAgent"""
    print_header("3️⃣ TEST ANALYSISAGENT")
    
    agent = AnalysisAgent(agent_id="test_analysis_001")
    print(f"  ✅ Agent créé: {agent.agent_id}")
    
    # Test avec température normale
    print_subheader("Analyse température normale (22°C)")
    data_normal = {
        "normalized_value": 22.0,
        "normalized_unit": "°C",
        "sensor_type": "temperature",
        "quality_score": 0.95,
        "location": "Bureau 101"
    }
    
    result_normal = agent.process(data_normal)
    print(f"  ✅ Risk Score: {result_normal.get('risk_score', 0):.1f}/100")
    print(f"  ✅ Risk Level: {result_normal.get('risk_level')}")
    print(f"  ✅ Alertes: {result_normal.get('alerts_count', 0)}")
    
    # Test avec température critique
    print_subheader("Analyse température CRITIQUE (42°C)")
    data_critical = {
        "normalized_value": 42.0,
        "normalized_unit": "°C",
        "sensor_type": "temperature",
        "quality_score": 0.9,
        "location": "Fonderie"
    }
    
    result_critical = agent.process(data_critical)
    print(f"  ⚠️ Risk Score: {result_critical.get('risk_score', 0):.1f}/100")
    print(f"  ⚠️ Risk Level: {result_critical.get('risk_level')}")
    print(f"  ⚠️ Alertes générées: {result_critical.get('alerts_count', 0)}")
    print(f"  ⚠️ Catégorie danger: {result_critical.get('hazard_category')}")
    
    if result_critical.get('alerts'):
        for alert in result_critical['alerts'][:2]:
            print(f"     → {alert.get('type')}: {alert.get('message', '')[:50]}...")
    
    # Test avec bruit excessif
    print_subheader("Analyse bruit excessif (95 dB)")
    data_noise = {
        "normalized_value": 95.0,
        "normalized_unit": "dB",
        "sensor_type": "noise",
        "quality_score": 0.85,
        "location": "Atelier Machines"
    }
    
    result_noise = agent.process(data_noise)
    print(f"  🔊 Risk Score: {result_noise.get('risk_score', 0):.1f}/100")
    print(f"  🔊 Risk Level: {result_noise.get('risk_level')}")
    print(f"  🔊 Recommandations nécessaires: {result_noise.get('recommendations_needed')}")
    
    # Statistiques
    stats = agent.get_statistics()
    print(f"\n  📊 Statistiques: {stats['analyses_performed']} analyses, {stats['alerts_generated']} alertes")
    
    return True

def test_recommendation_agent():
    """Test du RecommendationAgent"""
    print_header("4️⃣ TEST RECOMMENDATIONAGENT")
    
    agent = RecommendationAgent(agent_id="test_recommendation_001")
    print(f"  ✅ Agent créé: {agent.agent_id}")
    
    # Test avec analyse de risque élevé
    print_subheader("Recommandations pour risque ÉLEVÉ")
    analysis_data = {
        "risk_score": 75.0,
        "risk_level": "high",
        "hazard_category": "physical",
        "alerts": [
            {"type": "threshold_exceeded", "severity": "high"}
        ],
        "contributing_factors": ["Dépassement seuil température"],
        "location": "Zone Production",
        "sensor_type": "temperature"
    }
    
    result = agent.process(analysis_data)
    print(f"  ✅ Status: {result.get('status')}")
    print(f"  ✅ Recommandations générées: {result.get('recommendations_count', 0)}")
    print(f"  ✅ Réduction risque totale: {result.get('total_risk_reduction', 0):.1f}%")
    print(f"  ✅ Coût estimé total: {result.get('total_estimated_cost', 0):.0f} CAD")
    
    # Afficher les recommandations
    if result.get('recommendations'):
        print("\n  📋 Recommandations proposées:")
        for i, rec in enumerate(result['recommendations'][:3], 1):
            print(f"     {i}. [{rec.get('priority')}] {rec.get('title')}")
            print(f"        Type: {rec.get('action_type')} | Réduction: {rec.get('risk_reduction')}%")
    
    # Test avec risque faible (pas de recommandations)
    print_subheader("Risque faible - Pas de recommandations")
    low_risk_data = {
        "risk_score": 15.0,
        "risk_level": "low",
        "hazard_category": "physical",
        "alerts": [],
        "sensor_type": "temperature"
    }
    
    result_low = agent.process(low_risk_data)
    print(f"  ℹ️ Status: {result_low.get('status')}")
    print(f"  ℹ️ Message: {result_low.get('message', 'N/A')[:60]}...")
    
    return True

def test_orchestration_agent():
    """Test de l'OrchestrationAgent - Pipeline complet"""
    print_header("5️⃣ TEST ORCHESTRATIONAGENT (Pipeline Complet)")
    
    agent = OrchestrationAgent(agent_id="test_orchestrator_001")
    print(f"  ✅ Orchestrateur créé: {agent.agent_id}")
    
    # Status du pipeline
    pipeline_status = agent.get_pipeline_status()
    print("\n  📡 Status des agents du pipeline:")
    for name, info in pipeline_status.items():
        print(f"     • {name}: {info.get('agent_id')}")
    
    # Test workflow complet avec données critiques
    print_subheader("Workflow complet - Température critique")
    
    sensor_data = {
        "source": "capteur_iot_zone_a",
        "sensor_type": "temperature",
        "value": 45.0,  # Température critique !
        "unit": "°C",
        "location": "Zone Fonderie",
        "timestamp": datetime.utcnow().isoformat()
    }
    
    print(f"  📥 Données entrée: {sensor_data['value']} {sensor_data['unit']} @ {sensor_data['location']}")
    print("  ⏳ Exécution du pipeline...")
    
    result = agent.process(sensor_data)
    
    print(f"\n  📤 Résultat du workflow:")
    print(f"     • Status: {result.get('status')}")
    print(f"     • Étapes complétées: {result.get('stages_completed')}")
    print(f"     • Durée: {result.get('total_duration_ms', 0):.2f} ms")
    print(f"     • Risk Score: {result.get('risk_score', 'N/A')}")
    print(f"     • Recommandations: {result.get('recommendations_count', 0)}")
    
    if result.get('errors'):
        print(f"     ⚠️ Erreurs: {len(result['errors'])}")
    
    # Test avec données normales
    print_subheader("Workflow complet - Conditions normales")
    
    normal_data = {
        "source": "capteur_bureau",
        "sensor_type": "temperature",
        "value": 22.0,
        "unit": "°C",
        "location": "Bureau Direction"
    }
    
    result_normal = agent.process(normal_data)
    print(f"  📤 Status: {result_normal.get('status')}")
    print(f"  📤 Risk Score: {result_normal.get('risk_score', 'N/A')}")
    print(f"  📤 Recommandations nécessaires: {result_normal.get('recommendations_count', 0) > 0}")
    
    # Statistiques globales
    print_subheader("Statistiques globales du système")
    stats = agent.get_global_statistics()
    orch_stats = stats['orchestrator']
    print(f"  📊 Workflows exécutés: {orch_stats['workflows_executed']}")
    print(f"  📊 Taux de succès: {orch_stats['success_rate']:.1f}%")
    print(f"  📊 Durée moyenne: {orch_stats['average_duration_ms']:.2f} ms")
    print(f"  📊 Total alertes: {orch_stats['total_alerts']}")
    print(f"  📊 Total recommandations: {orch_stats['total_recommendations']}")
    
    return True

def main():
    """Exécute tous les tests"""
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 15 + "🧪 TESTS 5 AGENTS FONDAMENTAUX" + " " * 15 + "   ║")
    print("║" + " " * 20 + "EDGY-AgenticX5 | SafetyGraph" + " " * 15 + "   ║")
    print("╚" + "═" * 68 + "╝")
    
    results = {}
    
    try:
        # Test 1: PerceptionAgent
        results["PerceptionAgent"] = test_perception_agent()
    except Exception as e:
        print(f"  ❌ ERREUR: {str(e)}")
        results["PerceptionAgent"] = False
    
    try:
        # Test 2: NormalizationAgent
        results["NormalizationAgent"] = test_normalization_agent()
    except Exception as e:
        print(f"  ❌ ERREUR: {str(e)}")
        results["NormalizationAgent"] = False
    
    try:
        # Test 3: AnalysisAgent
        results["AnalysisAgent"] = test_analysis_agent()
    except Exception as e:
        print(f"  ❌ ERREUR: {str(e)}")
        results["AnalysisAgent"] = False
    
    try:
        # Test 4: RecommendationAgent
        results["RecommendationAgent"] = test_recommendation_agent()
    except Exception as e:
        print(f"  ❌ ERREUR: {str(e)}")
        results["RecommendationAgent"] = False
    
    try:
        # Test 5: OrchestrationAgent
        results["OrchestrationAgent"] = test_orchestration_agent()
    except Exception as e:
        print(f"  ❌ ERREUR: {str(e)}")
        results["OrchestrationAgent"] = False
    
    # Résumé final
    print_header("📊 RÉSUMÉ DES TESTS")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for agent, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status} - {agent}")
    
    print("\n" + "=" * 70)
    if passed == total:
        print(f"  🎉 TOUS LES TESTS PASSENT! ({passed}/{total})")
        print("  🚀 Les 5 Agents Fondamentaux sont opérationnels!")
    else:
        print(f"  ⚠️ {passed}/{total} tests passés")
    print("=" * 70 + "\n")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
