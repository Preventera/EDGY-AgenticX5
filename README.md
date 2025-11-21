# EDGY-AgenticX5

## Architecture Agentique Multi-Agent pour la Santé et Sécurité au Travail (SST)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

## 🎯 Vision

EDGY-AgenticX5 est un système agentique avancé qui combine la puissance de la cartographie organisationnelle **EDGY** avec une architecture **multi-agent autonome** basée sur **Claude 4.5** pour révolutionner la gestion de la SST.

### Caractéristiques Principales

- 🗺️ **Cartographie EDGY** : Alignement identité-expérience-opérations
- 🤖 **Agents Autonomes** : Intelligence distribuée avec supervision humaine
- 🔒 **Conformité SHACL** : Validation des règles métier et gouvernance
- 📊 **Monitoring Temps Réel** : Détection proactive des risques
- 🔄 **Orchestration Multi-Agent** : Coordination intelligente des workflows
- 🛡️ **Sécurité et RGPD** : Protection des données sensibles

## 🏗️ Architecture

```
EDGY-AgenticX5/
├── src/
│   ├── agents/              # Agents autonomes Claude 4.5
│   │   ├── decision_agent.py      # Agent de décision SST
│   │   ├── monitoring_agent.py    # Agent de surveillance
│   │   ├── orchestrator_agent.py  # Orchestrateur multi-agents
│   │   └── base_agent.py          # Classe de base
│   ├── cartography/         # Modules cartographie EDGY
│   │   ├── edgy_mapper.py         # Générateur de cartes EDGY
│   │   ├── edgy_schema.py         # Schémas et ontologies
│   │   └── visualizer.py          # Visualisation interactive
│   ├── orchestration/       # Orchestration et coordination
│   │   ├── workflow_engine.py     # Moteur de workflows
│   │   ├── message_bus.py         # Bus de messages inter-agents
│   │   └── context_manager.py     # Gestion mémoire contextuelle
│   ├── shacl/              # Règles de gouvernance
│   │   ├── rules_engine.py        # Moteur de règles SHACL
│   │   ├── validator.py           # Validateur sémantique
│   │   └── compliance_checker.py  # Vérification conformité
│   └── utils/              # Utilitaires communs
│       ├── logger.py              # Logging centralisé
│       ├── config.py              # Configuration système
│       └── security.py            # Sécurité et guardrails
├── tests/                  # Tests automatisés
│   ├── unit/                      # Tests unitaires
│   └── integration/               # Tests d'intégration
├── configs/                # Configurations
│   ├── agents/                    # Config agents
│   ├── ci/                        # CI/CD pipelines
│   └── shacl/                     # Règles SHACL
├── docs/                   # Documentation
│   ├── architecture/              # Architecture technique
│   ├── guides/                    # Guides utilisateur
│   └── api/                       # Documentation API
└── .vscode/                # Configuration VS Code
```

## 🚀 Installation Rapide

### Prérequis

- Python 3.10+
- Node.js 18+ (pour outils de visualisation)
- Git
- Visual Studio Code (recommandé)

### Configuration Locale

```bash
# Cloner le dépôt
git clone https://github.com/Preventera/EDGY-AgenticX5.git
cd EDGY-AgenticX5

# Créer environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou venv\Scripts\activate  # Windows

# Installer dépendances
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Configuration VS Code
code .
```

### Configuration API Claude

Créer un fichier `.env` à la racine :

```env
ANTHROPIC_API_KEY=your_api_key_here
EDGY_ENV=development
LOG_LEVEL=INFO
```

## 📚 Démarrage Rapide

### 1. Cartographie EDGY de Base

```python
from src.cartography.edgy_mapper import EDGYMapper

# Initialiser le mapper
mapper = EDGYMapper()

# Créer cartographie organisation
organization_map = mapper.create_organizational_map(
    organization_name="MonEntreprise SST",
    domains=["Production", "Maintenance", "Qualité"],
    processes=["Inspection", "Formation", "Audit"]
)

# Visualiser
mapper.visualize(organization_map, output="map.html")
```

### 2. Déployer un Agent de Monitoring

```python
from src.agents.monitoring_agent import MonitoringAgent

# Initialiser l'agent
agent = MonitoringAgent(
    name="SST_Monitor_01",
    config_path="configs/agents/monitoring.yaml"
)

# Lancer surveillance
agent.start_monitoring(
    data_sources=["sensor_network", "incident_reports"],
    alert_threshold="critical"
)
```

### 3. Orchestration Multi-Agent

```python
from src.orchestration.workflow_engine import WorkflowEngine

# Créer pipeline agentique
engine = WorkflowEngine()

# Définir workflow
workflow = engine.create_workflow(
    name="Risk_Detection_Pipeline",
    agents=["monitoring", "analysis", "decision"],
    human_validation_points=["critical_decisions"]
)

# Exécuter
results = engine.execute(workflow, context={"site": "usine_A"})
```

## 🧪 Tests

### Exécuter tous les tests

```bash
# Tests unitaires
pytest tests/unit/ -v --cov=src

# Tests d'intégration
pytest tests/integration/ -v

# Tests end-to-end
pytest tests/e2e/ -v --slow
```

### Validation SHACL

```bash
# Valider règles de gouvernance
python -m src.shacl.validator --config configs/shacl/rules.ttl --data data/sample.ttl
```

## 🔧 Développement

### Configuration VS Code

Le projet inclut des configurations VS Code optimisées :

- **Débogage** : `.vscode/launch.json`
- **Tâches** : `.vscode/tasks.json`
- **Extensions recommandées** : `.vscode/extensions.json`

### Workflow Git

```bash
# Créer une branche feature
git checkout -b feature/nom-fonctionnalite

# Commit avec convention
git commit -m "feat(agents): ajout agent de prédiction risques"

# Push et créer PR
git push origin feature/nom-fonctionnalite
```

### CI/CD

Le projet utilise GitHub Actions pour :

- ✅ Tests automatiques sur PR
- 🔍 Analyse de code (pylint, mypy)
- 📦 Build et packaging
- 🚀 Déploiement automatique (staging/prod)

## 📊 Monitoring et Métriques

### KPIs Principaux

- **Taux de détection proactive** : >90%
- **Temps de réponse incidents** : <2 min
- **Précision des agents** : >95%
- **Disponibilité système** : 99.9%

### Dashboard

Accéder au dashboard de monitoring :

```bash
# Lancer dashboard
python -m src.utils.dashboard --port 8080
```

Ouvrir : http://localhost:8080

## 🔒 Sécurité et Conformité

### Guardrails Agents

- ✅ Validation humaine sur décisions critiques
- ✅ Kill switch automatique sur anomalies
- ✅ Traçabilité complète des actions
- ✅ Chiffrement données sensibles (AES-256)
- ✅ Conformité RGPD

### Audit Trail

Tous les événements sont logués dans :
- `logs/agents/` : Actions agents
- `logs/security/` : Événements sécurité
- `logs/audit/` : Piste d'audit

## 🤝 Contribution

Nous accueillons les contributions ! Voir [CONTRIBUTING.md](CONTRIBUTING.md).

### Processus de Contribution

1. Fork le projet
2. Créer une branche (`git checkout -b feature/AmazingFeature`)
3. Commit changements (`git commit -m 'feat: Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📖 Documentation Complète

- [Architecture Technique](docs/architecture/README.md)
- [Guide Développeur](docs/guides/developer_guide.md)
- [Guide Déploiement](docs/guides/deployment_guide.md)
- [API Reference](docs/api/README.md)
- [Cas d'Usage](docs/use_cases/README.md)

## 🗺️ Roadmap

### Phase 1 - MVP (Q1 2025) ✅
- [x] Architecture de base
- [x] Agent de monitoring
- [x] Cartographie EDGY
- [x] Tests unitaires

### Phase 2 - Production (Q2 2025)
- [ ] Orchestration avancée
- [ ] Dashboard temps réel
- [ ] Intégration SGSST
- [ ] Tests à grande échelle

### Phase 3 - Évolution (Q3-Q4 2025)
- [ ] Agents spécialisés sectoriels
- [ ] Auto-apprentissage continu
- [ ] Intégration IoT/sensors
- [ ] Multi-site management

## 💼 Cas d'Usage

### 1. PME Manufacturière
Déploiement rapide sur site unique avec 50-200 employés.

### 2. Grande Entreprise Multi-Sites
Orchestration centralisée avec agents distribués.

### 3. Secteur Construction
Agents mobiles pour chantiers temporaires.

## 🏆 Équipe

**Preventera** - Innovation SST & IA
**GenAISafety** - Plateforme technologique

## 📄 Licence

Ce projet est sous licence MIT - voir [LICENSE](LICENSE).

## 📞 Support

- 📧 Email : support@preventera.com
- 💬 Discord : [EDGY-AgenticX5 Community](https://discord.gg/edgy-agentic)
- 📚 Documentation : https://docs.edgy-agentic.com
- 🐛 Issues : https://github.com/Preventera/EDGY-AgenticX5/issues

## 🙏 Remerciements

Projet développé avec le soutien de :
- Anthropic (Claude 4.5 API)
- Enterprise Design (EDGY Framework)
- Communauté SST open-source

---

**Fait avec ❤️ pour une SST intelligente et proactive**
