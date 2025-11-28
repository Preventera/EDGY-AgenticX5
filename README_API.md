# 🛡️ SafetyGraph API

API REST FastAPI pour requêtes Cypher sur le graphe de connaissances SafetyGraph.

## 📋 Description

SafetyGraph API expose 50+ endpoints pour interroger le graphe Neo4j contenant les données SST du Québec :
- 460 Organisations (16 secteurs SCIAN)
- 3,926 Personnes
- 2,870 Risques
- 1,429 Zones

## 🚀 Démarrage rapide

### Prérequis

```bash
pip install fastapi uvicorn neo4j pydantic
```

### Configuration

Variables d'environnement (optionnelles) :

```bash
export NEO4J_URI="bolt://localhost:7687"
export NEO4J_USER="neo4j"
export NEO4J_PASSWORD="votre_mot_de_passe"
```

### Démarrage

```bash
# Démarrage standard
uvicorn safetygraph_api:app --host 0.0.0.0 --port 8002

# Avec rechargement automatique (développement)
uvicorn safetygraph_api:app --port 8002 --reload
```

### Documentation

- **Swagger UI**: http://localhost:8002/docs
- **ReDoc**: http://localhost:8002/redoc
- **OpenAPI JSON**: http://localhost:8002/openapi.json

## 📊 Endpoints disponibles

### Santé
| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/` | Page d'accueil |
| GET | `/health` | Health check avec état Neo4j |

### Statistiques
| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/v1/stats` | Statistiques globales du graphe |
| GET | `/api/v1/stats/kpis` | KPIs calculés pour dashboard |

### Secteurs SCIAN
| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/v1/sectors` | Liste tous les secteurs |
| GET | `/api/v1/sectors/{scian}` | Détail d'un secteur |
| GET | `/api/v1/sectors/priority/cnesst` | 5 secteurs prioritaires CNESST |

### Risques
| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/v1/risks` | Liste des risques (paramètres: limit, min_score) |
| GET | `/api/v1/risks/tolerance-zero` | Risques TZ (score ≥ 15) |
| GET | `/api/v1/risks/categories` | Risques par catégorie |
| GET | `/api/v1/risks/matrix` | Données matrice P×G |

### Zones
| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/v1/zones` | Liste des zones (paramètre: risk_level) |
| GET | `/api/v1/zones/hotspots` | Zones à concentration élevée |
| GET | `/api/v1/zones/by-level` | Distribution par niveau |

### Personnes
| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/v1/persons/age-distribution` | Distribution par âge |
| GET | `/api/v1/persons/certifications` | Certifications SST fréquentes |
| GET | `/api/v1/persons/exposed` | Personnes les plus exposées |

### Alertes
| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/v1/alerts` | Toutes les alertes actives |
| GET | `/api/v1/alerts/young-workers` | Alertes jeunes travailleurs |

### Conformité
| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/v1/compliance/certification-coverage` | Taux certification par secteur |
| GET | `/api/v1/compliance/missing-epi` | Zones sans EPI définis |

### Analyses Prédictives
| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/v1/predictive/features` | Features pour ML (XGBoost) |
| GET | `/api/v1/predictive/risk-score-by-org` | Scores par organisation |
| GET | `/api/v1/predictive/sector-correlation` | Corrélation secteur-risque |

### Agents IA
| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/v1/agents/visionai/targets` | Cibles surveillance caméra |
| GET | `/api/v1/agents/ergoai/targets` | Cibles risques ergonomiques |
| GET | `/api/v1/agents/alertai/triggers` | Déclencheurs d'alertes |
| GET | `/api/v1/agents/complyai/gaps` | Écarts de conformité |

### Recherche
| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/v1/search/organizations?q=` | Recherche organisations |
| GET | `/api/v1/search/risks?q=` | Recherche risques |

### Cypher personnalisé
| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/api/v1/cypher/execute` | Exécuter requête Cypher |

### Export
| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/v1/export/dashboard-data` | Données complètes dashboard |

## 💻 Exemples d'utilisation

### Python (requests)

```python
import requests

# Statistiques globales
response = requests.get("http://localhost:8002/api/v1/stats")
print(response.json())

# Risques Tolérance Zéro
response = requests.get("http://localhost:8002/api/v1/risks/tolerance-zero")
print(response.json())

# Requête Cypher personnalisée
response = requests.post(
    "http://localhost:8002/api/v1/cypher/execute",
    json={
        "query": "MATCH (o:Organization) RETURN o.name LIMIT 10",
        "params": {}
    }
)
print(response.json())
```

### cURL

```bash
# Health check
curl http://localhost:8002/health

# Liste des secteurs
curl http://localhost:8002/api/v1/sectors

# Recherche
curl "http://localhost:8002/api/v1/search/organizations?q=CGI"

# Requête Cypher
curl -X POST http://localhost:8002/api/v1/cypher/execute \
  -H "Content-Type: application/json" \
  -d '{"query": "MATCH (r:RisqueDanger) RETURN count(r) AS total"}'
```

### JavaScript (fetch)

```javascript
// Statistiques
fetch('http://localhost:8002/api/v1/stats')
  .then(res => res.json())
  .then(data => console.log(data));

// Alertes
fetch('http://localhost:8002/api/v1/alerts')
  .then(res => res.json())
  .then(data => console.log(data));
```

## 🧪 Tests

```bash
# Exécuter tous les tests
python test_safetygraph_api.py

# Démonstration requêtes Cypher
python test_safetygraph_api.py demo
```

## 🔒 Sécurité

- Seules les requêtes en lecture (MATCH) sont autorisées via `/api/v1/cypher/execute`
- Les opérations d'écriture (CREATE, DELETE, SET, etc.) sont bloquées
- CORS configuré pour autoriser toutes les origines (à restreindre en production)

## 📁 Structure des fichiers

```
├── safetygraph_api.py          # API FastAPI principale
├── test_safetygraph_api.py     # Script de tests
├── SST_100_requetes.cypher     # 100 requêtes Cypher documentées
└── README_API.md               # Cette documentation
```

## 🔗 Liens

- [Documentation Neo4j Cypher](https://neo4j.com/docs/cypher-manual/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [GitHub EDGY-AgenticX5](https://github.com/Preventera/EDGY-AgenticX5)

## 📄 Licence

EDGY-AgenticX5 | Preventera | GenAISafety

---

*SafetyGraph API - Analyses prédictives SST pour le Québec* 🛡️
