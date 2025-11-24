#!/usr/bin/env python3
"""
Module Dashboard Cartographie EDGY - EDGY-AgenticX5
Interface Streamlit pour visualiser et gérer la cartographie organisationnelle

À intégrer dans dashboard_streamlit.py ou à utiliser standalone
"""

import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime

# ============================================
# CONFIGURATION
# ============================================

API_BASE_URL = "http://localhost:8000"

# ============================================
# STYLES CSS CARTOGRAPHIE
# ============================================

CARTOGRAPHY_CSS = """
<style>
    .org-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin-bottom: 1rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    .person-card {
        background: white;
        border-left: 4px solid #3B82F6;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0 10px 10px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .team-card {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    
    .zone-card-critical {
        background: linear-gradient(135deg, #ff416c 0%, #ff4b2b 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    
    .zone-card-high {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    
    .zone-card-medium {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        color: #333;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    
    .zone-card-low {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        color: #333;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    
    .process-card {
        background: white;
        border: 2px solid #8B5CF6;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    
    .stat-box {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .stat-number {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E3A8A;
    }
    
    .stat-label {
        color: #6B7280;
        font-size: 0.9rem;
    }
    
    .hierarchy-level {
        margin-left: 2rem;
        border-left: 2px dashed #CBD5E1;
        padding-left: 1rem;
    }
</style>
"""

# ============================================
# FONCTIONS API
# ============================================

def api_get(endpoint: str):
    """GET request to API"""
    try:
        response = requests.get(f"{API_BASE_URL}{endpoint}", timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def api_post(endpoint: str, data: dict = None):
    """POST request to API"""
    try:
        response = requests.post(
            f"{API_BASE_URL}{endpoint}",
            json=data or {},
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"Erreur API: {e}")
        return None

def api_delete(endpoint: str):
    """DELETE request to API"""
    try:
        response = requests.delete(f"{API_BASE_URL}{endpoint}", timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

# ============================================
# COMPOSANTS UI
# ============================================

def render_stats_cards(stats: dict):
    """Afficher les cartes de statistiques"""
    cols = st.columns(7)
    
    icons = {
        "organizations": "🏢",
        "persons": "👥",
        "teams": "👔",
        "roles": "🎭",
        "processes": "⚙️",
        "zones": "📍",
        "relations": "🔗"
    }
    
    labels = {
        "organizations": "Organisations",
        "persons": "Personnes",
        "teams": "Équipes",
        "roles": "Rôles",
        "processes": "Processus",
        "zones": "Zones",
        "relations": "Relations"
    }
    
    for i, (key, value) in enumerate(stats.items()):
        if key != "last_updated":
            with cols[i % 7]:
                st.markdown(f"""
                <div class="stat-box">
                    <div style="font-size: 2rem;">{icons.get(key, '📊')}</div>
                    <div class="stat-number">{value}</div>
                    <div class="stat-label">{labels.get(key, key)}</div>
                </div>
                """, unsafe_allow_html=True)


def render_person_card(person: dict):
    """Afficher une carte personne"""
    supervisor = f"👤 Superviseur: {person.get('supervisor_id', 'Aucun')}" if person.get('supervisor_id') else ""
    roles = ", ".join(person.get('roles', [])) or "Aucun rôle"
    teams = ", ".join(person.get('teams', [])) or "Aucune équipe"
    
    st.markdown(f"""
    <div class="person-card">
        <h4>👤 {person.get('name', 'Inconnu')}</h4>
        <p>📧 {person.get('email', 'N/A')} | 🏢 {person.get('department', 'N/A')}</p>
        <p>🎭 Rôles: {roles}</p>
        <p>👔 Équipes: {teams}</p>
        <small>{supervisor}</small>
    </div>
    """, unsafe_allow_html=True)


def render_zone_card(zone: dict):
    """Afficher une carte zone de risque"""
    risk_level = zone.get('risk_level', 'moyen')
    
    # Mapper les niveaux de risque aux classes CSS
    css_class = {
        'critique': 'zone-card-critical',
        'élevé': 'zone-card-high',
        'eleve': 'zone-card-high',
        'moyen': 'zone-card-medium',
        'faible': 'zone-card-low',
        'minimal': 'zone-card-low'
    }.get(risk_level.lower() if risk_level else 'moyen', 'zone-card-medium')
    
    risk_emoji = {
        'critique': '🔴',
        'élevé': '🟠',
        'eleve': '🟠',
        'moyen': '🟡',
        'faible': '🟢',
        'minimal': '⚪'
    }.get(risk_level.lower() if risk_level else 'moyen', '🟡')
    
    hazards = zone.get('hazards', [])
    controls = zone.get('controls', [])
    ppe = zone.get('required_ppe', [])
    
    st.markdown(f"""
    <div class="{css_class}">
        <h4>{risk_emoji} {zone.get('name', 'Zone inconnue')}</h4>
        <p>📍 {zone.get('location', 'Localisation N/A')}</p>
        <p><strong>Niveau de risque:</strong> {risk_level.upper()}</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("⚠️ Dangers et contrôles"):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**⚠️ Dangers:**")
            for h in hazards:
                st.markdown(f"- {h}")
        with col2:
            st.markdown("**🛡️ Contrôles:**")
            for c in controls:
                st.markdown(f"- {c}")
        
        if ppe:
            st.markdown("**👷 EPI requis:** " + ", ".join(ppe))


def render_process_card(process: dict):
    """Afficher une carte processus"""
    process_type = process.get('process_type', 'N/A')
    if hasattr(process_type, 'value'):
        process_type = process_type.value
    
    type_emoji = {
        'inspection': '🔍',
        'audit': '📋',
        'formation': '🎓',
        'incident': '🚨',
        'maintenance': '🔧',
        'prevention': '🛡️',
        'intervention': '🚑'
    }.get(str(process_type).lower(), '⚙️')
    
    st.markdown(f"""
    <div class="process-card">
        <h4>{type_emoji} {process.get('name', 'Processus inconnu')}</h4>
        <p><strong>Type:</strong> {process_type} | <strong>Fréquence:</strong> {process.get('frequency', 'N/A')}</p>
        <p>{process.get('description', '')}</p>
    </div>
    """, unsafe_allow_html=True)


def render_team_card(team: dict):
    """Afficher une carte équipe"""
    st.markdown(f"""
    <div class="team-card">
        <h4>👔 {team.get('name', 'Équipe inconnue')}</h4>
        <p>🏢 {team.get('department', 'N/A')} | 👥 {team.get('members_count', 0)} membres</p>
        <p>{team.get('description', '')}</p>
    </div>
    """, unsafe_allow_html=True)


# ============================================
# PAGES PRINCIPALES
# ============================================

def page_overview():
    """Page vue d'ensemble de la cartographie"""
    st.header("🗺️ Vue d'ensemble de la Cartographie")
    
    # Récupérer les stats
    stats = api_get("/cartography/stats")
    
    if stats:
        render_stats_cards(stats)
        st.markdown("---")
    else:
        st.warning("⚠️ Impossible de récupérer les statistiques. L'API est-elle démarrée ?")
        return
    
    # Boutons d'action
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🎮 Créer données démo", use_container_width=True):
            with st.spinner("Création des données..."):
                result = api_post("/cartography/demo/populate")
                if result and result.get("status") == "success":
                    st.success("✅ Données de démonstration créées !")
                    st.rerun()
                else:
                    st.error("❌ Erreur lors de la création")
    
    with col2:
        if st.button("🔄 Sync Neo4j", use_container_width=True):
            with st.spinner("Synchronisation..."):
                result = api_post("/cartography/sync-neo4j")
                if result and result.get("status") == "success":
                    st.success(f"✅ Synchronisation réussie !")
                    st.json(result.get("sync_stats", {}))
                else:
                    st.error("❌ Erreur de synchronisation")
    
    with col3:
        if st.button("📊 Stats Neo4j", use_container_width=True):
            result = api_get("/cartography/neo4j-stats")
            if result:
                st.json(result.get("statistics", {}))
    
    with col4:
        if st.button("📤 Export RDF", use_container_width=True):
            result = api_post("/cartography/export/rdf", {"format": "turtle"})
            if result:
                st.success(f"✅ {result.get('triples_count', 0)} triples générés")
                with st.expander("Voir RDF"):
                    st.code(result.get("content", ""), language="turtle")


def page_persons():
    """Page gestion des personnes"""
    st.header("👥 Gestion des Personnes")
    
    # Récupérer les personnes
    persons = api_get("/cartography/persons")
    
    if not persons:
        st.info("Aucune personne enregistrée. Créez des données démo d'abord.")
        return
    
    # Afficher sous forme de tableau
    df = pd.DataFrame(persons)
    st.dataframe(df, use_container_width=True)
    
    st.markdown("---")
    
    # Afficher les cartes
    cols = st.columns(2)
    for i, person in enumerate(persons):
        with cols[i % 2]:
            render_person_card(person)
    
    # Formulaire d'ajout
    st.markdown("---")
    st.subheader("➕ Ajouter une personne")
    
    with st.form("add_person"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Nom *")
            email = st.text_input("Email")
            department = st.text_input("Département")
        with col2:
            employee_id = st.text_input("ID Employé")
            phone = st.text_input("Téléphone")
        
        submitted = st.form_submit_button("Ajouter", use_container_width=True)
        
        if submitted and name:
            result = api_post("/cartography/persons", {
                "name": name,
                "email": email,
                "department": department,
                "employee_id": employee_id,
                "phone": phone
            })
            if result:
                st.success(f"✅ {name} ajouté(e) !")
                st.rerun()


def page_zones():
    """Page gestion des zones de risque"""
    st.header("📍 Zones de Risque")
    
    # Récupérer les zones
    zones = api_get("/cartography/zones")
    
    if not zones:
        st.info("Aucune zone enregistrée. Créez des données démo d'abord.")
        return
    
    # Résumé par niveau de risque
    risk_counts = {}
    for z in zones:
        level = z.get('risk_level', 'moyen')
        risk_counts[level] = risk_counts.get(level, 0) + 1
    
    cols = st.columns(5)
    risk_order = ['critique', 'élevé', 'moyen', 'faible', 'minimal']
    emojis = {'critique': '🔴', 'élevé': '🟠', 'moyen': '🟡', 'faible': '🟢', 'minimal': '⚪'}
    
    for i, level in enumerate(risk_order):
        with cols[i]:
            count = risk_counts.get(level, 0)
            st.metric(f"{emojis.get(level, '')} {level.title()}", count)
    
    st.markdown("---")
    
    # Afficher les zones
    for zone in zones:
        render_zone_card(zone)
    
    # Formulaire d'ajout
    st.markdown("---")
    st.subheader("➕ Ajouter une zone")
    
    with st.form("add_zone"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Nom de la zone *")
            location = st.text_input("Localisation")
            zone_type = st.selectbox("Type", ["Intérieur", "Extérieur", "Mixte"])
        with col2:
            risk_level = st.selectbox("Niveau de risque", ["minimal", "faible", "moyen", "élevé", "critique"])
            max_occupancy = st.number_input("Capacité max", min_value=1, value=10)
        
        hazards = st.text_area("Dangers (un par ligne)")
        controls = st.text_area("Contrôles (un par ligne)")
        ppe = st.text_input("EPI requis (séparés par des virgules)")
        
        submitted = st.form_submit_button("Ajouter", use_container_width=True)
        
        if submitted and name:
            result = api_post("/cartography/zones", {
                "name": name,
                "location": location,
                "zone_type": zone_type,
                "risk_level": risk_level,
                "max_occupancy": max_occupancy,
                "hazards": [h.strip() for h in hazards.split('\n') if h.strip()],
                "controls": [c.strip() for c in controls.split('\n') if c.strip()],
                "required_ppe": [p.strip() for p in ppe.split(',') if p.strip()]
            })
            if result:
                st.success(f"✅ Zone {name} créée !")
                st.rerun()


def page_teams():
    """Page gestion des équipes"""
    st.header("👔 Gestion des Équipes")
    
    teams = api_get("/cartography/teams")
    
    if not teams:
        st.info("Aucune équipe enregistrée.")
        return
    
    for team in teams:
        render_team_card(team)
    
    # Formulaire d'ajout
    st.markdown("---")
    st.subheader("➕ Ajouter une équipe")
    
    with st.form("add_team"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Nom de l'équipe *")
            department = st.text_input("Département")
        with col2:
            description = st.text_area("Description")
        
        submitted = st.form_submit_button("Ajouter", use_container_width=True)
        
        if submitted and name:
            result = api_post("/cartography/teams", {
                "name": name,
                "department": department,
                "description": description
            })
            if result:
                st.success(f"✅ Équipe {name} créée !")
                st.rerun()


def page_processes():
    """Page gestion des processus SST"""
    st.header("⚙️ Processus SST")
    
    processes = api_get("/cartography/processes")
    
    if not processes:
        st.info("Aucun processus enregistré.")
        return
    
    for process in processes:
        render_process_card(process)
    
    # Formulaire d'ajout
    st.markdown("---")
    st.subheader("➕ Ajouter un processus")
    
    with st.form("add_process"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Nom du processus *")
            process_type = st.selectbox("Type", [
                "inspection", "audit", "formation", 
                "incident", "maintenance", "prevention", "intervention"
            ])
        with col2:
            frequency = st.selectbox("Fréquence", [
                "Quotidien", "Hebdomadaire", "Mensuel", 
                "Trimestriel", "Annuel", "À la demande"
            ])
            description = st.text_area("Description")
        
        steps = st.text_area("Étapes (une par ligne)")
        
        submitted = st.form_submit_button("Ajouter", use_container_width=True)
        
        if submitted and name:
            result = api_post("/cartography/processes", {
                "name": name,
                "process_type": process_type,
                "frequency": frequency,
                "description": description,
                "steps": [s.strip() for s in steps.split('\n') if s.strip()]
            })
            if result:
                st.success(f"✅ Processus {name} créé !")
                st.rerun()


def page_neo4j_view():
    """Page visualisation Neo4j"""
    st.header("🔗 Données Neo4j")
    
    stats = api_get("/cartography/neo4j-stats")
    
    if not stats or stats.get("status") != "connected":
        st.error("❌ Neo4j non disponible")
        return
    
    # Statistiques
    st.subheader("📊 Statistiques des entités EDGY")
    neo4j_stats = stats.get("statistics", {})
    
    cols = st.columns(4)
    for i, (entity, count) in enumerate(neo4j_stats.items()):
        with cols[i % 4]:
            st.metric(entity, count)
    
    # Structure organisationnelle
    st.markdown("---")
    st.subheader("🏢 Structure Organisationnelle")
    
    org_structure = stats.get("organization_structure", {})
    persons = org_structure.get("persons", [])
    
    if persons:
        df = pd.DataFrame(persons)
        st.dataframe(df, use_container_width=True)
    
    # Zones par risque
    st.markdown("---")
    st.subheader("📍 Zones par Niveau de Risque")
    
    zones = stats.get("zones_by_risk", [])
    for zone in zones:
        render_zone_card(zone)


# ============================================
# APPLICATION PRINCIPALE
# ============================================

def run_cartography_dashboard():
    """Exécuter le dashboard cartographie standalone"""
    st.set_page_config(
        page_title="EDGY Cartographie | Dashboard",
        page_icon="🗺️",
        layout="wide"
    )
    
    # Injecter CSS
    st.markdown(CARTOGRAPHY_CSS, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); 
                padding: 2rem; border-radius: 15px; margin-bottom: 2rem;">
        <h1 style="color: white; text-align: center; margin: 0;">
            🗺️ EDGY Cartographie Organisationnelle
        </h1>
        <p style="color: rgba(255,255,255,0.8); text-align: center; margin: 0.5rem 0 0 0;">
            Visualisation et gestion de la structure SST
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Menu latéral
    with st.sidebar:
        st.image("https://img.icons8.com/fluency/96/000000/map.png", width=80)
        st.title("Navigation")
        
        page = st.radio(
            "Section",
            ["🏠 Vue d'ensemble", "👥 Personnes", "👔 Équipes", 
             "📍 Zones de risque", "⚙️ Processus", "🔗 Neo4j"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        st.markdown("**EDGY-AgenticX5**")
        st.markdown("v1.1.0 | Cartographie")
    
    # Afficher la page sélectionnée
    if page == "🏠 Vue d'ensemble":
        page_overview()
    elif page == "👥 Personnes":
        page_persons()
    elif page == "👔 Équipes":
        page_teams()
    elif page == "📍 Zones de risque":
        page_zones()
    elif page == "⚙️ Processus":
        page_processes()
    elif page == "🔗 Neo4j":
        page_neo4j_view()


# ============================================
# FONCTION D'INTÉGRATION
# ============================================

def add_cartography_section():
    """
    Fonction à appeler depuis dashboard_streamlit.py pour ajouter
    la section cartographie au dashboard principal
    """
    st.markdown(CARTOGRAPHY_CSS, unsafe_allow_html=True)
    
    tabs = st.tabs([
        "🏠 Vue d'ensemble", "👥 Personnes", "👔 Équipes",
        "📍 Zones", "⚙️ Processus", "🔗 Neo4j"
    ])
    
    with tabs[0]:
        page_overview()
    with tabs[1]:
        page_persons()
    with tabs[2]:
        page_teams()
    with tabs[3]:
        page_zones()
    with tabs[4]:
        page_processes()
    with tabs[5]:
        page_neo4j_view()


# ============================================
# POINT D'ENTRÉE STANDALONE
# ============================================

if __name__ == "__main__":
    run_cartography_dashboard()
