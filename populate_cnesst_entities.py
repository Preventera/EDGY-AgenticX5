#!/usr/bin/env python3
"""Population Neo4j - Données CNESST"""

import os, sys
from datetime import datetime
sys.path.insert(0, os.path.dirname(__file__))

from src.cartography.connector import SafetyGraphCartographyConnector
from src.cartography.models import Organization, Person, Team, Role, Zone, Risk, RiskLevel, RelationType

SECTEURS = {
    "611110": {
        "nom": "Écoles",
        "risques": [{"desc": "Chute escalier", "cat": "chute", "prob": 4, "grav": 3}, {"desc": "Chute échelle", "cat": "chute", "prob": 3, "grav": 4}],
        "zones": [{"nom": "Salle classe", "risk": "faible", "dangers": ["Chute"], "epi": []}, {"nom": "Gymnase", "risk": "moyen", "dangers": ["Impact"], "epi": []}, {"nom": "Escaliers", "risk": "moyen", "dangers": ["Chute"], "epi": []}],
        "roles": ["Enseignant", "Concierge", "Éducateur"],
        "certs": ["SIMDUT", "Premiers soins"],
    },
    "23": {
        "nom": "Construction", 
        "risques": [{"desc": "Chute hauteur", "cat": "chute", "prob": 4, "grav": 5}, {"desc": "Coincement", "cat": "mecanique", "prob": 3, "grav": 5}, {"desc": "Électrocution", "cat": "electrique", "prob": 2, "grav": 5}],
        "zones": [{"nom": "Zone excavation", "risk": "critique", "dangers": ["Effondrement"], "epi": ["Casque"]}, {"nom": "Travail hauteur", "risk": "critique", "dangers": ["Chute"], "epi": ["Harnais"]}],
        "roles": ["Charpentier", "Électricien", "Contremaître"],
        "certs": ["SIMDUT", "Travail hauteur", "ASP"],
    },
    "31-33": {
        "nom": "Fabrication",
        "risques": [{"desc": "Coincement machine", "cat": "mecanique", "prob": 3, "grav": 5}, {"desc": "Bruit >90dB", "cat": "bruit", "prob": 5, "grav": 3}],
        "zones": [{"nom": "Ligne production", "risk": "eleve", "dangers": ["Coincement"], "epi": ["Lunettes"]}, {"nom": "Zone soudure", "risk": "critique", "dangers": ["Brûlure"], "epi": ["Masque"]}],
        "roles": ["Opérateur", "Soudeur", "Superviseur"],
        "certs": ["SIMDUT", "Cadenassage"],
    },
    "62": {
        "nom": "Santé",
        "risques": [{"desc": "Blessure patient", "cat": "ergonomique", "prob": 5, "grav": 4}, {"desc": "Piqûre", "cat": "biologique", "prob": 4, "grav": 4}],
        "zones": [{"nom": "Urgence", "risk": "critique", "dangers": ["Violence"], "epi": ["Gants"]}, {"nom": "Chambre", "risk": "moyen", "dangers": ["Ergonomie"], "epi": ["Gants"]}],
        "roles": ["Infirmière", "Préposé", "Médecin"],
        "certs": ["SIMDUT", "PDSB", "RCR"],
    },
    "48-49": {
        "nom": "Transport",
        "risques": [{"desc": "Accident route", "cat": "mecanique", "prob": 3, "grav": 5}, {"desc": "Collision chariot", "cat": "mecanique", "prob": 3, "grav": 5}],
        "zones": [{"nom": "Quai", "risk": "eleve", "dangers": ["Chute"], "epi": ["Casque"]}, {"nom": "Zone chariots", "risk": "critique", "dangers": ["Collision"], "epi": ["Dossard"]}],
        "roles": ["Camionneur", "Cariste", "Superviseur"],
        "certs": ["SIMDUT", "Chariot"],
    },
}

ORGS = [
    {"name": "École Jean-de-Brébeuf", "sector": "611110", "nb": 180},
    {"name": "École Félix-Leclerc", "sector": "611110", "nb": 45},
    {"name": "Construction Pomerleau", "sector": "23", "nb": 500},
    {"name": "Construction ABC", "sector": "23", "nb": 35},
    {"name": "Usine Métallurgique QC", "sector": "31-33", "nb": 350},
    {"name": "Industries Plastiques", "sector": "31-33", "nb": 120},
    {"name": "CHSLD Jardins du Parc", "sector": "62", "nb": 200},
    {"name": "Clinique Santé Plus", "sector": "62", "nb": 40},
    {"name": "Transport Routier QC", "sector": "48-49", "nb": 85},
    {"name": "Entrepôts Distribution", "sector": "48-49", "nb": 50},
]

AGES = ["18-24", "25-34", "35-44", "45-54", "55-64"]

def populate():
    print("=" * 50)
    print("🛡️ POPULATION SAFETYGRAPH - CNESST")
    print("=" * 50)
    
    conn = SafetyGraphCartographyConnector()
    conn.connect()
    print("✅ Neo4j connecté\n")
    
    stats = {"orgs": 0, "zones": 0, "risks": 0, "persons": 0, "teams": 0, "roles": 0}
    
    print("📦 Organisations...")
    org_map = {}
    for o in ORGS:
        org = Organization(name=o["name"], sector_scian=o["sector"], nb_employes=o["nb"])
        oid = conn.inject_organization(org)
        org_map[o["name"]] = {"id": oid, "sector": o["sector"], "nb": o["nb"]}
        stats["orgs"] += 1
        print(f"   ✅ {o['name']}")
    
    print("\n🏗️ Entités par org...")
    for name, info in org_map.items():
        oid, sector = info["id"], info["sector"]
        data = SECTEURS[sector]
        print(f"\n   📍 {name}")
        
        # Rôles
        rids = []
        for r in data["roles"]:
            role = Role(name=r, niveau_hierarchique=3 if "Superviseur" in r or "Contremaître" in r else 1)
            rids.append(conn.inject_role(role))
            stats["roles"] += 1
        print(f"      • {len(rids)} rôles")
        
        # Zones (SANS description)
        zids = []
        for z in data["zones"]:
            zone = Zone(name=z["nom"], risk_level=RiskLevel(z["risk"]), dangers_identifies=z["dangers"], epi_requis=z["epi"])
            zid = conn.inject_zone(zone)
            zids.append(zid)
            conn.create_relation(zid, oid, RelationType.APPARTIENT_A)
            stats["zones"] += 1
        print(f"      • {len(zids)} zones")
        
        # Risques
        rkids = []
        for i, r in enumerate(data["risques"]):
            risk = Risk(description=r["desc"], categorie=r["cat"], probabilite=r["prob"], gravite=r["grav"], statut="actif")
            rid = conn.inject_risk(risk)
            rkids.append(rid)
            if zids: conn.create_relation(rid, zids[i % len(zids)], RelationType.LOCALISE_DANS)
            stats["risks"] += 1
        print(f"      • {len(rkids)} risques")
        
        # Équipes
        tids = []
        for t in ["Jour", "Soir"]:
            team = Team(name=f"Équipe {t}", department=data["nom"])
            tid = conn.inject_team(team)
            tids.append(tid)
            conn.create_relation(tid, oid, RelationType.APPARTIENT_A)
            stats["teams"] += 1
        print(f"      • {len(tids)} équipes")
        
        # Personnes
        nb = max(5, min(info["nb"] // 25, 8))
        for i in range(nb):
            p = Person(matricule=f"EMP-{stats['persons']+1:04d}", department=data["nom"], age_groupe=AGES[i % 5], certifications_sst=data["certs"][:2])
            pid = conn.inject_person(p, anonymize=True)
            stats["persons"] += 1
            if tids: conn.create_relation(pid, tids[i % len(tids)], RelationType.MEMBRE_DE)
            if rids: conn.create_relation(pid, rids[i % len(rids)], RelationType.OCCUPE_ROLE)
            if zids: conn.create_relation(pid, zids[i % len(zids)], RelationType.TRAVAILLE_DANS)
        print(f"      • {nb} personnes")
    
    print("\n" + "=" * 50)
    print("📊 RÉSUMÉ")
    for k, v in stats.items(): print(f"   {k}: {v}")
    print(f"\n   Neo4j: {conn.get_graph_stats()}")
    print("=" * 50)
    print("✅ TERMINÉ!")
    conn.close()

if __name__ == "__main__":
    populate()