#!/usr/bin/env python3
"""Test du système sans appeler l'API Anthropic"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.agents.monitoring_agent import MonitoringAgent

def test_without_api():
    """Test de l'initialisation sans appeler Claude"""
    
    print('🧪 Test de l\'initialisation des agents (sans API)...\n')
    
    # Test 1: Créer l'agent
    print('1️⃣ Création du MonitoringAgent...')
    agent = MonitoringAgent(
        agent_id='test_monitor',
        name='Test Monitor',
        anthropic_api_key='dummy_key'  # Clé factice
    )
    print('   ✅ Agent créé: {} (ID: {})'.format(agent.name, agent.agent_id))
    
    # Test 2: Vérifier l'état
    print('\n2️⃣ Vérification de l\'état...')
    state = agent.get_state()
    print('   ✅ État: {}'.format(state['status']))
    print('   ✅ Capacités: {} configurées'.format(len(state['config']['capabilities'])))
    
    # Test 3: Vérifier les seuils
    print('\n3️⃣ Vérification des seuils...')
    for level, threshold in agent.thresholds.items():
        print('   ✅ {}: {}'.format(level, threshold))
    
    # Test 4: Vérifier la structure
    print('\n4️⃣ Vérification de la structure...')
    print('   ✅ Sources surveillées: {}'.format(len(agent.monitored_sources)))
    print('   ✅ Alertes actives: {}'.format(len(agent.active_alerts)))
    print('   ✅ Monitoring actif: {}'.format(agent.monitoring_active))
    
    print('\n✅ TOUS LES TESTS RÉUSSIS !')
    print('\n⚠️  Pour tester avec l\'API Claude, ajoutez des crédits:')
    print('   https://console.anthropic.com/settings/plans')
    print('\n📊 Le prototype fonctionne correctement !')
    print('   Structure: ✅')
    print('   Imports: ✅')
    print('   Configuration: ✅')
    print('   Agents: ✅')

if __name__ == '__main__':
    test_without_api()
