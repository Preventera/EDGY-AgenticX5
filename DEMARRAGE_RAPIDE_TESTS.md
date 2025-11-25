# ⚡ DÉMARRAGE RAPIDE - Tests EDGY-AgenticX5

**Temps requis:** 5 minutes  
**Prérequis:** Python, pip

---

## 🚀 EN 3 ÉTAPES

### **ÉTAPE 1 : Installation** (2 min)

```powershell
# Ouvrir PowerShell dans le dossier du projet
cd C:\Users\Mario\Documents\PROJECTS_NEW\EDGY-AGENTIC\EDGY-AgenticX5

# Installer pytest
pip install pytest pytest-cov pytest-mock --break-system-packages
```

### **ÉTAPE 2 : Copier les fichiers** (1 min)

Télécharger depuis outputs et copier :
- `pytest.ini` → racine du projet
- `run_tests.ps1` → racine du projet
- `tests/` (dossier complet) → racine du projet

Structure finale :
```
EDGY-AgenticX5/
├── pytest.ini              ← Nouveau
├── run_tests.ps1           ← Nouveau
├── tests/                  ← Nouveau (dossier)
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_cartography_api.py
│   ├── test_neo4j_mapper.py
│   └── README.md
└── src/
    └── edgy_core/
```

### **ÉTAPE 3 : Exécuter** (2 min)

```powershell
# Lancer tous les tests
.\run_tests.ps1
```

---

## ✅ RÉSULTAT ATTENDU

```
🧪 Tests EDGY-AgenticX5
========================

📋 Exécution de TOUS les tests...

🚀 Commande: python -m pytest tests/ -v

======================== test session starts =========================
collected 38 items

tests/test_cartography_api.py::TestOrganizationAPI::test_create_organization PASSED
tests/test_cartography_api.py::TestOrganizationAPI::test_get_organization PASSED
...
tests/test_neo4j_mapper.py::TestBatchOperations::test_sync_all_entities PASSED

========================= 38 passed in 2.54s =========================

========================
✅ TOUS LES TESTS ONT RÉUSSI!
⏱️ Durée: 2.54s
```

---

## 🎯 COMMANDES UTILES

```powershell
# Tous les tests (par défaut)
.\run_tests.ps1

# Tests unitaires rapides uniquement
.\run_tests.ps1 -Mode unit

# Tests API Cartographie uniquement
pytest tests/test_cartography_api.py -v

# Tests Neo4j Mapper uniquement
pytest tests/test_neo4j_mapper.py -v

# Avec couverture de code
.\run_tests.ps1 -Mode coverage

# Avec rapport HTML
.\run_tests.ps1 -Mode coverage -Html

# Mode verbeux (debug)
.\run_tests.ps1 -Verbose
```

---

## 🐛 DÉPANNAGE

### Erreur : "pytest n'est pas reconnu"
```powershell
# Solution : Installer pytest
pip install pytest pytest-cov pytest-mock --break-system-packages
```

### Erreur : "ModuleNotFoundError: No module named 'edgy_core'"
```powershell
# Solution : Vérifier que vous êtes dans le bon dossier
cd C:\Users\Mario\Documents\PROJECTS_NEW\EDGY-AGENTIC\EDGY-AgenticX5
```

### Erreur : "cannot import name 'EDGYCartographyStore'"
```powershell
# Solution : Vérifier que les fichiers src/edgy_core/ existent
dir src\edgy_core\api\cartography_api.py
dir src\edgy_core\transformers\neo4j_mapper.py
```

### Tests échouent
1. Vérifier que tous les fichiers sont bien copiés
2. Vérifier que le code source est à jour (git pull)
3. Nettoyer le cache Python : `Remove-Item -Path src\__pycache__ -Recurse -Force`

---

## 📊 PROCHAINES ÉTAPES

Après avoir exécuté les tests avec succès :

1. ✅ **Corriger le bug Relations Neo4j** (les tests vont aider à le détecter)
2. ✅ **Ajouter tests pour nouvelles fonctionnalités**
3. ✅ **Intégrer dans CI/CD GitHub Actions**

---

## 🎊 SUCCÈS !

Si vous voyez `✅ TOUS LES TESTS ONT RÉUSSI!`, félicitations ! 🎉

Vous avez maintenant une base solide de tests automatisés pour :
- Valider le code existant (~3,814 lignes)
- Détecter les régressions
- Développer en confiance

---

**Besoin d'aide ?** Consultez `tests/README.md` pour la documentation complète.
