#!/usr/bin/env python3
"""
🛡️ Script de Population Neo4j - Secteurs SCIAN 62
Soins de santé et assistance sociale
EDGY-AgenticX5 | SafetyGraph | Preventera

⚠️ SECTEUR #1 EN LÉSIONS PROFESSIONNELLES AU QUÉBEC
   74,517 dossiers ouverts et acceptés en 2022 (CNESST)

Basé sur les données CNESST:
- Plan d'action national prévention des risques en milieu de santé
- Risques priorisés: TMS, chutes de même niveau, violence au travail
- Statistiques RSSS (Réseau de la santé et des services sociaux)

Secteurs inclus:
- 621: Services de soins ambulatoires
- 622: Hôpitaux
- 623: Établissements de soins infirmiers et de soins pour bénéficiaires internes
- 624: Assistance sociale
"""

import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

from src.cartography.connector import SafetyGraphCartographyConnector
from src.cartography.models import Organization, Person, Team, Role, Zone, Risk, RiskLevel, RelationType

# ============================================================================
# DONNÉES CNESST - SECTEURS SCIAN 62 (SOINS DE SANTÉ)
# SECTEUR #1 EN LÉSIONS PROFESSIONNELLES AU QUÉBEC
# Risques priorisés CNESST: TMS, Chutes même niveau, Violence
# ============================================================================

SECTEURS_SCIAN_62 = {
    "622110": {
        "nom": "Hôpitaux généraux et chirurgicaux",
        "description": "Centres hospitaliers, urgences, chirurgie",
        "risques": [
            {"desc": "TMS - mobilisation patients", "cat": "ergonomique", "prob": 5, "grav": 4},
            {"desc": "Violence/agression patient ou visiteur", "cat": "violence", "prob": 4, "grav": 4},
            {"desc": "Piqûre aiguille/objet tranchant", "cat": "biologique", "prob": 4, "grav": 4},
            {"desc": "Exposition sang/liquides biologiques", "cat": "biologique", "prob": 4, "grav": 4},
            {"desc": "Chute de même niveau (plancher mouillé)", "cat": "chute", "prob": 4, "grav": 3},
            {"desc": "Exposition agents infectieux (COVID, TB)", "cat": "biologique", "prob": 4, "grav": 4},
            {"desc": "Détresse psychologique/épuisement", "cat": "psychosocial", "prob": 5, "grav": 4},
            {"desc": "Exposition radiations (radiologie)", "cat": "physique", "prob": 2, "grav": 4},
            {"desc": "Exposition médicaments cytotoxiques", "cat": "chimique", "prob": 3, "grav": 4},
        ],
        "zones": [
            {"nom": "Urgence", "risk": "critique", "dangers": ["Violence", "Piqûre", "Stress"], "epi": ["Gants", "Masque N95", "Visière"]},
            {"nom": "Unité de soins intensifs", "risk": "critique", "dangers": ["TMS", "Infections", "Stress"], "epi": ["Gants", "Blouse", "Masque"]},
            {"nom": "Bloc opératoire", "risk": "eleve", "dangers": ["Piqûre", "Sang", "Posture"], "epi": ["Gants doubles", "Lunettes", "Blouse"]},
            {"nom": "Unité de soins", "risk": "eleve", "dangers": ["TMS", "Chute", "Violence"], "epi": ["Chaussures antidérapantes", "Gants"]},
            {"nom": "Radiologie/Imagerie", "risk": "eleve", "dangers": ["Radiation", "TMS patient"], "epi": ["Tablier plombé", "Dosimètre"]},
        ],
        "roles": ["Infirmière", "Infirmier auxiliaire", "Préposé aux bénéficiaires (PAB)", "Médecin", "Inhalothérapeute", "Technicien en radiologie", "Brancardier", "Chef d'unité"],
        "certs": ["PDSB", "RCR", "SIMDUT", "Prévention infections", "Gestion violence"],
    },
    
    "622310": {
        "nom": "Hôpitaux psychiatriques",
        "description": "Soins psychiatriques, santé mentale",
        "risques": [
            {"desc": "Violence/agression patient psychiatrique", "cat": "violence", "prob": 5, "grav": 4},
            {"desc": "Morsure/griffure patient", "cat": "biologique", "prob": 4, "grav": 3},
            {"desc": "Détresse psychologique personnel", "cat": "psychosocial", "prob": 5, "grav": 4},
            {"desc": "TMS - contention patient", "cat": "ergonomique", "prob": 4, "grav": 4},
            {"desc": "Exposition fumée secondaire", "cat": "chimique", "prob": 3, "grav": 3},
            {"desc": "Automutilation témoin (trauma)", "cat": "psychosocial", "prob": 3, "grav": 4},
        ],
        "zones": [
            {"nom": "Unité psychiatrique fermée", "risk": "critique", "dangers": ["Violence", "Contention", "Trauma"], "epi": ["Alarme personnelle", "Gants"]},
            {"nom": "Urgence psychiatrique", "risk": "critique", "dangers": ["Agression", "Automutilation"], "epi": ["Alarme", "Formation OMEGA"]},
            {"nom": "Salle d'isolement", "risk": "critique", "dangers": ["Violence", "Contention"], "epi": ["Équipe intervention"]},
            {"nom": "Unité de soins longue durée psy", "risk": "eleve", "dangers": ["Violence", "TMS"], "epi": ["Alarme", "Gants"]},
        ],
        "roles": ["Infirmière psychiatrique", "PAB psychiatrie", "Éducateur spécialisé", "Psychiatre", "Travailleur social", "Agent de sécurité", "Chef d'unité psy"],
        "certs": ["OMEGA", "PDSB", "RCR", "Intervention de crise", "Gestion violence", "Contention"],
    },
    
    "623110": {
        "nom": "CHSLD - Soins infirmiers",
        "description": "Centres d'hébergement et de soins de longue durée",
        "risques": [
            {"desc": "TMS - transfert/mobilisation résident", "cat": "ergonomique", "prob": 5, "grav": 4},
            {"desc": "Violence résident (démence, Alzheimer)", "cat": "violence", "prob": 4, "grav": 3},
            {"desc": "Chute de même niveau", "cat": "chute", "prob": 4, "grav": 3},
            {"desc": "Exposition infections (grippe, gastro)", "cat": "biologique", "prob": 4, "grav": 3},
            {"desc": "Détresse psychologique/surcharge", "cat": "psychosocial", "prob": 5, "grav": 4},
            {"desc": "Piqûre lors soins (insuline)", "cat": "biologique", "prob": 3, "grav": 3},
            {"desc": "Blessure équipement (lève-personne)", "cat": "mecanique", "prob": 3, "grav": 4},
        ],
        "zones": [
            {"nom": "Chambre résident", "risk": "eleve", "dangers": ["TMS", "Violence", "Chute"], "epi": ["Gants", "Blouse"]},
            {"nom": "Salle de bain adaptée", "risk": "critique", "dangers": ["Chute", "TMS", "Humidité"], "epi": ["Chaussures antidérapantes", "Gants"]},
            {"nom": "Corridor/aire commune", "risk": "moyen", "dangers": ["Chute", "Errance"], "epi": ["Chaussures sécuritaires"]},
            {"nom": "Salle à manger", "risk": "moyen", "dangers": ["Étouffement", "Violence"], "epi": ["Formation dysphagie"]},
        ],
        "roles": ["PAB (Préposé aux bénéficiaires)", "Infirmière", "Infirmier auxiliaire", "Ergothérapeute", "Physiothérapeute", "Récréologue", "Chef d'unité CHSLD"],
        "certs": ["PDSB", "RCR", "Approche Alzheimer", "Prévention infections", "Lève-personne"],
    },
    
    "623210": {
        "nom": "Résidences pour personnes âgées (RPA)",
        "description": "Résidences privées pour aînés",
        "risques": [
            {"desc": "TMS - aide au transfert", "cat": "ergonomique", "prob": 4, "grav": 4},
            {"desc": "Chute de même niveau", "cat": "chute", "prob": 4, "grav": 3},
            {"desc": "Violence résident confus", "cat": "violence", "prob": 3, "grav": 3},
            {"desc": "Blessure équipement cuisine", "cat": "mecanique", "prob": 3, "grav": 3},
            {"desc": "Brûlure (cuisine, buanderie)", "cat": "thermique", "prob": 3, "grav": 3},
            {"desc": "Surcharge de travail", "cat": "psychosocial", "prob": 4, "grav": 3},
        ],
        "zones": [
            {"nom": "Appartement résident", "risk": "eleve", "dangers": ["TMS", "Chute"], "epi": ["Gants", "Chaussures"]},
            {"nom": "Cuisine collective", "risk": "eleve", "dangers": ["Brûlure", "Coupure", "Chute"], "epi": ["Tablier", "Gants cuisine"]},
            {"nom": "Buanderie", "risk": "moyen", "dangers": ["Chaleur", "Chimique"], "epi": ["Gants", "Tablier"]},
            {"nom": "Aires communes", "risk": "moyen", "dangers": ["Chute", "Violence"], "epi": ["Chaussures antidérapantes"]},
        ],
        "roles": ["Préposé aux résidents", "Cuisinier", "Aide-cuisinier", "Préposé entretien", "Infirmière RPA", "Directeur RPA"],
        "certs": ["PDSB", "RCR", "Hygiène alimentaire", "Prévention chutes"],
    },
    
    "621111": {
        "nom": "Cabinets de médecins",
        "description": "Cliniques médicales, GMF",
        "risques": [
            {"desc": "Piqûre aiguille/vaccination", "cat": "biologique", "prob": 3, "grav": 4},
            {"desc": "Exposition agents infectieux", "cat": "biologique", "prob": 3, "grav": 3},
            {"desc": "TMS - posture bureau prolongée", "cat": "ergonomique", "prob": 4, "grav": 3},
            {"desc": "Violence verbale patient mécontent", "cat": "violence", "prob": 3, "grav": 2},
            {"desc": "Stress/surcharge de travail", "cat": "psychosocial", "prob": 4, "grav": 3},
        ],
        "zones": [
            {"nom": "Salle d'examen", "risk": "eleve", "dangers": ["Piqûre", "Infection"], "epi": ["Gants", "Masque"]},
            {"nom": "Salle de prélèvements", "risk": "eleve", "dangers": ["Piqûre", "Sang"], "epi": ["Gants", "Lunettes", "Conteneur objets piquants"]},
            {"nom": "Réception/accueil", "risk": "moyen", "dangers": ["Violence verbale", "Infection"], "epi": ["Masque", "Plexiglas"]},
        ],
        "roles": ["Médecin", "Infirmière clinique", "Secrétaire médicale", "Technicienne prélèvements", "Gestionnaire clinique"],
        "certs": ["RCR", "SIMDUT", "Prévention infections", "Gestion stress"],
    },
    
    "621210": {
        "nom": "Cabinets de dentistes",
        "description": "Cliniques dentaires",
        "risques": [
            {"desc": "TMS - posture travail précis", "cat": "ergonomique", "prob": 5, "grav": 4},
            {"desc": "Piqûre aiguille/instrument", "cat": "biologique", "prob": 3, "grav": 4},
            {"desc": "Exposition aérosols (sang, salive)", "cat": "biologique", "prob": 4, "grav": 4},
            {"desc": "Bruit équipements dentaires", "cat": "bruit", "prob": 4, "grav": 3},
            {"desc": "Exposition mercure (amalgames)", "cat": "chimique", "prob": 2, "grav": 4},
            {"desc": "Exposition radiations (rayons X)", "cat": "physique", "prob": 2, "grav": 3},
        ],
        "zones": [
            {"nom": "Salle de traitement", "risk": "eleve", "dangers": ["Piqûre", "Aérosols", "TMS"], "epi": ["Masque N95", "Visière", "Gants"]},
            {"nom": "Salle de stérilisation", "risk": "eleve", "dangers": ["Piqûre", "Chimique", "Chaleur"], "epi": ["Gants épais", "Lunettes"]},
            {"nom": "Salle radiologie dentaire", "risk": "moyen", "dangers": ["Radiation"], "epi": ["Tablier plombé", "Dosimètre"]},
        ],
        "roles": ["Dentiste", "Hygiéniste dentaire", "Assistante dentaire", "Secrétaire dentaire", "Denturologiste"],
        "certs": ["RCR", "SIMDUT", "Prévention infections", "Radioprotection"],
    },
    
    "621610": {
        "nom": "Services de soins à domicile",
        "description": "Soins infirmiers et assistance à domicile",
        "risques": [
            {"desc": "TMS - soins sans équipement adapté", "cat": "ergonomique", "prob": 5, "grav": 4},
            {"desc": "Violence client/famille", "cat": "violence", "prob": 3, "grav": 4},
            {"desc": "Accident routier (déplacements)", "cat": "routier", "prob": 3, "grav": 5},
            {"desc": "Travail isolé (pas de secours)", "cat": "psychosocial", "prob": 4, "grav": 4},
            {"desc": "Exposition infections domicile", "cat": "biologique", "prob": 3, "grav": 3},
            {"desc": "Morsure animaux domestiques", "cat": "biologique", "prob": 3, "grav": 3},
            {"desc": "Conditions insalubres domicile", "cat": "biologique", "prob": 3, "grav": 3},
        ],
        "zones": [
            {"nom": "Domicile client", "risk": "eleve", "dangers": ["TMS", "Violence", "Isolement", "Animaux"], "epi": ["Gants", "Masque", "Téléphone"]},
            {"nom": "Véhicule personnel", "risk": "eleve", "dangers": ["Accident routier", "Météo"], "epi": ["Ceinture", "Kit urgence"]},
            {"nom": "CLSC/Bureau", "risk": "moyen", "dangers": ["Ergonomie"], "epi": ["Standard bureau"]},
        ],
        "roles": ["Infirmière SAD", "Auxiliaire familiale et sociale", "Ergothérapeute SAD", "Physiothérapeute SAD", "Travailleur social", "Coordonnateur SAD"],
        "certs": ["PDSB", "RCR", "Conduite sécuritaire", "Travail isolé", "Gestion violence"],
    },
    
    "624110": {
        "nom": "Services à l'enfance et à la jeunesse",
        "description": "Centres jeunesse, protection de l'enfance (DPJ)",
        "risques": [
            {"desc": "Violence/agression jeune", "cat": "violence", "prob": 4, "grav": 4},
            {"desc": "Morsure/griffure enfant", "cat": "biologique", "prob": 3, "grav": 3},
            {"desc": "Détresse psychologique (trauma vicariant)", "cat": "psychosocial", "prob": 5, "grav": 4},
            {"desc": "TMS - contention physique", "cat": "ergonomique", "prob": 4, "grav": 4},
            {"desc": "Menaces famille/parent", "cat": "violence", "prob": 3, "grav": 4},
            {"desc": "Accident lors transport jeune", "cat": "routier", "prob": 3, "grav": 4},
        ],
        "zones": [
            {"nom": "Unité de vie (centre jeunesse)", "risk": "critique", "dangers": ["Violence", "Contention", "Trauma"], "epi": ["Alarme", "Formation OMEGA"]},
            {"nom": "Bureau intervenant", "risk": "moyen", "dangers": ["Violence", "Menaces"], "epi": ["Alarme", "Protocole"]},
            {"nom": "Domicile famille (visite)", "risk": "eleve", "dangers": ["Violence", "Menaces", "Isolement"], "epi": ["Téléphone", "Protocole duo"]},
        ],
        "roles": ["Éducateur spécialisé", "Travailleur social DPJ", "Psychologue", "Agent de relations humaines", "Chef de service", "Agent de sécurité"],
        "certs": ["OMEGA", "RCR", "Intervention de crise", "Trauma vicariant", "Gestion agressivité"],
    },
    
    "624410": {
        "nom": "Garderies et services de garde",
        "description": "CPE, garderies, services de garde",
        "risques": [
            {"desc": "TMS - lever/porter enfants", "cat": "ergonomique", "prob": 5, "grav": 3},
            {"desc": "Exposition infections (rhume, gastro)", "cat": "biologique", "prob": 5, "grav": 2},
            {"desc": "Morsure/griffure enfant", "cat": "biologique", "prob": 3, "grav": 2},
            {"desc": "Chute de même niveau (jouets)", "cat": "chute", "prob": 4, "grav": 3},
            {"desc": "Bruit niveau élevé constant", "cat": "bruit", "prob": 5, "grav": 3},
            {"desc": "Violence parent mécontent", "cat": "violence", "prob": 2, "grav": 3},
            {"desc": "Épuisement professionnel", "cat": "psychosocial", "prob": 4, "grav": 3},
        ],
        "zones": [
            {"nom": "Local poupons", "risk": "eleve", "dangers": ["TMS", "Infections"], "epi": ["Gants", "Tablier"]},
            {"nom": "Local préscolaire", "risk": "moyen", "dangers": ["Bruit", "Chute", "Infections"], "epi": ["Bouchons disponibles"]},
            {"nom": "Cour extérieure", "risk": "moyen", "dangers": ["Chute", "Météo"], "epi": ["Chaussures sécuritaires"]},
            {"nom": "Cuisine/préparation repas", "risk": "moyen", "dangers": ["Coupure", "Brûlure", "Allergènes"], "epi": ["Gants", "Tablier"]},
        ],
        "roles": ["Éducatrice petite enfance", "Aide-éducatrice", "Responsable alimentation", "Directrice CPE", "Éducatrice spécialisée"],
        "certs": ["RCR pédiatrique", "Premiers soins", "Hygiène alimentaire", "SIMDUT"],
    },
}

# ORGANISATIONS DE SANTÉ QUÉBÉCOISES À CRÉER
ORGANISATIONS_SCIAN_62 = [
    # Hôpitaux généraux (622110)
    {"name": "CHUM - Centre hospitalier Université Montréal", "sector": "622110", "nb": 14000, "region": "Montréal"},
    {"name": "CUSM - Centre universitaire santé McGill", "sector": "622110", "nb": 16000, "region": "Montréal"},
    {"name": "CHU de Québec - Université Laval", "sector": "622110", "nb": 15000, "region": "Québec"},
    {"name": "CIUSSS Centre-Sud Montréal", "sector": "622110", "nb": 12000, "region": "Montréal"},
    {"name": "CISSS Montérégie-Centre", "sector": "622110", "nb": 8500, "region": "Montérégie"},
    {"name": "Hôpital Maisonneuve-Rosemont", "sector": "622110", "nb": 5500, "region": "Montréal"},
    
    # Hôpitaux psychiatriques (622310)
    {"name": "Institut universitaire en santé mentale de Montréal", "sector": "622310", "nb": 2800, "region": "Montréal"},
    {"name": "Institut universitaire en santé mentale de Québec", "sector": "622310", "nb": 1800, "region": "Québec"},
    {"name": "Hôpital Douglas", "sector": "622310", "nb": 1500, "region": "Montréal"},
    
    # CHSLD (623110)
    {"name": "CHSLD Champlain - Marie-Victorin", "sector": "623110", "nb": 450, "region": "Montréal"},
    {"name": "CHSLD St-Lambert-sur-le-Golf", "sector": "623110", "nb": 280, "region": "Montérégie"},
    {"name": "CHSLD Providence Notre-Dame-de-Lourdes", "sector": "623110", "nb": 320, "region": "Montréal"},
    {"name": "Vigi Santé - Réseau CHSLD", "sector": "623110", "nb": 2500, "region": "Montréal"},
    
    # RPA (623210)
    {"name": "Groupe Chartwell Québec", "sector": "623210", "nb": 3500, "region": "Montréal"},
    {"name": "Résidences Soleil", "sector": "623210", "nb": 2800, "region": "Montréal"},
    {"name": "Le Groupe Maurice", "sector": "623210", "nb": 2200, "region": "Montréal"},
    {"name": "Cogir Immobilier - RPA", "sector": "623210", "nb": 1800, "region": "Québec"},
    
    # Cliniques médicales (621111)
    {"name": "Groupe Santé Physimed", "sector": "621111", "nb": 350, "region": "Montréal"},
    {"name": "Clinique médicale 1851", "sector": "621111", "nb": 120, "region": "Montréal"},
    {"name": "GMF-U Laval", "sector": "621111", "nb": 85, "region": "Laval"},
    
    # Cliniques dentaires (621210)
    {"name": "Centres dentaires Lapointe", "sector": "621210", "nb": 450, "region": "Montréal"},
    {"name": "Clinique dentaire Bücco", "sector": "621210", "nb": 280, "region": "Québec"},
    
    # Soins à domicile (621610)
    {"name": "Bayshore Soins de santé", "sector": "621610", "nb": 650, "region": "Montréal"},
    {"name": "AlayaCare Québec", "sector": "621610", "nb": 380, "region": "Montréal"},
    {"name": "Coopérative de solidarité SABSA", "sector": "621610", "nb": 120, "region": "Québec"},
    
    # Centres jeunesse (624110)
    {"name": "Centre jeunesse de Montréal - Institut universitaire", "sector": "624110", "nb": 2200, "region": "Montréal"},
    {"name": "Centre jeunesse de Québec - Institut universitaire", "sector": "624110", "nb": 1500, "region": "Québec"},
    {"name": "Batshaw Youth and Family Centres", "sector": "624110", "nb": 800, "region": "Montréal"},
    
    # CPE et garderies (624410)
    {"name": "Association québécoise des CPE (réseau)", "sector": "624410", "nb": 5000, "region": "Québec"},
    {"name": "Garderies Montessori Québec", "sector": "624410", "nb": 350, "region": "Montréal"},
    {"name": "CPE Le Jardin des Merveilles", "sector": "624410", "nb": 85, "region": "Montréal"},
]

AGES = ["18-24", "25-34", "35-44", "45-54", "55-64"]


def populate_scian62():
    """Peuple SafetyGraph avec les secteurs SCIAN 62 (Soins de santé et assistance sociale)"""
    
    print("=" * 70)
    print("🏥💉 POPULATION SAFETYGRAPH - SCIAN 62")
    print("    Soins de santé et assistance sociale")
    print("    ⚠️ SECTEUR #1 EN LÉSIONS PROFESSIONNELLES AU QUÉBEC")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Secteurs: {len(SECTEURS_SCIAN_62)}")
    print(f"Organisations: {len(ORGANISATIONS_SCIAN_62)}")
    print("=" * 70)
    
    conn = SafetyGraphCartographyConnector()
    conn.connect()
    print("\n✅ Neo4j connecté")
    print(f"📊 Stats initiales: {conn.get_graph_stats()}\n")
    
    stats = {"orgs": 0, "zones": 0, "risks": 0, "persons": 0, "teams": 0, "roles": 0}
    
    # Créer organisations
    print("📦 Création des organisations SCIAN 62 (SANTÉ)...")
    org_map = {}
    for o in ORGANISATIONS_SCIAN_62:
        org = Organization(
            name=o["name"],
            sector_scian=o["sector"],
            nb_employes=o["nb"],
            region_ssq=o["region"]
        )
        oid = conn.inject_organization(org)
        org_map[o["name"]] = {"id": oid, "sector": o["sector"], "nb": o["nb"]}
        stats["orgs"] += 1
        sector_nom = SECTEURS_SCIAN_62[o["sector"]]["nom"]
        print(f"   ✅ {o['name'][:45]} ({o['sector']})")
    
    # Créer entités par organisation
    print("\n🏗️ Création des entités par organisation...")
    
    for name, info in org_map.items():
        oid, sector = info["id"], info["sector"]
        data = SECTEURS_SCIAN_62[sector]
        print(f"\n   🏥 {name[:50]}")
        print(f"      Secteur: {data['nom']}")
        
        # Rôles
        rids = []
        for r in data["roles"]:
            is_sup = any(x in r for x in ["Chef", "Directeur", "Coordonnateur", "Gestionnaire", "Responsable"])
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
        
        # Équipes (selon type d'établissement)
        tids = []
        if "622" in sector:  # Hôpitaux - 24/7
            equipes = ["Équipe Jour", "Équipe Soir", "Équipe Nuit", "Équipe Volante"]
        elif "623" in sector:  # CHSLD/RPA - 24/7
            equipes = ["Équipe Jour", "Équipe Soir", "Équipe Nuit"]
        elif "624110" in sector:  # Centres jeunesse
            equipes = ["Équipe Jour", "Équipe Soir", "Équipe Nuit", "Équipe Urgence"]
        else:
            equipes = ["Équipe Principale", "Équipe Soutien"]
            
        for t in equipes:
            team = Team(name=t, department=data["nom"][:25])
            tid = conn.inject_team(team)
            tids.append(tid)
            conn.create_relation(tid, oid, RelationType.APPARTIENT_A)
            stats["teams"] += 1
        print(f"      • {len(tids)} équipes")
        
        # Personnes (ratio basé sur taille - secteur santé = beaucoup d'employés)
        nb_persons = max(5, min(info["nb"] // 200, 50))
        for i in range(nb_persons):
            p = Person(
                matricule=f"SANTE62-{sector[-3:]}-{stats['persons']+1:04d}",
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
            # Exposition aux risques (85% du personnel de santé exposé)
            if rkids and i % 10 < 8:
                conn.create_relation(pid, rkids[i % len(rkids)], RelationType.EXPOSE_A)
        
        print(f"      • {nb_persons} personnes (anonymisées Loi 25)")
    
    # Résumé
    print("\n" + "=" * 70)
    print("📊 RÉSUMÉ POPULATION SCIAN 62 - SANTÉ")
    print("   ⚠️ 74,517 lésions professionnelles/an au Québec (2022)")
    print("=" * 70)
    print(f"   Organisations santé: {stats['orgs']}")
    print(f"   Zones de travail: {stats['zones']}")
    print(f"   Risques identifiés: {stats['risks']} (TMS, Violence, Infections)")
    print(f"   Équipes: {stats['teams']}")
    print(f"   Rôles/Professions: {stats['roles']}")
    print(f"   Personnes: {stats['persons']}")
    print(f"\n   Neo4j final: {conn.get_graph_stats()}")
    print("=" * 70)
    print("✅ POPULATION SCIAN 62 (SANTÉ) TERMINÉE!")
    print("=" * 70)
    
    conn.close()
    return stats


if __name__ == "__main__":
    populate_scian62()
