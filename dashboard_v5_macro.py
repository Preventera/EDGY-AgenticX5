"""
EDGY-AgenticX5 Dashboard v5.0 - Cartographie Macro
===================================================
Intégration Cartographie Organisationnelle + Incidents CNESST
Visualisation Sunburst multi-niveaux avec filtres

Auteur: Mario Genest - GenAISafety/Preventera
"""

from nicegui import ui
import httpx
from datetime import datetime
from typing import Dict, List, Optional

API_URL = "http://localhost:8000"

# ============================================================
# DONNÉES EXEMPLE - CARTOGRAPHIE MACRO
# ============================================================

# Simulation d'une entreprise avec incidents mappés
ENTERPRISE_DATA = {
    "name": "Manufacturier ABC Inc.",
    "sector_scian": "31-33",
    "total_employees": 150,
    "departments": [
        {
            "id": "prod",
            "name": "Production",
            "employees": 80,
            "risk_level": "eleve",
            "incidents_2024": 32,
            "incidents_2023": 28,
            "cost_total": 245000,
            "days_lost": 156,
            "teams": [
                {"name": "Soudure", "employees": 25, "incidents": 18, "risk": "critique", "top_risk": "Brûlures"},
                {"name": "Assemblage", "employees": 30, "incidents": 14, "risk": "eleve", "top_risk": "TMS"},
                {"name": "Finition", "employees": 25, "incidents": 0, "risk": "faible", "top_risk": "-"}
            ]
        },
        {
            "id": "maint",
            "name": "Maintenance",
            "employees": 25,
            "risk_level": "moyen",
            "incidents_2024": 9,
            "incidents_2023": 11,
            "cost_total": 67000,
            "days_lost": 42,
            "teams": [
                {"name": "Électrique", "employees": 10, "incidents": 5, "risk": "eleve", "top_risk": "Électrocution"},
                {"name": "Mécanique", "employees": 15, "incidents": 4, "risk": "moyen", "top_risk": "Coupures"}
            ]
        },
        {
            "id": "qual",
            "name": "Qualité",
            "employees": 20,
            "risk_level": "faible",
            "incidents_2024": 4,
            "incidents_2023": 3,
            "cost_total": 12000,
            "days_lost": 8,
            "teams": [
                {"name": "Contrôle", "employees": 12, "incidents": 2, "risk": "faible", "top_risk": "Chutes"},
                {"name": "Laboratoire", "employees": 8, "incidents": 2, "risk": "moyen", "top_risk": "Chimique"}
            ]
        },
        {
            "id": "admin",
            "name": "Administration",
            "employees": 25,
            "risk_level": "faible",
            "incidents_2024": 2,
            "incidents_2023": 1,
            "cost_total": 3500,
            "days_lost": 3,
            "teams": [
                {"name": "Bureau", "employees": 20, "incidents": 1, "risk": "faible", "top_risk": "Ergonomie"},
                {"name": "Réception", "employees": 5, "incidents": 1, "risk": "faible", "top_risk": "Chutes"}
            ]
        }
    ]
}

# Benchmarks CNESST par secteur SCIAN
SCIAN_BENCHMARKS = {
    "31-33": {"name": "Fabrication", "taux_freq": 42.3, "jours_moy": 145, "cout_moy": 67500},
    "23": {"name": "Construction", "taux_freq": 45.8, "jours_moy": 227, "cout_moy": 89420},
    "62": {"name": "Santé", "taux_freq": 28.4, "jours_moy": 156, "cout_moy": 67230},
    "48": {"name": "Transport", "taux_freq": 38.7, "jours_moy": 198, "cout_moy": 78940}
}

# Types d'incidents CNESST
INCIDENT_TYPES = [
    {"type": "TMS (Troubles musculo-squelettiques)", "count": 18, "pct": 38.3, "color": "#ef4444"},
    {"type": "Brûlures", "count": 12, "pct": 25.5, "color": "#f97316"},
    {"type": "Coupures/Lacérations", "count": 8, "pct": 17.0, "color": "#eab308"},
    {"type": "Chutes", "count": 5, "pct": 10.6, "color": "#22c55e"},
    {"type": "Autres", "count": 4, "pct": 8.5, "color": "#3b82f6"}
]

# ============================================================
# STYLES
# ============================================================

HEADER_STYLE = "background: linear-gradient(135deg, #1e3a5f 0%, #2d5a87 100%);"

CARD_CRITIQUE = """
    background: linear-gradient(135deg, #dc2626 0%, #ef4444 100%);
    border-radius: 12px; padding: 20px; color: white;
"""
CARD_ELEVE = """
    background: linear-gradient(135deg, #ea580c 0%, #f97316 100%);
    border-radius: 12px; padding: 20px; color: white;
"""
CARD_MOYEN = """
    background: linear-gradient(135deg, #ca8a04 0%, #eab308 100%);
    border-radius: 12px; padding: 20px; color: white;
"""
CARD_FAIBLE = """
    background: linear-gradient(135deg, #16a34a 0%, #22c55e 100%);
    border-radius: 12px; padding: 20px; color: white;
"""
CARD_INFO = """
    background: linear-gradient(135deg, #2563eb 0%, #3b82f6 100%);
    border-radius: 12px; padding: 20px; color: white;
"""

def get_risk_style(risk_level: str) -> str:
    styles = {
        "critique": CARD_CRITIQUE,
        "eleve": CARD_ELEVE,
        "moyen": CARD_MOYEN,
        "faible": CARD_FAIBLE
    }
    return styles.get(risk_level.lower(), CARD_INFO)

def get_risk_color(risk_level: str) -> str:
    colors = {
        "critique": "#dc2626",
        "eleve": "#ea580c",
        "moyen": "#ca8a04",
        "faible": "#16a34a"
    }
    return colors.get(risk_level.lower(), "#3b82f6")

# ============================================================
# FONCTIONS API
# ============================================================

async def fetch_cnesst_summary():
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{API_URL}/cnesst/summary")
            if response.status_code == 200:
                return response.json()
    except Exception as e:
        print(f"Erreur API: {e}")
    return None

# ============================================================
# COMPOSANTS GRAPHIQUES
# ============================================================

def create_sunburst_chart(data: Dict):
    """Crée le graphique Sunburst de la cartographie macro"""
    
    # Construire les données pour Highcharts Sunburst
    chart_data = []
    
    # Niveau 0: Entreprise (centre)
    enterprise_total = sum(d["incidents_2024"] for d in data["departments"])
    chart_data.append({
        "id": "enterprise",
        "name": data["name"],
        "value": enterprise_total,
        "color": "#1e3a5f"
    })
    
    # Niveau 1: Départements
    for dept in data["departments"]:
        dept_color = get_risk_color(dept["risk_level"])
        chart_data.append({
            "id": dept["id"],
            "name": dept["name"],
            "parent": "enterprise",
            "value": dept["incidents_2024"],
            "color": dept_color
        })
        
        # Niveau 2: Équipes
        for team in dept["teams"]:
            team_color = get_risk_color(team["risk"])
            chart_data.append({
                "id": f"{dept['id']}_{team['name']}",
                "name": team["name"],
                "parent": dept["id"],
                "value": max(team["incidents"], 1),  # Min 1 pour visibilité
                "color": team_color
            })
    
    chart_options = {
        "chart": {
            "type": "sunburst",
            "height": 500
        },
        "title": {
            "text": "Cartographie Macro des Incidents par Département"
        },
        "subtitle": {
            "text": "Cliquez pour explorer les niveaux"
        },
        "series": [{
            "type": "sunburst",
            "data": chart_data,
            "allowTraversingTree": True,
            "cursor": "pointer",
            "dataLabels": {
                "format": "{point.name}",
                "filter": {
                    "property": "innerArcLength",
                    "operator": ">",
                    "value": 16
                }
            },
            "levels": [
                {"level": 1, "colorByPoint": True},
                {"level": 2, "colorVariation": {"key": "brightness", "to": 0.5}},
                {"level": 3, "colorVariation": {"key": "brightness", "to": -0.5}}
            ]
        }],
        "tooltip": {
            "headerFormat": "",
            "pointFormat": "<b>{point.name}</b>: {point.value} incidents"
        }
    }
    
    ui.highchart(chart_options).classes("w-full")


def create_treemap_chart(data: Dict):
    """Crée le Treemap alternatif"""
    
    chart_data = []
    
    for dept in data["departments"]:
        # Département
        chart_data.append({
            "id": dept["id"],
            "name": f"{dept['name']} ({dept['incidents_2024']} inc.)",
            "color": get_risk_color(dept["risk_level"])
        })
        
        # Équipes
        for team in dept["teams"]:
            chart_data.append({
                "name": team["name"],
                "parent": dept["id"],
                "value": max(team["incidents"], 1),
                "color": get_risk_color(team["risk"])
            })
    
    chart_options = {
        "chart": {"type": "treemap", "height": 400},
        "title": {"text": "Répartition des Incidents par Zone"},
        "series": [{
            "type": "treemap",
            "layoutAlgorithm": "squarified",
            "allowDrillToNode": True,
            "dataLabels": {
                "enabled": True,
                "format": "{point.name}"
            },
            "levels": [{
                "level": 1,
                "dataLabels": {"enabled": True},
                "borderWidth": 3
            }],
            "data": chart_data
        }],
        "tooltip": {
            "pointFormat": "<b>{point.name}</b><br>Incidents: {point.value}"
        }
    }
    
    ui.highchart(chart_options).classes("w-full")


def create_incidents_by_type_chart():
    """Graphique des types d'incidents"""
    
    chart_options = {
        "chart": {"type": "pie", "height": 350},
        "title": {"text": "Répartition par Type d'Incident"},
        "plotOptions": {
            "pie": {
                "allowPointSelect": True,
                "cursor": "pointer",
                "dataLabels": {
                    "enabled": True,
                    "format": "{point.name}: {point.percentage:.1f}%"
                }
            }
        },
        "series": [{
            "name": "Incidents",
            "data": [
                {"name": t["type"], "y": t["count"], "color": t["color"]}
                for t in INCIDENT_TYPES
            ]
        }]
    }
    
    ui.highchart(chart_options).classes("w-full")


def create_trend_chart(data: Dict):
    """Graphique de tendance par département"""
    
    departments = [d["name"] for d in data["departments"]]
    incidents_2023 = [d["incidents_2023"] for d in data["departments"]]
    incidents_2024 = [d["incidents_2024"] for d in data["departments"]]
    
    chart_options = {
        "chart": {"type": "column", "height": 350},
        "title": {"text": "Évolution des Incidents 2023 vs 2024"},
        "xAxis": {"categories": departments},
        "yAxis": {"title": {"text": "Nombre d'incidents"}},
        "series": [
            {"name": "2023", "data": incidents_2023, "color": "#94a3b8"},
            {"name": "2024", "data": incidents_2024, "color": "#3b82f6"}
        ],
        "plotOptions": {
            "column": {
                "dataLabels": {"enabled": True}
            }
        }
    }
    
    ui.highchart(chart_options).classes("w-full")


# ============================================================
# PAGE PRINCIPALE - CARTOGRAPHIE MACRO
# ============================================================

@ui.page("/")
async def main_page():
    # Variables d'état pour les filtres
    selected_dept = {"value": "all"}
    selected_period = {"value": "2024"}
    
    # En-tête
    with ui.header().classes("text-white p-4").style(HEADER_STYLE):
        with ui.row().classes("w-full items-center justify-between"):
            with ui.row().classes("items-center gap-4"):
                ui.icon("map").classes("text-3xl")
                ui.label("EDGY-AgenticX5").classes("text-2xl font-bold")
                ui.badge("v5.0 Cartographie Macro").props("color=green")
            
            with ui.row().classes("gap-2"):
                ui.button("Données CNESST", on_click=lambda: ui.navigate.to("/cnesst")).props("flat color=white")
                ui.button("Actualiser", on_click=lambda: ui.navigate.to("/")).props("flat color=white")
    
    # Contenu principal
    with ui.column().classes("w-full p-6 gap-6"):
        
        # Titre et description
        ui.label("🗺️ Cartographie Macro des Risques SST").classes("text-3xl font-bold text-blue-900")
        ui.label("Visualisation hiérarchique des incidents par département, équipe et zone").classes("text-lg text-gray-600")
        
        # ============================================================
        # SECTION FILTRES
        # ============================================================
        
        with ui.card().classes("w-full"):
            ui.label("🔍 Filtres de visualisation").classes("text-xl font-bold mb-4")
            
            with ui.row().classes("gap-4 flex-wrap"):
                # Filtre département
                with ui.column():
                    ui.label("Département").classes("text-sm text-gray-600")
                    dept_options = ["Tous"] + [d["name"] for d in ENTERPRISE_DATA["departments"]]
                    ui.select(dept_options, value="Tous").classes("w-48")
                
                # Filtre secteur SCIAN
                with ui.column():
                    ui.label("Secteur SCIAN").classes("text-sm text-gray-600")
                    scian_options = [f"{k} - {v['name']}" for k, v in SCIAN_BENCHMARKS.items()]
                    ui.select(scian_options, value="31-33 - Fabrication").classes("w-56")
                
                # Filtre période
                with ui.column():
                    ui.label("Période").classes("text-sm text-gray-600")
                    ui.select(["2024", "2023", "2022", "Tout"], value="2024").classes("w-32")
                
                # Filtre type d'incident
                with ui.column():
                    ui.label("Type d'incident").classes("text-sm text-gray-600")
                    type_options = ["Tous"] + [t["type"] for t in INCIDENT_TYPES]
                    ui.select(type_options, value="Tous").classes("w-64")
        
        # ============================================================
        # KPIs GLOBAUX
        # ============================================================
        
        total_incidents = sum(d["incidents_2024"] for d in ENTERPRISE_DATA["departments"])
        total_cost = sum(d["cost_total"] for d in ENTERPRISE_DATA["departments"])
        total_days = sum(d["days_lost"] for d in ENTERPRISE_DATA["departments"])
        
        with ui.row().classes("w-full gap-4 flex-wrap"):
            # Total incidents
            with ui.card().style(CARD_INFO):
                ui.icon("warning").classes("text-3xl")
                ui.label(str(total_incidents)).classes("text-3xl font-bold")
                ui.label("Incidents 2024").classes("text-sm opacity-80")
            
            # Coût total
            with ui.card().style(CARD_ELEVE):
                ui.icon("attach_money").classes("text-3xl")
                ui.label(f"{total_cost:,}$").classes("text-3xl font-bold")
                ui.label("Coûts totaux").classes("text-sm opacity-80")
            
            # Jours perdus
            with ui.card().style(CARD_MOYEN):
                ui.icon("event_busy").classes("text-3xl")
                ui.label(str(total_days)).classes("text-3xl font-bold")
                ui.label("Jours perdus").classes("text-sm opacity-80")
            
            # Taux de fréquence
            taux_freq = (total_incidents / ENTERPRISE_DATA["total_employees"]) * 100
            benchmark = SCIAN_BENCHMARKS["31-33"]["taux_freq"]
            with ui.card().style(CARD_FAIBLE if taux_freq < benchmark else CARD_CRITIQUE):
                ui.icon("speed").classes("text-3xl")
                ui.label(f"{taux_freq:.1f}").classes("text-3xl font-bold")
                ui.label(f"Taux fréq. (bench: {benchmark})").classes("text-sm opacity-80")
        
        # ============================================================
        # CARTOGRAPHIE SUNBURST
        # ============================================================
        
        ui.separator()
        ui.label("📊 Cartographie Hiérarchique des Incidents").classes("text-2xl font-bold text-blue-800")
        
        with ui.row().classes("w-full gap-6"):
            # Sunburst principal
            with ui.card().classes("flex-1"):
                create_sunburst_chart(ENTERPRISE_DATA)
            
            # Légende et insights
            with ui.card().classes("w-80"):
                ui.label("🎯 Légende des risques").classes("text-lg font-bold mb-4")
                
                with ui.column().classes("gap-2"):
                    with ui.row().classes("items-center gap-2"):
                        ui.html('<div style="width:20px;height:20px;background:#dc2626;border-radius:4px;"></div>')
                        ui.label("Critique - Action immédiate")
                    with ui.row().classes("items-center gap-2"):
                        ui.html('<div style="width:20px;height:20px;background:#ea580c;border-radius:4px;"></div>')
                        ui.label("Élevé - Priorité haute")
                    with ui.row().classes("items-center gap-2"):
                        ui.html('<div style="width:20px;height:20px;background:#ca8a04;border-radius:4px;"></div>')
                        ui.label("Moyen - À surveiller")
                    with ui.row().classes("items-center gap-2"):
                        ui.html('<div style="width:20px;height:20px;background:#16a34a;border-radius:4px;"></div>')
                        ui.label("Faible - Sous contrôle")
                
                ui.separator()
                
                ui.label("💡 Insights clés").classes("text-lg font-bold mt-4 mb-2")
                
                # Calculer le département le plus à risque
                max_dept = max(ENTERPRISE_DATA["departments"], key=lambda d: d["incidents_2024"])
                
                with ui.column().classes("gap-2 text-sm"):
                    ui.label(f"⚠️ {max_dept['name']} concentre {max_dept['incidents_2024']} incidents ({max_dept['incidents_2024']/total_incidents*100:.0f}%)").classes("text-red-700")
                    ui.label(f"📈 Hausse de {((total_incidents/sum(d['incidents_2023'] for d in ENTERPRISE_DATA['departments']))-1)*100:.1f}% vs 2023").classes("text-orange-700")
                    ui.label(f"💰 Coût moyen: {total_cost//total_incidents:,}$/incident").classes("text-blue-700")
        
        # ============================================================
        # DÉTAIL PAR DÉPARTEMENT
        # ============================================================
        
        ui.separator()
        ui.label("🏢 Détail par Département").classes("text-2xl font-bold text-blue-800")
        
        with ui.row().classes("w-full gap-4 flex-wrap"):
            for dept in ENTERPRISE_DATA["departments"]:
                with ui.card().classes("w-72").style(get_risk_style(dept["risk_level"])):
                    with ui.row().classes("justify-between items-center"):
                        ui.label(dept["name"]).classes("text-xl font-bold")
                        ui.badge(dept["risk_level"].upper()).props(f"color={'red' if dept['risk_level']=='critique' else 'orange' if dept['risk_level']=='eleve' else 'yellow' if dept['risk_level']=='moyen' else 'green'}")
                    
                    ui.separator().classes("my-2")
                    
                    with ui.column().classes("gap-1"):
                        ui.label(f"👥 {dept['employees']} employés").classes("text-sm")
                        ui.label(f"⚠️ {dept['incidents_2024']} incidents").classes("text-sm")
                        ui.label(f"💰 {dept['cost_total']:,}$").classes("text-sm")
                        ui.label(f"📅 {dept['days_lost']} jours perdus").classes("text-sm")
                    
                    ui.separator().classes("my-2")
                    
                    ui.label("Équipes:").classes("text-sm font-bold")
                    for team in dept["teams"]:
                        color = "🔴" if team["risk"] == "critique" else "🟠" if team["risk"] == "eleve" else "🟡" if team["risk"] == "moyen" else "🟢"
                        ui.label(f"  {color} {team['name']}: {team['incidents']} inc.").classes("text-xs")
        
        # ============================================================
        # GRAPHIQUES COMPLÉMENTAIRES
        # ============================================================
        
        ui.separator()
        
        with ui.row().classes("w-full gap-6"):
            with ui.card().classes("flex-1"):
                create_incidents_by_type_chart()
            
            with ui.card().classes("flex-1"):
                create_trend_chart(ENTERPRISE_DATA)
        
        # ============================================================
        # SECTION BENCHMARKS CNESST
        # ============================================================
        
        ui.separator()
        ui.label("📊 Benchmarks CNESST Québec").classes("text-2xl font-bold text-green-800")
        
        # Charger données CNESST
        cnesst_data = await fetch_cnesst_summary()
        
        if cnesst_data:
            with ui.card().classes("w-full bg-green-50"):
                with ui.row().classes("justify-between items-center"):
                    ui.label(f"📈 Base de référence: {cnesst_data.get('total_incidents', 0):,} incidents CNESST").classes("text-xl font-bold text-green-800")
                    ui.badge(f"2017-2023").props("color=green")
                
                ui.separator()
                
                # Tableau de comparaison
                columns = [
                    {"name": "metric", "label": "Métrique", "field": "metric"},
                    {"name": "enterprise", "label": "Votre entreprise", "field": "enterprise"},
                    {"name": "sector", "label": "Secteur (31-33)", "field": "sector"},
                    {"name": "status", "label": "Statut", "field": "status"}
                ]
                
                benchmark = SCIAN_BENCHMARKS["31-33"]
                rows = [
                    {
                        "metric": "Taux de fréquence",
                        "enterprise": f"{taux_freq:.1f}",
                        "sector": f"{benchmark['taux_freq']}",
                        "status": "✅ Meilleur" if taux_freq < benchmark["taux_freq"] else "⚠️ À améliorer"
                    },
                    {
                        "metric": "Jours moyens perdus",
                        "enterprise": f"{total_days/total_incidents:.0f}",
                        "sector": f"{benchmark['jours_moy']}",
                        "status": "✅ Meilleur" if total_days/total_incidents < benchmark["jours_moy"] else "⚠️ À améliorer"
                    },
                    {
                        "metric": "Coût moyen/incident",
                        "enterprise": f"{total_cost//total_incidents:,}$",
                        "sector": f"{benchmark['cout_moy']:,}$",
                        "status": "✅ Meilleur" if total_cost/total_incidents < benchmark["cout_moy"] else "⚠️ À améliorer"
                    }
                ]
                
                ui.table(columns=columns, rows=rows).classes("w-full")
        
        # ============================================================
        # FOOTER
        # ============================================================
        
        ui.separator()
        with ui.row().classes("w-full justify-between items-center text-gray-500"):
            ui.label("© 2025 GenAISafety/Preventera - Mario Genest")
            ui.label(f"Dernière mise à jour: {datetime.now().strftime('%Y-%m-%d %H:%M')}")


# ============================================================
# PAGE CNESST
# ============================================================

@ui.page("/cnesst")
async def cnesst_page():
    with ui.header().classes("bg-green-800 text-white p-4"):
        with ui.row().classes("w-full items-center justify-between"):
            with ui.row().classes("items-center gap-4"):
                ui.icon("assessment").classes("text-3xl")
                ui.label("Données CNESST").classes("text-2xl font-bold")
            ui.button("← Cartographie Macro", on_click=lambda: ui.navigate.to("/")).props("flat color=white")
    
    with ui.column().classes("w-full p-6"):
        ui.label("📊 Données CNESST - 793K+ incidents").classes("text-3xl font-bold")
        
        cnesst_data = await fetch_cnesst_summary()
        
        if cnesst_data:
            with ui.row().classes("gap-4"):
                with ui.card().classes("p-6 bg-green-100"):
                    ui.label(f"{cnesst_data.get('total_incidents', 0):,}").classes("text-4xl font-bold text-green-800")
                    ui.label("Total incidents").classes("text-gray-600")
                
                with ui.card().classes("p-6 bg-blue-100"):
                    ui.label(f"{cnesst_data.get('years_count', 0)}").classes("text-4xl font-bold text-blue-800")
                    ui.label("Années").classes("text-gray-600")
            
            # Tableau par année
            if "by_year" in cnesst_data:
                with ui.card().classes("w-full mt-6"):
                    ui.label("📅 Incidents par Année").classes("text-xl font-bold mb-4")
                    
                    columns = [
                        {"name": "year", "label": "Année", "field": "year"},
                        {"name": "incidents", "label": "Incidents", "field": "incidents"},
                        {"name": "size", "label": "Taille (Mo)", "field": "size"}
                    ]
                    rows = [
                        {"year": y["year"], "incidents": f"{y['incidents']:,}", "size": f"{y['size_mb']:.1f}"}
                        for y in cnesst_data["by_year"]
                    ]
                    ui.table(columns=columns, rows=rows).classes("w-full")


# ============================================================
# LANCEMENT
# ============================================================

if __name__ in {"__main__", "__mp_main__"}:
    print("\n" + "="*60)
    print("🗺️ EDGY-AgenticX5 Dashboard v5.0 - Cartographie Macro")
    print("="*60)
    print("📊 Dashboard: http://localhost:8003")
    print("📡 API requise: http://localhost:8000")
    print("="*60 + "\n")
    
    ui.run(
        title="EDGY-AgenticX5 Cartographie Macro",
        port=8003,
        reload=False,
        show=False
    )
