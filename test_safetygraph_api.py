#!/usr/bin/env python3
"""
🧪 Tests et exemples pour SafetyGraph API
EDGY-AgenticX5 | Preventera | GenAISafety

Utilisation:
    python test_safetygraph_api.py

Prérequis:
    pip install requests rich

L'API doit être démarrée sur http://localhost:8002
"""

import requests
import json
from datetime import datetime

# Configuration
API_BASE = "http://localhost:8002"

# Couleurs pour affichage
class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    CYAN = "\033[96m"
    YELLOW = "\033[93m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


def print_header(title: str):
    """Afficher un en-tête"""
    print(f"\n{Colors.CYAN}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}  {title}{Colors.RESET}")
    print(f"{Colors.CYAN}{'='*60}{Colors.RESET}\n")


def print_success(msg: str):
    print(f"{Colors.GREEN}✅ {msg}{Colors.RESET}")


def print_error(msg: str):
    print(f"{Colors.RED}❌ {msg}{Colors.RESET}")


def print_info(msg: str):
    print(f"{Colors.YELLOW}ℹ️  {msg}{Colors.RESET}")


def test_endpoint(method: str, endpoint: str, description: str, params: dict = None, json_data: dict = None):
    """Tester un endpoint et afficher le résultat"""
    url = f"{API_BASE}{endpoint}"
    print(f"\n{Colors.BOLD}📌 {description}{Colors.RESET}")
    print(f"   {method} {endpoint}")
    
    try:
        if method == "GET":
            response = requests.get(url, params=params, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=json_data, timeout=10)
        else:
            print_error(f"Méthode non supportée: {method}")
            return None
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Status: {response.status_code}")
            
            # Afficher un résumé des données
            if isinstance(data, dict):
                for key, value in data.items():
                    if isinstance(value, list):
                        print(f"   📊 {key}: {len(value)} éléments")
                        if len(value) > 0 and isinstance(value[0], dict):
                            print(f"      Premier: {json.dumps(value[0], ensure_ascii=False)[:100]}...")
                    elif isinstance(value, (int, float)):
                        print(f"   📊 {key}: {value}")
                    elif isinstance(value, str) and len(value) < 100:
                        print(f"   📊 {key}: {value}")
            
            return data
        else:
            print_error(f"Status: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return None
            
    except requests.exceptions.ConnectionError:
        print_error("Connexion refusée - L'API n'est pas démarrée")
        print_info(f"Démarrez l'API avec: uvicorn safetygraph_api:app --port 8002")
        return None
    except Exception as e:
        print_error(f"Erreur: {e}")
        return None


def run_all_tests():
    """Exécuter tous les tests"""
    
    print_header("🛡️ SafetyGraph API - Suite de Tests")
    print(f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔗 API: {API_BASE}")
    
    tests_passed = 0
    tests_failed = 0
    
    # ========================================
    # Tests de santé
    # ========================================
    print_header("1️⃣ Tests de Santé")
    
    if test_endpoint("GET", "/", "Page d'accueil"):
        tests_passed += 1
    else:
        tests_failed += 1
    
    if test_endpoint("GET", "/health", "Health check"):
        tests_passed += 1
    else:
        tests_failed += 1
    
    # ========================================
    # Tests statistiques
    # ========================================
    print_header("2️⃣ Tests Statistiques")
    
    if test_endpoint("GET", "/api/v1/stats", "Statistiques globales"):
        tests_passed += 1
    else:
        tests_failed += 1
    
    if test_endpoint("GET", "/api/v1/stats/kpis", "KPIs calculés"):
        tests_passed += 1
    else:
        tests_failed += 1
    
    # ========================================
    # Tests secteurs SCIAN
    # ========================================
    print_header("3️⃣ Tests Secteurs SCIAN")
    
    if test_endpoint("GET", "/api/v1/sectors", "Liste des secteurs"):
        tests_passed += 1
    else:
        tests_failed += 1
    
    if test_endpoint("GET", "/api/v1/sectors/54", "Détail secteur 54 (Services pro)"):
        tests_passed += 1
    else:
        tests_failed += 1
    
    if test_endpoint("GET", "/api/v1/sectors/priority/cnesst", "Secteurs prioritaires CNESST"):
        tests_passed += 1
    else:
        tests_failed += 1
    
    # ========================================
    # Tests risques
    # ========================================
    print_header("4️⃣ Tests Risques")
    
    if test_endpoint("GET", "/api/v1/risks", "Liste des risques", {"limit": 10}):
        tests_passed += 1
    else:
        tests_failed += 1
    
    if test_endpoint("GET", "/api/v1/risks/tolerance-zero", "Risques Tolérance Zéro"):
        tests_passed += 1
    else:
        tests_failed += 1
    
    if test_endpoint("GET", "/api/v1/risks/categories", "Catégories de risques"):
        tests_passed += 1
    else:
        tests_failed += 1
    
    if test_endpoint("GET", "/api/v1/risks/matrix", "Matrice de risques"):
        tests_passed += 1
    else:
        tests_failed += 1
    
    # ========================================
    # Tests zones
    # ========================================
    print_header("5️⃣ Tests Zones")
    
    if test_endpoint("GET", "/api/v1/zones", "Liste des zones"):
        tests_passed += 1
    else:
        tests_failed += 1
    
    if test_endpoint("GET", "/api/v1/zones/hotspots", "Zones hotspots"):
        tests_passed += 1
    else:
        tests_failed += 1
    
    if test_endpoint("GET", "/api/v1/zones/by-level", "Distribution par niveau"):
        tests_passed += 1
    else:
        tests_failed += 1
    
    # ========================================
    # Tests personnes
    # ========================================
    print_header("6️⃣ Tests Personnes")
    
    if test_endpoint("GET", "/api/v1/persons/age-distribution", "Distribution par âge"):
        tests_passed += 1
    else:
        tests_failed += 1
    
    if test_endpoint("GET", "/api/v1/persons/certifications", "Certifications SST"):
        tests_passed += 1
    else:
        tests_failed += 1
    
    if test_endpoint("GET", "/api/v1/persons/exposed", "Personnes exposées", {"min_risks": 2}):
        tests_passed += 1
    else:
        tests_failed += 1
    
    # ========================================
    # Tests alertes
    # ========================================
    print_header("7️⃣ Tests Alertes")
    
    if test_endpoint("GET", "/api/v1/alerts", "Alertes actives"):
        tests_passed += 1
    else:
        tests_failed += 1
    
    if test_endpoint("GET", "/api/v1/alerts/young-workers", "Alertes jeunes travailleurs"):
        tests_passed += 1
    else:
        tests_failed += 1
    
    # ========================================
    # Tests conformité
    # ========================================
    print_header("8️⃣ Tests Conformité")
    
    if test_endpoint("GET", "/api/v1/compliance/certification-coverage", "Couverture certifications"):
        tests_passed += 1
    else:
        tests_failed += 1
    
    if test_endpoint("GET", "/api/v1/compliance/missing-epi", "EPI manquants"):
        tests_passed += 1
    else:
        tests_failed += 1
    
    # ========================================
    # Tests prédictifs
    # ========================================
    print_header("9️⃣ Tests Analyses Prédictives")
    
    if test_endpoint("GET", "/api/v1/predictive/features", "Features pour ML"):
        tests_passed += 1
    else:
        tests_failed += 1
    
    if test_endpoint("GET", "/api/v1/predictive/risk-score-by-org", "Scores par organisation"):
        tests_passed += 1
    else:
        tests_failed += 1
    
    if test_endpoint("GET", "/api/v1/predictive/sector-correlation", "Corrélations secteur-risque"):
        tests_passed += 1
    else:
        tests_failed += 1
    
    # ========================================
    # Tests agents IA
    # ========================================
    print_header("🔟 Tests Agents IA")
    
    if test_endpoint("GET", "/api/v1/agents/visionai/targets", "Cibles VisionAI"):
        tests_passed += 1
    else:
        tests_failed += 1
    
    if test_endpoint("GET", "/api/v1/agents/ergoai/targets", "Cibles ErgoAI"):
        tests_passed += 1
    else:
        tests_failed += 1
    
    if test_endpoint("GET", "/api/v1/agents/alertai/triggers", "Déclencheurs AlertAI"):
        tests_passed += 1
    else:
        tests_failed += 1
    
    if test_endpoint("GET", "/api/v1/agents/complyai/gaps", "Écarts ComplyAI"):
        tests_passed += 1
    else:
        tests_failed += 1
    
    # ========================================
    # Tests recherche
    # ========================================
    print_header("1️⃣1️⃣ Tests Recherche")
    
    if test_endpoint("GET", "/api/v1/search/organizations", "Recherche organisations", {"q": "CGI"}):
        tests_passed += 1
    else:
        tests_failed += 1
    
    if test_endpoint("GET", "/api/v1/search/risks", "Recherche risques", {"q": "chute"}):
        tests_passed += 1
    else:
        tests_failed += 1
    
    # ========================================
    # Test requête Cypher personnalisée
    # ========================================
    print_header("1️⃣2️⃣ Test Requête Cypher")
    
    cypher_query = {
        "query": "MATCH (o:Organization) RETURN o.name AS org LIMIT 5",
        "params": {}
    }
    if test_endpoint("POST", "/api/v1/cypher/execute", "Requête Cypher personnalisée", json_data=cypher_query):
        tests_passed += 1
    else:
        tests_failed += 1
    
    # ========================================
    # Test export dashboard
    # ========================================
    print_header("1️⃣3️⃣ Test Export Dashboard")
    
    if test_endpoint("GET", "/api/v1/export/dashboard-data", "Données dashboard"):
        tests_passed += 1
    else:
        tests_failed += 1
    
    # ========================================
    # Résumé
    # ========================================
    print_header("📊 Résumé des Tests")
    
    total = tests_passed + tests_failed
    success_rate = (tests_passed / total * 100) if total > 0 else 0
    
    print(f"   Tests réussis:  {Colors.GREEN}{tests_passed}{Colors.RESET}")
    print(f"   Tests échoués:  {Colors.RED}{tests_failed}{Colors.RESET}")
    print(f"   Total:          {total}")
    print(f"   Taux réussite:  {success_rate:.1f}%")
    
    if tests_failed == 0:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 Tous les tests ont réussi!{Colors.RESET}")
    elif tests_passed == 0:
        print(f"\n{Colors.RED}{Colors.BOLD}❌ Aucun test n'a réussi - Vérifiez que l'API est démarrée{Colors.RESET}")
        print(f"{Colors.YELLOW}   uvicorn safetygraph_api:app --port 8002{Colors.RESET}")
    else:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠️ Certains tests ont échoué{Colors.RESET}")


def demo_cypher_queries():
    """Démonstration de requêtes Cypher via l'API"""
    
    print_header("🔮 Démonstration Requêtes Cypher")
    
    queries = [
        {
            "name": "Top 5 organisations par employés",
            "query": """
                MATCH (o:Organization)
                WHERE o.nb_employes IS NOT NULL
                RETURN o.name AS organisation, o.nb_employes AS employes
                ORDER BY employes DESC
                LIMIT 5
            """
        },
        {
            "name": "Risques critiques par catégorie",
            "query": """
                MATCH (r:RisqueDanger)
                WHERE r.probabilite * r.gravite >= 15
                RETURN r.categorie AS categorie, count(r) AS count
                ORDER BY count DESC
            """
        },
        {
            "name": "Zones avec le plus de risques",
            "query": """
                MATCH (z:Zone)<-[:LOCALISE_DANS]-(r:RisqueDanger)
                RETURN z.name AS zone, z.risk_level AS niveau, count(r) AS nb_risques
                ORDER BY nb_risques DESC
                LIMIT 10
            """
        }
    ]
    
    for q in queries:
        print(f"\n{Colors.BOLD}📌 {q['name']}{Colors.RESET}")
        
        try:
            response = requests.post(
                f"{API_BASE}/api/v1/cypher/execute",
                json={"query": q["query"], "params": {}},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print_success(f"Exécuté en {data['execution_time_ms']}ms - {data['count']} résultats")
                
                for i, row in enumerate(data["data"][:3]):
                    print(f"   {i+1}. {json.dumps(row, ensure_ascii=False)}")
                
                if data["count"] > 3:
                    print(f"   ... et {data['count'] - 3} autres")
            else:
                print_error(f"Erreur: {response.status_code}")
                
        except Exception as e:
            print_error(f"Erreur: {e}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        demo_cypher_queries()
    else:
        run_all_tests()
        print(f"\n{Colors.CYAN}💡 Pour une démo des requêtes Cypher: python test_safetygraph_api.py demo{Colors.RESET}\n")
