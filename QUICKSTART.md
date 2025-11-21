# 🚀 Guide de Démarrage Rapide - EDGY-AgenticX5

## Installation et Premier Lancement en 5 Minutes

### 1. Cloner et Configurer

```bash
# Cloner le dépôt
git clone https://github.com/Preventera/EDGY-AgenticX5.git
cd EDGY-AgenticX5

# Copier le fichier d'environnement
cp .env.example .env

# Éditer .env et ajouter votre clé API Anthropic
# ANTHROPIC_API_KEY=votre_clé_ici
```

### 2. Installation avec Python

```bash
# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou venv\Scripts\activate  # Windows

# Installer les dépendances
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 3. Premier Test

```bash
# Exécuter l'exemple complet
python examples/complete_usage.py
```

### 4. Installation avec Docker (Recommandé pour Production)

```bash
# Construire et lancer toute la stack
docker-compose up -d

# Vérifier les logs
docker-compose logs -f app

# Accéder aux services
# - Application: http://localhost:8000
# - Grafana: http://localhost:3000 (admin/admin)
# - Prometheus: http://localhost:9090
```

## 🧪 Tester les Composants Individuellement

### Agent de Monitoring

```python
from src.agents.monitoring_agent import MonitoringAgent
import asyncio

async def test_monitoring():
    agent = MonitoringAgent(
        agent_id="test_monitor",
        name="Test Monitor"
    )
    
    # Données de test
    data = {
        "site": "Site A",
        "sensors": {
            "temperature": 28.5,
            "humidity": 55
        }
    }
    
    result = await agent.process(data)
    print(f"Risques détectés: {result['risks_detected']}")

# Exécuter
asyncio.run(test_monitoring())
```

### Agent d'Orchestration

```python
from src.agents.orchestrator_agent import OrchestratorAgent
from src.agents.monitoring_agent import MonitoringAgent
import asyncio

async def test_orchestration():
    # Créer l'orchestrateur
    orchestrator = OrchestratorAgent()
    
    # Créer et enregistrer un agent
    monitor = MonitoringAgent(agent_id="monitor_01")
    orchestrator.register_agent("monitor_01", monitor)
    
    # Créer un workflow
    request = {
        "description": "Analyser les risques du site",
        "context": {"site": "Site A"}
    }
    
    result = await orchestrator.process(request)
    print(f"Workflow complété: {result['workflow_id']}")

asyncio.run(test_orchestration())
```

## 📊 Visualiser les Métriques

Après le lancement avec Docker Compose:

1. **Grafana** - http://localhost:3000
   - Connexion: admin/admin
   - Dashboards préconfigurés pour les agents

2. **Prometheus** - http://localhost:9090
   - Métriques en temps réel
   - Requêtes PromQL

## 🧪 Exécuter les Tests

```bash
# Tous les tests
pytest tests/ -v --cov=src

# Tests unitaires uniquement
pytest tests/unit/ -v

# Tests avec couverture HTML
pytest tests/ --cov=src --cov-report=html
open htmlcov/index.html
```

## 🛠️ Développement avec VS Code

1. Ouvrir le projet dans VS Code
   ```bash
   code .
   ```

2. Installer les extensions recommandées
   - VS Code proposera automatiquement les extensions

3. Utiliser les configurations de debug
   - Appuyer sur F5 pour déboguer
   - Configurations disponibles dans `.vscode/launch.json`

4. Exécuter les tâches
   - `Ctrl+Shift+B` (ou `Cmd+Shift+B` sur Mac)
   - Choisir une tâche (tests, linting, etc.)

## 🔐 Configuration de Sécurité

### Clé API Anthropic

```bash
# Dans .env
ANTHROPIC_API_KEY=your_key_here

# Ou via variable d'environnement
export ANTHROPIC_API_KEY=your_key_here
```

### Autres Configurations

```bash
# Niveau de log
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR

# Environnement
EDGY_ENV=development  # development, staging, production

# Sécurité
ENABLE_SECURITY_GUARDRAILS=True
REQUIRE_HUMAN_VALIDATION_CRITICAL=True
```

## 📚 Ressources Supplémentaires

- **Documentation Complète**: [docs/](docs/)
- **Exemples**: [examples/](examples/)
- **API Reference**: [docs/api/](docs/api/)
- **Architecture**: [docs/architecture/](docs/architecture/)

## 🆘 Dépannage Rapide

### Problème: "ANTHROPIC_API_KEY non défini"
```bash
# Vérifier que la clé est dans .env
cat .env | grep ANTHROPIC_API_KEY

# Ou définir temporairement
export ANTHROPIC_API_KEY=votre_clé
```

### Problème: "Module not found"
```bash
# Réinstaller les dépendances
pip install -r requirements.txt --force-reinstall
```

### Problème: "Permission denied"
```bash
# Donner les permissions d'exécution
chmod +x scripts/*.sh
```

### Problème: Docker ne démarre pas
```bash
# Vérifier Docker
docker --version
docker-compose --version

# Reconstruire les images
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## ✅ Checklist de Démarrage

- [ ] Dépôt cloné
- [ ] `.env` configuré avec ANTHROPIC_API_KEY
- [ ] Dépendances Python installées
- [ ] Tests passent (`pytest`)
- [ ] Exemple exécuté avec succès
- [ ] Docker fonctionne (optionnel)
- [ ] VS Code configuré (optionnel)

## 🎯 Prochaines Étapes

1. Lire la [documentation architecture](docs/architecture/README.md)
2. Explorer les [cas d'usage](docs/use_cases/)
3. Contribuer au projet (voir [CONTRIBUTING.md](CONTRIBUTING.md))
4. Rejoindre la communauté Discord

## 💡 Conseil Pro

Utilisez le mode développement pour voir les logs détaillés:

```bash
# .env
EDGY_ENV=development
LOG_LEVEL=DEBUG
DEBUG=True

# Puis relancer
python examples/complete_usage.py
```

---

**Besoin d'aide?** Ouvrez une issue sur GitHub ou contactez support@preventera.com
