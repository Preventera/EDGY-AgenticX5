#!/usr/bin/env python3
"""
🛡️ Script de Population Neo4j - Secteurs SCIAN 21
Extraction minière, exploitation en carrière, pétrole et gaz
EDGY-AgenticX5 | SafetyGraph | Preventera

Basé sur les données CNESST:
- Plan d'action mines souterraines (accidents mortels)
- Risques Tolérance Zéro CNESST
- Formation sauveteurs miniers
- Magazine Belmine

Secteurs inclus:
- 2111: Extraction de pétrole et de gaz
- 2121: Extraction de charbon
- 2122: Extraction de minerais métalliques (or, fer, cuivre, zinc)
- 2123: Extraction de minerais non métalliques (carrières)
- 2131: Activités de soutien à l'extraction minière
"""

import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

from src.cartography.connector import SafetyGraphCartographyConnector
from src.cartography.models import Organization, Person, Team, Role, Zone, Risk, RiskLevel, RelationType

# ============================================================================
# DONNÉES CNESST - SECTEURS SCIAN 21 (MINES ET EXTRACTION)
# Risques Tolérance Zéro identifiés par la CNESST
# ============================================================================

SECTEURS_SCIAN_21 = {
    "212210": {
        "nom": "Extraction de minerais de fer",
        "description": "Mines de fer à ciel ouvert et souterraines",
        "risques": [
            {"desc": "Effondrement galerie souterraine", "cat": "geotechnique", "prob": 2, "grav": 5},
            {"desc": "Collision véhicule lourd (camion 400t)", "cat": "mecanique", "prob": 3, "grav": 5},
            {"desc": "Chute de roches/éboulis", "cat": "geotechnique", "prob": 3, "grav": 5},
            {"desc": "Explosion/déflagration (dynamitage)", "cat": "explosion", "prob": 2, "grav": 5},
            {"desc": "Coincement/écrasement équipement minier", "cat": "mecanique", "prob": 3, "grav": 5},
            {"desc": "Inhalation poussières silice cristalline", "cat": "chimique", "prob": 4, "grav": 4},
            {"desc": "Bruit >85dB équipements lourds", "cat": "bruit", "prob": 5, "grav": 3},
            {"desc": "Vibrations corps entier (foreuse)", "cat": "ergonomique", "prob": 4, "grav": 3},
        ],
        "zones": [
            {"nom": "Front de taille souterrain", "risk": "critique", "dangers": ["Effondrement", "Chute roches", "Ventilation"], "epi": ["Casque minier", "Lampe frontale", "Auto-sauveteur"]},
            {"nom": "Rampe d'accès mine", "risk": "critique", "dangers": ["Collision", "Chute véhicule"], "epi": ["Ceinture 5 points", "Radio"]},
            {"nom": "Zone de dynamitage", "risk": "critique", "dangers": ["Explosion", "Projection"], "epi": ["Abri", "Périmètre sécurité"]},
            {"nom": "Concasseur primaire", "risk": "eleve", "dangers": ["Coincement", "Poussières"], "epi": ["Masque P100", "Casque"]},
            {"nom": "Atelier mécanique mine", "risk": "eleve", "dangers": ["Écrasement", "Huiles"], "epi": ["Chaussures sécurité", "Gants"]},
        ],
        "roles": ["Mineur de fond", "Opérateur foreuse", "Boutefeu", "Opérateur camion minier", "Mécanicien minier", "Géologue", "Ingénieur minier", "Contremaître mine"],
        "certs": ["SIMDUT", "Sauveteur minier CNESST", "Dynamitage", "Véhicule lourd minier", "Espace clos", "Cadenassage", "Auto-sauveteur"],
    },
    
    "212220": {
        "nom": "Extraction de minerais d'or et d'argent",
        "description": "Mines d'or souterraines profondes",
        "risques": [
            {"desc": "Coup de terrain (rockburst)", "cat": "geotechnique", "prob": 3, "grav": 5},
            {"desc": "Effondrement chantier souterrain", "cat": "geotechnique", "prob": 2, "grav": 5},
            {"desc": "Asphyxie déficience O2", "cat": "chimique", "prob": 2, "grav": 5},
            {"desc": "Intoxication gaz (CO, NO2, H2S)", "cat": "chimique", "prob": 3, "grav": 5},
            {"desc": "Noyade (infiltration eau)", "cat": "noyade", "prob": 2, "grav": 5},
            {"desc": "Chaleur extrême profondeur (>40°C)", "cat": "thermique", "prob": 4, "grav": 4},
            {"desc": "Exposition cyanure (traitement or)", "cat": "chimique", "prob": 3, "grav": 5},
            {"desc": "Chute dans puits/cheminée", "cat": "chute", "prob": 2, "grav": 5},
        ],
        "zones": [
            {"nom": "Chantier d'abattage profond", "risk": "critique", "dangers": ["Coup terrain", "Chaleur", "Gaz"], "epi": ["Auto-sauveteur", "Détecteur multi-gaz", "Gilet refroidissant"]},
            {"nom": "Puits principal", "risk": "critique", "dangers": ["Chute", "Cage", "Câble"], "epi": ["Harnais", "Casque", "Lampe"]},
            {"nom": "Station de pompage", "risk": "critique", "dangers": ["Noyade", "Électricité"], "epi": ["VFI", "Gants isolants"]},
            {"nom": "Usine de traitement cyanure", "risk": "critique", "dangers": ["Cyanure", "Acide"], "epi": ["Combinaison chimique", "SCBA"]},
            {"nom": "Salle de treuil", "risk": "eleve", "dangers": ["Câble", "Électricité"], "epi": ["Gants", "Lunettes"]},
        ],
        "roles": ["Mineur de fond", "Opérateur de treuil", "Pompier de mine", "Préposé traitement", "Boutefeu", "Géoméchanicien", "Superviseur souterrain", "Directeur mine"],
        "certs": ["SIMDUT", "Sauveteur minier CNESST", "Dynamitage", "Travail chaleur", "Cyanure", "Espace clos", "Détection gaz"],
    },
    
    "212231": {
        "nom": "Extraction de minerais de plomb-zinc",
        "description": "Mines de métaux de base",
        "risques": [
            {"desc": "Exposition plomb (saturnisme)", "cat": "chimique", "prob": 4, "grav": 4},
            {"desc": "Effondrement pilier/galerie", "cat": "geotechnique", "prob": 2, "grav": 5},
            {"desc": "Inhalation fumées soudage zinc", "cat": "chimique", "prob": 3, "grav": 4},
            {"desc": "Chute hauteur (cheminée minerai)", "cat": "chute", "prob": 3, "grav": 5},
            {"desc": "Collision engin souterrain (LHD)", "cat": "mecanique", "prob": 3, "grav": 5},
            {"desc": "Bruit foreuse jumbo >100dB", "cat": "bruit", "prob": 5, "grav": 4},
        ],
        "zones": [
            {"nom": "Galerie d'extraction", "risk": "critique", "dangers": ["Effondrement", "Collision LHD"], "epi": ["Casque", "Dossard réfléchissant", "Radio"]},
            {"nom": "Cheminée à minerai", "risk": "critique", "dangers": ["Chute", "Ensevelissement"], "epi": ["Harnais", "Ligne de vie"]},
            {"nom": "Concentrateur", "risk": "eleve", "dangers": ["Plomb", "Zinc", "Bruit"], "epi": ["Masque P100", "Bouchons", "Combinaison"]},
        ],
        "roles": ["Mineur", "Opérateur LHD (chargeuse)", "Opérateur jumbo", "Mécanicien souterrain", "Échantillonneur", "Contremaître"],
        "certs": ["SIMDUT", "Sauveteur minier", "Plomb santé", "Espace clos", "Véhicule souterrain"],
    },
    
    "212314": {
        "nom": "Extraction de granite (carrières)",
        "description": "Carrières à ciel ouvert",
        "risques": [
            {"desc": "Projection fragments (dynamitage)", "cat": "explosion", "prob": 3, "grav": 5},
            {"desc": "Chute paroi carrière", "cat": "chute", "prob": 3, "grav": 5},
            {"desc": "Écrasement par blocs", "cat": "mecanique", "prob": 3, "grav": 5},
            {"desc": "Renversement chargeuse/camion", "cat": "mecanique", "prob": 3, "grav": 5},
            {"desc": "Inhalation silice cristalline", "cat": "chimique", "prob": 4, "grav": 4},
            {"desc": "Bruit équipements concassage", "cat": "bruit", "prob": 5, "grav": 3},
        ],
        "zones": [
            {"nom": "Front de taille carrière", "risk": "critique", "dangers": ["Chute paroi", "Projection", "Blocs"], "epi": ["Casque", "Lunettes", "Dossard"]},
            {"nom": "Zone de dynamitage", "risk": "critique", "dangers": ["Explosion", "Projection"], "epi": ["Abri certifié", "Radio"]},
            {"nom": "Station concassage", "risk": "eleve", "dangers": ["Poussières", "Bruit", "Coincement"], "epi": ["Masque P100", "Bouchons"]},
            {"nom": "Rampe accès carrière", "risk": "eleve", "dangers": ["Renversement", "Collision"], "epi": ["Ceinture", "Radio"]},
        ],
        "roles": ["Carrier", "Boutefeu", "Opérateur pelle hydraulique", "Opérateur concasseur", "Camionneur carrière", "Chef carrière"],
        "certs": ["SIMDUT", "Dynamitage", "Silice", "Véhicule lourd", "Premiers soins"],
    },
    
    "212315": {
        "nom": "Extraction de sable et gravier",
        "description": "Sablières et gravières",
        "risques": [
            {"desc": "Ensevelissement effondrement talus", "cat": "geotechnique", "prob": 3, "grav": 5},
            {"desc": "Noyade (bassin décantation)", "cat": "noyade", "prob": 2, "grav": 5},
            {"desc": "Collision véhicule lourd", "cat": "mecanique", "prob": 3, "grav": 4},
            {"desc": "Coincement convoyeur", "cat": "mecanique", "prob": 3, "grav": 4},
            {"desc": "Inhalation poussières silice", "cat": "chimique", "prob": 4, "grav": 4},
        ],
        "zones": [
            {"nom": "Front d'extraction sable", "risk": "critique", "dangers": ["Ensevelissement", "Effondrement"], "epi": ["Casque", "Radio", "Périmètre"]},
            {"nom": "Bassin décantation", "risk": "critique", "dangers": ["Noyade", "Enlisement"], "epi": ["VFI", "Perche"]},
            {"nom": "Convoyeurs/cribles", "risk": "eleve", "dangers": ["Coincement", "Poussières"], "epi": ["Arrêt urgence", "Masque"]},
        ],
        "roles": ["Opérateur excavatrice", "Opérateur chargeuse", "Camionneur", "Préposé convoyeurs", "Chef sablière"],
        "certs": ["SIMDUT", "Silice", "Véhicule lourd", "Travail isolé"],
    },
    
    "213118": {
        "nom": "Services de forage (exploration)",
        "description": "Forage d'exploration minière",
        "risques": [
            {"desc": "Coincement/happement foreuse", "cat": "mecanique", "prob": 3, "grav": 5},
            {"desc": "Projection tige de forage", "cat": "mecanique", "prob": 2, "grav": 5},
            {"desc": "Renversement foreuse mobile", "cat": "mecanique", "prob": 3, "grav": 5},
            {"desc": "Électrocution (lignes HT)", "cat": "electrique", "prob": 2, "grav": 5},
            {"desc": "Isolement région éloignée", "cat": "psychosocial", "prob": 4, "grav": 4},
            {"desc": "Hypothermie/engelures hiver", "cat": "thermique", "prob": 3, "grav": 4},
            {"desc": "Attaque ours/animaux sauvages", "cat": "biologique", "prob": 2, "grav": 4},
        ],
        "zones": [
            {"nom": "Plateforme de forage", "risk": "critique", "dangers": ["Coincement", "Projection tige"], "epi": ["Casque", "Lunettes", "Gants anti-vibration"]},
            {"nom": "Camp exploration", "risk": "moyen", "dangers": ["Isolement", "Ours"], "epi": ["Radio satellite", "Bear spray"]},
            {"nom": "Accès hélicoptère/route", "risk": "eleve", "dangers": ["Transport", "Météo"], "epi": ["VFI", "Équipement survie"]},
        ],
        "roles": ["Foreur diamant", "Aide-foreur", "Géologue exploration", "Chef de camp", "Pilote hélicoptère", "Mécanicien foreuse"],
        "certs": ["SIMDUT", "Premiers soins éloigné", "Survie forêt", "Hélicoptère", "Travail isolé", "Ours"],
    },
    
    "211110": {
        "nom": "Extraction de pétrole et gaz",
        "description": "Puits de pétrole et gaz naturel",
        "risques": [
            {"desc": "Éruption puits (blowout)", "cat": "explosion", "prob": 2, "grav": 5},
            {"desc": "Explosion gaz H2S", "cat": "chimique", "prob": 2, "grav": 5},
            {"desc": "Incendie hydrocarbures", "cat": "thermique", "prob": 3, "grav": 5},
            {"desc": "Chute derrick/tour forage", "cat": "chute", "prob": 3, "grav": 5},
            {"desc": "Coincement équipement forage", "cat": "mecanique", "prob": 3, "grav": 5},
            {"desc": "Exposition benzène/BTEX", "cat": "chimique", "prob": 3, "grav": 4},
        ],
        "zones": [
            {"nom": "Plancher de forage", "risk": "critique", "dangers": ["Coincement", "H2S", "Éruption"], "epi": ["Détecteur H2S", "SCBA", "Casque"]},
            {"nom": "Tour de forage (derrick)", "risk": "critique", "dangers": ["Chute", "Vent"], "epi": ["Harnais", "Ligne de vie"]},
            {"nom": "Zone tête de puits", "risk": "critique", "dangers": ["Pression", "Fuite gaz"], "epi": ["Détecteur gaz", "EPI feu"]},
            {"nom": "Réservoirs stockage", "risk": "eleve", "dangers": ["Vapeurs", "Incendie"], "epi": ["Masque vapeurs", "Vêtements FR"]},
        ],
        "roles": ["Foreur pétrolier", "Assistant foreur", "Motorman", "Derrickman", "Opérateur BOP", "Superviseur forage", "Ingénieur puits"],
        "certs": ["SIMDUT", "H2S Alive", "Contrôle puits", "Travail hauteur", "Lutte incendie", "Sauvetage"],
    },
}

# ORGANISATIONS MINIÈRES QUÉBÉCOISES À CRÉER
ORGANISATIONS_SCIAN_21 = [
    # Extraction de fer (212210)
    {"name": "ArcelorMittal Mines Canada", "sector": "212210", "nb": 2500, "region": "Côte-Nord"},
    {"name": "Minerai de Fer Québec (MFQ)", "sector": "212210", "nb": 800, "region": "Côte-Nord"},
    {"name": "Champion Iron - Bloom Lake", "sector": "212210", "nb": 650, "region": "Côte-Nord"},
    
    # Extraction d'or (212220)
    {"name": "Agnico Eagle - LaRonde", "sector": "212220", "nb": 1200, "region": "Abitibi"},
    {"name": "Eldorado Gold - Lamaque", "sector": "212220", "nb": 450, "region": "Abitibi"},
    {"name": "Newmont - Éléonore", "sector": "212220", "nb": 800, "region": "Nord-du-Québec"},
    {"name": "IAMGOLD - Westwood", "sector": "212220", "nb": 550, "region": "Abitibi"},
    
    # Plomb-zinc (212231)
    {"name": "Glencore - Mine Matagami", "sector": "212231", "nb": 400, "region": "Abitibi"},
    {"name": "Trevali - Caribou", "sector": "212231", "nb": 250, "region": "Nouveau-Brunswick"}, # près Québec
    
    # Carrières granite (212314)
    {"name": "Polycor - Carrières Stanstead", "sector": "212314", "nb": 180, "region": "Estrie"},
    {"name": "Granicor - Rivière-à-Pierre", "sector": "212314", "nb": 120, "region": "Capitale-Nationale"},
    
    # Sable et gravier (212315)
    {"name": "Bauval - Sablières Québec", "sector": "212315", "nb": 85, "region": "Capitale-Nationale"},
    {"name": "Demix Agrégats", "sector": "212315", "nb": 150, "region": "Montréal"},
    
    # Services forage (213118)
    {"name": "Major Drilling", "sector": "213118", "nb": 350, "region": "Val-d'Or"},
    {"name": "Forages Chibougamau", "sector": "213118", "nb": 120, "region": "Nord-du-Québec"},
    {"name": "Orbit Garant Drilling", "sector": "213118", "nb": 280, "region": "Val-d'Or"},
    
    # Pétrole et gaz (211110) - peu au Québec mais inclus
    {"name": "Junex - Gaspésie", "sector": "211110", "nb": 45, "region": "Gaspésie"},
]

AGES = ["18-24", "25-34", "35-44", "45-54", "55-64"]


def populate_scian21():
    """Peuple SafetyGraph avec les secteurs SCIAN 21 (Mines et Extraction)"""
    
    print("=" * 70)
    print("⛏️🏔️ POPULATION SAFETYGRAPH - SCIAN 21")
    print("    Extraction minière, carrières, pétrole et gaz")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Secteurs: {len(SECTEURS_SCIAN_21)}")
    print(f"Organisations: {len(ORGANISATIONS_SCIAN_21)}")
    print("=" * 70)
    
    conn = SafetyGraphCartographyConnector()
    conn.connect()
    print("\n✅ Neo4j connecté")
    print(f"📊 Stats initiales: {conn.get_graph_stats()}\n")
    
    stats = {"orgs": 0, "zones": 0, "risks": 0, "persons": 0, "teams": 0, "roles": 0}
    
    # Créer organisations
    print("📦 Création des organisations SCIAN 21 (MINES)...")
    org_map = {}
    for o in ORGANISATIONS_SCIAN_21:
        org = Organization(
            name=o["name"],
            sector_scian=o["sector"],
            nb_employes=o["nb"],
            region_ssq=o["region"]
        )
        oid = conn.inject_organization(org)
        org_map[o["name"]] = {"id": oid, "sector": o["sector"], "nb": o["nb"]}
        stats["orgs"] += 1
        sector_nom = SECTEURS_SCIAN_21[o["sector"]]["nom"]
        print(f"   ✅ {o['name']} ({o['sector']} - {sector_nom[:30]})")
    
    # Créer entités par organisation
    print("\n🏗️ Création des entités par organisation...")
    
    for name, info in org_map.items():
        oid, sector = info["id"], info["sector"]
        data = SECTEURS_SCIAN_21[sector]
        print(f"\n   ⛏️ {name}")
        print(f"      Secteur: {data['nom']}")
        
        # Rôles
        rids = []
        for r in data["roles"]:
            is_sup = any(x in r for x in ["Chef", "Contremaître", "Superviseur", "Directeur", "Ingénieur"])
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
        print(f"      • {len(zids)} zones (🔴 critique: {sum(1 for z in data['zones'] if z['risk'] == 'critique')})")
        
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
        print(f"      • {len(rkids)} risques (⚠️ score EDGY max: {max(r['prob']*r['grav'] for r in data['risques'])})")
        
        # Équipes (selon type de mine)
        tids = []
        if "souterrain" in data["nom"].lower() or "or" in data["nom"].lower() or "fer" in data["nom"].lower():
            equipes = ["Équipe Jour", "Équipe Soir", "Équipe Nuit", "Équipe Sauvetage"]
        elif "carrière" in data["nom"].lower() or "sable" in data["nom"].lower():
            equipes = ["Équipe Production", "Équipe Entretien"]
        else:
            equipes = ["Équipe A", "Équipe B", "Équipe Urgence"]
            
        for t in equipes:
            team = Team(name=t, department=data["nom"][:25])
            tid = conn.inject_team(team)
            tids.append(tid)
            conn.create_relation(tid, oid, RelationType.APPARTIENT_A)
            stats["teams"] += 1
        print(f"      • {len(tids)} équipes")
        
        # Personnes (ratio basé sur taille, secteur minier = plus gros)
        nb_persons = max(5, min(info["nb"] // 50, 20))
        for i in range(nb_persons):
            p = Person(
                matricule=f"MINE21-{sector[-3:]}-{stats['persons']+1:04d}",
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
            # Exposition aux risques critiques (70% des mineurs exposés)
            if rkids and i % 10 < 7:
                conn.create_relation(pid, rkids[i % len(rkids)], RelationType.EXPOSE_A)
        
        print(f"      • {nb_persons} personnes (anonymisées Loi 25)")
    
    # Résumé
    print("\n" + "=" * 70)
    print("📊 RÉSUMÉ POPULATION SCIAN 21 - MINES")
    print("=" * 70)
    print(f"   Organisations minières: {stats['orgs']}")
    print(f"   Zones de travail: {stats['zones']}")
    print(f"   Risques identifiés: {stats['risks']} (incl. Tolérance Zéro)")
    print(f"   Équipes: {stats['teams']}")
    print(f"   Rôles/Professions: {stats['roles']}")
    print(f"   Personnes: {stats['persons']}")
    print(f"\n   Neo4j final: {conn.get_graph_stats()}")
    print("=" * 70)
    print("✅ POPULATION SCIAN 21 (MINES) TERMINÉE!")
    print("=" * 70)
    
    conn.close()
    return stats


if __name__ == "__main__":
    populate_scian21()
