#!/usr/bin/env python3
"""
🛡️ SafetyGraph - Générateur Automatique de Requêtes Cypher
EDGY-AgenticX5 | Preventera | GenAISafety

Génère automatiquement des requêtes Cypher personnalisées selon:
- Le code SCIAN de l'entreprise
- Le profil de risques CNESST du secteur
- La taille de l'entreprise
- Les priorités réglementaires

Usage:
    python cypher_generator.py --scian 236 --output construction.cypher
    python cypher_generator.py --scian 621 --employes 500 --output sante.cypher
    python cypher_generator.py --list-sectors
    python cypher_generator.py --all --output-dir ./requetes/

Auteur: GenAISafety / Preventera
Date: Novembre 2025
"""

import argparse
import os
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, field


# ============================================================================
# PROFILS DE RISQUES CNESST PAR SECTEUR SCIAN
# ============================================================================

@dataclass
class ProfilRisque:
    """Profil de risques CNESST pour un secteur"""
    scian: str
    nom: str
    nom_court: str
    lesions_annuelles: int
    risques_prioritaires: List[Dict]  # [{"categorie": str, "pct": int, "priorite": str}]
    certifications_requises: List[str]
    epi_critiques: List[str]
    mots_cles_risques: List[str]
    reglementations: List[str]


# Base de données des profils CNESST par secteur
PROFILS_CNESST: Dict[str, ProfilRisque] = {
    
    # =========================================================================
    # CONSTRUCTION (SCIAN 236-238)
    # =========================================================================
    "236": ProfilRisque(
        scian="236",
        nom="Construction de bâtiments",
        nom_court="Construction",
        lesions_annuelles=18000,
        risques_prioritaires=[
            {"categorie": "chute", "pct": 28, "priorite": "CRITIQUE", "emoji": "🪜"},
            {"categorie": "mecanique", "pct": 22, "priorite": "CRITIQUE", "emoji": "🔧"},
            {"categorie": "electrique", "pct": 12, "priorite": "CRITIQUE", "emoji": "⚡"},
            {"categorie": "ergonomique", "pct": 18, "priorite": "ELEVE", "emoji": "🦴"},
            {"categorie": "bruit", "pct": 8, "priorite": "MOYEN", "emoji": "🔊"},
            {"categorie": "chimique", "pct": 7, "priorite": "ELEVE", "emoji": "🧪"},
            {"categorie": "thermique", "pct": 5, "priorite": "MOYEN", "emoji": "☀️"},
        ],
        certifications_requises=["ASP Construction", "Travail en hauteur", "LOTO", "SIMDUT", "Premiers soins", "Espace clos"],
        epi_critiques=["casque", "harnais", "lunettes", "gants", "bottes", "gilet haute visibilité"],
        mots_cles_risques=["chute", "hauteur", "échafaud", "échelle", "toiture", "excavation", "grue", "électrique", "silice", "amiante"],
        reglementations=["RSST", "Code de sécurité construction", "ASP Construction", "CNESST"]
    ),
    
    "237": ProfilRisque(
        scian="237",
        nom="Travaux de génie civil",
        nom_court="Génie civil",
        lesions_annuelles=8000,
        risques_prioritaires=[
            {"categorie": "mecanique", "pct": 30, "priorite": "CRITIQUE", "emoji": "🔧"},
            {"categorie": "chute", "pct": 20, "priorite": "CRITIQUE", "emoji": "🪜"},
            {"categorie": "ensevelissement", "pct": 15, "priorite": "CRITIQUE", "emoji": "⛏️"},
            {"categorie": "electrique", "pct": 10, "priorite": "ELEVE", "emoji": "⚡"},
            {"categorie": "ergonomique", "pct": 12, "priorite": "ELEVE", "emoji": "🦴"},
            {"categorie": "chimique", "pct": 8, "priorite": "MOYEN", "emoji": "🧪"},
        ],
        certifications_requises=["ASP Construction", "Excavation", "Espace clos", "Signalisation routière", "SIMDUT"],
        epi_critiques=["casque", "gilet haute visibilité", "bottes", "gants", "protecteurs auditifs"],
        mots_cles_risques=["excavation", "tranchée", "ensevelissement", "route", "pont", "égout", "circulation"],
        reglementations=["RSST", "Code de sécurité construction", "MTQ"]
    ),
    
    "238": ProfilRisque(
        scian="238",
        nom="Entrepreneurs spécialisés",
        nom_court="Spécialisés",
        lesions_annuelles=12000,
        risques_prioritaires=[
            {"categorie": "chute", "pct": 25, "priorite": "CRITIQUE", "emoji": "🪜"},
            {"categorie": "electrique", "pct": 20, "priorite": "CRITIQUE", "emoji": "⚡"},
            {"categorie": "mecanique", "pct": 18, "priorite": "ELEVE", "emoji": "🔧"},
            {"categorie": "ergonomique", "pct": 15, "priorite": "ELEVE", "emoji": "🦴"},
            {"categorie": "chimique", "pct": 12, "priorite": "ELEVE", "emoji": "🧪"},
            {"categorie": "thermique", "pct": 10, "priorite": "MOYEN", "emoji": "🔥"},
        ],
        certifications_requises=["ASP Construction", "Travail en hauteur", "LOTO", "Électricité", "Soudage", "SIMDUT"],
        epi_critiques=["casque", "harnais", "lunettes", "gants isolants", "masque soudeur"],
        mots_cles_risques=["électrique", "soudure", "plomberie", "toiture", "isolation", "peinture"],
        reglementations=["RSST", "Code de sécurité construction", "Code électrique"]
    ),
    
    # =========================================================================
    # SANTÉ (SCIAN 621-624)
    # =========================================================================
    "621": ProfilRisque(
        scian="621",
        nom="Services de soins ambulatoires",
        nom_court="Soins ambulatoires",
        lesions_annuelles=25000,
        risques_prioritaires=[
            {"categorie": "ergonomique", "pct": 35, "priorite": "CRITIQUE", "emoji": "🦴"},
            {"categorie": "biologique", "pct": 25, "priorite": "CRITIQUE", "emoji": "🦠"},
            {"categorie": "psychosocial", "pct": 20, "priorite": "ELEVE", "emoji": "🧠"},
            {"categorie": "chimique", "pct": 10, "priorite": "ELEVE", "emoji": "🧪"},
            {"categorie": "chute", "pct": 5, "priorite": "MOYEN", "emoji": "🪜"},
            {"categorie": "violence", "pct": 5, "priorite": "ELEVE", "emoji": "⚠️"},
        ],
        certifications_requises=["SIMDUT", "Premiers soins", "RCR", "PDSB", "Prévention infections"],
        epi_critiques=["gants", "masque", "blouse", "lunettes protection", "écran facial"],
        mots_cles_risques=["manutention patient", "piqûre", "infection", "stress", "agression", "TMS", "lombaire"],
        reglementations=["RSST", "Loi sur les infirmières", "Protocoles infectieux"]
    ),
    
    "622": ProfilRisque(
        scian="622",
        nom="Hôpitaux",
        nom_court="Hôpitaux",
        lesions_annuelles=35000,
        risques_prioritaires=[
            {"categorie": "ergonomique", "pct": 40, "priorite": "CRITIQUE", "emoji": "🦴"},
            {"categorie": "biologique", "pct": 22, "priorite": "CRITIQUE", "emoji": "🦠"},
            {"categorie": "psychosocial", "pct": 18, "priorite": "ELEVE", "emoji": "🧠"},
            {"categorie": "chimique", "pct": 8, "priorite": "ELEVE", "emoji": "🧪"},
            {"categorie": "violence", "pct": 7, "priorite": "ELEVE", "emoji": "⚠️"},
            {"categorie": "radiation", "pct": 5, "priorite": "ELEVE", "emoji": "☢️"},
        ],
        certifications_requises=["SIMDUT", "PDSB", "RCR", "Prévention infections", "Radioprotection"],
        epi_critiques=["gants", "masque N95", "blouse", "lunettes", "tablier plombé"],
        mots_cles_risques=["patient", "civière", "piqûre", "sang", "chimio", "radiation", "urgence", "psychiatrie"],
        reglementations=["RSST", "Loi sur les services de santé", "INSPQ"]
    ),
    
    "623": ProfilRisque(
        scian="623",
        nom="Établissements de soins infirmiers",
        nom_court="CHSLD/Soins",
        lesions_annuelles=10000,
        risques_prioritaires=[
            {"categorie": "ergonomique", "pct": 45, "priorite": "CRITIQUE", "emoji": "🦴"},
            {"categorie": "psychosocial", "pct": 20, "priorite": "ELEVE", "emoji": "🧠"},
            {"categorie": "biologique", "pct": 15, "priorite": "ELEVE", "emoji": "🦠"},
            {"categorie": "violence", "pct": 12, "priorite": "ELEVE", "emoji": "⚠️"},
            {"categorie": "chute", "pct": 8, "priorite": "MOYEN", "emoji": "🪜"},
        ],
        certifications_requises=["PDSB", "SIMDUT", "RCR", "Prévention infections", "Gestion comportements"],
        epi_critiques=["gants", "masque", "blouse", "chaussures antidérapantes"],
        mots_cles_risques=["transfert patient", "levage", "démence", "agitation", "incontinence"],
        reglementations=["RSST", "MSSS", "Loi sur les CHSLD"]
    ),
    
    "624": ProfilRisque(
        scian="624",
        nom="Services sociaux",
        nom_court="Services sociaux",
        lesions_annuelles=4500,
        risques_prioritaires=[
            {"categorie": "psychosocial", "pct": 35, "priorite": "CRITIQUE", "emoji": "🧠"},
            {"categorie": "violence", "pct": 25, "priorite": "CRITIQUE", "emoji": "⚠️"},
            {"categorie": "ergonomique", "pct": 20, "priorite": "ELEVE", "emoji": "🦴"},
            {"categorie": "biologique", "pct": 10, "priorite": "MOYEN", "emoji": "🦠"},
            {"categorie": "chute", "pct": 10, "priorite": "MOYEN", "emoji": "🪜"},
        ],
        certifications_requises=["Intervention de crise", "Premiers soins", "RCR", "SIMDUT"],
        epi_critiques=["alarme personnelle", "chaussures sécuritaires"],
        mots_cles_risques=["agression", "menace", "stress", "épuisement", "intervention domicile"],
        reglementations=["RSST", "Loi sur les services sociaux"]
    ),
    
    # =========================================================================
    # FABRICATION (SCIAN 31-33)
    # =========================================================================
    "31": ProfilRisque(
        scian="31",
        nom="Fabrication d'aliments",
        nom_court="Agroalimentaire",
        lesions_annuelles=12000,
        risques_prioritaires=[
            {"categorie": "ergonomique", "pct": 30, "priorite": "CRITIQUE", "emoji": "🦴"},
            {"categorie": "mecanique", "pct": 25, "priorite": "CRITIQUE", "emoji": "🔧"},
            {"categorie": "chute", "pct": 15, "priorite": "ELEVE", "emoji": "🪜"},
            {"categorie": "thermique", "pct": 12, "priorite": "ELEVE", "emoji": "🔥"},
            {"categorie": "chimique", "pct": 10, "priorite": "MOYEN", "emoji": "🧪"},
            {"categorie": "bruit", "pct": 8, "priorite": "MOYEN", "emoji": "🔊"},
        ],
        certifications_requises=["SIMDUT", "LOTO", "Hygiène alimentaire", "Cariste", "Premiers soins"],
        epi_critiques=["gants", "tablier", "bottes antidérapantes", "résille", "protecteurs auditifs"],
        mots_cles_risques=["coupure", "brûlure", "froid", "manutention", "convoyeur", "trancheuse"],
        reglementations=["RSST", "MAPAQ", "ACIA"]
    ),
    
    "32": ProfilRisque(
        scian="32",
        nom="Fabrication de produits",
        nom_court="Fabrication",
        lesions_annuelles=20000,
        risques_prioritaires=[
            {"categorie": "mecanique", "pct": 30, "priorite": "CRITIQUE", "emoji": "🔧"},
            {"categorie": "ergonomique", "pct": 25, "priorite": "CRITIQUE", "emoji": "🦴"},
            {"categorie": "chimique", "pct": 15, "priorite": "ELEVE", "emoji": "🧪"},
            {"categorie": "bruit", "pct": 12, "priorite": "ELEVE", "emoji": "🔊"},
            {"categorie": "chute", "pct": 10, "priorite": "MOYEN", "emoji": "🪜"},
            {"categorie": "electrique", "pct": 8, "priorite": "ELEVE", "emoji": "⚡"},
        ],
        certifications_requises=["SIMDUT", "LOTO", "Cariste", "Pont roulant", "Premiers soins"],
        epi_critiques=["lunettes", "gants", "protecteurs auditifs", "chaussures sécurité", "casque"],
        mots_cles_risques=["machine", "presse", "coincement", "écrasement", "solvant", "poussière"],
        reglementations=["RSST", "Code électrique", "Normes machines"]
    ),
    
    "33": ProfilRisque(
        scian="33",
        nom="Fabrication de machines et métaux",
        nom_court="Métallurgie",
        lesions_annuelles=13000,
        risques_prioritaires=[
            {"categorie": "mecanique", "pct": 35, "priorite": "CRITIQUE", "emoji": "🔧"},
            {"categorie": "ergonomique", "pct": 20, "priorite": "ELEVE", "emoji": "🦴"},
            {"categorie": "bruit", "pct": 15, "priorite": "ELEVE", "emoji": "🔊"},
            {"categorie": "chimique", "pct": 12, "priorite": "ELEVE", "emoji": "🧪"},
            {"categorie": "thermique", "pct": 10, "priorite": "ELEVE", "emoji": "🔥"},
            {"categorie": "electrique", "pct": 8, "priorite": "ELEVE", "emoji": "⚡"},
        ],
        certifications_requises=["SIMDUT", "LOTO", "Soudage", "Pont roulant", "Cariste", "Meulage"],
        epi_critiques=["lunettes", "masque soudeur", "gants", "tablier cuir", "protecteurs auditifs"],
        mots_cles_risques=["soudure", "meulage", "tour", "presse", "métal chaud", "fumées", "huile"],
        reglementations=["RSST", "CSA W117.2", "Code électrique"]
    ),
    
    # =========================================================================
    # COMMERCE DE DÉTAIL (SCIAN 44-45)
    # =========================================================================
    "44": ProfilRisque(
        scian="44",
        nom="Commerce de détail",
        nom_court="Commerce",
        lesions_annuelles=25000,
        risques_prioritaires=[
            {"categorie": "ergonomique", "pct": 35, "priorite": "CRITIQUE", "emoji": "🦴"},
            {"categorie": "chute", "pct": 25, "priorite": "ELEVE", "emoji": "🪜"},
            {"categorie": "mecanique", "pct": 15, "priorite": "MOYEN", "emoji": "🔧"},
            {"categorie": "violence", "pct": 12, "priorite": "ELEVE", "emoji": "⚠️"},
            {"categorie": "psychosocial", "pct": 8, "priorite": "MOYEN", "emoji": "🧠"},
            {"categorie": "thermique", "pct": 5, "priorite": "MOYEN", "emoji": "🔥"},
        ],
        certifications_requises=["SIMDUT", "Manutention", "Cariste", "Premiers soins"],
        epi_critiques=["chaussures sécurité", "gants manutention", "ceinture lombaire"],
        mots_cles_risques=["manutention", "boîte", "palette", "escabeau", "vol", "agression client"],
        reglementations=["RSST", "Normes travail"]
    ),
    
    "45": ProfilRisque(
        scian="45",
        nom="Commerce de détail divers",
        nom_court="Détail divers",
        lesions_annuelles=8000,
        risques_prioritaires=[
            {"categorie": "ergonomique", "pct": 40, "priorite": "CRITIQUE", "emoji": "🦴"},
            {"categorie": "chute", "pct": 20, "priorite": "ELEVE", "emoji": "🪜"},
            {"categorie": "violence", "pct": 15, "priorite": "ELEVE", "emoji": "⚠️"},
            {"categorie": "mecanique", "pct": 10, "priorite": "MOYEN", "emoji": "🔧"},
            {"categorie": "psychosocial", "pct": 10, "priorite": "MOYEN", "emoji": "🧠"},
        ],
        certifications_requises=["SIMDUT", "Manutention", "Premiers soins"],
        epi_critiques=["chaussures antidérapantes", "gants"],
        mots_cles_risques=["caisse", "étalage", "client difficile", "station debout", "répétitif"],
        reglementations=["RSST", "Normes travail"]
    ),
    
    # =========================================================================
    # HÉBERGEMENT ET RESTAURATION (SCIAN 72)
    # =========================================================================
    "72": ProfilRisque(
        scian="72",
        nom="Hébergement et restauration",
        nom_court="Resto/Hôtel",
        lesions_annuelles=15000,
        risques_prioritaires=[
            {"categorie": "ergonomique", "pct": 28, "priorite": "CRITIQUE", "emoji": "🦴"},
            {"categorie": "chute", "pct": 22, "priorite": "ELEVE", "emoji": "🪜"},
            {"categorie": "thermique", "pct": 20, "priorite": "ELEVE", "emoji": "🔥"},
            {"categorie": "coupure", "pct": 15, "priorite": "ELEVE", "emoji": "🔪"},
            {"categorie": "chimique", "pct": 8, "priorite": "MOYEN", "emoji": "🧪"},
            {"categorie": "psychosocial", "pct": 7, "priorite": "MOYEN", "emoji": "🧠"},
        ],
        certifications_requises=["SIMDUT", "Hygiène alimentaire", "Premiers soins", "MAPAQ"],
        epi_critiques=["chaussures antidérapantes", "tablier", "gants cuisine", "gants four"],
        mots_cles_risques=["brûlure", "coupure", "huile chaude", "plancher glissant", "charge lourde", "stress"],
        reglementations=["RSST", "MAPAQ", "Normes travail"]
    ),
    
    # =========================================================================
    # TRANSPORT ET ENTREPOSAGE (SCIAN 48-49)
    # =========================================================================
    "48": ProfilRisque(
        scian="48",
        nom="Transport",
        nom_court="Transport",
        lesions_annuelles=12000,
        risques_prioritaires=[
            {"categorie": "ergonomique", "pct": 30, "priorite": "CRITIQUE", "emoji": "🦴"},
            {"categorie": "mecanique", "pct": 25, "priorite": "CRITIQUE", "emoji": "🔧"},
            {"categorie": "chute", "pct": 18, "priorite": "ELEVE", "emoji": "🪜"},
            {"categorie": "collision", "pct": 12, "priorite": "CRITIQUE", "emoji": "🚛"},
            {"categorie": "psychosocial", "pct": 10, "priorite": "MOYEN", "emoji": "🧠"},
            {"categorie": "vibration", "pct": 5, "priorite": "MOYEN", "emoji": "〰️"},
        ],
        certifications_requises=["Classe 1/3", "Cariste", "SIMDUT", "Matières dangereuses", "Premiers soins"],
        epi_critiques=["chaussures sécurité", "gilet haute visibilité", "gants"],
        mots_cles_risques=["camion", "chargement", "quai", "chariot élévateur", "fatigue", "route"],
        reglementations=["RSST", "SAAQ", "Transport Canada"]
    ),
    
    "49": ProfilRisque(
        scian="49",
        nom="Entreposage",
        nom_court="Entreposage",
        lesions_annuelles=8000,
        risques_prioritaires=[
            {"categorie": "ergonomique", "pct": 35, "priorite": "CRITIQUE", "emoji": "🦴"},
            {"categorie": "mecanique", "pct": 25, "priorite": "CRITIQUE", "emoji": "🔧"},
            {"categorie": "chute", "pct": 20, "priorite": "ELEVE", "emoji": "🪜"},
            {"categorie": "collision", "pct": 10, "priorite": "ELEVE", "emoji": "🚛"},
            {"categorie": "thermique", "pct": 10, "priorite": "MOYEN", "emoji": "❄️"},
        ],
        certifications_requises=["Cariste", "SIMDUT", "Rayonnage", "Premiers soins"],
        epi_critiques=["chaussures sécurité", "gilet haute visibilité", "gants", "vêtements chauds"],
        mots_cles_risques=["palette", "rayonnage", "chariot", "froid", "manutention", "empilage"],
        reglementations=["RSST", "Normes rayonnage"]
    ),
    
    # =========================================================================
    # MINES (SCIAN 21)
    # =========================================================================
    "21": ProfilRisque(
        scian="21",
        nom="Extraction minière",
        nom_court="Mines",
        lesions_annuelles=3000,
        risques_prioritaires=[
            {"categorie": "mecanique", "pct": 28, "priorite": "CRITIQUE", "emoji": "🔧"},
            {"categorie": "chute", "pct": 18, "priorite": "CRITIQUE", "emoji": "🪜"},
            {"categorie": "effondrement", "pct": 15, "priorite": "CRITIQUE", "emoji": "⛏️"},
            {"categorie": "chimique", "pct": 12, "priorite": "ELEVE", "emoji": "🧪"},
            {"categorie": "bruit", "pct": 12, "priorite": "ELEVE", "emoji": "🔊"},
            {"categorie": "ergonomique", "pct": 10, "priorite": "ELEVE", "emoji": "🦴"},
            {"categorie": "electrique", "pct": 5, "priorite": "ELEVE", "emoji": "⚡"},
        ],
        certifications_requises=["Module minier", "Espace clos", "SIMDUT", "Premiers soins", "Sauvetage minier"],
        epi_critiques=["casque lampe", "bottes cap acier", "lunettes", "protecteurs auditifs", "auto-sauveteur"],
        mots_cles_risques=["souterrain", "dynamitage", "ventilation", "machinerie lourde", "poussière", "silicose"],
        reglementations=["Loi sur les mines", "RSST", "CNESST secteur minier"]
    ),
    
    # =========================================================================
    # SERVICES PUBLICS (SCIAN 22)
    # =========================================================================
    "22": ProfilRisque(
        scian="22",
        nom="Services publics",
        nom_court="Énergie/Eau",
        lesions_annuelles=2500,
        risques_prioritaires=[
            {"categorie": "electrique", "pct": 30, "priorite": "CRITIQUE", "emoji": "⚡"},
            {"categorie": "chute", "pct": 20, "priorite": "CRITIQUE", "emoji": "🪜"},
            {"categorie": "mecanique", "pct": 18, "priorite": "ELEVE", "emoji": "🔧"},
            {"categorie": "espace_clos", "pct": 12, "priorite": "CRITIQUE", "emoji": "🕳️"},
            {"categorie": "chimique", "pct": 10, "priorite": "ELEVE", "emoji": "🧪"},
            {"categorie": "ergonomique", "pct": 10, "priorite": "MOYEN", "emoji": "🦴"},
        ],
        certifications_requises=["Électricité haute tension", "LOTO", "Espace clos", "Travail en hauteur", "SIMDUT"],
        epi_critiques=["gants isolants", "harnais", "casque", "lunettes arc flash", "détecteur gaz"],
        mots_cles_risques=["haute tension", "poteau", "transformateur", "égout", "réservoir", "chlore"],
        reglementations=["RSST", "Code électrique", "Hydro-Québec"]
    ),
    
    # =========================================================================
    # AGRICULTURE (SCIAN 11)
    # =========================================================================
    "11": ProfilRisque(
        scian="11",
        nom="Agriculture, foresterie, pêche",
        nom_court="Agriculture",
        lesions_annuelles=5000,
        risques_prioritaires=[
            {"categorie": "mecanique", "pct": 35, "priorite": "CRITIQUE", "emoji": "🔧"},
            {"categorie": "ergonomique", "pct": 20, "priorite": "ELEVE", "emoji": "🦴"},
            {"categorie": "chute", "pct": 15, "priorite": "ELEVE", "emoji": "🪜"},
            {"categorie": "chimique", "pct": 12, "priorite": "ELEVE", "emoji": "🧪"},
            {"categorie": "biologique", "pct": 10, "priorite": "MOYEN", "emoji": "🦠"},
            {"categorie": "thermique", "pct": 8, "priorite": "MOYEN", "emoji": "☀️"},
        ],
        certifications_requises=["Pesticides", "SIMDUT", "Tracteur", "Premiers soins", "Tronçonneuse"],
        epi_critiques=["bottes", "gants", "combinaison", "masque respiratoire", "lunettes"],
        mots_cles_risques=["tracteur", "PTO", "pesticide", "silo", "animal", "chaleur", "foresterie"],
        reglementations=["RSST", "UPA", "MAPAQ", "Pesticides"]
    ),
    
    # =========================================================================
    # SERVICES PROFESSIONNELS (SCIAN 54)
    # =========================================================================
    "54": ProfilRisque(
        scian="54",
        nom="Services professionnels et techniques",
        nom_court="Services pro",
        lesions_annuelles=3000,
        risques_prioritaires=[
            {"categorie": "ergonomique", "pct": 45, "priorite": "CRITIQUE", "emoji": "🦴"},
            {"categorie": "psychosocial", "pct": 30, "priorite": "ELEVE", "emoji": "🧠"},
            {"categorie": "chute", "pct": 10, "priorite": "MOYEN", "emoji": "🪜"},
            {"categorie": "electrique", "pct": 8, "priorite": "MOYEN", "emoji": "⚡"},
            {"categorie": "violence", "pct": 7, "priorite": "MOYEN", "emoji": "⚠️"},
        ],
        certifications_requises=["Premiers soins", "Ergonomie bureau"],
        epi_critiques=["chaise ergonomique", "écran ajustable", "clavier ergonomique"],
        mots_cles_risques=["écran", "posture", "stress", "surcharge", "télétravail", "sédentarité"],
        reglementations=["RSST", "Normes ergonomie ANSI"]
    ),
    
    # =========================================================================
    # ADMINISTRATION PUBLIQUE (SCIAN 91)
    # =========================================================================
    "91": ProfilRisque(
        scian="91",
        nom="Administration publique",
        nom_court="Admin publique",
        lesions_annuelles=4000,
        risques_prioritaires=[
            {"categorie": "ergonomique", "pct": 40, "priorite": "CRITIQUE", "emoji": "🦴"},
            {"categorie": "psychosocial", "pct": 25, "priorite": "ELEVE", "emoji": "🧠"},
            {"categorie": "violence", "pct": 15, "priorite": "ELEVE", "emoji": "⚠️"},
            {"categorie": "chute", "pct": 12, "priorite": "MOYEN", "emoji": "🪜"},
            {"categorie": "routier", "pct": 8, "priorite": "MOYEN", "emoji": "🚗"},
        ],
        certifications_requises=["Premiers soins", "Intervention clientèle difficile"],
        epi_critiques=["chaise ergonomique", "alarme personnelle"],
        mots_cles_risques=["bureau", "public", "agression verbale", "stress", "écran"],
        reglementations=["RSST", "Politique santé fonction publique"]
    ),
}


# ============================================================================
# GÉNÉRATEUR DE REQUÊTES CYPHER
# ============================================================================

class CypherGenerator:
    """Générateur de requêtes Cypher personnalisées par secteur SCIAN"""
    
    def __init__(self, scian: str, nb_employes: Optional[int] = None, nom_entreprise: Optional[str] = None):
        self.scian = self._normaliser_scian(scian)
        self.nb_employes = nb_employes
        self.nom_entreprise = nom_entreprise
        self.profil = self._get_profil()
        self.date_generation = datetime.now().strftime("%Y-%m-%d %H:%M")
        
    def _normaliser_scian(self, scian: str) -> str:
        """Normaliser le code SCIAN"""
        scian = scian.strip().replace("-", "").replace(" ", "")
        
        # Mapper les codes composés
        mappings = {
            "236238": "236",
            "3133": "32",
            "4445": "44",
            "4849": "48",
            "621624": "621",
        }
        
        # Essayer le code direct d'abord
        if scian in PROFILS_CNESST:
            return scian
        
        # Essayer les 3 premiers chiffres
        if scian[:3] in PROFILS_CNESST:
            return scian[:3]
            
        # Essayer les 2 premiers chiffres
        if scian[:2] in PROFILS_CNESST:
            return scian[:2]
            
        # Essayer les mappings
        if scian in mappings:
            return mappings[scian]
            
        return scian
    
    def _get_profil(self) -> ProfilRisque:
        """Obtenir le profil de risques CNESST"""
        if self.scian not in PROFILS_CNESST:
            # Profil par défaut
            return ProfilRisque(
                scian=self.scian,
                nom=f"Secteur SCIAN {self.scian}",
                nom_court=f"SCIAN {self.scian}",
                lesions_annuelles=5000,
                risques_prioritaires=[
                    {"categorie": "ergonomique", "pct": 30, "priorite": "ELEVE", "emoji": "🦴"},
                    {"categorie": "chute", "pct": 20, "priorite": "ELEVE", "emoji": "🪜"},
                    {"categorie": "mecanique", "pct": 20, "priorite": "ELEVE", "emoji": "🔧"},
                ],
                certifications_requises=["SIMDUT", "Premiers soins"],
                epi_critiques=["chaussures sécurité", "lunettes", "gants"],
                mots_cles_risques=["accident", "blessure", "danger"],
                reglementations=["RSST"]
            )
        return PROFILS_CNESST[self.scian]
    
    def _generer_entete(self) -> str:
        """Générer l'en-tête du fichier"""
        return f"""// ============================================================================
// 🛡️ REQUÊTES CYPHER GÉNÉRÉES AUTOMATIQUEMENT - SafetyGraph
// ============================================================================
// Secteur: {self.profil.nom} (SCIAN {self.profil.scian})
// Profil de risques: CNESST Québec
// Lésions annuelles secteur: {self.profil.lesions_annuelles:,}
// Généré le: {self.date_generation}
// Générateur: EDGY-AgenticX5 / Preventera / GenAISafety
// ============================================================================

// PROFIL DE RISQUES DU SECTEUR:
// {"".join([f'''
// {r["emoji"]} {r["categorie"].upper()}: {r["pct"]}% des lésions - Priorité {r["priorite"]}''' for r in self.profil.risques_prioritaires])}
//
// CERTIFICATIONS REQUISES: {", ".join(self.profil.certifications_requises)}
// EPI CRITIQUES: {", ".join(self.profil.epi_critiques)}
// ============================================================================

"""
    
    def _generer_diagnostic(self) -> str:
        """Section 1: Diagnostic initial"""
        scian_filter = self._get_scian_filter()
        
        return f"""
// ============================================================================
// 1. 📋 DIAGNOSTIC INITIAL - Vue d'ensemble
// ============================================================================

// 1.1 Statistiques globales de l'organisation
MATCH (o:Organization)
WHERE {scian_filter}
OPTIONAL MATCH (o)<-[:APPARTIENT_A]-(z:Zone)
OPTIONAL MATCH (z)<-[:LOCALISE_DANS]-(r:RisqueDanger)
OPTIONAL MATCH (o)<-[:APPARTIENT_A]-(t:Team)<-[:MEMBRE_DE]-(p:Person)
RETURN o.name AS organisation,
       o.nb_employes AS employes,
       count(DISTINCT z) AS nb_zones,
       count(DISTINCT r) AS nb_risques,
       count(DISTINCT p) AS nb_travailleurs,
       round(avg(r.probabilite * r.gravite) * 100) / 100 AS score_risque_moyen
ORDER BY nb_risques DESC;

// 1.2 Distribution des zones par niveau de risque
MATCH (o:Organization)<-[:APPARTIENT_A]-(z:Zone)
WHERE {scian_filter}
RETURN z.risk_level AS niveau_risque,
       count(z) AS nb_zones,
       collect(z.name)[0..5] AS exemples_zones
ORDER BY CASE z.risk_level 
    WHEN 'critique' THEN 1 
    WHEN 'eleve' THEN 2 
    WHEN 'moyen' THEN 3 
    ELSE 4 END;

// 1.3 Répartition des risques par catégorie
MATCH (o:Organization)<-[:APPARTIENT_A]-(z:Zone)<-[:LOCALISE_DANS]-(r:RisqueDanger)
WHERE {scian_filter}
RETURN r.categorie AS categorie,
       count(r) AS nb_risques,
       round(avg(r.probabilite * r.gravite) * 100) / 100 AS score_moyen,
       sum(CASE WHEN r.probabilite * r.gravite >= 15 THEN 1 ELSE 0 END) AS nb_tolerance_zero
ORDER BY nb_risques DESC;

"""
    
    def _generer_section_risque(self, risque: Dict, index: int) -> str:
        """Générer une section pour un type de risque spécifique"""
        categorie = risque["categorie"]
        emoji = risque["emoji"]
        pct = risque["pct"]
        priorite = risque["priorite"]
        scian_filter = self._get_scian_filter()
        
        # Mots-clés spécifiques à cette catégorie
        mots_cles = self._get_mots_cles_categorie(categorie)
        mots_cles_filter = " OR ".join([f"toLower(r.description) CONTAINS '{m}'" for m in mots_cles])
        
        # Certifications liées à cette catégorie
        certifs = self._get_certifications_categorie(categorie)
        
        return f"""
// ============================================================================
// {index}. {emoji} RISQUES {categorie.upper()} - {pct}% des lésions ({priorite})
// ============================================================================

// {index}.1 Identifier tous les risques {categorie}
MATCH (o:Organization)<-[:APPARTIENT_A]-(z:Zone)<-[:LOCALISE_DANS]-(r:RisqueDanger)
WHERE {scian_filter}
  AND (r.categorie = '{categorie}' OR {mots_cles_filter})
RETURN z.name AS zone,
       r.description AS risque,
       r.probabilite AS P,
       r.gravite AS G,
       r.probabilite * r.gravite AS score,
       CASE WHEN r.probabilite * r.gravite >= 15 THEN '🔴 TOLÉRANCE ZÉRO'
            WHEN r.probabilite * r.gravite >= 10 THEN '🟠 ÉLEVÉ'
            ELSE '🟡 MODÉRÉ' END AS priorite
ORDER BY score DESC;

// {index}.2 Travailleurs exposés aux risques {categorie}
MATCH (o:Organization)<-[:APPARTIENT_A]-(z:Zone)<-[:LOCALISE_DANS]-(r:RisqueDanger)
MATCH (p:Person)-[:TRAVAILLE_DANS]->(z)
WHERE {scian_filter}
  AND (r.categorie = '{categorie}' OR {mots_cles_filter})
WITH p, collect(DISTINCT z.name) AS zones_exposition, count(r) AS nb_risques, max(r.probabilite * r.gravite) AS score_max
RETURN p.matricule AS travailleur,
       p.age_groupe AS age,
       zones_exposition,
       nb_risques,
       score_max
ORDER BY score_max DESC
LIMIT 30;

// {index}.3 Zones critiques pour risques {categorie}
MATCH (o:Organization)<-[:APPARTIENT_A]-(z:Zone)<-[:LOCALISE_DANS]-(r:RisqueDanger)
WHERE {scian_filter}
  AND (r.categorie = '{categorie}' OR {mots_cles_filter})
WITH z, count(r) AS nb_risques, avg(r.probabilite * r.gravite) AS score_moyen
WHERE nb_risques >= 2
RETURN z.name AS zone_critique,
       z.risk_level AS niveau_zone,
       nb_risques,
       round(score_moyen * 100) / 100 AS score_moyen,
       z.epi_requis AS epi_actuels
ORDER BY score_moyen DESC;

// {index}.4 Gap certifications pour risques {categorie}
MATCH (o:Organization)<-[:APPARTIENT_A]-(z:Zone)<-[:LOCALISE_DANS]-(r:RisqueDanger)
MATCH (p:Person)-[:TRAVAILLE_DANS]->(z)
WHERE {scian_filter}
  AND (r.categorie = '{categorie}' OR {mots_cles_filter})
  AND r.probabilite * r.gravite >= 10
  AND (p.certifications_sst IS NULL{self._get_certif_filter(certifs)})
RETURN DISTINCT p.matricule AS travailleur,
       z.name AS zone,
       p.certifications_sst AS certifications_actuelles,
       '{", ".join(certifs)}' AS certifications_recommandees
LIMIT 30;

"""
    
    def _generer_alertes(self) -> str:
        """Section alertes et surveillance"""
        scian_filter = self._get_scian_filter()
        
        return f"""
// ============================================================================
// 🚨 ALERTES ET SURVEILLANCE PROACTIVE
// ============================================================================

// 🔴 ALERTE CRITIQUE: Risques Tolérance Zéro (score >= 15)
MATCH (o:Organization)<-[:APPARTIENT_A]-(z:Zone)<-[:LOCALISE_DANS]-(r:RisqueDanger)
WHERE {scian_filter}
  AND r.probabilite * r.gravite >= 15
RETURN '🔴 TOLÉRANCE ZÉRO' AS alerte,
       o.name AS organisation,
       z.name AS zone,
       r.categorie AS type_risque,
       r.description AS description,
       r.probabilite * r.gravite AS score
ORDER BY score DESC;

// 🟠 ALERTE: Concentration de risques (hotspots)
MATCH (o:Organization)<-[:APPARTIENT_A]-(z:Zone)<-[:LOCALISE_DANS]-(r:RisqueDanger)
WHERE {scian_filter}
WITH z, o, count(r) AS nb_risques, avg(r.probabilite * r.gravite) AS score_moyen
WHERE nb_risques >= 3
RETURN z.name AS zone_hotspot,
       o.name AS organisation,
       nb_risques,
       round(score_moyen * 100) / 100 AS score_moyen,
       CASE WHEN score_moyen >= 12 THEN '🔴 CRITIQUE'
            WHEN score_moyen >= 8 THEN '🟠 ÉLEVÉ'
            ELSE '🟡 MODÉRÉ' END AS niveau_alerte
ORDER BY score_moyen DESC;

// 👤 ALERTE: Jeunes travailleurs (18-24) en zones à risque
MATCH (o:Organization)<-[:APPARTIENT_A]-(z:Zone)<-[:LOCALISE_DANS]-(r:RisqueDanger)
MATCH (p:Person)-[:TRAVAILLE_DANS]->(z)
WHERE {scian_filter}
  AND p.age_groupe = '18-24'
  AND r.probabilite * r.gravite >= 10
RETURN '⚠️ JEUNE TRAVAILLEUR EXPOSÉ' AS alerte,
       p.matricule AS travailleur,
       z.name AS zone,
       collect(DISTINCT r.categorie) AS types_risques,
       max(r.probabilite * r.gravite) AS score_max;

// 👴 ALERTE: Travailleurs expérimentés (55+) - risques ergonomiques
MATCH (o:Organization)<-[:APPARTIENT_A]-(z:Zone)<-[:LOCALISE_DANS]-(r:RisqueDanger)
MATCH (p:Person)-[:TRAVAILLE_DANS]->(z)
WHERE {scian_filter}
  AND p.age_groupe IN ['55-64', '65+']
  AND r.categorie = 'ergonomique'
RETURN '⚠️ TRAVAILLEUR EXPÉRIMENTÉ - RISQUE ERGO' AS alerte,
       p.matricule AS travailleur,
       z.name AS zone,
       r.description AS risque;

"""
    
    def _generer_conformite(self) -> str:
        """Section conformité et audit"""
        scian_filter = self._get_scian_filter()
        certifs = self.profil.certifications_requises
        epis = self.profil.epi_critiques
        
        return f"""
// ============================================================================
// ✅ CONFORMITÉ ET AUDIT - {", ".join(self.profil.reglementations)}
// ============================================================================

// Vérification EPI par zone à risque
MATCH (o:Organization)<-[:APPARTIENT_A]-(z:Zone)
WHERE {scian_filter}
  AND z.risk_level IN ['critique', 'eleve']
RETURN z.name AS zone,
       z.risk_level AS niveau,
       z.epi_requis AS epi_definis,
       CASE WHEN z.epi_requis IS NULL OR size(z.epi_requis) = 0 
            THEN '❌ EPI NON DÉFINIS - ACTION REQUISE'
            WHEN size(z.epi_requis) < 3
            THEN '⚠️ EPI POSSIBLEMENT INCOMPLETS'
            ELSE '✅ OK' END AS statut_epi;

// Taux de certification par équipe
MATCH (o:Organization)<-[:APPARTIENT_A]-(t:Team)<-[:MEMBRE_DE]-(p:Person)
WHERE {scian_filter}
WITH t, o,
     count(p) AS total,
     sum(CASE WHEN p.certifications_sst IS NOT NULL AND size(p.certifications_sst) > 0 THEN 1 ELSE 0 END) AS certifies
RETURN o.name AS organisation,
       t.name AS equipe,
       total AS nb_membres,
       certifies AS nb_certifies,
       round(certifies * 100.0 / total) AS taux_certification,
       CASE WHEN certifies * 100.0 / total < 80 THEN '⚠️ FORMATION REQUISE' ELSE '✅' END AS statut
ORDER BY taux_certification ASC;

// Vérification certifications requises secteur: {", ".join(certifs)}
MATCH (o:Organization)<-[:APPARTIENT_A]-(t:Team)<-[:MEMBRE_DE]-(p:Person)
WHERE {scian_filter}
WITH p, p.certifications_sst AS certs
WHERE certs IS NULL OR size([c IN certs WHERE c IN {certifs}]) < 2
RETURN p.matricule AS travailleur,
       certs AS certifications_actuelles,
       '{", ".join(certifs[:3])}' AS certifications_prioritaires
LIMIT 50;

// Score de maturité SST par organisation
MATCH (o:Organization)
WHERE {scian_filter}
OPTIONAL MATCH (o)<-[:APPARTIENT_A]-(z:Zone)<-[:LOCALISE_DANS]-(r:RisqueDanger)
OPTIONAL MATCH (o)<-[:APPARTIENT_A]-(t:Team)<-[:MEMBRE_DE]-(p:Person)
WITH o,
     count(DISTINCT z) AS zones,
     count(DISTINCT r) AS risques,
     count(DISTINCT p) AS personnes,
     sum(CASE WHEN p.certifications_sst IS NOT NULL THEN 1 ELSE 0 END) AS certifies,
     sum(CASE WHEN z.epi_requis IS NOT NULL THEN 1 ELSE 0 END) AS zones_epi
WITH o, zones, risques, personnes, certifies, zones_epi,
     CASE WHEN zones > 0 THEN 20 ELSE 0 END +
     CASE WHEN risques > 0 THEN 20 ELSE 0 END +
     CASE WHEN personnes > 0 AND certifies * 1.0 / personnes > 0.5 THEN 30 ELSE 15 END +
     CASE WHEN zones > 0 AND zones_epi * 1.0 / zones > 0.7 THEN 20 ELSE 10 END AS score_maturite
RETURN o.name AS organisation,
       score_maturite AS 'Score /90',
       CASE WHEN score_maturite >= 70 THEN '✅ MATURE'
            WHEN score_maturite >= 50 THEN '🟡 EN PROGRESSION'
            ELSE '🔴 À AMÉLIORER' END AS niveau_maturite;

"""
    
    def _generer_agents_ia(self) -> str:
        """Section requêtes pour agents IA"""
        scian_filter = self._get_scian_filter()
        top3_risques = [r["categorie"] for r in self.profil.risques_prioritaires[:3]]
        
        return f"""
// ============================================================================
// 🤖 REQUÊTES POUR AGENTS IA - SafetyGraph
// ============================================================================

// Agent VisionAI - Zones prioritaires surveillance caméra
MATCH (o:Organization)<-[:APPARTIENT_A]-(z:Zone)<-[:LOCALISE_DANS]-(r:RisqueDanger)
WHERE {scian_filter}
  AND z.risk_level = 'critique'
  AND r.categorie IN {top3_risques}
RETURN DISTINCT z.name AS zone_surveillance,
       collect(DISTINCT r.categorie) AS types_risques,
       'VisionAI' AS agent,
       'Détection comportements à risque en temps réel' AS mission;

// Agent ErgoAI - Postes à analyser
MATCH (o:Organization)<-[:APPARTIENT_A]-(z:Zone)<-[:LOCALISE_DANS]-(r:RisqueDanger)
MATCH (p:Person)-[:TRAVAILLE_DANS]->(z)
WHERE {scian_filter}
  AND r.categorie = 'ergonomique'
WITH z, count(DISTINCT p) AS nb_exposes, avg(r.probabilite * r.gravite) AS score
WHERE nb_exposes >= 3
RETURN z.name AS poste_analyse,
       nb_exposes AS travailleurs_exposes,
       round(score * 100) / 100 AS score_ergo,
       'ErgoAI' AS agent,
       'Analyse posturale et recommandations' AS mission
ORDER BY score DESC;

// Agent AlertAI - Déclencheurs d'alertes
MATCH (o:Organization)<-[:APPARTIENT_A]-(z:Zone)<-[:LOCALISE_DANS]-(r:RisqueDanger)
WHERE {scian_filter}
WITH z, o, count(r) AS nb_risques, avg(r.probabilite * r.gravite) AS score_moyen
WHERE score_moyen >= 10 OR nb_risques >= 5
RETURN o.name AS organisation,
       z.name AS zone,
       nb_risques,
       round(score_moyen * 100) / 100 AS score,
       CASE 
           WHEN score_moyen >= 15 THEN 'CRITIQUE - Alerte immédiate'
           WHEN score_moyen >= 12 THEN 'ÉLEVÉ - Alerte superviseur'
           ELSE 'MODÉRÉ - Surveillance renforcée'
       END AS action_alertai
ORDER BY score DESC;

// Agent PredictAI - Features ML pour prédiction
MATCH (o:Organization)<-[:APPARTIENT_A]-(z:Zone)<-[:LOCALISE_DANS]-(r:RisqueDanger)
WHERE {scian_filter}
OPTIONAL MATCH (o)<-[:APPARTIENT_A]-(t:Team)<-[:MEMBRE_DE]-(p:Person)
WITH o,
     count(DISTINCT z) AS nb_zones,
     count(DISTINCT r) AS nb_risques,
     count(DISTINCT t) AS nb_equipes,
     count(DISTINCT p) AS nb_personnes,
     avg(r.probabilite * r.gravite) AS score_moyen,
     sum(CASE WHEN r.categorie = '{top3_risques[0]}' THEN 1 ELSE 0 END) AS risques_cat1,
     sum(CASE WHEN r.categorie = '{top3_risques[1] if len(top3_risques) > 1 else top3_risques[0]}' THEN 1 ELSE 0 END) AS risques_cat2,
     sum(CASE WHEN r.probabilite * r.gravite >= 15 THEN 1 ELSE 0 END) AS risques_TZ
RETURN o.name AS organisation,
       o.nb_employes AS employes,
       nb_zones, nb_risques, nb_equipes, nb_personnes,
       round(score_moyen * 100) / 100 AS score_moyen,
       risques_cat1 AS '{top3_risques[0]}',
       risques_cat2 AS '{top3_risques[1] if len(top3_risques) > 1 else "autre"}',
       risques_TZ AS tolerance_zero,
       round(nb_risques * 1.0 / CASE WHEN nb_zones > 0 THEN nb_zones ELSE 1 END * 100) / 100 AS densite_risques;

// Agent ComplyAI - Écarts de conformité
MATCH (o:Organization)
WHERE {scian_filter}
OPTIONAL MATCH (o)<-[:APPARTIENT_A]-(z:Zone)
OPTIONAL MATCH (z)<-[:LOCALISE_DANS]-(r:RisqueDanger)
WITH o, count(DISTINCT z) AS zones, count(r) AS risques
WHERE zones > 0 AND risques = 0
RETURN o.name AS organisation,
       zones AS zones_sans_risques_documentes,
       'ComplyAI' AS agent,
       '⚠️ Audit de conformité requis - Risques non documentés' AS action;

"""
    
    def _generer_dashboard(self) -> str:
        """Section données pour dashboard"""
        scian_filter = self._get_scian_filter()
        
        return f"""
// ============================================================================
// 📊 DONNÉES POUR DASHBOARD ET VISUALISATION
// ============================================================================

// Données graphique - Risques par catégorie (barres/donut)
MATCH (o:Organization)<-[:APPARTIENT_A]-(z:Zone)<-[:LOCALISE_DANS]-(r:RisqueDanger)
WHERE {scian_filter}
RETURN r.categorie AS label,
       count(r) AS value,
       round(avg(r.probabilite * r.gravite) * 100) / 100 AS score_moyen
ORDER BY value DESC;

// Données graphique - Zones par niveau de risque (donut)
MATCH (o:Organization)<-[:APPARTIENT_A]-(z:Zone)
WHERE {scian_filter}
RETURN z.risk_level AS label, count(z) AS value
ORDER BY CASE z.risk_level 
    WHEN 'critique' THEN 1 WHEN 'eleve' THEN 2 
    WHEN 'moyen' THEN 3 ELSE 4 END;

// Données matrice de risques (scatter plot P x G)
MATCH (o:Organization)<-[:APPARTIENT_A]-(z:Zone)<-[:LOCALISE_DANS]-(r:RisqueDanger)
WHERE {scian_filter}
RETURN r.probabilite AS x,
       r.gravite AS y,
       count(r) AS size,
       r.categorie AS category
ORDER BY x, y;

// Données KPI cards
MATCH (o:Organization)<-[:APPARTIENT_A]-(z:Zone)<-[:LOCALISE_DANS]-(r:RisqueDanger)
WHERE {scian_filter}
WITH count(DISTINCT o) AS orgs,
     count(DISTINCT z) AS zones,
     count(r) AS risques,
     sum(CASE WHEN r.probabilite * r.gravite >= 15 THEN 1 ELSE 0 END) AS TZ,
     avg(r.probabilite * r.gravite) AS score_moy
RETURN orgs AS nb_organisations,
       zones AS nb_zones,
       risques AS nb_risques,
       TZ AS risques_tolerance_zero,
       round(score_moy * 100) / 100 AS score_risque_moyen,
       round(TZ * 100.0 / risques) AS pct_critique;

// Top 10 organisations par risque
MATCH (o:Organization)<-[:APPARTIENT_A]-(z:Zone)<-[:LOCALISE_DANS]-(r:RisqueDanger)
WHERE {scian_filter}
WITH o, count(r) AS nb_risques, avg(r.probabilite * r.gravite) AS score
RETURN o.name AS organisation, nb_risques, round(score * 100) / 100 AS score_moyen
ORDER BY score DESC
LIMIT 10;

"""
    
    def _get_scian_filter(self) -> str:
        """Générer le filtre SCIAN pour les requêtes"""
        # Gérer les codes composés
        codes = [self.scian]
        
        # Ajouter les variantes
        if self.scian == "236":
            codes = ["236", "237", "238", "236-238"]
        elif self.scian == "621":
            codes = ["621", "622", "623", "624", "621-624"]
        elif self.scian == "31":
            codes = ["31", "311", "312", "31-33"]
        elif self.scian == "32":
            codes = ["32", "321", "322", "323", "324", "325", "326", "327", "31-33"]
        elif self.scian == "33":
            codes = ["33", "331", "332", "333", "334", "335", "336", "337", "339", "31-33"]
        elif self.scian == "44":
            codes = ["44", "441", "442", "443", "444", "445", "44-45"]
        elif self.scian == "45":
            codes = ["45", "451", "452", "453", "454", "44-45"]
        elif self.scian == "48":
            codes = ["48", "481", "482", "483", "484", "485", "486", "487", "488", "48-49", "484-493"]
        elif self.scian == "49":
            codes = ["49", "491", "492", "493", "48-49", "484-493"]
            
        return f"o.sector_scian IN {codes}"
    
    def _get_mots_cles_categorie(self, categorie: str) -> List[str]:
        """Obtenir les mots-clés spécifiques à une catégorie de risque"""
        mots_cles_map = {
            "chute": ["chute", "hauteur", "échafaud", "échelle", "escalier", "glissade", "toiture", "plateforme"],
            "mecanique": ["machine", "écrasement", "coincement", "coupure", "presse", "convoyeur", "engrenage", "chariot"],
            "electrique": ["électrique", "tension", "arc flash", "câble", "disjoncteur", "haute tension"],
            "ergonomique": ["manutention", "posture", "répétitif", "charge", "lombaire", "TMS", "lever", "tirer"],
            "chimique": ["chimique", "solvant", "acide", "gaz", "vapeur", "poussière", "silice", "amiante"],
            "biologique": ["infection", "sang", "piqûre", "virus", "bactérie", "moisissure"],
            "psychosocial": ["stress", "harcèlement", "violence", "surcharge", "épuisement", "burnout"],
            "bruit": ["bruit", "décibel", "surdité", "audition"],
            "thermique": ["brûlure", "chaleur", "froid", "température", "four", "congélateur"],
            "radiation": ["radiation", "rayon X", "radioactif"],
            "violence": ["agression", "menace", "violence", "client difficile"],
            "coupure": ["coupure", "lacération", "tranchant", "couteau", "lame"],
            "collision": ["collision", "véhicule", "circulation", "renversement"],
            "ensevelissement": ["ensevelissement", "effondrement", "tranchée", "excavation"],
            "espace_clos": ["espace clos", "réservoir", "citerne", "puits", "égout"],
            "vibration": ["vibration", "outil vibrant"],
        }
        
        base = mots_cles_map.get(categorie, [categorie])
        # Ajouter les mots-clés spécifiques du profil
        return list(set(base + [m for m in self.profil.mots_cles_risques if categorie in m.lower()]))
    
    def _get_certifications_categorie(self, categorie: str) -> List[str]:
        """Obtenir les certifications liées à une catégorie de risque"""
        certif_map = {
            "chute": ["Travail en hauteur", "Échafaudage", "ASP Construction"],
            "mecanique": ["LOTO", "Cariste", "Pont roulant", "Sécurité machines"],
            "electrique": ["LOTO", "Électricité", "Haute tension", "Arc flash"],
            "ergonomique": ["Manutention", "PDSB", "Ergonomie"],
            "chimique": ["SIMDUT", "Matières dangereuses"],
            "biologique": ["Prévention infections", "SIMDUT"],
            "espace_clos": ["Espace clos", "Sauvetage"],
        }
        
        base = certif_map.get(categorie, [])
        # Filtrer par certifications du profil
        return [c for c in self.profil.certifications_requises if c in base or not base][:3]
    
    def _get_certif_filter(self, certifs: List[str]) -> str:
        """Générer le filtre pour vérifier les certifications manquantes"""
        if not certifs:
            return ""
        filters = [f" OR NOT '{c}' IN p.certifications_sst" for c in certifs[:2]]
        return "".join(filters)
    
    def generer(self) -> str:
        """Générer toutes les requêtes Cypher"""
        sections = [self._generer_entete()]
        sections.append(self._generer_diagnostic())
        
        # Générer une section pour chaque risque prioritaire
        for i, risque in enumerate(self.profil.risques_prioritaires[:5], start=2):
            sections.append(self._generer_section_risque(risque, i))
        
        sections.append(self._generer_alertes())
        sections.append(self._generer_conformite())
        sections.append(self._generer_agents_ia())
        sections.append(self._generer_dashboard())
        
        # Footer
        sections.append(f"""
// ============================================================================
// FIN DES REQUÊTES GÉNÉRÉES POUR SCIAN {self.profil.scian} - {self.profil.nom_court.upper()}
// Total: ~50 requêtes personnalisées selon profil CNESST
// ============================================================================
""")
        
        return "\n".join(sections)
    
    def sauvegarder(self, output_path: str):
        """Sauvegarder les requêtes dans un fichier"""
        contenu = self.generer()
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(contenu)
        print(f"✅ Requêtes générées: {output_path}")
        print(f"   Secteur: {self.profil.nom} (SCIAN {self.profil.scian})")
        print(f"   Lésions annuelles: {self.profil.lesions_annuelles:,}")
        print(f"   Risques prioritaires: {len(self.profil.risques_prioritaires)}")


# ============================================================================
# CLI
# ============================================================================

def lister_secteurs():
    """Afficher la liste des secteurs disponibles"""
    print("\n🏭 SECTEURS SCIAN DISPONIBLES\n")
    print(f"{'SCIAN':<8} {'Secteur':<40} {'Lésions/an':<12} {'Top risque'}")
    print("-" * 80)
    
    for scian, profil in sorted(PROFILS_CNESST.items(), key=lambda x: x[1].lesions_annuelles, reverse=True):
        top_risque = profil.risques_prioritaires[0]
        print(f"{scian:<8} {profil.nom_court:<40} {profil.lesions_annuelles:>10,}  {top_risque['emoji']} {top_risque['categorie']}")
    
    print(f"\nTotal: {len(PROFILS_CNESST)} secteurs disponibles\n")


def generer_tous(output_dir: str):
    """Générer les requêtes pour tous les secteurs"""
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"\n🔄 Génération des requêtes pour {len(PROFILS_CNESST)} secteurs...\n")
    
    for scian, profil in PROFILS_CNESST.items():
        output_path = os.path.join(output_dir, f"cypher_{profil.nom_court.lower().replace('/', '_').replace(' ', '_')}_scian{scian}.cypher")
        generator = CypherGenerator(scian)
        generator.sauvegarder(output_path)
    
    print(f"\n✅ Tous les fichiers générés dans: {output_dir}\n")


def main():
    parser = argparse.ArgumentParser(
        description="🛡️ SafetyGraph - Générateur de requêtes Cypher par secteur SCIAN",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  python cypher_generator.py --scian 236 --output construction.cypher
  python cypher_generator.py --scian 621 --output sante.cypher
  python cypher_generator.py --list-sectors
  python cypher_generator.py --all --output-dir ./requetes/
        """
    )
    
    parser.add_argument("--scian", "-s", type=str, help="Code SCIAN du secteur")
    parser.add_argument("--output", "-o", type=str, help="Fichier de sortie (.cypher)")
    parser.add_argument("--employes", "-e", type=int, help="Nombre d'employés (optionnel)")
    parser.add_argument("--list-sectors", "-l", action="store_true", help="Lister les secteurs disponibles")
    parser.add_argument("--all", "-a", action="store_true", help="Générer pour tous les secteurs")
    parser.add_argument("--output-dir", "-d", type=str, default="./cypher_generated", help="Dossier de sortie pour --all")
    
    args = parser.parse_args()
    
    if args.list_sectors:
        lister_secteurs()
        return
    
    if args.all:
        generer_tous(args.output_dir)
        return
    
    if not args.scian:
        parser.print_help()
        print("\n❌ Erreur: Spécifiez un code SCIAN avec --scian ou utilisez --list-sectors\n")
        return
    
    output = args.output or f"cypher_scian{args.scian}.cypher"
    
    generator = CypherGenerator(args.scian, args.employes)
    generator.sauvegarder(output)


if __name__ == "__main__":
    main()
