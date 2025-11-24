#!/usr/bin/env python3
"""
Test Agents Sectoriels SCIAN - EDGY-AgenticX5
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from agents_sectoriels_scian import (
    SecteurSCIAN,
    AgentSectoriel,
    RegistreAgentsSectoriels,
    creer_registre_agents,
    creer_agent_construction,
    creer_agent_fabrication
)
from datetime import datetime


def test_agent_construction():
    """Test de l'agent Construction (SCIAN 23)"""
    print("\n" + "=" * 60)
    print("  TEST 1: AGENT CONSTRUCTION (SCIAN 23)")
    print("=" * 60)
    
    agent = creer_agent_construction()
    info = agent.get_info()
    
    print(f"\n  Agent ID: {info['agent_id']}")
    print(f"  Secteur: {info['secteur']}")
    print(f"  Code SCIAN: {info['code_scian']}")
    print(f"  Précision: {info['precision_prediction']*100:.1f}%")
    
    print(f"\n  Risques principaux:")
    for risque in info['risques_principaux']:
        print(f"    - {risque}")
    
    print(f"\n  Seuils critiques:")
    for seuil, valeur in info['seuils_critiques'].items():
        print(f"    - {seuil}: {valeur}")
    
    # Test avec données capteurs
    donnees = [
        {"sensor_type": "temperature", "value": 38.0, "unit": "C"},
        {"sensor_type": "noise", "value": 92.0, "unit": "dB"},
        {"sensor_type": "height", "value": 8.0, "unit": "m"}
    ]
    
    print(f"\n  Analyse de données:")
    resultat = agent.analyser_risques(donnees)
    
    print(f"    Score risque: {resultat['score_risque']}")
    print(f"    Niveau: {resultat['niveau_risque']}")
    print(f"    Alertes: {len(resultat['alertes'])}")
    print(f"    Recommandations: {len(resultat['recommandations'])}")
    
    if resultat['alertes']:
        print(f"\n  Alertes générées:")
        for alerte in resultat['alertes']:
            print(f"    - {alerte['sensor_type']}: {alerte['value']} (seuil: {alerte['seuil']})")
    
    print("\n  [OK] Agent Construction validé!")
    return True


def test_agent_fabrication():
    """Test de l'agent Fabrication (SCIAN 31-33)"""
    print("\n" + "=" * 60)
    print("  TEST 2: AGENT FABRICATION (SCIAN 31-33)")
    print("=" * 60)
    
    agent = creer_agent_fabrication()
    info = agent.get_info()
    
    print(f"\n  Agent ID: {info['agent_id']}")
    print(f"  Secteur: {info['secteur']}")
    print(f"  Précision: {info['precision_prediction']*100:.1f}%")
    
    # Test avec données capteurs
    donnees = [
        {"sensor_type": "vibration", "value": 6.5, "unit": "m/s2"},
        {"sensor_type": "noise", "value": 88.0, "unit": "dB"},
        {"sensor_type": "temperature", "value": 32.0, "unit": "C"}
    ]
    
    resultat = agent.analyser_risques(donnees)
    
    print(f"\n  Analyse:")
    print(f"    Score: {resultat['score_risque']}")
    print(f"    Niveau: {resultat['niveau_risque']}")
    print(f"    Alertes: {len(resultat['alertes'])}")
    
    print("\n  [OK] Agent Fabrication validé!")
    return True


def test_registre_agents():
    """Test du registre des agents"""
    print("\n" + "=" * 60)
    print("  TEST 3: REGISTRE DES AGENTS SECTORIELS")
    print("=" * 60)
    
    registre = creer_registre_agents()
    
    agents = registre.lister_agents()
    print(f"\n  {len(agents)} agents enregistrés:")
    for agent in agents:
        print(f"    - {agent['agent_id']}: {agent['secteur']} ({agent['precision_prediction']*100:.1f}%)")
    
    print("\n  [OK] Registre validé!")
    return True


def test_selection_agent_par_zone():
    """Test de la sélection d'agent par type de zone"""
    print("\n" + "=" * 60)
    print("  TEST 4: SELECTION AGENT PAR ZONE")
    print("=" * 60)
    
    registre = creer_registre_agents()
    
    zones_test = [
        ("Chantier de construction nord", "23"),
        ("Usine de fabrication métallique", "31-33"),
        ("Mine à ciel ouvert", "21"),
        ("Hôpital régional", "62"),
        ("Entrepôt logistique", "48-49"),
        ("Bureau administratif", None)  # Pas d'agent
    ]
    
    print(f"\n  Tests de sélection:")
    for zone, attendu in zones_test:
        agent = registre.get_agent_pour_zone(zone)
        if agent:
            resultat = agent.config.code_scian
            status = "[OK]" if resultat == attendu else "[DIFF]"
            print(f"    {status} {zone} -> {agent.agent_id}")
        else:
            status = "[OK]" if attendu is None else "[MISS]"
            print(f"    {status} {zone} -> Aucun agent")
    
    print("\n  [OK] Sélection par zone validée!")
    return True


def test_analyse_complete():
    """Test d'analyse complète avec agent adapté"""
    print("\n" + "=" * 60)
    print("  TEST 5: ANALYSE COMPLETE MULTI-SECTEURS")
    print("=" * 60)
    
    registre = creer_registre_agents()
    
    # Scénario 1: Chantier de construction
    print("\n  --- Scénario: Chantier de construction ---")
    donnees_chantier = [
        {"sensor_type": "temperature", "value": 42.0, "unit": "C"},
        {"sensor_type": "noise", "value": 95.0, "unit": "dB"},
        {"sensor_type": "dust", "value": 5.0, "unit": "mg/m3"}
    ]
    
    resultat = registre.analyser_avec_agent_adapte("chantier", donnees_chantier)
    
    print(f"    Agent: {resultat.get('agent_id')}")
    print(f"    Niveau risque: {resultat.get('niveau_risque')}")
    print(f"    Score: {resultat.get('score_risque')}")
    print(f"    Alertes: {len(resultat.get('alertes', []))}")
    
    if resultat.get('recommandations'):
        print(f"    Recommandations:")
        for rec in resultat['recommandations']:
            print(f"      - [{rec['priorite']}] {rec['titre']}")
    
    # Scénario 2: Usine manufacturing
    print("\n  --- Scénario: Usine manufacturing ---")
    donnees_usine = [
        {"sensor_type": "vibration", "value": 7.0, "unit": "m/s2"},
        {"sensor_type": "noise", "value": 90.0, "unit": "dB"}
    ]
    
    resultat = registre.analyser_avec_agent_adapte("usine", donnees_usine)
    
    print(f"    Agent: {resultat.get('agent_id')}")
    print(f"    Niveau risque: {resultat.get('niveau_risque')}")
    print(f"    Alertes: {len(resultat.get('alertes', []))}")
    
    print("\n  [OK] Analyses complètes validées!")
    return True


def test_stats_globales():
    """Test des statistiques globales"""
    print("\n" + "=" * 60)
    print("  TEST 6: STATISTIQUES GLOBALES")
    print("=" * 60)
    
    registre = creer_registre_agents()
    
    # Exécuter quelques analyses pour générer des stats
    registre.analyser_avec_agent_adapte("chantier", [{"sensor_type": "temperature", "value": 40}])
    registre.analyser_avec_agent_adapte("usine", [{"sensor_type": "noise", "value": 90}])
    registre.analyser_avec_agent_adapte("mine", [{"sensor_type": "dust", "value": 4}])
    
    stats = registre.get_stats_globales()
    
    print(f"\n  Nombre d'agents: {stats['nombre_agents']}")
    print(f"  Secteurs couverts: {', '.join(stats['secteurs_couverts'])}")
    print(f"  Analyses totales: {stats['analyses_totales']}")
    print(f"  Alertes totales: {stats['alertes_totales']}")
    print(f"  Recommandations totales: {stats['recommandations_totales']}")
    
    print("\n  [OK] Statistiques validées!")
    return True


def main():
    print("\n" + "=" * 60)
    print("  EDGY-AgenticX5 - TEST AGENTS SECTORIELS SCIAN")
    print("=" * 60)
    print(f"  Timestamp: {datetime.utcnow().isoformat()}")
    
    tests = [
        ("Agent Construction", test_agent_construction),
        ("Agent Fabrication", test_agent_fabrication),
        ("Registre Agents", test_registre_agents),
        ("Sélection par Zone", test_selection_agent_par_zone),
        ("Analyse Complète", test_analyse_complete),
        ("Statistiques Globales", test_stats_globales)
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
    
    print(f"\n  {passed}/{len(tests)} tests réussis")
    
    if passed == len(tests):
        print("\n  🎉 TOUS LES AGENTS SECTORIELS SONT OPERATIONNELS!")
    
    print("=" * 60 + "\n")
    
    return passed == len(tests)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
