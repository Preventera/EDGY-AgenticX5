#!/usr/bin/env python3
"""
Dashboard Streamlit - EDGY-AgenticX5
Interface de monitoring temps réel pour le système de prévention SST

Fonctionnalités:
- Monitoring des zones en temps réel
- Visualisation des alertes et risques
- Statistiques Neo4j
- Simulation d'événements
- État des agents
"""

import streamlit as st
import requests
import json
from datetime import datetime, timedelta
import time

# Configuration de la page
st.set_page_config(
    page_title="EDGY-AgenticX5 | Dashboard SST",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# CONFIGURATION
# ============================================

API_BASE_URL = "http://localhost:8000"

# ============================================
# STYLES CSS
# ============================================

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E3A8A;
        text-align: center;
        padding: 1rem;
        background: linear-gradient(90deg, #EFF6FF 0%, #DBEAFE 100%);
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E3A8A;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #6B7280;
        margin-top: 0.5rem;
    }
    
    .alert-critical {
        background: #FEE2E2;
        border-left: 4px solid #DC2626;
        padding: 1rem;
        border-radius: 5px;
        margin: 0.5rem 0;
    }
    
    .alert-high {
        background: #FEF3C7;
        border-left: 4px solid #F59E0B;
        padding: 1rem;
        border-radius: 5px;
        margin: 0.5rem 0;
    }
    
    .alert-medium {
        background: #E0F2FE;
        border-left: 4px solid #0EA5E9;
        padding: 1rem;
        border-radius: 5px;
        margin: 0.5rem 0;
    }
    
    .agent-card {
        background: #F0FDF4;
        border: 1px solid #86EFAC;
        padding: 0.8rem;
        border-radius: 8px;
        margin: 0.3rem 0;
    }
    
    .agent-card-inactive {
        background: #FEF2F2;
        border: 1px solid #FECACA;
        padding: 0.8rem;
        border-radius: 8px;
        margin: 0.3rem 0;
    }
    
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    
    .status-healthy {
        background: #D1FAE5;
        color: #065F46;
    }
    
    .status-warning {
        background: #FEF3C7;
        color: #92400E;
    }
    
    .status-error {
        background: #FEE2E2;
        color: #991B1B;
    }
    
    .zone-card {
        background: white;
        border: 1px solid #E5E7EB;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        transition: all 0.3s ease;
    }
    
    .zone-card:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        transform: translateY(-2px);
    }
    
    .risk-critical { color: #DC2626; font-weight: bold; }
    .risk-high { color: #F59E0B; font-weight: bold; }
    .risk-medium { color: #0EA5E9; }
    .risk-low { color: #10B981; }
</style>
""", unsafe_allow_html=True)

# ============================================
# FONCTIONS UTILITAIRES
# ============================================

def api_call(endpoint: str, method: str = "GET", data: dict = None) -> dict:
    """Appel API avec gestion d'erreurs"""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        if method == "GET":
            response = requests.get(url, timeout=5)
        else:
            response = requests.post(url, json=data, timeout=10)
        
        if response.status_code == 200:
            return {"success": True, "data": response.json()}
        else:
            return {"success": False, "error": f"HTTP {response.status_code}"}
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "API non disponible"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_risk_color(niveau: str) -> str:
    """Retourne la classe CSS pour le niveau de risque"""
    mapping = {
        "critical": "risk-critical",
        "critique": "risk-critical",
        "TRÈS ÉLEVÉ": "risk-critical",
        "high": "risk-high",
        "élevé": "risk-high",
        "ÉLEVÉ": "risk-high",
        "medium": "risk-medium",
        "moyen": "risk-medium",
        "MOYEN": "risk-medium",
        "low": "risk-low",
        "faible": "risk-low",
        "FAIBLE": "risk-low"
    }
    return mapping.get(niveau, "risk-medium")


def get_risk_emoji(niveau: str) -> str:
    """Retourne l'emoji pour le niveau de risque"""
    mapping = {
        "critical": "🔴",
        "critique": "🔴",
        "TRÈS ÉLEVÉ": "🔴",
        "high": "🟠",
        "élevé": "🟠",
        "ÉLEVÉ": "🟠",
        "medium": "🟡",
        "moyen": "🟡",
        "MOYEN": "🟡",
        "low": "🟢",
        "faible": "🟢",
        "FAIBLE": "🟢",
        "minimal": "⚪"
    }
    return mapping.get(niveau, "🟡")

# ============================================
# SIDEBAR
# ============================================

with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/safety-hat.png", width=80)
    st.title("🛡️ EDGY-AgenticX5")
    st.caption("Système de Prévention SST Multi-Agents")
    
    st.divider()
    
    # Navigation
    page = st.radio(
        "📍 Navigation",
        ["🏠 Accueil", "📊 Monitoring", "🚨 Alertes", "🤖 Agents", "⚙️ Simulation"],
        label_visibility="collapsed"
    )
    
    st.divider()
    
    # Status API
    st.subheader("📡 Status Système")
    health = api_call("/health")
    
    if health["success"]:
        data = health["data"]
        st.success("✅ API Connectée")
        
        col1, col2 = st.columns(2)
        with col1:
            neo4j_status = "✅" if data.get("components", {}).get("neo4j") else "❌"
            st.metric("Neo4j", neo4j_status)
        with col2:
            orch_status = "✅" if data.get("components", {}).get("orchestrator") else "❌"
            st.metric("Orchestrator", orch_status)
        
        if "neo4j_stats" in data:
            st.caption(f"📊 {data['neo4j_stats'].get('nodes', 0)} nœuds | {data['neo4j_stats'].get('relationships', 0)} relations")
    else:
        st.error(f"❌ {health['error']}")
        st.info("💡 Lancez l'API: `python api.py`")
    
    st.divider()
    st.caption(f"🕐 {datetime.now().strftime('%H:%M:%S')}")
    st.caption("v1.0.0 | Sprint 2")

# ============================================
# PAGE: ACCUEIL
# ============================================

if page == "🏠 Accueil":
    st.markdown('<div class="main-header">🛡️ EDGY-AgenticX5 Dashboard</div>', unsafe_allow_html=True)
    st.markdown("### Système Intelligent de Prévention SST Multi-Agents")
    
    # Métriques principales
    col1, col2, col3, col4 = st.columns(4)
    
    health = api_call("/health")
    stats = api_call("/api/v1/stats")
    zones = api_call("/api/v1/zones")
    
    with col1:
        if health["success"]:
            nodes = health["data"].get("neo4j_stats", {}).get("nodes", 0)
            st.metric("📊 Nœuds Neo4j", f"{nodes:,}")
        else:
            st.metric("📊 Nœuds Neo4j", "N/A")
    
    with col2:
        if health["success"]:
            rels = health["data"].get("neo4j_stats", {}).get("relationships", 0)
            st.metric("🔗 Relations", f"{rels:,}")
        else:
            st.metric("🔗 Relations", "N/A")
    
    with col3:
        if zones["success"]:
            st.metric("🏭 Zones Actives", len(zones["data"]))
        else:
            st.metric("🏭 Zones Actives", "N/A")
    
    with col4:
        st.metric("🤖 Agents Actifs", "13")
    
    st.divider()
    
    # Vue d'ensemble
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.subheader("📈 Vue d'Ensemble du Système")
        
        # Architecture
        st.markdown("""
        ```
        ┌─────────────────────────────────────────────────────────────┐
        │                    EDGY-AgenticX5                           │
        ├─────────────────────────────────────────────────────────────┤
        │  📡 Capteurs IoT  →  🤖 13 Agents  →  📊 Neo4j SafetyGraph │
        │                           ↓                                 │
        │  🔄 LangGraph Orchestration  →  🚨 Alertes Temps Réel      │
        │                           ↓                                 │
        │  📋 Recommandations SST  →  👷 Superviseurs Terrain        │
        └─────────────────────────────────────────────────────────────┘
        ```
        """)
        
        # Agents par catégorie
        st.markdown("#### 🤖 Architecture Multi-Agents")
        
        agents_data = {
            "Fondamentaux": ["Perception", "Analysis", "Recommendation", "Security", "Orchestrator"],
            "Collecte": ["A1 Collecteur"],
            "Analytiques": ["AN1 Prédicteur (94.7%)"],
            "Support": ["S1 Router"],
            "Sectoriels SCIAN": ["SC-23 Construction", "SC-31-33 Fabrication", "SC-21 Extraction", "SC-62 Santé", "SC-48-49 Transport"]
        }
        
        for categorie, agents in agents_data.items():
            with st.expander(f"📂 {categorie} ({len(agents)} agents)"):
                for agent in agents:
                    st.markdown(f"  ✅ {agent}")
    
    with col_right:
        st.subheader("⚡ Actions Rapides")
        
        if st.button("🔄 Rafraîchir Données", use_container_width=True):
            st.rerun()
        
        if st.button("🚨 Simuler Alerte Critique", use_container_width=True):
            result = api_call("/api/v1/simulate/critical", method="POST")
            if result["success"]:
                st.success("✅ Simulation exécutée!")
                st.json(result["data"])
            else:
                st.error(f"❌ {result['error']}")
        
        st.divider()
        
        st.subheader("📊 Statistiques Rapides")
        if stats["success"]:
            st.metric("Workflows", stats["data"].get("workflows_executed", 0))
            st.metric("Taux Succès", f"{stats['data'].get('success_rate', 0)*100:.1f}%")
        else:
            st.info("API non disponible")

# ============================================
# PAGE: MONITORING
# ============================================

elif page == "📊 Monitoring":
    st.markdown('<div class="main-header">📊 Monitoring des Zones</div>', unsafe_allow_html=True)
    
    # Récupérer les zones
    zones_result = api_call("/api/v1/zones")
    
    if zones_result["success"]:
        zones = zones_result["data"]
        
        # Filtres
        col1, col2, col3 = st.columns(3)
        with col1:
            filtre_risque = st.selectbox("Filtrer par risque", ["Tous", "TRÈS ÉLEVÉ", "ÉLEVÉ", "MOYEN", "FAIBLE"])
        with col2:
            filtre_type = st.selectbox("Filtrer par type", ["Tous", "Intérieur", "Extérieur"])
        with col3:
            recherche = st.text_input("🔍 Rechercher", placeholder="Nom de zone...")
        
        # Appliquer filtres
        zones_filtrees = zones
        if filtre_risque != "Tous":
            zones_filtrees = [z for z in zones_filtrees if z.get("niveau_risque") == filtre_risque]
        if filtre_type != "Tous":
            zones_filtrees = [z for z in zones_filtrees if z.get("type") == filtre_type]
        if recherche:
            zones_filtrees = [z for z in zones_filtrees if recherche.lower() in z.get("nom", "").lower()]
        
        st.info(f"📍 {len(zones_filtrees)} zones affichées sur {len(zones)}")
        
        # Affichage des zones
        cols = st.columns(3)
        for i, zone in enumerate(zones_filtrees):
            with cols[i % 3]:
                niveau = zone.get("niveau_risque", "MOYEN")
                emoji = get_risk_emoji(niveau)
                
                with st.container():
                    st.markdown(f"""
                    <div class="zone-card">
                        <h4>{emoji} {zone.get('nom', 'Zone')}</h4>
                        <p><strong>Type:</strong> {zone.get('type', 'N/A')}</p>
                        <p><strong>Risque:</strong> <span class="{get_risk_color(niveau)}">{niveau}</span></p>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.error(f"❌ Impossible de charger les zones: {zones_result['error']}")
        st.info("💡 Vérifiez que l'API est lancée: `python api.py`")

# ============================================
# PAGE: ALERTES
# ============================================

elif page == "🚨 Alertes":
    st.markdown('<div class="main-header">🚨 Centre d\'Alertes</div>', unsafe_allow_html=True)
    
    # Récupérer les risques et near-misses
    risks_result = api_call("/api/v1/risks")
    near_misses_result = api_call("/api/v1/near-misses")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("⚠️ Risques Identifiés")
        
        if risks_result["success"]:
            risks = risks_result["data"]
            
            if risks:
                for risk in risks[:10]:
                    severite = risk.get("severite", "medium")
                    alert_class = "alert-critical" if severite in ["critical", "CRITIQUE"] else "alert-high" if severite in ["high", "ÉLEVÉ"] else "alert-medium"
                    
                    st.markdown(f"""
                    <div class="{alert_class}">
                        <strong>{risk.get('description', 'Risque non décrit')[:80]}</strong><br>
                        <small>Catégorie: {risk.get('categorie', 'N/A')} | Sévérité: {severite}</small>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.success("✅ Aucun risque actif!")
        else:
            st.error(f"❌ {risks_result['error']}")
    
    with col2:
        st.subheader("🎯 Near-Misses Récents")
        
        if near_misses_result["success"]:
            near_misses = near_misses_result["data"]
            
            if near_misses:
                for nm in near_misses[:10]:
                    gravite = nm.get("potentiel_gravite", "moyen")
                    alert_class = "alert-critical" if gravite in ["critical", "CRITIQUE", "élevé"] else "alert-medium"
                    
                    st.markdown(f"""
                    <div class="{alert_class}">
                        <strong>🎯 {nm.get('type_risque', 'Type inconnu')}</strong><br>
                        <small>Gravité potentielle: {gravite}</small><br>
                        <small>Zone: {nm.get('zone_id', 'N/A')}</small>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.success("✅ Aucun near-miss récent!")
        else:
            st.error(f"❌ {near_misses_result['error']}")

# ============================================
# PAGE: AGENTS
# ============================================

elif page == "🤖 Agents":
    st.markdown('<div class="main-header">🤖 État des Agents</div>', unsafe_allow_html=True)
    
    # Liste des agents
    agents = [
        {"id": "Perception", "categorie": "Fondamental", "status": "active", "precision": None},
        {"id": "Analysis", "categorie": "Fondamental", "status": "active", "precision": None},
        {"id": "Recommendation", "categorie": "Fondamental", "status": "active", "precision": None},
        {"id": "Security Manager", "categorie": "Fondamental", "status": "active", "precision": None},
        {"id": "Orchestrator", "categorie": "Fondamental", "status": "active", "precision": None},
        {"id": "A1 Collecteur", "categorie": "Collecte", "status": "active", "precision": None},
        {"id": "AN1 Prédicteur", "categorie": "Analytique", "status": "active", "precision": 94.7},
        {"id": "S1 Router", "categorie": "Support", "status": "active", "precision": None},
        {"id": "SC-23 Construction", "categorie": "Sectoriel SCIAN", "status": "active", "precision": 93.7},
        {"id": "SC-31-33 Fabrication", "categorie": "Sectoriel SCIAN", "status": "active", "precision": 91.2},
        {"id": "SC-21 Extraction", "categorie": "Sectoriel SCIAN", "status": "active", "precision": 89.5},
        {"id": "SC-62 Santé", "categorie": "Sectoriel SCIAN", "status": "active", "precision": 88.7},
        {"id": "SC-48-49 Transport", "categorie": "Sectoriel SCIAN", "status": "active", "precision": 90.1},
    ]
    
    # Métriques
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🤖 Total Agents", len(agents))
    with col2:
        actifs = len([a for a in agents if a["status"] == "active"])
        st.metric("✅ Actifs", actifs)
    with col3:
        with_precision = [a["precision"] for a in agents if a["precision"]]
        avg_precision = sum(with_precision) / len(with_precision) if with_precision else 0
        st.metric("🎯 Précision Moy.", f"{avg_precision:.1f}%")
    with col4:
        categories = len(set(a["categorie"] for a in agents))
        st.metric("📂 Catégories", categories)
    
    st.divider()
    
    # Grouper par catégorie
    categories = {}
    for agent in agents:
        cat = agent["categorie"]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(agent)
    
    # Affichage par catégorie
    for categorie, agents_cat in categories.items():
        st.subheader(f"📂 {categorie}")
        
        cols = st.columns(4)
        for i, agent in enumerate(agents_cat):
            with cols[i % 4]:
                status_emoji = "🟢" if agent["status"] == "active" else "🔴"
                precision_str = f" | {agent['precision']}%" if agent["precision"] else ""
                
                card_class = "agent-card" if agent["status"] == "active" else "agent-card-inactive"
                
                st.markdown(f"""
                <div class="{card_class}">
                    <strong>{status_emoji} {agent['id']}</strong><br>
                    <small>Status: {agent['status']}{precision_str}</small>
                </div>
                """, unsafe_allow_html=True)

# ============================================
# PAGE: SIMULATION
# ============================================

elif page == "⚙️ Simulation":
    st.markdown('<div class="main-header">⚙️ Simulation & Tests</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎮 Simulateur d'Événements")
        
        st.markdown("#### Paramètres de Simulation")
        
        zone_id = st.text_input("Zone ID", value="ZONE-PROD-001")
        
        col_a, col_b = st.columns(2)
        with col_a:
            temperature = st.slider("🌡️ Température (°C)", 15, 50, 38)
        with col_b:
            bruit = st.slider("🔊 Bruit (dB)", 50, 110, 85)
        
        col_c, col_d = st.columns(2)
        with col_c:
            humidite = st.slider("💧 Humidité (%)", 20, 100, 65)
        with col_d:
            vibration = st.slider("📳 Vibration (m/s²)", 0.0, 10.0, 3.5)
        
        if st.button("🚀 Lancer Simulation", type="primary", use_container_width=True):
            payload = {
                "sensor_readings": [
                    {"sensor_id": "TEMP-SIM", "sensor_type": "temperature", "value": temperature, "unit": "C"},
                    {"sensor_id": "NOISE-SIM", "sensor_type": "noise", "value": bruit, "unit": "dB"},
                    {"sensor_id": "HUM-SIM", "sensor_type": "humidity", "value": humidite, "unit": "%"},
                    {"sensor_id": "VIB-SIM", "sensor_type": "vibration", "value": vibration, "unit": "m/s2"}
                ],
                "zone_id": zone_id
            }
            
            with st.spinner("Traitement en cours..."):
                result = api_call("/api/v1/workflow/process", method="POST", data=payload)
            
            if result["success"]:
                data = result["data"]
                
                st.success("✅ Simulation terminée!")
                
                # Résultats
                risk_level = data.get("risk_level", "unknown")
                risk_score = data.get("risk_score", 0)
                
                emoji = get_risk_emoji(risk_level)
                st.markdown(f"### {emoji} Niveau de Risque: **{risk_level.upper()}** ({risk_score}/100)")
                
                # Alertes
                if data.get("alerts"):
                    st.markdown("#### 🚨 Alertes Générées")
                    for alert in data["alerts"]:
                        st.warning(f"⚠️ {alert.get('sensor_type', 'N/A')}: {alert.get('value')} (seuil: {alert.get('threshold')})")
                
                # Recommandations
                if data.get("recommendations"):
                    st.markdown("#### 📋 Recommandations")
                    for rec in data["recommendations"]:
                        st.info(f"💡 {rec}")
                
                # JSON complet
                with st.expander("📄 Réponse JSON complète"):
                    st.json(data)
            else:
                st.error(f"❌ Erreur: {result['error']}")
    
    with col2:
        st.subheader("⚡ Tests Rapides")
        
        st.markdown("#### Simulation Critique")
        st.caption("Génère un événement avec température 45°C et bruit 92dB")
        
        if st.button("🔴 Simuler Événement Critique", use_container_width=True):
            result = api_call("/api/v1/simulate/critical", method="POST")
            
            if result["success"]:
                st.success("✅ Événement critique simulé!")
                st.json(result["data"])
            else:
                st.error(f"❌ {result['error']}")
        
        st.divider()
        
        st.markdown("#### 🔍 Test Health Check")
        
        if st.button("🏥 Vérifier Santé API", use_container_width=True):
            result = api_call("/health")
            
            if result["success"]:
                st.success("✅ API en bonne santé!")
                st.json(result["data"])
            else:
                st.error(f"❌ {result['error']}")
        
        st.divider()
        
        st.markdown("#### 📊 Statistiques")
        
        if st.button("📈 Charger Statistiques", use_container_width=True):
            result = api_call("/api/v1/stats")
            
            if result["success"]:
                st.json(result["data"])
            else:
                st.error(f"❌ {result['error']}")

# ============================================
# FOOTER
# ============================================

st.divider()
st.markdown("""
<div style="text-align: center; color: #6B7280; font-size: 0.8rem;">
    🛡️ EDGY-AgenticX5 | Système de Prévention SST Multi-Agents<br>
    Développé par GenAISafety / Preventera / SquadrAI<br>
    © 2025 - Tous droits réservés
</div>
""", unsafe_allow_html=True)
