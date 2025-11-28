#!/usr/bin/env python3
"""
🛡️ Script de Population Neo4j - Secteurs SCIAN 22
Services publics (Utilities)
EDGY-AgenticX5 | SafetyGraph | Preventera

⚡ INFRASTRUCTURES CRITIQUES QUÉBEC
   Hydro-Québec Distribution, Énergir, services eau
   Réseaux électriques, gaz naturel, eau potable, assainissement

Secteurs inclus:
- 221111: Production d'électricité hydroélectrique
- 221112: Production d'électricité thermique
- 221119: Autres types de production d'électricité (éolien, solaire)
- 221121: Distribution d'électricité
- 221210: Distribution de gaz naturel
- 221310: Réseaux d'aqueduc et systèmes d'irrigation
- 221320: Réseaux d'égout et installations d'assainissement

Risques Tolérance Zéro spécifiques:
- Électrocution haute/moyenne tension
- Arc électrique (arc flash)
- Explosion gaz naturel
- Espace clos (réservoirs, chambres)
- Asphyxie (H2S, méthane)
- Chute de hauteur (pylônes, réservoirs)
"""

import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

from src.cartography.connector import SafetyGraphCartographyConnector
from src.cartography.models import Organization, Person, Team, Role, Zone, Risk, RiskLevel, RelationType

# ============================================================================
# DONNÉES CNESST - SECTEURS SCIAN 22 (SERVICES PUBLICS)
# INFRASTRUCTURES CRITIQUES QUÉBEC
# ============================================================================

SECTEURS_SCIAN_22 = {
    "221111": {
        "nom": "Production d'électricité hydroélectrique",
        "description": "Centrales hydroélectriques, barrages, turbines",
        "risques": [
            {"desc": "Électrocution équipement haute tension", "cat": "electrique", "prob": 2, "grav": 5, "tz": True},
            {"desc": "Arc électrique flash (alternateurs)", "cat": "electrique", "prob": 2, "grav": 5, "tz": True},
            {"desc": "Noyade vannes/canal fuite", "cat": "physique", "prob": 2, "grav": 5, "tz": True},
            {"desc": "Chute hauteur galeries/structures", "cat": "chute", "prob": 3, "grav": 5, "tz": True},
            {"desc": "Espace clos galeries souterraines", "cat": "chimique", "prob": 2, "grav": 5, "tz": True},
            {"desc": "Écrasement équipement rotatif", "cat": "mecanique", "prob": 2, "grav": 5},
            {"desc": "Bruit turbines/alternateurs >95dB", "cat": "bruit", "prob": 5, "grav": 3},
            {"desc": "Huile isolante PCB (anciens équipements)", "cat": "chimique", "prob": 2, "grav": 4},
        ],
        "zones": [
            {"nom": "Salle des machines (turbines)", "risk": "critique", "dangers": ["Électrocution", "Écrasement", "Bruit"], "epi": ["Protection auditive", "Casque", "Bottes isolantes"]},
            {"nom": "Galerie d'amenée/fuite", "risk": "critique", "dangers": ["Noyade", "Espace clos", "Chute"], "epi": ["VFI", "Détecteur gaz", "Harnais"]},
            {"nom": "Poste élévateur", "risk": "critique", "dangers": ["Électrocution HT", "Arc flash"], "epi": ["EPI arc flash complet", "Gants isolants"]},
            {"nom": "Évacuateur de crues", "risk": "eleve", "dangers": ["Noyade", "Chute"], "epi": ["VFI", "Harnais", "Radio"]},
        ],
        "roles": ["Opérateur centrale", "Technicien électricité HT", "Mécanicien turbines", "Technicien instrumentation", "Chef de quart", "Surintendant centrale"],
        "certs": ["Hydro-Québec HT", "Espace clos", "Cadenassage LOTO", "Sauvetage aquatique", "Premiers soins"],
    },
    
    "221119": {
        "nom": "Autres types de production d'électricité",
        "description": "Éolien, solaire, biomasse",
        "risques": [
            {"desc": "Chute nacelle éolienne (80-150m)", "cat": "chute", "prob": 2, "grav": 5, "tz": True},
            {"desc": "Électrocution convertisseur/transformateur", "cat": "electrique", "prob": 2, "grav": 5, "tz": True},
            {"desc": "Écrasement pales rotation", "cat": "mecanique", "prob": 1, "grav": 5},
            {"desc": "Arc électrique onduleur solaire", "cat": "electrique", "prob": 2, "grav": 4},
            {"desc": "Espace clos nacelle éolienne", "cat": "chimique", "prob": 2, "grav": 4},
            {"desc": "Chute toiture panneaux solaires", "cat": "chute", "prob": 3, "grav": 4},
            {"desc": "Brûlure électrique DC solaire", "cat": "electrique", "prob": 3, "grav": 3},
            {"desc": "Exposition froid/vent altitude", "cat": "thermique", "prob": 4, "grav": 3},
        ],
        "zones": [
            {"nom": "Nacelle éolienne (80-150m)", "risk": "critique", "dangers": ["Chute extrême", "Électrocution", "Espace clos"], "epi": ["Harnais 100%", "Kit évacuation", "Casque"]},
            {"nom": "Mât éolienne (intérieur)", "risk": "critique", "dangers": ["Chute", "Espace clos"], "epi": ["Harnais", "Détecteur O2", "Casque"]},
            {"nom": "Champ solaire", "risk": "eleve", "dangers": ["Électrocution DC", "Chaleur"], "epi": ["Gants isolants", "Lunettes", "Chapeau"]},
            {"nom": "Poste de raccordement", "risk": "critique", "dangers": ["Électrocution", "Arc flash"], "epi": ["EPI arc flash", "Gants isolants"]},
        ],
        "roles": ["Technicien éolien", "Technicien solaire", "Électricien renouvelable", "Opérateur parc", "Superviseur maintenance"],
        "certs": ["Travail hauteur éolien", "GWO (Global Wind Organisation)", "Espace clos", "Arc flash", "Premiers soins"],
    },
    
    "221121": {
        "nom": "Distribution d'électricité",
        "description": "Réseaux moyenne/basse tension, compteurs, branchements",
        "risques": [
            {"desc": "Électrocution ligne moyenne tension", "cat": "electrique", "prob": 3, "grav": 5, "tz": True},
            {"desc": "Arc électrique transformateur", "cat": "electrique", "prob": 2, "grav": 5, "tz": True},
            {"desc": "Chute nacelle/poteau", "cat": "chute", "prob": 3, "grav": 5, "tz": True},
            {"desc": "Électrisation induction", "cat": "electrique", "prob": 3, "grav": 4},
            {"desc": "Accident véhicule nacelle", "cat": "routier", "prob": 3, "grav": 4},
            {"desc": "Morsure chien (compteurs)", "cat": "biologique", "prob": 4, "grav": 2},
            {"desc": "Agression client mécontent", "cat": "violence", "prob": 3, "grav": 3},
            {"desc": "TMS - travail en hauteur prolongé", "cat": "ergonomique", "prob": 4, "grav": 3},
        ],
        "zones": [
            {"nom": "Ligne moyenne tension (25kV)", "risk": "critique", "dangers": ["Électrocution", "Arc flash", "Chute"], "epi": ["Gants isolants", "Harnais", "Casque"]},
            {"nom": "Poste de distribution", "risk": "critique", "dangers": ["Électrocution", "Arc flash"], "epi": ["EPI arc flash", "Détecteur tension"]},
            {"nom": "Chambre souterraine câbles", "risk": "eleve", "dangers": ["Espace clos", "Électrocution"], "epi": ["Détecteur gaz", "Ventilation"]},
            {"nom": "Résidence client (compteur)", "risk": "moyen", "dangers": ["Chien", "Agression"], "epi": ["Chaussures sécurité"]},
        ],
        "roles": ["Monteur de lignes distribution", "Jointeur câbles", "Technicien compteurs", "Opérateur nacelle", "Contremaître distribution", "Répartiteur"],
        "certs": ["Hydro-Québec MT/BT", "Travail hauteur", "Conduite nacelle", "Arc flash", "Premiers soins"],
    },
    
    "221210": {
        "nom": "Distribution de gaz naturel",
        "description": "Réseaux gaz, branchements, compteurs, détection fuites",
        "risques": [
            {"desc": "Explosion gaz naturel", "cat": "chimique", "prob": 2, "grav": 5, "tz": True},
            {"desc": "Asphyxie atmosphère appauvrie O2", "cat": "chimique", "prob": 2, "grav": 5, "tz": True},
            {"desc": "Incendie fuite gaz", "cat": "chimique", "prob": 3, "grav": 5, "tz": True},
            {"desc": "Effondrement excavation conduite", "cat": "mecanique", "prob": 3, "grav": 5, "tz": True},
            {"desc": "Intoxication mercaptan (odorant)", "cat": "chimique", "prob": 3, "grav": 2},
            {"desc": "Brûlure soudure/brasage", "cat": "thermique", "prob": 3, "grav": 3},
            {"desc": "Accident véhicule intervention", "cat": "routier", "prob": 3, "grav": 4},
            {"desc": "Agression client (coupure service)", "cat": "violence", "prob": 3, "grav": 3},
        ],
        "zones": [
            {"nom": "Poste de détente gaz", "risk": "critique", "dangers": ["Explosion", "Incendie", "Bruit"], "epi": ["Détecteur gaz", "Vêtements ignifuges"]},
            {"nom": "Excavation conduite gaz", "risk": "critique", "dangers": ["Explosion", "Effondrement"], "epi": ["Détecteur gaz", "Casque", "Bottes"]},
            {"nom": "Chambre de vanne", "risk": "critique", "dangers": ["Espace clos", "Gaz"], "epi": ["Détecteur 4 gaz", "Ventilation"]},
            {"nom": "Résidence client (compteur)", "risk": "eleve", "dangers": ["Fuite gaz", "Agression"], "epi": ["Détecteur portatif"]},
        ],
        "roles": ["Technicien gaz", "Soudeur gaz", "Détecteur fuites", "Installateur compteurs", "Contremaître gaz", "Répartiteur urgence"],
        "certs": ["Énergir gaz naturel", "Espace clos", "SIMDUT", "Soudage gaz", "Info-Excavation", "Premiers soins"],
    },
    
    "221310": {
        "nom": "Réseaux d'aqueduc et systèmes d'irrigation",
        "description": "Usines filtration, réservoirs, distribution eau potable",
        "risques": [
            {"desc": "Noyade réservoir/bassin", "cat": "physique", "prob": 2, "grav": 5, "tz": True},
            {"desc": "Asphyxie espace clos réservoir", "cat": "chimique", "prob": 2, "grav": 5, "tz": True},
            {"desc": "Intoxication chlore gazeux", "cat": "chimique", "prob": 2, "grav": 5, "tz": True},
            {"desc": "Chute hauteur réservoir surélevé", "cat": "chute", "prob": 3, "grav": 5, "tz": True},
            {"desc": "Électrocution pompes/équipement", "cat": "electrique", "prob": 2, "grav": 5, "tz": True},
            {"desc": "Effondrement excavation conduite", "cat": "mecanique", "prob": 3, "grav": 5, "tz": True},
            {"desc": "Brûlure chimique (produits traitement)", "cat": "chimique", "prob": 3, "grav": 3},
            {"desc": "Bruit station pompage >90dB", "cat": "bruit", "prob": 5, "grav": 3},
        ],
        "zones": [
            {"nom": "Réservoir eau (intérieur)", "risk": "critique", "dangers": ["Noyade", "Espace clos", "Chute"], "epi": ["VFI", "Détecteur O2", "Harnais"]},
            {"nom": "Salle chloration", "risk": "critique", "dangers": ["Chlore gazeux", "Intoxication"], "epi": ["APRIA", "Douche urgence", "Détecteur Cl2"]},
            {"nom": "Station de pompage", "risk": "eleve", "dangers": ["Électrocution", "Bruit", "Noyade"], "epi": ["Bottes isolantes", "Protection auditive"]},
            {"nom": "Château d'eau (toit)", "risk": "critique", "dangers": ["Chute hauteur", "Espace clos"], "epi": ["Harnais", "Casque"]},
        ],
        "roles": ["Opérateur usine filtration", "Technicien chloration", "Mécanicien pompes", "Technicien réseau", "Contremaître aqueduc", "Chimiste eau"],
        "certs": ["OIQ/Eau potable", "Espace clos", "Chlore gazeux", "Cadenassage LOTO", "Premiers soins"],
    },
    
    "221320": {
        "nom": "Réseaux d'égout et installations d'assainissement",
        "description": "Usines épuration, stations pompage, collecteurs",
        "risques": [
            {"desc": "Asphyxie H2S/méthane égout", "cat": "chimique", "prob": 3, "grav": 5, "tz": True},
            {"desc": "Explosion méthane digesteur", "cat": "chimique", "prob": 2, "grav": 5, "tz": True},
            {"desc": "Noyade bassin/déversoir", "cat": "physique", "prob": 2, "grav": 5, "tz": True},
            {"desc": "Espace clos collecteur égout", "cat": "chimique", "prob": 3, "grav": 5, "tz": True},
            {"desc": "Pathogènes eaux usées", "cat": "biologique", "prob": 5, "grav": 3},
            {"desc": "Électrocution pompes submersibles", "cat": "electrique", "prob": 2, "grav": 5, "tz": True},
            {"desc": "Chute bassin décantation", "cat": "chute", "prob": 3, "grav": 4},
            {"desc": "Effondrement excavation conduite", "cat": "mecanique", "prob": 3, "grav": 5, "tz": True},
            {"desc": "Odeurs nauséabondes/stress", "cat": "chimique", "prob": 5, "grav": 2},
        ],
        "zones": [
            {"nom": "Collecteur principal (égout)", "risk": "critique", "dangers": ["H2S", "Méthane", "Noyade"], "epi": ["APRIA", "Détecteur 4 gaz", "VFI", "Tripode"]},
            {"nom": "Digesteur anaérobie", "risk": "critique", "dangers": ["Explosion méthane", "Asphyxie"], "epi": ["Détecteur CH4", "Vêtements antistatiques"]},
            {"nom": "Bassin aération/décantation", "risk": "eleve", "dangers": ["Noyade", "Pathogènes"], "epi": ["VFI", "Gants", "Masque"]},
            {"nom": "Station pompage égout", "risk": "critique", "dangers": ["H2S", "Électrocution", "Espace clos"], "epi": ["Détecteur gaz", "Ventilation"]},
        ],
        "roles": ["Opérateur station épuration", "Technicien égout", "Mécanicien pompes", "Laborantin eaux usées", "Contremaître assainissement", "Égoutier"],
        "certs": ["Espace clos avancé", "H2S/Méthane", "Sauvetage espace clos", "Cadenassage", "Premiers soins", "Vaccination hépatite"],
    },
}

# ORGANISATIONS DE SERVICES PUBLICS QUÉBÉCOISES
ORGANISATIONS_SCIAN_22 = [
    # Production hydroélectrique (221111)
    {"name": "Hydro-Québec Production", "sector": "221111", "nb": 4500, "region": "Montréal"},
    {"name": "Centrale Manic-5 (HQ)", "sector": "221111", "nb": 180, "region": "Côte-Nord"},
    {"name": "Centrale La Grande (HQ)", "sector": "221111", "nb": 220, "region": "Nord-du-Québec"},
    {"name": "Centrale Beauharnois (HQ)", "sector": "221111", "nb": 150, "region": "Montérégie"},
    {"name": "Rio Tinto Alcan - Énergie électrique", "sector": "221111", "nb": 280, "region": "Saguenay"},
    
    # Éolien/Solaire (221119)
    {"name": "Hydro-Québec Éolien", "sector": "221119", "nb": 180, "region": "Gaspésie"},
    {"name": "Boralex (parcs éoliens)", "sector": "221119", "nb": 320, "region": "Montréal"},
    {"name": "Kruger Énergie", "sector": "221119", "nb": 150, "region": "Montréal"},
    {"name": "Énergir Solaire", "sector": "221119", "nb": 80, "region": "Montréal"},
    {"name": "Innergex Renouvelable", "sector": "221119", "nb": 220, "region": "Longueuil"},
    
    # Distribution électricité (221121)
    {"name": "Hydro-Québec Distribution", "sector": "221121", "nb": 6500, "region": "Montréal"},
    {"name": "Hydro-Sherbrooke", "sector": "221121", "nb": 180, "region": "Sherbrooke"},
    {"name": "Hydro-Westmount", "sector": "221121", "nb": 45, "region": "Montréal"},
    {"name": "Électricité Joliette", "sector": "221121", "nb": 35, "region": "Lanaudière"},
    
    # Distribution gaz (221210)
    {"name": "Énergir (Gaz Métro)", "sector": "221210", "nb": 1500, "region": "Montréal"},
    {"name": "Gazifère", "sector": "221210", "nb": 120, "region": "Outaouais"},
    {"name": "Intragaz", "sector": "221210", "nb": 85, "region": "Mauricie"},
    
    # Aqueduc (221310)
    {"name": "Service de l'eau - Ville de Montréal", "sector": "221310", "nb": 850, "region": "Montréal"},
    {"name": "Service de l'eau - Ville de Québec", "sector": "221310", "nb": 420, "region": "Québec"},
    {"name": "Service de l'eau - Ville de Laval", "sector": "221310", "nb": 180, "region": "Laval"},
    {"name": "Régie eau Longueuil", "sector": "221310", "nb": 150, "region": "Montérégie"},
    
    # Égout/Assainissement (221320)
    {"name": "Station épuration Jean-R.-Marcotte (Montréal)", "sector": "221320", "nb": 450, "region": "Montréal"},
    {"name": "Station épuration Québec-Est", "sector": "221320", "nb": 180, "region": "Québec"},
    {"name": "Station épuration Laval", "sector": "221320", "nb": 120, "region": "Laval"},
    {"name": "SÉMER (Rimouski)", "sector": "221320", "nb": 85, "region": "Bas-Saint-Laurent"},
    {"name": "Régie assainissement eaux Châteauguay", "sector": "221320", "nb": 65, "region": "Montérégie"},
]

AGES = ["18-24", "25-34", "35-44", "45-54", "55-64"]


def populate_scian22():
    """Peuple SafetyGraph avec les secteurs SCIAN 22 (Services publics)"""
    
    print("=" * 70)
    print("⚡💧 POPULATION SAFETYGRAPH - SCIAN 22")
    print("    Services publics (Utilities)")
    print("    ⚡ INFRASTRUCTURES CRITIQUES QUÉBEC")
    print("    🔴 Hydro-Québec, Énergir, Services eau municipaux")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Secteurs: {len(SECTEURS_SCIAN_22)}")
    print(f"Organisations: {len(ORGANISATIONS_SCIAN_22)}")
    print("=" * 70)
    
    conn = SafetyGraphCartographyConnector()
    conn.connect()
    print("\n✅ Neo4j connecté")
    print(f"📊 Stats initiales: {conn.get_graph_stats()}\n")
    
    stats = {"orgs": 0, "zones": 0, "risks": 0, "persons": 0, "teams": 0, "roles": 0, "tz_risks": 0}
    
    # Créer organisations
    print("📦 Création des organisations SCIAN 22 (SERVICES PUBLICS)...")
    org_map = {}
    for o in ORGANISATIONS_SCIAN_22:
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
        data = SECTEURS_SCIAN_22[sector]
        
        # Emoji selon secteur
        if sector in ["221111", "221119", "221121"]:
            emoji = "⚡"
        elif sector == "221210":
            emoji = "🔥"
        else:
            emoji = "💧"
            
        print(f"\n   {emoji} {name[:40]}")
        print(f"      Secteur: {data['nom']}")
        
        # Rôles
        rids = []
        for r in data["roles"]:
            is_sup = any(x in r for x in ["Contremaître", "Surintendant", "Chef", "Superviseur", "Répartiteur"])
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
        
        # Équipes (services publics = quarts 24/7)
        tids = []
        if info["nb"] > 500:
            equipes = ["Équipe Jour", "Équipe Soir", "Équipe Nuit", "Équipe Urgence", "Équipe Entretien"]
        else:
            equipes = ["Équipe Exploitation", "Équipe Entretien"]
            
        for t in equipes:
            team = Team(name=t, department=data["nom"][:25])
            tid = conn.inject_team(team)
            tids.append(tid)
            conn.create_relation(tid, oid, RelationType.APPARTIENT_A)
            stats["teams"] += 1
        print(f"      • {len(tids)} équipes")
        
        # Personnes
        nb_persons = max(5, min(info["nb"] // 100, 30))
        for i in range(nb_persons):
            p = Person(
                matricule=f"UTIL22-{sector[-3:]}-{stats['persons']+1:04d}",
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
            if rkids and i % 10 < 8:
                conn.create_relation(pid, rkids[i % len(rkids)], RelationType.EXPOSE_A)
        
        print(f"      • {nb_persons} personnes (anonymisées Loi 25)")
    
    # Résumé
    print("\n" + "=" * 70)
    print("📊 RÉSUMÉ POPULATION SCIAN 22 - SERVICES PUBLICS")
    print("   ⚡ INFRASTRUCTURES CRITIQUES QUÉBEC")
    print("=" * 70)
    print(f"   Organisations services publics: {stats['orgs']}")
    print(f"   Zones de travail: {stats['zones']}")
    print(f"   Risques identifiés: {stats['risks']}")
    print(f"   🔴 Risques Tolérance Zéro: {stats['tz_risks']}")
    print(f"   Équipes: {stats['teams']}")
    print(f"   Rôles/Professions: {stats['roles']}")
    print(f"   Personnes: {stats['persons']}")
    print(f"\n   Neo4j final: {conn.get_graph_stats()}")
    print("=" * 70)
    print("✅ POPULATION SCIAN 22 (SERVICES PUBLICS) TERMINÉE!")
    print("=" * 70)
    
    conn.close()
    return stats


if __name__ == "__main__":
    populate_scian22()
