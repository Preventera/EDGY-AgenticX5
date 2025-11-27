#!/usr/bin/env python3
import os, sys
from datetime import datetime
sys.path.insert(0, os.path.dirname(__file__))

from src.cartography.connector import SafetyGraphCartographyConnector
from src.cartography.models import Organization, Person, Team, Role, Zone, Risk, RiskLevel, RelationType

SECTEURS_SCIAN_11 = {
    "111": {
        "nom": "Cultures agricoles",
        "risques": [
            {"desc": "Renversement tracteur", "cat": "mecanique", "prob": 3, "grav": 5},
            {"desc": "Exposition pesticides", "cat": "chimique", "prob": 4, "grav": 4},
            {"desc": "Coincement prise de force", "cat": "mecanique", "prob": 2, "grav": 5},
            {"desc": "Coup de chaleur", "cat": "thermique", "prob": 4, "grav": 4},
        ],
        "zones": [
            {"nom": "Champs de culture", "risk": "eleve", "dangers": ["Renversement", "Pesticides"], "epi": ["Chapeau", "Gants"]},
            {"nom": "Atelier machinerie", "risk": "eleve", "dangers": ["Coincement"], "epi": ["Chaussures sécurité"]},
            {"nom": "Serre agricole", "risk": "moyen", "dangers": ["Chaleur", "Pesticides"], "epi": ["Gants", "Masque"]},
        ],
        "roles": ["Agriculteur", "Ouvrier agricole", "Opérateur machinerie", "Chef de culture"],
        "certs": ["SIMDUT", "Pesticides", "Premiers soins"],
    },
    "112": {
        "nom": "Élevage",
        "risques": [
            {"desc": "Coup/écrasement par animaux", "cat": "biologique", "prob": 4, "grav": 4},
            {"desc": "Gaz de lisier (H2S, CO2)", "cat": "chimique", "prob": 3, "grav": 5},
            {"desc": "Asphyxie fosse à lisier", "cat": "chimique", "prob": 2, "grav": 5},
            {"desc": "Zoonoses transmissibles", "cat": "biologique", "prob": 3, "grav": 4},
        ],
        "zones": [
            {"nom": "Étable", "risk": "eleve", "dangers": ["Coup animal", "Zoonoses"], "epi": ["Bottes", "Gants"]},
            {"nom": "Porcherie", "risk": "critique", "dangers": ["Gaz lisier", "Bruit"], "epi": ["Masque", "Bouchons"]},
            {"nom": "Fosse à lisier", "risk": "critique", "dangers": ["H2S", "Asphyxie"], "epi": ["Détecteur gaz", "Harnais"]},
        ],
        "roles": ["Éleveur", "Ouvrier agricole", "Préposé soins animaux", "Chef exploitation"],
        "certs": ["SIMDUT", "Espace clos", "Détection gaz", "Premiers soins"],
    },
    "113": {
        "nom": "Foresterie",
        "risques": [
            {"desc": "Frappé par arbre en chute", "cat": "mecanique", "prob": 3, "grav": 5},
            {"desc": "Blessure scie à chaîne", "cat": "mecanique", "prob": 4, "grav": 5},
            {"desc": "Renversement abatteuse", "cat": "mecanique", "prob": 3, "grav": 5},
            {"desc": "Écrasement par grumes", "cat": "mecanique", "prob": 3, "grav": 5},
            {"desc": "Bruit scie >100dB", "cat": "bruit", "prob": 5, "grav": 4},
        ],
        "zones": [
            {"nom": "Zone abattage", "risk": "critique", "dangers": ["Chute arbre", "Scie à chaîne"], "epi": ["Casque forestier", "Jambières"]},
            {"nom": "Zone débardage", "risk": "critique", "dangers": ["Écrasement", "Renversement"], "epi": ["Casque", "Dossard"]},
            {"nom": "Aire empilement", "risk": "eleve", "dangers": ["Écrasement billots"], "epi": ["Casque", "Bottes"]},
        ],
        "roles": ["Abatteur manuel", "Opérateur abatteuse", "Débardeur", "Sylviculteur", "Contremaître forestier"],
        "certs": ["Abattage manuel CNESST", "Secourisme forêt", "Scie à chaîne"],
    },
    "114": {
        "nom": "Pêche et chasse",
        "risques": [
            {"desc": "Noyade chute par-dessus bord", "cat": "noyade", "prob": 3, "grav": 5},
            {"desc": "Hypothermie eau froide", "cat": "thermique", "prob": 3, "grav": 5},
            {"desc": "Glissade pont mouillé", "cat": "chute", "prob": 5, "grav": 3},
            {"desc": "Écrasement équipement pont", "cat": "mecanique", "prob": 3, "grav": 4},
        ],
        "zones": [
            {"nom": "Pont de bateau", "risk": "critique", "dangers": ["Noyade", "Glissade"], "epi": ["VFI", "Bottes antidérapantes"]},
            {"nom": "Cale à poisson", "risk": "eleve", "dangers": ["Glissade", "Froid"], "epi": ["Bottes", "Gants"]},
            {"nom": "Zone de chasse", "risk": "eleve", "dangers": ["Arme à feu", "Froid"], "epi": ["Dossard orange"]},
        ],
        "roles": ["Capitaine bateau", "Matelot-pêcheur", "Chasseur commercial", "Guide chasse"],
        "certs": ["Sauvetage maritime", "VFI", "Permis armes"],
    },
    "115": {
        "nom": "Soutien agriculture/foresterie",
        "risques": [
            {"desc": "Épandage pesticides", "cat": "chimique", "prob": 3, "grav": 4},
            {"desc": "Renversement équipement", "cat": "mecanique", "prob": 3, "grav": 5},
            {"desc": "TMS plantation répétitive", "cat": "ergonomique", "prob": 5, "grav": 3},
            {"desc": "Morsure tiques (Lyme)", "cat": "biologique", "prob": 4, "grav": 3},
        ],
        "zones": [
            {"nom": "Zone épandage", "risk": "eleve", "dangers": ["Pesticides"], "epi": ["Combinaison", "Masque"]},
            {"nom": "Site plantation", "risk": "moyen", "dangers": ["TMS", "Insectes"], "epi": ["Chapeau", "Gants"]},
        ],
        "roles": ["Opérateur épandage", "Planteur forestier", "Débroussailleur", "Chef équipe"],
        "certs": ["SIMDUT", "Pesticides", "Scie à chaîne"],
    },
}

ORGS = [
    {"name": "Fermes Maraîchères Québec", "sector": "111", "nb": 45, "region": "Montérégie"},
    {"name": "Vergers Paul Jodoin", "sector": "111", "nb": 25, "region": "Montérégie"},
    {"name": "Ferme Laitière Rivière-du-Loup", "sector": "112", "nb": 35, "region": "Bas-Saint-Laurent"},
    {"name": "Porcherie Beauce inc.", "sector": "112", "nb": 28, "region": "Beauce"},
    {"name": "Ferme Avicole Lanaudière", "sector": "112", "nb": 40, "region": "Lanaudière"},
    {"name": "Coopérative Forestière BSL", "sector": "113", "nb": 180, "region": "Bas-Saint-Laurent"},
    {"name": "Rexforêt inc.", "sector": "113", "nb": 250, "region": "Abitibi"},
    {"name": "Sylviculture Mauricie", "sector": "113", "nb": 85, "region": "Mauricie"},
    {"name": "Pêcheries Gaspésiennes", "sector": "114", "nb": 65, "region": "Gaspésie"},
    {"name": "Coopérative Pêcheurs Natashquan", "sector": "114", "nb": 35, "region": "Côte-Nord"},
    {"name": "Services Forestiers Québec", "sector": "115", "nb": 150, "region": "Capitale-Nationale"},
    {"name": "Plantations Boréales inc.", "sector": "115", "nb": 200, "region": "Abitibi"},
]

AGES = ["18-24", "25-34", "35-44", "45-54", "55-64"]

def populate():
    print("=" * 60)
    print("🌾🌲🎣 POPULATION SAFETYGRAPH - SCIAN 11")
    print("=" * 60)
    
    conn = SafetyGraphCartographyConnector()
    conn.connect()
    print("✅ Neo4j connecté\n")
    
    stats = {"orgs": 0, "zones": 0, "risks": 0, "persons": 0, "teams": 0, "roles": 0}
    
    print("📦 Organisations SCIAN 11...")
    org_map = {}
    for o in ORGS:
        org = Organization(name=o["name"], sector_scian=o["sector"], nb_employes=o["nb"], region_ssq=o["region"])
        oid = conn.inject_organization(org)
        org_map[o["name"]] = {"id": oid, "sector": o["sector"], "nb": o["nb"]}
        stats["orgs"] += 1
        print(f"   ✅ {o['name']} ({o['sector']})")
    
    print("\n🏗️ Entités par organisation...")
    for name, info in org_map.items():
        oid, sector = info["id"], info["sector"]
        data = SECTEURS_SCIAN_11[sector]
        print(f"\n   📍 {name} - {data['nom']}")
        
        rids = []
        for r in data["roles"]:
            role = Role(name=r, niveau_hierarchique=3 if "Chef" in r or "Contremaître" in r or "Capitaine" in r else 1)
            rids.append(conn.inject_role(role))
            stats["roles"] += 1
        print(f"      • {len(rids)} rôles")
        
        zids = []
        for z in data["zones"]:
            zone = Zone(name=z["nom"], risk_level=RiskLevel(z["risk"]), dangers_identifies=z["dangers"], epi_requis=z["epi"])
            zid = conn.inject_zone(zone)
            zids.append(zid)
            conn.create_relation(zid, oid, RelationType.APPARTIENT_A)
            stats["zones"] += 1
        print(f"      • {len(zids)} zones")
        
        rkids = []
        for i, r in enumerate(data["risques"]):
            risk = Risk(description=r["desc"], categorie=r["cat"], probabilite=r["prob"], gravite=r["grav"], statut="actif")
            rid = conn.inject_risk(risk)
            rkids.append(rid)
            if zids: conn.create_relation(rid, zids[i % len(zids)], RelationType.LOCALISE_DANS)
            stats["risks"] += 1
        print(f"      • {len(rkids)} risques")
        
        tids = []
        equipes = ["Équipe Coupe", "Équipe Débardage"] if sector == "113" else ["Équipe Principale", "Équipe Saisonnière"]
        for t in equipes:
            team = Team(name=t, department=data["nom"][:20])
            tid = conn.inject_team(team)
            tids.append(tid)
            conn.create_relation(tid, oid, RelationType.APPARTIENT_A)
            stats["teams"] += 1
        print(f"      • {len(tids)} équipes")
        
        nb = max(4, min(info["nb"] // 10, 10))
        for i in range(nb):
            p = Person(matricule=f"AGRI11-{stats['persons']+1:04d}", department=data["nom"][:20], age_groupe=AGES[i % 5], certifications_sst=data["certs"][:2])
            pid = conn.inject_person(p, anonymize=True)
            stats["persons"] += 1
            if tids: conn.create_relation(pid, tids[i % len(tids)], RelationType.MEMBRE_DE)
            if rids: conn.create_relation(pid, rids[i % len(rids)], RelationType.OCCUPE_ROLE)
            if zids: conn.create_relation(pid, zids[i % len(zids)], RelationType.TRAVAILLE_DANS)
        print(f"      • {nb} personnes")
    
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ SCIAN 11")
    for k, v in stats.items(): print(f"   {k}: {v}")
    print(f"\n   Neo4j: {conn.get_graph_stats()}")
    print("=" * 60)
    print("✅ TERMINÉ!")
    conn.close()

if __name__ == "__main__":
    populate()
