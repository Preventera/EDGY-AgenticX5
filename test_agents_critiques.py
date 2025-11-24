#!/usr/bin/env python3
"""
Test Agents Critiques (A1, AN1, S1) - EDGY-AgenticX5
"""

import sys
import os
from datetime import datetime

# Import des agents
from agent_a1_collecteur import AgentCollecteur, creer_agent_collecteur
from agent_an1_predicteur import AgentPredicteur, creer_agent_predicteur
from agent_s1_router import AgentRouter, creer_agent_router


def test_agent_a1_collecteur():
    """Test de l'agent A1 - Collecteur de données"""
    print("\n" + "=" * 60)
    print("  TEST 1: AGENT A1 - COLLECTEUR DE DONNÉES")
    print("=" * 60)
    
    agent = creer_agent_collecteur()
    
    print(f"\n  Agent ID: {agent.agent_id}")
    print(f"  Nom: {agent.name}")
    
    # Données de test
    donnees_test = [
        {"sensor_type": "temperature", "value": 38.5, "unit": "C", "zone_id": "ZONE-PROD-001"},
        {"sensor_type": "noise", "value": 88.0, "unit": "dB", "zone_id": "ZONE-PROD-001"},
        {"sensor_type": "humidity", "value": 65.0, "unit": "%", "zone_id": "ZONE-PROD-001"},
        {"sensor_type": "vibration", "value": 4.5, "unit": "m/s2", "zone_id": "ZONE-PROD-002"},
        {"sensor_type": "temperature", "value": 95.0, "unit": "F", "zone_id": "ZONE-PROD-002"},  # Conversion F->C
        {"sensor_type": "temperature", "value": 150.0, "unit": "C", "zone_id": "ZONE-TEST"},  # Hors seuils
    ]
    
    print(f"\n  Collecte de {len(donnees_test)} mesures...")
    resultat = agent.collecter(donnees_test)
    
    print(f"\n  Résultats:")
    print(f"    - Collectées: {resultat['donnees_collectees']}")
    print(f"    - Validées: {resultat['donnees_validees']}")
    print(f"    - Rejetées: {resultat['donnees_rejetees']}")
    print(f"    - Temps: {resultat['processing_time_ms']:.2f} ms")
    
    # Vérifier les enrichissements
    if resultat['donnees']:
        print(f"\n  Exemple de donnée enrichie:")
        donnee = resultat['donnees'][0]
        print(f"    - Type: {donnee['type']}")
        print(f"    - Valeur normalisée: {donnee['valeur_normalisee']} {donnee['unite']}")
        print(f"    - Qualité: {donnee['qualite']*100:.0f}%")
        print(f"    - Période: {donnee['enrichissements'].get('periode_journee')}")
        print(f"    - Saison: {donnee['enrichissements'].get('saison')}")
    
    # Stats
    stats = agent.get_stats()
    print(f"\n  Taux de validation: {stats['taux_validation']*100:.1f}%")
    
    success = resultat['donnees_validees'] >= 4  # Au moins 4 sur 6 validées
    print(f"\n  {'[OK]' if success else '[ECHEC]'} Agent A1 validé!")
    return success


def test_agent_an1_predicteur():
    """Test de l'agent AN1 - Prédicteur d'incidents"""
    print("\n" + "=" * 60)
    print("  TEST 2: AGENT AN1 - PRÉDICTEUR D'INCIDENTS")
    print("=" * 60)
    
    agent = creer_agent_predicteur()
    
    print(f"\n  Agent ID: {agent.agent_id}")
    print(f"  Nom: {agent.name}")
    print(f"  Précision modèle: {agent.precision_globale*100:.1f}%")
    
    # Contexte de test (situation à risque)
    contexte_test = {
        "temperature": 42.0,        # Élevée
        "noise": 95.0,              # Élevé
        "heures_travail": 11,       # Fatigue
        "anciennete_jours": 30,     # Peu d'expérience
        "etat_equipement": 0.6,     # Moyen
        "maintenance_ok": 0.7,
        "heure": 15,                # Après-midi
        "vibration": 6.0
    }
    
    print(f"\n  Analyse prédictive en cours...")
    resultat = agent.predire(contexte_test, "ZONE-TEST-001")
    
    print(f"\n  Résultats:")
    print(f"    - Risque global: {resultat['risque_global']['score']}/100 ({resultat['risque_global']['niveau']})")
    print(f"    - Prédictions: {len(resultat['predictions'])}")
    print(f"    - Alertes: {len(resultat['alertes'])}")
    print(f"    - Patterns détectés: {len(resultat['patterns_detectes'])}")
    
    # Top prédictions
    if resultat['predictions']:
        print(f"\n  Top 3 prédictions:")
        for i, pred in enumerate(resultat['predictions'][:3]):
            print(f"    {i+1}. {pred['type_incident']} ({pred['horizon']})")
            print(f"       Probabilité: {pred['probabilite']*100:.1f}%")
            print(f"       Confiance: {pred['niveau_confiance']}")
    
    # Alertes
    if resultat['alertes']:
        print(f"\n  Alertes générées:")
        for alerte in resultat['alertes'][:2]:
            print(f"    - [{alerte['niveau'].upper()}] {alerte['message'][:60]}...")
    
    # Recommandations
    if resultat['recommandations_prioritaires']:
        print(f"\n  Recommandations prioritaires:")
        for rec in resultat['recommandations_prioritaires']:
            print(f"    - [{rec['priorite']}] {rec['type_incident']}: {rec['actions'][0] if rec['actions'] else 'N/A'}")
    
    stats = agent.get_stats()
    print(f"\n  Prédictions totales: {stats['predictions_totales']}")
    
    success = len(resultat['predictions']) > 0 and resultat['risque_global']['score'] > 30
    print(f"\n  {'[OK]' if success else '[ECHEC]'} Agent AN1 validé!")
    return success


def test_agent_s1_router():
    """Test de l'agent S1 - Router intelligent"""
    print("\n" + "=" * 60)
    print("  TEST 3: AGENT S1 - ROUTER INTELLIGENT")
    print("=" * 60)
    
    agent = creer_agent_router()
    
    print(f"\n  Agent ID: {agent.agent_id}")
    print(f"  Nom: {agent.name}")
    print(f"  Agents enregistrés: {len(agent.agents_disponibles)}")
    
    # Requêtes de test
    requetes_test = [
        {
            "id": "REQ-001",
            "contenu": {"message": "Collecte des capteurs de température zone construction"},
            "source": "api"
        },
        {
            "id": "REQ-002",
            "contenu": {"message": "Prédire les risques pour la semaine prochaine usine"},
            "source": "dashboard"
        },
        {
            "id": "REQ-003",
            "contenu": {"message": "ALERTE CRITIQUE: Accident sur chantier nord"},
            "source": "terrain"
        },
        {
            "id": "REQ-004",
            "contenu": {"message": "Générer rapport mensuel SST"},
            "source": "management"
        },
        {
            "id": "REQ-005",
            "contenu": {
                "zone_id": "ZONE-HOPITAL-001",
                "sensor_type": "temperature",
                "value": 28.0
            },
            "source": "iot"
        }
    ]
    
    print(f"\n  Routage de {len(requetes_test)} requêtes...")
    
    resultats = []
    for requete in requetes_test:
        resultat = agent.router(requete)
        resultats.append(resultat)
        
        print(f"\n  Requête {resultat['requete_id']}:")
        print(f"    - Type: {resultat['classification']['type']}")
        print(f"    - Urgence: {resultat['classification']['urgence']}")
        print(f"    - Priorité: {resultat['routage']['priorite']}")
        print(f"    - Agents: {', '.join(resultat['routage']['agents_cibles'])}")
        print(f"    - Pipeline: {' → '.join(resultat['routage']['pipeline'])}")
    
    # Stats
    stats = agent.get_stats()
    print(f"\n  Statistiques:")
    print(f"    - Requêtes routées: {stats['requetes_routees']}")
    print(f"    - Requêtes critiques: {stats['requetes_critiques']}")
    print(f"    - Agents les plus utilisés:")
    agents_sorted = sorted(stats['agents_utilises'].items(), key=lambda x: x[1], reverse=True)
    for agent_id, count in agents_sorted[:3]:
        print(f"      • {agent_id}: {count}")
    
    success = all(r['statut'] == 'routed' for r in resultats)
    print(f"\n  {'[OK]' if success else '[ECHEC]'} Agent S1 validé!")
    return success


def test_integration_agents():
    """Test d'intégration des 3 agents"""
    print("\n" + "=" * 60)
    print("  TEST 4: INTÉGRATION A1 + AN1 + S1")
    print("=" * 60)
    
    # Créer les agents
    router = creer_agent_router()
    collecteur = creer_agent_collecteur()
    predicteur = creer_agent_predicteur()
    
    print(f"\n  Scénario: Workflow complet de détection de risque")
    
    # Étape 1: Router reçoit une requête
    print(f"\n  1. Routage de la requête...")
    requete = {
        "contenu": {
            "action": "analyser risques zone production",
            "zone_id": "ZONE-PROD-001",
            "sensor_readings": [
                {"sensor_type": "temperature", "value": 45.0, "unit": "C"},
                {"sensor_type": "noise", "value": 95.0, "unit": "dB"}
            ]
        }
    }
    
    decision_routage = router.router(requete)
    print(f"    → Type: {decision_routage['classification']['type']}")
    print(f"    → Pipeline: {' → '.join(decision_routage['routage']['pipeline'])}")
    
    # Étape 2: Collecteur normalise les données
    print(f"\n  2. Collecte et normalisation...")
    donnees_capteurs = requete["contenu"]["sensor_readings"]
    for d in donnees_capteurs:
        d["zone_id"] = requete["contenu"]["zone_id"]
    
    resultat_collecte = collecteur.collecter(donnees_capteurs)
    print(f"    → Données validées: {resultat_collecte['donnees_validees']}/{resultat_collecte['donnees_collectees']}")
    
    # Étape 3: Prédicteur analyse les risques
    print(f"\n  3. Prédiction des risques...")
    contexte = {
        "temperature": 45.0,
        "noise": 95.0,
        "zone_id": "ZONE-PROD-001"
    }
    
    resultat_prediction = predicteur.predire(contexte, "ZONE-PROD-001")
    print(f"    → Risque global: {resultat_prediction['risque_global']['score']}/100")
    print(f"    → Niveau: {resultat_prediction['risque_global']['niveau']}")
    print(f"    → Alertes: {len(resultat_prediction['alertes'])}")
    
    # Résumé
    print(f"\n  Workflow complet exécuté avec succès!")
    
    success = (
        decision_routage['statut'] == 'routed' and
        resultat_collecte['donnees_validees'] > 0 and
        resultat_prediction['risque_global']['score'] > 0
    )
    
    print(f"\n  {'[OK]' if success else '[ECHEC]'} Intégration validée!")
    return success


def main():
    print("\n" + "=" * 60)
    print("  EDGY-AgenticX5 - TEST AGENTS CRITIQUES (A1, AN1, S1)")
    print("=" * 60)
    print(f"  Timestamp: {datetime.utcnow().isoformat()}")
    
    tests = [
        ("Agent A1 - Collecteur", test_agent_a1_collecteur),
        ("Agent AN1 - Prédicteur", test_agent_an1_predicteur),
        ("Agent S1 - Router", test_agent_s1_router),
        ("Intégration A1+AN1+S1", test_integration_agents)
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"\n  [ERREUR] {name}: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    # Résumé
    print("\n" + "=" * 60)
    print("  RÉSUMÉ DES TESTS")
    print("=" * 60)
    
    passed = 0
    for name, success in results:
        status = "[OK]" if success else "[ECHEC]"
        print(f"  {status} {name}")
        if success:
            passed += 1
    
    print(f"\n  {passed}/{len(tests)} tests réussis")
    
    if passed == len(tests):
        print("\n  🎉 TOUS LES AGENTS CRITIQUES SONT OPÉRATIONNELS!")
    
    print("=" * 60 + "\n")
    
    return passed == len(tests)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
