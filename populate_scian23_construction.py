#!/usr/bin/env python3
"""
🛡️ Script de Population Neo4j - Secteurs SCIAN 23
Construction
EDGY-AgenticX5 | SafetyGraph | Preventera

⚠️ SECTEUR LE PLUS MORTEL AU QUÉBEC
   ~700 chutes de hauteur/an sur chantiers
   ~4 décès/an en moyenne
   Tolérance Zéro CNESST: Chutes >3m, électrisation, effondrement

Basé sur les données CNESST 2024-2027:
- Priorités Tolérance Zéro: chutes hauteur, amiante, silice, électrisation
- Risques prédominants: ergonomiques, psychosociaux, bruit, chutes même niveau
- Code de sécurité pour les travaux de construction (CSTC)

Secteurs inclus:
- 236110: Construction résidentielle unifamiliale
- 236220: Construction commerciale et institutionnelle
- 237110: Construction de routes et autoroutes
- 237310: Construction de routes et ponts
- 238110: Travaux de coffrage à béton
- 238130: Travaux de charpenterie
- 238160: Travaux de couverture (toiture)
- 238170: Travaux de revêtement extérieur
- 238210: Travaux d'installation électrique
- 238220: Travaux de plomberie, chauffage
- 238320: Travaux de peinture
- 238910: Préparation de sites
- 238990: Travaux spécialisés divers
"""

import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

from src.cartography.connector import SafetyGraphCartographyConnector
from src.cartography.models import Organization, Person, Team, Role, Zone, Risk, RiskLevel, RelationType

# ============================================================================
# DONNÉES CNESST - SECTEURS SCIAN 23 (CONSTRUCTION)
# SECTEUR LE PLUS MORTEL AU QUÉBEC - TOLÉRANCE ZÉRO
# ~18,000 lésions/an | ~700 chutes hauteur/an | ~4 décès/an
# ============================================================================

SECTEURS_SCIAN_23 = {
    "236110": {
        "nom": "Construction résidentielle unifamiliale",
        "description": "Maisons unifamiliales, jumelées, en rangée",
        "risques": [
            {"desc": "Chute de hauteur >3m (toit, échafaudage)", "cat": "chute", "prob": 4, "grav": 5, "tz": True},
            {"desc": "Chute d'échelle ou escabeau", "cat": "chute", "prob": 4, "grav": 4},
            {"desc": "Électrisation/électrocution", "cat": "electrique", "prob": 3, "grav": 5, "tz": True},
            {"desc": "Effondrement structure/coffrage", "cat": "mecanique", "prob": 2, "grav": 5, "tz": True},
            {"desc": "Coupure scie circulaire/outils", "cat": "mecanique", "prob": 4, "grav": 4},
            {"desc": "TMS - manutention matériaux", "cat": "ergonomique", "prob": 5, "grav": 3},
            {"desc": "Exposition silice cristalline", "cat": "chimique", "prob": 3, "grav": 5, "tz": True},
            {"desc": "Bruit >85dB (outils électriques)", "cat": "bruit", "prob": 5, "grav": 3},
            {"desc": "Frappé par objet (chute matériaux)", "cat": "mecanique", "prob": 4, "grav": 4},
        ],
        "zones": [
            {"nom": "Toiture en construction", "risk": "critique", "dangers": ["Chute >3m", "Glissade", "Météo"], "epi": ["Harnais", "Ancrage", "Casque"]},
            {"nom": "Échafaudage", "risk": "critique", "dangers": ["Chute", "Effondrement"], "epi": ["Harnais", "Casque", "Bottes"]},
            {"nom": "Fondations/excavation", "risk": "eleve", "dangers": ["Effondrement", "Eau"], "epi": ["Casque", "Bottes", "Dossard"]},
            {"nom": "Intérieur chantier", "risk": "eleve", "dangers": ["Électricité", "Outils", "Trébuchement"], "epi": ["Casque", "Lunettes", "Bottes"]},
        ],
        "roles": ["Charpentier-menuisier", "Couvreur", "Électricien résidentiel", "Plombier", "Tireur de joints", "Contremaître", "Surintendant"],
        "certs": ["ASP Construction", "Travail hauteur", "SIMDUT", "Premiers soins", "Nacelle/échafaudage"],
    },
    
    "236220": {
        "nom": "Construction commerciale et institutionnelle",
        "description": "Édifices commerciaux, écoles, hôpitaux",
        "risques": [
            {"desc": "Chute de hauteur >3m (structure acier)", "cat": "chute", "prob": 4, "grav": 5, "tz": True},
            {"desc": "Effondrement structure/coffrage béton", "cat": "mecanique", "prob": 2, "grav": 5, "tz": True},
            {"desc": "Électrisation haute tension", "cat": "electrique", "prob": 2, "grav": 5, "tz": True},
            {"desc": "Écrasement grue/équipement lourd", "cat": "mecanique", "prob": 2, "grav": 5},
            {"desc": "Exposition amiante (rénovation)", "cat": "chimique", "prob": 2, "grav": 5, "tz": True},
            {"desc": "Exposition silice (béton, brique)", "cat": "chimique", "prob": 4, "grav": 5, "tz": True},
            {"desc": "Espace clos (réservoirs, puits)", "cat": "chimique", "prob": 2, "grav": 5, "tz": True},
            {"desc": "Travaux à chaud (soudure)", "cat": "thermique", "prob": 3, "grav": 4},
            {"desc": "Bruit chantier >90dB", "cat": "bruit", "prob": 5, "grav": 3},
        ],
        "zones": [
            {"nom": "Structure acier en hauteur", "risk": "critique", "dangers": ["Chute", "Vent", "Grue"], "epi": ["Harnais 100%", "Casque", "Gants"]},
            {"nom": "Coffrage béton", "risk": "critique", "dangers": ["Effondrement", "Béton", "Chute"], "epi": ["Casque", "Bottes", "Gants"]},
            {"nom": "Zone grue/levage", "risk": "critique", "dangers": ["Écrasement", "Charge suspendue"], "epi": ["Casque", "Dossard", "Radio"]},
            {"nom": "Excavation profonde", "risk": "critique", "dangers": ["Effondrement", "Espace clos"], "epi": ["Casque", "Détecteur gaz", "Harnais"]},
        ],
        "roles": ["Monteur acier structure", "Coffreur", "Ferblantier", "Grutier", "Soudeur", "Électricien industriel", "Surintendant", "Directeur de projet"],
        "certs": ["ASP Construction", "Travail hauteur", "Grue mobile", "Espace clos", "Soudage", "SIMDUT"],
    },
    
    "237310": {
        "nom": "Construction de routes et ponts",
        "description": "Routes, autoroutes, ponts, viaducs",
        "risques": [
            {"desc": "Frappé par véhicule (circulation)", "cat": "routier", "prob": 4, "grav": 5, "tz": True},
            {"desc": "Écrasement équipement lourd", "cat": "mecanique", "prob": 3, "grav": 5},
            {"desc": "Renversement machinerie", "cat": "mecanique", "prob": 2, "grav": 5},
            {"desc": "Chute pont/viaduc >3m", "cat": "chute", "prob": 3, "grav": 5, "tz": True},
            {"desc": "Exposition asphalte chaud", "cat": "chimique", "prob": 4, "grav": 3},
            {"desc": "Exposition silice (concassage)", "cat": "chimique", "prob": 4, "grav": 5, "tz": True},
            {"desc": "Vibrations corps entier", "cat": "ergonomique", "prob": 5, "grav": 3},
            {"desc": "Coup de chaleur (été)", "cat": "thermique", "prob": 4, "grav": 4},
            {"desc": "Bruit équipement >95dB", "cat": "bruit", "prob": 5, "grav": 3},
        ],
        "zones": [
            {"nom": "Chantier routier actif", "risk": "critique", "dangers": ["Circulation", "Équipement"], "epi": ["Dossard classe 3", "Casque", "Bottes"]},
            {"nom": "Structure pont/viaduc", "risk": "critique", "dangers": ["Chute", "Circulation"], "epi": ["Harnais", "Casque", "Dossard"]},
            {"nom": "Zone asphaltage", "risk": "eleve", "dangers": ["Chaleur", "Vapeurs", "Équipement"], "epi": ["Masque vapeurs", "Gants chaleur"]},
            {"nom": "Zone dynamitage", "risk": "critique", "dangers": ["Explosion", "Projection"], "epi": ["Abri", "Protection auditive"]},
        ],
        "roles": ["Opérateur pelle mécanique", "Opérateur niveleuse", "Opérateur rouleau", "Signaleur routier", "Arpenteur", "Contremaître génie civil", "Directeur de projet"],
        "certs": ["ASP Construction", "Signalisation routière", "Équipement lourd", "Dynamitage", "SIMDUT", "Premiers soins"],
    },
    
    "238110": {
        "nom": "Travaux de coffrage à béton",
        "description": "Coffrage, décoffrage, coulée de béton",
        "risques": [
            {"desc": "Effondrement coffrage", "cat": "mecanique", "prob": 3, "grav": 5, "tz": True},
            {"desc": "Chute lors décoffrage >3m", "cat": "chute", "prob": 4, "grav": 5, "tz": True},
            {"desc": "Écrasement panneau coffrage", "cat": "mecanique", "prob": 3, "grav": 4},
            {"desc": "Contact béton frais (brûlure chimique)", "cat": "chimique", "prob": 4, "grav": 3},
            {"desc": "Exposition silice béton", "cat": "chimique", "prob": 4, "grav": 5, "tz": True},
            {"desc": "TMS - manutention panneaux lourds", "cat": "ergonomique", "prob": 5, "grav": 4},
            {"desc": "Piqûre/perforation clous", "cat": "mecanique", "prob": 4, "grav": 3},
        ],
        "zones": [
            {"nom": "Zone coffrage vertical", "risk": "critique", "dangers": ["Chute", "Effondrement", "Écrasement"], "epi": ["Harnais", "Casque", "Gants"]},
            {"nom": "Zone coulée béton", "risk": "eleve", "dangers": ["Béton frais", "Pompe", "Vibration"], "epi": ["Bottes caoutchouc", "Gants", "Lunettes"]},
            {"nom": "Zone décoffrage", "risk": "critique", "dangers": ["Chute panneaux", "Clous"], "epi": ["Casque", "Gants", "Bottes"]},
        ],
        "roles": ["Coffreur", "Finisseur béton", "Opérateur pompe béton", "Ferrailleur", "Contremaître coffrage"],
        "certs": ["ASP Construction", "Travail hauteur", "Coffrage", "SIMDUT", "Premiers soins"],
    },
    
    "238160": {
        "nom": "Travaux de couverture (toiture)",
        "description": "Toiture, bardeaux, membrane, toit plat",
        "risques": [
            {"desc": "Chute de toit >3m", "cat": "chute", "prob": 5, "grav": 5, "tz": True},
            {"desc": "Glissade surface inclinée/mouillée", "cat": "chute", "prob": 4, "grav": 4},
            {"desc": "Brûlure bitume/torche", "cat": "thermique", "prob": 3, "grav": 4},
            {"desc": "Exposition vapeurs bitume", "cat": "chimique", "prob": 4, "grav": 3},
            {"desc": "Coup de chaleur toit noir été", "cat": "thermique", "prob": 4, "grav": 4},
            {"desc": "Exposition UV intense", "cat": "physique", "prob": 5, "grav": 3},
            {"desc": "Coupure métal/outils", "cat": "mecanique", "prob": 3, "grav": 3},
            {"desc": "Chute par trappe non protégée", "cat": "chute", "prob": 3, "grav": 5},
        ],
        "zones": [
            {"nom": "Toit incliné", "risk": "critique", "dangers": ["Chute", "Glissade", "Vent"], "epi": ["Harnais 100%", "Ancrage", "Chaussures antidérapantes"]},
            {"nom": "Toit plat périmètre", "risk": "critique", "dangers": ["Chute bord", "Trappe"], "epi": ["Harnais ou garde-corps", "Ligne avertissement"]},
            {"nom": "Zone torchage membrane", "risk": "eleve", "dangers": ["Brûlure", "Incendie", "Vapeurs"], "epi": ["Gants chaleur", "Extincteur", "Masque"]},
        ],
        "roles": ["Couvreur", "Poseur membrane", "Ferblantier toiture", "Aide-couvreur", "Contremaître toiture"],
        "certs": ["ASP Construction", "Travail hauteur", "Torchage", "Premiers soins", "Protection chutes"],
    },
    
    "238210": {
        "nom": "Travaux d'installation électrique",
        "description": "Électricité bâtiment, industriel, lignes",
        "risques": [
            {"desc": "Électrocution contact direct", "cat": "electrique", "prob": 3, "grav": 5, "tz": True},
            {"desc": "Arc électrique (flash)", "cat": "electrique", "prob": 2, "grav": 5, "tz": True},
            {"desc": "Chute échelle/nacelle", "cat": "chute", "prob": 3, "grav": 4},
            {"desc": "Brûlure électrique", "cat": "electrique", "prob": 3, "grav": 4},
            {"desc": "TMS - postures contraignantes", "cat": "ergonomique", "prob": 4, "grav": 3},
            {"desc": "Coupure fils/outils", "cat": "mecanique", "prob": 3, "grav": 2},
            {"desc": "Exposition amiante (rénovation)", "cat": "chimique", "prob": 2, "grav": 5, "tz": True},
        ],
        "zones": [
            {"nom": "Panneau électrique sous tension", "risk": "critique", "dangers": ["Électrocution", "Arc flash"], "epi": ["Gants isolants", "Visière arc", "Combinaison arc"]},
            {"nom": "Chambre électrique haute tension", "risk": "critique", "dangers": ["Électrocution", "Arc flash"], "epi": ["EPI arc flash complet", "Détecteur tension"]},
            {"nom": "Travail en hauteur électrique", "risk": "eleve", "dangers": ["Chute", "Électricité"], "epi": ["Harnais", "Gants isolants", "Casque"]},
        ],
        "roles": ["Électricien compagnon", "Électricien apprenti", "Électricien industriel", "Électricien lignes", "Contremaître électricité", "Maître électricien"],
        "certs": ["Licence électricien", "ASP Construction", "Arc flash", "Travail hauteur", "Cadenassage LOTO"],
    },
    
    "238220": {
        "nom": "Travaux de plomberie et chauffage",
        "description": "Plomberie, chauffage, climatisation, gaz",
        "risques": [
            {"desc": "Brûlure soudure/brasage", "cat": "thermique", "prob": 4, "grav": 3},
            {"desc": "Exposition gaz (fuite, CO)", "cat": "chimique", "prob": 2, "grav": 5},
            {"desc": "Espace clos (réservoirs, fosses)", "cat": "chimique", "prob": 2, "grav": 5, "tz": True},
            {"desc": "TMS - postures contraignantes", "cat": "ergonomique", "prob": 5, "grav": 3},
            {"desc": "Coupure tuyaux/outils", "cat": "mecanique", "prob": 3, "grav": 3},
            {"desc": "Exposition amiante (vieux bâtiments)", "cat": "chimique", "prob": 2, "grav": 5, "tz": True},
            {"desc": "Chute échelle/trappe", "cat": "chute", "prob": 3, "grav": 4},
        ],
        "zones": [
            {"nom": "Chaufferie/salle mécanique", "risk": "eleve", "dangers": ["Gaz", "Chaleur", "Bruit"], "epi": ["Détecteur CO", "Lunettes", "Protection auditive"]},
            {"nom": "Excavation conduite", "risk": "eleve", "dangers": ["Effondrement", "Eau"], "epi": ["Casque", "Bottes", "Dossard"]},
            {"nom": "Espace clos réservoir", "risk": "critique", "dangers": ["Asphyxie", "Gaz"], "epi": ["Détecteur 4 gaz", "Ventilation", "Harnais"]},
        ],
        "roles": ["Plombier compagnon", "Plombier apprenti", "Tuyauteur", "Frigoriste", "Mécanicien gaz", "Contremaître plomberie"],
        "certs": ["Licence plombier", "ASP Construction", "Gaz naturel", "Espace clos", "Brasage/soudage"],
    },
    
    "238910": {
        "nom": "Préparation de sites",
        "description": "Excavation, démolition, décontamination",
        "risques": [
            {"desc": "Effondrement excavation >1.2m", "cat": "mecanique", "prob": 3, "grav": 5, "tz": True},
            {"desc": "Écrasement équipement lourd", "cat": "mecanique", "prob": 3, "grav": 5},
            {"desc": "Exposition amiante (démolition)", "cat": "chimique", "prob": 3, "grav": 5, "tz": True},
            {"desc": "Exposition silice (concassage)", "cat": "chimique", "prob": 4, "grav": 5, "tz": True},
            {"desc": "Contact ligne électrique enfouie", "cat": "electrique", "prob": 2, "grav": 5, "tz": True},
            {"desc": "Contact conduite gaz", "cat": "chimique", "prob": 2, "grav": 5},
            {"desc": "Renversement machinerie pente", "cat": "mecanique", "prob": 2, "grav": 5},
            {"desc": "Bruit/vibrations", "cat": "bruit", "prob": 5, "grav": 3},
        ],
        "zones": [
            {"nom": "Excavation profonde >1.5m", "risk": "critique", "dangers": ["Effondrement", "Eau", "Gaz"], "epi": ["Casque", "Dossard", "Échelle évasion"]},
            {"nom": "Zone démolition", "risk": "critique", "dangers": ["Effondrement", "Amiante", "Projection"], "epi": ["Casque", "Masque P100", "Combinaison"]},
            {"nom": "Zone équipement lourd", "risk": "eleve", "dangers": ["Écrasement", "Angle mort"], "epi": ["Dossard classe 3", "Casque"]},
        ],
        "roles": ["Opérateur excavatrice", "Opérateur bulldozer", "Camionneur", "Démolisseur", "Technicien décontamination", "Contremaître terrassement"],
        "certs": ["ASP Construction", "Équipement lourd", "Amiante", "Info-Excavation", "SIMDUT"],
    },
    
    "238130": {
        "nom": "Travaux de charpenterie",
        "description": "Charpente bois, structure, finition",
        "risques": [
            {"desc": "Chute structure/échafaudage >3m", "cat": "chute", "prob": 4, "grav": 5, "tz": True},
            {"desc": "Coupure scie circulaire", "cat": "mecanique", "prob": 4, "grav": 4},
            {"desc": "Piqûre clou pneumatique", "cat": "mecanique", "prob": 3, "grav": 4},
            {"desc": "TMS - levage matériaux", "cat": "ergonomique", "prob": 5, "grav": 3},
            {"desc": "Projection éclats bois", "cat": "mecanique", "prob": 4, "grav": 3},
            {"desc": "Bruit outils >90dB", "cat": "bruit", "prob": 5, "grav": 3},
            {"desc": "Exposition poussière bois", "cat": "chimique", "prob": 4, "grav": 3},
        ],
        "zones": [
            {"nom": "Structure charpente hauteur", "risk": "critique", "dangers": ["Chute", "Instabilité"], "epi": ["Harnais", "Casque", "Gants"]},
            {"nom": "Zone coupe bois", "risk": "eleve", "dangers": ["Coupure", "Projection", "Bruit"], "epi": ["Lunettes", "Bouchons", "Gants"]},
            {"nom": "Plancher en construction", "risk": "eleve", "dangers": ["Chute ouverture", "Clous"], "epi": ["Casque", "Bottes semelle anti-perforation"]},
        ],
        "roles": ["Charpentier-menuisier", "Charpentier finition", "Poseur plancher", "Apprenti charpentier", "Contremaître charpente"],
        "certs": ["ASP Construction", "Travail hauteur", "Outils portatifs", "SIMDUT", "Premiers soins"],
    },
}

# ORGANISATIONS DE CONSTRUCTION QUÉBÉCOISES À CRÉER
ORGANISATIONS_SCIAN_23 = [
    # Construction résidentielle (236110)
    {"name": "Groupe Voyer", "sector": "236110", "nb": 450, "region": "Québec"},
    {"name": "Construction Trilec", "sector": "236110", "nb": 280, "region": "Montréal"},
    {"name": "Maisons Laprise", "sector": "236110", "nb": 180, "region": "Montérégie"},
    {"name": "Construction Bonneville", "sector": "236110", "nb": 150, "region": "Lanaudière"},
    
    # Construction commerciale/institutionnelle (236220)
    {"name": "Pomerleau", "sector": "236220", "nb": 3500, "region": "Québec"},
    {"name": "EBC inc.", "sector": "236220", "nb": 2800, "region": "Québec"},
    {"name": "Groupe Canam", "sector": "236220", "nb": 4200, "region": "Québec"},
    {"name": "PCL Construction", "sector": "236220", "nb": 1800, "region": "Montréal"},
    {"name": "Aecon Québec", "sector": "236220", "nb": 1500, "region": "Montréal"},
    {"name": "EllisDon Québec", "sector": "236220", "nb": 850, "region": "Montréal"},
    {"name": "Broccolini Construction", "sector": "236220", "nb": 650, "region": "Montréal"},
    
    # Routes et ponts (237310)
    {"name": "Eurovia Québec", "sector": "237310", "nb": 2200, "region": "Québec"},
    {"name": "Sintra (Colas)", "sector": "237310", "nb": 1800, "region": "Montréal"},
    {"name": "Construction DJL", "sector": "237310", "nb": 450, "region": "Montréal"},
    {"name": "Roxboro Excavation", "sector": "237310", "nb": 380, "region": "Montréal"},
    
    # Coffrage (238110)
    {"name": "Supermétal Structures", "sector": "238110", "nb": 450, "region": "Québec"},
    {"name": "Coffrages Synergy", "sector": "238110", "nb": 280, "region": "Montréal"},
    {"name": "Aluma Systems Québec", "sector": "238110", "nb": 180, "region": "Montréal"},
    
    # Toiture (238160)
    {"name": "Couvertures Montréal-Nord", "sector": "238160", "nb": 150, "region": "Montréal"},
    {"name": "Toitures Trois Étoiles", "sector": "238160", "nb": 120, "region": "Québec"},
    {"name": "Flynn Canada (toiture)", "sector": "238160", "nb": 280, "region": "Montréal"},
    
    # Électricité (238210)
    {"name": "Bélanger électrique", "sector": "238210", "nb": 380, "region": "Montréal"},
    {"name": "Énergir Services électriques", "sector": "238210", "nb": 280, "region": "Montréal"},
    {"name": "Plan Group électrique", "sector": "238210", "nb": 450, "region": "Montréal"},
    
    # Plomberie/Chauffage (238220)
    {"name": "Régis Côté et fils", "sector": "238220", "nb": 280, "region": "Québec"},
    {"name": "Plomberie Chauffage Normand", "sector": "238220", "nb": 180, "region": "Montréal"},
    {"name": "Énergir Services mécaniques", "sector": "238220", "nb": 350, "region": "Montréal"},
    
    # Préparation sites/excavation (238910)
    {"name": "Excavation Lafontaine", "sector": "238910", "nb": 280, "region": "Montréal"},
    {"name": "Démolition Panzini", "sector": "238910", "nb": 150, "region": "Montréal"},
    {"name": "Location Boisjoli", "sector": "238910", "nb": 180, "region": "Laurentides"},
    
    # Charpenterie (238130)
    {"name": "Charpentes Montmorency", "sector": "238130", "nb": 120, "region": "Québec"},
    {"name": "Nordic Structures", "sector": "238130", "nb": 280, "region": "Montréal"},
]

AGES = ["18-24", "25-34", "35-44", "45-54", "55-64"]


def populate_scian23():
    """Peuple SafetyGraph avec les secteurs SCIAN 23 (Construction)"""
    
    print("=" * 70)
    print("🏗️⚠️ POPULATION SAFETYGRAPH - SCIAN 23")
    print("    Construction")
    print("    ⚠️ SECTEUR LE PLUS MORTEL AU QUÉBEC")
    print("    🔴 TOLÉRANCE ZÉRO: Chutes >3m, électrisation, effondrement")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Secteurs: {len(SECTEURS_SCIAN_23)}")
    print(f"Organisations: {len(ORGANISATIONS_SCIAN_23)}")
    print("=" * 70)
    
    conn = SafetyGraphCartographyConnector()
    conn.connect()
    print("\n✅ Neo4j connecté")
    print(f"📊 Stats initiales: {conn.get_graph_stats()}\n")
    
    stats = {"orgs": 0, "zones": 0, "risks": 0, "persons": 0, "teams": 0, "roles": 0, "tz_risks": 0}
    
    # Créer organisations
    print("📦 Création des organisations SCIAN 23 (CONSTRUCTION)...")
    org_map = {}
    for o in ORGANISATIONS_SCIAN_23:
        org = Organization(
            name=o["name"],
            sector_scian=o["sector"],
            nb_employes=o["nb"],
            region_ssq=o["region"]
        )
        oid = conn.inject_organization(org)
        org_map[o["name"]] = {"id": oid, "sector": o["sector"], "nb": o["nb"]}
        stats["orgs"] += 1
        print(f"   ✅ {o['name'][:40]} ({o['sector']})")
    
    # Créer entités par organisation
    print("\n🏗️ Création des entités par organisation...")
    
    for name, info in org_map.items():
        oid, sector = info["id"], info["sector"]
        data = SECTEURS_SCIAN_23[sector]
        print(f"\n   🏗️ {name[:40]}")
        print(f"      Secteur: {data['nom']}")
        
        # Rôles
        rids = []
        for r in data["roles"]:
            is_sup = any(x in r for x in ["Contremaître", "Surintendant", "Directeur", "Maître"])
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
        
        # Risques (avec identification Tolérance Zéro)
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
        
        # Équipes (chantiers = quarts jour principalement)
        tids = []
        if info["nb"] > 500:
            equipes = ["Équipe Chantier A", "Équipe Chantier B", "Équipe Chantier C", "Équipe Atelier"]
        else:
            equipes = ["Équipe Chantier", "Équipe Maintenance"]
            
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
                matricule=f"CONST23-{sector[-3:]}-{stats['persons']+1:04d}",
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
            # Exposition aux risques (90% du personnel construction exposé)
            if rkids and i % 10 < 9:
                conn.create_relation(pid, rkids[i % len(rkids)], RelationType.EXPOSE_A)
        
        print(f"      • {nb_persons} personnes (anonymisées Loi 25)")
    
    # Résumé
    print("\n" + "=" * 70)
    print("📊 RÉSUMÉ POPULATION SCIAN 23 - CONSTRUCTION")
    print("   ⚠️ SECTEUR LE PLUS MORTEL AU QUÉBEC")
    print("=" * 70)
    print(f"   Organisations construction: {stats['orgs']}")
    print(f"   Zones de travail: {stats['zones']}")
    print(f"   Risques identifiés: {stats['risks']}")
    print(f"   🔴 Risques Tolérance Zéro: {stats['tz_risks']}")
    print(f"   Équipes: {stats['teams']}")
    print(f"   Rôles/Professions: {stats['roles']}")
    print(f"   Personnes: {stats['persons']}")
    print(f"\n   Neo4j final: {conn.get_graph_stats()}")
    print("=" * 70)
    print("✅ POPULATION SCIAN 23 (CONSTRUCTION) TERMINÉE!")
    print("=" * 70)
    
    conn.close()
    return stats


if __name__ == "__main__":
    populate_scian23()
