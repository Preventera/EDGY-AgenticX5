#!/usr/bin/env python3
"""
🛡️ SafetyGraph Dashboard - Streamlit
EDGY-AgenticX5 | Preventera | GenAISafety

Dashboard interactif pour visualiser les 16 secteurs SCIAN
avec connexion directe à Neo4j

Installation:
    pip install streamlit plotly pandas neo4j --break-system-packages

Exécution:
    streamlit run safetygraph_dashboard.py
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from neo4j import GraphDatabase
import os
from datetime import datetime

# ============================================================================
# CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="SafetyGraph Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Connexion Neo4j
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

# Secteurs SCIAN avec couleurs
SECTEURS_CONFIG = {
    "611": {"nom": "🏫 Écoles", "couleur": "#FFB6C1"},
    "31-33": {"nom": "🏭 Fabrication", "couleur": "#4169E1"},
    "111-115": {"nom": "🌾 Agriculture", "couleur": "#228B22"},
    "212-213": {"nom": "⛏️ Mines", "couleur": "#8B4513"},
    "484-493": {"nom": "🚛 Transport", "couleur": "#FF8C00"},
    "621-624": {"nom": "🏥 Santé", "couleur": "#DC143C"},
    "561-562": {"nom": "🧹 Services soutien", "couleur": "#9370DB"},
    "911-912": {"nom": "🚒 Admin publiques", "couleur": "#4682B4"},
    "311-312": {"nom": "🍖 Agroalimentaire", "couleur": "#DAA520"},
    "236-238": {"nom": "🏗️ Construction", "couleur": "#FF6347"},
    "237": {"nom": "⚡ Génie civil", "couleur": "#FFD700"},
    "22": {"nom": "⚡💧 Services publics", "couleur": "#00CED1"},
    "72": {"nom": "🍽️ Hébergement/Resto", "couleur": "#FF69B4"},
    "44-45": {"nom": "🛒 Commerce détail", "couleur": "#32CD32"},
    "54": {"nom": "💼 Services pro", "couleur": "#6A5ACD"},
}

# ============================================================================
# CONNEXION NEO4J
# ============================================================================

@st.cache_resource
def get_neo4j_driver():
    """Connexion Neo4j avec cache"""
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        driver.verify_connectivity()
        return driver
    except Exception as e:
        st.error(f"❌ Erreur connexion Neo4j: {e}")
        return None

def run_query(query, params=None):
    """Exécute une requête Cypher"""
    driver = get_neo4j_driver()
    if not driver:
        return []
    try:
        with driver.session() as session:
            result = session.run(query, params or {})
            return [dict(record) for record in result]
    except Exception as e:
        st.error(f"Erreur requête: {e}")
        return []

# ============================================================================
# REQUÊTES CYPHER
# ============================================================================

def get_stats_globales():
    """Statistiques globales du graphe"""
    query = """
    MATCH (o:Organization) WITH count(o) as orgs
    MATCH (p:Person) WITH orgs, count(p) as persons
    MATCH (r:RisqueDanger) WITH orgs, persons, count(r) as risks
    MATCH (z:Zone) WITH orgs, persons, risks, count(z) as zones
    MATCH (t:Team) WITH orgs, persons, risks, zones, count(t) as teams
    MATCH (ro:Role) 
    RETURN orgs, persons, risks, zones, teams, count(ro) as roles
    """
    result = run_query(query)
    if result:
        return result[0]
    return {"orgs": 0, "persons": 0, "risks": 0, "zones": 0, "teams": 0, "roles": 0}

def get_orgs_par_secteur():
    """Organisations par secteur SCIAN"""
    query = """
    MATCH (o:Organization)
    WHERE o.sector_scian IS NOT NULL
    RETURN o.sector_scian as secteur, count(o) as count, 
           collect(o.name)[0..5] as exemples,
           sum(o.nb_employes) as total_employes
    ORDER BY count DESC
    """
    return run_query(query)

def get_risques_par_categorie():
    """Risques par catégorie"""
    query = """
    MATCH (r:RisqueDanger)
    WHERE r.categorie IS NOT NULL
    RETURN r.categorie as categorie, count(r) as count,
           avg(r.probabilite * r.gravite) as score_moyen
    ORDER BY count DESC
    """
    return run_query(query)

def get_zones_par_niveau():
    """Zones par niveau de risque"""
    query = """
    MATCH (z:Zone)
    WHERE z.risk_level IS NOT NULL
    RETURN z.risk_level as niveau, count(z) as count
    ORDER BY 
        CASE z.risk_level 
            WHEN 'critique' THEN 1 
            WHEN 'eleve' THEN 2 
            WHEN 'moyen' THEN 3 
            ELSE 4 
        END
    """
    return run_query(query)

def get_top_organisations():
    """Top organisations par nombre d'employés"""
    query = """
    MATCH (o:Organization)
    WHERE o.nb_employes IS NOT NULL AND o.nb_employes > 0
    RETURN o.name as nom, o.sector_scian as secteur, 
           o.nb_employes as employes, o.region_ssq as region
    ORDER BY o.nb_employes DESC
    LIMIT 20
    """
    return run_query(query)

def get_risques_tolerance_zero():
    """Risques à tolérance zéro (score >= 15)"""
    query = """
    MATCH (r:RisqueDanger)
    WHERE r.probabilite * r.gravite >= 15
    RETURN r.description as risque, r.categorie as categorie,
           r.probabilite as prob, r.gravite as grav,
           r.probabilite * r.gravite as score
    ORDER BY score DESC
    LIMIT 30
    """
    return run_query(query)

def get_personnes_par_age():
    """Distribution des personnes par groupe d'âge"""
    query = """
    MATCH (p:Person)
    WHERE p.age_groupe IS NOT NULL
    RETURN p.age_groupe as age, count(p) as count
    ORDER BY p.age_groupe
    """
    return run_query(query)

def get_certifications_frequentes():
    """Certifications SST les plus fréquentes"""
    query = """
    MATCH (p:Person)
    WHERE p.certifications_sst IS NOT NULL
    UNWIND p.certifications_sst as cert
    RETURN cert as certification, count(*) as count
    ORDER BY count DESC
    LIMIT 15
    """
    return run_query(query)

def search_organisations(terme):
    """Recherche d'organisations"""
    query = """
    MATCH (o:Organization)
    WHERE toLower(o.name) CONTAINS toLower($terme)
       OR o.sector_scian CONTAINS $terme
    RETURN o.name as nom, o.sector_scian as secteur, 
           o.nb_employes as employes, o.region_ssq as region
    LIMIT 20
    """
    return run_query(query, {"terme": terme})

def get_relations_graph():
    """Données pour le graphe de relations"""
    query = """
    MATCH (o:Organization)<-[:APPARTIENT_A]-(z:Zone)
    WITH o, count(z) as nb_zones
    MATCH (o)<-[:APPARTIENT_A]-(t:Team)
    WITH o, nb_zones, count(t) as nb_teams
    RETURN o.name as org, o.sector_scian as secteur, 
           nb_zones, nb_teams, o.nb_employes as employes
    ORDER BY employes DESC
    LIMIT 30
    """
    return run_query(query)

# ============================================================================
# INTERFACE STREAMLIT
# ============================================================================

def main():
    # Header
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); 
                padding: 20px; border-radius: 10px; margin-bottom: 20px;">
        <h1 style="color: white; margin: 0;">🛡️ SafetyGraph Dashboard</h1>
        <p style="color: #00d4ff; margin: 5px 0 0 0;">
            EDGY-AgenticX5 | 16 Secteurs SCIAN | Neo4j Knowledge Graph
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 🔧 Configuration")
        
        # Test connexion
        driver = get_neo4j_driver()
        if driver:
            st.success("✅ Neo4j connecté")
        else:
            st.error("❌ Neo4j non connecté")
            st.info(f"URI: {NEO4J_URI}")
            st.stop()
        
        st.markdown("---")
        st.markdown("### 📊 Navigation")
        page = st.radio(
            "Section",
            ["🏠 Vue d'ensemble", "🏢 Organisations", "⚠️ Risques", 
             "👥 Personnes", "🔍 Recherche", "📈 Analyses"]
        )
        
        st.markdown("---")
        st.markdown("### ℹ️ À propos")
        st.markdown("""
        **SafetyGraph** est un graphe de connaissances 
        pour la prévention SST au Québec.
        
        - 16 secteurs SCIAN
        - 460+ organisations
        - 2,800+ risques
        - 3,900+ personnes
        
        *Données anonymisées (Loi 25)*
        """)
    
    # Contenu principal selon la page
    if page == "🏠 Vue d'ensemble":
        render_overview()
    elif page == "🏢 Organisations":
        render_organisations()
    elif page == "⚠️ Risques":
        render_risques()
    elif page == "👥 Personnes":
        render_personnes()
    elif page == "🔍 Recherche":
        render_recherche()
    elif page == "📈 Analyses":
        render_analyses()

def render_overview():
    """Page Vue d'ensemble"""
    st.header("🏠 Vue d'ensemble SafetyGraph")
    
    # KPIs
    stats = get_stats_globales()
    
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        st.metric("🏢 Organisations", f"{stats.get('orgs', 0):,}")
    with col2:
        st.metric("👥 Personnes", f"{stats.get('persons', 0):,}")
    with col3:
        st.metric("⚠️ Risques", f"{stats.get('risks', 0):,}")
    with col4:
        st.metric("📍 Zones", f"{stats.get('zones', 0):,}")
    with col5:
        st.metric("👔 Équipes", f"{stats.get('teams', 0):,}")
    with col6:
        st.metric("🎯 Rôles", f"{stats.get('roles', 0):,}")
    
    st.markdown("---")
    
    # Graphiques
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Organisations par secteur SCIAN")
        data = get_orgs_par_secteur()
        if data:
            df = pd.DataFrame(data)
            
            # Mapper les noms de secteurs
            def get_secteur_nom(code):
                for key, val in SECTEURS_CONFIG.items():
                    if code and (code.startswith(key.split("-")[0]) or code in key):
                        return val["nom"]
                return f"SCIAN {code}"
            
            df["secteur_nom"] = df["secteur"].apply(get_secteur_nom)
            
            fig = px.bar(
                df.head(15), 
                x="count", 
                y="secteur_nom",
                orientation="h",
                color="count",
                color_continuous_scale="Blues",
                labels={"count": "Nombre", "secteur_nom": "Secteur"}
            )
            fig.update_layout(height=500, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🎯 Zones par niveau de risque")
        data = get_zones_par_niveau()
        if data:
            df = pd.DataFrame(data)
            
            colors = {
                "critique": "#DC143C",
                "eleve": "#FF8C00", 
                "moyen": "#FFD700",
                "faible": "#32CD32"
            }
            df["couleur"] = df["niveau"].map(colors)
            
            fig = px.pie(
                df, 
                values="count", 
                names="niveau",
                color="niveau",
                color_discrete_map=colors,
                hole=0.4
            )
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
    
    # Risques par catégorie
    st.subheader("⚠️ Risques par catégorie")
    data = get_risques_par_categorie()
    if data:
        df = pd.DataFrame(data)
        
        fig = px.treemap(
            df,
            path=["categorie"],
            values="count",
            color="score_moyen",
            color_continuous_scale="RdYlGn_r",
            labels={"count": "Nombre", "score_moyen": "Score moyen"}
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

def render_organisations():
    """Page Organisations"""
    st.header("🏢 Organisations par secteur")
    
    # Top organisations
    st.subheader("🏆 Top 20 organisations (par employés)")
    data = get_top_organisations()
    if data:
        df = pd.DataFrame(data)
        
        fig = px.bar(
            df,
            x="employes",
            y="nom",
            orientation="h",
            color="secteur",
            hover_data=["region"],
            labels={"employes": "Employés", "nom": "Organisation", "secteur": "SCIAN"}
        )
        fig.update_layout(height=600, yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, use_container_width=True)
        
        # Tableau détaillé
        st.dataframe(
            df.rename(columns={
                "nom": "Organisation",
                "secteur": "SCIAN",
                "employes": "Employés",
                "region": "Région"
            }),
            use_container_width=True,
            hide_index=True
        )

def render_risques():
    """Page Risques"""
    st.header("⚠️ Analyse des risques SST")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔴 Risques Tolérance Zéro (score ≥ 15)")
        data = get_risques_tolerance_zero()
        if data:
            df = pd.DataFrame(data)
            
            fig = px.scatter(
                df,
                x="prob",
                y="grav",
                size="score",
                color="categorie",
                hover_data=["risque"],
                labels={"prob": "Probabilité", "grav": "Gravité", "score": "Score"},
                size_max=30
            )
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📊 Distribution des scores de risque")
        if data:
            fig = px.histogram(
                df,
                x="score",
                nbins=10,
                color="categorie",
                labels={"score": "Score (P×G)", "count": "Nombre"}
            )
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
    
    # Tableau des risques critiques
    st.subheader("📋 Liste des risques critiques")
    if data:
        st.dataframe(
            df.rename(columns={
                "risque": "Description",
                "categorie": "Catégorie",
                "prob": "P",
                "grav": "G",
                "score": "Score"
            }),
            use_container_width=True,
            hide_index=True
        )

def render_personnes():
    """Page Personnes"""
    st.header("👥 Analyse des personnes")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Distribution par groupe d'âge")
        data = get_personnes_par_age()
        if data:
            df = pd.DataFrame(data)
            
            fig = px.bar(
                df,
                x="age",
                y="count",
                color="age",
                labels={"age": "Groupe d'âge", "count": "Nombre"}
            )
            fig.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🎓 Certifications SST fréquentes")
        data = get_certifications_frequentes()
        if data:
            df = pd.DataFrame(data)
            
            fig = px.bar(
                df,
                x="count",
                y="certification",
                orientation="h",
                color="count",
                color_continuous_scale="Greens",
                labels={"count": "Nombre", "certification": "Certification"}
            )
            fig.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

def render_recherche():
    """Page Recherche"""
    st.header("🔍 Recherche d'organisations")
    
    terme = st.text_input(
        "Rechercher une organisation",
        placeholder="Ex: Hydro-Québec, CGI, Metro, SCIAN 54..."
    )
    
    if terme:
        data = search_organisations(terme)
        if data:
            st.success(f"✅ {len(data)} résultat(s) trouvé(s)")
            df = pd.DataFrame(data)
            
            st.dataframe(
                df.rename(columns={
                    "nom": "Organisation",
                    "secteur": "SCIAN",
                    "employes": "Employés",
                    "region": "Région"
                }),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.warning("❌ Aucun résultat trouvé")
    else:
        st.info("💡 Entrez un terme de recherche (nom, secteur SCIAN...)")

def render_analyses():
    """Page Analyses avancées"""
    st.header("📈 Analyses avancées")
    
    st.subheader("🔗 Réseau Organisations-Zones-Équipes")
    data = get_relations_graph()
    if data:
        df = pd.DataFrame(data)
        
        fig = px.scatter(
            df,
            x="nb_zones",
            y="nb_teams",
            size="employes",
            color="secteur",
            hover_data=["org"],
            labels={
                "nb_zones": "Nombre de zones",
                "nb_teams": "Nombre d'équipes",
                "employes": "Employés"
            },
            size_max=50
        )
        fig.update_layout(height=600)
        st.plotly_chart(fig, use_container_width=True)
    
    # Matrice de corrélation
    st.subheader("📊 Statistiques par secteur")
    orgs_data = get_orgs_par_secteur()
    if orgs_data:
        df = pd.DataFrame(orgs_data)
        
        # Créer un graphique bubble
        fig = px.scatter(
            df,
            x="count",
            y="total_employes",
            size="count",
            color="secteur",
            hover_data=["exemples"],
            labels={
                "count": "Nombre d'organisations",
                "total_employes": "Total employés",
                "secteur": "SCIAN"
            },
            size_max=40
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# EXÉCUTION
# ============================================================================

if __name__ == "__main__":
    main()
