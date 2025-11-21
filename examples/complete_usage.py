"""
Exemple d'utilisation complète de EDGY-AgenticX5.

Ce script démontre l'utilisation des différents composants du système
pour un cas d'usage SST réel.
"""

import asyncio
import os
from datetime import datetime
from typing import Dict, Any

from src.agents.monitoring_agent import MonitoringAgent
from src.agents.orchestrator_agent import OrchestratorAgent
from src.utils.config import get_settings
from src.utils.logger import get_logger


logger = get_logger("example")


async def scenario_1_monitoring_simple():
    """
    Scénario 1: Surveillance simple d'un site industriel.
    
    Un agent de monitoring surveille les données de capteurs
    et génère des alertes si nécessaire.
    """
    logger.info("=== Scénario 1: Monitoring Simple ===")
    
    # Initialiser l'agent de monitoring
    monitoring_agent = MonitoringAgent(
        agent_id="monitor_site_a",
        name="Site A Monitor",
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY")
    )
    
    # Démarrer la surveillance
    await monitoring_agent.start_monitoring(
        data_sources=["temp_sensors", "gas_detectors", "incident_reports"],
        alert_threshold="medium"
    )
    
    # Simuler des données de capteurs
    sensor_data = {
        "site": "Site A - Zone Production",
        "timestamp": datetime.now().isoformat(),
        "sensors": {
            "temperature": {
                "zone_1": 28.5,
                "zone_2": 32.1,  # Légèrement élevée
                "zone_3": 25.0
            },
            "humidity": {
                "zone_1": 45,
                "zone_2": 55,
                "zone_3": 50
            },
            "gas_levels": {
                "co2": 400,  # ppm
                "co": 5      # ppm
            }
        },
        "equipment_status": {
            "ventilation_zone_2": "reduced",  # Anomalie
            "emergency_exits": "operational"
        }
    }
    
    # Traiter les données
    logger.info("Traitement des données de capteurs...")
    result = await monitoring_agent.process(sensor_data)
    
    # Afficher les résultats
    logger.info(f"Analyse complétée: {result['risks_detected']} risques détectés")
    
    if result["alerts"]:
        logger.warning(f"{len(result['alerts'])} alertes générées:")
        for i, alert in enumerate(result["alerts"], 1):
            logger.warning(f"  Alerte {i}: {alert['severity']} - {alert['description']}")
            logger.info(f"    Actions recommandées:")
            for action in alert['recommended_actions']:
                logger.info(f"      - {action}")
    
    if result["recommendations"]:
        logger.info("Recommandations préventives:")
        for rec in result["recommendations"]:
            logger.info(f"  - {rec}")
    
    # Arrêter la surveillance
    await monitoring_agent.stop_monitoring()
    
    return result


async def scenario_2_orchestration_multi_agents():
    """
    Scénario 2: Orchestration multi-agents pour analyse complète.
    
    Un orchestrateur coordonne plusieurs agents pour une analyse
    approfondie d'un incident SST.
    """
    logger.info("\n=== Scénario 2: Orchestration Multi-Agents ===")
    
    # Initialiser l'orchestrateur
    orchestrator = OrchestratorAgent(
        agent_id="orchestrator_01",
        name="SST Orchestrator",
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY")
    )
    
    # Créer et enregistrer les agents
    monitoring_agent = MonitoringAgent(
        agent_id="monitor_01",
        name="Monitoring Agent",
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY")
    )
    
    orchestrator.register_agent("monitor_01", monitoring_agent)
    
    # Définir une demande d'analyse
    analysis_request = {
        "description": """
        Analyser un incident de quasi-accident dans l'atelier de production.
        Un employé a glissé près d'une machine en fonctionnement mais n'a pas été blessé.
        Identifier les causes racines et proposer des actions correctives.
        """,
        "context": {
            "location": "Atelier Production - Zone 2",
            "datetime": "2025-01-15 14:30",
            "employee_id": "EMP-12345",
            "equipment_involved": "Machine CNC-04",
            "witnesses": 2,
            "conditions": {
                "floor_condition": "légèrement humide",
                "lighting": "normal",
                "noise_level": "élevé"
            }
        }
    }
    
    # Exécuter le workflow orchestré
    logger.info("Lancement de l'analyse orchestrée...")
    result = await orchestrator.process(analysis_request)
    
    # Afficher les résultats consolidés
    logger.info("Analyse orchestrée complétée")
    logger.info(f"Workflow ID: {result['workflow_id']}")
    
    if "results" in result and result["results"]:
        consolidated = result["results"]
        
        if "summary" in consolidated:
            logger.info(f"\nSynthèse: {consolidated['summary']}")
        
        if "key_findings" in consolidated:
            logger.info("\nPoints clés identifiés:")
            for finding in consolidated["key_findings"]:
                logger.info(f"  - {finding}")
        
        if "consolidated_recommendations" in consolidated:
            logger.info("\nRecommandations consolidées:")
            for rec in consolidated["consolidated_recommendations"]:
                logger.info(f"  - {rec}")
        
        if "priority_actions" in consolidated:
            logger.info("\nActions prioritaires:")
            for action in consolidated["priority_actions"]:
                logger.info(f"  - {action}")
    
    return result


async def scenario_3_cartographie_edgy():
    """
    Scénario 3: Utilisation de la cartographie EDGY.
    
    Créer une cartographie organisationnelle EDGY pour identifier
    les zones de friction et opportunités d'amélioration SST.
    """
    logger.info("\n=== Scénario 3: Cartographie EDGY ===")
    
    # TODO: Implémenter quand le module EDGY sera créé
    logger.info("Module de cartographie EDGY en cours de développement...")
    logger.info("Cette fonctionnalité permettra de:")
    logger.info("  - Cartographier l'organisation selon le framework EDGY")
    logger.info("  - Identifier les zones blanches et points de friction")
    logger.info("  - Visualiser les liens entre identité, expérience et opérations")
    logger.info("  - Prioriser les interventions SST")
    
    return {"status": "pending", "message": "Module en développement"}


async def main():
    """Fonction principale exécutant tous les scénarios."""
    
    logger.info("╔═══════════════════════════════════════════════════════════╗")
    logger.info("║          EDGY-AgenticX5 - Exemples d'Utilisation         ║")
    logger.info("║          Système Agentique Multi-Agent pour SST          ║")
    logger.info("╚═══════════════════════════════════════════════════════════╝\n")
    
    # Vérifier la configuration
    settings = get_settings()
    if not settings.anthropic_api_key:
        logger.error("ANTHROPIC_API_KEY non configurée!")
        logger.error("Définissez la variable d'environnement ou le fichier .env")
        return
    
    logger.info(f"Environnement: {settings.environment}")
    logger.info(f"Log Level: {settings.log_level}\n")
    
    try:
        # Exécuter les scénarios
        result1 = await scenario_1_monitoring_simple()
        
        await asyncio.sleep(2)  # Pause entre les scénarios
        
        result2 = await scenario_2_orchestration_multi_agents()
        
        await asyncio.sleep(2)
        
        result3 = await scenario_3_cartographie_edgy()
        
        # Résumé final
        logger.info("\n╔═══════════════════════════════════════════════════════════╗")
        logger.info("║                    Résumé d'Exécution                     ║")
        logger.info("╚═══════════════════════════════════════════════════════════╝")
        logger.info(f"✓ Scénario 1: Monitoring - {result1.get('status', 'unknown')}")
        logger.info(f"✓ Scénario 2: Orchestration - {result2.get('status', 'unknown')}")
        logger.info(f"✓ Scénario 3: Cartographie EDGY - {result3.get('status', 'unknown')}")
        logger.info("\nTous les scénarios complétés avec succès!")
        
    except Exception as e:
        logger.error(f"Erreur lors de l'exécution: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    # Exécuter le programme
    asyncio.run(main())
