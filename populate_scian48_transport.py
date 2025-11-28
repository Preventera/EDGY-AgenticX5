#!/usr/bin/env python3
"""
🛡️ Script de Population Neo4j - Secteurs SCIAN 48-49
Transport et entreposage
EDGY-AgenticX5 | SafetyGraph | Preventera

Basé sur les données CNESST:
- Déplacements routiers dans le cadre du travail
- Transport routier de matières dangereuses
- Association du camionnage du Québec (ACQ)
- Statistiques lésions professionnelles

Secteurs inclus:
- 481: Transport aérien
- 482: Transport ferroviaire
- 483: Transport par eau
- 484: Transport par camion
- 485: Transport en commun et transport terrestre de voyageurs
- 486: Transport par pipeline
- 487: Transport de tourisme et d'agrément
- 488: Activités de soutien au transport
- 491: Services postaux
- 492: Messageries et services de messagers
- 493: Entreposage
"""

import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

from src.cartography.connector import SafetyGraphCartographyConnector
from src.cartography.models import Organization, Person, Team, Role, Zone, Risk, RiskLevel, RelationType

# ============================================================================
# DONNÉES CNESST - SECTEURS SCIAN 48-49 (TRANSPORT ET ENTREPOSAGE)
# ============================================================================

SECTEURS_SCIAN_48 = {
    "484110": {
        "nom": "Transport local par camion",
        "description": "Camionnage local, livraison urbaine",
        "risques": [
            {"desc": "Accident routier collision", "cat": "routier", "prob": 3, "grav": 5},
            {"desc": "Chute de la cabine/remorque", "cat": "chute", "prob": 4, "grav": 4},
            {"desc": "TMS - manutention chargement/déchargement", "cat": "ergonomique", "prob": 5, "grav": 3},
            {"desc": "Écrasement lors arrimage", "cat": "mecanique", "prob": 3, "grav": 5},
            {"desc": "Coincement hayon élévateur", "cat": "mecanique", "prob": 3, "grav": 4},
            {"desc": "Fatigue/somnolence au volant", "cat": "psychosocial", "prob": 4, "grav": 5},
            {"desc": "Agression vol de cargaison", "cat": "violence", "prob": 2, "grav": 4},
        ],
        "zones": [
            {"nom": "Cabine camion", "risk": "eleve", "dangers": ["Collision", "Fatigue", "Vibrations"], "epi": ["Ceinture", "Chaussures sécurité"]},
            {"nom": "Aire de chargement", "risk": "eleve", "dangers": ["Chute", "Écrasement", "TMS"], "epi": ["Casque", "Gants", "Chaussures"]},
            {"nom": "Quai de livraison", "risk": "moyen", "dangers": ["Hayon", "Circulation"], "epi": ["Dossard", "Chaussures"]},
            {"nom": "Stationnement camions", "risk": "moyen", "dangers": ["Recul", "Angle mort"], "epi": ["Dossard réfléchissant"]},
        ],
        "roles": ["Chauffeur classe 1", "Chauffeur classe 3", "Aide-livreur", "Répartiteur", "Chef de flotte"],
        "certs": ["Permis classe 1/3", "SIMDUT", "Arrimage", "Matières dangereuses", "Premiers soins"],
    },
    
    "484121": {
        "nom": "Transport longue distance par camion",
        "description": "Camionnage longue distance, transport interprovincial",
        "risques": [
            {"desc": "Accident routier haute vitesse", "cat": "routier", "prob": 3, "grav": 5},
            {"desc": "Fatigue chronique/heures de conduite", "cat": "psychosocial", "prob": 4, "grav": 5},
            {"desc": "Conditions météo (verglas, tempête)", "cat": "environnement", "prob": 4, "grav": 5},
            {"desc": "TMS - position assise prolongée", "cat": "ergonomique", "prob": 5, "grav": 3},
            {"desc": "Renversement semi-remorque", "cat": "routier", "prob": 2, "grav": 5},
            {"desc": "Isolation/détresse psychologique", "cat": "psychosocial", "prob": 4, "grav": 3},
            {"desc": "Accident arrêt routier (relais)", "cat": "routier", "prob": 3, "grav": 4},
        ],
        "zones": [
            {"nom": "Cabine semi-remorque", "risk": "eleve", "dangers": ["Collision", "Fatigue", "Isolement"], "epi": ["Ceinture", "ELD"]},
            {"nom": "Aire de repos routière", "risk": "moyen", "dangers": ["Vol", "Agression"], "epi": ["Téléphone", "Éclairage"]},
            {"nom": "Poste frontière", "risk": "bas", "dangers": ["Attente", "Stress"], "epi": ["Documentation"]},
            {"nom": "Terminal de transbordement", "risk": "eleve", "dangers": ["Chariot élévateur", "Recul"], "epi": ["Dossard", "Casque"]},
        ],
        "roles": ["Chauffeur longue distance classe 1", "Owner-operator", "Chauffeur d'équipe", "Répartiteur", "Directeur transport"],
        "certs": ["Permis classe 1", "FAST/PEP", "Heures de service", "ELD", "SIMDUT", "Matières dangereuses"],
    },
    
    "484210": {
        "nom": "Déménagement et entreposage",
        "description": "Services de déménagement résidentiel et commercial",
        "risques": [
            {"desc": "TMS - levage charges lourdes", "cat": "ergonomique", "prob": 5, "grav": 4},
            {"desc": "Chute escaliers/rampes", "cat": "chute", "prob": 4, "grav": 4},
            {"desc": "Écrasement/coincement meubles", "cat": "mecanique", "prob": 4, "grav": 4},
            {"desc": "Blessure dos (hernie discale)", "cat": "ergonomique", "prob": 4, "grav": 4},
            {"desc": "Chute objet sur pieds/tête", "cat": "chute", "prob": 4, "grav": 3},
            {"desc": "Coupure verre/miroir", "cat": "coupure", "prob": 3, "grav": 3},
        ],
        "zones": [
            {"nom": "Résidence client", "risk": "eleve", "dangers": ["Escaliers", "Espaces restreints", "TMS"], "epi": ["Ceinture lombaire", "Gants"]},
            {"nom": "Camion déménagement", "risk": "eleve", "dangers": ["Chute rampe", "Écrasement"], "epi": ["Chaussures", "Gants"]},
            {"nom": "Entrepôt stockage", "risk": "moyen", "dangers": ["Rayonnage", "Chariot"], "epi": ["Casque", "Dossard"]},
        ],
        "roles": ["Déménageur", "Chef d'équipe déménagement", "Chauffeur-déménageur", "Estimateur", "Directeur opérations"],
        "certs": ["Manutention sécuritaire", "SIMDUT", "Chariot élévateur", "Premiers soins"],
    },
    
    "484230": {
        "nom": "Transport de matières dangereuses",
        "description": "Transport TMD - produits chimiques, inflammables, explosifs",
        "risques": [
            {"desc": "Déversement matières dangereuses", "cat": "chimique", "prob": 2, "grav": 5},
            {"desc": "Incendie/explosion cargo inflammable", "cat": "explosion", "prob": 2, "grav": 5},
            {"desc": "Intoxication vapeurs chimiques", "cat": "chimique", "prob": 3, "grav": 5},
            {"desc": "Accident routier avec TMD", "cat": "routier", "prob": 2, "grav": 5},
            {"desc": "Brûlure chimique lors connexion", "cat": "chimique", "prob": 3, "grav": 4},
            {"desc": "Contamination environnementale", "cat": "chimique", "prob": 2, "grav": 4},
        ],
        "zones": [
            {"nom": "Citerne transport", "risk": "critique", "dangers": ["Déversement", "Vapeurs", "Explosion"], "epi": ["Combinaison chimique", "SCBA", "Gants nitrile"]},
            {"nom": "Point de chargement chimique", "risk": "critique", "dangers": ["Connexion", "Vapeurs", "Brûlure"], "epi": ["Masque vapeurs", "Lunettes", "Tablier"]},
            {"nom": "Aire de stationnement TMD", "risk": "eleve", "dangers": ["Fuite", "Incendie"], "epi": ["Extincteur", "Kit déversement"]},
        ],
        "roles": ["Chauffeur TMD certifié", "Opérateur citerne", "Préposé chargement TMD", "Conseiller TMD", "Coordonnateur urgence"],
        "certs": ["TMD Transport Canada", "SIMDUT", "Intervention urgence TMD", "Premiers soins", "Lutte incendie"],
    },
    
    "485110": {
        "nom": "Transport urbain en commun",
        "description": "Autobus urbains, métro",
        "risques": [
            {"desc": "Agression par passager", "cat": "violence", "prob": 4, "grav": 4},
            {"desc": "Accident collision autobus", "cat": "routier", "prob": 3, "grav": 5},
            {"desc": "TMS - position assise prolongée", "cat": "ergonomique", "prob": 5, "grav": 3},
            {"desc": "Stress/détresse psychologique", "cat": "psychosocial", "prob": 4, "grav": 3},
            {"desc": "Blessure passager (freinage)", "cat": "routier", "prob": 3, "grav": 3},
            {"desc": "Glissade entrée/sortie autobus", "cat": "chute", "prob": 3, "grav": 3},
        ],
        "zones": [
            {"nom": "Poste de conduite autobus", "risk": "eleve", "dangers": ["Agression", "Collision", "Stress"], "epi": ["Vitre protection", "Radio"]},
            {"nom": "Garage entretien autobus", "risk": "eleve", "dangers": ["Gaz échappement", "Fosse"], "epi": ["Masque", "Harnais"]},
            {"nom": "Terminal autobus", "risk": "moyen", "dangers": ["Circulation", "Piétons"], "epi": ["Dossard"]},
        ],
        "roles": ["Chauffeur autobus", "Opérateur métro", "Mécanicien autobus", "Inspecteur", "Chef de terminus"],
        "certs": ["Permis classe 2", "Formation passagers", "Gestion agressivité", "Premiers soins"],
    },
    
    "488519": {
        "nom": "Autres activités de soutien au transport routier",
        "description": "Remorquage, dépannage routier",
        "risques": [
            {"desc": "Frappé par véhicule sur route", "cat": "routier", "prob": 3, "grav": 5},
            {"desc": "Écrasement lors remorquage", "cat": "mecanique", "prob": 3, "grav": 5},
            {"desc": "Blessure câble/chaîne sous tension", "cat": "mecanique", "prob": 3, "grav": 4},
            {"desc": "Travail nuit/visibilité réduite", "cat": "environnement", "prob": 4, "grav": 4},
            {"desc": "Conditions météo extrêmes", "cat": "environnement", "prob": 4, "grav": 4},
            {"desc": "Contact véhicule accidenté (fluides)", "cat": "chimique", "prob": 3, "grav": 3},
        ],
        "zones": [
            {"nom": "Bord de route intervention", "risk": "critique", "dangers": ["Circulation", "Visibilité", "Météo"], "epi": ["Dossard classe 3", "Cônes", "Gyrophare"]},
            {"nom": "Atelier remorquage", "risk": "eleve", "dangers": ["Treuil", "Levage"], "epi": ["Gants", "Casque", "Chaussures"]},
        ],
        "roles": ["Opérateur dépanneuse", "Remorqueur poids lourd", "Répartiteur 24h", "Mécanicien routier", "Propriétaire remorquage"],
        "certs": ["Permis classe 1/3", "Intervention routière", "Signalisation", "Premiers soins", "TMD base"],
    },
    
    "493110": {
        "nom": "Entreposage général",
        "description": "Entrepôts, centres de distribution",
        "risques": [
            {"desc": "Collision chariot élévateur", "cat": "mecanique", "prob": 3, "grav": 5},
            {"desc": "Chute de hauteur (rayonnage)", "cat": "chute", "prob": 3, "grav": 5},
            {"desc": "Écrasement par palette/marchandise", "cat": "mecanique", "prob": 3, "grav": 5},
            {"desc": "TMS - manutention répétitive", "cat": "ergonomique", "prob": 5, "grav": 3},
            {"desc": "Renversement chariot élévateur", "cat": "mecanique", "prob": 2, "grav": 5},
            {"desc": "Coincement quai de chargement", "cat": "mecanique", "prob": 3, "grav": 4},
            {"desc": "Effondrement rayonnage", "cat": "mecanique", "prob": 2, "grav": 5},
        ],
        "zones": [
            {"nom": "Allées entrepôt", "risk": "eleve", "dangers": ["Chariot", "Piétons", "Palettes"], "epi": ["Dossard", "Chaussures sécurité"]},
            {"nom": "Zone rayonnage haute", "risk": "critique", "dangers": ["Chute hauteur", "Effondrement"], "epi": ["Harnais", "Casque"]},
            {"nom": "Quai de chargement", "risk": "eleve", "dangers": ["Recul camion", "Hayon"], "epi": ["Dossard", "Casque"]},
            {"nom": "Zone préparation commandes", "risk": "moyen", "dangers": ["TMS", "Coupures"], "epi": ["Gants", "Ceinture lombaire"]},
        ],
        "roles": ["Cariste", "Préparateur commandes", "Réceptionnaire", "Expéditeur", "Chef d'entrepôt", "Superviseur quai"],
        "certs": ["Chariot élévateur", "SIMDUT", "Travail hauteur", "Premiers soins", "Manutention"],
    },
    
    "493120": {
        "nom": "Entreposage frigorifique",
        "description": "Entrepôts réfrigérés, congélation",
        "risques": [
            {"desc": "Hypothermie/engelures", "cat": "thermique", "prob": 4, "grav": 4},
            {"desc": "Glissade sol glacé", "cat": "chute", "prob": 4, "grav": 3},
            {"desc": "Asphyxie (fuite réfrigérant NH3)", "cat": "chimique", "prob": 2, "grav": 5},
            {"desc": "Enfermement chambre froide", "cat": "environnement", "prob": 2, "grav": 5},
            {"desc": "TMS - travail froid", "cat": "ergonomique", "prob": 4, "grav": 3},
            {"desc": "Collision chariot (visibilité buée)", "cat": "mecanique", "prob": 3, "grav": 4},
        ],
        "zones": [
            {"nom": "Chambre congélation -25°C", "risk": "critique", "dangers": ["Hypothermie", "Enfermement", "Glissade"], "epi": ["Combinaison grand froid", "Gants isolants", "Alarme homme mort"]},
            {"nom": "Chambre réfrigérée 4°C", "risk": "eleve", "dangers": ["Froid", "Humidité", "Glissade"], "epi": ["Vêtements isolants", "Bottes antidérapantes"]},
            {"nom": "Salle machines (compresseurs NH3)", "risk": "critique", "dangers": ["Ammoniac", "Bruit", "Pression"], "epi": ["Détecteur NH3", "Masque évasion", "Bouchons"]},
        ],
        "roles": ["Manutentionnaire frigorifique", "Cariste froid", "Technicien réfrigération", "Préparateur commandes froid", "Chef entrepôt froid"],
        "certs": ["Chariot élévateur", "Travail au froid", "SIMDUT", "Ammoniac", "Premiers soins", "Espace clos"],
    },
    
    "492110": {
        "nom": "Services de messagerie et colis",
        "description": "Livraison colis, messagerie express",
        "risques": [
            {"desc": "Accident routier livraison", "cat": "routier", "prob": 4, "grav": 4},
            {"desc": "Morsure chien domicile", "cat": "biologique", "prob": 3, "grav": 3},
            {"desc": "TMS - manutention colis répétitive", "cat": "ergonomique", "prob": 5, "grav": 3},
            {"desc": "Vol/agression livraison", "cat": "violence", "prob": 3, "grav": 4},
            {"desc": "Glissade escalier/perron", "cat": "chute", "prob": 4, "grav": 3},
            {"desc": "Stress délais livraison", "cat": "psychosocial", "prob": 4, "grav": 2},
        ],
        "zones": [
            {"nom": "Véhicule livraison", "risk": "eleve", "dangers": ["Collision", "Recul", "Colis"], "epi": ["Ceinture", "Chaussures"]},
            {"nom": "Centre de tri", "risk": "eleve", "dangers": ["Convoyeurs", "TMS", "Bruit"], "epi": ["Gants", "Bouchons", "Dossard"]},
            {"nom": "Point de livraison client", "risk": "moyen", "dangers": ["Chien", "Escalier", "Vol"], "epi": ["Spray poivre", "Lampe"]},
        ],
        "roles": ["Livreur/Coursier", "Chauffeur-livreur", "Trieur colis", "Répartiteur", "Superviseur livraison"],
        "certs": ["Permis classe 5", "Manutention", "Conduite défensive", "Premiers soins"],
    },
}

# ORGANISATIONS DE TRANSPORT QUÉBÉCOISES À CRÉER
ORGANISATIONS_SCIAN_48 = [
    # Transport local camion (484110)
    {"name": "Transport Robert", "sector": "484110", "nb": 850, "region": "Montréal"},
    {"name": "Groupe Morneau", "sector": "484110", "nb": 600, "region": "Montréal"},
    {"name": "Transport Guilbault", "sector": "484110", "nb": 450, "region": "Montréal"},
    
    # Transport longue distance (484121)
    {"name": "Transport Bourassa", "sector": "484121", "nb": 380, "region": "Québec"},
    {"name": "Groupe Transforce", "sector": "484121", "nb": 1200, "region": "Montréal"},
    {"name": "Transport Hervé Lemieux", "sector": "484121", "nb": 280, "region": "Montréal"},
    
    # Déménagement (484210)
    {"name": "Déménagement Myette", "sector": "484210", "nb": 120, "region": "Montréal"},
    {"name": "AMJ Campbell Québec", "sector": "484210", "nb": 85, "region": "Montréal"},
    
    # Transport matières dangereuses (484230)
    {"name": "Groupe Thibault Van Houtte", "sector": "484230", "nb": 280, "region": "Montréal"},
    {"name": "Transport TFI - TMD", "sector": "484230", "nb": 180, "region": "Montréal"},
    
    # Transport urbain (485110)
    {"name": "STM - Société de transport de Montréal", "sector": "485110", "nb": 10500, "region": "Montréal"},
    {"name": "RTC - Réseau de transport de la Capitale", "sector": "485110", "nb": 2200, "region": "Québec"},
    {"name": "STL - Société de transport de Laval", "sector": "485110", "nb": 1100, "region": "Laval"},
    
    # Remorquage (488519)
    {"name": "CAA-Québec Remorquage", "sector": "488519", "nb": 450, "region": "Québec"},
    {"name": "Remorquage Boisvert", "sector": "488519", "nb": 85, "region": "Montréal"},
    
    # Entreposage général (493110)
    {"name": "Groupe Logistec", "sector": "493110", "nb": 680, "region": "Montréal"},
    {"name": "Entreposage Montréal inc.", "sector": "493110", "nb": 220, "region": "Montréal"},
    {"name": "Purolator Distribution", "sector": "493110", "nb": 350, "region": "Montréal"},
    
    # Entreposage frigorifique (493120)
    {"name": "Congebec", "sector": "493120", "nb": 380, "region": "Montréal"},
    {"name": "Frigo-Transit", "sector": "493120", "nb": 150, "region": "Québec"},
    
    # Messagerie (492110)
    {"name": "Purolator Québec", "sector": "492110", "nb": 1200, "region": "Montréal"},
    {"name": "Postes Canada - Québec", "sector": "492110", "nb": 5500, "region": "Montréal"},
    {"name": "FedEx Québec", "sector": "492110", "nb": 800, "region": "Montréal"},
    {"name": "UPS Québec", "sector": "492110", "nb": 650, "region": "Montréal"},
]

AGES = ["18-24", "25-34", "35-44", "45-54", "55-64"]


def populate_scian48():
    """Peuple SafetyGraph avec les secteurs SCIAN 48-49 (Transport et Entreposage)"""
    
    print("=" * 70)
    print("🚛📦 POPULATION SAFETYGRAPH - SCIAN 48-49")
    print("    Transport et Entreposage")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Secteurs: {len(SECTEURS_SCIAN_48)}")
    print(f"Organisations: {len(ORGANISATIONS_SCIAN_48)}")
    print("=" * 70)
    
    conn = SafetyGraphCartographyConnector()
    conn.connect()
    print("\n✅ Neo4j connecté")
    print(f"📊 Stats initiales: {conn.get_graph_stats()}\n")
    
    stats = {"orgs": 0, "zones": 0, "risks": 0, "persons": 0, "teams": 0, "roles": 0}
    
    # Créer organisations
    print("📦 Création des organisations SCIAN 48-49 (TRANSPORT)...")
    org_map = {}
    for o in ORGANISATIONS_SCIAN_48:
        org = Organization(
            name=o["name"],
            sector_scian=o["sector"],
            nb_employes=o["nb"],
            region_ssq=o["region"]
        )
        oid = conn.inject_organization(org)
        org_map[o["name"]] = {"id": oid, "sector": o["sector"], "nb": o["nb"]}
        stats["orgs"] += 1
        sector_nom = SECTEURS_SCIAN_48[o["sector"]]["nom"]
        print(f"   ✅ {o['name']} ({o['sector']} - {sector_nom[:30]})")
    
    # Créer entités par organisation
    print("\n🏗️ Création des entités par organisation...")
    
    for name, info in org_map.items():
        oid, sector = info["id"], info["sector"]
        data = SECTEURS_SCIAN_48[sector]
        print(f"\n   🚛 {name}")
        print(f"      Secteur: {data['nom']}")
        
        # Rôles
        rids = []
        for r in data["roles"]:
            is_sup = any(x in r for x in ["Chef", "Superviseur", "Directeur", "Coordonnateur", "Propriétaire"])
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
        print(f"      • {len(zids)} zones")
        
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
        print(f"      • {len(rkids)} risques (score EDGY max: {max(r['prob']*r['grav'] for r in data['risques'])})")
        
        # Équipes (selon type de transport)
        tids = []
        if "485" in sector:  # Transport en commun - 24h
            equipes = ["Équipe Jour", "Équipe Soir", "Équipe Nuit", "Équipe Fin semaine"]
        elif "493" in sector:  # Entreposage - quarts
            equipes = ["Équipe Matin", "Équipe Après-midi", "Équipe Nuit"]
        else:
            equipes = ["Équipe Route", "Équipe Entretien", "Équipe Répartition"]
            
        for t in equipes:
            team = Team(name=t, department=data["nom"][:25])
            tid = conn.inject_team(team)
            tids.append(tid)
            conn.create_relation(tid, oid, RelationType.APPARTIENT_A)
            stats["teams"] += 1
        print(f"      • {len(tids)} équipes")
        
        # Personnes (ratio basé sur taille)
        nb_persons = max(5, min(info["nb"] // 100, 25))
        for i in range(nb_persons):
            p = Person(
                matricule=f"TRANS48-{sector[-3:]}-{stats['persons']+1:04d}",
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
            # Exposition aux risques routiers (80% des chauffeurs)
            if rkids and i % 10 < 8:
                conn.create_relation(pid, rkids[i % len(rkids)], RelationType.EXPOSE_A)
        
        print(f"      • {nb_persons} personnes (anonymisées Loi 25)")
    
    # Résumé
    print("\n" + "=" * 70)
    print("📊 RÉSUMÉ POPULATION SCIAN 48-49 - TRANSPORT")
    print("=" * 70)
    print(f"   Organisations transport: {stats['orgs']}")
    print(f"   Zones de travail: {stats['zones']}")
    print(f"   Risques identifiés: {stats['risks']}")
    print(f"   Équipes: {stats['teams']}")
    print(f"   Rôles/Professions: {stats['roles']}")
    print(f"   Personnes: {stats['persons']}")
    print(f"\n   Neo4j final: {conn.get_graph_stats()}")
    print("=" * 70)
    print("✅ POPULATION SCIAN 48-49 (TRANSPORT) TERMINÉE!")
    print("=" * 70)
    
    conn.close()
    return stats


if __name__ == "__main__":
    populate_scian48()
