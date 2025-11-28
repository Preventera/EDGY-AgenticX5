#!/usr/bin/env python3
"""
🛡️ Script de Population Neo4j - Secteurs SCIAN 54
Services professionnels, scientifiques et techniques
EDGY-AgenticX5 | SafetyGraph | Preventera

💼 SECTEUR COL BLANC - Capital humain et expertise
   Ingénieurs, architectes, TI, laboratoires, consultants
   Risques psychosociaux, ergonomiques, chimiques (labo)

Secteurs inclus:
- 541110: Bureaux d'avocats
- 541212: Bureaux de comptables
- 541310: Services d'architecture
- 541330: Services de génie
- 541380: Laboratoires d'essais
- 541410: Design d'intérieur
- 541510: Conception de systèmes informatiques
- 541611: Conseils en gestion
- 541620: Conseils en environnement
- 541710: Recherche et développement en sciences physiques
- 541720: Recherche et développement en sciences sociales

Risques principaux:
- Ergonomiques (TMS bureau, écrans)
- Psychosociaux (stress, surcharge, harcèlement)
- Chimiques (laboratoires)
- Chantiers (ingénieurs terrain)
- Cybersécurité/stress TI
"""

import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

from src.cartography.connector import SafetyGraphCartographyConnector
from src.cartography.models import Organization, Person, Team, Role, Zone, Risk, RiskLevel, RelationType

# ============================================================================
# DONNÉES CNESST - SECTEURS SCIAN 54 (SERVICES PROFESSIONNELS)
# SECTEUR COL BLANC - CAPITAL HUMAIN
# ============================================================================

SECTEURS_SCIAN_54 = {
    "541110": {
        "nom": "Bureaux d'avocats",
        "description": "Services juridiques, cabinets d'avocats",
        "risques": [
            {"desc": "TMS - travail bureau prolongé", "cat": "ergonomique", "prob": 5, "grav": 3},
            {"desc": "Fatigue visuelle écrans", "cat": "ergonomique", "prob": 5, "grav": 2},
            {"desc": "Stress/surcharge travail", "cat": "psychosocial", "prob": 5, "grav": 3},
            {"desc": "Épuisement professionnel (burnout)", "cat": "psychosocial", "prob": 4, "grav": 4},
            {"desc": "Harcèlement psychologique", "cat": "psychosocial", "prob": 3, "grav": 4},
            {"desc": "Violence client mécontent", "cat": "violence", "prob": 2, "grav": 4},
            {"desc": "Chute même niveau (câbles, dossiers)", "cat": "chute", "prob": 3, "grav": 2},
        ],
        "zones": [
            {"nom": "Bureau avocat", "risk": "moyen", "dangers": ["TMS", "Stress", "Écrans"], "epi": []},
            {"nom": "Salle de réunion", "risk": "moyen", "dangers": ["Stress", "Conflit"], "epi": []},
            {"nom": "Palais de justice (déplacement)", "risk": "moyen", "dangers": ["Stress", "Violence"], "epi": []},
        ],
        "roles": ["Avocat associé", "Avocat salarié", "Parajuriste", "Adjoint juridique", "Réceptionniste", "Directeur administratif"],
        "certs": ["Barreau du Québec", "Ergonomie bureau", "Premiers soins"],
    },
    
    "541212": {
        "nom": "Bureaux de comptables",
        "description": "Services comptables, vérification, fiscalité",
        "risques": [
            {"desc": "TMS - travail bureau prolongé", "cat": "ergonomique", "prob": 5, "grav": 3},
            {"desc": "Fatigue visuelle écrans/chiffres", "cat": "ergonomique", "prob": 5, "grav": 2},
            {"desc": "Stress période fiscale intense", "cat": "psychosocial", "prob": 5, "grav": 4},
            {"desc": "Épuisement professionnel", "cat": "psychosocial", "prob": 4, "grav": 4},
            {"desc": "Heures supplémentaires excessives", "cat": "psychosocial", "prob": 5, "grav": 3},
            {"desc": "Sédentarité prolongée", "cat": "ergonomique", "prob": 5, "grav": 3},
        ],
        "zones": [
            {"nom": "Bureau comptable", "risk": "moyen", "dangers": ["TMS", "Écrans", "Stress"], "epi": []},
            {"nom": "Salle serveurs/archives", "risk": "moyen", "dangers": ["Poussière", "Ergonomie"], "epi": []},
            {"nom": "Client (déplacement)", "risk": "moyen", "dangers": ["Conduite", "Stress"], "epi": []},
        ],
        "roles": ["CPA associé", "CPA vérificateur", "Comptable", "Technicien comptable", "Fiscaliste", "Directeur associé"],
        "certs": ["CPA Québec", "Ergonomie bureau", "Premiers soins"],
    },
    
    "541310": {
        "nom": "Services d'architecture",
        "description": "Bureaux d'architectes, design architectural",
        "risques": [
            {"desc": "TMS - travail bureau/dessin prolongé", "cat": "ergonomique", "prob": 5, "grav": 3},
            {"desc": "Fatigue visuelle écrans/plans", "cat": "ergonomique", "prob": 5, "grav": 2},
            {"desc": "Stress délais/clients", "cat": "psychosocial", "prob": 4, "grav": 3},
            {"desc": "Chute chantier (visite)", "cat": "chute", "prob": 3, "grav": 4},
            {"desc": "Exposition poussière chantier", "cat": "chimique", "prob": 3, "grav": 2},
            {"desc": "Accident véhicule (déplacements)", "cat": "routier", "prob": 3, "grav": 4},
        ],
        "zones": [
            {"nom": "Bureau/Atelier design", "risk": "moyen", "dangers": ["TMS", "Écrans", "Maquettes"], "epi": []},
            {"nom": "Chantier construction (visite)", "risk": "eleve", "dangers": ["Chute", "Poussière", "Équipement"], "epi": ["Casque", "Bottes", "Dossard"]},
            {"nom": "Salle de réunion client", "risk": "moyen", "dangers": ["Stress"], "epi": []},
        ],
        "roles": ["Architecte principal", "Architecte", "Technologue architecture", "Dessinateur CAD", "Directeur de projet", "Stagiaire architecture"],
        "certs": ["OAQ (Ordre architectes)", "ASP Construction (visites)", "Ergonomie", "Premiers soins"],
    },
    
    "541330": {
        "nom": "Services de génie",
        "description": "Bureaux d'ingénieurs, génie-conseil",
        "risques": [
            {"desc": "Chute chantier (inspection)", "cat": "chute", "prob": 3, "grav": 5},
            {"desc": "TMS - travail bureau prolongé", "cat": "ergonomique", "prob": 5, "grav": 3},
            {"desc": "Exposition bruit chantier", "cat": "bruit", "prob": 3, "grav": 3},
            {"desc": "Exposition poussière/amiante (inspection)", "cat": "chimique", "prob": 2, "grav": 4},
            {"desc": "Électrisation (inspection électrique)", "cat": "electrique", "prob": 2, "grav": 5},
            {"desc": "Stress délais/responsabilité", "cat": "psychosocial", "prob": 4, "grav": 3},
            {"desc": "Accident véhicule (déplacements)", "cat": "routier", "prob": 3, "grav": 4},
            {"desc": "Espace clos (inspection)", "cat": "chimique", "prob": 2, "grav": 5},
        ],
        "zones": [
            {"nom": "Bureau ingénieur", "risk": "moyen", "dangers": ["TMS", "Écrans", "Stress"], "epi": []},
            {"nom": "Chantier construction (inspection)", "risk": "critique", "dangers": ["Chute", "Électricité", "Écrasement"], "epi": ["Casque", "Bottes", "Dossard", "Lunettes"]},
            {"nom": "Usine client (inspection)", "risk": "eleve", "dangers": ["Bruit", "Chimique", "Mécanique"], "epi": ["Casque", "Lunettes", "Bouchons"]},
            {"nom": "Laboratoire essais", "risk": "eleve", "dangers": ["Chimique", "Mécanique"], "epi": ["Sarrau", "Lunettes", "Gants"]},
        ],
        "roles": ["Ingénieur principal", "Ingénieur de projet", "Ingénieur junior", "Technicien génie civil", "Dessinateur CAD", "Chargé de projet", "Directeur technique"],
        "certs": ["OIQ (Ordre ingénieurs)", "ASP Construction", "Espace clos", "Cadenassage", "SIMDUT", "Premiers soins"],
    },
    
    "541380": {
        "nom": "Laboratoires d'essais",
        "description": "Essais matériaux, analyses, contrôle qualité",
        "risques": [
            {"desc": "Exposition produits chimiques", "cat": "chimique", "prob": 4, "grav": 4},
            {"desc": "Brûlure chimique (acides, bases)", "cat": "chimique", "prob": 3, "grav": 4},
            {"desc": "Coupure verrerie laboratoire", "cat": "mecanique", "prob": 4, "grav": 3},
            {"desc": "Inhalation vapeurs toxiques", "cat": "chimique", "prob": 3, "grav": 4},
            {"desc": "Incendie/explosion solvants", "cat": "chimique", "prob": 2, "grav": 5},
            {"desc": "Exposition radiation (rayons X)", "cat": "physique", "prob": 2, "grav": 4},
            {"desc": "TMS - manipulation échantillons", "cat": "ergonomique", "prob": 4, "grav": 3},
            {"desc": "Écrasement presse/équipement essai", "cat": "mecanique", "prob": 2, "grav": 5},
        ],
        "zones": [
            {"nom": "Laboratoire chimie", "risk": "critique", "dangers": ["Chimique", "Incendie", "Verrerie"], "epi": ["Sarrau", "Lunettes", "Gants nitrile", "Hotte"]},
            {"nom": "Laboratoire essais mécaniques", "risk": "eleve", "dangers": ["Écrasement", "Projection", "Bruit"], "epi": ["Lunettes", "Gants", "Protection auditive"]},
            {"nom": "Salle rayons X", "risk": "critique", "dangers": ["Radiation"], "epi": ["Dosimètre", "Tablier plomb"]},
            {"nom": "Chantier prélèvement", "risk": "eleve", "dangers": ["Chute", "Circulation"], "epi": ["Casque", "Dossard", "Bottes"]},
        ],
        "roles": ["Chimiste", "Technicien laboratoire", "Ingénieur matériaux", "Technicien prélèvement", "Directeur laboratoire", "Responsable qualité"],
        "certs": ["SIMDUT avancé", "Radioprotection", "Manipulation produits dangereux", "Premiers soins", "ASP Construction"],
    },
    
    "541510": {
        "nom": "Conception de systèmes informatiques",
        "description": "Services TI, développement logiciel, cybersécurité",
        "risques": [
            {"desc": "TMS - travail écran prolongé", "cat": "ergonomique", "prob": 5, "grav": 3},
            {"desc": "Fatigue visuelle écrans", "cat": "ergonomique", "prob": 5, "grav": 2},
            {"desc": "Sédentarité prolongée", "cat": "ergonomique", "prob": 5, "grav": 3},
            {"desc": "Stress/surcharge cognitive", "cat": "psychosocial", "prob": 5, "grav": 3},
            {"desc": "Épuisement professionnel (burnout)", "cat": "psychosocial", "prob": 4, "grav": 4},
            {"desc": "Stress astreinte/urgences 24/7", "cat": "psychosocial", "prob": 4, "grav": 3},
            {"desc": "Isolement télétravail", "cat": "psychosocial", "prob": 4, "grav": 3},
            {"desc": "Électrisation salle serveurs", "cat": "electrique", "prob": 2, "grav": 4},
        ],
        "zones": [
            {"nom": "Bureau développeur", "risk": "moyen", "dangers": ["TMS", "Écrans", "Sédentarité"], "epi": []},
            {"nom": "Salle serveurs/Data center", "risk": "eleve", "dangers": ["Électricité", "Bruit", "Froid"], "epi": ["Protection auditive"]},
            {"nom": "Domicile (télétravail)", "risk": "moyen", "dangers": ["Ergonomie", "Isolement"], "epi": []},
        ],
        "roles": ["Développeur logiciel", "Analyste programmeur", "Architecte TI", "Administrateur systèmes", "Spécialiste cybersécurité", "Chef d'équipe", "Directeur TI"],
        "certs": ["Certifications TI (AWS, Azure, etc.)", "Ergonomie bureau", "Premiers soins"],
    },
    
    "541611": {
        "nom": "Conseils en gestion",
        "description": "Consultants en gestion, stratégie, RH",
        "risques": [
            {"desc": "TMS - travail bureau/portable", "cat": "ergonomique", "prob": 5, "grav": 3},
            {"desc": "Stress délais/performance", "cat": "psychosocial", "prob": 5, "grav": 3},
            {"desc": "Épuisement professionnel", "cat": "psychosocial", "prob": 4, "grav": 4},
            {"desc": "Fatigue déplacements fréquents", "cat": "psychosocial", "prob": 4, "grav": 3},
            {"desc": "Accident véhicule/avion", "cat": "routier", "prob": 3, "grav": 4},
            {"desc": "Décalage horaire (mandats internationaux)", "cat": "psychosocial", "prob": 3, "grav": 2},
            {"desc": "Conflit client/consultant", "cat": "psychosocial", "prob": 3, "grav": 3},
        ],
        "zones": [
            {"nom": "Bureau consultant", "risk": "moyen", "dangers": ["TMS", "Stress"], "epi": []},
            {"nom": "Site client", "risk": "moyen", "dangers": ["Stress", "Ergonomie variable"], "epi": []},
            {"nom": "Déplacement (voiture, avion)", "risk": "eleve", "dangers": ["Accident", "Fatigue"], "epi": []},
        ],
        "roles": ["Consultant senior", "Consultant", "Analyste d'affaires", "Gestionnaire de projet", "Associé", "Directeur pratique"],
        "certs": ["PMP", "Lean Six Sigma", "Ergonomie", "Premiers soins"],
    },
    
    "541620": {
        "nom": "Conseils en environnement",
        "description": "Consultants environnement, études d'impact, décontamination",
        "risques": [
            {"desc": "Exposition contaminants sol (terrain)", "cat": "chimique", "prob": 3, "grav": 4},
            {"desc": "Exposition amiante (bâtiments)", "cat": "chimique", "prob": 2, "grav": 5, "tz": True},
            {"desc": "Chute terrain accidenté", "cat": "chute", "prob": 3, "grav": 3},
            {"desc": "Morsure/piqûre (terrain)", "cat": "biologique", "prob": 3, "grav": 3},
            {"desc": "Exposition intempéries", "cat": "thermique", "prob": 4, "grav": 2},
            {"desc": "Accident véhicule (déplacements)", "cat": "routier", "prob": 3, "grav": 4},
            {"desc": "TMS - bureau/prélèvements", "cat": "ergonomique", "prob": 4, "grav": 3},
            {"desc": "Noyade cours d'eau (échantillonnage)", "cat": "physique", "prob": 2, "grav": 5},
        ],
        "zones": [
            {"nom": "Bureau consultant", "risk": "moyen", "dangers": ["TMS", "Écrans"], "epi": []},
            {"nom": "Site contaminé", "risk": "critique", "dangers": ["Chimique", "Sol contaminé"], "epi": ["Combinaison Tyvek", "Masque", "Gants", "Bottes"]},
            {"nom": "Terrain naturel (étude)", "risk": "eleve", "dangers": ["Chute", "Animaux", "Intempéries"], "epi": ["Bottes", "Chapeau", "Insectifuge"]},
            {"nom": "Cours d'eau (échantillonnage)", "risk": "eleve", "dangers": ["Noyade", "Glissade"], "epi": ["VFI", "Bottes cuissardes"]},
        ],
        "roles": ["Consultant environnement", "Biologiste", "Géologue", "Technicien environnement", "Chargé de projet", "Directeur environnement"],
        "certs": ["SIMDUT", "ASP Construction", "Amiante", "Premiers soins", "Sauvetage aquatique"],
    },
    
    "541710": {
        "nom": "Recherche et développement en sciences physiques",
        "description": "R&D, laboratoires de recherche, innovation",
        "risques": [
            {"desc": "Exposition produits chimiques recherche", "cat": "chimique", "prob": 4, "grav": 4},
            {"desc": "Exposition radiation (laboratoire)", "cat": "physique", "prob": 2, "grav": 5},
            {"desc": "Brûlure chimique/thermique", "cat": "chimique", "prob": 3, "grav": 4},
            {"desc": "Incendie/explosion (solvants, gaz)", "cat": "chimique", "prob": 2, "grav": 5},
            {"desc": "Coupure verrerie/équipement", "cat": "mecanique", "prob": 4, "grav": 3},
            {"desc": "Exposition laser haute puissance", "cat": "physique", "prob": 2, "grav": 4},
            {"desc": "Stress recherche/publications", "cat": "psychosocial", "prob": 4, "grav": 3},
            {"desc": "Exposition pathogènes (bio)", "cat": "biologique", "prob": 2, "grav": 5},
        ],
        "zones": [
            {"nom": "Laboratoire chimie R&D", "risk": "critique", "dangers": ["Chimique", "Incendie", "Explosion"], "epi": ["Sarrau", "Lunettes", "Gants", "Hotte"]},
            {"nom": "Laboratoire physique/laser", "risk": "critique", "dangers": ["Laser", "Radiation", "Électricité"], "epi": ["Lunettes laser", "Dosimètre"]},
            {"nom": "Laboratoire biologie", "risk": "critique", "dangers": ["Pathogènes", "Biohazard"], "epi": ["Sarrau", "Gants", "Masque", "Hotte bio"]},
            {"nom": "Bureau chercheur", "risk": "moyen", "dangers": ["TMS", "Stress"], "epi": []},
        ],
        "roles": ["Chercheur principal", "Chercheur", "Associé de recherche", "Technicien laboratoire R&D", "Directeur R&D", "Stagiaire postdoctoral"],
        "certs": ["SIMDUT avancé", "Biosécurité", "Radioprotection", "Laser", "Premiers soins"],
    },
}

# ORGANISATIONS SERVICES PROFESSIONNELS QUÉBÉCOISES
ORGANISATIONS_SCIAN_54 = [
    # Bureaux d'avocats (541110)
    {"name": "Norton Rose Fulbright (Montréal)", "sector": "541110", "nb": 450, "region": "Montréal"},
    {"name": "McCarthy Tétrault (Montréal)", "sector": "541110", "nb": 380, "region": "Montréal"},
    {"name": "Fasken (Montréal)", "sector": "541110", "nb": 350, "region": "Montréal"},
    {"name": "Lavery Avocats", "sector": "541110", "nb": 280, "region": "Montréal"},
    
    # Bureaux comptables (541212)
    {"name": "Deloitte Québec", "sector": "541212", "nb": 1800, "region": "Montréal"},
    {"name": "PwC Québec", "sector": "541212", "nb": 1500, "region": "Montréal"},
    {"name": "KPMG Québec", "sector": "541212", "nb": 1200, "region": "Montréal"},
    {"name": "EY Québec", "sector": "541212", "nb": 1100, "region": "Montréal"},
    {"name": "Raymond Chabot Grant Thornton", "sector": "541212", "nb": 850, "region": "Montréal"},
    {"name": "MNP Québec", "sector": "541212", "nb": 450, "region": "Montréal"},
    
    # Architecture (541310)
    {"name": "Lemay (architecture)", "sector": "541310", "nb": 320, "region": "Montréal"},
    {"name": "Provencher_Roy", "sector": "541310", "nb": 180, "region": "Montréal"},
    {"name": "NEUF architect(e)s", "sector": "541310", "nb": 150, "region": "Montréal"},
    {"name": "Groupe A / Annexe U", "sector": "541310", "nb": 120, "region": "Québec"},
    
    # Services de génie (541330)
    {"name": "WSP Québec", "sector": "541330", "nb": 4500, "region": "Montréal"},
    {"name": "SNC-Lavalin (ingénierie)", "sector": "541330", "nb": 3500, "region": "Montréal"},
    {"name": "Stantec Québec", "sector": "541330", "nb": 1800, "region": "Montréal"},
    {"name": "CIMA+", "sector": "541330", "nb": 1500, "region": "Québec"},
    {"name": "Norda Stelo", "sector": "541330", "nb": 850, "region": "Québec"},
    {"name": "Tetra Tech Québec", "sector": "541330", "nb": 650, "region": "Montréal"},
    {"name": "EXP Services", "sector": "541330", "nb": 550, "region": "Montréal"},
    {"name": "Englobe", "sector": "541330", "nb": 480, "region": "Québec"},
    
    # Laboratoires d'essais (541380)
    {"name": "Bureau Veritas Québec", "sector": "541380", "nb": 280, "region": "Montréal"},
    {"name": "SGS Canada (Québec)", "sector": "541380", "nb": 220, "region": "Montréal"},
    {"name": "Maxxam Analytics (Montréal)", "sector": "541380", "nb": 150, "region": "Montréal"},
    {"name": "AGAT Laboratories", "sector": "541380", "nb": 120, "region": "Montréal"},
    
    # Services TI (541510)
    {"name": "CGI Québec", "sector": "541510", "nb": 5500, "region": "Montréal"},
    {"name": "Ubisoft Montréal", "sector": "541510", "nb": 4000, "region": "Montréal"},
    {"name": "Desjardins TI", "sector": "541510", "nb": 2500, "region": "Lévis"},
    {"name": "Intact Lab", "sector": "541510", "nb": 850, "region": "Montréal"},
    {"name": "Coveo", "sector": "541510", "nb": 650, "region": "Québec"},
    {"name": "Lightspeed", "sector": "541510", "nb": 580, "region": "Montréal"},
    {"name": "GSoft", "sector": "541510", "nb": 350, "region": "Montréal"},
    
    # Conseils en gestion (541611)
    {"name": "McKinsey & Company (Montréal)", "sector": "541611", "nb": 180, "region": "Montréal"},
    {"name": "BCG (Montréal)", "sector": "541611", "nb": 150, "region": "Montréal"},
    {"name": "Accenture Québec", "sector": "541611", "nb": 850, "region": "Montréal"},
    {"name": "Capgemini Québec", "sector": "541611", "nb": 450, "region": "Montréal"},
    
    # Conseils environnement (541620)
    {"name": "WSP Environnement", "sector": "541620", "nb": 450, "region": "Montréal"},
    {"name": "Englobe (environnement)", "sector": "541620", "nb": 380, "region": "Québec"},
    {"name": "Groupe Synergis", "sector": "541620", "nb": 180, "region": "Montréal"},
    {"name": "Sanexen (environnement)", "sector": "541620", "nb": 280, "region": "Montréal"},
    
    # R&D Sciences physiques (541710)
    {"name": "CNRC Boucherville", "sector": "541710", "nb": 450, "region": "Montérégie"},
    {"name": "IREQ Hydro-Québec", "sector": "541710", "nb": 380, "region": "Varennes"},
    {"name": "INO (Institut national optique)", "sector": "541710", "nb": 280, "region": "Québec"},
    {"name": "CRIQ", "sector": "541710", "nb": 180, "region": "Québec"},
]

AGES = ["18-24", "25-34", "35-44", "45-54", "55-64"]


def populate_scian54():
    """Peuple SafetyGraph avec les secteurs SCIAN 54 (Services professionnels)"""
    
    print("=" * 70)
    print("💼🔬 POPULATION SAFETYGRAPH - SCIAN 54")
    print("    Services professionnels, scientifiques et techniques")
    print("    💼 Ingénieurs, architectes, TI, laboratoires, consultants")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Secteurs: {len(SECTEURS_SCIAN_54)}")
    print(f"Organisations: {len(ORGANISATIONS_SCIAN_54)}")
    print("=" * 70)
    
    conn = SafetyGraphCartographyConnector()
    conn.connect()
    print("\n✅ Neo4j connecté")
    print(f"📊 Stats initiales: {conn.get_graph_stats()}\n")
    
    stats = {"orgs": 0, "zones": 0, "risks": 0, "persons": 0, "teams": 0, "roles": 0}
    
    # Créer organisations
    print("📦 Création des organisations SCIAN 54 (SERVICES PROFESSIONNELS)...")
    org_map = {}
    for o in ORGANISATIONS_SCIAN_54:
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
        data = SECTEURS_SCIAN_54[sector]
        
        # Emoji selon secteur
        if sector == "541110":
            emoji = "⚖️"
        elif sector == "541212":
            emoji = "📊"
        elif sector == "541310":
            emoji = "🏛️"
        elif sector == "541330":
            emoji = "🔧"
        elif sector == "541380":
            emoji = "🧪"
        elif sector == "541510":
            emoji = "💻"
        elif sector == "541611":
            emoji = "📈"
        elif sector == "541620":
            emoji = "🌿"
        else:
            emoji = "🔬"
            
        print(f"\n   {emoji} {name[:40]}")
        print(f"      Secteur: {data['nom']}")
        
        # Rôles
        rids = []
        for r in data["roles"]:
            is_sup = any(x in r for x in ["Principal", "Associé", "Directeur", "Chef", "Senior"])
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
        
        # Équipes (professionnels = structure par département)
        tids = []
        if info["nb"] > 500:
            equipes = ["Équipe Projets", "Équipe Support", "Équipe Admin", "Équipe Direction"]
        else:
            equipes = ["Équipe Principale", "Équipe Admin"]
            
        for t in equipes:
            team = Team(name=t, department=data["nom"][:25])
            tid = conn.inject_team(team)
            tids.append(tid)
            conn.create_relation(tid, oid, RelationType.APPARTIENT_A)
            stats["teams"] += 1
        print(f"      • {len(tids)} équipes")
        
        # Personnes (professionnels = plus de 25-44 ans)
        nb_persons = max(5, min(info["nb"] // 100, 35))
        for i in range(nb_persons):
            # Distribution âge typique professionnels
            age_dist = ["25-34", "25-34", "35-44", "35-44", "45-54"]
            p = Person(
                matricule=f"PROF54-{sector[-3:]}-{stats['persons']+1:04d}",
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
            if rkids and i % 10 < 7:
                conn.create_relation(pid, rkids[i % len(rkids)], RelationType.EXPOSE_A)
        
        print(f"      • {nb_persons} personnes (anonymisées Loi 25)")
    
    # Résumé
    print("\n" + "=" * 70)
    print("📊 RÉSUMÉ POPULATION SCIAN 54 - SERVICES PROFESSIONNELS")
    print("   💼 Ingénieurs, TI, Laboratoires, Consultants")
    print("=" * 70)
    print(f"   Organisations services professionnels: {stats['orgs']}")
    print(f"   Zones de travail: {stats['zones']}")
    print(f"   Risques identifiés: {stats['risks']}")
    print(f"   Équipes: {stats['teams']}")
    print(f"   Rôles/Professions: {stats['roles']}")
    print(f"   Personnes: {stats['persons']}")
    print(f"\n   Neo4j final: {conn.get_graph_stats()}")
    print("=" * 70)
    print("✅ POPULATION SCIAN 54 (SERVICES PROFESSIONNELS) TERMINÉE!")
    print("=" * 70)
    
    conn.close()
    return stats


if __name__ == "__main__":
    populate_scian54()
