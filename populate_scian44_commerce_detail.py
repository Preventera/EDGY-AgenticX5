#!/usr/bin/env python3
"""
🛡️ Script de Population Neo4j - Secteurs SCIAN 44-45
Commerce de détail
EDGY-AgenticX5 | SafetyGraph | Preventera

🛒 3e SECTEUR EN LÉSIONS QUÉBEC - ~25,000/an
   Supermarchés, quincailleries, grands magasins
   TMS, chutes, écrasement, violence/vol

Secteurs inclus:
- 445110: Supermarchés et autres épiceries
- 445120: Dépanneurs
- 444110: Centres de rénovation (quincailleries)
- 444120: Magasins de peinture et papier peint
- 452110: Grands magasins
- 452910: Clubs-entrepôts
- 441110: Concessionnaires automobiles
- 447110: Stations-service avec dépanneur
- 453110: Fleuristes
- 448110: Magasins de vêtements

Risques principaux CNESST:
- TMS (manutention, caisse)
- Chutes même niveau
- Frappé/coincé par objets
- Violence/vol à main armée
"""

import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

from src.cartography.connector import SafetyGraphCartographyConnector
from src.cartography.models import Organization, Person, Team, Role, Zone, Risk, RiskLevel, RelationType

# ============================================================================
# DONNÉES CNESST - SECTEURS SCIAN 44-45 (COMMERCE DE DÉTAIL)
# 3e SECTEUR EN LÉSIONS - ~25,000/AN
# ============================================================================

SECTEURS_SCIAN_44 = {
    "445110": {
        "nom": "Supermarchés et autres épiceries",
        "description": "Épiceries, supermarchés, marchés alimentaires",
        "risques": [
            {"desc": "TMS - caisse répétitif", "cat": "ergonomique", "prob": 5, "grav": 3},
            {"desc": "TMS - manutention marchandises", "cat": "ergonomique", "prob": 5, "grav": 3},
            {"desc": "Glissade plancher mouillé/gras", "cat": "chute", "prob": 5, "grav": 3},
            {"desc": "Chute même niveau (encombrements)", "cat": "chute", "prob": 4, "grav": 3},
            {"desc": "Frappé par chariot/transpalette", "cat": "mecanique", "prob": 4, "grav": 3},
            {"desc": "Coupure couteau (boucherie)", "cat": "mecanique", "prob": 4, "grav": 4},
            {"desc": "Exposition froid (chambre froide)", "cat": "thermique", "prob": 4, "grav": 2},
            {"desc": "Vol à main armée", "cat": "violence", "prob": 2, "grav": 5},
            {"desc": "Agression client", "cat": "violence", "prob": 3, "grav": 3},
            {"desc": "Chute objets rayonnages", "cat": "mecanique", "prob": 3, "grav": 4},
        ],
        "zones": [
            {"nom": "Caisses/Service client", "risk": "moyen", "dangers": ["TMS", "Violence", "Station debout"], "epi": ["Tapis anti-fatigue"]},
            {"nom": "Entrepôt arrière-boutique", "risk": "eleve", "dangers": ["Chute objets", "TMS", "Chariot"], "epi": ["Chaussures sécurité", "Gants"]},
            {"nom": "Boucherie/Charcuterie", "risk": "eleve", "dangers": ["Coupure", "Froid", "TMS"], "epi": ["Gants maille", "Tablier", "Bottes"]},
            {"nom": "Chambre froide/Congélateur", "risk": "eleve", "dangers": ["Froid extrême", "Glissade"], "epi": ["Vêtements isolants", "Gants"]},
            {"nom": "Aire de vente", "risk": "moyen", "dangers": ["Glissade", "Collision chariot"], "epi": ["Chaussures fermées"]},
        ],
        "roles": ["Caissier/Caissière", "Commis épicerie", "Boucher", "Commis fruits/légumes", "Manutentionnaire", "Gérant rayon", "Directeur magasin"],
        "certs": ["SIMDUT", "Manutention sécuritaire", "Hygiène alimentaire", "Premiers soins"],
    },
    
    "445120": {
        "nom": "Dépanneurs",
        "description": "Dépanneurs, convenience stores",
        "risques": [
            {"desc": "Vol à main armée", "cat": "violence", "prob": 3, "grav": 5},
            {"desc": "Agression client intoxiqué", "cat": "violence", "prob": 4, "grav": 4},
            {"desc": "TMS - station debout prolongée", "cat": "ergonomique", "prob": 5, "grav": 3},
            {"desc": "TMS - manutention marchandises", "cat": "ergonomique", "prob": 4, "grav": 3},
            {"desc": "Travail isolé (nuit)", "cat": "psychosocial", "prob": 4, "grav": 4},
            {"desc": "Glissade plancher", "cat": "chute", "prob": 3, "grav": 3},
            {"desc": "Fatigue quarts de nuit", "cat": "psychosocial", "prob": 5, "grav": 3},
        ],
        "zones": [
            {"nom": "Caisse/Comptoir", "risk": "eleve", "dangers": ["Vol armé", "Violence", "TMS"], "epi": []},
            {"nom": "Réserve arrière", "risk": "moyen", "dangers": ["TMS", "Chute objets"], "epi": ["Chaussures fermées"]},
            {"nom": "Extérieur/Stationnement", "risk": "eleve", "dangers": ["Violence", "Accident"], "epi": []},
        ],
        "roles": ["Commis dépanneur", "Caissier nuit", "Gérant dépanneur"],
        "certs": ["Vente tabac/loterie", "Premiers soins", "Intervention crise"],
    },
    
    "444110": {
        "nom": "Centres de rénovation (quincailleries)",
        "description": "Quincailleries, centres rénovation, matériaux",
        "risques": [
            {"desc": "Chute objets lourds (bois, ciment)", "cat": "mecanique", "prob": 4, "grav": 5},
            {"desc": "Écrasement chariot élévateur", "cat": "mecanique", "prob": 2, "grav": 5},
            {"desc": "TMS - manutention matériaux lourds", "cat": "ergonomique", "prob": 5, "grav": 4},
            {"desc": "Chute hauteur (rayonnages)", "cat": "chute", "prob": 3, "grav": 5},
            {"desc": "Coupure métal/verre", "cat": "mecanique", "prob": 4, "grav": 3},
            {"desc": "Exposition poussière/silice (coupe)", "cat": "chimique", "prob": 3, "grav": 3},
            {"desc": "Collision chariot élévateur", "cat": "mecanique", "prob": 3, "grav": 4},
            {"desc": "Renversement palette", "cat": "mecanique", "prob": 3, "grav": 4},
            {"desc": "Bruit zone coupe >85dB", "cat": "bruit", "prob": 4, "grav": 3},
        ],
        "zones": [
            {"nom": "Cour à bois extérieure", "risk": "critique", "dangers": ["Écrasement", "Chariot élévateur", "TMS"], "epi": ["Casque", "Dossard", "Bottes sécurité"]},
            {"nom": "Rayonnage hauteur (entrepôt)", "risk": "critique", "dangers": ["Chute objets", "Chariot"], "epi": ["Casque", "Dossard"]},
            {"nom": "Zone coupe bois/métal", "risk": "eleve", "dangers": ["Coupure", "Bruit", "Poussière"], "epi": ["Lunettes", "Protection auditive", "Gants"]},
            {"nom": "Aire de vente", "risk": "moyen", "dangers": ["TMS", "Chute objets"], "epi": ["Chaussures sécurité"]},
        ],
        "roles": ["Commis quincaillerie", "Cariste", "Commis cour à bois", "Opérateur coupe", "Conseiller ventes", "Gérant rayon", "Directeur magasin"],
        "certs": ["Cariste/Chariot élévateur", "SIMDUT", "Manutention", "Travail hauteur", "Premiers soins"],
    },
    
    "452110": {
        "nom": "Grands magasins",
        "description": "Magasins à rayons, department stores",
        "risques": [
            {"desc": "TMS - manutention/réapprovisionnement", "cat": "ergonomique", "prob": 5, "grav": 3},
            {"desc": "TMS - caisse répétitif", "cat": "ergonomique", "prob": 5, "grav": 3},
            {"desc": "Chute même niveau (encombrements)", "cat": "chute", "prob": 4, "grav": 3},
            {"desc": "Chute escabeau/échelle", "cat": "chute", "prob": 3, "grav": 4},
            {"desc": "Vol à l'étalage/agression", "cat": "violence", "prob": 3, "grav": 3},
            {"desc": "Frappé par chariot", "cat": "mecanique", "prob": 3, "grav": 3},
            {"desc": "Stress période achalandée", "cat": "psychosocial", "prob": 5, "grav": 2},
        ],
        "zones": [
            {"nom": "Aire de vente", "risk": "moyen", "dangers": ["TMS", "Chute", "Violence"], "epi": []},
            {"nom": "Entrepôt/Réserve", "risk": "eleve", "dangers": ["Chute objets", "TMS", "Chariot"], "epi": ["Chaussures sécurité"]},
            {"nom": "Quai réception", "risk": "eleve", "dangers": ["Écrasement", "TMS", "Camion"], "epi": ["Dossard", "Bottes"]},
            {"nom": "Caisses", "risk": "moyen", "dangers": ["TMS", "Violence"], "epi": []},
        ],
        "roles": ["Commis ventes", "Caissier", "Manutentionnaire", "Étalagiste", "Chef caisse", "Gérant département", "Directeur magasin"],
        "certs": ["Manutention", "SIMDUT", "Premiers soins"],
    },
    
    "452910": {
        "nom": "Clubs-entrepôts",
        "description": "Costco, clubs de gros, entrepôts membres",
        "risques": [
            {"desc": "Collision chariot élévateur", "cat": "mecanique", "prob": 3, "grav": 5},
            {"desc": "Chute palettes/marchandises", "cat": "mecanique", "prob": 4, "grav": 5},
            {"desc": "TMS - manutention gros formats", "cat": "ergonomique", "prob": 5, "grav": 4},
            {"desc": "Écrasement entre palettes", "cat": "mecanique", "prob": 2, "grav": 5},
            {"desc": "Chute hauteur (rayonnages géants)", "cat": "chute", "prob": 2, "grav": 5},
            {"desc": "Frappé par chariot client", "cat": "mecanique", "prob": 4, "grav": 3},
            {"desc": "Exposition froid (chambres froides)", "cat": "thermique", "prob": 4, "grav": 2},
            {"desc": "Bruit ambiant entrepôt", "cat": "bruit", "prob": 4, "grav": 2},
        ],
        "zones": [
            {"nom": "Allées entrepôt (chariot élévateur)", "risk": "critique", "dangers": ["Collision", "Chute palettes"], "epi": ["Dossard", "Casque zones désignées"]},
            {"nom": "Rayonnages géants", "risk": "critique", "dangers": ["Chute objets", "Écrasement"], "epi": ["Casque", "Dossard"]},
            {"nom": "Chambre froide géante", "risk": "eleve", "dangers": ["Froid", "Glissade", "TMS"], "epi": ["Vêtements isolants"]},
            {"nom": "Zone réception marchandises", "risk": "critique", "dangers": ["Chariot", "Camion", "TMS"], "epi": ["Dossard", "Bottes", "Casque"]},
        ],
        "roles": ["Commis entrepôt", "Cariste Costco", "Caissier", "Démonstrateur", "Préposé viandes", "Superviseur", "Gérant magasin"],
        "certs": ["Cariste/Chariot élévateur", "Manutention", "SIMDUT", "Premiers soins"],
    },
    
    "441110": {
        "nom": "Concessionnaires automobiles",
        "description": "Vente automobiles neuves, service",
        "risques": [
            {"desc": "Écrasement véhicule (pont élévateur)", "cat": "mecanique", "prob": 2, "grav": 5},
            {"desc": "Brûlure échappement/moteur", "cat": "thermique", "prob": 3, "grav": 3},
            {"desc": "Intoxication monoxyde carbone", "cat": "chimique", "prob": 2, "grav": 5},
            {"desc": "Chute sous véhicule (fosse)", "cat": "chute", "prob": 2, "grav": 4},
            {"desc": "Coupure/écrasement pièces", "cat": "mecanique", "prob": 4, "grav": 3},
            {"desc": "TMS - postures mécanicien", "cat": "ergonomique", "prob": 5, "grav": 3},
            {"desc": "Exposition huiles/solvants", "cat": "chimique", "prob": 4, "grav": 2},
            {"desc": "Bruit atelier >85dB", "cat": "bruit", "prob": 4, "grav": 3},
        ],
        "zones": [
            {"nom": "Atelier mécanique", "risk": "critique", "dangers": ["Écrasement", "Brûlure", "Chimique"], "epi": ["Bottes sécurité", "Lunettes", "Gants"]},
            {"nom": "Zone ponts élévateurs", "risk": "critique", "dangers": ["Écrasement", "Chute"], "epi": ["Casque", "Bottes"]},
            {"nom": "Showroom ventes", "risk": "moyen", "dangers": ["Glissade", "Collision véhicule"], "epi": []},
            {"nom": "Entrepôt pièces", "risk": "eleve", "dangers": ["Chute objets", "TMS"], "epi": ["Chaussures sécurité"]},
        ],
        "roles": ["Mécanicien automobile", "Technicien service", "Conseiller ventes", "Préposé pièces", "Carrossier", "Directeur service", "Directeur ventes"],
        "certs": ["ASE/Mécanique", "Cadenassage", "SIMDUT", "Premiers soins", "Propane/AC"],
    },
    
    "447110": {
        "nom": "Stations-service avec dépanneur",
        "description": "Stations essence, service, dépanneur",
        "risques": [
            {"desc": "Incendie/explosion essence", "cat": "chimique", "prob": 1, "grav": 5},
            {"desc": "Vol à main armée", "cat": "violence", "prob": 3, "grav": 5},
            {"desc": "Agression client", "cat": "violence", "prob": 3, "grav": 4},
            {"desc": "Exposition vapeurs essence", "cat": "chimique", "prob": 4, "grav": 2},
            {"desc": "Frappé par véhicule", "cat": "routier", "prob": 2, "grav": 5},
            {"desc": "Glissade (huile, glace)", "cat": "chute", "prob": 4, "grav": 3},
            {"desc": "TMS - station debout", "cat": "ergonomique", "prob": 4, "grav": 3},
            {"desc": "Travail isolé nuit", "cat": "psychosocial", "prob": 4, "grav": 4},
        ],
        "zones": [
            {"nom": "Îlot de distribution essence", "risk": "critique", "dangers": ["Incendie", "Frappé véhicule", "Vapeurs"], "epi": ["Dossard", "Chaussures antistatiques"]},
            {"nom": "Caisse dépanneur", "risk": "eleve", "dangers": ["Vol armé", "Violence"], "epi": []},
            {"nom": "Zone lavage auto", "risk": "moyen", "dangers": ["Glissade", "Chimique"], "epi": ["Bottes imperméables"]},
        ],
        "roles": ["Préposé station", "Caissier", "Préposé lavage", "Gérant station"],
        "certs": ["Manutention carburant", "Intervention crise", "Premiers soins"],
    },
}

# ORGANISATIONS COMMERCE DÉTAIL QUÉBÉCOISES
ORGANISATIONS_SCIAN_44 = [
    # Supermarchés (445110)
    {"name": "Metro Inc.", "sector": "445110", "nb": 8500, "region": "Montréal"},
    {"name": "IGA (Sobeys)", "sector": "445110", "nb": 6500, "region": "Québec"},
    {"name": "Maxi (Loblaw)", "sector": "445110", "nb": 4500, "region": "Montréal"},
    {"name": "Provigo (Loblaw)", "sector": "445110", "nb": 3200, "region": "Montréal"},
    {"name": "Super C (Metro)", "sector": "445110", "nb": 2800, "region": "Montréal"},
    {"name": "Marché Adonis", "sector": "445110", "nb": 850, "region": "Montréal"},
    {"name": "Avril Supermarché Santé", "sector": "445110", "nb": 280, "region": "Granby"},
    
    # Dépanneurs (445120)
    {"name": "Couche-Tard (Alimentation)", "sector": "445120", "nb": 5500, "region": "Laval"},
    {"name": "Dépanneurs Beau-Soir", "sector": "445120", "nb": 280, "region": "Montréal"},
    
    # Quincailleries/Rénovation (444110)
    {"name": "RONA (Lowe's Canada)", "sector": "444110", "nb": 4500, "region": "Boucherville"},
    {"name": "Home Depot Québec", "sector": "444110", "nb": 3200, "region": "Montréal"},
    {"name": "BMR Groupe", "sector": "444110", "nb": 1800, "region": "Boucherville"},
    {"name": "Patrick Morin", "sector": "444110", "nb": 850, "region": "Saint-Hyacinthe"},
    {"name": "Canac", "sector": "444110", "nb": 1200, "region": "Québec"},
    
    # Grands magasins (452110)
    {"name": "Walmart Canada (Québec)", "sector": "452110", "nb": 8500, "region": "Montréal"},
    {"name": "Hudson's Bay (La Baie)", "sector": "452110", "nb": 1200, "region": "Montréal"},
    {"name": "Winners/HomeSense (TJX)", "sector": "452110", "nb": 2200, "region": "Montréal"},
    {"name": "Dollarama", "sector": "452110", "nb": 3500, "region": "Montréal"},
    
    # Clubs-entrepôts (452910)
    {"name": "Costco Québec", "sector": "452910", "nb": 4500, "region": "Montréal"},
    {"name": "Wholesale Club (Loblaw)", "sector": "452910", "nb": 850, "region": "Montréal"},
    
    # Concessionnaires auto (441110)
    {"name": "Groupe Park Avenue", "sector": "441110", "nb": 1200, "region": "Montréal"},
    {"name": "Groupe Beaucage", "sector": "441110", "nb": 850, "region": "Sherbrooke"},
    {"name": "HGrégoire", "sector": "441110", "nb": 650, "region": "Montréal"},
    {"name": "AutoPlanet Direct", "sector": "441110", "nb": 280, "region": "Montréal"},
    
    # Stations-service (447110)
    {"name": "Petro-Canada Québec", "sector": "447110", "nb": 1500, "region": "Montréal"},
    {"name": "Ultramar (Parkland)", "sector": "447110", "nb": 1200, "region": "Montréal"},
    {"name": "Shell Québec", "sector": "447110", "nb": 850, "region": "Montréal"},
    {"name": "Esso (Imperial)", "sector": "447110", "nb": 650, "region": "Montréal"},
]

AGES = ["18-24", "25-34", "35-44", "45-54", "55-64"]


def populate_scian44():
    """Peuple SafetyGraph avec les secteurs SCIAN 44-45 (Commerce de détail)"""
    
    print("=" * 70)
    print("🛒🏪 POPULATION SAFETYGRAPH - SCIAN 44-45")
    print("    Commerce de détail")
    print("    🛒 3e SECTEUR EN LÉSIONS QUÉBEC")
    print("    ~25,000 lésions/an (TMS, chutes, violence)")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Secteurs: {len(SECTEURS_SCIAN_44)}")
    print(f"Organisations: {len(ORGANISATIONS_SCIAN_44)}")
    print("=" * 70)
    
    conn = SafetyGraphCartographyConnector()
    conn.connect()
    print("\n✅ Neo4j connecté")
    print(f"📊 Stats initiales: {conn.get_graph_stats()}\n")
    
    stats = {"orgs": 0, "zones": 0, "risks": 0, "persons": 0, "teams": 0, "roles": 0}
    
    # Créer organisations
    print("📦 Création des organisations SCIAN 44-45 (COMMERCE DÉTAIL)...")
    org_map = {}
    for o in ORGANISATIONS_SCIAN_44:
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
        data = SECTEURS_SCIAN_44[sector]
        
        # Emoji selon secteur
        if sector == "445110":
            emoji = "🛒"
        elif sector == "445120":
            emoji = "🏪"
        elif sector == "444110":
            emoji = "🔨"
        elif sector in ["452110", "452910"]:
            emoji = "🏬"
        elif sector == "441110":
            emoji = "🚗"
        else:
            emoji = "⛽"
            
        print(f"\n   {emoji} {name[:40]}")
        print(f"      Secteur: {data['nom']}")
        
        # Rôles
        rids = []
        for r in data["roles"]:
            is_sup = any(x in r for x in ["Chef", "Gérant", "Directeur", "Superviseur"])
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
        if info["nb"] > 1000:
            equipes = ["Équipe Matin", "Équipe Jour", "Équipe Soir", "Équipe Nuit"]
        elif info["nb"] > 300:
            equipes = ["Équipe Jour", "Équipe Soir", "Équipe Fin semaine"]
        else:
            equipes = ["Équipe Principale"]
            
        for t in equipes:
            team = Team(name=t, department=data["nom"][:25])
            tid = conn.inject_team(team)
            tids.append(tid)
            conn.create_relation(tid, oid, RelationType.APPARTIENT_A)
            stats["teams"] += 1
        print(f"      • {len(tids)} équipes")
        
        # Personnes
        nb_persons = max(5, min(info["nb"] // 100, 40))
        for i in range(nb_persons):
            # Distribution âge typique commerce détail
            age_dist = ["18-24", "18-24", "25-34", "35-44", "45-54"]
            p = Person(
                matricule=f"COMM44-{sector[-3:]}-{stats['persons']+1:04d}",
                department=data["nom"][:25],
                age_groupe=age_dist[i % 5],
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
            if rkids and i % 10 < 7:
                conn.create_relation(pid, rkids[i % len(rkids)], RelationType.EXPOSE_A)
        
        print(f"      • {nb_persons} personnes (anonymisées Loi 25)")
    
    # Résumé
    print("\n" + "=" * 70)
    print("📊 RÉSUMÉ POPULATION SCIAN 44-45 - COMMERCE DE DÉTAIL")
    print("   🛒 3e SECTEUR EN LÉSIONS QUÉBEC")
    print("=" * 70)
    print(f"   Organisations commerce détail: {stats['orgs']}")
    print(f"   Zones de travail: {stats['zones']}")
    print(f"   Risques identifiés: {stats['risks']}")
    print(f"   Équipes: {stats['teams']}")
    print(f"   Rôles/Professions: {stats['roles']}")
    print(f"   Personnes: {stats['persons']}")
    print(f"\n   Neo4j final: {conn.get_graph_stats()}")
    print("=" * 70)
    print("✅ POPULATION SCIAN 44-45 (COMMERCE DE DÉTAIL) TERMINÉE!")
    print("=" * 70)
    
    conn.close()
    return stats


if __name__ == "__main__":
    populate_scian44()
