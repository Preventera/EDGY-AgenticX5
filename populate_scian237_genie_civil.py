#!/usr/bin/env python3
"""
🛡️ Script de Population Neo4j - Secteurs SCIAN 237
Travaux de génie civil
EDGY-AgenticX5 | SafetyGraph | Preventera

⚡ SECTEUR NÉVRALGIQUE QUÉBEC - 40,000+ travailleurs
   Hydro-Québec, barrages, lignes haute tension, pipelines
   ACRGTQ: Association représentant 2,500+ employeurs

Secteurs inclus:
- 237110: Construction d'oléoducs et gazoducs
- 237120: Construction de réseaux d'aqueduc et d'égout
- 237130: Construction de lignes électriques et télécommunications
- 237310: Construction de routes, rues et ponts (expansion)
- 237990: Autres travaux de génie civil (barrages, éoliennes)

Risques Tolérance Zéro spécifiques:
- Électrocution haute tension (lignes 735kV)
- Effondrement excavation/tranchée
- Espace clos (égouts, réservoirs)
- Chute de hauteur (pylônes, structures)
- Asphyxie (travaux souterrains)
"""

import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

from src.cartography.connector import SafetyGraphCartographyConnector
from src.cartography.models import Organization, Person, Team, Role, Zone, Risk, RiskLevel, RelationType

# ============================================================================
# DONNÉES CNESST - SECTEURS SCIAN 237 (GÉNIE CIVIL)
# SECTEUR NÉVRALGIQUE QUÉBEC - HYDRO-QUÉBEC, BARRAGES, PIPELINES
# ============================================================================

SECTEURS_SCIAN_237 = {
    "237110": {
        "nom": "Construction d'oléoducs et gazoducs",
        "description": "Pipelines pétrole, gaz naturel, structures connexes",
        "risques": [
            {"desc": "Explosion/incendie gaz naturel", "cat": "chimique", "prob": 2, "grav": 5, "tz": True},
            {"desc": "Asphyxie atmosphère explosive", "cat": "chimique", "prob": 2, "grav": 5, "tz": True},
            {"desc": "Effondrement tranchée pipeline", "cat": "mecanique", "prob": 3, "grav": 5, "tz": True},
            {"desc": "Écrasement équipement lourd", "cat": "mecanique", "prob": 3, "grav": 5},
            {"desc": "Brûlure soudure pipeline", "cat": "thermique", "prob": 4, "grav": 3},
            {"desc": "Intoxication H2S (gaz sulfureux)", "cat": "chimique", "prob": 2, "grav": 5, "tz": True},
            {"desc": "TMS - manutention tuyaux lourds", "cat": "ergonomique", "prob": 5, "grav": 3},
            {"desc": "Exposition froid extrême (Nord)", "cat": "thermique", "prob": 4, "grav": 4},
        ],
        "zones": [
            {"nom": "Tranchée pipeline active", "risk": "critique", "dangers": ["Effondrement", "Gaz", "Équipement"], "epi": ["Détecteur 4 gaz", "Casque", "Bottes"]},
            {"nom": "Zone soudure pipeline", "risk": "critique", "dangers": ["Explosion", "Brûlure", "Fumées"], "epi": ["Masque soudeur", "Gants", "Combinaison ignifuge"]},
            {"nom": "Station de compression", "risk": "critique", "dangers": ["Explosion", "Bruit", "Gaz"], "epi": ["Détecteur gaz", "Protection auditive"]},
            {"nom": "Emprise pipeline", "risk": "eleve", "dangers": ["Équipement lourd", "Circulation"], "epi": ["Dossard", "Casque", "Bottes"]},
        ],
        "roles": ["Soudeur pipeline", "Opérateur pelle pipeline", "Poseur tuyaux", "Inspecteur soudure", "Technicien cathodique", "Contremaître pipeline", "Surintendant"],
        "certs": ["ASP Construction", "Soudage CWB", "Espace clos", "H2S Alive", "SIMDUT", "Premiers soins"],
    },
    
    "237120": {
        "nom": "Construction de réseaux d'aqueduc et d'égout",
        "description": "Aqueducs, égouts, usines traitement eau",
        "risques": [
            {"desc": "Effondrement tranchée >1.2m", "cat": "mecanique", "prob": 4, "grav": 5, "tz": True},
            {"desc": "Asphyxie espace clos (égout)", "cat": "chimique", "prob": 3, "grav": 5, "tz": True},
            {"desc": "Intoxication H2S/méthane égout", "cat": "chimique", "prob": 3, "grav": 5, "tz": True},
            {"desc": "Noyade accumulation eau", "cat": "physique", "prob": 2, "grav": 5, "tz": True},
            {"desc": "Électrocution pompes/équipement", "cat": "electrique", "prob": 2, "grav": 5, "tz": True},
            {"desc": "Écrasement équipement excavation", "cat": "mecanique", "prob": 3, "grav": 5},
            {"desc": "Contact conduite gaz/électrique", "cat": "electrique", "prob": 2, "grav": 5, "tz": True},
            {"desc": "Pathogènes eaux usées", "cat": "biologique", "prob": 4, "grav": 3},
            {"desc": "TMS - manutention tuyaux béton", "cat": "ergonomique", "prob": 5, "grav": 3},
        ],
        "zones": [
            {"nom": "Tranchée excavation profonde", "risk": "critique", "dangers": ["Effondrement", "Gaz", "Eau"], "epi": ["Détecteur 4 gaz", "Harnais", "Échelle évasion"]},
            {"nom": "Égout existant (intervention)", "risk": "critique", "dangers": ["H2S", "Méthane", "Noyade"], "epi": ["APRIA", "Détecteur", "Tripode"]},
            {"nom": "Regard/chambre de vanne", "risk": "critique", "dangers": ["Espace clos", "Gaz"], "epi": ["Détecteur", "Ventilation", "Harnais"]},
            {"nom": "Zone pose conduites", "risk": "eleve", "dangers": ["Écrasement", "Équipement"], "epi": ["Casque", "Dossard", "Bottes"]},
        ],
        "roles": ["Poseur de conduites", "Opérateur excavatrice", "Jointeur tuyaux", "Soudeur PEHD", "Technicien essais", "Contremaître aqueduc", "Surintendant"],
        "certs": ["ASP Construction", "Espace clos", "SIMDUT", "Info-Excavation", "Soudage PEHD", "Premiers soins"],
    },
    
    "237130": {
        "nom": "Construction de lignes électriques et télécommunications",
        "description": "Lignes haute tension, distribution, télécoms, pylônes",
        "risques": [
            {"desc": "Électrocution haute tension (735kV)", "cat": "electrique", "prob": 2, "grav": 5, "tz": True},
            {"desc": "Arc électrique flash", "cat": "electrique", "prob": 2, "grav": 5, "tz": True},
            {"desc": "Chute de pylône/structure >3m", "cat": "chute", "prob": 3, "grav": 5, "tz": True},
            {"desc": "Chute lors montage pylône", "cat": "chute", "prob": 3, "grav": 5, "tz": True},
            {"desc": "Écrasement pylône/équipement", "cat": "mecanique", "prob": 2, "grav": 5},
            {"desc": "Électrisation induction magnétique", "cat": "electrique", "prob": 3, "grav": 4},
            {"desc": "Chute d'objets (outils, matériaux)", "cat": "mecanique", "prob": 4, "grav": 4},
            {"desc": "Exposition intempéries extrêmes", "cat": "thermique", "prob": 4, "grav": 3},
            {"desc": "TMS - travail en hauteur prolongé", "cat": "ergonomique", "prob": 4, "grav": 3},
        ],
        "zones": [
            {"nom": "Pylône haute tension sous tension", "risk": "critique", "dangers": ["Électrocution 735kV", "Arc flash", "Chute"], "epi": ["Combinaison conductrice", "Harnais", "Outils isolés"]},
            {"nom": "Pylône hors tension (construction)", "risk": "critique", "dangers": ["Chute >30m", "Écrasement"], "epi": ["Harnais 100%", "Casque", "Gants"]},
            {"nom": "Zone tirage câbles", "risk": "eleve", "dangers": ["Écrasement", "Fouet câble"], "epi": ["Casque", "Gants", "Dossard"]},
            {"nom": "Poste de transformation", "risk": "critique", "dangers": ["Électrocution", "Arc flash", "Huile PCB"], "epi": ["EPI arc flash", "Détecteur tension"]},
        ],
        "roles": ["Monteur de lignes", "Jointeur câbles HT", "Opérateur nacelle", "Électricien poste", "Arpenteur lignes", "Contremaître lignes", "Surintendant HQ"],
        "certs": ["ASP Construction", "Travail hauteur", "Ligne sous tension", "Arc flash", "Premiers soins", "Secourisme pylône"],
    },
    
    "237990": {
        "nom": "Autres travaux de génie civil",
        "description": "Barrages, centrales, éoliennes, ouvrages maritimes",
        "risques": [
            {"desc": "Noyade travaux maritimes/barrages", "cat": "physique", "prob": 2, "grav": 5, "tz": True},
            {"desc": "Chute de hauteur >3m (barrage, éolienne)", "cat": "chute", "prob": 3, "grav": 5, "tz": True},
            {"desc": "Écrasement équipement lourd", "cat": "mecanique", "prob": 3, "grav": 5},
            {"desc": "Effondrement batardeau/coffrage", "cat": "mecanique", "prob": 2, "grav": 5, "tz": True},
            {"desc": "Électrocution centrale", "cat": "electrique", "prob": 2, "grav": 5, "tz": True},
            {"desc": "Espace clos galeries/tunnels", "cat": "chimique", "prob": 2, "grav": 5, "tz": True},
            {"desc": "Chute nacelle éolienne (80-150m)", "cat": "chute", "prob": 2, "grav": 5, "tz": True},
            {"desc": "Hypothermie travaux nordiques", "cat": "thermique", "prob": 4, "grav": 4},
            {"desc": "Bruit dynamitage/équipement", "cat": "bruit", "prob": 5, "grav": 3},
        ],
        "zones": [
            {"nom": "Barrage en construction", "risk": "critique", "dangers": ["Noyade", "Chute", "Écrasement"], "epi": ["VFI", "Harnais", "Casque"]},
            {"nom": "Nacelle éolienne (80-150m)", "risk": "critique", "dangers": ["Chute extrême", "Électrocution"], "epi": ["Harnais 100%", "Évacuation urgence"]},
            {"nom": "Galerie souterraine centrale", "risk": "critique", "dangers": ["Espace clos", "Électricité", "Chute"], "epi": ["Détecteur gaz", "Harnais", "Lampe"]},
            {"nom": "Zone batardeau maritime", "risk": "critique", "dangers": ["Noyade", "Effondrement"], "epi": ["VFI", "Casque", "Radio"]},
        ],
        "roles": ["Monteur éolienne", "Opérateur barrage", "Plongeur industriel", "Dynamiteur", "Grutier lourd", "Contremaître génie civil", "Directeur projet"],
        "certs": ["ASP Construction", "Travail hauteur", "Plongée industrielle", "Espace clos", "Dynamitage", "Sauvetage aquatique"],
    },
}

# ORGANISATIONS DE GÉNIE CIVIL QUÉBÉCOISES
ORGANISATIONS_SCIAN_237 = [
    # Oléoducs/Gazoducs (237110)
    {"name": "Énergir (construction)", "sector": "237110", "nb": 450, "region": "Montréal"},
    {"name": "Trans-Northern Pipelines", "sector": "237110", "nb": 180, "region": "Montréal"},
    {"name": "Gazifère construction", "sector": "237110", "nb": 120, "region": "Outaouais"},
    
    # Aqueduc/Égout (237120)
    {"name": "Aqua-Pipe (Sanexen)", "sector": "237120", "nb": 280, "region": "Montréal"},
    {"name": "Thomas & Betts (conduites)", "sector": "237120", "nb": 180, "region": "Québec"},
    {"name": "Bricon (aqueduc)", "sector": "237120", "nb": 150, "region": "Montréal"},
    {"name": "Les Excavations Marchand", "sector": "237120", "nb": 120, "region": "Lanaudière"},
    {"name": "Entreprises Michaudville", "sector": "237120", "nb": 180, "region": "Chaudière-Appalaches"},
    
    # Lignes électriques/Télécoms (237130)
    {"name": "Hydro-Québec Équipement (TransÉnergie)", "sector": "237130", "nb": 3500, "region": "Montréal"},
    {"name": "Valard Construction (lignes HT)", "sector": "237130", "nb": 850, "region": "Québec"},
    {"name": "Alcatel Submarine Networks", "sector": "237130", "nb": 280, "region": "Montréal"},
    {"name": "Électro-Câble", "sector": "237130", "nb": 180, "region": "Montréal"},
    {"name": "Installation BG (télécom)", "sector": "237130", "nb": 220, "region": "Québec"},
    {"name": "Groupe Riccobono (lignes)", "sector": "237130", "nb": 320, "region": "Montréal"},
    
    # Autres génie civil - Barrages/Éoliennes (237990)
    {"name": "Hydro-Québec Production (barrages)", "sector": "237990", "nb": 2800, "region": "Côte-Nord"},
    {"name": "SNC-Lavalin Énergie", "sector": "237990", "nb": 1500, "region": "Montréal"},
    {"name": "Borea Construction (éoliennes)", "sector": "237990", "nb": 450, "region": "Gaspésie"},
    {"name": "EDF Renouvelables Canada", "sector": "237990", "nb": 280, "region": "Gaspésie"},
    {"name": "Innergex (construction)", "sector": "237990", "nb": 180, "region": "Longueuil"},
    {"name": "Norda Stelo (génie civil)", "sector": "237990", "nb": 350, "region": "Québec"},
    {"name": "CIMA+ Construction", "sector": "237990", "nb": 280, "region": "Québec"},
]

AGES = ["18-24", "25-34", "35-44", "45-54", "55-64"]


def populate_scian237():
    """Peuple SafetyGraph avec les secteurs SCIAN 237 (Génie Civil)"""
    
    print("=" * 70)
    print("⚡🏗️ POPULATION SAFETYGRAPH - SCIAN 237")
    print("    Travaux de génie civil")
    print("    ⚡ SECTEUR NÉVRALGIQUE QUÉBEC")
    print("    🔴 Hydro-Québec, barrages, lignes 735kV, pipelines")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Secteurs: {len(SECTEURS_SCIAN_237)}")
    print(f"Organisations: {len(ORGANISATIONS_SCIAN_237)}")
    print("=" * 70)
    
    conn = SafetyGraphCartographyConnector()
    conn.connect()
    print("\n✅ Neo4j connecté")
    print(f"📊 Stats initiales: {conn.get_graph_stats()}\n")
    
    stats = {"orgs": 0, "zones": 0, "risks": 0, "persons": 0, "teams": 0, "roles": 0, "tz_risks": 0}
    
    # Créer organisations
    print("📦 Création des organisations SCIAN 237 (GÉNIE CIVIL)...")
    org_map = {}
    for o in ORGANISATIONS_SCIAN_237:
        org = Organization(
            name=o["name"],
            sector_scian=o["sector"],
            nb_employes=o["nb"],
            region_ssq=o["region"]
        )
        oid = conn.inject_organization(org)
        org_map[o["name"]] = {"id": oid, "sector": o["sector"], "nb": o["nb"]}
        stats["orgs"] += 1
        print(f"   ✅ {o['name'][:45]} ({o['sector']})")
    
    # Créer entités par organisation
    print("\n🏗️ Création des entités par organisation...")
    
    for name, info in org_map.items():
        oid, sector = info["id"], info["sector"]
        data = SECTEURS_SCIAN_237[sector]
        
        # Emoji selon secteur
        emoji = "🔥" if sector == "237110" else "🚰" if sector == "237120" else "⚡" if sector == "237130" else "🏗️"
        print(f"\n   {emoji} {name[:40]}")
        print(f"      Secteur: {data['nom']}")
        
        # Rôles
        rids = []
        for r in data["roles"]:
            is_sup = any(x in r for x in ["Contremaître", "Surintendant", "Directeur"])
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
        
        # Risques (avec identification Tolérance Zéro)
        rkids = []
        tz_count = 0
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
            if r.get("tz"):
                tz_count += 1
                stats["tz_risks"] += 1
        max_score = max(r["prob"]*r["grav"] for r in data["risques"])
        print(f"      • {len(rkids)} risques (score max: {max_score}, 🔴 Tolérance Zéro: {tz_count})")
        
        # Équipes
        tids = []
        if info["nb"] > 500:
            equipes = ["Équipe Chantier Nord", "Équipe Chantier Sud", "Équipe Maintenance", "Équipe Urgence"]
        else:
            equipes = ["Équipe Chantier", "Équipe Entretien"]
            
        for t in equipes:
            team = Team(name=t, department=data["nom"][:25])
            tid = conn.inject_team(team)
            tids.append(tid)
            conn.create_relation(tid, oid, RelationType.APPARTIENT_A)
            stats["teams"] += 1
        print(f"      • {len(tids)} équipes")
        
        # Personnes (anonymisées)
        nb_persons = max(5, min(info["nb"] // 100, 25))
        for i in range(nb_persons):
            p = Person(
                matricule=f"GC237-{sector[-3:]}-{stats['persons']+1:04d}",
                department=data["nom"][:25],
                age_groupe=AGES[i % 5],
                certifications_sst=data["certs"][:5]
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
            # 95% exposés aux risques (secteur très dangereux)
            if rkids and i % 20 < 19:
                conn.create_relation(pid, rkids[i % len(rkids)], RelationType.EXPOSE_A)
        
        print(f"      • {nb_persons} personnes (anonymisées Loi 25)")
    
    # Résumé
    print("\n" + "=" * 70)
    print("📊 RÉSUMÉ POPULATION SCIAN 237 - GÉNIE CIVIL")
    print("   ⚡ SECTEUR NÉVRALGIQUE QUÉBEC")
    print("=" * 70)
    print(f"   Organisations génie civil: {stats['orgs']}")
    print(f"   Zones de travail: {stats['zones']}")
    print(f"   Risques identifiés: {stats['risks']}")
    print(f"   🔴 Risques Tolérance Zéro: {stats['tz_risks']}")
    print(f"   Équipes: {stats['teams']}")
    print(f"   Rôles/Professions: {stats['roles']}")
    print(f"   Personnes: {stats['persons']}")
    print(f"\n   Neo4j final: {conn.get_graph_stats()}")
    print("=" * 70)
    print("✅ POPULATION SCIAN 237 (GÉNIE CIVIL) TERMINÉE!")
    print("=" * 70)
    
    conn.close()
    return stats


if __name__ == "__main__":
    populate_scian237()
