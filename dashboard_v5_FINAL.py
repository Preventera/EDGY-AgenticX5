"""
EDGY-AgenticX5 Dashboard v5.0 - Cartographie Macro BILINGUE
============================================================
Version FINALE avec:
- Toggle FR/EN
- 19 secteurs SCIAN
- Années 2017-2023
- Mention XAI et données CNESST
- Auteur: Mario Deshaies

Auteur: Mario Deshaies - GenAISafety/Preventera
"""

from nicegui import ui
import httpx
from datetime import datetime
import plotly.graph_objects as go

API_URL = "http://localhost:8000"

# Variable globale pour la langue
current_lang = {"value": "fr"}

# ============================================================
# DONNÉES EXEMPLE - CARTOGRAPHIE MACRO
# ============================================================

ENTERPRISE_DATA = {
    "name": "Manufacturier ABC Inc.",
    "name_en": "ABC Manufacturing Inc.",
    "sector_scian": "31-33",
    "total_employees": 150,
    "departments": [
        {
            "id": "prod",
            "name": "Production",
            "name_en": "Production",
            "employees": 80,
            "risk_level": "eleve",
            "incidents_2024": 32,
            "incidents_2023": 28,
            "cost_total": 245000,
            "days_lost": 156,
            "teams": [
                {"name": "Soudure", "name_en": "Welding", "employees": 25, "incidents": 18, "risk": "critique", "top_risk": "Brûlures"},
                {"name": "Assemblage", "name_en": "Assembly", "employees": 30, "incidents": 14, "risk": "eleve", "top_risk": "TMS"},
                {"name": "Finition", "name_en": "Finishing", "employees": 25, "incidents": 0, "risk": "faible", "top_risk": "-"}
            ]
        },
        {
            "id": "maint",
            "name": "Maintenance",
            "name_en": "Maintenance",
            "employees": 25,
            "risk_level": "moyen",
            "incidents_2024": 9,
            "incidents_2023": 11,
            "cost_total": 67000,
            "days_lost": 42,
            "teams": [
                {"name": "Électrique", "name_en": "Electrical", "employees": 10, "incidents": 5, "risk": "eleve", "top_risk": "Électrocution"},
                {"name": "Mécanique", "name_en": "Mechanical", "employees": 15, "incidents": 4, "risk": "moyen", "top_risk": "Coupures"}
            ]
        },
        {
            "id": "qual",
            "name": "Qualité",
            "name_en": "Quality",
            "employees": 20,
            "risk_level": "faible",
            "incidents_2024": 4,
            "incidents_2023": 3,
            "cost_total": 12000,
            "days_lost": 8,
            "teams": [
                {"name": "Contrôle", "name_en": "Control", "employees": 12, "incidents": 2, "risk": "faible", "top_risk": "Chutes"},
                {"name": "Laboratoire", "name_en": "Laboratory", "employees": 8, "incidents": 2, "risk": "moyen", "top_risk": "Chimique"}
            ]
        },
        {
            "id": "admin",
            "name": "Administration",
            "name_en": "Administration",
            "employees": 25,
            "risk_level": "faible",
            "incidents_2024": 2,
            "incidents_2023": 1,
            "cost_total": 3500,
            "days_lost": 3,
            "teams": [
                {"name": "Bureau", "name_en": "Office", "employees": 20, "incidents": 1, "risk": "faible", "top_risk": "Ergonomie"},
                {"name": "Réception", "name_en": "Reception", "employees": 5, "incidents": 1, "risk": "faible", "top_risk": "Chutes"}
            ]
        }
    ]
}

# 19 Secteurs SCIAN complets
SCIAN_BENCHMARKS = {
    "11": {"name": "Agriculture, foresterie", "name_en": "Agriculture, Forestry", "taux_freq": 52.1, "jours_moy": 185, "cout_moy": 72000},
    "21": {"name": "Extraction minière", "name_en": "Mining", "taux_freq": 48.5, "jours_moy": 210, "cout_moy": 95000},
    "22": {"name": "Services publics", "name_en": "Utilities", "taux_freq": 25.2, "jours_moy": 142, "cout_moy": 68000},
    "23": {"name": "Construction", "name_en": "Construction", "taux_freq": 45.8, "jours_moy": 227, "cout_moy": 89420},
    "31-33": {"name": "Fabrication", "name_en": "Manufacturing", "taux_freq": 42.3, "jours_moy": 145, "cout_moy": 67500},
    "41": {"name": "Commerce de gros", "name_en": "Wholesale Trade", "taux_freq": 28.5, "jours_moy": 98, "cout_moy": 45000},
    "44-45": {"name": "Commerce de détail", "name_en": "Retail Trade", "taux_freq": 22.1, "jours_moy": 85, "cout_moy": 38000},
    "48-49": {"name": "Transport, entreposage", "name_en": "Transportation", "taux_freq": 38.7, "jours_moy": 198, "cout_moy": 78940},
    "51": {"name": "Industrie information", "name_en": "Information Industry", "taux_freq": 12.3, "jours_moy": 45, "cout_moy": 25000},
    "52": {"name": "Finance, assurances", "name_en": "Finance, Insurance", "taux_freq": 8.5, "jours_moy": 32, "cout_moy": 18000},
    "53": {"name": "Services immobiliers", "name_en": "Real Estate", "taux_freq": 15.2, "jours_moy": 65, "cout_moy": 35000},
    "54": {"name": "Services professionnels", "name_en": "Professional Services", "taux_freq": 10.8, "jours_moy": 42, "cout_moy": 22000},
    "56": {"name": "Services administratifs", "name_en": "Administrative Services", "taux_freq": 32.4, "jours_moy": 125, "cout_moy": 52000},
    "61": {"name": "Services enseignement", "name_en": "Educational Services", "taux_freq": 18.6, "jours_moy": 78, "cout_moy": 42000},
    "62": {"name": "Soins de santé", "name_en": "Health Care", "taux_freq": 28.4, "jours_moy": 156, "cout_moy": 67230},
    "71": {"name": "Arts, spectacles", "name_en": "Arts, Entertainment", "taux_freq": 24.2, "jours_moy": 95, "cout_moy": 48000},
    "72": {"name": "Hébergement, restauration", "name_en": "Accommodation, Food", "taux_freq": 35.6, "jours_moy": 88, "cout_moy": 42000},
    "81": {"name": "Autres services", "name_en": "Other Services", "taux_freq": 29.8, "jours_moy": 112, "cout_moy": 55000},
    "91": {"name": "Admin. publiques", "name_en": "Public Administration", "taux_freq": 22.5, "jours_moy": 95, "cout_moy": 52000}
}

# Années disponibles CNESST
AVAILABLE_YEARS = ["2023", "2022", "2021", "2020", "2019", "2018", "2017"]

INCIDENT_TYPES = [
    {"type": "TMS", "type_en": "MSD", "count": 18, "color": "#ef4444"},
    {"type": "Brûlures", "type_en": "Burns", "count": 12, "color": "#f97316"},
    {"type": "Coupures", "type_en": "Cuts", "count": 8, "color": "#eab308"},
    {"type": "Chutes", "type_en": "Falls", "count": 5, "color": "#22c55e"},
    {"type": "Autres", "type_en": "Others", "count": 4, "color": "#3b82f6"}
]

# ============================================================
# STYLES
# ============================================================

HEADER_STYLE = "background: linear-gradient(135deg, #1e3a5f 0%, #2d5a87 100%);"

def get_risk_color(risk_level: str) -> str:
    colors = {"critique": "#dc2626", "eleve": "#ea580c", "moyen": "#ca8a04", "faible": "#16a34a"}
    return colors.get(risk_level.lower(), "#3b82f6")

def get_risk_bg(risk_level: str) -> str:
    styles = {
        "critique": "background: linear-gradient(135deg, #dc2626 0%, #ef4444 100%); color: white; border-radius: 12px; padding: 15px;",
        "eleve": "background: linear-gradient(135deg, #ea580c 0%, #f97316 100%); color: white; border-radius: 12px; padding: 15px;",
        "moyen": "background: linear-gradient(135deg, #ca8a04 0%, #eab308 100%); color: white; border-radius: 12px; padding: 15px;",
        "faible": "background: linear-gradient(135deg, #16a34a 0%, #22c55e 100%); color: white; border-radius: 12px; padding: 15px;"
    }
    return styles.get(risk_level.lower(), "background: #3b82f6; color: white;")

def get_risk_label(risk_level: str, lang: str) -> str:
    labels = {
        "fr": {"critique": "CRITIQUE", "eleve": "ÉLEVÉ", "moyen": "MOYEN", "faible": "FAIBLE"},
        "en": {"critique": "CRITICAL", "eleve": "HIGH", "moyen": "MEDIUM", "faible": "LOW"}
    }
    return labels[lang].get(risk_level.lower(), risk_level.upper())

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

def create_sunburst_plotly(data, lang):
    ids, labels, parents, values, colors = [], [], [], [], []
    name_key = "name_en" if lang == "en" else "name"
    
    for dept in data["departments"]:
        dept_total = sum(team["incidents"] for team in dept["teams"])
        dept_name = dept.get(name_key, dept["name"])
        
        ids.append(dept["id"])
        labels.append(f"{dept_name}<br>{dept_total} incidents")
        parents.append("")
        values.append(dept_total if dept_total > 0 else 1)
        colors.append(get_risk_color(dept["risk_level"]))
        
        for team in dept["teams"]:
            if team["incidents"] > 0:
                team_id = f"{dept['id']}-{team['name']}"
                team_name = team.get(name_key, team["name"])
                ids.append(team_id)
                labels.append(f"{team_name}<br>{team['incidents']} inc.")
                parents.append(dept["id"])
                values.append(team["incidents"])
                colors.append(get_risk_color(team["risk"]))
    
    fig = go.Figure(go.Sunburst(
        ids=ids, labels=labels, parents=parents, values=values,
        marker=dict(colors=colors), branchvalues="total",
        hovertemplate="<b>%{label}</b><extra></extra>", insidetextorientation='radial'
    ))
    
    title = "Macro Incident Mapping" if lang == "en" else "Cartographie Macro des Incidents"
    fig.update_layout(title=dict(text=title, font=dict(size=18)), height=500, margin=dict(t=60, l=10, r=10, b=10))
    return fig

def create_pie_types(lang):
    type_key = "type_en" if lang == "en" else "type"
    fig = go.Figure(go.Pie(
        labels=[t.get(type_key, t["type"]) for t in INCIDENT_TYPES],
        values=[t["count"] for t in INCIDENT_TYPES],
        marker=dict(colors=[t["color"] for t in INCIDENT_TYPES]),
        hole=0.4, textinfo="label+percent"
    ))
    title = "Incident Type Distribution" if lang == "en" else "Répartition par Type d'Incident"
    fig.update_layout(title=title, height=350, showlegend=True)
    return fig

def create_bar_comparison(data, lang):
    name_key = "name_en" if lang == "en" else "name"
    departments = [d.get(name_key, d["name"]) for d in data["departments"]]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(name="2023", x=departments, y=[d["incidents_2023"] for d in data["departments"]], marker_color="#94a3b8", text=[d["incidents_2023"] for d in data["departments"]], textposition="outside"))
    fig.add_trace(go.Bar(name="2024", x=departments, y=[d["incidents_2024"] for d in data["departments"]], marker_color="#3b82f6", text=[d["incidents_2024"] for d in data["departments"]], textposition="outside"))
    
    title = "Incident Evolution 2023 vs 2024" if lang == "en" else "Évolution des Incidents 2023 vs 2024"
    fig.update_layout(title=title, barmode="group", height=350, xaxis_title="Department" if lang == "en" else "Département", yaxis_title="Number of incidents" if lang == "en" else "Nombre d'incidents")
    return fig

def create_treemap_plotly(data, lang):
    ids, labels, parents, values, colors = [], [], [], [], []
    name_key = "name_en" if lang == "en" else "name"
    total_all = sum(d["incidents_2024"] for d in data["departments"])
    
    enterprise_name = data.get("name_en" if lang == "en" else "name", data["name"])
    ids.append("root")
    labels.append(f"{enterprise_name}<br>{total_all} incidents")
    parents.append("")
    values.append(total_all)
    colors.append("#1e3a5f")
    
    for dept in data["departments"]:
        dept_total = sum(team["incidents"] for team in dept["teams"])
        if dept_total > 0:
            dept_name = dept.get(name_key, dept["name"])
            ids.append(dept["id"])
            labels.append(f"{dept_name}<br>{dept_total} inc.")
            parents.append("root")
            values.append(dept_total)
            colors.append(get_risk_color(dept["risk_level"]))
            
            for team in dept["teams"]:
                if team["incidents"] > 0:
                    team_id = f"{dept['id']}_{team['name']}"
                    team_name = team.get(name_key, team["name"])
                    ids.append(team_id)
                    labels.append(f"{team_name}<br>{team['incidents']} inc.")
                    parents.append(dept["id"])
                    values.append(team["incidents"])
                    colors.append(get_risk_color(team["risk"]))
    
    fig = go.Figure(go.Treemap(ids=ids, labels=labels, parents=parents, values=values, marker=dict(colors=colors), textinfo="label", hovertemplate="<b>%{label}</b><extra></extra>", pathbar=dict(visible=True)))
    title = "Incident Treemap by Zone" if lang == "en" else "Treemap des Incidents par Zone"
    fig.update_layout(title=dict(text=title, font=dict(size=18)), height=400, margin=dict(t=60, l=10, r=10, b=10))
    return fig

# ============================================================
# PAGE PRINCIPALE
# ============================================================

@ui.page("/")
async def main_page():
    lang = current_lang["value"]
    name_key = "name_en" if lang == "en" else "name"
    
    # En-tête
    with ui.header().classes("text-white p-4").style(HEADER_STYLE):
        with ui.row().classes("w-full items-center justify-between"):
            with ui.row().classes("items-center gap-4"):
                ui.icon("map").classes("text-3xl")
                ui.label("EDGY-AgenticX5").classes("text-2xl font-bold")
                badge_text = "v5.0 Macro Mapping" if lang == "en" else "v5.0 Cartographie Macro"
                ui.badge(badge_text).props("color=green")
            
            with ui.row().classes("gap-2 items-center"):
                ui.button("🇫🇷 FR", on_click=lambda: set_language("fr")).props("flat color=white" if lang == "en" else "color=white")
                ui.button("🇬🇧 EN", on_click=lambda: set_language("en")).props("flat color=white" if lang == "fr" else "color=white")
                ui.label("|").classes("text-white/50")
                ui.button("CNESST", on_click=lambda: ui.navigate.to("/cnesst")).props("flat color=white")
                ui.button("⟳", on_click=lambda: ui.navigate.to("/")).props("flat color=white")
    
    with ui.column().classes("w-full p-6 gap-6"):
        
        # Titre
        title = "🗺️ OHS Macro Risk Mapping" if lang == "en" else "🗺️ Cartographie Macro des Risques SST"
        subtitle = "Hierarchical visualization of incidents by department and team" if lang == "en" else "Visualisation hiérarchique des incidents par département et équipe"
        ui.label(title).classes("text-3xl font-bold text-blue-900")
        ui.label(subtitle).classes("text-lg text-gray-600")
        
        # XAI Notice
        xai_text = "⚠️ Demo Data - XAI Integration with real CNESST data in progress" if lang == "en" else "⚠️ Données démo - Intégration XAI avec données CNESST réelles en cours"
        ui.label(xai_text).classes("text-sm text-orange-600 bg-orange-50 px-4 py-2 rounded-lg")
        
        # FILTRES
        filter_label = "🔍 Filters" if lang == "en" else "🔍 Filtres"
        with ui.card().classes("w-full"):
            ui.label(filter_label).classes("text-xl font-bold mb-4")
            with ui.row().classes("gap-4 flex-wrap"):
                with ui.column():
                    ui.label("Department" if lang == "en" else "Département").classes("text-sm text-gray-600")
                    all_label = "All" if lang == "en" else "Tous"
                    dept_options = [all_label] + [d.get(name_key, d["name"]) for d in ENTERPRISE_DATA["departments"]]
                    ui.select(dept_options, value=all_label).classes("w-48")
                
                with ui.column():
                    ui.label("NAICS Sector" if lang == "en" else "Secteur SCIAN").classes("text-sm text-gray-600")
                    scian_name_key = "name_en" if lang == "en" else "name"
                    scian_options = [f"{k} - {v.get(scian_name_key, v['name'])}" for k, v in SCIAN_BENCHMARKS.items()]
                    default_scian = "31-33 - Manufacturing" if lang == "en" else "31-33 - Fabrication"
                    ui.select(scian_options, value=default_scian).classes("w-72")
                
                with ui.column():
                    ui.label("Year (CNESST)" if lang == "en" else "Année (CNESST)").classes("text-sm text-gray-600")
                    all_years = "All" if lang == "en" else "Toutes"
                    year_options = AVAILABLE_YEARS + [all_years]
                    ui.select(year_options, value="2023").classes("w-32")
        
        # KPIs
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
                ui.label("Total Costs" if lang == "en" else "Coûts totaux").classes("text-sm opacity-80")
            
            with ui.card().style("background: linear-gradient(135deg, #ca8a04 0%, #eab308 100%); color: white; border-radius: 12px; padding: 20px;"):
                ui.icon("event_busy").classes("text-3xl")
                ui.label(str(total_days)).classes("text-3xl font-bold")
                ui.label("Days Lost" if lang == "en" else "Jours perdus").classes("text-sm opacity-80")
            
            benchmark = SCIAN_BENCHMARKS["31-33"]["taux_freq"]
            card_style = "background: linear-gradient(135deg, #16a34a 0%, #22c55e 100%); color: white; border-radius: 12px; padding: 20px;" if taux_freq < benchmark else "background: linear-gradient(135deg, #dc2626 0%, #ef4444 100%); color: white; border-radius: 12px; padding: 20px;"
            with ui.card().style(card_style):
                ui.icon("speed").classes("text-3xl")
                ui.label(f"{taux_freq:.1f}").classes("text-3xl font-bold")
                freq_label = f"{'Freq. Rate' if lang == 'en' else 'Taux fréq.'} (bench: {benchmark})"
                ui.label(freq_label).classes("text-sm opacity-80")
        
        # SUNBURST + LÉGENDE
        ui.separator()
        map_title = "📊 Hierarchical Mapping" if lang == "en" else "📊 Cartographie Hiérarchique"
        ui.label(map_title).classes("text-2xl font-bold text-blue-800")
        
        with ui.row().classes("w-full gap-6"):
            with ui.card().classes("flex-1"):
                ui.plotly(create_sunburst_plotly(ENTERPRISE_DATA, lang)).classes("w-full")
            
            with ui.card().classes("w-80"):
                legend_title = "🎯 Risk Legend" if lang == "en" else "🎯 Légende des risques"
                ui.label(legend_title).classes("text-lg font-bold mb-4")
                
                risk_labels = [
                    ("Critical - Immediate Action" if lang == "en" else "Critique - Action immédiate", "#dc2626"),
                    ("High - High Priority" if lang == "en" else "Élevé - Priorité haute", "#ea580c"),
                    ("Medium - Monitor" if lang == "en" else "Moyen - À surveiller", "#ca8a04"),
                    ("Low - Under Control" if lang == "en" else "Faible - Sous contrôle", "#16a34a")
                ]
                
                with ui.column().classes("gap-3"):
                    for label, color in risk_labels:
                        with ui.row().classes("items-center gap-2"):
                            ui.element("div").style(f"width:20px;height:20px;background:{color};border-radius:4px;")
                            ui.label(label)
                
                ui.separator()
                ui.label("💡 Insights").classes("text-lg font-bold mt-4 mb-2")
                
                max_dept = max(ENTERPRISE_DATA["departments"], key=lambda d: d["incidents_2024"])
                max_dept_name = max_dept.get(name_key, max_dept["name"])
                
                with ui.column().classes("gap-2 text-sm"):
                    ui.label(f"⚠️ {max_dept_name}: {max_dept['incidents_2024']} incidents ({max_dept['incidents_2024']/total_incidents*100:.0f}%)").classes("text-red-700")
                    prev_total = sum(d['incidents_2023'] for d in ENTERPRISE_DATA['departments'])
                    change = ((total_incidents/prev_total)-1)*100
                    change_word = "Increase" if lang == "en" and change > 0 else "Decrease" if lang == "en" else "Hausse" if change > 0 else "Baisse"
                    ui.label(f"📈 {change_word} {abs(change):.1f}% vs 2023").classes("text-orange-700")
                    avg_label = "Avg. cost" if lang == "en" else "Coût moyen"
                    ui.label(f"💰 {avg_label}: {total_cost//total_incidents:,}$/incident").classes("text-blue-700")
        
        # DÉPARTEMENTS
        ui.separator()
        dept_title = "🏢 Department Details" if lang == "en" else "🏢 Détail par Département"
        ui.label(dept_title).classes("text-2xl font-bold text-blue-800")
        
        with ui.row().classes("w-full gap-4 flex-wrap"):
            for dept in ENTERPRISE_DATA["departments"]:
                dept_name = dept.get(name_key, dept["name"])
                with ui.card().classes("w-72").style(get_risk_bg(dept["risk_level"])):
                    with ui.row().classes("justify-between items-center"):
                        ui.label(dept_name).classes("text-xl font-bold")
                        ui.badge(get_risk_label(dept["risk_level"], lang)).props("color=white outline")
                    
                    ui.separator().classes("my-2 bg-white/30")
                    emp_label = "employees" if lang == "en" else "employés"
                    days_label = "days lost" if lang == "en" else "jours perdus"
                    ui.label(f"👥 {dept['employees']} {emp_label}").classes("text-sm")
                    ui.label(f"⚠️ {dept['incidents_2024']} incidents").classes("text-sm")
                    ui.label(f"💰 {dept['cost_total']:,}$").classes("text-sm")
                    ui.label(f"📅 {dept['days_lost']} {days_label}").classes("text-sm")
                    
                    ui.separator().classes("my-2 bg-white/30")
                    teams_label = "Teams:" if lang == "en" else "Équipes:"
                    ui.label(teams_label).classes("text-sm font-bold")
                    for team in dept["teams"]:
                        team_name = team.get(name_key, team["name"])
                        icon = "🔴" if team["risk"] == "critique" else "🟠" if team["risk"] == "eleve" else "🟡" if team["risk"] == "moyen" else "🟢"
                        ui.label(f"{icon} {team_name}: {team['incidents']} inc.").classes("text-xs")
        
        # GRAPHIQUES
        ui.separator()
        with ui.row().classes("w-full gap-6"):
            with ui.card().classes("flex-1"):
                ui.plotly(create_pie_types(lang)).classes("w-full")
            with ui.card().classes("flex-1"):
                ui.plotly(create_bar_comparison(ENTERPRISE_DATA, lang)).classes("w-full")
        
        # TREEMAP
        with ui.card().classes("w-full"):
            ui.plotly(create_treemap_plotly(ENTERPRISE_DATA, lang)).classes("w-full")
        
        # BENCHMARKS CNESST
        ui.separator()
        bench_title = "📊 CNESST Quebec Benchmarks" if lang == "en" else "📊 Benchmarks CNESST Québec"
        ui.label(bench_title).classes("text-2xl font-bold text-green-800")
        
        cnesst_data = await fetch_cnesst_summary()
        
        if cnesst_data and cnesst_data.get("total_incidents", 0) > 0:
            with ui.card().classes("w-full bg-green-50"):
                base_label = "Base" if lang == "en" else "Base"
                inc_label = "CNESST incidents" if lang == "en" else "incidents CNESST"
                with ui.row().classes("justify-between items-center mb-4"):
                    ui.label(f"📈 {base_label}: {cnesst_data.get('total_incidents', 0):,} {inc_label}").classes("text-xl font-bold text-green-800")
                    ui.badge("2017-2023").props("color=green")
                
                benchmark = SCIAN_BENCHMARKS["31-33"]
                better = "✅ Better" if lang == "en" else "✅ Meilleur"
                to_improve = "⚠️ To Improve" if lang == "en" else "⚠️ À améliorer"
                
                columns = [
                    {"name": "metric", "label": "Metric" if lang == "en" else "Métrique", "field": "metric"},
                    {"name": "enterprise", "label": "Your Company" if lang == "en" else "Votre entreprise", "field": "enterprise"},
                    {"name": "sector", "label": "Sector (31-33)" if lang == "en" else "Secteur (31-33)", "field": "sector"},
                    {"name": "status", "label": "Status" if lang == "en" else "Statut", "field": "status"}
                ]
                rows = [
                    {"metric": "Frequency Rate" if lang == "en" else "Taux de fréquence", "enterprise": f"{taux_freq:.1f}", "sector": f"{benchmark['taux_freq']}", "status": better if taux_freq < benchmark["taux_freq"] else to_improve},
                    {"metric": "Avg. Days Lost" if lang == "en" else "Jours moyens perdus", "enterprise": f"{total_days/total_incidents:.0f}", "sector": f"{benchmark['jours_moy']}", "status": better if total_days/total_incidents < benchmark["jours_moy"] else to_improve},
                    {"metric": "Avg. Cost/Incident" if lang == "en" else "Coût moyen/incident", "enterprise": f"{total_cost//total_incidents:,}$", "sector": f"{benchmark['cout_moy']:,}$", "status": better if total_cost/total_incidents < benchmark["cout_moy"] else to_improve}
                ]
                ui.table(columns=columns, rows=rows).classes("w-full")
        else:
            ui.label("⚠️ CNESST API not available" if lang == "en" else "⚠️ API CNESST non disponible").classes("text-orange-600")
        
        # Footer
        ui.separator()
        with ui.row().classes("w-full justify-between text-gray-500"):
            ui.label("© 2025 GenAISafety/Preventera - Mario Deshaies")
            source = "Source: CNESST Quebec | Demo Data - XAI Integration in Progress" if lang == "en" else "Source: CNESST Québec | Données démo - Intégration XAI en cours"
            ui.label(source).classes("text-xs")
            updated = "Updated" if lang == "en" else "Mis à jour"
            ui.label(f"{updated}: {datetime.now().strftime('%Y-%m-%d %H:%M')}")


def set_language(lang):
    current_lang["value"] = lang
    ui.navigate.to("/")


@ui.page("/cnesst")
async def cnesst_page():
    lang = current_lang["value"]
    
    with ui.header().classes("bg-green-800 text-white p-4"):
        with ui.row().classes("w-full items-center justify-between"):
            title = "📊 CNESST Data" if lang == "en" else "📊 Données CNESST"
            ui.label(title).classes("text-2xl font-bold")
            with ui.row().classes("gap-2"):
                ui.button("🇫🇷 FR", on_click=lambda: set_language("fr")).props("flat color=white")
                ui.button("🇬🇧 EN", on_click=lambda: set_language("en")).props("flat color=white")
                ui.button("← Back" if lang == "en" else "← Retour", on_click=lambda: ui.navigate.to("/")).props("flat color=white")
    
    with ui.column().classes("w-full p-6"):
        cnesst_data = await fetch_cnesst_summary()
        
        if cnesst_data:
            ui.label(f"Total: {cnesst_data.get('total_incidents', 0):,} incidents").classes("text-3xl font-bold text-green-800")
            
            if "by_year" in cnesst_data:
                columns = [
                    {"name": "year", "label": "Year" if lang == "en" else "Année", "field": "year"},
                    {"name": "incidents", "label": "Incidents", "field": "incidents"},
                    {"name": "size", "label": "Size (MB)" if lang == "en" else "Taille (Mo)", "field": "size"}
                ]
                rows = [{"year": y["year"], "incidents": f"{y['incidents']:,}", "size": f"{y['size_mb']:.1f}"} for y in cnesst_data["by_year"]]
                ui.table(columns=columns, rows=rows).classes("w-full mt-4")


if __name__ in {"__main__", "__mp_main__"}:
    print("\n" + "="*60)
    print("🗺️ EDGY-AgenticX5 Dashboard v5.0 - BILINGUE FR/EN")
    print("   Auteur: Mario Deshaies - GenAISafety/Preventera")
    print("="*60)
    print("📊 Dashboard: http://localhost:8003")
    print("📡 API requise: http://localhost:8000")
    print("="*60 + "\n")
    
    ui.run(title="EDGY-AgenticX5", port=8003, reload=False, show=False)
