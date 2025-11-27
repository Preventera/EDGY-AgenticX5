"""
EDGY-AgenticX5 Dashboard v4.0 - Avec Données CNESST Réelles
============================================================
Dashboard NiceGUI avec intégration des 793K+ incidents CNESST

Auteur: Mario Genest - GenAISafety/Preventera
"""

from nicegui import ui
import httpx
from datetime import datetime

API_URL = "http://localhost:8000"

# ============================================================
# STYLES
# ============================================================

CARD_STYLE = """
    background: linear-gradient(135deg, #1e3a5f 0%, #2d5a87 100%);
    border-radius: 12px;
    padding: 20px;
    color: white;
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
"""

STAT_CARD = """
    background: linear-gradient(135deg, #2d5a87 0%, #3d7ab7 100%);
    border-radius: 10px;
    padding: 15px;
    text-align: center;
    color: white;
"""

CNESST_CARD = """
    background: linear-gradient(135deg, #1a5f2a 0%, #2d8747 100%);
    border-radius: 10px;
    padding: 15px;
    text-align: center;
    color: white;
"""

# ============================================================
# FONCTIONS API
# ============================================================

async def fetch_api(endpoint: str):
    """Appel API asynchrone"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{API_URL}{endpoint}")
            if response.status_code == 200:
                return response.json()
    except Exception as e:
        print(f"Erreur API {endpoint}: {e}")
    return None

async def fetch_carto_stats():
    return await fetch_api("/cartography/stats")

async def fetch_cnesst_summary():
    return await fetch_api("/cnesst/summary")

async def fetch_cnesst_trends():
    return await fetch_api("/cnesst/trends")

async def fetch_cnesst_columns():
    return await fetch_api("/cnesst/columns")

async def fetch_combined_stats():
    return await fetch_api("/dashboard/combined-stats")

async def populate_demo():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{API_URL}/cartography/demo/populate")
            return response.json() if response.status_code == 200 else None
    except:
        return None

# ============================================================
# COMPOSANTS UI
# ============================================================

def create_stat_box(label: str, value, icon: str, style: str = STAT_CARD):
    """Crée une boîte de statistique"""
    with ui.card().style(style):
        ui.icon(icon).classes('text-3xl mb-2')
        ui.label(str(value)).classes('text-2xl font-bold')
        ui.label(label).classes('text-sm opacity-80')

def create_cnesst_year_chart(trends_data):
    """Crée le graphique des tendances CNESST par année"""
    if not trends_data:
        return
    
    years = trends_data.get("years", [])
    incidents = trends_data.get("incidents", [])
    
    if not years or not incidents:
        ui.label("Aucune donnée de tendance disponible").classes('text-gray-500')
        return
    
    chart_options = {
        'chart': {'type': 'column', 'height': 350},
        'title': {'text': 'Incidents CNESST par Année (2017-2023)'},
        'xAxis': {'categories': [str(y) for y in years]},
        'yAxis': {'title': {'text': 'Nombre d\'incidents'}},
        'series': [{
            'name': 'Incidents',
            'data': incidents,
            'color': '#2d8747'
        }],
        'plotOptions': {
            'column': {
                'dataLabels': {
                    'enabled': True,
                    'format': '{point.y:,.0f}'
                }
            }
        }
    }
    
    ui.highchart(chart_options).classes('w-full')

def create_risk_pie_chart(risk_data):
    """Crée le graphique de répartition des risques"""
    if not risk_data:
        return
    
    data = [
        {'name': 'Faible', 'y': risk_data.get('faible', 0), 'color': '#22c55e'},
        {'name': 'Moyen', 'y': risk_data.get('moyen', 0), 'color': '#eab308'},
        {'name': 'Élevé', 'y': risk_data.get('eleve', 0), 'color': '#f97316'},
        {'name': 'Critique', 'y': risk_data.get('critique', 0), 'color': '#ef4444'}
    ]
    
    # Filtrer les valeurs à 0
    data = [d for d in data if d['y'] > 0]
    
    if not data:
        ui.label("Aucune donnée de risque").classes('text-gray-500')
        return
    
    chart_options = {
        'chart': {'type': 'pie', 'height': 300},
        'title': {'text': 'Répartition des Risques'},
        'series': [{
            'name': 'Éléments',
            'data': data
        }],
        'plotOptions': {
            'pie': {
                'allowPointSelect': True,
                'cursor': 'pointer',
                'dataLabels': {
                    'enabled': True,
                    'format': '{point.name}: {point.y}'
                }
            }
        }
    }
    
    ui.highchart(chart_options).classes('w-full')

# ============================================================
# PAGE PRINCIPALE
# ============================================================

@ui.page('/')
async def main_page():
    # En-tête
    with ui.header().classes('bg-blue-900 text-white p-4'):
        with ui.row().classes('w-full items-center justify-between'):
            with ui.row().classes('items-center gap-4'):
                ui.icon('security').classes('text-3xl')
                ui.label('EDGY-AgenticX5').classes('text-2xl font-bold')
                ui.badge('v4.0 + CNESST').props('color=green')
            
            with ui.row().classes('gap-2'):
                ui.button('Actualiser', on_click=lambda: ui.navigate.to('/')).props('flat color=white')
    
    # Contenu principal
    with ui.column().classes('w-full p-6 gap-6'):
        
        # Titre
        ui.label('🏭 Dashboard SST avec Données CNESST Réelles').classes('text-3xl font-bold text-blue-900')
        ui.label('793,737+ lésions professionnelles (2017-2023)').classes('text-lg text-gray-600')
        
        # Charger les données
        carto_stats = await fetch_carto_stats()
        cnesst_summary = await fetch_cnesst_summary()
        cnesst_trends = await fetch_cnesst_trends()
        
        # ============================================================
        # SECTION CNESST
        # ============================================================
        
        ui.separator()
        ui.label('📊 DONNÉES CNESST QUÉBEC').classes('text-2xl font-bold text-green-800')
        
        if cnesst_summary and cnesst_summary.get("total_incidents", 0) > 0:
            # KPIs CNESST
            with ui.row().classes('w-full gap-4 flex-wrap'):
                create_stat_box(
                    "Total Incidents",
                    f"{cnesst_summary.get('total_incidents', 0):,}",
                    "assignment_late",
                    CNESST_CARD
                )
                create_stat_box(
                    "Années Disponibles",
                    cnesst_summary.get("years_count", 0),
                    "calendar_month",
                    CNESST_CARD
                )
                create_stat_box(
                    "Taille Données",
                    f"{cnesst_summary.get('total_size_mb', 0):.0f} Mo",
                    "storage",
                    CNESST_CARD
                )
                create_stat_box(
                    "Source",
                    "CNESST",
                    "verified",
                    CNESST_CARD
                )
            
            # Tableau par année
            with ui.card().classes('w-full'):
                ui.label('📅 Incidents par Année').classes('text-xl font-bold mb-4')
                
                by_year = cnesst_summary.get("by_year", [])
                if by_year:
                    columns = [
                        {'name': 'year', 'label': 'Année', 'field': 'year', 'align': 'center'},
                        {'name': 'incidents', 'label': 'Incidents', 'field': 'incidents', 'align': 'right'},
                        {'name': 'size_mb', 'label': 'Taille (Mo)', 'field': 'size_mb', 'align': 'right'}
                    ]
                    
                    rows = [
                        {
                            'year': y['year'],
                            'incidents': f"{y['incidents']:,}",
                            'size_mb': f"{y['size_mb']:.1f}"
                        }
                        for y in by_year
                    ]
                    
                    ui.table(columns=columns, rows=rows).classes('w-full')
            
            # Graphique tendances
            if cnesst_trends:
                with ui.card().classes('w-full'):
                    create_cnesst_year_chart(cnesst_trends)
        
        else:
            with ui.card().classes('w-full p-6 bg-yellow-50'):
                ui.icon('warning').classes('text-4xl text-yellow-600')
                ui.label('Données CNESST non disponibles').classes('text-xl font-bold text-yellow-800')
                ui.label('Assurez-vous que les fichiers CSV sont dans data/cnesst/').classes('text-gray-600')
        
        # ============================================================
        # SECTION CARTOGRAPHIE
        # ============================================================
        
        ui.separator()
        ui.label('🗺️ CARTOGRAPHIE ORGANISATIONNELLE').classes('text-2xl font-bold text-blue-800')
        
        if carto_stats:
            # KPIs Cartographie
            with ui.row().classes('w-full gap-4 flex-wrap'):
                create_stat_box("Organisations", carto_stats.get("organizations", 0), "business", STAT_CARD)
                create_stat_box("Personnes", carto_stats.get("persons", 0), "people", STAT_CARD)
                create_stat_box("Équipes", carto_stats.get("teams", 0), "groups", STAT_CARD)
                create_stat_box("Zones", carto_stats.get("zones", 0), "location_on", STAT_CARD)
                create_stat_box("Processus", carto_stats.get("processes", 0), "settings", STAT_CARD)
                create_stat_box("Relations", carto_stats.get("relations", 0), "link", STAT_CARD)
            
            # Graphique des risques
            risk_data = carto_stats.get("risk_distribution", {})
            if any(v > 0 for v in risk_data.values()):
                with ui.card().classes('w-full'):
                    create_risk_pie_chart(risk_data)
        else:
            with ui.card().classes('w-full p-6 bg-blue-50'):
                ui.icon('info').classes('text-4xl text-blue-600')
                ui.label('Cartographie vide').classes('text-xl font-bold text-blue-800')
                
                async def do_populate():
                    result = await populate_demo()
                    if result:
                        ui.notify('Données démo créées!', type='positive')
                        ui.navigate.to('/')
                    else:
                        ui.notify('Erreur lors de la création', type='negative')
                
                ui.button('Peupler avec données démo', on_click=do_populate).props('color=primary')
        
        # ============================================================
        # FOOTER
        # ============================================================
        
        ui.separator()
        with ui.row().classes('w-full justify-between items-center text-gray-500'):
            ui.label(f'© 2025 GenAISafety/Preventera - Mario Genest')
            ui.label(f'Dernière mise à jour: {datetime.now().strftime("%Y-%m-%d %H:%M")}')


# ============================================================
# PAGE CNESST DÉTAILLÉE
# ============================================================

@ui.page('/cnesst')
async def cnesst_page():
    with ui.header().classes('bg-green-800 text-white p-4'):
        with ui.row().classes('w-full items-center justify-between'):
            with ui.row().classes('items-center gap-4'):
                ui.icon('assessment').classes('text-3xl')
                ui.label('Données CNESST').classes('text-2xl font-bold')
            
            ui.button('← Retour', on_click=lambda: ui.navigate.to('/')).props('flat color=white')
    
    with ui.column().classes('w-full p-6 gap-6'):
        ui.label('📊 Exploration des Données CNESST').classes('text-3xl font-bold')
        
        # Structure des données
        columns_info = await fetch_cnesst_columns()
        
        if columns_info and "columns" in columns_info:
            with ui.card().classes('w-full'):
                ui.label(f'📋 Structure des Données ({columns_info.get("total_columns", 0)} colonnes)').classes('text-xl font-bold mb-4')
                
                with ui.expansion('Voir toutes les colonnes'):
                    cols = columns_info.get("columns", [])
                    for i in range(0, len(cols), 4):
                        with ui.row().classes('gap-4'):
                            for col in cols[i:i+4]:
                                ui.badge(col).props('color=blue')
            
            # Exemple de données
            if "sample_row" in columns_info:
                with ui.card().classes('w-full'):
                    ui.label('🔍 Exemple d\'enregistrement').classes('text-xl font-bold mb-4')
                    
                    sample = columns_info.get("sample_row", {})
                    # Afficher les 10 premiers champs
                    items = list(sample.items())[:10]
                    
                    columns = [
                        {'name': 'field', 'label': 'Champ', 'field': 'field'},
                        {'name': 'value', 'label': 'Valeur', 'field': 'value'}
                    ]
                    rows = [{'field': k, 'value': str(v)[:100]} for k, v in items]
                    
                    ui.table(columns=columns, rows=rows).classes('w-full')


# ============================================================
# LANCEMENT
# ============================================================

if __name__ in {"__main__", "__mp_main__"}:
    print("\n" + "="*60)
    print("🚀 EDGY-AgenticX5 Dashboard v4.0 avec CNESST")
    print("="*60)
    print("📊 Dashboard: http://localhost:8003")
    print("📡 API requise: http://localhost:8000")
    print("="*60 + "\n")
    
    ui.run(
        title='EDGY-AgenticX5 + CNESST',
        port=8003,
        reload=False,
        show=False
    )
