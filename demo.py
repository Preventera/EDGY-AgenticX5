"""
Script de Démonstration EDGY-AgenticX5
Simule une situation SST réelle avec interaction multi-agents
"""
import logging
import sys
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Ajouter le dossier src au path
sys.path.insert(0, str(Path(__file__).parent))

from src.agents.monitoring_agent import MonitoringAgent
from src.agents.orchestrator_agent import OrchestratorAgent
from src.agents.security_manager import SecurityManager
from src.utils.claude_client import ClaudeClient

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def print_banner():
    """Affiche la bannière de démarrage."""
    banner = '''
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║                    EDGY-AGENTICX5                             ║
║           Architecture Agentique Multi-Agent                  ║
║              pour la Santé et Sécurité au Travail            ║
║                                                               ║
║        Développé par Mario Deshaies, CAISO                    ║
║           Preventera & GenAISafety                            ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
'''
    print(banner)

def print_section(title: str):
    """Affiche un titre de section."""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")

def simulate_sensor_data() -> Dict[str, Any]:
    """Simule des données de capteurs."""
    return {
        "machine_id": "M-47",
        "location": "Ligne de production A",
        "timestamp": datetime.now().isoformat(),
        "sensors": {
            "temperature": {
                "value": 95,
                "unit": "°C",
                "threshold_warning": 80,
                "threshold_critical": 95
            },
            "vibration": {
                "value": 8.2,
                "unit": "mm/s",
                "threshold_warning": 5,
                "threshold_critical": 10
            },
            "pressure": {
                "value": 145,
                "unit": "PSI",
                "threshold_warning": 150,
                "threshold_critical": 200
            },
            "noise": {
                "value": 88,
                "unit": "dB",
                "threshold_warning": 85,
                "threshold_critical": 95
            }
        }
    }

def run_demo():
    """Exécute la démonstration complète."""
    
    # Afficher la bannière
    print_banner()
    
    # Phase 1: Initialisation des agents
    print_section("PHASE 1 : Initialisation des Agents")
    
    print("🤖 Initialisation de MonitoringAgent...")
    monitoring = MonitoringAgent()
    monitoring.initialize()
    time.sleep(0.5)
    
    print("🎯 Initialisation de OrchestratorAgent...")
    orchestrator = OrchestratorAgent()
    orchestrator.initialize()
    time.sleep(0.5)
    
    print("🛡️  Initialisation de SecurityManager...")
    security = SecurityManager()
    security.initialize()
    time.sleep(0.5)
    
    print("🧠 Initialisation de ClaudeClient...")
    claude = ClaudeClient()
    time.sleep(0.5)
    
    print("\n✅ Tous les agents sont initialisés et opérationnels !")
    time.sleep(2)
    
    # Phase 2: Simulation d'une situation SST
    print_section("PHASE 2 : Simulation d'une Situation SST")
    
    print("📊 Collecte des données de capteurs...\n")
    sensor_data = simulate_sensor_data()
    
    print(f"🏭 Machine: {sensor_data['machine_id']}")
    print(f"📍 Localisation: {sensor_data['location']}")
    print(f"⏰ Timestamp: {sensor_data['timestamp']}\n")
    
    print("📈 Données des capteurs:")
    for sensor_name, sensor_info in sensor_data['sensors'].items():
        value = sensor_info['value']
        unit = sensor_info['unit']
        warning = sensor_info['threshold_warning']
        critical = sensor_info['threshold_critical']
        
        # Déterminer le statut
        if value >= critical:
            status = "🔴 CRITIQUE"
        elif value >= warning:
            status = "🟠 AVERTISSEMENT"
        else:
            status = "🟢 NORMAL"
        
        print(f"  • {sensor_name.capitalize():12} : {value:6.1f} {unit:5} {status}")
        print(f"    {'':14}   (Seuils: ⚠️ {warning} | 🔴 {critical})")
    
    time.sleep(2)
    
    # Phase 3: Analyse par MonitoringAgent
    print_section("PHASE 3 : Analyse par MonitoringAgent")
    
    print("🔍 MonitoringAgent analyse les données...\n")
    monitoring_result = monitoring.process(sensor_data)
    
    print(f"📋 Résultat de l'analyse:")
    print(f"  • Statut: {monitoring_result['status']}")
    print(f"  • Sévérité: {monitoring_result.get('severity', 'N/A')}")
    
    if monitoring_result.get('anomalies'):
        print(f"\n⚠️  Anomalies détectées ({len(monitoring_result['anomalies'])}):")
        for i, anomaly in enumerate(monitoring_result['anomalies'], 1):
            print(f"  {i}. {anomaly['sensor']}: {anomaly['value']} {anomaly['unit']}")
            print(f"     Seuil dépassé: {anomaly['threshold']} {anomaly['unit']}")
    
    if monitoring_result.get('recommendations'):
        print(f"\n💡 Recommandations:")
        for i, rec in enumerate(monitoring_result['recommendations'], 1):
            print(f"  {i}. {rec}")
    
    time.sleep(2)
    
    # Phase 4: Analyse IA par Claude
    print_section("PHASE 4 : Analyse Avancée par Claude AI")
    
    print("🧠 Claude analyse la situation en profondeur...\n")
    
    situation_description = {
        "description": f"Anomalies critiques détectées sur {sensor_data['machine_id']}",
        "parameters": {
            "temperature": f"{sensor_data['sensors']['temperature']['value']}°C",
            "vibration": f"{sensor_data['sensors']['vibration']['value']} mm/s",
            "machine_id": sensor_data['machine_id'],
            "location": sensor_data['location']
        }
    }
    
    claude_result = claude.analyze_sst_situation(situation_description)
    
    if claude_result['success']:
        print("✅ Analyse IA terminée\n")
        print(f"📊 Tokens utilisés: {claude_result['tokens_used']['total']}")
        print(f"🤖 Modèle: {claude_result['model']}\n")
        print("📋 Analyse de Claude:\n")
        print("-" * 70)
        print(claude_result['response'])
        print("-" * 70)
    else:
        print(f"❌ Erreur lors de l'analyse IA: {claude_result.get('error', 'Unknown')}")
    
    time.sleep(2)
    
    # Phase 5: Validation par SecurityManager
    print_section("PHASE 5 : Validation par SecurityManager")
    
    print("🛡️  SecurityManager valide les actions proposées...\n")
    
    # Action proposée: Arrêt d'urgence
    proposed_action = {
        "type": "emergency_shutdown",
        "severity": "CRITICAL",
        "target": sensor_data['machine_id'],
        "reason": "Température et vibrations critiques",
        "parameters": {
            "temperature": sensor_data['sensors']['temperature']['value'],
            "vibration": sensor_data['sensors']['vibration']['value']
        }
    }
    
    print(f"🔧 Action proposée: {proposed_action['type']}")
    print(f"⚠️  Sévérité: {proposed_action['severity']}")
    print(f"🎯 Cible: {proposed_action['target']}\n")
    
    validation_result = security.process({
        "action_type": "validate",
        "action": proposed_action
    })
    
    print(f"📋 Résultat de la validation:")
    print(f"  • Statut: {validation_result['status']}")
    print(f"  • Raison: {validation_result['reason']}")
    print(f"  • Timestamp: {validation_result['timestamp']}")
    
    time.sleep(2)
    
    # Phase 6: Orchestration
    print_section("PHASE 6 : Orchestration par OrchestratorAgent")
    
    print("🎯 OrchestratorAgent coordonne la réponse...\n")
    
    orchestration_data = {
        "incident_type": "critical_anomaly",
        "monitoring_result": monitoring_result,
        "claude_analysis": claude_result,
        "security_validation": validation_result,
        "sensor_data": sensor_data
    }
    
    orchestration_result = orchestrator.process(orchestration_data)
    
    print(f"📋 Plan d'action orchestré:")
    print(f"  • Statut: {orchestration_result.get('status', 'N/A')}")
    
    if orchestration_result.get('actions'):
        print(f"\n🎬 Actions à exécuter ({len(orchestration_result['actions'])}):")
        for i, action in enumerate(orchestration_result['actions'], 1):
            print(f"  {i}. {action}")
    
    time.sleep(2)
    
    # Phase 7: Audit Trail
    print_section("PHASE 7 : Audit Trail et Conformité")
    
    print("📚 Vérification de l'audit trail...\n")
    
    audit_entries = security.get_audit_trail(limit=10)
    print(f"📝 {len(audit_entries)} entrées dans l'audit trail\n")
    
    print("📋 Dernières entrées:")
    for i, entry in enumerate(audit_entries[-5:], 1):
        print(f"  {i}. [{entry['timestamp']}] {entry['event_type']}")
    
    print("\n✅ Vérification de la conformité:")
    compliance_standards = ["RGPD", "CNESST", "ISO_45001", "LSST"]
    
    for standard in compliance_standards:
        compliant = security.check_compliance(standard)
        status = "✅" if compliant else "❌"
        print(f"  {status} {standard}: {'Conforme' if compliant else 'Non conforme'}")
    
    time.sleep(2)
    
    # Phase 8: Résumé et statistiques
    print_section("PHASE 8 : Résumé de la Démonstration")
    
    print("📊 Statistiques de la session:\n")
    print(f"  • Agents actifs: 3 (Monitoring, Orchestrator, Security)")
    print(f"  • IA utilisée: Claude 4.5 (Mode: {'MOCK' if claude.mock_mode else 'PROD'})")
    print(f"  • Anomalies détectées: {len(monitoring_result.get('anomalies', []))}")
    print(f"  • Actions validées: {validation_result['status']}")
    print(f"  • Entrées audit trail: {len(audit_entries)}")
    print(f"  • Conformité: {sum(1 for std in compliance_standards if security.check_compliance(std))}/{len(compliance_standards)}")
    
    time.sleep(1)
    
    # Phase 9: Arrêt propre
    print_section("PHASE 9 : Arrêt des Agents")
    
    print("🛑 Arrêt propre des agents...\n")
    
    print("  • Arrêt de MonitoringAgent...")
    monitoring.shutdown()
    time.sleep(0.3)
    
    print("  • Arrêt de OrchestratorAgent...")
    orchestrator.shutdown()
    time.sleep(0.3)
    
    print("  • Arrêt de SecurityManager...")
    security.shutdown()
    time.sleep(0.3)
    
    print("\n✅ Tous les agents sont arrêtés proprement !")
    
    # Conclusion
    print_section("DÉMONSTRATION TERMINÉE")
    
    print("""
🎉 La démonstration EDGY-AgenticX5 est terminée avec succès !

📌 Points clés démontrés:
  ✅ Architecture multi-agent fonctionnelle
  ✅ Surveillance en temps réel des équipements
  ✅ Analyse IA avancée des situations SST
  ✅ Validation de sécurité et guardrails
  ✅ Orchestration intelligente des actions
  ✅ Audit trail complet pour conformité
  ✅ Intégration avec Claude 4.5

🚀 Prochaines étapes:
  • Déploiement en environnement de production
  • Intégration avec systèmes SCADA/IoT réels
  • Formation des équipes SST
  • Mise en place monitoring continu

📧 Contact: Mario Deshaies, CAISO @ Preventera.online
🌐 GitHub: https://github.com/Preventera/EDGY-AgenticX5

Merci d'avoir testé EDGY-AgenticX5 ! 🙏
""")

if __name__ == "__main__":
    try:
        run_demo()
    except KeyboardInterrupt:
        print("\n\n⚠️  Démonstration interrompue par l'utilisateur")
    except Exception as e:
        logger.error(f"Erreur durant la démonstration: {e}", exc_info=True)
        print(f"\n❌ Erreur: {e}")
    finally:
        print("\n👋 Au revoir !\n")
