#!/usr/bin/env python3
"""
Agent S1 - Router Intelligent
EDGY-AgenticX5

Responsabilités:
- Routage intelligent des requêtes vers les agents appropriés
- Classification des demandes par type et urgence
- Orchestration des workflows multi-agents
- Gestion des priorités et de la charge
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import re


# ============================================
# ÉNUMÉRATIONS
# ============================================

class TypeRequete(str, Enum):
    """Types de requêtes supportées"""
    COLLECTE = "collecte"
    ANALYSE = "analyse"
    PREDICTION = "prediction"
    RECOMMANDATION = "recommandation"
    ALERTE = "alerte"
    RAPPORT = "rapport"
    INSPECTION = "inspection"
    INCIDENT = "incident"


class NiveauUrgence(str, Enum):
    """Niveaux d'urgence des requêtes"""
    CRITIQUE = "critical"
    HAUTE = "high"
    NORMALE = "normal"
    BASSE = "low"


class StatutRoutage(str, Enum):
    """Statut du routage"""
    ROUTE = "routed"
    EN_ATTENTE = "pending"
    ECHEC = "failed"
    COMPLETE = "completed"


# ============================================
# MODÈLES DE DONNÉES
# ============================================

@dataclass
class RequeteEntree:
    """Requête entrante à router"""
    id: str
    contenu: Dict[str, Any]
    source: str
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DecisionRoutage:
    """Décision de routage"""
    requete_id: str
    type_requete: TypeRequete
    urgence: NiveauUrgence
    agents_cibles: List[str]
    pipeline: List[str]
    priorite: int
    raison: str
    confiance: float


# ============================================
# AGENT S1 - ROUTER
# ============================================

class AgentRouter:
    """
    Agent S1 - Router Intelligent
    
    Fonctionnalités:
    - Classification automatique des requêtes
    - Routage vers agents spécialisés
    - Gestion des pipelines multi-agents
    - Équilibrage de charge
    """
    
    def __init__(self):
        self.agent_id = "S1"
        self.name = "Router_Intelligent"
        self.logger = logging.getLogger(f"EDGY.Agent.{self.agent_id}")
        
        self.state = "idle"
        
        # Registre des agents disponibles
        self.agents_disponibles = {
            # Agents fondamentaux
            "perception": {"capabilities": ["collecte", "detection"], "charge": 0},
            "analysis": {"capabilities": ["analyse", "evaluation"], "charge": 0},
            "recommendation": {"capabilities": ["recommandation", "action"], "charge": 0},
            "security_manager": {"capabilities": ["validation", "securite"], "charge": 0},
            "orchestrator": {"capabilities": ["coordination", "workflow"], "charge": 0},
            
            # Agents de collecte
            "A1": {"capabilities": ["collecte", "normalisation"], "charge": 0},
            
            # Agents analytiques
            "AN1": {"capabilities": ["prediction", "analyse_risque"], "charge": 0},
            
            # Agents sectoriels
            "SC-23": {"capabilities": ["construction", "analyse"], "charge": 0},
            "SC-31-33": {"capabilities": ["fabrication", "analyse"], "charge": 0},
            "SC-21": {"capabilities": ["extraction", "analyse"], "charge": 0},
            "SC-62": {"capabilities": ["sante", "analyse"], "charge": 0},
            "SC-48-49": {"capabilities": ["transport", "analyse"], "charge": 0}
        }
        
        # Règles de routage
        self.regles_routage = [
            {
                "pattern": r"(capteur|sensor|mesure|température|bruit)",
                "type": TypeRequete.COLLECTE,
                "agents": ["A1", "perception"],
                "pipeline": ["A1", "perception", "analysis"]
            },
            {
                "pattern": r"(prédire|prédiction|anticiper|futur|risque)",
                "type": TypeRequete.PREDICTION,
                "agents": ["AN1"],
                "pipeline": ["A1", "AN1", "recommendation"]
            },
            {
                "pattern": r"(analyser|analyse|évaluer|diagnostic)",
                "type": TypeRequete.ANALYSE,
                "agents": ["analysis", "AN1"],
                "pipeline": ["perception", "analysis", "recommendation"]
            },
            {
                "pattern": r"(recommander|action|mesure|corriger)",
                "type": TypeRequete.RECOMMANDATION,
                "agents": ["recommendation"],
                "pipeline": ["analysis", "recommendation"]
            },
            {
                "pattern": r"(alerte|urgence|danger|critique|immédiat)",
                "type": TypeRequete.ALERTE,
                "agents": ["security_manager", "orchestrator"],
                "pipeline": ["perception", "security_manager", "orchestrator", "recommendation"]
            },
            {
                "pattern": r"(rapport|résumé|statistique|bilan)",
                "type": TypeRequete.RAPPORT,
                "agents": ["analysis"],
                "pipeline": ["A1", "analysis"]
            },
            {
                "pattern": r"(inspection|audit|vérification|contrôle)",
                "type": TypeRequete.INSPECTION,
                "agents": ["A1", "analysis", "recommendation"],
                "pipeline": ["A1", "analysis", "recommendation"]
            },
            {
                "pattern": r"(incident|accident|blessure|near.?miss)",
                "type": TypeRequete.INCIDENT,
                "agents": ["security_manager", "AN1", "recommendation"],
                "pipeline": ["perception", "security_manager", "AN1", "analysis", "recommendation"]
            }
        ]
        
        # Mapping secteur -> agent sectoriel
        self.mapping_secteurs = {
            "construction": "SC-23",
            "chantier": "SC-23",
            "batiment": "SC-23",
            "fabrication": "SC-31-33",
            "usine": "SC-31-33",
            "manufacturing": "SC-31-33",
            "mine": "SC-21",
            "extraction": "SC-21",
            "carriere": "SC-21",
            "hopital": "SC-62",
            "clinique": "SC-62",
            "sante": "SC-62",
            "transport": "SC-48-49",
            "entrepot": "SC-48-49",
            "logistique": "SC-48-49"
        }
        
        # Statistiques
        self.stats = {
            "requetes_routees": 0,
            "requetes_critiques": 0,
            "routage_par_type": {t.value: 0 for t in TypeRequete},
            "agents_utilises": {}
        }
        
        self.logger.info(f"Agent {self.agent_id} initialisé - {self.name}")
    
    def router(self, requete: Dict[str, Any]) -> Dict[str, Any]:
        """
        Point d'entrée principal pour router une requête
        
        Args:
            requete: Dictionnaire contenant la requête à router
            
        Returns:
            Décision de routage avec agents cibles et pipeline
        """
        self.state = "routing"
        start_time = datetime.utcnow()
        
        # Créer l'objet requête
        requete_obj = RequeteEntree(
            id=requete.get("id", f"REQ-{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"),
            contenu=requete.get("contenu", requete),
            source=requete.get("source", "api"),
            timestamp=datetime.utcnow(),
            metadata=requete.get("metadata", {})
        )
        
        # Classifier la requête
        type_requete, confiance_type = self._classifier_requete(requete_obj)
        
        # Déterminer l'urgence
        urgence = self._evaluer_urgence(requete_obj, type_requete)
        
        # Sélectionner les agents
        agents_cibles, pipeline = self._selectionner_agents(requete_obj, type_requete)
        
        # Ajouter agent sectoriel si pertinent
        agent_sectoriel = self._identifier_agent_sectoriel(requete_obj)
        if agent_sectoriel and agent_sectoriel not in agents_cibles:
            agents_cibles.append(agent_sectoriel)
            pipeline.insert(1, agent_sectoriel)
        
        # Calculer la priorité
        priorite = self._calculer_priorite(urgence, type_requete)
        
        # Créer la décision
        decision = DecisionRoutage(
            requete_id=requete_obj.id,
            type_requete=type_requete,
            urgence=urgence,
            agents_cibles=agents_cibles,
            pipeline=pipeline,
            priorite=priorite,
            raison=self._generer_raison_routage(type_requete, agents_cibles),
            confiance=confiance_type
        )
        
        # Mise à jour statistiques
        self._maj_statistiques(decision)
        
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        self.state = "idle"
        
        return {
            "agent_id": self.agent_id,
            "timestamp": datetime.utcnow().isoformat(),
            "statut": StatutRoutage.ROUTE.value,
            "requete_id": decision.requete_id,
            "classification": {
                "type": decision.type_requete.value,
                "urgence": decision.urgence.value,
                "confiance": round(decision.confiance, 2)
            },
            "routage": {
                "agents_cibles": decision.agents_cibles,
                "pipeline": decision.pipeline,
                "priorite": decision.priorite
            },
            "raison": decision.raison,
            "processing_time_ms": processing_time
        }
    
    def _classifier_requete(self, requete: RequeteEntree) -> Tuple[TypeRequete, float]:
        """Classifier la requête par type"""
        
        # Construire le texte à analyser
        texte = self._extraire_texte(requete.contenu)
        texte_lower = texte.lower()
        
        meilleur_match = None
        meilleure_confiance = 0.0
        
        for regle in self.regles_routage:
            pattern = regle["pattern"]
            matches = re.findall(pattern, texte_lower, re.IGNORECASE)
            
            if matches:
                confiance = min(len(matches) * 0.25 + 0.5, 0.95)
                if confiance > meilleure_confiance:
                    meilleure_confiance = confiance
                    meilleur_match = regle["type"]
        
        # Défaut si aucun match
        if not meilleur_match:
            meilleur_match = TypeRequete.ANALYSE
            meilleure_confiance = 0.5
        
        return meilleur_match, meilleure_confiance
    
    def _evaluer_urgence(self, requete: RequeteEntree, type_requete: TypeRequete) -> NiveauUrgence:
        """Évaluer le niveau d'urgence de la requête"""
        
        texte = self._extraire_texte(requete.contenu).lower()
        
        # Mots-clés d'urgence
        mots_critiques = ["critique", "urgent", "immédiat", "danger", "accident", "blessure", "évacuation"]
        mots_hauts = ["alerte", "attention", "rapidement", "prioritaire", "important"]
        
        # Vérifier les mots-clés
        for mot in mots_critiques:
            if mot in texte:
                return NiveauUrgence.CRITIQUE
        
        for mot in mots_hauts:
            if mot in texte:
                return NiveauUrgence.HAUTE
        
        # Certains types sont intrinsèquement plus urgents
        if type_requete == TypeRequete.ALERTE:
            return NiveauUrgence.HAUTE
        elif type_requete == TypeRequete.INCIDENT:
            return NiveauUrgence.CRITIQUE
        
        # Vérifier les données de capteurs
        donnees = requete.contenu
        if isinstance(donnees, dict):
            risk_level = donnees.get("risk_level", "")
            if risk_level == "critical":
                return NiveauUrgence.CRITIQUE
            elif risk_level == "high":
                return NiveauUrgence.HAUTE
        
        return NiveauUrgence.NORMALE
    
    def _selectionner_agents(self, requete: RequeteEntree, type_requete: TypeRequete) -> Tuple[List[str], List[str]]:
        """Sélectionner les agents appropriés"""
        
        # Trouver la règle correspondante
        for regle in self.regles_routage:
            if regle["type"] == type_requete:
                agents = regle["agents"].copy()
                pipeline = regle["pipeline"].copy()
                
                # Équilibrage de charge simple
                agents = self._equilibrer_charge(agents)
                
                return agents, pipeline
        
        # Défaut
        return ["analysis", "recommendation"], ["perception", "analysis", "recommendation"]
    
    def _identifier_agent_sectoriel(self, requete: RequeteEntree) -> Optional[str]:
        """Identifier l'agent sectoriel pertinent"""
        
        texte = self._extraire_texte(requete.contenu).lower()
        
        # Chercher des mots-clés sectoriels
        for keyword, agent_id in self.mapping_secteurs.items():
            if keyword in texte:
                return agent_id
        
        # Vérifier zone_id si présent
        zone_id = requete.contenu.get("zone_id", "")
        zone_lower = zone_id.lower()
        for keyword, agent_id in self.mapping_secteurs.items():
            if keyword in zone_lower:
                return agent_id
        
        return None
    
    def _equilibrer_charge(self, agents: List[str]) -> List[str]:
        """Équilibrer la charge entre agents similaires"""
        
        # Trier par charge (le moins chargé en premier)
        agents_tries = sorted(
            agents,
            key=lambda a: self.agents_disponibles.get(a, {}).get("charge", 0)
        )
        
        # Incrémenter la charge des agents sélectionnés
        for agent in agents_tries:
            if agent in self.agents_disponibles:
                self.agents_disponibles[agent]["charge"] += 1
        
        return agents_tries
    
    def _calculer_priorite(self, urgence: NiveauUrgence, type_requete: TypeRequete) -> int:
        """Calculer la priorité numérique (1 = plus haute)"""
        
        priorite_base = {
            NiveauUrgence.CRITIQUE: 1,
            NiveauUrgence.HAUTE: 3,
            NiveauUrgence.NORMALE: 5,
            NiveauUrgence.BASSE: 7
        }
        
        ajustement_type = {
            TypeRequete.INCIDENT: -1,
            TypeRequete.ALERTE: 0,
            TypeRequete.PREDICTION: 1,
            TypeRequete.ANALYSE: 2,
            TypeRequete.RAPPORT: 3
        }
        
        priorite = priorite_base.get(urgence, 5) + ajustement_type.get(type_requete, 0)
        return max(1, min(priorite, 10))
    
    def _generer_raison_routage(self, type_requete: TypeRequete, agents: List[str]) -> str:
        """Générer une explication du routage"""
        
        raisons = {
            TypeRequete.COLLECTE: "Requête de collecte de données - routage vers agents de collecte",
            TypeRequete.ANALYSE: "Demande d'analyse - routage vers agents analytiques",
            TypeRequete.PREDICTION: "Demande prédictive - routage vers le prédicteur AN1",
            TypeRequete.RECOMMANDATION: "Demande de recommandations - routage vers agent de recommandation",
            TypeRequete.ALERTE: "Alerte détectée - routage prioritaire vers security manager",
            TypeRequete.RAPPORT: "Génération de rapport - routage vers agents d'analyse",
            TypeRequete.INSPECTION: "Inspection demandée - workflow complet activé",
            TypeRequete.INCIDENT: "Incident signalé - activation du protocole d'urgence"
        }
        
        return f"{raisons.get(type_requete, 'Routage standard')} → [{', '.join(agents)}]"
    
    def _extraire_texte(self, contenu: Any) -> str:
        """Extraire le texte d'un contenu (dict, str, list)"""
        
        if isinstance(contenu, str):
            return contenu
        elif isinstance(contenu, dict):
            # Concaténer les valeurs textuelles
            textes = []
            for key, value in contenu.items():
                textes.append(str(key))
                if isinstance(value, str):
                    textes.append(value)
                elif isinstance(value, list):
                    textes.extend([str(v) for v in value])
            return " ".join(textes)
        elif isinstance(contenu, list):
            return " ".join([self._extraire_texte(item) for item in contenu])
        else:
            return str(contenu)
    
    def _maj_statistiques(self, decision: DecisionRoutage):
        """Mettre à jour les statistiques"""
        
        self.stats["requetes_routees"] += 1
        
        if decision.urgence == NiveauUrgence.CRITIQUE:
            self.stats["requetes_critiques"] += 1
        
        self.stats["routage_par_type"][decision.type_requete.value] += 1
        
        for agent in decision.agents_cibles:
            if agent not in self.stats["agents_utilises"]:
                self.stats["agents_utilises"][agent] = 0
            self.stats["agents_utilises"][agent] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Récupérer les statistiques du router"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "state": self.state,
            "requetes_routees": self.stats["requetes_routees"],
            "requetes_critiques": self.stats["requetes_critiques"],
            "routage_par_type": self.stats["routage_par_type"],
            "agents_utilises": self.stats["agents_utilises"],
            "agents_disponibles": list(self.agents_disponibles.keys())
        }
    
    def enregistrer_agent(self, agent_id: str, capabilities: List[str]):
        """Enregistrer un nouvel agent dans le router"""
        
        self.agents_disponibles[agent_id] = {
            "capabilities": capabilities,
            "charge": 0
        }
        self.logger.info(f"Agent {agent_id} enregistré avec capabilities: {capabilities}")
    
    def reset_charge(self):
        """Réinitialiser les compteurs de charge"""
        
        for agent in self.agents_disponibles:
            self.agents_disponibles[agent]["charge"] = 0


# ============================================
# FACTORY
# ============================================

def creer_agent_router() -> AgentRouter:
    """Factory pour créer l'agent router"""
    return AgentRouter()


# ============================================
# EXPORTS
# ============================================

__all__ = [
    "TypeRequete",
    "NiveauUrgence",
    "StatutRoutage",
    "RequeteEntree",
    "DecisionRoutage",
    "AgentRouter",
    "creer_agent_router"
]
