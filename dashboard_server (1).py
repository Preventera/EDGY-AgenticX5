#!/usr/bin/env python3
"""
Endpoint Dashboard pour EDGY-AgenticX5
Fournit toutes les donnees necessaires pour le dashboard React
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pathlib import Path
import sys

# Ajouter le chemin src
sys.path.insert(0, str(Path(__file__).parent / "src"))

from edgy_core.api.cartography_api import store

app = FastAPI(
    title="EDGY Dashboard API",
    description="API pour le dashboard de visualisation EDGY",
    version="1.0.0"
)

# CORS pour permettre les requetes depuis le frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_class=HTMLResponse)
async def root():
    """Page d'accueil avec le dashboard React"""
    html_content = """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EDGY-AgenticX5 Dashboard</title>
    <script crossorigin src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
    <script crossorigin src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body {
            margin: 0;
            padding: 0;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
        }
    </style>
</head>
<body>
    <div id="root"></div>
    
    <script type="text/babel">
        const { useState, useEffect } = React;
        
        const Dashboard = () => {
            const [data, setData] = useState(null);
            const [loading, setLoading] = useState(true);
            
            useEffect(() => {
                loadData();
            }, []);
            
            const loadData = async () => {
                try {
                    const response = await fetch('http://localhost:8001/dashboard');
                    const result = await response.json();
                    setData(result);
                } catch (err) {
                    console.error('Erreur:', err);
                } finally {
                    setLoading(false);
                }
            };
            
            if (loading) {
                return (
                    <div className="flex items-center justify-center h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
                        <div className="text-center">
                            <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-blue-600 mx-auto mb-4"></div>
                            <p className="text-xl text-gray-700">Chargement...</p>
                        </div>
                    </div>
                );
            }
            
            if (!data) {
                return (
                    <div className="flex items-center justify-center h-screen">
                        <div className="text-center p-8 bg-red-100 rounded-lg">
                            <p className="text-xl text-red-700">Erreur de chargement</p>
                            <button 
                                onClick={loadData}
                                className="mt-4 px-6 py-2 bg-red-600 text-white rounded hover:bg-red-700"
                            >
                                Reessayer
                            </button>
                        </div>
                    </div>
                );
            }
            
            const kpis = data.kpis || {};
            
            return (
                <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 p-8">
                    <div className="mb-8 text-center">
                        <h1 className="text-5xl font-bold text-gray-900 mb-2">
                            EDGY-AgenticX5 Dashboard
                        </h1>
                        <p className="text-xl text-gray-600">Cartographie Organisationnelle & Analyse SST</p>
                        <button 
                            onClick={loadData}
                            className="mt-4 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition shadow-lg"
                        >
                            Actualiser
                        </button>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-6 mb-8">
                        <div className="bg-white rounded-xl shadow-lg p-6 hover:shadow-2xl transition">
                            <div className="text-sm text-gray-600 mb-2">Personnes</div>
                            <div className="text-4xl font-bold text-blue-600">{kpis.total_persons || 0}</div>
                        </div>

                        <div className="bg-white rounded-xl shadow-lg p-6 hover:shadow-2xl transition">
                            <div className="text-sm text-gray-600 mb-2">Equipes</div>
                            <div className="text-4xl font-bold text-green-600">{kpis.total_teams || 0}</div>
                        </div>

                        <div className="bg-white rounded-xl shadow-lg p-6 hover:shadow-2xl transition">
                            <div className="text-sm text-gray-600 mb-2">Zones</div>
                            <div className="text-4xl font-bold text-purple-600">{kpis.total_zones || 0}</div>
                        </div>

                        <div className="bg-white rounded-xl shadow-lg p-6 hover:shadow-2xl transition">
                            <div className="text-sm text-gray-600 mb-2">Processus</div>
                            <div className="text-4xl font-bold text-cyan-600">{kpis.total_processes || 0}</div>
                        </div>

                        <div className="bg-white rounded-xl shadow-lg p-6 hover:shadow-2xl transition">
                            <div className="text-sm text-gray-600 mb-2">Relations</div>
                            <div className="text-4xl font-bold text-indigo-600">{kpis.total_relations || 0}</div>
                        </div>

                        <div className="bg-white rounded-xl shadow-lg p-6 hover:shadow-2xl transition border-4 border-red-500">
                            <div className="text-sm text-gray-600 mb-2">Risque Eleve</div>
                            <div className="text-4xl font-bold text-red-600">{kpis.high_risk_zones || 0}</div>
                        </div>
                    </div>

                    <div className="bg-white rounded-xl shadow-2xl p-8 mb-8">
                        <h2 className="text-3xl font-bold mb-6 text-gray-800">Vue d'Ensemble</h2>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
                            <div className="p-4 bg-blue-50 rounded-lg">
                                <div className="text-2xl font-bold text-blue-700">{data.stats?.organizations || 0}</div>
                                <div className="text-sm text-gray-600">Organisations</div>
                            </div>
                            <div className="p-4 bg-green-50 rounded-lg">
                                <div className="text-2xl font-bold text-green-700">{data.stats?.persons || 0}</div>
                                <div className="text-sm text-gray-600">Employes</div>
                            </div>
                            <div className="p-4 bg-purple-50 rounded-lg">
                                <div className="text-2xl font-bold text-purple-700">{data.stats?.teams || 0}</div>
                                <div className="text-sm text-gray-600">Equipes</div>
                            </div>
                            <div className="p-4 bg-orange-50 rounded-lg">
                                <div className="text-2xl font-bold text-orange-700">{data.stats?.roles || 0}</div>
                                <div className="text-sm text-gray-600">Roles</div>
                            </div>
                        </div>
                    </div>

                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                        <div className="bg-white rounded-xl shadow-2xl p-6">
                            <h3 className="text-2xl font-bold mb-4 text-gray-800">Personnes</h3>
                            <div className="overflow-auto max-h-96">
                                <table className="w-full text-sm">
                                    <thead className="sticky top-0 bg-gray-100">
                                        <tr>
                                            <th className="p-3 text-left font-semibold">Nom</th>
                                            <th className="p-3 text-left font-semibold">Departement</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {(data.persons || []).map(person => (
                                            <tr key={person.id} className="border-t hover:bg-gray-50 transition">
                                                <td className="p-3">{person.name}</td>
                                                <td className="p-3 text-gray-600">{person.department || '-'}</td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </div>

                        <div className="bg-white rounded-xl shadow-2xl p-6">
                            <h3 className="text-2xl font-bold mb-4 text-gray-800">Zones a Risque</h3>
                            <div className="overflow-auto max-h-96">
                                <table className="w-full text-sm">
                                    <thead className="sticky top-0 bg-gray-100">
                                        <tr>
                                            <th className="p-3 text-left font-semibold">Zone</th>
                                            <th className="p-3 text-left font-semibold">Niveau</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {(data.zones || []).map(zone => (
                                            <tr key={zone.id} className="border-t hover:bg-gray-50 transition">
                                                <td className="p-3">{zone.name}</td>
                                                <td className="p-3">
                                                    <span className={'px-3 py-1 rounded-full text-xs font-bold ' + (
                                                        zone.risk_level === 'critique' ? 'bg-red-600 text-white' :
                                                        zone.risk_level === 'eleve' ? 'bg-orange-500 text-white' :
                                                        zone.risk_level === 'moyen' ? 'bg-yellow-500 text-white' :
                                                        'bg-green-500 text-white'
                                                    )}>
                                                        {zone.risk_level || 'moyen'}
                                                    </span>
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            );
        };
        
        ReactDOM.render(<Dashboard />, document.getElementById('root'));
    </script>
</body>
</html>"""
    return html_content


@app.get("/dashboard")
async def get_dashboard_data():
    """Recupere toutes les donnees pour le dashboard"""
    stats = store.get_stats()
    
    persons_data = []
    for person in store.persons.values():
        persons_data.append({
            "id": person["id"],
            "name": person["name"],
            "department": person.get("department"),
            "supervisor_id": person.get("supervisor_id"),
            "role_ids": person.get("role_ids", []),
            "team_ids": person.get("team_ids", [])
        })
    
    relations_data = []
    for rel in store.relations:
        relations_data.append({
            "source": rel["source_id"],
            "target": rel["target_id"],
            "type": rel["relation_type"]
        })
    
    kpis = {
        "total_persons": len(store.persons),
        "total_teams": len(store.teams),
        "total_zones": len(store.zones),
        "total_processes": len(store.processes),
        "total_relations": len(store.relations),
        "high_risk_zones": sum(1 for z in store.zones.values() if z.get("risk_level") == "eleve"),
        "supervisors": sum(1 for p in store.persons.values() if any(
            role_id in store.roles and store.roles[role_id].get("can_supervise", False)
            for role_id in p.get("role_ids", [])
        ))
    }
    
    return {
        "stats": stats.model_dump(),
        "kpis": kpis,
        "persons": persons_data,
        "organizations": list(store.organizations.values()),
        "teams": list(store.teams.values()),
        "roles": list(store.roles.values()),
        "zones": list(store.zones.values()),
        "processes": list(store.processes.values()),
        "relations": relations_data
    }


@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "ok",
        "service": "EDGY Dashboard API",
        "version": "1.0.0",
        "entities": {
            "organizations": len(store.organizations),
            "persons": len(store.persons),
            "teams": len(store.teams),
            "roles": len(store.roles),
            "zones": len(store.zones),
            "processes": len(store.processes),
            "relations": len(store.relations)
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "=" * 60)
    print("  EDGY-AgenticX5 Dashboard Server")
    print("=" * 60)
    print("\n  Dashboard: http://localhost:8001")
    print("  API:       http://localhost:8001/dashboard")
    print("  Health:    http://localhost:8001/health")
    print("\n" + "=" * 60 + "\n")
    
    uvicorn.run(
        "dashboard_server:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
