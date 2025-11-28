#!/usr/bin/env python3
"""
🛡️ Script de Population Neo4j - Secteurs SCIAN 72
Hébergement et services de restauration
EDGY-AgenticX5 | SafetyGraph | Preventera

🍽️ 5e SECTEUR PRIORITAIRE CNESST - ~15,000 lésions/an
   Hôtels, restaurants, services alimentaires
   TMS, brûlures, coupures, glissades, violence

Secteurs inclus:
- 721110: Hôtels (sauf les hôtels-casinos)
- 721120: Hôtels-casinos
- 721191: Gîtes touristiques (B&B)
- 721310: Parcs pour véhicules récréatifs et campings
- 722511: Restaurants à service complet
- 722512: Établissements de restauration à service restreint
- 722310: Services de restauration contractuels
- 722320: Traiteurs
- 722410: Bars et tavernes

Risques principaux CNESST:
- TMS (troubles musculosquelettiques)
- Brûlures (cuisine, friteuses, four)
- Coupures (couteaux, trancheurs)
- Glissades/chutes plancher mouillé
- Violence clientèle
"""

import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

from src.cartography.connector import SafetyGraphCartographyConnector
from src.cartography.models import Organization, Person, Team, Role, Zone, Risk, RiskLevel, RelationType

# ============================================================================
# DONNÉES CNESST - SECTEURS SCIAN 72 (HÉBERGEMENT/RESTAURATION)
# 5e SECTEUR PRIORITAIRE - ~15,000 LÉSIONS/AN
# ============================================================================

SECTEURS_SCIAN_72 = {
    "721110": {
        "nom": "Hôtels (sauf hôtels-casinos)",
        "description": "Hôtels, motels, auberges",
        "risques": [
            {"desc": "TMS - ménage répétitif (lits, aspirateur)", "cat": "ergonomique", "prob": 5, "grav": 3},
            {"desc": "Glissade plancher mouillé (salle de bain)", "cat": "chute", "prob": 4, "grav": 3},
            {"desc": "Chute escalier/marches", "cat": "chute", "prob": 3, "grav": 4},
            {"desc": "Violence/agression client", "cat": "violence", "prob": 3, "grav": 4},
            {"desc": "Exposition produits chimiques nettoyage", "cat": "chimique", "prob": 4, "grav": 2},
            {"desc": "Piqûre aiguille (seringue chambre)", "cat": "biologique", "prob": 2, "grav": 4},
            {"desc": "Brûlure buanderie (vapeur, repassage)", "cat": "thermique", "prob": 3, "grav": 3},
            {"desc": "Stress/harcèlement psychologique", "cat": "psychosocial", "prob": 4, "grav": 3},
        ],
        "zones": [
            {"nom": "Chambres (ménage)", "risk": "moyen", "dangers": ["TMS", "Chimique", "Piqûre"], "epi": ["Gants", "Chaussures fermées"]},
            {"nom": "Buanderie", "risk": "eleve", "dangers": ["Brûlure vapeur", "TMS", "Bruit"], "epi": ["Gants chaleur", "Protection auditive"]},
            {"nom": "Réception/Lobby", "risk": "moyen", "dangers": ["Violence client", "TMS bureau"], "epi": []},
            {"nom": "Cuisine hôtel", "risk": "eleve", "dangers": ["Brûlure", "Coupure", "Glissade"], "epi": ["Tablier", "Chaussures antidérapantes"]},
        ],
        "roles": ["Préposé aux chambres", "Femme/Homme de chambre", "Réceptionniste", "Concierge", "Buandier", "Chef cuisine hôtel", "Directeur hébergement"],
        "certs": ["SIMDUT", "Premiers soins", "RCR", "Hygiène salubrité"],
    },
    
    "722511": {
        "nom": "Restaurants à service complet",
        "description": "Restaurants avec service aux tables",
        "risques": [
            {"desc": "Brûlure four/plaque chauffante", "cat": "thermique", "prob": 4, "grav": 4},
            {"desc": "Brûlure huile friteuse", "cat": "thermique", "prob": 3, "grav": 5},
            {"desc": "Coupure couteau/trancheur", "cat": "mecanique", "prob": 4, "grav": 4},
            {"desc": "Glissade plancher cuisine gras", "cat": "chute", "prob": 5, "grav": 3},
            {"desc": "TMS - station debout prolongée", "cat": "ergonomique", "prob": 5, "grav": 3},
            {"desc": "TMS - transport plateaux lourds", "cat": "ergonomique", "prob": 4, "grav": 3},
            {"desc": "Violence/harcèlement client", "cat": "violence", "prob": 3, "grav": 3},
            {"desc": "Brûlure vapeur/liquide chaud", "cat": "thermique", "prob": 4, "grav": 3},
            {"desc": "Stress/pression rush service", "cat": "psychosocial", "prob": 5, "grav": 2},
        ],
        "zones": [
            {"nom": "Cuisine chaude", "risk": "critique", "dangers": ["Brûlure", "Coupure", "Glissade", "Chaleur"], "epi": ["Tablier", "Chaussures antidérapantes", "Gants chaleur"]},
            {"nom": "Zone friteuses", "risk": "critique", "dangers": ["Brûlure huile 180°C", "Incendie"], "epi": ["Gants longs", "Tablier ignifuge", "Extincteur"]},
            {"nom": "Salle à manger", "risk": "moyen", "dangers": ["Glissade", "TMS", "Violence"], "epi": ["Chaussures antidérapantes"]},
            {"nom": "Plonge/Lavage", "risk": "eleve", "dangers": ["Coupure", "Chimique", "TMS"], "epi": ["Gants", "Tablier imperméable"]},
        ],
        "roles": ["Chef cuisinier", "Cuisinier", "Aide-cuisinier", "Serveur/Serveuse", "Barman", "Plongeur", "Gérant restaurant"],
        "certs": ["Hygiène salubrité MAPAQ", "SIMDUT", "Premiers soins", "Service alcool"],
    },
    
    "722512": {
        "nom": "Établissements de restauration à service restreint",
        "description": "Restauration rapide, comptoir, livraison",
        "risques": [
            {"desc": "Brûlure friteuse/grill", "cat": "thermique", "prob": 4, "grav": 4},
            {"desc": "Brûlure liquide chaud (café, soupe)", "cat": "thermique", "prob": 4, "grav": 3},
            {"desc": "Glissade plancher mouillé/gras", "cat": "chute", "prob": 5, "grav": 3},
            {"desc": "Coupure trancheur/couteau", "cat": "mecanique", "prob": 3, "grav": 4},
            {"desc": "TMS - cadence rapide répétitive", "cat": "ergonomique", "prob": 5, "grav": 3},
            {"desc": "Violence/vol à main armée", "cat": "violence", "prob": 2, "grav": 5},
            {"desc": "Agression client mécontent", "cat": "violence", "prob": 4, "grav": 3},
            {"desc": "Accident livraison (vélo, auto)", "cat": "routier", "prob": 3, "grav": 4},
            {"desc": "Stress/pression service rapide", "cat": "psychosocial", "prob": 5, "grav": 2},
        ],
        "zones": [
            {"nom": "Cuisine fast-food", "risk": "critique", "dangers": ["Brûlure", "Glissade", "Cadence"], "epi": ["Tablier", "Chaussures antidérapantes"]},
            {"nom": "Zone friteuse/grill", "risk": "critique", "dangers": ["Brûlure huile", "Incendie"], "epi": ["Gants chaleur", "Extincteur proche"]},
            {"nom": "Comptoir service", "risk": "moyen", "dangers": ["Violence", "TMS"], "epi": []},
            {"nom": "Service au volant", "risk": "moyen", "dangers": ["Intempéries", "Violence"], "epi": []},
        ],
        "roles": ["Équipier polyvalent", "Cuisinier fast-food", "Caissier", "Livreur", "Chef d'équipe", "Gérant"],
        "certs": ["Hygiène salubrité MAPAQ", "SIMDUT", "Premiers soins"],
    },
    
    "722310": {
        "nom": "Services de restauration contractuels",
        "description": "Cafétérias institutions, services alimentaires",
        "risques": [
            {"desc": "Brûlure équipement cuisine collective", "cat": "thermique", "prob": 4, "grav": 4},
            {"desc": "TMS - préparation gros volumes", "cat": "ergonomique", "prob": 5, "grav": 3},
            {"desc": "Glissade plancher cuisine", "cat": "chute", "prob": 4, "grav": 3},
            {"desc": "Coupure équipement industriel", "cat": "mecanique", "prob": 3, "grav": 4},
            {"desc": "Coincement équipement (mélangeur)", "cat": "mecanique", "prob": 2, "grav": 5},
            {"desc": "Exposition produits allergènes", "cat": "biologique", "prob": 3, "grav": 3},
            {"desc": "Bruit cuisine collective >85dB", "cat": "bruit", "prob": 4, "grav": 3},
        ],
        "zones": [
            {"nom": "Cuisine centrale production", "risk": "critique", "dangers": ["Brûlure", "Coupure", "Coincement"], "epi": ["Tablier", "Gants", "Résille cheveux"]},
            {"nom": "Zone équipement lourd", "risk": "eleve", "dangers": ["Coincement", "Bruit"], "epi": ["Protection auditive", "Gants"]},
            {"nom": "Cafétéria service", "risk": "moyen", "dangers": ["Glissade", "TMS"], "epi": ["Chaussures antidérapantes"]},
            {"nom": "Réception marchandises", "risk": "eleve", "dangers": ["TMS", "Froid"], "epi": ["Gants", "Veste"]},
        ],
        "roles": ["Chef production", "Cuisinier collectivité", "Aide alimentaire", "Préposé cafétéria", "Magasinier", "Directeur services alimentaires"],
        "certs": ["Hygiène salubrité MAPAQ", "SIMDUT", "Cadenassage", "Premiers soins"],
    },
    
    "722320": {
        "nom": "Traiteurs",
        "description": "Services traiteur, événements, banquets",
        "risques": [
            {"desc": "Brûlure équipement mobile", "cat": "thermique", "prob": 4, "grav": 3},
            {"desc": "TMS - transport équipement lourd", "cat": "ergonomique", "prob": 5, "grav": 3},
            {"desc": "Accident véhicule livraison", "cat": "routier", "prob": 3, "grav": 4},
            {"desc": "Glissade site événement", "cat": "chute", "prob": 3, "grav": 3},
            {"desc": "Coupure préparation", "cat": "mecanique", "prob": 4, "grav": 3},
            {"desc": "Stress événements/délais", "cat": "psychosocial", "prob": 5, "grav": 2},
            {"desc": "Fatigue horaires atypiques", "cat": "psychosocial", "prob": 5, "grav": 3},
        ],
        "zones": [
            {"nom": "Cuisine traiteur", "risk": "eleve", "dangers": ["Brûlure", "Coupure", "Cadence"], "epi": ["Tablier", "Chaussures antidérapantes"]},
            {"nom": "Véhicule livraison", "risk": "eleve", "dangers": ["Accident routier", "TMS"], "epi": ["Ceinture", "Chaussures"]},
            {"nom": "Site événement", "risk": "moyen", "dangers": ["Glissade", "TMS", "Électrique"], "epi": ["Chaussures fermées"]},
        ],
        "roles": ["Chef traiteur", "Cuisinier événementiel", "Serveur banquet", "Livreur", "Coordonnateur événements"],
        "certs": ["Hygiène salubrité MAPAQ", "Permis conduire", "SIMDUT", "Premiers soins"],
    },
    
    "722410": {
        "nom": "Bars et tavernes",
        "description": "Bars, pubs, discothèques, tavernes",
        "risques": [
            {"desc": "Violence/agression client intoxiqué", "cat": "violence", "prob": 4, "grav": 4},
            {"desc": "Vol à main armée", "cat": "violence", "prob": 2, "grav": 5},
            {"desc": "Glissade plancher mouillé/alcool", "cat": "chute", "prob": 4, "grav": 3},
            {"desc": "Coupure verre brisé", "cat": "mecanique", "prob": 4, "grav": 3},
            {"desc": "TMS - station debout prolongée", "cat": "ergonomique", "prob": 5, "grav": 3},
            {"desc": "Bruit discothèque >100dB", "cat": "bruit", "prob": 5, "grav": 4},
            {"desc": "Harcèlement sexuel", "cat": "psychosocial", "prob": 3, "grav": 4},
            {"desc": "Fatigue travail nuit", "cat": "psychosocial", "prob": 5, "grav": 3},
        ],
        "zones": [
            {"nom": "Bar/Comptoir", "risk": "eleve", "dangers": ["Violence", "Coupure verre", "TMS"], "epi": ["Chaussures fermées"]},
            {"nom": "Salle discothèque", "risk": "eleve", "dangers": ["Bruit", "Violence", "Glissade"], "epi": ["Bouchons discrets"]},
            {"nom": "Entrée/Vestiaire", "risk": "eleve", "dangers": ["Violence", "Vol"], "epi": []},
            {"nom": "Stationnement", "risk": "eleve", "dangers": ["Violence", "Accident"], "epi": ["Lampe", "Radio"]},
        ],
        "roles": ["Barman/Barmaid", "Serveur bar", "Portier/Agent sécurité", "DJ", "Gérant bar"],
        "certs": ["Service alcool RBQ", "Premiers soins", "Intervention crise", "RCR"],
    },
}

# ORGANISATIONS HÉBERGEMENT/RESTAURATION QUÉBÉCOISES
ORGANISATIONS_SCIAN_72 = [
    # Hôtels (721110)
    {"name": "Fairmont Le Château Frontenac", "sector": "721110", "nb": 650, "region": "Québec"},
    {"name": "Fairmont Reine Elizabeth", "sector": "721110", "nb": 580, "region": "Montréal"},
    {"name": "Marriott Montréal", "sector": "721110", "nb": 320, "region": "Montréal"},
    {"name": "Hilton Québec", "sector": "721110", "nb": 280, "region": "Québec"},
    {"name": "Delta Hotels (Marriott)", "sector": "721110", "nb": 450, "region": "Montréal"},
    {"name": "Groupe Germain Hôtels", "sector": "721110", "nb": 380, "region": "Québec"},
    {"name": "Hôtel & Spa Le Germain", "sector": "721110", "nb": 120, "region": "Montréal"},
    
    # Restaurants service complet (722511)
    {"name": "Groupe Sportscene (La Cage)", "sector": "722511", "nb": 850, "region": "Montréal"},
    {"name": "St-Hubert (Groupe MTY)", "sector": "722511", "nb": 1200, "region": "Montréal"},
    {"name": "Pacini (Imvescor)", "sector": "722511", "nb": 380, "region": "Montréal"},
    {"name": "Scores Rotisserie", "sector": "722511", "nb": 280, "region": "Montréal"},
    {"name": "Bâton Rouge", "sector": "722511", "nb": 320, "region": "Montréal"},
    
    # Restauration rapide (722512)
    {"name": "Tim Hortons Québec (RBI)", "sector": "722512", "nb": 4500, "region": "Montréal"},
    {"name": "McDonald's Québec", "sector": "722512", "nb": 3800, "region": "Montréal"},
    {"name": "Subway Québec", "sector": "722512", "nb": 1500, "region": "Montréal"},
    {"name": "A&W Québec", "sector": "722512", "nb": 850, "region": "Montréal"},
    {"name": "Groupe MTY (Valentine, Thai Express)", "sector": "722512", "nb": 2200, "region": "Montréal"},
    {"name": "Couche-Tard (services alimentaires)", "sector": "722512", "nb": 1800, "region": "Laval"},
    {"name": "Harvey's/Swiss Chalet Québec", "sector": "722512", "nb": 650, "region": "Montréal"},
    
    # Services alimentaires contractuels (722310)
    {"name": "Compass Group Canada (Chartwells)", "sector": "722310", "nb": 2500, "region": "Montréal"},
    {"name": "Sodexo Québec", "sector": "722310", "nb": 1800, "region": "Montréal"},
    {"name": "Aramark Québec", "sector": "722310", "nb": 1200, "region": "Montréal"},
    {"name": "Services alimentaires SHSE (hôpitaux)", "sector": "722310", "nb": 850, "region": "Québec"},
    
    # Traiteurs (722320)
    {"name": "Groupe Agnus Dei Traiteur", "sector": "722320", "nb": 280, "region": "Montréal"},
    {"name": "La Queue de Cochon Traiteur", "sector": "722320", "nb": 150, "region": "Montréal"},
    {"name": "Traiteur Nourcy", "sector": "722320", "nb": 120, "region": "Montréal"},
    
    # Bars (722410)
    {"name": "Groupe Arcade (bars Montréal)", "sector": "722410", "nb": 280, "region": "Montréal"},
    {"name": "New City Gas", "sector": "722410", "nb": 150, "region": "Montréal"},
    {"name": "Distillerie de Montréal (bar)", "sector": "722410", "nb": 85, "region": "Montréal"},
]

AGES = ["18-24", "25-34", "35-44", "45-54", "55-64"]


def populate_scian72():
    """Peuple SafetyGraph avec les secteurs SCIAN 72 (Hébergement/Restauration)"""
    
    print("=" * 70)
    print("🍽️🏨 POPULATION SAFETYGRAPH - SCIAN 72")
    print("    Hébergement et services de restauration")
    print("    🍽️ 5e SECTEUR PRIORITAIRE CNESST")
    print("    ~15,000 lésions/an (TMS, brûlures, coupures)")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Secteurs: {len(SECTEURS_SCIAN_72)}")
    print(f"Organisations: {len(ORGANISATIONS_SCIAN_72)}")
    print("=" * 70)
    
    conn = SafetyGraphCartographyConnector()
    conn.connect()
    print("\n✅ Neo4j connecté")
    print(f"📊 Stats initiales: {conn.get_graph_stats()}\n")
    
    stats = {"orgs": 0, "zones": 0, "risks": 0, "persons": 0, "teams": 0, "roles": 0}
    
    # Créer organisations
    print("📦 Création des organisations SCIAN 72 (HÉBERGEMENT/RESTAURATION)...")
    org_map = {}
    for o in ORGANISATIONS_SCIAN_72:
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
        data = SECTEURS_SCIAN_72[sector]
        
        # Emoji selon secteur
        emoji = "🏨" if sector.startswith("721") else "🍺" if sector == "722410" else "🍽️"
            
        print(f"\n   {emoji} {name[:40]}")
        print(f"      Secteur: {data['nom']}")
        
        # Rôles
        rids = []
        for r in data["roles"]:
            is_sup = any(x in r for x in ["Chef", "Gérant", "Directeur", "Coordonnateur"])
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
        
        # Équipes (restauration = quarts multiples)
        tids = []
        if info["nb"] > 500:
            equipes = ["Équipe Matin", "Équipe Jour", "Équipe Soir", "Équipe Fin semaine"]
        else:
            equipes = ["Équipe Jour", "Équipe Soir"]
            
        for t in equipes:
            team = Team(name=t, department=data["nom"][:25])
            tid = conn.inject_team(team)
            tids.append(tid)
            conn.create_relation(tid, oid, RelationType.APPARTIENT_A)
            stats["teams"] += 1
        print(f"      • {len(tids)} équipes")
        
        # Personnes (secteur avec beaucoup de jeunes travailleurs)
        nb_persons = max(5, min(info["nb"] // 80, 35))
        for i in range(nb_persons):
            # Surreprésentation 18-24 ans dans ce secteur
            age_dist = ["18-24", "18-24", "25-34", "25-34", "35-44"]
            p = Person(
                matricule=f"REST72-{sector[-3:]}-{stats['persons']+1:04d}",
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
            if rkids and i % 10 < 8:
                conn.create_relation(pid, rkids[i % len(rkids)], RelationType.EXPOSE_A)
        
        print(f"      • {nb_persons} personnes (anonymisées Loi 25)")
    
    # Résumé
    print("\n" + "=" * 70)
    print("📊 RÉSUMÉ POPULATION SCIAN 72 - HÉBERGEMENT/RESTAURATION")
    print("   🍽️ 5e SECTEUR PRIORITAIRE CNESST")
    print("=" * 70)
    print(f"   Organisations hébergement/resto: {stats['orgs']}")
    print(f"   Zones de travail: {stats['zones']}")
    print(f"   Risques identifiés: {stats['risks']}")
    print(f"   Équipes: {stats['teams']}")
    print(f"   Rôles/Professions: {stats['roles']}")
    print(f"   Personnes: {stats['persons']}")
    print(f"\n   Neo4j final: {conn.get_graph_stats()}")
    print("=" * 70)
    print("✅ POPULATION SCIAN 72 (HÉBERGEMENT/RESTAURATION) TERMINÉE!")
    print("=" * 70)
    
    conn.close()
    return stats


if __name__ == "__main__":
    populate_scian72()
