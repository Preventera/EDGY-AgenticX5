#!/usr/bin/env python3
"""
🛡️ Script de Population Neo4j - Secteurs SCIAN 56
Services administratifs, de soutien, gestion des déchets et assainissement
EDGY-AgenticX5 | SafetyGraph | Preventera

Basé sur les données CNESST:
- Services de conciergerie et nettoyage
- Services de sécurité et surveillance
- Services d'aménagement paysager
- Gestion des déchets et recyclage

Secteurs inclus:
- 5611: Services de gestion de bureau
- 5613: Services de placement de personnel
- 5614: Services de soutien aux entreprises
- 5616: Services d'enquêtes et de sécurité
- 5617: Services relatifs aux bâtiments (nettoyage, conciergerie)
- 5619: Autres services de soutien
- 5621: Collecte des déchets
- 5622: Traitement et élimination des déchets
- 5629: Assainissement et autres services de gestion des déchets
"""

import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

from src.cartography.connector import SafetyGraphCartographyConnector
from src.cartography.models import Organization, Person, Team, Role, Zone, Risk, RiskLevel, RelationType

# ============================================================================
# DONNÉES CNESST - SECTEURS SCIAN 56 (SERVICES DE SOUTIEN)
# ============================================================================

SECTEURS_SCIAN_56 = {
    "561720": {
        "nom": "Services de conciergerie",
        "description": "Nettoyage commercial, entretien ménager",
        "risques": [
            {"desc": "Chute de même niveau (plancher mouillé)", "cat": "chute", "prob": 5, "grav": 3},
            {"desc": "Exposition produits chimiques nettoyage", "cat": "chimique", "prob": 4, "grav": 3},
            {"desc": "TMS - mouvements répétitifs", "cat": "ergonomique", "prob": 5, "grav": 3},
            {"desc": "Coupure/blessure manipulation déchets", "cat": "mecanique", "prob": 3, "grav": 3},
            {"desc": "Piqûre aiguille (déchets biomédicaux)", "cat": "biologique", "prob": 2, "grav": 4},
            {"desc": "Chute hauteur (échelle, escabeau)", "cat": "chute", "prob": 3, "grav": 4},
            {"desc": "Travail isolé/de nuit", "cat": "psychosocial", "prob": 4, "grav": 3},
        ],
        "zones": [
            {"nom": "Bureaux/espaces commerciaux", "risk": "moyen", "dangers": ["Chute", "Chimique"], "epi": ["Gants", "Chaussures antidérapantes"]},
            {"nom": "Toilettes/salles de bain", "risk": "eleve", "dangers": ["Chimique", "Biologique", "Glissade"], "epi": ["Gants", "Lunettes", "Masque"]},
            {"nom": "Corridors/escaliers", "risk": "moyen", "dangers": ["Chute", "Équipement"], "epi": ["Chaussures antidérapantes"]},
            {"nom": "Local d'entretien", "risk": "eleve", "dangers": ["Chimique", "Stockage"], "epi": ["Gants", "Tablier", "Lunettes"]},
        ],
        "roles": ["Préposé à l'entretien", "Concierge", "Chef d'équipe nettoyage", "Superviseur entretien", "Directeur services"],
        "certs": ["SIMDUT", "Produits chimiques", "Travail hauteur", "Premiers soins"],
    },
    
    "561612": {
        "nom": "Services de sécurité et patrouille",
        "description": "Gardiens de sécurité, agents de surveillance",
        "risques": [
            {"desc": "Agression/violence lors intervention", "cat": "violence", "prob": 4, "grav": 4},
            {"desc": "Stress post-traumatique (incident)", "cat": "psychosocial", "prob": 3, "grav": 4},
            {"desc": "TMS - station debout prolongée", "cat": "ergonomique", "prob": 4, "grav": 3},
            {"desc": "Accident véhicule patrouille", "cat": "routier", "prob": 3, "grav": 4},
            {"desc": "Morsure chien (patrouille)", "cat": "biologique", "prob": 2, "grav": 3},
            {"desc": "Travail isolé/de nuit", "cat": "psychosocial", "prob": 4, "grav": 3},
            {"desc": "Exposition intempéries (extérieur)", "cat": "thermique", "prob": 4, "grav": 3},
        ],
        "zones": [
            {"nom": "Poste de garde", "risk": "moyen", "dangers": ["Violence", "Ergonomie"], "epi": ["Radio", "Gilet pare-balles optionnel"]},
            {"nom": "Ronde extérieure", "risk": "eleve", "dangers": ["Agression", "Intempéries", "Chien"], "epi": ["Lampe", "Radio", "Vêtements chauds"]},
            {"nom": "Stationnement", "risk": "eleve", "dangers": ["Violence", "Véhicule"], "epi": ["Dossard", "Radio", "Lampe"]},
            {"nom": "Véhicule patrouille", "risk": "moyen", "dangers": ["Accident routier"], "epi": ["Ceinture", "Radio"]},
        ],
        "roles": ["Agent de sécurité", "Gardien", "Patrouilleur", "Superviseur sécurité", "Directeur sécurité"],
        "certs": ["BSP (Bureau sécurité privée)", "Premiers soins", "RCR", "Gestion de crise", "Autodéfense"],
    },
    
    "561621": {
        "nom": "Services de systèmes de sécurité",
        "description": "Installation systèmes d'alarme, surveillance électronique",
        "risques": [
            {"desc": "Électrocution installation", "cat": "electrique", "prob": 3, "grav": 5},
            {"desc": "Chute échelle/escabeau", "cat": "chute", "prob": 4, "grav": 4},
            {"desc": "Coupure câblage/outils", "cat": "mecanique", "prob": 3, "grav": 3},
            {"desc": "TMS - postures contraignantes", "cat": "ergonomique", "prob": 4, "grav": 3},
            {"desc": "Blessure outils électriques", "cat": "mecanique", "prob": 3, "grav": 3},
            {"desc": "Travail en hauteur (câblage plafond)", "cat": "chute", "prob": 3, "grav": 4},
        ],
        "zones": [
            {"nom": "Site client (installation)", "risk": "eleve", "dangers": ["Électricité", "Hauteur", "Outils"], "epi": ["Gants isolants", "Lunettes", "Casque"]},
            {"nom": "Atelier technique", "risk": "moyen", "dangers": ["Outils", "Électricité"], "epi": ["Lunettes", "Gants"]},
            {"nom": "Véhicule service", "risk": "moyen", "dangers": ["Routier", "Outils"], "epi": ["Ceinture"]},
        ],
        "roles": ["Technicien alarme", "Installateur systèmes", "Électricien sécurité", "Superviseur technique", "Chef de projet"],
        "certs": ["Licence électricité", "Travail hauteur", "SIMDUT", "Premiers soins"],
    },
    
    "561730": {
        "nom": "Services d'aménagement paysager",
        "description": "Entretien pelouses, jardins, déneigement",
        "risques": [
            {"desc": "Coupure/amputation (tondeuse, taille-haie)", "cat": "mecanique", "prob": 3, "grav": 5},
            {"desc": "Projection débris (souffleuse, débroussailleuse)", "cat": "mecanique", "prob": 4, "grav": 4},
            {"desc": "TMS - travail physique répétitif", "cat": "ergonomique", "prob": 5, "grav": 3},
            {"desc": "Coup de chaleur été", "cat": "thermique", "prob": 4, "grav": 4},
            {"desc": "Engelures/hypothermie déneigement", "cat": "thermique", "prob": 3, "grav": 4},
            {"desc": "Piqûre insectes (guêpes, abeilles)", "cat": "biologique", "prob": 4, "grav": 3},
            {"desc": "Exposition pesticides/herbicides", "cat": "chimique", "prob": 3, "grav": 4},
            {"desc": "Bruit équipements >85dB", "cat": "bruit", "prob": 5, "grav": 3},
            {"desc": "Vibrations mains-bras (outils)", "cat": "ergonomique", "prob": 4, "grav": 3},
        ],
        "zones": [
            {"nom": "Terrain client", "risk": "eleve", "dangers": ["Équipements", "Chaleur", "Insectes"], "epi": ["Lunettes", "Bouchons", "Gants", "Chapeau"]},
            {"nom": "Stationnement (déneigement)", "risk": "eleve", "dangers": ["Froid", "Véhicules", "Glace"], "epi": ["Vêtements chauds", "Dossard", "Crampons"]},
            {"nom": "Camion/remorque équipement", "risk": "moyen", "dangers": ["Chute", "Équipement"], "epi": ["Chaussures sécurité"]},
        ],
        "roles": ["Jardinier paysagiste", "Opérateur tondeuse", "Déneigeur", "Chef d'équipe terrain", "Superviseur paysagement"],
        "certs": ["Pesticides", "SIMDUT", "Équipements motorisés", "Premiers soins", "Travail chaleur"],
    },
    
    "562111": {
        "nom": "Collecte de déchets non dangereux",
        "description": "Camions à ordures, collecte résidentielle et commerciale",
        "risques": [
            {"desc": "Écrasement par camion (recul)", "cat": "mecanique", "prob": 3, "grav": 5},
            {"desc": "Coincement mécanisme compacteur", "cat": "mecanique", "prob": 2, "grav": 5},
            {"desc": "TMS - levage conteneurs lourds", "cat": "ergonomique", "prob": 5, "grav": 4},
            {"desc": "Piqûre/coupure objets dans déchets", "cat": "biologique", "prob": 4, "grav": 4},
            {"desc": "Exposition agents biologiques (déchets)", "cat": "biologique", "prob": 4, "grav": 3},
            {"desc": "Chute montée/descente camion", "cat": "chute", "prob": 4, "grav": 3},
            {"desc": "Accident routier (circulation urbaine)", "cat": "routier", "prob": 3, "grav": 5},
            {"desc": "Bruit camion compacteur >85dB", "cat": "bruit", "prob": 5, "grav": 3},
        ],
        "zones": [
            {"nom": "Arrière camion collecte", "risk": "critique", "dangers": ["Compacteur", "TMS", "Piqûre"], "epi": ["Gants épais", "Bottes sécurité", "Dossard"]},
            {"nom": "Rue/stationnement collecte", "risk": "eleve", "dangers": ["Circulation", "Recul camion"], "epi": ["Dossard classe 3", "Casque optionnel"]},
            {"nom": "Cabine camion", "risk": "moyen", "dangers": ["Routier", "Bruit"], "epi": ["Ceinture", "Bouchons"]},
        ],
        "roles": ["Éboueur/Collecteur", "Chauffeur camion ordures", "Chef d'équipe collecte", "Répartiteur", "Superviseur collecte"],
        "certs": ["Permis classe 3", "SIMDUT", "Travail routier", "Premiers soins"],
    },
    
    "562112": {
        "nom": "Collecte de déchets dangereux",
        "description": "Transport et collecte matières dangereuses, biomédicales",
        "risques": [
            {"desc": "Exposition produits chimiques dangereux", "cat": "chimique", "prob": 3, "grav": 5},
            {"desc": "Piqûre aiguille/déchets biomédicaux", "cat": "biologique", "prob": 3, "grav": 5},
            {"desc": "Déversement matières dangereuses", "cat": "chimique", "prob": 2, "grav": 5},
            {"desc": "Inhalation vapeurs toxiques", "cat": "chimique", "prob": 3, "grav": 5},
            {"desc": "Brûlure chimique", "cat": "chimique", "prob": 2, "grav": 4},
            {"desc": "Explosion/incendie (réactifs)", "cat": "explosion", "prob": 2, "grav": 5},
        ],
        "zones": [
            {"nom": "Zone chargement déchets dangereux", "risk": "critique", "dangers": ["Chimique", "Biologique", "Déversement"], "epi": ["Combinaison Tyvek", "Masque vapeurs", "Gants nitrile", "Lunettes"]},
            {"nom": "Véhicule transport TMD", "risk": "critique", "dangers": ["Déversement", "Accident"], "epi": ["Kit déversement", "SCBA", "Détecteur gaz"]},
            {"nom": "Entrepôt stockage temporaire", "risk": "eleve", "dangers": ["Chimique", "Réaction"], "epi": ["EPI complet", "Ventilation"]},
        ],
        "roles": ["Technicien déchets dangereux", "Chauffeur TMD", "Manutentionnaire spécialisé", "Coordonnateur TMD", "Directeur environnement"],
        "certs": ["TMD Transport Canada", "SIMDUT", "Intervention urgence", "Biorisques", "Premiers soins avancés"],
    },
    
    "562211": {
        "nom": "Sites d'enfouissement",
        "description": "Sites d'enfouissement technique, dépotoirs",
        "risques": [
            {"desc": "Collision véhicule lourd (bulldozer)", "cat": "mecanique", "prob": 3, "grav": 5},
            {"desc": "Renversement équipement terrain instable", "cat": "mecanique", "prob": 3, "grav": 5},
            {"desc": "Inhalation biogaz (méthane, H2S)", "cat": "chimique", "prob": 3, "grav": 5},
            {"desc": "Exposition agents pathogènes", "cat": "biologique", "prob": 3, "grav": 4},
            {"desc": "Incendie déchets", "cat": "thermique", "prob": 3, "grav": 4},
            {"desc": "Chute terrain irrégulier", "cat": "chute", "prob": 4, "grav": 3},
            {"desc": "Bruit équipements lourds", "cat": "bruit", "prob": 5, "grav": 3},
        ],
        "zones": [
            {"nom": "Front d'enfouissement actif", "risk": "critique", "dangers": ["Véhicules", "Biogaz", "Terrain"], "epi": ["Casque", "Dossard", "Détecteur gaz", "Bottes"]},
            {"nom": "Zone compactage", "risk": "critique", "dangers": ["Bulldozer", "Renversement"], "epi": ["Dossard classe 3", "Radio"]},
            {"nom": "Station pompage lixiviat", "risk": "eleve", "dangers": ["Chimique", "Biologique"], "epi": ["Gants", "Masque", "Combinaison"]},
            {"nom": "Guérite/pesée", "risk": "moyen", "dangers": ["Circulation"], "epi": ["Dossard"]},
        ],
        "roles": ["Opérateur bulldozer", "Opérateur compacteur", "Préposé pesée", "Technicien environnement", "Directeur site"],
        "certs": ["Équipement lourd", "SIMDUT", "Espace clos", "Détection gaz", "Premiers soins"],
    },
    
    "562910": {
        "nom": "Services d'assainissement",
        "description": "Nettoyage fosses septiques, égouts, décontamination",
        "risques": [
            {"desc": "Asphyxie espace clos (fosse, égout)", "cat": "chimique", "prob": 2, "grav": 5},
            {"desc": "Intoxication gaz (H2S, CH4, CO)", "cat": "chimique", "prob": 3, "grav": 5},
            {"desc": "Noyade fosse septique", "cat": "noyade", "prob": 2, "grav": 5},
            {"desc": "Exposition agents pathogènes (eaux usées)", "cat": "biologique", "prob": 4, "grav": 4},
            {"desc": "Chute dans ouverture", "cat": "chute", "prob": 3, "grav": 5},
            {"desc": "Écrasement équipement pompage", "cat": "mecanique", "prob": 2, "grav": 4},
        ],
        "zones": [
            {"nom": "Fosse septique", "risk": "critique", "dangers": ["Gaz", "Noyade", "Asphyxie"], "epi": ["Détecteur 4 gaz", "Harnais", "Trépied", "SCBA"]},
            {"nom": "Égout/canalisation", "risk": "critique", "dangers": ["Gaz", "Noyade", "Espace clos"], "epi": ["EPI espace clos complet", "Ventilation forcée"]},
            {"nom": "Camion pompage", "risk": "eleve", "dangers": ["Pression", "Biologique"], "epi": ["Gants", "Lunettes", "Combinaison"]},
        ],
        "roles": ["Technicien assainissement", "Opérateur pompage", "Préposé vidange", "Superviseur terrain", "Directeur opérations"],
        "certs": ["Espace clos", "Détection gaz", "SIMDUT", "Biorisques", "Sauvetage espace clos", "Premiers soins"],
    },
    
    "561320": {
        "nom": "Services de placement temporaire",
        "description": "Agences de placement, travail temporaire",
        "risques": [
            {"desc": "TMS - postes variés non adaptés", "cat": "ergonomique", "prob": 4, "grav": 3},
            {"desc": "Formation insuffisante poste temporaire", "cat": "psychosocial", "prob": 4, "grav": 4},
            {"desc": "Stress adaptation constante", "cat": "psychosocial", "prob": 4, "grav": 3},
            {"desc": "Équipement inconnu (risque machine)", "cat": "mecanique", "prob": 3, "grav": 4},
            {"desc": "Harcèlement/violence milieu inconnu", "cat": "violence", "prob": 3, "grav": 3},
        ],
        "zones": [
            {"nom": "Site client assigné", "risk": "eleve", "dangers": ["Variable selon poste", "Formation"], "epi": ["Selon poste assigné"]},
            {"nom": "Bureau agence", "risk": "moyen", "dangers": ["Ergonomie bureau"], "epi": ["Standard bureau"]},
        ],
        "roles": ["Travailleur temporaire", "Manoeuvre assigné", "Conseiller placement", "Recruteur", "Directeur agence"],
        "certs": ["Formation poste", "SIMDUT", "Orientation SST", "Premiers soins"],
    },
}

# ORGANISATIONS DE SERVICES DE SOUTIEN QUÉBÉCOISES À CRÉER
ORGANISATIONS_SCIAN_56 = [
    # Conciergerie (561720)
    {"name": "GDI Services aux immeubles", "sector": "561720", "nb": 8500, "region": "Montréal"},
    {"name": "Roy Entretien ménager", "sector": "561720", "nb": 1200, "region": "Québec"},
    {"name": "ServiceMaster Québec", "sector": "561720", "nb": 650, "region": "Montréal"},
    {"name": "Entretien Distinction", "sector": "561720", "nb": 480, "region": "Montréal"},
    
    # Sécurité (561612)
    {"name": "Garda World", "sector": "561612", "nb": 12000, "region": "Montréal"},
    {"name": "Securitas Canada - Québec", "sector": "561612", "nb": 3500, "region": "Montréal"},
    {"name": "Corps canadien des commissionnaires", "sector": "561612", "nb": 2800, "region": "Québec"},
    {"name": "G4S Sécurité", "sector": "561612", "nb": 1500, "region": "Montréal"},
    
    # Systèmes sécurité (561621)
    {"name": "ADT Québec", "sector": "561621", "nb": 450, "region": "Montréal"},
    {"name": "Alarme Provinciale", "sector": "561621", "nb": 280, "region": "Montréal"},
    {"name": "Protection Incendie Idéal", "sector": "561621", "nb": 180, "region": "Québec"},
    
    # Aménagement paysager (561730)
    {"name": "Groupe Vertdure", "sector": "561730", "nb": 850, "region": "Montréal"},
    {"name": "Entreprises Martel (paysagement)", "sector": "561730", "nb": 380, "region": "Québec"},
    {"name": "Les Entreprises Métivier", "sector": "561730", "nb": 280, "region": "Montréal"},
    {"name": "Déneigement Nordique", "sector": "561730", "nb": 450, "region": "Québec"},
    
    # Collecte déchets (562111)
    {"name": "Waste Management Québec", "sector": "562111", "nb": 2200, "region": "Montréal"},
    {"name": "GFL Environmental - Québec", "sector": "562111", "nb": 1800, "region": "Montréal"},
    {"name": "EBI Environnement", "sector": "562111", "nb": 650, "region": "Montréal"},
    {"name": "Services Matrec", "sector": "562111", "nb": 850, "region": "Montréal"},
    
    # Déchets dangereux (562112)
    {"name": "Stericycle Québec", "sector": "562112", "nb": 280, "region": "Montréal"},
    {"name": "Clean Harbors Québec", "sector": "562112", "nb": 350, "region": "Montréal"},
    {"name": "Sanexen Services environnementaux", "sector": "562112", "nb": 420, "region": "Montréal"},
    
    # Sites enfouissement (562211)
    {"name": "BFI Canada - Lachenaie", "sector": "562211", "nb": 180, "region": "Lanaudière"},
    {"name": "Régie intermunicipale Argenteuil", "sector": "562211", "nb": 85, "region": "Laurentides"},
    
    # Assainissement (562910)
    {"name": "Sani-Sable", "sector": "562910", "nb": 120, "region": "Montréal"},
    {"name": "Pompage Express Québec", "sector": "562910", "nb": 85, "region": "Québec"},
    {"name": "Enviro-Option", "sector": "562910", "nb": 95, "region": "Montréal"},
    
    # Placement temporaire (561320)
    {"name": "Randstad Québec", "sector": "561320", "nb": 850, "region": "Montréal"},
    {"name": "Adecco Québec", "sector": "561320", "nb": 650, "region": "Montréal"},
    {"name": "Manpower Québec", "sector": "561320", "nb": 480, "region": "Montréal"},
]

AGES = ["18-24", "25-34", "35-44", "45-54", "55-64"]


def populate_scian56():
    """Peuple SafetyGraph avec les secteurs SCIAN 56 (Services de soutien)"""
    
    print("=" * 70)
    print("🧹🔒 POPULATION SAFETYGRAPH - SCIAN 56")
    print("    Services administratifs, soutien, gestion des déchets")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Secteurs: {len(SECTEURS_SCIAN_56)}")
    print(f"Organisations: {len(ORGANISATIONS_SCIAN_56)}")
    print("=" * 70)
    
    conn = SafetyGraphCartographyConnector()
    conn.connect()
    print("\n✅ Neo4j connecté")
    print(f"📊 Stats initiales: {conn.get_graph_stats()}\n")
    
    stats = {"orgs": 0, "zones": 0, "risks": 0, "persons": 0, "teams": 0, "roles": 0}
    
    # Créer organisations
    print("📦 Création des organisations SCIAN 56 (SERVICES)...")
    org_map = {}
    for o in ORGANISATIONS_SCIAN_56:
        org = Organization(
            name=o["name"],
            sector_scian=o["sector"],
            nb_employes=o["nb"],
            region_ssq=o["region"]
        )
        oid = conn.inject_organization(org)
        org_map[o["name"]] = {"id": oid, "sector": o["sector"], "nb": o["nb"]}
        stats["orgs"] += 1
        sector_nom = SECTEURS_SCIAN_56[o["sector"]]["nom"]
        print(f"   ✅ {o['name'][:40]} ({o['sector']})")
    
    # Créer entités par organisation
    print("\n🏗️ Création des entités par organisation...")
    
    for name, info in org_map.items():
        oid, sector = info["id"], info["sector"]
        data = SECTEURS_SCIAN_56[sector]
        print(f"\n   🧹 {name[:45]}")
        print(f"      Secteur: {data['nom']}")
        
        # Rôles
        rids = []
        for r in data["roles"]:
            is_sup = any(x in r for x in ["Chef", "Superviseur", "Directeur", "Coordonnateur"])
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
        if "562" in sector:  # Déchets - quarts
            equipes = ["Équipe Jour", "Équipe Collecte", "Équipe Entretien"]
        elif "561612" in sector:  # Sécurité - 24/7
            equipes = ["Équipe Jour", "Équipe Soir", "Équipe Nuit"]
        else:
            equipes = ["Équipe Principale", "Équipe Terrain"]
            
        for t in equipes:
            team = Team(name=t, department=data["nom"][:25])
            tid = conn.inject_team(team)
            tids.append(tid)
            conn.create_relation(tid, oid, RelationType.APPARTIENT_A)
            stats["teams"] += 1
        print(f"      • {len(tids)} équipes")
        
        # Personnes
        nb_persons = max(5, min(info["nb"] // 150, 30))
        for i in range(nb_persons):
            p = Person(
                matricule=f"SERV56-{sector[-3:]}-{stats['persons']+1:04d}",
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
            # Exposition aux risques
            if rkids and i % 10 < 7:
                conn.create_relation(pid, rkids[i % len(rkids)], RelationType.EXPOSE_A)
        
        print(f"      • {nb_persons} personnes (anonymisées Loi 25)")
    
    # Résumé
    print("\n" + "=" * 70)
    print("📊 RÉSUMÉ POPULATION SCIAN 56 - SERVICES DE SOUTIEN")
    print("=" * 70)
    print(f"   Organisations: {stats['orgs']}")
    print(f"   Zones de travail: {stats['zones']}")
    print(f"   Risques identifiés: {stats['risks']}")
    print(f"   Équipes: {stats['teams']}")
    print(f"   Rôles/Professions: {stats['roles']}")
    print(f"   Personnes: {stats['persons']}")
    print(f"\n   Neo4j final: {conn.get_graph_stats()}")
    print("=" * 70)
    print("✅ POPULATION SCIAN 56 (SERVICES) TERMINÉE!")
    print("=" * 70)
    
    conn.close()
    return stats


if __name__ == "__main__":
    populate_scian56()
