#!/usr/bin/env python3
"""
🛡️ Script de Population Neo4j - Secteurs SCIAN 33 (Fabrication)
EDGY-AgenticX5 | SafetyGraph | Preventera
"""

import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

from src.cartography.connector import SafetyGraphCartographyConnector
from src.cartography.models import Organization, Person, Team, Role, Zone, Risk, RiskLevel, RelationType

SECTEURS_SCIAN_33 = {
    "332710": {
        "nom": "Ateliers d'usinage",
        "risques": [
            {"desc": "Coincement dans tour/fraiseuse CNC", "cat": "mecanique", "prob": 4, "grav": 5},
            {"desc": "Projection copeaux métalliques", "cat": "mecanique", "prob": 5, "grav": 3},
            {"desc": "Coupure par pièces usinées", "cat": "mecanique", "prob": 4, "grav": 3},
            {"desc": "Bruit machines >90dB", "cat": "bruit", "prob": 5, "grav": 3},
            {"desc": "Exposition huiles de coupe", "cat": "chimique", "prob": 4, "grav": 3},
        ],
        "zones": [
            {"nom": "Zone tours CNC", "risk": "critique", "dangers": ["Coincement", "Projection"], "epi": ["Lunettes", "Bouchons"]},
            {"nom": "Zone fraiseuses", "risk": "eleve", "dangers": ["Coincement", "Coupure"], "epi": ["Lunettes", "Gants"]},
            {"nom": "Zone meulage", "risk": "eleve", "dangers": ["Projection", "Bruit"], "epi": ["Lunettes", "Masque"]},
        ],
        "roles": ["Machiniste CNC", "Tourneur", "Fraiseur", "Superviseur atelier"],
        "certs": ["SIMDUT", "Cadenassage", "Pont roulant"],
    },
    "332113": {
        "nom": "Forgeage",
        "risques": [
            {"desc": "Brûlure par métal en fusion", "cat": "thermique", "prob": 4, "grav": 5},
            {"desc": "Écrasement par marteau-pilon", "cat": "mecanique", "prob": 3, "grav": 5},
            {"desc": "Exposition chaleur extrême >40C", "cat": "thermique", "prob": 5, "grav": 4},
            {"desc": "Bruit impulsionnel forgeage", "cat": "bruit", "prob": 5, "grav": 4},
        ],
        "zones": [
            {"nom": "Zone fours", "risk": "critique", "dangers": ["Brûlure", "Chaleur"], "epi": ["Vêtements aluminisés", "Gants thermiques"]},
            {"nom": "Zone marteaux-pilons", "risk": "critique", "dangers": ["Écrasement", "Bruit"], "epi": ["Casque", "Bouchons"]},
        ],
        "roles": ["Forgeron", "Opérateur marteau-pilon", "Chauffeur four", "Contremaître forge"],
        "certs": ["SIMDUT", "Cadenassage", "Travail chaleur"],
    },
    "331110": {
        "nom": "Sidérurgie",
        "risques": [
            {"desc": "Contact métal en fusion", "cat": "thermique", "prob": 3, "grav": 5},
            {"desc": "Inhalation fumées métalliques", "cat": "chimique", "prob": 4, "grav": 4},
            {"desc": "Coincement laminoir", "cat": "mecanique", "prob": 3, "grav": 5},
            {"desc": "Exposition monoxyde carbone", "cat": "chimique", "prob": 3, "grav": 5},
        ],
        "zones": [
            {"nom": "Zone haut-fourneau", "risk": "critique", "dangers": ["Métal fusion", "CO"], "epi": ["Combinaison aluminisée", "Masque"]},
            {"nom": "Zone laminoir", "risk": "critique", "dangers": ["Coincement", "Chaleur"], "epi": ["Casque", "Lunettes"]},
        ],
        "roles": ["Opérateur haut-fourneau", "Lamineur", "Pontier", "Chef sidérurgie"],
        "certs": ["SIMDUT", "Cadenassage", "Espace clos", "Détection gaz"],
    },
    "331511": {
        "nom": "Fonderies de fer",
        "risques": [
            {"desc": "Brûlure métal en fusion", "cat": "thermique", "prob": 4, "grav": 5},
            {"desc": "Inhalation silice cristalline", "cat": "chimique", "prob": 4, "grav": 5},
            {"desc": "Explosion poche de coulée", "cat": "thermique", "prob": 2, "grav": 5},
        ],
        "zones": [
            {"nom": "Zone fusion/coulée", "risk": "critique", "dangers": ["Métal fusion", "Explosion"], "epi": ["Combinaison aluminisée", "Visière"]},
            {"nom": "Zone moulage sable", "risk": "eleve", "dangers": ["Silice", "Poussière"], "epi": ["Masque P100"]},
        ],
        "roles": ["Fondeur", "Mouleur", "Noyauteur", "Contremaître fonderie"],
        "certs": ["SIMDUT", "Protection respiratoire", "Travail chaleur"],
    },
    "336410": {
        "nom": "Fabrication aérospatiale",
        "risques": [
            {"desc": "Exposition composites/résines époxy", "cat": "chimique", "prob": 4, "grav": 4},
            {"desc": "Chute travail hauteur aéronef", "cat": "chute", "prob": 3, "grav": 5},
            {"desc": "Bruit rivetage/perçage", "cat": "bruit", "prob": 5, "grav": 3},
            {"desc": "TMS postures contraignantes", "cat": "ergonomique", "prob": 5, "grav": 4},
        ],
        "zones": [
            {"nom": "Zone assemblage fuselage", "risk": "eleve", "dangers": ["Chute hauteur", "Ergonomie"], "epi": ["Harnais", "Casque"]},
            {"nom": "Zone composites", "risk": "critique", "dangers": ["Résines", "Poussières"], "epi": ["Combinaison", "Masque respiratoire"]},
        ],
        "roles": ["Assembleur aéronautique", "Technicien composites", "Riveteur", "Chef assemblage"],
        "certs": ["SIMDUT", "Travail hauteur", "Protection respiratoire"],
    },
    "332319": {
        "nom": "Charpentes métalliques",
        "risques": [
            {"desc": "Inhalation fumées soudage", "cat": "chimique", "prob": 5, "grav": 4},
            {"desc": "Brûlure soudure/découpe", "cat": "thermique", "prob": 4, "grav": 3},
            {"desc": "Exposition UV soudage", "cat": "rayonnement", "prob": 5, "grav": 3},
            {"desc": "Chute pièces lourdes", "cat": "mecanique", "prob": 4, "grav": 5},
        ],
        "zones": [
            {"nom": "Zone soudure", "risk": "critique", "dangers": ["Fumées", "UV", "Brûlure"], "epi": ["Masque soudeur", "Gants", "Tablier"]},
            {"nom": "Zone découpe plasma", "risk": "critique", "dangers": ["Brûlure", "Fumées"], "epi": ["Masque soudeur", "Gants cuir"]},
        ],
        "roles": ["Soudeur-assembleur", "Opérateur découpe", "Monteur structures", "Chef atelier"],
        "certs": ["SIMDUT", "Soudage CWB", "Pont roulant"],
    },
    "336611": {
        "nom": "Construction navale",
        "risques": [
            {"desc": "Chute hauteur coque/échafaudages", "cat": "chute", "prob": 4, "grav": 5},
            {"desc": "Noyade travail sur eau", "cat": "noyade", "prob": 2, "grav": 5},
            {"desc": "Asphyxie espace clos cales", "cat": "chimique", "prob": 3, "grav": 5},
            {"desc": "Inhalation fumées soudage", "cat": "chimique", "prob": 5, "grav": 4},
        ],
        "zones": [
            {"nom": "Zone cale sèche", "risk": "critique", "dangers": ["Chute", "Noyade"], "epi": ["Harnais", "VFI", "Casque"]},
            {"nom": "Zone soudure coque", "risk": "critique", "dangers": ["Fumées", "Espace clos"], "epi": ["Masque soudeur", "Détecteur gaz"]},
        ],
        "roles": ["Soudeur naval", "Charpentier naval", "Tuyauteur", "Chef chantier naval"],
        "certs": ["SIMDUT", "Travail hauteur", "Espace clos", "Sauvetage aquatique"],
    },
}

ORGANISATIONS_SCIAN_33 = [
    {"name": "Usinage Précision Québec", "sector": "332710", "nb": 45, "region": "Québec"},
    {"name": "Ateliers CNC Montréal", "sector": "332710", "nb": 85, "region": "Montréal"},
    {"name": "Forges Industrielles St-Laurent", "sector": "332113", "nb": 120, "region": "Trois-Rivières"},
    {"name": "ArcelorMittal Contrecoeur", "sector": "331110", "nb": 1200, "region": "Montérégie"},
    {"name": "Aciers Inoxydables Atlas", "sector": "331110", "nb": 350, "region": "Sorel-Tracy"},
    {"name": "Fonderie Laperle", "sector": "331511", "nb": 180, "region": "Montréal"},
    {"name": "Fonderies de Beauce", "sector": "331511", "nb": 95, "region": "Beauce"},
    {"name": "Bombardier Aéronautique", "sector": "336410", "nb": 3500, "region": "Montréal"},
    {"name": "Héroux-Devtek", "sector": "336410", "nb": 800, "region": "Longueuil"},
    {"name": "Structures Canam", "sector": "332319", "nb": 650, "region": "Québec"},
    {"name": "Acier Métropolitain", "sector": "332319", "nb": 180, "region": "Montréal"},
    {"name": "Chantier Davie Canada", "sector": "336611", "nb": 1500, "region": "Lévis"},
    {"name": "Océan Industries", "sector": "336611", "nb": 280, "region": "Gaspésie"},
]

AGES = ["18-24", "25-34", "35-44", "45-54", "55-64"]

def populate_scian33():
    print("=" * 60)
    print("🛡️ POPULATION SAFETYGRAPH - SCIAN 33 (FABRICATION)")
    print("=" * 60)
    
    conn = SafetyGraphCartographyConnector()
    conn.connect()
    print("✅ Neo4j connecté\n")
    
    stats = {"orgs": 0, "zones": 0, "risks": 0, "persons": 0, "teams": 0, "roles": 0}
    
    print("📦 Organisations SCIAN 33...")
    org_map = {}
    for o in ORGANISATIONS_SCIAN_33:
        org = Organization(name=o["name"], sector_scian=o["sector"], nb_employes=o["nb"], region_ssq=o["region"])
        oid = conn.inject_organization(org)
        org_map[o["name"]] = {"id": oid, "sector": o["sector"], "nb": o["nb"]}
        stats["orgs"] += 1
        print(f"   ✅ {o['name']} ({o['sector']})")
    
    print("\n🏗️ Entités par organisation...")
    for name, info in org_map.items():
        oid, sector = info["id"], info["sector"]
        data = SECTEURS_SCIAN_33[sector]
        print(f"\n   📍 {name} - {data['nom']}")
        
        rids = []
        for r in data["roles"]:
            role = Role(name=r, niveau_hierarchique=3 if "Chef" in r or "Contremaître" in r or "Superviseur" in r else 1)
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
        equipes = ["Jour", "Soir", "Nuit"] if info["nb"] > 500 else ["Jour", "Soir"]
        for t in equipes:
            team = Team(name=f"Équipe {t}", department=data["nom"][:20])
            tid = conn.inject_team(team)
            tids.append(tid)
            conn.create_relation(tid, oid, RelationType.APPARTIENT_A)
            stats["teams"] += 1
        print(f"      • {len(tids)} équipes")
        
        nb = max(5, min(info["nb"] // 100, 12))
        for i in range(nb):
            p = Person(matricule=f"FAB33-{stats['persons']+1:04d}", department=data["nom"][:20], age_groupe=AGES[i % 5], certifications_sst=data["certs"][:2])
            pid = conn.inject_person(p, anonymize=True)
            stats["persons"] += 1
            if tids: conn.create_relation(pid, tids[i % len(tids)], RelationType.MEMBRE_DE)
            if rids: conn.create_relation(pid, rids[i % len(rids)], RelationType.OCCUPE_ROLE)
            if zids: conn.create_relation(pid, zids[i % len(zids)], RelationType.TRAVAILLE_DANS)
        print(f"      • {nb} personnes")
    
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ SCIAN 33")
    for k, v in stats.items(): print(f"   {k}: {v}")
    print(f"\n   Neo4j: {conn.get_graph_stats()}")
    print("=" * 60)
    print("✅ TERMINÉ!")
    conn.close()

if __name__ == "__main__":
    populate_scian33()
