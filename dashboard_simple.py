#!/usr/bin/env python3
"""
Dashboard Simple pour EDGY-AgenticX5
Recupere les donnees depuis l'API principale sur port 8000
Version 2.0 - Affichage complet des tableaux
"""

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="EDGY Dashboard")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    """Dashboard React qui recupere les donnees de l'API principale"""
    html = """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EDGY-AgenticX5 Dashboard</title>
    <script src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
    <script src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body>
    <div id="root"></div>
    
    <script type="text/babel">
        const { useState, useEffect } = React;
        
        const Dashboard = () => {
            const [data, setData] = useState(null);
            const [loading, setLoading] = useState(true);
            const [error, setError] = useState(null);
            
            const loadData = async () => {
                setLoading(true);
                setError(null);
                try {
                    // Charger les stats
                    const statsResp = await fetch('http://localhost:8000/cartography/stats');
                    const stats = await statsResp.json();
                    console.log('Stats:', stats);
                    
                    // Charger les personnes
                    let persons = [];
                    try {
                        const personsResp = await fetch('http://localhost:8000/cartography/persons');
                        const personsData = await personsResp.json();
                        persons = Array.isArray(personsData) ? personsData : 
                                  personsData.items ? personsData.items :
                                  personsData.data ? personsData.data :
                                  Object.values(personsData);
                        console.log('Persons:', persons);
                    } catch (e) {
                        console.error('Erreur chargement personnes:', e);
                    }
                    
                    // Charger les zones
                    let zones = [];
                    try {
                        const zonesResp = await fetch('http://localhost:8000/cartography/zones');
                        const zonesData = await zonesResp.json();
                        zones = Array.isArray(zonesData) ? zonesData :
                                zonesData.items ? zonesData.items :
                                zonesData.data ? zonesData.data :
                                Object.values(zonesData);
                        console.log('Zones:', zones);
                    } catch (e) {
                        console.error('Erreur chargement zones:', e);
                    }
                    
                    // Charger les equipes
                    let teams = [];
                    try {
                        const teamsResp = await fetch('http://localhost:8000/cartography/teams');
                        const teamsData = await teamsResp.json();
                        teams = Array.isArray(teamsData) ? teamsData :
                                teamsData.items ? teamsData.items :
                                teamsData.data ? teamsData.data :
                                Object.values(teamsData);
                        console.log('Teams:', teams);
                    } catch (e) {
                        console.error('Erreur chargement equipes:', e);
                    }
                    
                    // Charger les roles
                    let roles = [];
                    try {
                        const rolesResp = await fetch('http://localhost:8000/cartography/roles');
                        const rolesData = await rolesResp.json();
                        roles = Array.isArray(rolesData) ? rolesData :
                                rolesData.items ? rolesData.items :
                                rolesData.data ? rolesData.data :
                                Object.values(rolesData);
                        console.log('Roles:', roles);
                    } catch (e) {
                        console.error('Erreur chargement roles:', e);
                    }
                    
                    // Calculer les zones a haut risque
                    const highRiskZones = zones.filter(z => 
                        z.risk_level === 'eleve' || z.risk_level === 'critique'
                    ).length;
                    
                    setData({
                        stats: stats,
                        persons: persons,
                        zones: zones,
                        teams: teams,
                        roles: roles,
                        kpis: {
                            total_persons: stats.persons || persons.length || 0,
                            total_teams: stats.teams || teams.length || 0,
                            total_zones: stats.zones || zones.length || 0,
                            total_processes: stats.processes || 0,
                            total_relations: stats.relations || 0,
                            high_risk_zones: highRiskZones
                        }
                    });
                } catch (err) {
                    console.error('Erreur generale:', err);
                    setError(err.message);
                } finally {
                    setLoading(false);
                }
            };
            
            useEffect(() => {
                loadData();
            }, []);
            
            if (loading) {
                return (
                    <div className="flex items-center justify-center h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
                        <div className="text-center">
                            <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-blue-600 mx-auto mb-4"></div>
                            <p className="text-xl text-gray-700">Chargement des donnees...</p>
                        </div>
                    </div>
                );
            }
            
            if (error) {
                return (
                    <div className="flex items-center justify-center h-screen bg-gradient-to-br from-red-50 to-red-100">
                        <div className="text-center p-8 bg-white rounded-lg shadow-xl">
                            <p className="text-2xl text-red-700 mb-4">Erreur de chargement</p>
                            <p className="text-sm text-gray-600 mb-4">{error}</p>
                            <p className="text-sm text-gray-500 mb-4">Verifiez que l'API tourne sur http://localhost:8000</p>
                            <button onClick={loadData} className="px-6 py-2 bg-red-600 text-white rounded hover:bg-red-700">
                                Reessayer
                            </button>
                        </div>
                    </div>
                );
            }
            
            if (!data) {
                return (
                    <div className="flex items-center justify-center h-screen">
                        <div className="text-center p-8 bg-yellow-100 rounded-lg">
                            <p className="text-xl text-yellow-700">Aucune donnee disponible</p>
                            <button onClick={loadData} className="mt-4 px-6 py-2 bg-yellow-600 text-white rounded hover:bg-yellow-700">
                                Recharger
                            </button>
                        </div>
                    </div>
                );
            }
            
            const kpis = data.kpis || {};
            const persons = data.persons || [];
            const zones = data.zones || [];
            const teams = data.teams || [];
            const roles = data.roles || [];
            
            return (
                <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 p-8">
                    {/* Header */}
                    <div className="mb-8 text-center">
                        <h1 className="text-5xl font-bold text-gray-900 mb-2">EDGY-AgenticX5 Dashboard</h1>
                        <p className="text-xl text-gray-600">Cartographie Organisationnelle & Analyse SST</p>
                        <button onClick={loadData} className="mt-4 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition shadow-lg">
                            🔄 Actualiser
                        </button>
                    </div>

                    {/* KPIs */}
                    <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-6 mb-8">
                        <div className="bg-white rounded-xl shadow-lg p-6 hover:shadow-2xl transition">
                            <div className="text-sm text-gray-600 mb-2">👥 Personnes</div>
                            <div className="text-4xl font-bold text-blue-600">{kpis.total_persons}</div>
                        </div>
                        <div className="bg-white rounded-xl shadow-lg p-6 hover:shadow-2xl transition">
                            <div className="text-sm text-gray-600 mb-2">🏢 Equipes</div>
                            <div className="text-4xl font-bold text-green-600">{kpis.total_teams}</div>
                        </div>
                        <div className="bg-white rounded-xl shadow-lg p-6 hover:shadow-2xl transition">
                            <div className="text-sm text-gray-600 mb-2">🛡️ Zones</div>
                            <div className="text-4xl font-bold text-purple-600">{kpis.total_zones}</div>
                        </div>
                        <div className="bg-white rounded-xl shadow-lg p-6 hover:shadow-2xl transition">
                            <div className="text-sm text-gray-600 mb-2">⚙️ Processus</div>
                            <div className="text-4xl font-bold text-cyan-600">{kpis.total_processes}</div>
                        </div>
                        <div className="bg-white rounded-xl shadow-lg p-6 hover:shadow-2xl transition">
                            <div className="text-sm text-gray-600 mb-2">🔗 Relations</div>
                            <div className="text-4xl font-bold text-indigo-600">{kpis.total_relations}</div>
                        </div>
                        <div className="bg-white rounded-xl shadow-lg p-6 hover:shadow-2xl transition border-4 border-red-500">
                            <div className="text-sm text-gray-600 mb-2">⚠️ Risque Eleve</div>
                            <div className="text-4xl font-bold text-red-600">{kpis.high_risk_zones}</div>
                        </div>
                    </div>

                    {/* Vue d'Ensemble */}
                    <div className="bg-white rounded-xl shadow-2xl p-8 mb-8">
                        <h2 className="text-3xl font-bold mb-6 text-gray-800">Vue d'Ensemble</h2>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
                            <div className="p-4 bg-blue-50 rounded-lg">
                                <div className="text-2xl font-bold text-blue-700">{data.stats?.organizations || 0}</div>
                                <div className="text-sm text-gray-600">Organisations</div>
                            </div>
                            <div className="p-4 bg-green-50 rounded-lg">
                                <div className="text-2xl font-bold text-green-700">{persons.length || data.stats?.persons || 0}</div>
                                <div className="text-sm text-gray-600">Employes</div>
                            </div>
                            <div className="p-4 bg-purple-50 rounded-lg">
                                <div className="text-2xl font-bold text-purple-700">{teams.length || data.stats?.teams || 0}</div>
                                <div className="text-sm text-gray-600">Equipes</div>
                            </div>
                            <div className="p-4 bg-orange-50 rounded-lg">
                                <div className="text-2xl font-bold text-orange-700">{roles.length || data.stats?.roles || 0}</div>
                                <div className="text-sm text-gray-600">Roles</div>
                            </div>
                        </div>
                    </div>

                    {/* Tableaux Personnes et Zones */}
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                        {/* Tableau Personnes */}
                        <div className="bg-white rounded-xl shadow-2xl p-6">
                            <h3 className="text-2xl font-bold mb-4 text-gray-800">
                                👥 Personnes ({persons.length})
                            </h3>
                            <div className="overflow-auto max-h-96">
                                {persons.length === 0 ? (
                                    <p className="text-gray-500 text-center py-8">Aucune personne enregistree</p>
                                ) : (
                                    <table className="w-full text-sm">
                                        <thead className="sticky top-0 bg-gray-100">
                                            <tr>
                                                <th className="p-3 text-left font-semibold">Nom</th>
                                                <th className="p-3 text-left font-semibold">Departement</th>
                                                <th className="p-3 text-left font-semibold">Email</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {persons.map((person, index) => (
                                                <tr key={person.id || index} className="border-t hover:bg-blue-50 transition">
                                                    <td className="p-3 font-medium">{person.name || person.nom || '-'}</td>
                                                    <td className="p-3 text-gray-600">{person.department || person.departement || '-'}</td>
                                                    <td className="p-3 text-gray-500">{person.email || '-'}</td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                )}
                            </div>
                        </div>

                        {/* Tableau Zones */}
                        <div className="bg-white rounded-xl shadow-2xl p-6">
                            <h3 className="text-2xl font-bold mb-4 text-gray-800">
                                🛡️ Zones a Risque ({zones.length})
                            </h3>
                            <div className="overflow-auto max-h-96">
                                {zones.length === 0 ? (
                                    <p className="text-gray-500 text-center py-8">Aucune zone enregistree</p>
                                ) : (
                                    <table className="w-full text-sm">
                                        <thead className="sticky top-0 bg-gray-100">
                                            <tr>
                                                <th className="p-3 text-left font-semibold">Zone</th>
                                                <th className="p-3 text-left font-semibold">Type</th>
                                                <th className="p-3 text-left font-semibold">Niveau</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {zones.map((zone, index) => (
                                                <tr key={zone.id || index} className="border-t hover:bg-purple-50 transition">
                                                    <td className="p-3 font-medium">{zone.name || zone.nom || '-'}</td>
                                                    <td className="p-3 text-gray-600">{zone.zone_type || zone.type || '-'}</td>
                                                    <td className="p-3">
                                                        <span className={'px-3 py-1 rounded-full text-xs font-bold ' + (
                                                            zone.risk_level === 'critique' ? 'bg-red-600 text-white' :
                                                            zone.risk_level === 'eleve' ? 'bg-orange-500 text-white' :
                                                            zone.risk_level === 'moyen' ? 'bg-yellow-500 text-white' :
                                                            'bg-green-500 text-white'
                                                        )}>
                                                            {zone.risk_level || 'faible'}
                                                        </span>
                                                    </td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                )}
                            </div>
                        </div>
                    </div>

                    {/* Tableaux Equipes et Roles */}
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mt-8">
                        {/* Tableau Equipes */}
                        <div className="bg-white rounded-xl shadow-2xl p-6">
                            <h3 className="text-2xl font-bold mb-4 text-gray-800">
                                🏢 Equipes ({teams.length})
                            </h3>
                            <div className="overflow-auto max-h-96">
                                {teams.length === 0 ? (
                                    <p className="text-gray-500 text-center py-8">Aucune equipe enregistree</p>
                                ) : (
                                    <table className="w-full text-sm">
                                        <thead className="sticky top-0 bg-gray-100">
                                            <tr>
                                                <th className="p-3 text-left font-semibold">Nom</th>
                                                <th className="p-3 text-left font-semibold">Description</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {teams.map((team, index) => (
                                                <tr key={team.id || index} className="border-t hover:bg-green-50 transition">
                                                    <td className="p-3 font-medium">{team.name || team.nom || '-'}</td>
                                                    <td className="p-3 text-gray-600">{team.description || '-'}</td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                )}
                            </div>
                        </div>

                        {/* Tableau Roles */}
                        <div className="bg-white rounded-xl shadow-2xl p-6">
                            <h3 className="text-2xl font-bold mb-4 text-gray-800">
                                🎭 Roles ({roles.length})
                            </h3>
                            <div className="overflow-auto max-h-96">
                                {roles.length === 0 ? (
                                    <p className="text-gray-500 text-center py-8">Aucun role enregistre</p>
                                ) : (
                                    <table className="w-full text-sm">
                                        <thead className="sticky top-0 bg-gray-100">
                                            <tr>
                                                <th className="p-3 text-left font-semibold">Role</th>
                                                <th className="p-3 text-left font-semibold">Superviseur</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {roles.map((role, index) => (
                                                <tr key={role.id || index} className="border-t hover:bg-orange-50 transition">
                                                    <td className="p-3 font-medium">{role.name || role.nom || '-'}</td>
                                                    <td className="p-3">
                                                        {role.can_supervise ? (
                                                            <span className="px-2 py-1 bg-green-100 text-green-700 rounded text-xs">Oui</span>
                                                        ) : (
                                                            <span className="px-2 py-1 bg-gray-100 text-gray-500 rounded text-xs">Non</span>
                                                        )}
                                                    </td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                )}
                            </div>
                        </div>
                    </div>

                    {/* Footer */}
                    <div className="mt-8 text-center text-gray-500 text-sm">
                        <p>EDGY-AgenticX5 Dashboard v2.0 | Donnees en temps reel depuis l'API</p>
                        <p className="mt-2">
                            API: <a href="http://localhost:8000/docs" target="_blank" className="text-blue-600 hover:underline">http://localhost:8000/docs</a>
                        </p>
                    </div>
                </div>
            );
        };
        
        ReactDOM.render(<Dashboard />, document.getElementById('root'));
    </script>
</body>
</html>"""
    return html

if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "=" * 60)
    print("  EDGY-AgenticX5 Dashboard v2.0")
    print("=" * 60)
    print("\n  Dashboard: http://localhost:8003")
    print("  Donnees depuis: http://localhost:8000")
    print("\n  Nouveautes:")
    print("    - Tableaux Personnes, Zones, Equipes, Roles")
    print("    - Meilleure gestion des erreurs")
    print("    - Debug console (F12)")
    print("\n" + "=" * 60 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8003, log_level="info")