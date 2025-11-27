"""
EDGY-AgenticX5 Dashboard v5.0 - Cartographie Macro (CORRIGÉ)
============================================================
Version corrigée avec Plotly (pas Highcharts) et syntaxe NiceGUI à jour

Auteur: Mario Genest - GenAISafety/Preventera
"""

from nicegui import ui
import httpx
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px

API_URL = "http://localhost:8000"

# ============================================================
# DONNÉES EXEMPLE - CARTOGRAPHIE MACRO
# ============================================================

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

SCIAN_BENCHMARKS = {
    "31-33": {"name": "Fabrication", "taux_freq": 42.3, "jours_moy": 145, "cout_moy": 67500},
    "23": {"name": "Construction", "taux_freq": 45.8, "jours_moy": 227, "cout_moy": 89420},
    "62": {"name": "Santé", "taux_freq": 28.4, "jours_moy": 156, "cout_moy": 67230},
    "48": {"name": "Transport", "taux_freq": 38.7, "jours_moy": 198, "cout_moy": 78940}
}

INCIDENT_TYPES = [
    {"type": "TMS", "count": 18, "color": "#ef4444"},
    {"type": "Brûlures", "count": 12, "color": "#f97316"},
    {"type": "Coupures", "count": 8, "color": "#eab308"},
    {"type": "Chutes", "count": 5, "color": "#22c55e"},
    {"type": "Autres", "count": 4, "color": "#3b82f6"}
]

# ============================================================
# STYLES
# ============================================================

HEADER_STYLE = "background: linear-gradient(135deg, #1e3a5f 0%, #2d5a87 100%);"

def get_risk_color(risk_level: str) -> str:
    colors = {
        "critique": "#dc2626",
        "eleve": "#ea580c",
        "moyen": "#ca8a04",
        "faible": "#16a34a"
    }
    return colors.get(risk_level.lower(), "#3b82f6")

def get_risk_bg(risk_level: str) -> str:
    styles = {
        "critique": "background: linear-gradient(135deg, #dc2626 0%, #ef4444 100%); color: white; border-radius: 12px; padding: 15px;",
        "eleve": "background: linear-gradient(135deg, #ea580c 0%, #f97316 100%); color: white; border-radius: 12px; padding: 15px;",
        "moyen": "background: linear-gradient(135deg, #ca8a04 0%, #eab308 100%); color: white; border-radius: 12px; padding: 15px;",
        "faible": "background: linear-gradient(135deg, #16a34a 0%, #22c55e 100%); color: white; border-radius: 12px; padding: 15px;"
    }
    return styles.get(risk_level.lower(), "background: #3b82f6; color: white; border-radius: 12px; padding: 15px;")

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
# GRAPHIQUES PLOTLY
# ============================================================

def create_sunburst_plotly(data):
    """Crée le Sunburst avec Plotly"""
    ids = ["Entreprise"]
    labels = [data["name"]]
    parents = [""]
    values = [sum(d["incidents_2024"] for d in data["departments"])]
    colors = ["#1e3a5f"]
    
    for dept in data["departments"]:
        dept_id = dept["name"]
        ids.append(dept_id)
        labels.append(f"{dept['name']} ({dept['incidents_2024']})")
        parents.append("Entreprise")
        values.append(dept["incidents_2024"])
        colors.append(get_risk_color(dept["risk_level"]))
        
        for team in dept["teams"]:
            team_id = f"{dept['name']}-{team['name']}"
            ids.append(team_id)
            labels.append(f"{team['name']} ({team['incidents']})")
            parents.append(dept_id)
            values.append(max(team["incidents"], 1))
            colors.append(get_risk_color(team["risk"]))
    
    fig = go.Figure(go.Sunburst(
        ids=ids,
        labels=labels,
        parents=parents,
        values=values,
        marker=dict(colors=colors),
        branchvalues="total",
        hovertemplate="<b>%{label}</b><br>Incidents: %{value}<extra></extra>"
    ))
    
    fig.update_layout(
        title="Cartographie Macro des Incidents",
        height=500,
        margin=dict(t=50, l=0, r=0, b=0)
    )
    
    return fig

def create_pie_types():
    """Pie chart des types d'incidents"""
    fig = go.Figure(go.Pie(
        labels=[t["type"] for t in INCIDENT_TYPES],
        values=[t["count"] for t in INCIDENT_TYPES],
        marker=dict(colors=[t["color"] for t in INCIDENT_TYPES]),
        hole=0.4,
        textinfo="label+percent"
    ))
    
    fig.update_layout(
        title="Répartition par Type d'Incident",
        height=350,
        showlegend=True
    )
    
    return fig

def create_bar_comparison(data):
    """Bar chart comparaison 2023 vs 2024"""
    departments = [d["name"] for d in data["departments"]]
    incidents_2023 = [d["incidents_2023"] for d in data["departments"]]
    incidents_2024 = [d["incidents_2024"] for d in data["departments"]]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name="2023",
        x=departments,
        y=incidents_2023,
        marker_color="#94a3b8",
        text=incidents_2023,
        textposition="outside"
    ))
    
    fig.add_trace(go.Bar(
        name="2024",
        x=departments,
        y=incidents_2024,
        marker_color="#3b82f6",
        text=incidents_2024,
        textposition="outside"
    ))
    
    fig.update_layout(
        title="Évolution des Incidents 2023 vs 2024",
        barmode="group",
        height=350,
        xaxis_title="Département",
        yaxis_title="Nombre d'incidents"
    )
    
    return fig

def create_treemap_plotly(data):
    """Treemap avec Plotly"""
    ids = []
    labels = []
    parents = []
    values = []
    colors = []
    
    # Root
    ids.append("root")
    labels.append(data["name"])
    parents.append("")
    values.append(0)
    colors.append("#1e3a5f")
    
    for dept in data["departments"]:
        ids.append(dept["id"])
        labels.append(f"{dept['name']}<br>{dept['incidents_2024']} inc.")
        parents.append("root")
        values.append(dept["incidents_2024"])
        colors.append(get_risk_color(dept["risk_level"]))
        
        for team in dept["teams"]:
            team_id = f"{dept['id']}_{team['name']}"
            ids.append(team_id)
            labels.append(f"{team['name']}<br>{team['incidents']} inc.")
            parents.append(dept["id"])
            values.append(max(team["incidents"], 1))
            colors.append(get_risk_color(team["risk"]))
    
    fig = go.Figure(go.Treemap(
        ids=ids,
        labels=labels,
        parents=parents,
        values=values,
        marker=dict(colors=colors),
        textinfo="label",
        hovertemplate="<b>%{label}</b><extra></extra>"
    ))
    
    fig.update_layout(
        title="Treemap des Incidents par Zone",
        height=400,
        margin=dict(t=50, l=0, r=0, b=0)
    )
    
    return fig

# ============================================================
# PAGE PRINCIPALE
# ============================================================

@ui.page("/")
async def main_page():
    # En-tête
    with ui.header().classes("text-white p-4").style(HEADER_STYLE):
        with ui.row().classes("w-full items-center justify-between"):
            with ui.row().classes("items-center gap-4"):
                ui.icon("map").classes("text-3xl")
                ui.label("EDGY-AgenticX5").classes("text-2xl font-bold")
                ui.badge("v5.0 Cartographie Macro").props("color=green")
            
            with ui.row().classes("gap-2"):
                ui.button("CNESST", on_click=lambda: ui.navigate.to("/cnesst")).props("flat color=white")
                ui.button("Actualiser", on_click=lambda: ui.navigate.to("/")).props("flat color=white")
    
    with ui.column().classes("w-full p-6 gap-6"):
        
        # Titre
        ui.label("🗺️ Cartographie Macro des Risques SST").classes("text-3xl font-bold text-blue-900")
        ui.label("Visualisation hiérarchique des incidents par département et équipe").classes("text-lg text-gray-600")
        
        # ============================================================
        # FILTRES
        # ============================================================
        
        with ui.card().classes("w-full"):
            ui.label("🔍 Filtres").classes("text-xl font-bold mb-4")
            with ui.row().classes("gap-4 flex-wrap"):
                with ui.column():
                    ui.label("Département").classes("text-sm text-gray-600")
                    dept_options = ["Tous"] + [d["name"] for d in ENTERPRISE_DATA["departments"]]
                    ui.select(dept_options, value="Tous").classes("w-48")
                
                with ui.column():
                    ui.label("Secteur SCIAN").classes("text-sm text-gray-600")
                    scian_options = [f"{k} - {v['name']}" for k, v in SCIAN_BENCHMARKS.items()]
                    ui.select(scian_options, value="31-33 - Fabrication").classes("w-56")
                
                with ui.column():
                    ui.label("Période").classes("text-sm text-gray-600")
                    ui.select(["2024", "2023", "2022"], value="2024").classes("w-32")
        
        # ============================================================
        # KPIs
        # ============================================================
        
        total_incidents = sum(d["incidents_2024"] for d in ENTERPRISE_DATA["departments"])
        total_cost = sum(d["cost_total"] for d in ENTERPRISE_DATA["departments"])
        total_days = sum(d["days_lost"] for d in ENTERPRISE_DATA["departments"])
        taux_freq = (total_incidents / ENTERPRISE_DATA["total_employees"]) * 100
        
        with ui.row().classes("w-full gap-4 flex-wrap"):
            with ui.card().style("background: linear-gradient(135deg, #2563eb 0%, #3b82f6 100%); color: white; border-radius: 12px; padding: 20px;"):
                ui.icon("warning").classes("text-3xl")
                ui.label(str(total_incidents)).classes("text-3xl font-bold")
                ui.label("Incidents 2024").classes("text-sm opacity-80")
            
            with ui.card().style("background: linear-gradient(135deg, #ea580c 0%, #f97316 100%); color: white; border-radius: 12px; padding: 20px;"):
                ui.icon("attach_money").classes("text-3xl")
                ui.label(f"{total_cost:,}$").classes("text-3xl font-bold")
                ui.label("Coûts totaux").classes("text-sm opacity-80")
            
            with ui.card().style("background: linear-gradient(135deg, #ca8a04 0%, #eab308 100%); color: white; border-radius: 12px; padding: 20px;"):
                ui.icon("event_busy").classes("text-3xl")
                ui.label(str(total_days)).classes("text-3xl font-bold")
                ui.label("Jours perdus").classes("text-sm opacity-80")
            
            benchmark = SCIAN_BENCHMARKS["31-33"]["taux_freq"]
            card_style = "background: linear-gradient(135deg, #16a34a 0%, #22c55e 100%); color: white; border-radius: 12px; padding: 20px;" if taux_freq < benchmark else "background: linear-gradient(135deg, #dc2626 0%, #ef4444 100%); color: white; border-radius: 12px; padding: 20px;"
            with ui.card().style(card_style):
                ui.icon("speed").classes("text-3xl")
                ui.label(f"{taux_freq:.1f}").classes("text-3xl font-bold")
                ui.label(f"Taux fréq. (bench: {benchmark})").classes("text-sm opacity-80")
        
        # ============================================================
        # SUNBURST + LÉGENDE
        # ============================================================
        
        ui.separator()
        ui.label("📊 Cartographie Hiérarchique").classes("text-2xl font-bold text-blue-800")
        
        with ui.row().classes("w-full gap-6"):
            with ui.card().classes("flex-1"):
                fig_sunburst = create_sunburst_plotly(ENTERPRISE_DATA)
                ui.plotly(fig_sunburst).classes("w-full")
            
            with ui.card().classes("w-80"):
                ui.label("🎯 Légende des risques").classes("text-lg font-bold mb-4")
                
                with ui.column().classes("gap-3"):
                    with ui.row().classes("items-center gap-2"):
                        ui.element("div").style("width:20px;height:20px;background:#dc2626;border-radius:4px;")
                        ui.label("Critique - Action immédiate")
                    with ui.row().classes("items-center gap-2"):
                        ui.element("div").style("width:20px;height:20px;background:#ea580c;border-radius:4px;")
                        ui.label("Élevé - Priorité haute")
                    with ui.row().classes("items-center gap-2"):
                        ui.element("div").style("width:20px;height:20px;background:#ca8a04;border-radius:4px;")
                        ui.label("Moyen - À surveiller")
                    with ui.row().classes("items-center gap-2"):
                        ui.element("div").style("width:20px;height:20px;background:#16a34a;border-radius:4px;")
                        ui.label("Faible - Sous contrôle")
                
                ui.separator()
                ui.label("💡 Insights").classes("text-lg font-bold mt-4 mb-2")
                
                max_dept = max(ENTERPRISE_DATA["departments"], key=lambda d: d["incidents_2024"])
                with ui.column().classes("gap-2 text-sm"):
                    ui.label(f"⚠️ {max_dept['name']}: {max_dept['incidents_2024']} incidents ({max_dept['incidents_2024']/total_incidents*100:.0f}%)").classes("text-red-700")
                    prev_total = sum(d['incidents_2023'] for d in ENTERPRISE_DATA['departments'])
                    change = ((total_incidents/prev_total)-1)*100
                    ui.label(f"📈 {'Hausse' if change > 0 else 'Baisse'} de {abs(change):.1f}% vs 2023").classes("text-orange-700")
                    ui.label(f"💰 Coût moyen: {total_cost//total_incidents:,}$/incident").classes("text-blue-700")
        
        # ============================================================
        # DÉPARTEMENTS
        # ============================================================
        
        ui.separator()
        ui.label("🏢 Détail par Département").classes("text-2xl font-bold text-blue-800")
        
        with ui.row().classes("w-full gap-4 flex-wrap"):
            for dept in ENTERPRISE_DATA["departments"]:
                with ui.card().classes("w-72").style(get_risk_bg(dept["risk_level"])):
                    with ui.row().classes("justify-between items-center"):
                        ui.label(dept["name"]).classes("text-xl font-bold")
                        ui.badge(dept["risk_level"].upper()).props("color=white outline")
                    
                    ui.separator().classes("my-2 bg-white/30")
                    
                    ui.label(f"👥 {dept['employees']} employés").classes("text-sm")
                    ui.label(f"⚠️ {dept['incidents_2024']} incidents").classes("text-sm")
                    ui.label(f"💰 {dept['cost_total']:,}$").classes("text-sm")
                    ui.label(f"📅 {dept['days_lost']} jours perdus").classes("text-sm")
                    
                    ui.separator().classes("my-2 bg-white/30")
                    ui.label("Équipes:").classes("text-sm font-bold")
                    for team in dept["teams"]:
                        icon = "🔴" if team["risk"] == "critique" else "🟠" if team["risk"] == "eleve" else "🟡" if team["risk"] == "moyen" else "🟢"
                        ui.label(f"{icon} {team['name']}: {team['incidents']} inc.").classes("text-xs")
        
        # ============================================================
        # GRAPHIQUES
        # ============================================================
        
        ui.separator()
        
        with ui.row().classes("w-full gap-6"):
            with ui.card().classes("flex-1"):
                fig_pie = create_pie_types()
                ui.plotly(fig_pie).classes("w-full")
            
            with ui.card().classes("flex-1"):
                fig_bar = create_bar_comparison(ENTERPRISE_DATA)
                ui.plotly(fig_bar).classes("w-full")
        
        # ============================================================
        # TREEMAP
        # ============================================================
        
        with ui.card().classes("w-full"):
            fig_tree = create_treemap_plotly(ENTERPRISE_DATA)
            ui.plotly(fig_tree).classes("w-full")
        
        # ============================================================
        # BENCHMARKS CNESST
        # ============================================================
        
        ui.separator()
        ui.label("📊 Benchmarks CNESST Québec").classes("text-2xl font-bold text-green-800")
        
        cnesst_data = await fetch_cnesst_summary()
        
        if cnesst_data and cnesst_data.get("total_incidents", 0) > 0:
            with ui.card().classes("w-full bg-green-50"):
                with ui.row().classes("justify-between items-center mb-4"):
                    ui.label(f"📈 Base: {cnesst_data.get('total_incidents', 0):,} incidents CNESST").classes("text-xl font-bold text-green-800")
                    ui.badge("2017-2023").props("color=green")
                
                benchmark = SCIAN_BENCHMARKS["31-33"]
                columns = [
                    {"name": "metric", "label": "Métrique", "field": "metric"},
                    {"name": "enterprise", "label": "Votre entreprise", "field": "enterprise"},
                    {"name": "sector", "label": "Secteur (31-33)", "field": "sector"},
                    {"name": "status", "label": "Statut", "field": "status"}
                ]
                rows = [
                    {"metric": "Taux de fréquence", "enterprise": f"{taux_freq:.1f}", "sector": f"{benchmark['taux_freq']}", "status": "✅ Meilleur" if taux_freq < benchmark["taux_freq"] else "⚠️ À améliorer"},
                    {"metric": "Jours moyens perdus", "enterprise": f"{total_days/total_incidents:.0f}", "sector": f"{benchmark['jours_moy']}", "status": "✅ Meilleur" if total_days/total_incidents < benchmark["jours_moy"] else "⚠️ À améliorer"},
                    {"metric": "Coût moyen/incident", "enterprise": f"{total_cost//total_incidents:,}$", "sector": f"{benchmark['cout_moy']:,}$", "status": "✅ Meilleur" if total_cost/total_incidents < benchmark["cout_moy"] else "⚠️ À améliorer"}
                ]
                ui.table(columns=columns, rows=rows).classes("w-full")
        else:
            ui.label("⚠️ API CNESST non disponible").classes("text-orange-600")
        
        # Footer
        ui.separator()
        with ui.row().classes("w-full justify-between text-gray-500"):
            ui.label("© 2025 GenAISafety/Preventera - Mario Genest")
            ui.label(f"Mis à jour: {datetime.now().strftime('%Y-%m-%d %H:%M')}")


# ============================================================
# PAGE CNESST
# ============================================================

@ui.page("/cnesst")
async def cnesst_page():
    with ui.header().classes("bg-green-800 text-white p-4"):
        with ui.row().classes("w-full items-center justify-between"):
            ui.label("📊 Données CNESST").classes("text-2xl font-bold")
            ui.button("← Retour", on_click=lambda: ui.navigate.to("/")).props("flat color=white")
    
    with ui.column().classes("w-full p-6"):
        cnesst_data = await fetch_cnesst_summary()
        
        if cnesst_data:
            ui.label(f"Total: {cnesst_data.get('total_incidents', 0):,} incidents").classes("text-3xl font-bold text-green-800")
            
            if "by_year" in cnesst_data:
                columns = [
                    {"name": "year", "label": "Année", "field": "year"},
                    {"name": "incidents", "label": "Incidents", "field": "incidents"},
                    {"name": "size", "label": "Taille (Mo)", "field": "size"}
                ]
                rows = [{"year": y["year"], "incidents": f"{y['incidents']:,}", "size": f"{y['size_mb']:.1f}"} for y in cnesst_data["by_year"]]
                ui.table(columns=columns, rows=rows).classes("w-full mt-4")


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
