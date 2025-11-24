#!/usr/bin/env python3
"""
Module Organigramme Interactif - EDGY-AgenticX5
Visualisation de la structure organisationnelle avec Plotly

Fonctionnalités:
- Organigramme hiérarchique des personnes/équipes
- Carte des zones de risque
- Graphe des relations
- Export en image
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import networkx as nx
import requests
from typing import Dict, List, Any, Optional
import pandas as pd

# ============================================
# CONFIGURATION
# ============================================

API_BASE_URL = "http://localhost:8000"

# Couleurs par niveau de risque
RISK_COLORS = {
    'critique': '#FF4136',
    'élevé': '#FF851B',
    'eleve': '#FF851B',
    'moyen': '#FFDC00',
    'faible': '#2ECC40',
    'minimal': '#7FDBFF'
}

# Couleurs par type d'entité
ENTITY_COLORS = {
    'Organization': '#667eea',
    'Person': '#3B82F6',
    'Team': '#10B981',
    'Role': '#8B5CF6',
    'Zone': '#F59E0B',
    'Process': '#EC4899'
}

# ============================================
# FONCTIONS API
# ============================================

def api_get(endpoint: str) -> Optional[Dict]:
    """GET request to API"""
    try:
        response = requests.get(f"{API_BASE_URL}{endpoint}", timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None


# ============================================
# ORGANIGRAMME HIÉRARCHIQUE
# ============================================

def create_org_chart(persons: List[Dict], teams: List[Dict]) -> go.Figure:
    """
    Créer un organigramme hiérarchique interactif
    """
    if not persons:
        return None
    
    # Créer le graphe NetworkX
    G = nx.DiGraph()
    
    # Ajouter les nœuds personnes
    for person in persons:
        G.add_node(
            person['id'],
            name=person.get('name', 'Inconnu'),
            type='Person',
            department=person.get('department', 'N/A'),
            email=person.get('email', ''),
            roles=person.get('roles', []),
            teams=person.get('teams', [])
        )
    
    # Ajouter les relations de supervision
    for person in persons:
        if person.get('supervisor_id'):
            G.add_edge(person['supervisor_id'], person['id'])
    
    # Calculer les positions avec un layout hiérarchique
    if len(G.nodes()) > 0:
        try:
            # Essayer le layout hiérarchique
            pos = hierarchy_pos(G)
        except:
            # Fallback sur spring layout
            pos = nx.spring_layout(G, k=2, iterations=50)
    else:
        return None
    
    # Créer les traces pour Plotly
    edge_x = []
    edge_y = []
    
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
    
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=2, color='#888'),
        hoverinfo='none',
        mode='lines',
        name='Supervision'
    )
    
    node_x = []
    node_y = []
    node_text = []
    node_hover = []
    node_colors = []
    node_sizes = []
    
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        
        data = G.nodes[node]
        name = data.get('name', node)
        dept = data.get('department', 'N/A')
        
        node_text.append(name)
        
        # Info au survol
        roles = ", ".join(data.get('roles', [])) or 'Aucun'
        teams_list = ", ".join(data.get('teams', [])) or 'Aucune'
        hover = f"<b>{name}</b><br>Département: {dept}<br>Rôles: {roles}<br>Équipes: {teams_list}"
        node_hover.append(hover)
        
        # Taille basée sur le nombre de subordonnés
        subordinates = len(list(G.successors(node)))
        node_sizes.append(30 + subordinates * 10)
        
        # Couleur par département
        dept_colors = {
            'Production': '#3B82F6',
            'Maintenance': '#10B981',
            'Sécurité': '#EF4444',
            'RH': '#8B5CF6',
            'Direction': '#F59E0B'
        }
        node_colors.append(dept_colors.get(dept, '#6B7280'))
    
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        hoverinfo='text',
        hovertext=node_hover,
        text=node_text,
        textposition='bottom center',
        marker=dict(
            size=node_sizes,
            color=node_colors,
            line=dict(width=2, color='white'),
            symbol='circle'
        ),
        name='Personnes'
    )
    
    # Créer la figure
    fig = go.Figure(
        data=[edge_trace, node_trace],
        layout=go.Layout(
            title=dict(
                text='🏢 Organigramme - Structure de Supervision',
                font=dict(size=20)
            ),
            showlegend=False,
            hovermode='closest',
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=40, r=40, t=60, b=40),
            height=500
        )
    )
    
    return fig


def hierarchy_pos(G, root=None, width=1., vert_gap=0.2, vert_loc=0, xcenter=0.5):
    """
    Calculer les positions pour un layout hiérarchique
    """
    if root is None:
        # Trouver les racines (nœuds sans parents)
        roots = [n for n in G.nodes() if G.in_degree(n) == 0]
        if not roots:
            roots = list(G.nodes())[:1]
        root = roots[0] if roots else list(G.nodes())[0]
    
    def _hierarchy_pos(G, root, width=1., vert_gap=0.2, vert_loc=0, xcenter=0.5, pos=None, parent=None, parsed=[]):
        if pos is None:
            pos = {root: (xcenter, vert_loc)}
        else:
            pos[root] = (xcenter, vert_loc)
        
        children = list(G.successors(root))
        if children:
            dx = width / len(children)
            nextx = xcenter - width/2 - dx/2
            for child in children:
                nextx += dx
                pos = _hierarchy_pos(G, child, width=dx, vert_gap=vert_gap,
                                    vert_loc=vert_loc-vert_gap, xcenter=nextx,
                                    pos=pos, parent=root, parsed=parsed)
        return pos
    
    return _hierarchy_pos(G, root, width, vert_gap, vert_loc, xcenter)


# ============================================
# CARTE DES ZONES DE RISQUE
# ============================================

def create_risk_zone_map(zones: List[Dict]) -> go.Figure:
    """
    Créer une carte des zones de risque avec niveaux colorés
    """
    if not zones:
        return None
    
    # Préparer les données
    zone_names = []
    risk_levels = []
    hazard_counts = []
    colors = []
    hover_texts = []
    
    risk_order = {'critique': 5, 'élevé': 4, 'eleve': 4, 'moyen': 3, 'faible': 2, 'minimal': 1}
    
    for zone in zones:
        name = zone.get('name', 'Zone inconnue')
        risk = zone.get('risk_level', 'moyen')
        hazards = zone.get('hazards', [])
        controls = zone.get('controls', [])
        
        zone_names.append(name)
        risk_levels.append(risk_order.get(risk.lower() if risk else 'moyen', 3))
        hazard_counts.append(len(hazards))
        colors.append(RISK_COLORS.get(risk.lower() if risk else 'moyen', '#FFDC00'))
        
        hover = f"<b>{name}</b><br>"
        hover += f"Niveau: {risk}<br>"
        hover += f"Dangers: {len(hazards)}<br>"
        hover += f"Contrôles: {len(controls)}"
        hover_texts.append(hover)
    
    # Créer le graphique en barres horizontales
    fig = go.Figure(go.Bar(
        y=zone_names,
        x=risk_levels,
        orientation='h',
        marker=dict(
            color=colors,
            line=dict(color='white', width=2)
        ),
        text=[f"Niveau {r}" for r in risk_levels],
        textposition='inside',
        hovertext=hover_texts,
        hoverinfo='text'
    ))
    
    fig.update_layout(
        title=dict(
            text='📍 Zones de Risque - Niveaux de Danger',
            font=dict(size=20)
        ),
        xaxis=dict(
            title='Niveau de Risque',
            tickvals=[1, 2, 3, 4, 5],
            ticktext=['Minimal', 'Faible', 'Moyen', 'Élevé', 'Critique'],
            range=[0, 6]
        ),
        yaxis=dict(title=''),
        height=max(300, len(zones) * 60),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=150, r=40, t=60, b=40)
    )
    
    return fig


# ============================================
# GRAPHE DE RELATIONS
# ============================================

def create_relations_graph(persons: List[Dict], teams: List[Dict], zones: List[Dict]) -> go.Figure:
    """
    Créer un graphe de toutes les relations entre entités
    """
    G = nx.Graph()
    
    # Ajouter les personnes
    for person in persons:
        G.add_node(
            person['id'],
            label=person.get('name', 'Inconnu'),
            type='Person',
            color=ENTITY_COLORS['Person']
        )
    
    # Ajouter les équipes
    for team in teams:
        G.add_node(
            team['id'],
            label=team.get('name', 'Équipe'),
            type='Team',
            color=ENTITY_COLORS['Team']
        )
    
    # Ajouter les zones
    for zone in zones:
        G.add_node(
            zone['id'],
            label=zone.get('name', 'Zone'),
            type='Zone',
            color=ENTITY_COLORS['Zone']
        )
    
    # Ajouter les relations
    for person in persons:
        # Relations équipes
        for team_id in person.get('team_ids', []):
            if team_id in G.nodes():
                G.add_edge(person['id'], team_id, relation='member_of')
        
        # Relations supervision
        if person.get('supervisor_id') and person['supervisor_id'] in G.nodes():
            G.add_edge(person['id'], person['supervisor_id'], relation='reports_to')
    
    # Layout
    pos = nx.spring_layout(G, k=3, iterations=50)
    
    # Créer les traces
    edge_x = []
    edge_y = []
    
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
    
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=1, color='#ccc'),
        hoverinfo='none',
        mode='lines'
    )
    
    # Grouper les nœuds par type
    traces = [edge_trace]
    
    for entity_type, color in ENTITY_COLORS.items():
        if entity_type in ['Person', 'Team', 'Zone']:
            nodes_of_type = [n for n in G.nodes() if G.nodes[n].get('type') == entity_type]
            
            if nodes_of_type:
                node_x = [pos[n][0] for n in nodes_of_type]
                node_y = [pos[n][1] for n in nodes_of_type]
                node_text = [G.nodes[n].get('label', n) for n in nodes_of_type]
                
                symbol = {'Person': 'circle', 'Team': 'square', 'Zone': 'diamond'}
                
                trace = go.Scatter(
                    x=node_x, y=node_y,
                    mode='markers+text',
                    hoverinfo='text',
                    hovertext=node_text,
                    text=node_text,
                    textposition='top center',
                    textfont=dict(size=10),
                    marker=dict(
                        size=20,
                        color=color,
                        symbol=symbol.get(entity_type, 'circle'),
                        line=dict(width=2, color='white')
                    ),
                    name=entity_type
                )
                traces.append(trace)
    
    fig = go.Figure(
        data=traces,
        layout=go.Layout(
            title=dict(
                text='🔗 Graphe des Relations',
                font=dict(size=20)
            ),
            showlegend=True,
            hovermode='closest',
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=40, r=40, t=60, b=40),
            height=500,
            legend=dict(
                orientation='h',
                yanchor='bottom',
                y=1.02,
                xanchor='right',
                x=1
            )
        )
    )
    
    return fig


# ============================================
# TREEMAP ORGANISATIONNEL
# ============================================

def create_org_treemap(persons: List[Dict], teams: List[Dict]) -> go.Figure:
    """
    Créer un treemap de l'organisation par département
    """
    if not persons:
        return None
    
    # Construire les données pour le treemap
    labels = ['Organisation']
    parents = ['']
    values = [0]
    colors = ['#667eea']
    
    # Grouper par département
    departments = {}
    for person in persons:
        dept = person.get('department', 'Autre')
        if dept not in departments:
            departments[dept] = []
        departments[dept].append(person)
    
    # Ajouter les départements
    dept_colors = {
        'Production': '#3B82F6',
        'Maintenance': '#10B981',
        'Sécurité': '#EF4444',
        'RH': '#8B5CF6',
        'Direction': '#F59E0B',
        'Autre': '#6B7280'
    }
    
    for dept, dept_persons in departments.items():
        labels.append(dept)
        parents.append('Organisation')
        values.append(len(dept_persons))
        colors.append(dept_colors.get(dept, '#6B7280'))
        
        # Ajouter les personnes
        for person in dept_persons:
            labels.append(person.get('name', 'Inconnu'))
            parents.append(dept)
            values.append(1)
            colors.append(dept_colors.get(dept, '#6B7280'))
    
    fig = go.Figure(go.Treemap(
        labels=labels,
        parents=parents,
        values=values,
        marker=dict(colors=colors),
        textinfo='label+value',
        hovertemplate='<b>%{label}</b><br>Effectif: %{value}<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(
            text='🏢 Structure Organisationnelle - Treemap',
            font=dict(size=20)
        ),
        margin=dict(l=10, r=10, t=60, b=10),
        height=500
    )
    
    return fig


# ============================================
# COMPOSANT STREAMLIT PRINCIPAL
# ============================================

def render_org_chart_section():
    """
    Rendu de la section organigramme dans Streamlit
    """
    st.header("📊 Visualisations Organisationnelles")
    
    # Récupérer les données
    with st.spinner("Chargement des données..."):
        persons = api_get("/cartography/persons") or []
        teams = api_get("/cartography/teams") or []
        zones = api_get("/cartography/zones") or []
    
    if not persons and not zones:
        st.warning("⚠️ Aucune donnée disponible. Créez des données démo d'abord.")
        if st.button("🎮 Créer données démo"):
            result = requests.post(f"{API_BASE_URL}/cartography/demo/populate")
            if result.status_code == 200:
                st.success("✅ Données créées !")
                st.rerun()
        return
    
    # Tabs pour les différentes visualisations
    tab1, tab2, tab3, tab4 = st.tabs([
        "🏢 Organigramme", "📍 Zones de Risque", "🔗 Relations", "📊 Treemap"
    ])
    
    with tab1:
        st.subheader("Structure de Supervision")
        fig = create_org_chart(persons, teams)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Pas assez de données pour l'organigramme")
        
        # Légende
        st.markdown("""
        **Légende:**
        - 🔵 Production | 🟢 Maintenance | 🔴 Sécurité | 🟣 RH | 🟡 Direction
        - La taille des cercles représente le nombre de subordonnés
        """)
    
    with tab2:
        st.subheader("Niveaux de Risque par Zone")
        fig = create_risk_zone_map(zones)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Aucune zone définie")
        
        # Statistiques
        if zones:
            col1, col2, col3 = st.columns(3)
            critical = sum(1 for z in zones if z.get('risk_level', '').lower() in ['critique', 'élevé', 'eleve'])
            with col1:
                st.metric("⚠️ Zones à risque élevé/critique", critical)
            with col2:
                total_hazards = sum(len(z.get('hazards', [])) for z in zones)
                st.metric("🔴 Total dangers identifiés", total_hazards)
            with col3:
                total_controls = sum(len(z.get('controls', [])) for z in zones)
                st.metric("🛡️ Contrôles en place", total_controls)
    
    with tab3:
        st.subheader("Graphe des Relations")
        fig = create_relations_graph(persons, teams, zones)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Pas assez de données")
        
        st.markdown("""
        **Légende:**
        - ⚫ Personnes | ⬛ Équipes | ◆ Zones
        - Les lignes représentent les relations (appartenance, supervision)
        """)
    
    with tab4:
        st.subheader("Répartition par Département")
        fig = create_org_treemap(persons, teams)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Pas assez de données")


# ============================================
# STANDALONE
# ============================================

if __name__ == "__main__":
    st.set_page_config(
        page_title="EDGY Organigramme",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("📊 Organigramme Interactif EDGY")
    render_org_chart_section()
