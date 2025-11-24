#!/usr/bin/env python3
"""
Test API FastAPI - EDGY-AgenticX5
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"


def test_health():
    """Test endpoint /health"""
    print("\n" + "=" * 50)
    print("  TEST: /health")
    print("=" * 50)
    
    response = requests.get(f"{BASE_URL}/health")
    data = response.json()
    
    print(f"  Status: {data['status']}")
    print(f"  Version: {data['version']}")
    print(f"  Components:")
    for comp, status in data['components'].items():
        icon = "[OK]" if status else "[--]"
        print(f"    {icon} {comp}")
    
    print(f"  Neo4j: {data['neo4j_stats']}")
    return response.status_code == 200


def test_zones():
    """Test endpoint /api/v1/zones"""
    print("\n" + "=" * 50)
    print("  TEST: /api/v1/zones")
    print("=" * 50)
    
    response = requests.get(f"{BASE_URL}/api/v1/zones")
    zones = response.json()
    
    print(f"  {len(zones)} zones trouvees:")
    for z in zones[:5]:
        print(f"    - {z.get('zone_id')}: {z.get('nom') or 'N/A'}")
    
    if len(zones) > 5:
        print(f"    ... et {len(zones) - 5} autres")
    
    return response.status_code == 200


def test_risks():
    """Test endpoint /api/v1/risks"""
    print("\n" + "=" * 50)
    print("  TEST: /api/v1/risks")
    print("=" * 50)
    
    response = requests.get(f"{BASE_URL}/api/v1/risks")
    risks = response.json()
    
    print(f"  {len(risks)} risques trouves:")
    for r in risks[:5]:
        print(f"    - {r.get('risque_id')}: {r.get('description') or 'N/A'}")
    
    return response.status_code == 200


def test_near_misses():
    """Test endpoint /api/v1/near-misses"""
    print("\n" + "=" * 50)
    print("  TEST: /api/v1/near-misses")
    print("=" * 50)
    
    response = requests.get(f"{BASE_URL}/api/v1/near-misses")
    near_misses = response.json()
    
    print(f"  {len(near_misses)} near-misses trouves:")
    for nm in near_misses[:5]:
        print(f"    - {nm.get('near_miss_id')}: {nm.get('type_risque')} ({nm.get('potentiel_gravite')})")
    
    return response.status_code == 200


def test_workflow():
    """Test endpoint /api/v1/workflow/process"""
    print("\n" + "=" * 50)
    print("  TEST: /api/v1/workflow/process")
    print("=" * 50)
    
    payload = {
        "sensor_readings": [
            {
                "sensor_id": "TEST-TEMP-001",
                "sensor_type": "temperature",
                "value": 38.0,
                "unit": "C",
                "zone_id": "ZONE-PROD-001"
            },
            {
                "sensor_id": "TEST-NOISE-001",
                "sensor_type": "noise",
                "value": 82.0,
                "unit": "dB",
                "zone_id": "ZONE-PROD-001"
            }
        ],
        "zone_id": "ZONE-PROD-001"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/workflow/process",
        json=payload
    )
    data = response.json()
    
    print(f"  Status: {data.get('status')}")
    print(f"  Workflow ID: {data.get('workflow_id')}")
    print(f"  Risk Level: {data.get('risk_level')}")
    print(f"  Risk Score: {data.get('risk_score')}")
    print(f"  Alertes: {len(data.get('alerts', []))}")
    print(f"  Recommandations: {len(data.get('recommendations', []))}")
    
    return response.status_code == 200 and data.get('status') == 'completed'


def test_simulate_critical():
    """Test endpoint /api/v1/simulate/critical"""
    print("\n" + "=" * 50)
    print("  TEST: /api/v1/simulate/critical")
    print("=" * 50)
    
    response = requests.post(f"{BASE_URL}/api/v1/simulate/critical")
    data = response.json()
    
    print(f"  Status: {data.get('status')}")
    print(f"  Risk Level: {data.get('risk_level')}")
    print(f"  Risk Score: {data.get('risk_score')}")
    
    if data.get('alerts'):
        print(f"  Alertes:")
        for alert in data['alerts']:
            print(f"    - {alert.get('sensor_type')}: {alert.get('value')} ({alert.get('severity')})")
    
    if data.get('recommendations'):
        print(f"  Recommandations:")
        for rec in data['recommendations']:
            print(f"    - [{rec.get('priority')}] {rec.get('title')}")
    
    return response.status_code == 200 and data.get('risk_level') == 'critical'


def test_stats():
    """Test endpoint /api/v1/stats"""
    print("\n" + "=" * 50)
    print("  TEST: /api/v1/stats")
    print("=" * 50)
    
    response = requests.get(f"{BASE_URL}/api/v1/stats")
    data = response.json()
    
    print(f"  Workflows executes: {data.get('workflows_executed')}")
    print(f"  Workflows reussis: {data.get('workflows_successful')}")
    print(f"  Taux de succes: {data.get('success_rate')}%")
    print(f"  Alertes generees: {data.get('alerts_generated')}")
    print(f"  Neo4j noeuds: {data.get('neo4j_nodes')}")
    print(f"  Neo4j relations: {data.get('neo4j_relationships')}")
    
    return response.status_code == 200


def main():
    print("\n" + "=" * 50)
    print("  EDGY-AgenticX5 - TEST API FASTAPI")
    print("=" * 50)
    print(f"  URL: {BASE_URL}")
    print(f"  Timestamp: {datetime.utcnow().isoformat()}")
    
    tests = [
        ("Health Check", test_health),
        ("Liste Zones", test_zones),
        ("Liste Risques", test_risks),
        ("Near-Misses", test_near_misses),
        ("Workflow Process", test_workflow),
        ("Simulate Critical", test_simulate_critical),
        ("Statistiques", test_stats),
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except requests.exceptions.ConnectionError:
            print(f"\n  [ERREUR] API non accessible sur {BASE_URL}")
            print("  Lancez d'abord: python api.py")
            return
        except Exception as e:
            print(f"\n  [ERREUR] {name}: {e}")
            results.append((name, False))
    
    # Résumé
    print("\n" + "=" * 50)
    print("  RESUME DES TESTS API")
    print("=" * 50)
    
    passed = 0
    for name, success in results:
        status = "[OK]" if success else "[ECHEC]"
        print(f"  {status} {name}")
        if success:
            passed += 1
    
    print(f"\n  {passed}/{len(tests)} tests reussis")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    main()
