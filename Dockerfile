# EDGY-AgenticX5 Dockerfile
# Multi-stage build pour optimiser la taille de l'image

# ===== Stage 1: Builder =====
FROM python:3.10-slim as builder

# Variables d'environnement Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Installation des dépendances système
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    make \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copier les fichiers requirements
WORKDIR /build
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --user -r requirements.txt

# ===== Stage 2: Runtime =====
FROM python:3.10-slim

# Variables d'environnement
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH=/home/appuser/.local/bin:$PATH \
    EDGY_ENV=production

# Installer uniquement les dépendances runtime nécessaires
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Créer utilisateur non-root
RUN useradd -m -u 1000 -s /bin/bash appuser

# Copier les dépendances Python du builder
COPY --from=builder --chown=appuser:appuser /root/.local /home/appuser/.local

# Définir le répertoire de travail
WORKDIR /app

# Copier le code source
COPY --chown=appuser:appuser . .

# Créer les répertoires nécessaires
RUN mkdir -p logs data configs && \
    chown -R appuser:appuser logs data configs

# Changer vers l'utilisateur non-root
USER appuser

# Port exposé (pour API/dashboard)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Commande par défaut
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
