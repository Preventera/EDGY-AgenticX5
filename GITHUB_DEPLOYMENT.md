# 📤 Guide: Pousser EDGY-AgenticX5 vers GitHub

## 🎯 Objectif
Ce guide vous montre comment pousser le prototype EDGY-AgenticX5 vers le dépôt GitHub https://github.com/Preventera/EDGY-AgenticX5

## 📋 Prérequis

✅ Git installé localement
✅ Compte GitHub avec accès au repository Preventera/EDGY-AgenticX5
✅ Clé SSH ou token d'accès personnel configuré

## 🚀 Étapes de Déploiement

### 1. Initialiser le Dépôt Local

```bash
cd /chemin/vers/EDGY-AgenticX5

# Initialiser Git (si pas déjà fait)
git init

# Configurer les informations utilisateur
git config user.name "Votre Nom"
git config user.email "votre.email@exemple.com"
```

### 2. Ajouter le Remote GitHub

```bash
# Ajouter le remote (HTTPS)
git remote add origin https://github.com/Preventera/EDGY-AgenticX5.git

# Ou avec SSH (recommandé)
git remote add origin git@github.com:Preventera/EDGY-AgenticX5.git

# Vérifier le remote
git remote -v
```

### 3. Préparer le Commit Initial

```bash
# Vérifier les fichiers à committer
git status

# Ajouter tous les fichiers
git add .

# Créer le commit initial
git commit -m "feat: Initial commit - EDGY-AgenticX5 prototype complet

✨ Features:
- Architecture agentique multi-agent pour SST
- Agent de base avec Claude 4.5 integration
- Agent de monitoring avec détection de risques
- Agent d'orchestration multi-agents
- Système de sécurité et guardrails complet
- Logging structuré et audit trail
- Configuration centralisée
- Tests unitaires et d'intégration
- CI/CD GitHub Actions complet
- Conteneurisation Docker + Docker Compose
- Configuration VS Code optimisée
- Documentation complète

🏗️ Architecture:
- Python 3.10+
- Anthropic Claude API
- PostgreSQL + Redis
- Prometheus + Grafana
- Framework EDGY pour cartographie

📚 Documentation:
- README.md complet
- Guide de démarrage rapide
- Exemples d'utilisation
- API Reference
- Architecture détaillée

🔒 Sécurité:
- Guardrails agents
- Validation humaine
- Chiffrement données sensibles
- Audit trail complet
- RGPD compliant

Developed by: Preventera / GenAISafety
For: Advanced AI-powered OSH management"
```

### 4. Pousser vers GitHub

#### Option A: Premier Push (nouveau dépôt)

```bash
# Créer et pousser la branche main
git branch -M main
git push -u origin main
```

#### Option B: Dépôt Existant (fusionner avec l'existant)

```bash
# Récupérer l'historique existant
git pull origin main --allow-unrelated-histories

# Résoudre les conflits si nécessaire
# Puis pousser
git push -u origin main
```

### 5. Créer les Branches de Développement

```bash
# Créer la branche develop
git checkout -b develop
git push -u origin develop

# Créer d'autres branches si nécessaire
git checkout -b feature/cartography-edgy
git push -u origin feature/cartography-edgy

git checkout -b feature/shacl-validation
git push -u origin feature/shacl-validation
```

### 6. Configurer les Secrets GitHub

Pour que le CI/CD fonctionne, configurez les secrets dans GitHub:

1. Aller sur: https://github.com/Preventera/EDGY-AgenticX5/settings/secrets/actions

2. Ajouter les secrets suivants:
   ```
   ANTHROPIC_API_KEY=votre_clé_anthropic
   DOCKER_USERNAME=votre_username_dockerhub
   DOCKER_PASSWORD=votre_password_dockerhub
   ```

### 7. Configurer les Protections de Branches

1. Aller sur: https://github.com/Preventera/EDGY-AgenticX5/settings/branches

2. Ajouter une règle pour `main`:
   - ✅ Require pull request before merging
   - ✅ Require status checks to pass
   - ✅ Require branches to be up to date
   - ✅ Include administrators

3. Ajouter une règle pour `develop`:
   - ✅ Require pull request before merging
   - ✅ Require status checks to pass

### 8. Créer les Tags de Version

```bash
# Retourner sur main
git checkout main

# Créer le premier tag
git tag -a v0.1.0 -m "Initial release - EDGY-AgenticX5 MVP

Version 0.1.0 - Features:
- Multi-agent architecture
- Monitoring agent
- Orchestrator agent
- Security guardrails
- Complete CI/CD
- Docker deployment
- Full documentation"

# Pousser le tag
git push origin v0.1.0

# Pousser tous les tags
git push origin --tags
```

## 📊 Workflow Git Recommandé

### Développement de Nouvelles Fonctionnalités

```bash
# 1. Partir de develop
git checkout develop
git pull origin develop

# 2. Créer une branche feature
git checkout -b feature/nom-fonctionnalite

# 3. Développer et committer
git add .
git commit -m "feat: Description de la fonctionnalité"

# 4. Pousser la branche
git push -u origin feature/nom-fonctionnalite

# 5. Créer une Pull Request sur GitHub
# develop ← feature/nom-fonctionnalite

# 6. Après review et merge, nettoyer
git checkout develop
git pull origin develop
git branch -d feature/nom-fonctionnalite
```

### Correction de Bugs (Hotfix)

```bash
# 1. Partir de main
git checkout main
git pull origin main

# 2. Créer une branche hotfix
git checkout -b hotfix/nom-bug

# 3. Corriger et committer
git add .
git commit -m "fix: Correction du bug"

# 4. Pousser et créer PR vers main
git push -u origin hotfix/nom-bug

# 5. Après merge dans main, merger aussi dans develop
```

### Release vers Production

```bash
# 1. Partir de develop
git checkout develop
git pull origin develop

# 2. Créer une branche release
git checkout -b release/v0.2.0

# 3. Finaliser (bump version, changelog, etc.)
git add .
git commit -m "chore: Prepare release v0.2.0"

# 4. Merger dans main
git checkout main
git merge --no-ff release/v0.2.0

# 5. Créer le tag
git tag -a v0.2.0 -m "Release v0.2.0"

# 6. Merger dans develop
git checkout develop
git merge --no-ff release/v0.2.0

# 7. Pousser tout
git push origin main develop --tags

# 8. Supprimer la branche release
git branch -d release/v0.2.0
```

## 🔍 Vérifications Post-Déploiement

### Sur GitHub

✅ Repository visible: https://github.com/Preventera/EDGY-AgenticX5
✅ README.md s'affiche correctement
✅ Actions CI/CD lancées automatiquement
✅ Secrets configurés
✅ Protections de branches actives
✅ Tags visibles dans Releases

### Tests CI/CD

```bash
# 1. Créer un petit changement
echo "# Test" >> README.md
git add README.md
git commit -m "test: CI/CD trigger"
git push origin main

# 2. Vérifier sur GitHub Actions
# https://github.com/Preventera/EDGY-AgenticX5/actions

# 3. Si tout est vert ✅, CI/CD fonctionne!
```

## 📝 Conventions de Commit

Utiliser le format Conventional Commits:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types**:
- `feat`: Nouvelle fonctionnalité
- `fix`: Correction de bug
- `docs`: Documentation
- `style`: Formatage (sans changement de code)
- `refactor`: Refactoring
- `test`: Ajout/modification de tests
- `chore`: Tâches de maintenance
- `perf`: Amélioration de performance
- `ci`: Changements CI/CD

**Exemples**:
```bash
git commit -m "feat(agents): add decision agent for risk assessment"
git commit -m "fix(monitoring): resolve memory leak in alert generation"
git commit -m "docs(readme): add installation instructions"
git commit -m "test(orchestrator): add integration tests for workflow"
git commit -m "chore(deps): update anthropic to v0.41.0"
```

## 🚨 Dépannage

### Problème: "Permission denied"

```bash
# Vérifier la configuration SSH
ssh -T git@github.com

# Si problème, reconfigurer SSH key
ssh-keygen -t ed25519 -C "votre.email@exemple.com"
cat ~/.ssh/id_ed25519.pub
# Ajouter la clé publique sur GitHub
```

### Problème: "Rejected - non-fast-forward"

```bash
# Récupérer les changements distants
git pull origin main --rebase

# Résoudre les conflits si nécessaire
# Puis pousser
git push origin main
```

### Problème: "Large files"

Si fichiers trop gros (>100MB):

```bash
# Installer Git LFS
git lfs install

# Tracker les gros fichiers
git lfs track "*.bin"
git lfs track "*.model"

# Committer
git add .gitattributes
git commit -m "chore: add Git LFS for large files"
```

## 🎉 Succès!

Si tout est configuré correctement, vous devriez voir:

1. ✅ Code sur GitHub
2. ✅ CI/CD qui tourne (badge vert)
3. ✅ README.md bien formaté
4. ✅ Structure de branches propre
5. ✅ Tags de version

Le projet EDGY-AgenticX5 est maintenant prêt pour le développement collaboratif! 🚀

---

**Prochaines étapes**:
1. Inviter les collaborateurs
2. Configurer les notifications
3. Créer le premier milestone
4. Planifier les features suivantes

**Ressources**:
- GitHub Docs: https://docs.github.com
- Git Flow: https://nvie.com/posts/a-successful-git-branching-model/
- Conventional Commits: https://www.conventionalcommits.org/
