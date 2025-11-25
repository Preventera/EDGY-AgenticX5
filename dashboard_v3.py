#!/usr/bin/env python3
"""
Dashboard EDGY-AgenticX5 v3.0
Avec Organigramme Plotly interactif
"""

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="EDGY Dashboard v3.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    """Dashboard React avec Organigramme Plotly"""
    html = """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EDGY-AgenticX5 Dashboard v3.0</title>
    <script src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
    <script src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
</head>
<body>
    <div id="root"></div>
    
    <script type="text/babel">
        const { useState, useEffect, useRef } = React;
        
        const Dashboard = () => {
            const [data, setData] = useState(null);
            const [loading, setLoading] = useState(true);
            const [activeTab, setActiveTab] = useState('overview');
            const orgChartRef = useRef(null);
            const relationsChartRef = useRef(null);
            const riskChartRef = useRef(null);
            
            const loadData = async () => {
                setLoading(true);
                try {
                    const statsResp = await fetch('http://localhost:8000/cartography/stats');
                    const stats = await statsResp.json();
                    
                    let persons = [];
                    try {
                        const resp = await fetch('http://localhost:8000/cartography/persons');
                        const data = await resp.json();
                        persons = Array.isArray(data) ? data : Object.values(data);
                    } catch (e) { console.error(e); }
                    
                    let zones = [];
                    try {
                        const resp = await fetch('http://localhost:8000/cartography/zones');
                        const data = await resp.json();
                        zones = Array.isArray(data) ? data : Object.values(data);
                    } catch (e) { console.error(e); }
                    
                    let teams = [];
                    try {
                        const resp = await fetch('http://localhost:8000/cartography/teams');
                        const data = await resp.json();
                        teams = Array.isArray(data) ? data : Object.values(data);
                    } catch (e) { console.error(e); }
                    
                    let roles = [];
                    try {
                        const resp = await fetch('http://localhost:8000/cartography/roles');
                        const data = await resp.json();
                        roles = Array.isArray(data) ? data : Object.values(data);
                    } catch (e) { console.error(e); }
                    
                    let organizations = [];
                    try {
                        const resp = await fetch('http://localhost:8000/cartography/organizations');
                        const data = await resp.json();
                        organizations = Array.isArray(data) ? data : Object.values(data);
                    } catch (e) { console.error(e); }
                    
                    const highRiskZones = zones.filter(z => 
                        z.risk_level === 'eleve' || z.risk_level === 'critique'
                    ).length;
                    
                    setData({
                        stats, persons, zones, teams, roles, organizations,
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
                    console.error('Erreur:', err);
                } finally {
                    setLoading(false);
                }
            };
            
            // Render Org Chart - Sunburst (better for hierarchy)
            const renderOrgChart = () => {
                if (!orgChartRef.current || !data) return;
                
                const teams = data.teams || [];
                const persons = data.persons || [];
                const orgs = data.organizations || [];
                
                // Si pas de données, afficher un message
                if (persons.length === 0 && teams.length === 0) {
                    orgChartRef.current.innerHTML = '<div style="display:flex;align-items:center;justify-content:center;height:100%;color:#666;font-size:18px;">Aucune donnee pour organigramme</div>';
                    return;
                }
                
                // Build hierarchy - IMPORTANT: single root
                const ids = [];
                const labels = [];
                const parents = [];
                const colors = [];
                
                // Root - Organisation (ID unique)
                const rootId = 'root';
                const rootLabel = orgs.length > 0 ? (orgs[0].name || 'Organisation') : 'EDGY-AgenticX5';
                ids.push(rootId);
                labels.push(rootLabel);
                parents.push('');
                colors.push('#3B82F6');
                
                // Group persons by department
                const deptMap = {};
                persons.forEach(p => {
                    const dept = p.department || 'Autres';
                    if (!deptMap[dept]) deptMap[dept] = [];
                    deptMap[dept].push(p);
                });
                
                // Add departments as second level (with unique IDs)
                const deptIds = {};
                Object.keys(deptMap).forEach((dept, idx) => {
                    const deptId = 'dept_' + idx;
                    deptIds[dept] = deptId;
                    ids.push(deptId);
                    labels.push(dept);
                    parents.push(rootId);  // Parent is root
                    colors.push('#10B981');
                });
                
                // Add persons under their department (with unique IDs)
                let personIdx = 0;
                Object.entries(deptMap).forEach(([dept, pList]) => {
                    const deptId = deptIds[dept];
                    pList.forEach(p => {
                        const personId = 'person_' + personIdx++;
                        ids.push(personId);
                        labels.push(p.name || 'Employe');
                        parents.push(deptId);  // Parent is department
                        colors.push('#8B5CF6');
                    });
                });
                
                const trace = {
                    type: 'sunburst',
                    ids: ids,
                    labels: labels,
                    parents: parents,
                    branchvalues: 'total',
                    textinfo: 'label',
                    insidetextorientation: 'radial',
                    marker: {
                        colors: colors,
                        line: { width: 2, color: 'white' }
                    },
                    hovertemplate: '<b>%{label}</b><extra></extra>'
                };
                
                const layout = {
                    title: {
                        text: '🏢 Organigramme Hierarchique',
                        font: { size: 20, color: '#1F2937' }
                    },
                    margin: { t: 50, l: 10, r: 10, b: 10 },
                    paper_bgcolor: 'rgba(0,0,0,0)'
                };
                
                Plotly.newPlot(orgChartRef.current, [trace], layout, {responsive: true});
            };
            
            // Render Risk Chart
            const renderRiskChart = () => {
                if (!riskChartRef.current || !data) return;
                
                const zones = data.zones || [];
                const riskCounts = {
                    'critique': 0,
                    'eleve': 0,
                    'moyen': 0,
                    'faible': 0
                };
                
                zones.forEach(z => {
                    const level = z.risk_level || 'faible';
                    if (riskCounts[level] !== undefined) {
                        riskCounts[level]++;
                    }
                });
                
                const trace = {
                    type: 'pie',
                    labels: ['Critique', 'Eleve', 'Moyen', 'Faible'],
                    values: [riskCounts.critique, riskCounts.eleve, riskCounts.moyen, riskCounts.faible],
                    marker: {
                        colors: ['#DC2626', '#F97316', '#EAB308', '#22C55E']
                    },
                    hole: 0.4,
                    textinfo: 'label+value',
                    hovertemplate: '<b>%{label}</b><br>%{value} zones<br>%{percent}<extra></extra>'
                };
                
                const layout = {
                    title: {
                        text: '⚠️ Repartition des Risques',
                        font: { size: 20, color: '#1F2937' }
                    },
                    showlegend: true,
                    legend: { orientation: 'h', y: -0.1 },
                    margin: { t: 50, l: 10, r: 10, b: 50 },
                    paper_bgcolor: 'rgba(0,0,0,0)'
                };
                
                Plotly.newPlot(riskChartRef.current, [trace], layout, {responsive: true});
            };
            
            // Render Stats Bar Chart
            const renderStatsChart = () => {
                if (!relationsChartRef.current || !data) return;
                
                const stats = data.stats || {};
                
                const trace = {
                    type: 'bar',
                    x: ['Organisations', 'Personnes', 'Equipes', 'Roles', 'Zones', 'Processus', 'Relations'],
                    y: [
                        stats.organizations || 0,
                        stats.persons || 0,
                        stats.teams || 0,
                        stats.roles || 0,
                        stats.zones || 0,
                        stats.processes || 0,
                        stats.relations || 0
                    ],
                    marker: {
                        color: ['#3B82F6', '#10B981', '#8B5CF6', '#F97316', '#EC4899', '#06B6D4', '#6366F1']
                    },
                    text: [
                        stats.organizations || 0,
                        stats.persons || 0,
                        stats.teams || 0,
                        stats.roles || 0,
                        stats.zones || 0,
                        stats.processes || 0,
                        stats.relations || 0
                    ],
                    textposition: 'outside'
                };
                
                const layout = {
                    title: {
                        text: '📊 Statistiques par Type',
                        font: { size: 20, color: '#1F2937' }
                    },
                    xaxis: { tickangle: -45 },
                    yaxis: { title: 'Nombre' },
                    margin: { t: 50, l: 50, r: 20, b: 100 },
                    paper_bgcolor: 'rgba(0,0,0,0)',
                    plot_bgcolor: 'rgba(0,0,0,0)'
                };
                
                Plotly.newPlot(relationsChartRef.current, [trace], layout, {responsive: true});
            };
            
            useEffect(() => {
                loadData();
            }, []);
            
            useEffect(() => {
                if (data && activeTab === 'charts') {
                    setTimeout(() => {
                        renderOrgChart();
                        renderRiskChart();
                        renderStatsChart();
                    }, 100);
                }
            }, [data, activeTab]);
            
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
                            <button onClick={loadData} className="mt-4 px-6 py-2 bg-red-600 text-white rounded">
                                Reessayer
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
                <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
                    {/* Header */}
                    <div className="bg-white shadow-lg sticky top-0 z-50">
                        <div className="max-w-7xl mx-auto px-4 py-4">
                            <div className="flex justify-between items-center">
                                <div>
                                    <h1 className="text-3xl font-bold text-gray-900">EDGY-AgenticX5</h1>
                                    <p className="text-gray-600">Cartographie Organisationnelle & SST</p>
                                </div>
                                <button onClick={loadData} className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition shadow">
                                    🔄 Actualiser
                                </button>
                            </div>
                            
                            {/* Tabs */}
                            <div className="flex space-x-4 mt-4">
                                <button 
                                    onClick={() => setActiveTab('overview')}
                                    className={`px-4 py-2 rounded-lg font-medium transition ${
                                        activeTab === 'overview' 
                                            ? 'bg-blue-600 text-white' 
                                            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                                    }`}
                                >
                                    📋 Vue d'ensemble
                                </button>
                                <button 
                                    onClick={() => setActiveTab('charts')}
                                    className={`px-4 py-2 rounded-lg font-medium transition ${
                                        activeTab === 'charts' 
                                            ? 'bg-blue-600 text-white' 
                                            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                                    }`}
                                >
                                    📊 Graphiques & Organigramme
                                </button>
                                <button 
                                    onClick={() => setActiveTab('tables')}
                                    className={`px-4 py-2 rounded-lg font-medium transition ${
                                        activeTab === 'tables' 
                                            ? 'bg-blue-600 text-white' 
                                            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                                    }`}
                                >
                                    📑 Tableaux
                                </button>
                            </div>
                        </div>
                    </div>
                    
                    <div className="max-w-7xl mx-auto px-4 py-8">
                        {/* KPIs - Always visible */}
                        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-8">
                            <div className="bg-white rounded-xl shadow-lg p-4 hover:shadow-2xl transition">
                                <div className="text-sm text-gray-600">👥 Personnes</div>
                                <div className="text-3xl font-bold text-blue-600">{kpis.total_persons}</div>
                            </div>
                            <div className="bg-white rounded-xl shadow-lg p-4 hover:shadow-2xl transition">
                                <div className="text-sm text-gray-600">🏢 Equipes</div>
                                <div className="text-3xl font-bold text-green-600">{kpis.total_teams}</div>
                            </div>
                            <div className="bg-white rounded-xl shadow-lg p-4 hover:shadow-2xl transition">
                                <div className="text-sm text-gray-600">🛡️ Zones</div>
                                <div className="text-3xl font-bold text-purple-600">{kpis.total_zones}</div>
                            </div>
                            <div className="bg-white rounded-xl shadow-lg p-4 hover:shadow-2xl transition">
                                <div className="text-sm text-gray-600">⚙️ Processus</div>
                                <div className="text-3xl font-bold text-cyan-600">{kpis.total_processes}</div>
                            </div>
                            <div className="bg-white rounded-xl shadow-lg p-4 hover:shadow-2xl transition">
                                <div className="text-sm text-gray-600">🔗 Relations</div>
                                <div className="text-3xl font-bold text-indigo-600">{kpis.total_relations}</div>
                            </div>
                            <div className="bg-white rounded-xl shadow-lg p-4 hover:shadow-2xl transition border-2 border-red-500">
                                <div className="text-sm text-gray-600">⚠️ Risque Eleve</div>
                                <div className="text-3xl font-bold text-red-600">{kpis.high_risk_zones}</div>
                            </div>
                        </div>
                        
                        {/* Tab Content */}
                        {activeTab === 'overview' && (
                            <div className="space-y-8">
                                {/* Vue d'Ensemble */}
                                <div className="bg-white rounded-xl shadow-2xl p-6">
                                    <h2 className="text-2xl font-bold mb-4 text-gray-800">Vue d'Ensemble</h2>
                                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
                                        <div className="p-4 bg-blue-50 rounded-lg">
                                            <div className="text-2xl font-bold text-blue-700">{data.stats?.organizations || 0}</div>
                                            <div className="text-sm text-gray-600">Organisations</div>
                                        </div>
                                        <div className="p-4 bg-green-50 rounded-lg">
                                            <div className="text-2xl font-bold text-green-700">{persons.length}</div>
                                            <div className="text-sm text-gray-600">Employes</div>
                                        </div>
                                        <div className="p-4 bg-purple-50 rounded-lg">
                                            <div className="text-2xl font-bold text-purple-700">{teams.length}</div>
                                            <div className="text-sm text-gray-600">Equipes</div>
                                        </div>
                                        <div className="p-4 bg-orange-50 rounded-lg">
                                            <div className="text-2xl font-bold text-orange-700">{roles.length}</div>
                                            <div className="text-sm text-gray-600">Roles</div>
                                        </div>
                                    </div>
                                </div>
                                
                                {/* Quick Tables */}
                                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                                    <div className="bg-white rounded-xl shadow-2xl p-6">
                                        <h3 className="text-xl font-bold mb-4">👥 Personnes ({persons.length})</h3>
                                        <div className="overflow-auto max-h-64">
                                            <table className="w-full text-sm">
                                                <thead className="bg-gray-100">
                                                    <tr>
                                                        <th className="p-2 text-left">Nom</th>
                                                        <th className="p-2 text-left">Dept</th>
                                                    </tr>
                                                </thead>
                                                <tbody>
                                                    {persons.slice(0, 5).map((p, i) => (
                                                        <tr key={i} className="border-t hover:bg-blue-50">
                                                            <td className="p-2">{p.name}</td>
                                                            <td className="p-2 text-gray-600">{p.department || '-'}</td>
                                                        </tr>
                                                    ))}
                                                </tbody>
                                            </table>
                                            {persons.length > 5 && (
                                                <p className="text-center text-gray-500 mt-2">
                                                    +{persons.length - 5} autres...
                                                </p>
                                            )}
                                        </div>
                                    </div>
                                    
                                    <div className="bg-white rounded-xl shadow-2xl p-6">
                                        <h3 className="text-xl font-bold mb-4">🛡️ Zones ({zones.length})</h3>
                                        <div className="overflow-auto max-h-64">
                                            <table className="w-full text-sm">
                                                <thead className="bg-gray-100">
                                                    <tr>
                                                        <th className="p-2 text-left">Zone</th>
                                                        <th className="p-2 text-left">Risque</th>
                                                    </tr>
                                                </thead>
                                                <tbody>
                                                    {zones.slice(0, 5).map((z, i) => (
                                                        <tr key={i} className="border-t hover:bg-purple-50">
                                                            <td className="p-2">{z.name}</td>
                                                            <td className="p-2">
                                                                <span className={'px-2 py-1 rounded text-xs font-bold ' + (
                                                                    z.risk_level === 'critique' ? 'bg-red-600 text-white' :
                                                                    z.risk_level === 'eleve' ? 'bg-orange-500 text-white' :
                                                                    z.risk_level === 'moyen' ? 'bg-yellow-500 text-white' :
                                                                    'bg-green-500 text-white'
                                                                )}>
                                                                    {z.risk_level || 'faible'}
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
                        )}
                        
                        {activeTab === 'charts' && (
                            <div className="space-y-8">
                                {/* Org Chart */}
                                <div className="bg-white rounded-xl shadow-2xl p-6">
                                    <div ref={orgChartRef} style={{height: '400px'}}></div>
                                </div>
                                
                                {/* Risk & Stats Charts */}
                                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                                    <div className="bg-white rounded-xl shadow-2xl p-6">
                                        <div ref={riskChartRef} style={{height: '350px'}}></div>
                                    </div>
                                    <div className="bg-white rounded-xl shadow-2xl p-6">
                                        <div ref={relationsChartRef} style={{height: '350px'}}></div>
                                    </div>
                                </div>
                            </div>
                        )}
                        
                        {activeTab === 'tables' && (
                            <div className="space-y-8">
                                {/* Full Tables */}
                                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                                    {/* Persons Table */}
                                    <div className="bg-white rounded-xl shadow-2xl p-6">
                                        <h3 className="text-2xl font-bold mb-4">👥 Personnes ({persons.length})</h3>
                                        <div className="overflow-auto max-h-96">
                                            <table className="w-full text-sm">
                                                <thead className="sticky top-0 bg-gray-100">
                                                    <tr>
                                                        <th className="p-3 text-left">Nom</th>
                                                        <th className="p-3 text-left">Departement</th>
                                                        <th className="p-3 text-left">Email</th>
                                                    </tr>
                                                </thead>
                                                <tbody>
                                                    {persons.map((p, i) => (
                                                        <tr key={i} className="border-t hover:bg-blue-50">
                                                            <td className="p-3 font-medium">{p.name}</td>
                                                            <td className="p-3 text-gray-600">{p.department || '-'}</td>
                                                            <td className="p-3 text-gray-500">{p.email || '-'}</td>
                                                        </tr>
                                                    ))}
                                                </tbody>
                                            </table>
                                        </div>
                                    </div>
                                    
                                    {/* Zones Table */}
                                    <div className="bg-white rounded-xl shadow-2xl p-6">
                                        <h3 className="text-2xl font-bold mb-4">🛡️ Zones ({zones.length})</h3>
                                        <div className="overflow-auto max-h-96">
                                            <table className="w-full text-sm">
                                                <thead className="sticky top-0 bg-gray-100">
                                                    <tr>
                                                        <th className="p-3 text-left">Zone</th>
                                                        <th className="p-3 text-left">Type</th>
                                                        <th className="p-3 text-left">Risque</th>
                                                    </tr>
                                                </thead>
                                                <tbody>
                                                    {zones.map((z, i) => (
                                                        <tr key={i} className="border-t hover:bg-purple-50">
                                                            <td className="p-3 font-medium">{z.name}</td>
                                                            <td className="p-3 text-gray-600">{z.zone_type || '-'}</td>
                                                            <td className="p-3">
                                                                <span className={'px-3 py-1 rounded-full text-xs font-bold ' + (
                                                                    z.risk_level === 'critique' ? 'bg-red-600 text-white' :
                                                                    z.risk_level === 'eleve' ? 'bg-orange-500 text-white' :
                                                                    z.risk_level === 'moyen' ? 'bg-yellow-500 text-white' :
                                                                    'bg-green-500 text-white'
                                                                )}>
                                                                    {z.risk_level || 'faible'}
                                                                </span>
                                                            </td>
                                                        </tr>
                                                    ))}
                                                </tbody>
                                            </table>
                                        </div>
                                    </div>
                                </div>
                                
                                {/* Teams & Roles */}
                                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                                    <div className="bg-white rounded-xl shadow-2xl p-6">
                                        <h3 className="text-2xl font-bold mb-4">🏢 Equipes ({teams.length})</h3>
                                        <div className="overflow-auto max-h-96">
                                            <table className="w-full text-sm">
                                                <thead className="sticky top-0 bg-gray-100">
                                                    <tr>
                                                        <th className="p-3 text-left">Nom</th>
                                                        <th className="p-3 text-left">Description</th>
                                                    </tr>
                                                </thead>
                                                <tbody>
                                                    {teams.map((t, i) => (
                                                        <tr key={i} className="border-t hover:bg-green-50">
                                                            <td className="p-3 font-medium">{t.name}</td>
                                                            <td className="p-3 text-gray-600">{t.description || '-'}</td>
                                                        </tr>
                                                    ))}
                                                </tbody>
                                            </table>
                                        </div>
                                    </div>
                                    
                                    <div className="bg-white rounded-xl shadow-2xl p-6">
                                        <h3 className="text-2xl font-bold mb-4">🎭 Roles ({roles.length})</h3>
                                        <div className="overflow-auto max-h-96">
                                            <table className="w-full text-sm">
                                                <thead className="sticky top-0 bg-gray-100">
                                                    <tr>
                                                        <th className="p-3 text-left">Role</th>
                                                        <th className="p-3 text-left">Superviseur</th>
                                                    </tr>
                                                </thead>
                                                <tbody>
                                                    {roles.map((r, i) => (
                                                        <tr key={i} className="border-t hover:bg-orange-50">
                                                            <td className="p-3 font-medium">{r.name}</td>
                                                            <td className="p-3">
                                                                {r.can_supervise ? (
                                                                    <span className="px-2 py-1 bg-green-100 text-green-700 rounded text-xs">Oui</span>
                                                                ) : (
                                                                    <span className="px-2 py-1 bg-gray-100 text-gray-500 rounded text-xs">Non</span>
                                                                )}
                                                            </td>
                                                        </tr>
                                                    ))}
                                                </tbody>
                                            </table>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>
                    
                    {/* Footer */}
                    <div className="bg-white border-t mt-8 py-4 text-center text-gray-500 text-sm">
                        <p>EDGY-AgenticX5 Dashboard v3.0 | 
                            <a href="http://localhost:8000/docs" target="_blank" className="text-blue-600 hover:underline ml-2">API Docs</a>
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
    print("  EDGY-AgenticX5 Dashboard v3.0")
    print("=" * 60)
    print("\n  Dashboard: http://localhost:8003")
    print("  API:       http://localhost:8000")
    print("\n  Nouveautes v3.0:")
    print("    - Organigramme Plotly interactif (Treemap)")
    print("    - Graphique repartition des risques (Pie)")
    print("    - Graphique statistiques (Bar)")
    print("    - Navigation par onglets")
    print("    - Header sticky")
    print("\n" + "=" * 60 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8003, log_level="info")