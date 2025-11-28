#!/usr/bin/env python3
"""
🛡️ Script de Population Neo4j - Secteurs SCIAN 91
Administrations publiques
EDGY-AgenticX5 | SafetyGraph | Preventera

Basé sur les données CNESST:
- Services de sécurité incendie (610 SSI au Québec)
- Services de police
- Travaux publics municipaux
- Services correctionnels

Secteurs inclus:
- 91121: Services de police municipaux
- 91122: Services de protection contre les incendies
- 91131: Travaux publics et voirie
- 91140: Services correctionnels
- 91190: Autres administrations publiques locales
"""

import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

from src.cartography.connector import SafetyGraphCartographyConnector
from src.cartography.models import Organization, Person, Team, Role, Zone, Risk, RiskLevel, RelationType

# ============================================================================
# DONNÉES CNESST - SECTEURS SCIAN 91 (ADMINISTRATIONS PUBLIQUES)
# 610 Services de sécurité incendie municipaux au Québec (2024)
# ============================================================================

SECTEURS_SCIAN_91 = {
    "911220": {
        "nom": "Services de protection contre les incendies",
        "description": "Services incendie municipaux, pompiers",
        "risques": [
            {"desc": "Effondrement structure en feu", "cat": "mecanique", "prob": 2, "grav": 5},
            {"desc": "Brûlures thermiques/flammes", "cat": "thermique", "prob": 3, "grav": 5},
            {"desc": "Inhalation fumée/gaz toxiques", "cat": "chimique", "prob": 4, "grav": 5},
            {"desc": "Chute hauteur (échelle, toit)", "cat": "chute", "prob": 3, "grav": 5},
            {"desc": "Électrocution (fils tombés)", "cat": "electrique", "prob": 2, "grav": 5},
            {"desc": "Accident véhicule urgence", "cat": "routier", "prob": 3, "grav": 5},
            {"desc": "Épuisement thermique/coup de chaleur", "cat": "thermique", "prob": 4, "grav": 4},
            {"desc": "Stress post-traumatique (TSPT)", "cat": "psychosocial", "prob": 4, "grav": 4},
            {"desc": "Cancer professionnel (exposition suie)", "cat": "chimique", "prob": 3, "grav": 5},
            {"desc": "Noyade intervention inondation", "cat": "noyade", "prob": 2, "grav": 5},
            {"desc": "TMS - port équipement lourd", "cat": "ergonomique", "prob": 4, "grav": 3},
            {"desc": "Blessure sauvetage victime", "cat": "ergonomique", "prob": 3, "grav": 4},
        ],
        "zones": [
            {"nom": "Scène d'incendie", "risk": "critique", "dangers": ["Feu", "Effondrement", "Fumée", "Électricité"], "epi": ["Habit bunker", "APRIA", "Casque", "Gants"]},
            {"nom": "Véhicule autopompe", "risk": "eleve", "dangers": ["Routier", "Équipement"], "epi": ["Ceinture", "Casque"]},
            {"nom": "Échelle aérienne", "risk": "critique", "dangers": ["Chute", "Électricité", "Vent"], "epi": ["Harnais", "Casque", "Gants"]},
            {"nom": "Caserne", "risk": "moyen", "dangers": ["Équipement", "Véhicules"], "epi": ["Uniforme", "Bottes"]},
            {"nom": "Zone inondation/eau", "risk": "critique", "dangers": ["Noyade", "Courant", "Froid"], "epi": ["VFI", "Combinaison sèche", "Casque eau vive"]},
        ],
        "roles": ["Pompier", "Lieutenant pompier", "Capitaine", "Chef aux opérations", "Directeur incendie", "Pompier préventionniste", "Technicien véhicule"],
        "certs": ["Pompier I/II", "Officier I/II", "APRIA", "Conduite urgence", "Sauvetage technique", "Matières dangereuses", "RCR/DEA", "Premiers répondants"],
    },
    
    "911210": {
        "nom": "Services de police",
        "description": "Corps policiers municipaux, SQ",
        "risques": [
            {"desc": "Agression/violence intervention", "cat": "violence", "prob": 4, "grav": 5},
            {"desc": "Blessure par arme à feu", "cat": "violence", "prob": 2, "grav": 5},
            {"desc": "Blessure arme blanche", "cat": "violence", "prob": 3, "grav": 5},
            {"desc": "Accident véhicule poursuite", "cat": "routier", "prob": 3, "grav": 5},
            {"desc": "Stress post-traumatique (TSPT)", "cat": "psychosocial", "prob": 4, "grav": 4},
            {"desc": "Exposition sang/liquides (arrestation)", "cat": "biologique", "prob": 3, "grav": 4},
            {"desc": "Morsure chien (intervention)", "cat": "biologique", "prob": 3, "grav": 3},
            {"desc": "TMS - ceinturon équipement lourd", "cat": "ergonomique", "prob": 4, "grav": 3},
            {"desc": "Exposition drogues (fentanyl)", "cat": "chimique", "prob": 3, "grav": 5},
            {"desc": "Fatigue/épuisement quarts irréguliers", "cat": "psychosocial", "prob": 4, "grav": 3},
        ],
        "zones": [
            {"nom": "Scène d'intervention", "risk": "critique", "dangers": ["Violence", "Armes", "Imprévisible"], "epi": ["Gilet pare-balles", "Arme service", "Radio"]},
            {"nom": "Véhicule patrouille", "risk": "eleve", "dangers": ["Routier", "Poursuite"], "epi": ["Ceinture", "Équipement complet"]},
            {"nom": "Poste de police", "risk": "moyen", "dangers": ["Violence détenu", "Ergonomie"], "epi": ["Uniforme", "Équipement"]},
            {"nom": "Cellule/détention", "risk": "eleve", "dangers": ["Violence", "Biologique"], "epi": ["Gants", "Formation contrôle"]},
        ],
        "roles": ["Agent patrouilleur", "Sergent", "Lieutenant-détective", "Capitaine", "Inspecteur", "Directeur police", "Agent communautaire", "Répartiteur 911"],
        "certs": ["ENPQ", "Arme à feu", "Conduite urgence", "Contrôle physique", "RCR", "Enquête", "Gestion de crise"],
    },
    
    "911310": {
        "nom": "Travaux publics municipaux",
        "description": "Voirie, aqueduc, égouts, parcs",
        "risques": [
            {"desc": "Frappé par véhicule (travail routier)", "cat": "routier", "prob": 4, "grav": 5},
            {"desc": "Asphyxie espace clos (égout, puits)", "cat": "chimique", "prob": 2, "grav": 5},
            {"desc": "Écrasement excavation (effondrement)", "cat": "mecanique", "prob": 2, "grav": 5},
            {"desc": "Électrocution (éclairage public)", "cat": "electrique", "prob": 2, "grav": 5},
            {"desc": "Engelures/hypothermie (déneigement)", "cat": "thermique", "prob": 4, "grav": 4},
            {"desc": "TMS - travail physique répétitif", "cat": "ergonomique", "prob": 5, "grav": 3},
            {"desc": "Bruit équipements >85dB", "cat": "bruit", "prob": 5, "grav": 3},
            {"desc": "Exposition asphalte chaud", "cat": "chimique", "prob": 3, "grav": 3},
            {"desc": "Piqûre insectes (parcs)", "cat": "biologique", "prob": 3, "grav": 2},
            {"desc": "Renversement équipement lourd", "cat": "mecanique", "prob": 2, "grav": 5},
        ],
        "zones": [
            {"nom": "Chantier routier", "risk": "critique", "dangers": ["Circulation", "Équipement"], "epi": ["Dossard classe 3", "Casque", "Bottes"]},
            {"nom": "Égout/regard d'égout", "risk": "critique", "dangers": ["Gaz", "Noyade", "Espace clos"], "epi": ["Détecteur 4 gaz", "Harnais", "Trépied"]},
            {"nom": "Atelier municipal", "risk": "eleve", "dangers": ["Machines", "Bruit"], "epi": ["Lunettes", "Bouchons", "Gants"]},
            {"nom": "Parc municipal", "risk": "moyen", "dangers": ["Outils", "Insectes"], "epi": ["Gants", "Chaussures sécurité"]},
            {"nom": "Rue/trottoir déneigement", "risk": "eleve", "dangers": ["Froid", "Circulation", "Glace"], "epi": ["Vêtements chauds", "Dossard", "Crampons"]},
        ],
        "roles": ["Col bleu/Journalier", "Opérateur équipement lourd", "Électricien municipal", "Plombier municipal", "Contremaître", "Chef de division", "Directeur travaux publics"],
        "certs": ["Signalisation routière", "Espace clos", "Équipement lourd", "SIMDUT", "Électricité", "Premiers soins"],
    },
    
    "911400": {
        "nom": "Services correctionnels",
        "description": "Établissements de détention provinciaux",
        "risques": [
            {"desc": "Agression détenu", "cat": "violence", "prob": 4, "grav": 4},
            {"desc": "Blessure arme improvisée", "cat": "violence", "prob": 3, "grav": 4},
            {"desc": "Prise d'otage", "cat": "violence", "prob": 2, "grav": 5},
            {"desc": "Exposition agents biologiques", "cat": "biologique", "prob": 3, "grav": 4},
            {"desc": "Stress chronique/épuisement", "cat": "psychosocial", "prob": 5, "grav": 4},
            {"desc": "Exposition drogues (fentanyl clandestin)", "cat": "chimique", "prob": 3, "grav": 5},
            {"desc": "Émeute/mouvement de masse", "cat": "violence", "prob": 2, "grav": 5},
            {"desc": "TMS - interventions physiques", "cat": "ergonomique", "prob": 4, "grav": 3},
        ],
        "zones": [
            {"nom": "Aile de détention", "risk": "critique", "dangers": ["Violence", "Arme improvisée"], "epi": ["Radio", "Menottes", "Formation intervention"]},
            {"nom": "Cour extérieure", "risk": "eleve", "dangers": ["Violence", "Évasion"], "epi": ["Radio", "Équipement intervention"]},
            {"nom": "Poste de contrôle", "risk": "moyen", "dangers": ["Ergonomie", "Stress"], "epi": ["Radio", "Équipement"]},
            {"nom": "Unité d'isolement", "risk": "critique", "dangers": ["Violence extrême", "Santé mentale"], "epi": ["Équipement intervention complète"]},
        ],
        "roles": ["Agent services correctionnels", "Sergent correctionnel", "Gestionnaire d'unité", "Agent de libération", "Directeur établissement", "Intervenant psychosocial"],
        "certs": ["ENPQ correctionnel", "Intervention physique", "Gestion de crise", "RCR", "Premiers soins", "Suicide/automutilation"],
    },
    
    "911190": {
        "nom": "Administration municipale générale",
        "description": "Hôtels de ville, services administratifs",
        "risques": [
            {"desc": "TMS - travail bureau prolongé", "cat": "ergonomique", "prob": 4, "grav": 3},
            {"desc": "Violence citoyen mécontent", "cat": "violence", "prob": 3, "grav": 3},
            {"desc": "Stress/surcharge de travail", "cat": "psychosocial", "prob": 4, "grav": 3},
            {"desc": "Chute escalier/plancher", "cat": "chute", "prob": 3, "grav": 3},
            {"desc": "Accident véhicule municipal", "cat": "routier", "prob": 2, "grav": 4},
        ],
        "zones": [
            {"nom": "Comptoir service aux citoyens", "risk": "eleve", "dangers": ["Violence verbale", "Agression"], "epi": ["Protocole", "Alarme"]},
            {"nom": "Bureau administratif", "risk": "moyen", "dangers": ["Ergonomie", "Stress"], "epi": ["Mobilier ergonomique"]},
            {"nom": "Salle du conseil", "risk": "moyen", "dangers": ["Violence", "Foule"], "epi": ["Sécurité présente"]},
        ],
        "roles": ["Commis administratif", "Agent service citoyens", "Greffier", "Directeur général", "Trésorier", "Urbaniste", "Inspecteur municipal"],
        "certs": ["Gestion stress", "Service clientèle difficile", "Premiers soins", "Ergonomie bureau"],
    },
    
    "912910": {
        "nom": "Services paramédicaux (ambulanciers)",
        "description": "Services ambulanciers, premiers répondants",
        "risques": [
            {"desc": "Violence patient/famille", "cat": "violence", "prob": 4, "grav": 4},
            {"desc": "Piqûre aiguille", "cat": "biologique", "prob": 3, "grav": 4},
            {"desc": "Exposition agents infectieux", "cat": "biologique", "prob": 4, "grav": 4},
            {"desc": "TMS - levage/transport patient", "cat": "ergonomique", "prob": 5, "grav": 4},
            {"desc": "Accident véhicule urgence", "cat": "routier", "prob": 3, "grav": 5},
            {"desc": "Stress post-traumatique (TSPT)", "cat": "psychosocial", "prob": 4, "grav": 4},
            {"desc": "Fatigue quarts 12-16h", "cat": "psychosocial", "prob": 5, "grav": 4},
            {"desc": "Exposition drogues (fentanyl scène)", "cat": "chimique", "prob": 3, "grav": 5},
        ],
        "zones": [
            {"nom": "Scène d'intervention", "risk": "critique", "dangers": ["Violence", "Biologique", "Imprévisible"], "epi": ["Gants", "Masque", "Lunettes", "Dossard"]},
            {"nom": "Ambulance", "risk": "eleve", "dangers": ["Routier", "TMS", "Biologique"], "epi": ["Gants", "Équipement complet"]},
            {"nom": "Caserne ambulancière", "risk": "moyen", "dangers": ["Fatigue", "Équipement"], "epi": ["Uniforme"]},
        ],
        "roles": ["Paramédic soins primaires", "Paramédic soins avancés", "Chef de service", "Répartiteur 911", "Directeur médical"],
        "certs": ["DEP Ambulancier", "Soins avancés", "RCR/DEA", "PHTLS", "Conduite urgence", "Gestion stress"],
    },
}

# ORGANISATIONS PUBLIQUES QUÉBÉCOISES À CRÉER
ORGANISATIONS_SCIAN_91 = [
    # Services incendie (911220)
    {"name": "Service incendie Ville de Montréal (SIM)", "sector": "911220", "nb": 2800, "region": "Montréal"},
    {"name": "Service incendie Ville de Québec", "sector": "911220", "nb": 680, "region": "Québec"},
    {"name": "Service incendie Ville de Laval", "sector": "911220", "nb": 420, "region": "Laval"},
    {"name": "Service incendie Longueuil", "sector": "911220", "nb": 380, "region": "Montérégie"},
    {"name": "Service incendie Gatineau", "sector": "911220", "nb": 350, "region": "Outaouais"},
    {"name": "Service incendie Sherbrooke", "sector": "911220", "nb": 180, "region": "Estrie"},
    {"name": "Service incendie Trois-Rivières", "sector": "911220", "nb": 150, "region": "Mauricie"},
    {"name": "Service incendie Saguenay", "sector": "911220", "nb": 140, "region": "Saguenay"},
    {"name": "Régie intermunicipale incendie (exemple)", "sector": "911220", "nb": 45, "region": "Régions"},
    
    # Services de police (911210)
    {"name": "SPVM - Service de police Ville de Montréal", "sector": "911210", "nb": 5500, "region": "Montréal"},
    {"name": "Sûreté du Québec (SQ)", "sector": "911210", "nb": 7800, "region": "Québec"},
    {"name": "Service de police Ville de Québec", "sector": "911210", "nb": 850, "region": "Québec"},
    {"name": "Service de police Ville de Laval", "sector": "911210", "nb": 520, "region": "Laval"},
    {"name": "Service de police Longueuil (SPAL)", "sector": "911210", "nb": 480, "region": "Montérégie"},
    {"name": "Service de police Gatineau", "sector": "911210", "nb": 420, "region": "Outaouais"},
    {"name": "Sécurité publique Trois-Rivières", "sector": "911210", "nb": 180, "region": "Mauricie"},
    
    # Travaux publics (911310)
    {"name": "Travaux publics Ville de Montréal", "sector": "911310", "nb": 4500, "region": "Montréal"},
    {"name": "Travaux publics Ville de Québec", "sector": "911310", "nb": 1800, "region": "Québec"},
    {"name": "Travaux publics Ville de Laval", "sector": "911310", "nb": 850, "region": "Laval"},
    {"name": "Travaux publics Longueuil", "sector": "911310", "nb": 650, "region": "Montérégie"},
    {"name": "Travaux publics Gatineau", "sector": "911310", "nb": 580, "region": "Outaouais"},
    
    # Services correctionnels (911400)
    {"name": "Établissement Bordeaux (Montréal)", "sector": "911400", "nb": 850, "region": "Montréal"},
    {"name": "Établissement Rivière-des-Prairies", "sector": "911400", "nb": 420, "region": "Montréal"},
    {"name": "Établissement Québec", "sector": "911400", "nb": 380, "region": "Québec"},
    {"name": "Établissement Sherbrooke", "sector": "911400", "nb": 220, "region": "Estrie"},
    
    # Administration municipale (911190)
    {"name": "Ville de Montréal - Administration", "sector": "911190", "nb": 3200, "region": "Montréal"},
    {"name": "Ville de Québec - Administration", "sector": "911190", "nb": 1400, "region": "Québec"},
    {"name": "Ville de Laval - Administration", "sector": "911190", "nb": 650, "region": "Laval"},
    
    # Services paramédicaux (912910)
    {"name": "Urgences-santé (Montréal/Laval)", "sector": "912910", "nb": 1400, "region": "Montréal"},
    {"name": "Corporation Ambulancière Québec", "sector": "912910", "nb": 420, "region": "Québec"},
    {"name": "Dessercom (régional)", "sector": "912910", "nb": 850, "region": "Régions"},
    {"name": "Ambulances Demers", "sector": "912910", "nb": 380, "region": "Montérégie"},
]

AGES = ["18-24", "25-34", "35-44", "45-54", "55-64"]


def populate_scian91():
    """Peuple SafetyGraph avec les secteurs SCIAN 91 (Administrations publiques)"""
    
    print("=" * 70)
    print("🚒🚔 POPULATION SAFETYGRAPH - SCIAN 91")
    print("    Administrations publiques")
    print("    🔥 Pompiers | 🚔 Police | 🚧 Travaux publics | 🚑 Ambulanciers")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Secteurs: {len(SECTEURS_SCIAN_91)}")
    print(f"Organisations: {len(ORGANISATIONS_SCIAN_91)}")
    print("=" * 70)
    
    conn = SafetyGraphCartographyConnector()
    conn.connect()
    print("\n✅ Neo4j connecté")
    print(f"📊 Stats initiales: {conn.get_graph_stats()}\n")
    
    stats = {"orgs": 0, "zones": 0, "risks": 0, "persons": 0, "teams": 0, "roles": 0}
    
    # Créer organisations
    print("📦 Création des organisations SCIAN 91 (ADMINISTRATIONS PUBLIQUES)...")
    org_map = {}
    for o in ORGANISATIONS_SCIAN_91:
        org = Organization(
            name=o["name"],
            sector_scian=o["sector"],
            nb_employes=o["nb"],
            region_ssq=o["region"]
        )
        oid = conn.inject_organization(org)
        org_map[o["name"]] = {"id": oid, "sector": o["sector"], "nb": o["nb"]}
        stats["orgs"] += 1
        sector_nom = SECTEURS_SCIAN_91[o["sector"]]["nom"]
        print(f"   ✅ {o['name'][:45]} ({o['sector']})")
    
    # Créer entités par organisation
    print("\n🏗️ Création des entités par organisation...")
    
    for name, info in org_map.items():
        oid, sector = info["id"], info["sector"]
        data = SECTEURS_SCIAN_91[sector]
        
        # Icône selon secteur
        if "incendie" in name.lower() or sector == "911220":
            icon = "🚒"
        elif "police" in name.lower() or "SQ" in name or sector == "911210":
            icon = "🚔"
        elif "ambulan" in name.lower() or "Urgences" in name or sector == "912910":
            icon = "🚑"
        elif "correctionnel" in name.lower() or "Établissement" in name:
            icon = "🔒"
        elif "Travaux" in name:
            icon = "🚧"
        else:
            icon = "🏛️"
            
        print(f"\n   {icon} {name[:45]}")
        print(f"      Secteur: {data['nom']}")
        
        # Rôles
        rids = []
        for r in data["roles"]:
            is_sup = any(x in r for x in ["Chef", "Directeur", "Capitaine", "Lieutenant", "Sergent", "Gestionnaire", "Inspecteur"])
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
        
        # Équipes (24/7 pour services urgence)
        tids = []
        if sector in ["911220", "911210", "912910"]:  # Urgence 24/7
            equipes = ["Équipe Jour", "Équipe Soir", "Équipe Nuit", "Équipe Volante"]
        elif sector == "911400":  # Correctionnel 24/7
            equipes = ["Équipe Jour", "Équipe Soir", "Équipe Nuit"]
        else:
            equipes = ["Équipe Jour", "Équipe Terrain", "Équipe Administration"]
            
        for t in equipes:
            team = Team(name=t, department=data["nom"][:25])
            tid = conn.inject_team(team)
            tids.append(tid)
            conn.create_relation(tid, oid, RelationType.APPARTIENT_A)
            stats["teams"] += 1
        print(f"      • {len(tids)} équipes")
        
        # Personnes (ratio basé sur taille)
        nb_persons = max(5, min(info["nb"] // 150, 40))
        for i in range(nb_persons):
            p = Person(
                matricule=f"GOUV91-{sector[-3:]}-{stats['persons']+1:04d}",
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
            # Exposition aux risques (90% du personnel urgence exposé)
            if rkids and i % 10 < 9:
                conn.create_relation(pid, rkids[i % len(rkids)], RelationType.EXPOSE_A)
        
        print(f"      • {nb_persons} personnes (anonymisées Loi 25)")
    
    # Résumé
    print("\n" + "=" * 70)
    print("📊 RÉSUMÉ POPULATION SCIAN 91 - ADMINISTRATIONS PUBLIQUES")
    print("=" * 70)
    print(f"   Organisations: {stats['orgs']}")
    print(f"   Zones de travail: {stats['zones']}")
    print(f"   Risques identifiés: {stats['risks']}")
    print(f"   Équipes: {stats['teams']}")
    print(f"   Rôles/Professions: {stats['roles']}")
    print(f"   Personnes: {stats['persons']}")
    print(f"\n   Neo4j final: {conn.get_graph_stats()}")
    print("=" * 70)
    print("✅ POPULATION SCIAN 91 (ADMINISTRATIONS PUBLIQUES) TERMINÉE!")
    print("=" * 70)
    
    conn.close()
    return stats


if __name__ == "__main__":
    populate_scian91()
