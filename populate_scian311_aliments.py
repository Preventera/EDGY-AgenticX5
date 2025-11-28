#!/usr/bin/env python3
"""
🛡️ Script de Population Neo4j - Secteurs SCIAN 311-312
Fabrication d'aliments et de boissons
EDGY-AgenticX5 | SafetyGraph | Preventera

Basé sur les données CNESST et Industrie Canada:
- Abattoirs et transformation de viande
- Fabrication de produits laitiers
- Boulangeries et produits de boulangerie
- Brasseries et fabrication de boissons
- Transformation de fruits et légumes

Secteurs inclus:
- 311611: Abattage d'animaux (sauf volailles)
- 311614: Transformation de la viande
- 311615: Transformation de la volaille
- 311511: Fabrication de lait de consommation
- 311515: Fabrication de beurre, fromage et produits laitiers secs
- 311811: Boulangeries de détail
- 311814: Boulangeries commerciales
- 311420: Mise en conserve de fruits et légumes
- 311920: Fabrication de café et thé
- 312120: Brasseries
- 312130: Vineries
"""

import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

from src.cartography.connector import SafetyGraphCartographyConnector
from src.cartography.models import Organization, Person, Team, Role, Zone, Risk, RiskLevel, RelationType

# ============================================================================
# DONNÉES CNESST - SECTEURS SCIAN 311-312 (ALIMENTS ET BOISSONS)
# ============================================================================

SECTEURS_SCIAN_311 = {
    "311611": {
        "nom": "Abattage d'animaux (sauf volailles)",
        "description": "Abattoirs de bovins, porcs, agneaux",
        "risques": [
            {"desc": "Coupure couteau/scie à os", "cat": "mecanique", "prob": 5, "grav": 4},
            {"desc": "Amputation scie/équipement", "cat": "mecanique", "prob": 2, "grav": 5},
            {"desc": "TMS - mouvements répétitifs découpe", "cat": "ergonomique", "prob": 5, "grav": 4},
            {"desc": "Glissade plancher mouillé/sang", "cat": "chute", "prob": 5, "grav": 3},
            {"desc": "Écrasement animal vivant", "cat": "mecanique", "prob": 3, "grav": 4},
            {"desc": "Exposition agents biologiques (zoonoses)", "cat": "biologique", "prob": 4, "grav": 4},
            {"desc": "Bruit équipements >85dB", "cat": "bruit", "prob": 5, "grav": 3},
            {"desc": "Exposition froid (chambre froide)", "cat": "thermique", "prob": 4, "grav": 3},
            {"desc": "Stress cadence élevée", "cat": "psychosocial", "prob": 5, "grav": 3},
        ],
        "zones": [
            {"nom": "Zone d'abattage", "risk": "critique", "dangers": ["Coupure", "Animal", "Sang"], "epi": ["Tablier mailles", "Gants mailles", "Casque", "Bottes"]},
            {"nom": "Salle de découpe", "risk": "critique", "dangers": ["Coupure", "TMS", "Glissade"], "epi": ["Gants mailles", "Tablier", "Chaussures antidérapantes"]},
            {"nom": "Chambre froide -18°C", "risk": "eleve", "dangers": ["Froid", "Glissade"], "epi": ["Vêtements isolants", "Crampons"]},
            {"nom": "Quai réception animaux", "risk": "eleve", "dangers": ["Animal", "Véhicule"], "epi": ["Bottes", "Casque"]},
        ],
        "roles": ["Abatteur", "Désosseur", "Découpeur viande", "Opérateur scie", "Inspecteur ACIA", "Contremaître abattage", "Directeur usine"],
        "certs": ["Manipulation animaux", "SIMDUT", "Premiers soins", "HACCP", "Travail au froid"],
    },
    
    "311614": {
        "nom": "Transformation de la viande",
        "description": "Charcuterie, saucisses, viandes fumées",
        "risques": [
            {"desc": "Coupure équipement tranchage", "cat": "mecanique", "prob": 4, "grav": 4},
            {"desc": "Brûlure fumoir/cuisson", "cat": "thermique", "prob": 3, "grav": 4},
            {"desc": "TMS - mouvements répétitifs", "cat": "ergonomique", "prob": 5, "grav": 3},
            {"desc": "Coincement machine à saucisse", "cat": "mecanique", "prob": 2, "grav": 4},
            {"desc": "Exposition nitrites/additifs", "cat": "chimique", "prob": 3, "grav": 3},
            {"desc": "Glissade plancher gras", "cat": "chute", "prob": 4, "grav": 3},
            {"desc": "Bruit machinerie", "cat": "bruit", "prob": 4, "grav": 3},
        ],
        "zones": [
            {"nom": "Salle de production", "risk": "eleve", "dangers": ["Machines", "Coupure", "TMS"], "epi": ["Gants", "Tablier", "Lunettes"]},
            {"nom": "Fumoir", "risk": "eleve", "dangers": ["Chaleur", "Fumée"], "epi": ["Gants chaleur", "Masque"]},
            {"nom": "Salle d'emballage", "risk": "moyen", "dangers": ["TMS", "Machines"], "epi": ["Gants", "Tablier"]},
            {"nom": "Chambre réfrigérée", "risk": "moyen", "dangers": ["Froid"], "epi": ["Vêtements chauds"]},
        ],
        "roles": ["Opérateur production", "Fumeur viande", "Préposé emballage", "Technicien qualité", "Chef de production", "Directeur usine"],
        "certs": ["HACCP", "SIMDUT", "Premiers soins", "Salubrité alimentaire"],
    },
    
    "311615": {
        "nom": "Transformation de la volaille",
        "description": "Abattage et transformation poulet, dinde",
        "risques": [
            {"desc": "Coupure couteau/cisaille", "cat": "mecanique", "prob": 5, "grav": 4},
            {"desc": "TMS - cadence très élevée", "cat": "ergonomique", "prob": 5, "grav": 4},
            {"desc": "Exposition agents biologiques (salmonelle)", "cat": "biologique", "prob": 4, "grav": 4},
            {"desc": "Syndrome tunnel carpien", "cat": "ergonomique", "prob": 5, "grav": 4},
            {"desc": "Glissade plancher mouillé", "cat": "chute", "prob": 5, "grav": 3},
            {"desc": "Bruit chaîne d'abattage >90dB", "cat": "bruit", "prob": 5, "grav": 3},
            {"desc": "Exposition ammoniac (réfrigération)", "cat": "chimique", "prob": 2, "grav": 5},
        ],
        "zones": [
            {"nom": "Chaîne d'abattage volaille", "risk": "critique", "dangers": ["Coupure", "TMS", "Biologique"], "epi": ["Gants mailles", "Tablier", "Masque"]},
            {"nom": "Salle d'éviscération", "risk": "critique", "dangers": ["Coupure", "Biologique"], "epi": ["Équipement complet"]},
            {"nom": "Zone de découpe", "risk": "eleve", "dangers": ["Coupure", "TMS"], "epi": ["Gants mailles", "Tablier"]},
            {"nom": "Salle mécanique NH3", "risk": "critique", "dangers": ["Ammoniac", "Froid"], "epi": ["SCBA", "Détecteur NH3"]},
        ],
        "roles": ["Préposé abattage", "Éviscéreur", "Découpeur volaille", "Opérateur chaîne", "Technicien réfrigération", "Superviseur", "Directeur usine"],
        "certs": ["HACCP", "SIMDUT", "Ammoniac", "Premiers soins", "Salubrité"],
    },
    
    "311511": {
        "nom": "Fabrication de lait de consommation",
        "description": "Laiteries, pasteurisation, embouteillage",
        "risques": [
            {"desc": "Brûlure vapeur/pasteurisation", "cat": "thermique", "prob": 3, "grav": 4},
            {"desc": "Glissade plancher lait renversé", "cat": "chute", "prob": 4, "grav": 3},
            {"desc": "TMS - levage/manutention", "cat": "ergonomique", "prob": 4, "grav": 3},
            {"desc": "Exposition produits nettoyage CIP", "cat": "chimique", "prob": 3, "grav": 4},
            {"desc": "Coincement convoyeur/machine", "cat": "mecanique", "prob": 2, "grav": 4},
            {"desc": "Bruit équipements", "cat": "bruit", "prob": 4, "grav": 3},
        ],
        "zones": [
            {"nom": "Salle de pasteurisation", "risk": "eleve", "dangers": ["Vapeur", "Chaleur", "CIP"], "epi": ["Gants chaleur", "Lunettes", "Tablier"]},
            {"nom": "Ligne d'embouteillage", "risk": "eleve", "dangers": ["Machine", "Bruit"], "epi": ["Lunettes", "Bouchons"]},
            {"nom": "Réception lait cru", "risk": "moyen", "dangers": ["Citerne", "Glissade"], "epi": ["Bottes", "Gants"]},
            {"nom": "Entrepôt réfrigéré", "risk": "moyen", "dangers": ["Froid", "Chariot"], "epi": ["Vêtements chauds"]},
        ],
        "roles": ["Opérateur pasteurisation", "Opérateur embouteillage", "Préposé réception", "Technicien qualité", "Mécanicien", "Chef de production"],
        "certs": ["HACCP", "SIMDUT", "Premiers soins", "Chariot élévateur", "CIP"],
    },
    
    "311515": {
        "nom": "Fabrication de fromage et produits laitiers",
        "description": "Fromageries, fabrication beurre, yogourt",
        "risques": [
            {"desc": "Brûlure lait/caillé chaud", "cat": "thermique", "prob": 3, "grav": 4},
            {"desc": "TMS - manipulation meules fromage", "cat": "ergonomique", "prob": 4, "grav": 4},
            {"desc": "Glissade plancher mouillé/lactose", "cat": "chute", "prob": 4, "grav": 3},
            {"desc": "Exposition moisissures (affinage)", "cat": "biologique", "prob": 3, "grav": 3},
            {"desc": "Coincement presse à fromage", "cat": "mecanique", "prob": 2, "grav": 4},
            {"desc": "Exposition produits nettoyage", "cat": "chimique", "prob": 3, "grav": 3},
        ],
        "zones": [
            {"nom": "Cuve de fabrication", "risk": "eleve", "dangers": ["Chaleur", "Glissade"], "epi": ["Bottes", "Tablier", "Gants"]},
            {"nom": "Salle d'affinage", "risk": "moyen", "dangers": ["Moisissures", "TMS"], "epi": ["Masque", "Gants"]},
            {"nom": "Salle de pressage", "risk": "eleve", "dangers": ["Machine", "TMS"], "epi": ["Gants", "Chaussures sécurité"]},
            {"nom": "Emballage", "risk": "moyen", "dangers": ["TMS"], "epi": ["Gants"]},
        ],
        "roles": ["Fromager", "Affineur", "Opérateur cuve", "Préposé emballage", "Technicien qualité", "Maître fromager", "Directeur production"],
        "certs": ["HACCP", "SIMDUT", "Premiers soins", "Salubrité alimentaire"],
    },
    
    "311814": {
        "nom": "Boulangeries commerciales",
        "description": "Fabrication pain industriel, pâtisseries",
        "risques": [
            {"desc": "Brûlure four industriel", "cat": "thermique", "prob": 4, "grav": 4},
            {"desc": "TMS - pétrissage/manutention", "cat": "ergonomique", "prob": 5, "grav": 3},
            {"desc": "Coincement pétrin/laminoir", "cat": "mecanique", "prob": 2, "grav": 5},
            {"desc": "Inhalation farine (asthme boulanger)", "cat": "chimique", "prob": 4, "grav": 4},
            {"desc": "Glissade plancher farine/huile", "cat": "chute", "prob": 4, "grav": 3},
            {"desc": "Bruit équipements", "cat": "bruit", "prob": 4, "grav": 3},
            {"desc": "Travail de nuit/fatigue", "cat": "psychosocial", "prob": 4, "grav": 3},
        ],
        "zones": [
            {"nom": "Zone pétrissage", "risk": "eleve", "dangers": ["Machine", "Farine", "TMS"], "epi": ["Masque poussière", "Gants"]},
            {"nom": "Zone cuisson/fours", "risk": "critique", "dangers": ["Chaleur", "Brûlure"], "epi": ["Gants chaleur", "Tablier"]},
            {"nom": "Ligne d'emballage", "risk": "moyen", "dangers": ["Machine", "TMS"], "epi": ["Gants", "Tablier"]},
            {"nom": "Entrepôt matières premières", "risk": "moyen", "dangers": ["Farine", "Chariot"], "epi": ["Masque", "Chaussures sécurité"]},
        ],
        "roles": ["Boulanger industriel", "Opérateur four", "Opérateur pétrin", "Préposé emballage", "Chef boulanger", "Directeur production"],
        "certs": ["HACCP", "SIMDUT", "Premiers soins", "Travail chaleur", "Protection respiratoire"],
    },
    
    "311420": {
        "nom": "Mise en conserve de fruits et légumes",
        "description": "Conserveries, congélation fruits et légumes",
        "risques": [
            {"desc": "Coupure équipement tranchage", "cat": "mecanique", "prob": 4, "grav": 4},
            {"desc": "Brûlure vapeur/autoclave", "cat": "thermique", "prob": 3, "grav": 5},
            {"desc": "TMS - travail répétitif saisonnier", "cat": "ergonomique", "prob": 5, "grav": 3},
            {"desc": "Glissade plancher mouillé", "cat": "chute", "prob": 4, "grav": 3},
            {"desc": "Exposition pesticides résiduels", "cat": "chimique", "prob": 2, "grav": 3},
            {"desc": "Bruit machinerie conserverie", "cat": "bruit", "prob": 4, "grav": 3},
        ],
        "zones": [
            {"nom": "Ligne de lavage/tri", "risk": "moyen", "dangers": ["Glissade", "TMS"], "epi": ["Bottes", "Tablier", "Gants"]},
            {"nom": "Zone de coupe/préparation", "risk": "eleve", "dangers": ["Coupure", "TMS"], "epi": ["Gants mailles", "Tablier"]},
            {"nom": "Salle autoclave", "risk": "critique", "dangers": ["Vapeur", "Pression"], "epi": ["Gants chaleur", "Lunettes"]},
            {"nom": "Congélateur IQF", "risk": "eleve", "dangers": ["Froid extrême"], "epi": ["Combinaison grand froid"]},
        ],
        "roles": ["Préposé tri", "Opérateur coupe", "Opérateur autoclave", "Préposé emballage", "Technicien qualité", "Chef de ligne", "Directeur usine"],
        "certs": ["HACCP", "SIMDUT", "Premiers soins", "Autoclave", "Travail au froid"],
    },
    
    "312120": {
        "nom": "Brasseries",
        "description": "Fabrication de bière",
        "risques": [
            {"desc": "Asphyxie CO2 (fermentation)", "cat": "chimique", "prob": 2, "grav": 5},
            {"desc": "Brûlure moût/vapeur", "cat": "thermique", "prob": 3, "grav": 4},
            {"desc": "Glissade plancher mouillé/houblon", "cat": "chute", "prob": 4, "grav": 3},
            {"desc": "Exposition produits nettoyage CIP", "cat": "chimique", "prob": 3, "grav": 4},
            {"desc": "TMS - manipulation fûts/caisses", "cat": "ergonomique", "prob": 4, "grav": 3},
            {"desc": "Espace clos (cuve fermentation)", "cat": "chimique", "prob": 2, "grav": 5},
            {"desc": "Bruit embouteillage", "cat": "bruit", "prob": 4, "grav": 3},
        ],
        "zones": [
            {"nom": "Salle de brassage", "risk": "eleve", "dangers": ["Vapeur", "Chaleur", "Glissade"], "epi": ["Bottes", "Lunettes", "Gants"]},
            {"nom": "Cuves de fermentation", "risk": "critique", "dangers": ["CO2", "Espace clos"], "epi": ["Détecteur CO2", "Harnais"]},
            {"nom": "Ligne d'embouteillage", "risk": "eleve", "dangers": ["Machine", "Bruit", "Verre"], "epi": ["Lunettes", "Bouchons", "Gants"]},
            {"nom": "Entrepôt fûts", "risk": "moyen", "dangers": ["TMS", "Chariot"], "epi": ["Chaussures sécurité", "Gants"]},
        ],
        "roles": ["Brasseur", "Opérateur fermentation", "Opérateur embouteillage", "Préposé entrepôt", "Technicien qualité", "Maître brasseur", "Directeur brasserie"],
        "certs": ["SIMDUT", "Espace clos", "Détection gaz", "HACCP", "Premiers soins", "Chariot élévateur"],
    },
    
    "312130": {
        "nom": "Vineries",
        "description": "Fabrication de vin, cidre",
        "risques": [
            {"desc": "Asphyxie CO2 (fermentation)", "cat": "chimique", "prob": 2, "grav": 5},
            {"desc": "Intoxication SO2 (sulfites)", "cat": "chimique", "prob": 3, "grav": 4},
            {"desc": "Chute échelle/cuve", "cat": "chute", "prob": 3, "grav": 4},
            {"desc": "TMS - manipulation barils", "cat": "ergonomique", "prob": 4, "grav": 3},
            {"desc": "Glissade cave humide", "cat": "chute", "prob": 4, "grav": 3},
            {"desc": "Espace clos (cuve inox)", "cat": "chimique", "prob": 2, "grav": 5},
        ],
        "zones": [
            {"nom": "Salle de vinification", "risk": "eleve", "dangers": ["CO2", "SO2", "Glissade"], "epi": ["Détecteur gaz", "Bottes", "Lunettes"]},
            {"nom": "Cave à barriques", "risk": "eleve", "dangers": ["CO2", "Humidité", "TMS"], "epi": ["Détecteur CO2", "Bottes"]},
            {"nom": "Ligne d'embouteillage", "risk": "moyen", "dangers": ["Machine", "Verre"], "epi": ["Lunettes", "Gants"]},
            {"nom": "Vignoble (vendanges)", "risk": "moyen", "dangers": ["Soleil", "Insectes", "TMS"], "epi": ["Chapeau", "Gants"]},
        ],
        "roles": ["Vinificateur", "Caviste", "Opérateur embouteillage", "Ouvrier viticole", "Œnologue", "Maître de chai", "Directeur domaine"],
        "certs": ["SIMDUT", "Espace clos", "Détection gaz", "HACCP", "Premiers soins"],
    },
}

# ORGANISATIONS AGROALIMENTAIRES QUÉBÉCOISES À CRÉER
ORGANISATIONS_SCIAN_311 = [
    # Abattage bovins/porcs (311611)
    {"name": "Olymel - Vallée-Jonction", "sector": "311611", "nb": 1800, "region": "Chaudière-Appalaches"},
    {"name": "Olymel - Saint-Esprit", "sector": "311611", "nb": 1200, "region": "Lanaudière"},
    {"name": "Viandes du Breton", "sector": "311611", "nb": 450, "region": "Bas-Saint-Laurent"},
    {"name": "Abattoir Colbex", "sector": "311611", "nb": 280, "region": "Montérégie"},
    
    # Transformation viande (311614)
    {"name": "Olymel - Anjou (charcuterie)", "sector": "311614", "nb": 650, "region": "Montréal"},
    {"name": "Aliments Maple Leaf - Laval", "sector": "311614", "nb": 480, "region": "Laval"},
    {"name": "Les Viandes Laroche", "sector": "311614", "nb": 180, "region": "Montréal"},
    
    # Transformation volaille (311615)
    {"name": "Exceldor Coopérative - Saint-Anselme", "sector": "311615", "nb": 1400, "region": "Chaudière-Appalaches"},
    {"name": "Exceldor - Saint-Bruno", "sector": "311615", "nb": 850, "region": "Montérégie"},
    {"name": "Volailles Grenville", "sector": "311615", "nb": 320, "region": "Laurentides"},
    
    # Laiteries (311511)
    {"name": "Agropur - Granby", "sector": "311511", "nb": 650, "region": "Estrie"},
    {"name": "Lactantia/Parmalat - Victoriaville", "sector": "311511", "nb": 380, "region": "Centre-du-Québec"},
    {"name": "Natrel - Montréal", "sector": "311511", "nb": 320, "region": "Montréal"},
    
    # Fromageries (311515)
    {"name": "Saputo - Montréal", "sector": "311515", "nb": 850, "region": "Montréal"},
    {"name": "Agropur - Notre-Dame-du-Bon-Conseil", "sector": "311515", "nb": 420, "region": "Centre-du-Québec"},
    {"name": "Fromagerie Perron", "sector": "311515", "nb": 85, "region": "Saguenay"},
    {"name": "Fromagerie du Village", "sector": "311515", "nb": 45, "region": "Montérégie"},
    
    # Boulangeries commerciales (311814)
    {"name": "Boulangerie St-Méthode", "sector": "311814", "nb": 450, "region": "Centre-du-Québec"},
    {"name": "Gadoua (Grupo Bimbo)", "sector": "311814", "nb": 380, "region": "Montréal"},
    {"name": "Boulangerie Première Moisson", "sector": "311814", "nb": 280, "region": "Montréal"},
    {"name": "Vachon (Hostess)", "sector": "311814", "nb": 350, "region": "Montérégie"},
    
    # Conserveries (311420)
    {"name": "Bonduelle Amérique du Nord", "sector": "311420", "nb": 450, "region": "Montérégie"},
    {"name": "Aliments Whyte's", "sector": "311420", "nb": 180, "region": "Centre-du-Québec"},
    {"name": "Fruits de mer Océan", "sector": "311420", "nb": 120, "region": "Gaspésie"},
    
    # Brasseries (312120)
    {"name": "Molson Coors - Montréal", "sector": "312120", "nb": 850, "region": "Montréal"},
    {"name": "Labatt - LaSalle", "sector": "312120", "nb": 420, "region": "Montréal"},
    {"name": "Unibroue", "sector": "312120", "nb": 180, "region": "Montérégie"},
    {"name": "Microbrasserie Le Trou du Diable", "sector": "312120", "nb": 85, "region": "Mauricie"},
    
    # Vineries (312130)
    {"name": "Vignoble Rivière du Chêne", "sector": "312130", "nb": 45, "region": "Laurentides"},
    {"name": "Domaine Pinnacle (cidre)", "sector": "312130", "nb": 35, "region": "Estrie"},
    {"name": "Vignoble de l'Orpailleur", "sector": "312130", "nb": 28, "region": "Montérégie"},
]

AGES = ["18-24", "25-34", "35-44", "45-54", "55-64"]


def populate_scian311():
    """Peuple SafetyGraph avec les secteurs SCIAN 311-312 (Aliments et boissons)"""
    
    print("=" * 70)
    print("🍖🍞🧀🍺 POPULATION SAFETYGRAPH - SCIAN 311-312")
    print("    Fabrication d'aliments et de boissons")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Secteurs: {len(SECTEURS_SCIAN_311)}")
    print(f"Organisations: {len(ORGANISATIONS_SCIAN_311)}")
    print("=" * 70)
    
    conn = SafetyGraphCartographyConnector()
    conn.connect()
    print("\n✅ Neo4j connecté")
    print(f"📊 Stats initiales: {conn.get_graph_stats()}\n")
    
    stats = {"orgs": 0, "zones": 0, "risks": 0, "persons": 0, "teams": 0, "roles": 0}
    
    # Créer organisations
    print("📦 Création des organisations SCIAN 311-312 (AGROALIMENTAIRE)...")
    org_map = {}
    for o in ORGANISATIONS_SCIAN_311:
        org = Organization(
            name=o["name"],
            sector_scian=o["sector"],
            nb_employes=o["nb"],
            region_ssq=o["region"]
        )
        oid = conn.inject_organization(org)
        org_map[o["name"]] = {"id": oid, "sector": o["sector"], "nb": o["nb"]}
        stats["orgs"] += 1
        print(f"   ✅ {o['name'][:40]} ({o['sector']})")
    
    # Créer entités par organisation
    print("\n🏗️ Création des entités par organisation...")
    
    for name, info in org_map.items():
        oid, sector = info["id"], info["sector"]
        data = SECTEURS_SCIAN_311[sector]
        
        # Icône selon secteur
        if "311611" in sector or "311614" in sector:
            icon = "🍖"
        elif "311615" in sector:
            icon = "🍗"
        elif "311511" in sector or "311515" in sector:
            icon = "🧀"
        elif "311814" in sector:
            icon = "🍞"
        elif "311420" in sector:
            icon = "🥫"
        elif "312120" in sector:
            icon = "🍺"
        elif "312130" in sector:
            icon = "🍷"
        else:
            icon = "🏭"
            
        print(f"\n   {icon} {name[:40]}")
        print(f"      Secteur: {data['nom']}")
        
        # Rôles
        rids = []
        for r in data["roles"]:
            is_sup = any(x in r for x in ["Chef", "Directeur", "Maître", "Superviseur", "Contremaître"])
            role = Role(name=r, niveau_hierarchique=3 if is_sup else 1, autorite_arret_travail=is_sup)
            rids.append(conn.inject_role(role))
            stats["roles"] += 1
        print(f"      • {len(rids)} rôles")
        
        # Zones
        zids = []
        for z in data["zones"]:
            zone = Zone(
                name=z["nom"],
                risk_level=RiskLevel(z["risk"]),
                dangers_identifies=z["dangers"],
                epi_requis=z["epi"]
            )
            zid = conn.inject_zone(zone)
            zids.append(zid)
            conn.create_relation(zid, oid, RelationType.APPARTIENT_A)
            stats["zones"] += 1
        nb_critique = sum(1 for z in data["zones"] if z["risk"] == "critique")
        print(f"      • {len(zids)} zones (🔴 critique: {nb_critique})")
        
        # Risques
        rkids = []
        for i, r in enumerate(data["risques"]):
            risk = Risk(
                description=r["desc"],
                categorie=r["cat"],
                probabilite=r["prob"],
                gravite=r["grav"],
                statut="actif"
            )
            rid = conn.inject_risk(risk)
            rkids.append(rid)
            if zids:
                conn.create_relation(rid, zids[i % len(zids)], RelationType.LOCALISE_DANS)
            stats["risks"] += 1
        max_score = max(r["prob"]*r["grav"] for r in data["risques"])
        print(f"      • {len(rkids)} risques (score EDGY max: {max_score})")
        
        # Équipes
        tids = []
        equipes = ["Équipe Jour", "Équipe Soir", "Équipe Nuit"] if info["nb"] > 200 else ["Équipe Production", "Équipe Qualité"]
            
        for t in equipes:
            team = Team(name=t, department=data["nom"][:25])
            tid = conn.inject_team(team)
            tids.append(tid)
            conn.create_relation(tid, oid, RelationType.APPARTIENT_A)
            stats["teams"] += 1
        print(f"      • {len(tids)} équipes")
        
        # Personnes
        nb_persons = max(5, min(info["nb"] // 100, 25))
        for i in range(nb_persons):
            p = Person(
                matricule=f"ALIM311-{sector[-3:]}-{stats['persons']+1:04d}",
                department=data["nom"][:25],
                age_groupe=AGES[i % 5],
                certifications_sst=data["certs"][:4]
            )
            pid = conn.inject_person(p, anonymize=True)
            stats["persons"] += 1
            
            # Relations
            if tids:
                conn.create_relation(pid, tids[i % len(tids)], RelationType.MEMBRE_DE)
            if rids:
                conn.create_relation(pid, rids[i % len(rids)], RelationType.OCCUPE_ROLE)
            if zids:
                conn.create_relation(pid, zids[i % len(zids)], RelationType.TRAVAILLE_DANS)
            # Exposition aux risques (85% personnel agroalimentaire exposé)
            if rkids and i % 10 < 8:
                conn.create_relation(pid, rkids[i % len(rkids)], RelationType.EXPOSE_A)
        
        print(f"      • {nb_persons} personnes (anonymisées Loi 25)")
    
    # Résumé
    print("\n" + "=" * 70)
    print("📊 RÉSUMÉ POPULATION SCIAN 311-312 - AGROALIMENTAIRE")
    print("=" * 70)
    print(f"   Organisations: {stats['orgs']}")
    print(f"   Zones de travail: {stats['zones']}")
    print(f"   Risques identifiés: {stats['risks']}")
    print(f"   Équipes: {stats['teams']}")
    print(f"   Rôles/Professions: {stats['roles']}")
    print(f"   Personnes: {stats['persons']}")
    print(f"\n   Neo4j final: {conn.get_graph_stats()}")
    print("=" * 70)
    print("✅ POPULATION SCIAN 311-312 (AGROALIMENTAIRE) TERMINÉE!")
    print("=" * 70)
    
    conn.close()
    return stats


if __name__ == "__main__":
    populate_scian311()
