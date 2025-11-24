#!/usr/bin/env python3
"""
Agents Sectoriels SCIAN - EDGY-AgenticX5
Agents spécialisés par secteur d'activité

Classification SCIAN (Système de Classification des Industries de l'Amérique du Nord):
- 21: Extraction minière et extraction de pétrole et de gaz
- 22: Services publics
- 23: Construction
- 31-33: Fabrication (Manufacturing)
- 44-45: Commerce de détail
- 48-49: Transport et entreposage
- 62: Soins de santé et assistance sociale
- 72: Hébergement et services de restauration
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum

# Import de la base agent
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from agents.base_agent import BaseAgent, AgentCapability, AgentState
except ImportError:
    # Fallback si base_agent n'est pas disponible
    class AgentCapability(Enum):
        ANALYSIS = "analysis"
        PREDICTION = "prediction"
        RECOMMENDATION = "recommendation"
    
    class AgentState(Enum):
        IDLE = "idle"
        PROCESSING = "processing"
        COMPLETED = "completed"
    
    class BaseAgent:
        def __init__(self, agent_id, name, capabilities):
            self.agent_id = agent_id
            self.name = name
            self.capabilities = capabilities
            self.state = AgentState.IDLE
            self.logger = logging.getLogger(f"Agent.{name}")


# ============================================
# ÉNUMÉRATIONS SCIAN
# ============================================

class SecteurSCIAN(str, Enum):
    """Secteurs SCIAN principaux"""
    EXTRACTION = "21"
    SERVICES_PUBLICS = "22"
    CONSTRUCTION = "23"
    FABRICATION = "31-33"
    COMMERCE_DETAIL = "44-45"
    TRANSPORT = "48-49"
    SANTE = "62"
    HEBERGEMENT = "72"


class TypeRisqueSectoriel(str, Enum):
    """Types de risques par secteur"""
    CHUTE_HAUTEUR = "chute_hauteur"
    EXPOSITION_CHIMIQUE = "exposition_chimique"
    ECRASEMENT = "ecrasement"
    ELECTROCUTION = "electrocution"
    TMS = "troubles_musculosquelettiques"
    BRUIT = "exposition_bruit"
    VIBRATION = "exposition_vibration"
    THERMIQUE = "stress_thermique"
    PSYCHOSOCIAL = "risque_psychosocial"
    BIOLOGIQUE = "risque_biologique"


# ============================================
# CONFIGURATION SECTORIELLE
# ============================================

@dataclass
class ConfigSectorielle:
    """Configuration spécifique à un secteur"""
    code_scian: str
    nom_secteur: str
    risques_principaux: List[TypeRisqueSectoriel]
    seuils_critiques: Dict[str, float]
    reglements_applicables: List[str]
    frequence_inspection: int  # jours
    precision_prediction: float = 0.85


CONFIGURATIONS_SECTORIELLES = {
    SecteurSCIAN.CONSTRUCTION: ConfigSectorielle(
        code_scian="23",
        nom_secteur="Construction",
        risques_principaux=[
            TypeRisqueSectoriel.CHUTE_HAUTEUR,
            TypeRisqueSectoriel.ECRASEMENT,
            TypeRisqueSectoriel.ELECTROCUTION,
            TypeRisqueSectoriel.EXPOSITION_CHIMIQUE
        ],
        seuils_critiques={
            "hauteur_travail_m": 3.0,
            "temperature_max_c": 35.0,
            "bruit_max_db": 85.0,
            "silice_max_mg_m3": 0.025
        },
        reglements_applicables=["RSST", "CSTC", "LSST art. 51"],
        frequence_inspection=7,
        precision_prediction=0.937
    ),
    SecteurSCIAN.FABRICATION: ConfigSectorielle(
        code_scian="31-33",
        nom_secteur="Fabrication/Manufacturing",
        risques_principaux=[
            TypeRisqueSectoriel.TMS,
            TypeRisqueSectoriel.ECRASEMENT,
            TypeRisqueSectoriel.BRUIT,
            TypeRisqueSectoriel.EXPOSITION_CHIMIQUE
        ],
        seuils_critiques={
            "vibration_max_m_s2": 5.0,
            "bruit_max_db": 85.0,
            "temperature_max_c": 30.0,
            "cadence_max_par_heure": 60
        },
        reglements_applicables=["RSST", "LSST", "Règlement sur la santé et sécurité"],
        frequence_inspection=14,
        precision_prediction=0.912
    ),
    SecteurSCIAN.EXTRACTION: ConfigSectorielle(
        code_scian="21",
        nom_secteur="Extraction minière",
        risques_principaux=[
            TypeRisqueSectoriel.ECRASEMENT,
            TypeRisqueSectoriel.EXPOSITION_CHIMIQUE,
            TypeRisqueSectoriel.VIBRATION,
            TypeRisqueSectoriel.BRUIT
        ],
        seuils_critiques={
            "concentration_poussieres_mg_m3": 3.0,
            "vibration_max_m_s2": 5.0,
            "bruit_max_db": 85.0,
            "oxygene_min_pct": 19.5
        },
        reglements_applicables=["RSST", "Règlement sur les mines", "LSST"],
        frequence_inspection=7,
        precision_prediction=0.895
    ),
    SecteurSCIAN.SANTE: ConfigSectorielle(
        code_scian="62",
        nom_secteur="Soins de santé",
        risques_principaux=[
            TypeRisqueSectoriel.TMS,
            TypeRisqueSectoriel.BIOLOGIQUE,
            TypeRisqueSectoriel.PSYCHOSOCIAL,
            TypeRisqueSectoriel.EXPOSITION_CHIMIQUE
        ],
        seuils_critiques={
            "charge_max_kg": 23.0,
            "heures_debout_max": 6.0,
            "patients_par_infirmiere": 8,
            "niveau_stress_max": 7
        },
        reglements_applicables=["RSST", "LSST", "Code des professions"],
        frequence_inspection=30,
        precision_prediction=0.887
    ),
    SecteurSCIAN.TRANSPORT: ConfigSectorielle(
        code_scian="48-49",
        nom_secteur="Transport et entreposage",
        risques_principaux=[
            TypeRisqueSectoriel.TMS,
            TypeRisqueSectoriel.ECRASEMENT,
            TypeRisqueSectoriel.CHUTE_HAUTEUR,
            TypeRisqueSectoriel.PSYCHOSOCIAL
        ],
        seuils_critiques={
            "heures_conduite_max": 13.0,
            "charge_max_kg": 23.0,
            "temperature_entrepot_min_c": 10.0,
            "niveau_fatigue_max": 6
        },
        reglements_applicables=["RSST", "Règlement sur les heures de conduite", "LSST"],
        frequence_inspection=14,
        precision_prediction=0.901
    )
}


# ============================================
# CLASSE AGENT SECTORIEL
# ============================================

class AgentSectoriel:
    """
    Agent spécialisé pour un secteur SCIAN spécifique
    
    Fonctionnalités:
    - Analyse des risques spécifiques au secteur
    - Recommandations adaptées à la réglementation
    - Seuils et alertes personnalisés
    - Prédictions avec précision sectorielle
    """
    
    def __init__(self, secteur: SecteurSCIAN):
        self.secteur = secteur
        self.config = CONFIGURATIONS_SECTORIELLES.get(secteur)
        
        if not self.config:
            raise ValueError(f"Secteur {secteur} non configuré")
        
        self.agent_id = f"SC-{self.config.code_scian}"
        self.name = f"Agent_{self.config.nom_secteur.replace(' ', '_')}"
        self.logger = logging.getLogger(f"EDGY.Agent.{self.agent_id}")
        
        self.state = "idle"
        self.stats = {
            "analyses_effectuees": 0,
            "alertes_generees": 0,
            "recommandations_emises": 0,
            "precision_moyenne": self.config.precision_prediction
        }
        
        self.logger.info(f"Agent sectoriel {self.agent_id} initialisé - {self.config.nom_secteur}")
    
    def analyser_risques(self, donnees_capteurs: List[Dict]) -> Dict[str, Any]:
        """
        Analyser les risques spécifiques au secteur
        
        Args:
            donnees_capteurs: Liste des lectures de capteurs
            
        Returns:
            Analyse des risques avec alertes et recommandations
        """
        self.state = "processing"
        start_time = datetime.utcnow()
        
        alertes = []
        risques_detectes = []
        score_risque = 0.0
        
        for lecture in donnees_capteurs:
            sensor_type = lecture.get("sensor_type", "")
            value = lecture.get("value", 0)
            
            # Vérifier les seuils sectoriels
            alerte = self._verifier_seuils(sensor_type, value)
            if alerte:
                alertes.append(alerte)
                score_risque = max(score_risque, alerte["score_contribution"])
        
        # Déterminer les risques principaux concernés
        for risque in self.config.risques_principaux:
            if self._risque_concerne(risque, donnees_capteurs):
                risques_detectes.append(risque.value)
        
        # Générer recommandations
        recommandations = self._generer_recommandations(alertes, risques_detectes)
        
        # Mise à jour statistiques
        self.stats["analyses_effectuees"] += 1
        self.stats["alertes_generees"] += len(alertes)
        self.stats["recommandations_emises"] += len(recommandations)
        
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        self.state = "idle"
        
        return {
            "agent_id": self.agent_id,
            "secteur": self.config.nom_secteur,
            "code_scian": self.config.code_scian,
            "timestamp": datetime.utcnow().isoformat(),
            "score_risque": score_risque,
            "niveau_risque": self._calculer_niveau_risque(score_risque),
            "alertes": alertes,
            "risques_detectes": risques_detectes,
            "recommandations": recommandations,
            "reglements_applicables": self.config.reglements_applicables,
            "precision_prediction": self.config.precision_prediction,
            "processing_time_ms": processing_time
        }
    
    def _verifier_seuils(self, sensor_type: str, value: float) -> Optional[Dict]:
        """Vérifier si une valeur dépasse les seuils sectoriels"""
        
        # Mapping capteur -> seuil sectoriel
        mapping_seuils = {
            "temperature": "temperature_max_c",
            "noise": "bruit_max_db",
            "vibration": "vibration_max_m_s2",
            "dust": "concentration_poussieres_mg_m3",
            "silica": "silice_max_mg_m3",
            "oxygen": "oxygene_min_pct"
        }
        
        seuil_key = mapping_seuils.get(sensor_type)
        if not seuil_key or seuil_key not in self.config.seuils_critiques:
            return None
        
        seuil = self.config.seuils_critiques[seuil_key]
        
        # Cas spécial pour oxygène (minimum)
        if "min" in seuil_key:
            if value < seuil:
                return {
                    "type": "seuil_min_depasse",
                    "sensor_type": sensor_type,
                    "value": value,
                    "seuil": seuil,
                    "severite": "critical" if value < seuil * 0.95 else "high",
                    "score_contribution": 90 if value < seuil * 0.95 else 70
                }
        else:
            # Seuils maximum
            if value >= seuil:
                ratio = value / seuil
                if ratio >= 1.2:
                    severite = "critical"
                    score = 90
                elif ratio >= 1.0:
                    severite = "high"
                    score = 70
                else:
                    return None
                
                return {
                    "type": "seuil_max_depasse",
                    "sensor_type": sensor_type,
                    "value": value,
                    "seuil": seuil,
                    "severite": severite,
                    "score_contribution": score,
                    "reglementation": self._get_reglementation_applicable(sensor_type)
                }
        
        return None
    
    def _risque_concerne(self, risque: TypeRisqueSectoriel, donnees: List[Dict]) -> bool:
        """Vérifier si un type de risque est concerné par les données"""
        
        mapping_risque_capteur = {
            TypeRisqueSectoriel.THERMIQUE: ["temperature"],
            TypeRisqueSectoriel.BRUIT: ["noise"],
            TypeRisqueSectoriel.VIBRATION: ["vibration"],
            TypeRisqueSectoriel.EXPOSITION_CHIMIQUE: ["gas", "dust", "silica", "chemical"],
            TypeRisqueSectoriel.TMS: ["posture", "load", "repetition"],
            TypeRisqueSectoriel.CHUTE_HAUTEUR: ["height", "altitude"],
        }
        
        capteurs_associes = mapping_risque_capteur.get(risque, [])
        
        for lecture in donnees:
            if lecture.get("sensor_type") in capteurs_associes:
                return True
        
        return False
    
    def _generer_recommandations(self, alertes: List[Dict], risques: List[str]) -> List[Dict]:
        """Générer des recommandations adaptées au secteur"""
        
        recommandations = []
        
        templates_sectoriels = {
            "Construction": {
                "chute_hauteur": {
                    "titre": "Sécurisation travaux en hauteur",
                    "actions": ["Vérifier harnais", "Installer garde-corps", "Former équipe"],
                    "reference": "RSST art. 324-346"
                },
                "exposition_chimique": {
                    "titre": "Protection exposition silice",
                    "actions": ["Arrosage zones", "Port masque FFP3", "Contrôle poussières"],
                    "reference": "RSST art. 41-42"
                }
            },
            "Fabrication/Manufacturing": {
                "troubles_musculosquelettiques": {
                    "titre": "Prévention TMS poste de travail",
                    "actions": ["Rotation postes", "Pauses actives", "Aménagement ergonomique"],
                    "reference": "RSST art. 170"
                },
                "exposition_bruit": {
                    "titre": "Protection auditive obligatoire",
                    "actions": ["Port bouchons/casque", "Encoffrement machines", "Rotation exposition"],
                    "reference": "RSST art. 130-141"
                }
            },
            "Extraction minière": {
                "ecrasement": {
                    "titre": "Prévention effondrements",
                    "actions": ["Inspection soutènement", "Évacuation zone", "Renforcement"],
                    "reference": "Règlement sur les mines"
                }
            },
            "Soins de santé": {
                "risque_biologique": {
                    "titre": "Protection risques biologiques",
                    "actions": ["EPI appropriés", "Protocole décontamination", "Vaccination"],
                    "reference": "RSST art. 69"
                },
                "troubles_musculosquelettiques": {
                    "titre": "Prévention TMS manutention patients",
                    "actions": ["Utiliser lève-personne", "Travail en équipe", "Formation PDSB"],
                    "reference": "RSST art. 170"
                }
            }
        }
        
        templates = templates_sectoriels.get(self.config.nom_secteur, {})
        
        for risque in risques:
            if risque in templates:
                template = templates[risque]
                recommandations.append({
                    "id": f"REC-{self.agent_id}-{risque[:4].upper()}",
                    "titre": template["titre"],
                    "actions": template["actions"],
                    "reference_reglementaire": template["reference"],
                    "priorite": "P1" if any(a["severite"] == "critical" for a in alertes) else "P2",
                    "secteur": self.config.nom_secteur
                })
        
        return recommandations
    
    def _get_reglementation_applicable(self, sensor_type: str) -> str:
        """Retourner la réglementation applicable pour un type de capteur"""
        
        mapping = {
            "temperature": "RSST art. 116-120",
            "noise": "RSST art. 130-141",
            "vibration": "RSST art. 142-143",
            "dust": "RSST art. 41-42",
            "gas": "RSST art. 101-108"
        }
        
        return mapping.get(sensor_type, "RSST")
    
    def _calculer_niveau_risque(self, score: float) -> str:
        """Calculer le niveau de risque basé sur le score"""
        if score >= 80:
            return "critical"
        elif score >= 60:
            return "high"
        elif score >= 40:
            return "medium"
        elif score >= 20:
            return "low"
        return "minimal"
    
    def get_info(self) -> Dict[str, Any]:
        """Retourner les informations de l'agent"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "secteur": self.config.nom_secteur,
            "code_scian": self.config.code_scian,
            "risques_principaux": [r.value for r in self.config.risques_principaux],
            "seuils_critiques": self.config.seuils_critiques,
            "reglements_applicables": self.config.reglements_applicables,
            "frequence_inspection_jours": self.config.frequence_inspection,
            "precision_prediction": self.config.precision_prediction,
            "stats": self.stats
        }


# ============================================
# REGISTRE DES AGENTS SECTORIELS
# ============================================

class RegistreAgentsSectoriels:
    """
    Registre central des agents sectoriels SCIAN
    Gère la création et l'accès aux agents par secteur
    """
    
    def __init__(self):
        self.agents: Dict[str, AgentSectoriel] = {}
        self.logger = logging.getLogger("EDGY.RegistreAgents")
        
        # Initialiser les agents pour chaque secteur configuré
        for secteur in CONFIGURATIONS_SECTORIELLES.keys():
            self._creer_agent(secteur)
    
    def _creer_agent(self, secteur: SecteurSCIAN) -> AgentSectoriel:
        """Créer et enregistrer un agent sectoriel"""
        agent = AgentSectoriel(secteur)
        self.agents[secteur.value] = agent
        self.logger.info(f"Agent {agent.agent_id} enregistré")
        return agent
    
    def get_agent(self, code_scian: str) -> Optional[AgentSectoriel]:
        """Récupérer un agent par code SCIAN"""
        return self.agents.get(code_scian)
    
    def get_agent_pour_zone(self, zone_type: str) -> Optional[AgentSectoriel]:
        """Récupérer l'agent approprié pour un type de zone"""
        
        mapping_zone_secteur = {
            "chantier": SecteurSCIAN.CONSTRUCTION,
            "construction": SecteurSCIAN.CONSTRUCTION,
            "usine": SecteurSCIAN.FABRICATION,
            "manufacturing": SecteurSCIAN.FABRICATION,
            "fabrication": SecteurSCIAN.FABRICATION,
            "mine": SecteurSCIAN.EXTRACTION,
            "extraction": SecteurSCIAN.EXTRACTION,
            "hopital": SecteurSCIAN.SANTE,
            "clinique": SecteurSCIAN.SANTE,
            "sante": SecteurSCIAN.SANTE,
            "entrepot": SecteurSCIAN.TRANSPORT,
            "transport": SecteurSCIAN.TRANSPORT,
            "logistique": SecteurSCIAN.TRANSPORT
        }
        
        zone_lower = zone_type.lower()
        for keyword, secteur in mapping_zone_secteur.items():
            if keyword in zone_lower:
                return self.agents.get(secteur.value)
        
        return None
    
    def analyser_avec_agent_adapte(self, zone_type: str, donnees_capteurs: List[Dict]) -> Dict[str, Any]:
        """Analyser les données avec l'agent sectoriel approprié"""
        
        agent = self.get_agent_pour_zone(zone_type)
        
        if not agent:
            # Agent générique si aucun secteur trouvé
            return {
                "status": "no_agent",
                "message": f"Aucun agent sectoriel pour zone type: {zone_type}",
                "agents_disponibles": list(self.agents.keys())
            }
        
        return agent.analyser_risques(donnees_capteurs)
    
    def lister_agents(self) -> List[Dict]:
        """Lister tous les agents disponibles"""
        return [agent.get_info() for agent in self.agents.values()]
    
    def get_stats_globales(self) -> Dict[str, Any]:
        """Récupérer les statistiques globales"""
        total_analyses = sum(a.stats["analyses_effectuees"] for a in self.agents.values())
        total_alertes = sum(a.stats["alertes_generees"] for a in self.agents.values())
        total_recommandations = sum(a.stats["recommandations_emises"] for a in self.agents.values())
        
        return {
            "nombre_agents": len(self.agents),
            "secteurs_couverts": list(self.agents.keys()),
            "analyses_totales": total_analyses,
            "alertes_totales": total_alertes,
            "recommandations_totales": total_recommandations,
            "agents": {
                agent.agent_id: agent.stats 
                for agent in self.agents.values()
            }
        }


# ============================================
# FACTORY FUNCTIONS
# ============================================

def creer_registre_agents() -> RegistreAgentsSectoriels:
    """Factory pour créer le registre des agents sectoriels"""
    return RegistreAgentsSectoriels()


def creer_agent_construction() -> AgentSectoriel:
    """Factory pour créer l'agent Construction"""
    return AgentSectoriel(SecteurSCIAN.CONSTRUCTION)


def creer_agent_fabrication() -> AgentSectoriel:
    """Factory pour créer l'agent Fabrication"""
    return AgentSectoriel(SecteurSCIAN.FABRICATION)


def creer_agent_extraction() -> AgentSectoriel:
    """Factory pour créer l'agent Extraction minière"""
    return AgentSectoriel(SecteurSCIAN.EXTRACTION)


def creer_agent_sante() -> AgentSectoriel:
    """Factory pour créer l'agent Santé"""
    return AgentSectoriel(SecteurSCIAN.SANTE)


def creer_agent_transport() -> AgentSectoriel:
    """Factory pour créer l'agent Transport"""
    return AgentSectoriel(SecteurSCIAN.TRANSPORT)


# ============================================
# EXPORTS
# ============================================

__all__ = [
    "SecteurSCIAN",
    "TypeRisqueSectoriel",
    "ConfigSectorielle",
    "AgentSectoriel",
    "RegistreAgentsSectoriels",
    "CONFIGURATIONS_SECTORIELLES",
    "creer_registre_agents",
    "creer_agent_construction",
    "creer_agent_fabrication",
    "creer_agent_extraction",
    "creer_agent_sante",
    "creer_agent_transport"
]
