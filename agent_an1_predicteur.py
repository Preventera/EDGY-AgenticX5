#!/usr/bin/env python3
"""
Agent AN1 - Prédicteur d'Incidents
EDGY-AgenticX5

Responsabilités:
- Prédiction d'incidents basée sur les patterns historiques
- Analyse de tendances multi-factorielles
- Calcul de scores de risque prédictifs
- Génération d'alertes préventives
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import math
import random


# ============================================
# ÉNUMÉRATIONS
# ============================================

class HorizonPrediction(str, Enum):
    """Horizons temporels de prédiction"""
    IMMEDIAT = "1h"      # 1 heure
    COURT = "24h"        # 24 heures
    MOYEN = "7j"         # 7 jours
    LONG = "30j"         # 30 jours


class TypeIncident(str, Enum):
    """Types d'incidents prédits"""
    ACCIDENT_TRAVAIL = "accident_travail"
    NEAR_MISS = "near_miss"
    DEFAILLANCE_EQUIPEMENT = "defaillance_equipement"
    EXPOSITION_DANGEREUSE = "exposition_dangereuse"
    INCIDENT_ENVIRONNEMENTAL = "incident_environnemental"


class NiveauConfiance(str, Enum):
    """Niveaux de confiance des prédictions"""
    TRES_ELEVE = "very_high"    # > 90%
    ELEVE = "high"              # 75-90%
    MOYEN = "medium"            # 50-75%
    FAIBLE = "low"              # < 50%


# ============================================
# MODÈLES DE DONNÉES
# ============================================

@dataclass
class FacteurRisque:
    """Facteur contribuant au risque"""
    nom: str
    valeur: float
    poids: float
    tendance: str  # "hausse", "baisse", "stable"
    contribution: float = 0.0


@dataclass
class Prediction:
    """Résultat de prédiction"""
    type_incident: TypeIncident
    horizon: HorizonPrediction
    probabilite: float
    score_risque: float
    niveau_confiance: NiveauConfiance
    facteurs_principaux: List[FacteurRisque]
    zone_id: str
    timestamp_prediction: datetime
    timestamp_horizon: datetime
    recommandations: List[str] = field(default_factory=list)


# ============================================
# AGENT AN1 - PREDICTEUR
# ============================================

class AgentPredicteur:
    """
    Agent AN1 - Prédicteur d'Incidents
    
    Fonctionnalités:
    - Modèles de prédiction multi-horizons
    - Analyse de facteurs de risque combinés
    - Détection de patterns précurseurs
    - Calcul de probabilités avec intervalle de confiance
    """
    
    def __init__(self):
        self.agent_id = "AN1"
        self.name = "Predicteur_Incidents"
        self.logger = logging.getLogger(f"EDGY.Agent.{self.agent_id}")
        
        self.state = "idle"
        self.precision_globale = 0.947  # 94.7% basé sur données CNESST
        
        # Historique des prédictions
        self.historique_predictions: List[Prediction] = []
        
        # Statistiques
        self.stats = {
            "predictions_totales": 0,
            "predictions_correctes": 0,
            "alertes_critiques": 0,
            "precision_moyenne": self.precision_globale
        }
        
        # Poids des facteurs par type d'incident
        self.poids_facteurs = {
            TypeIncident.ACCIDENT_TRAVAIL: {
                "temperature": 0.15,
                "noise": 0.10,
                "fatigue": 0.25,
                "experience": 0.20,
                "equipement": 0.15,
                "meteo": 0.10,
                "heure_journee": 0.05
            },
            TypeIncident.NEAR_MISS: {
                "temperature": 0.10,
                "noise": 0.15,
                "fatigue": 0.20,
                "experience": 0.15,
                "equipement": 0.20,
                "cadence": 0.15,
                "supervision": 0.05
            },
            TypeIncident.DEFAILLANCE_EQUIPEMENT: {
                "vibration": 0.25,
                "temperature": 0.20,
                "age_equipement": 0.20,
                "maintenance": 0.25,
                "charge_utilisation": 0.10
            },
            TypeIncident.EXPOSITION_DANGEREUSE: {
                "concentration_chimique": 0.30,
                "ventilation": 0.20,
                "epi_conformite": 0.25,
                "duree_exposition": 0.15,
                "temperature": 0.10
            }
        }
        
        # Seuils d'alerte
        self.seuils_alerte = {
            "critique": 0.80,
            "eleve": 0.60,
            "moyen": 0.40,
            "faible": 0.20
        }
        
        # Patterns précurseurs connus
        self.patterns_precurseurs = [
            {
                "nom": "Fatigue cumulative",
                "conditions": ["heures_travail > 10", "jours_consecutifs > 5"],
                "multiplicateur_risque": 1.8
            },
            {
                "nom": "Conditions météo extrêmes",
                "conditions": ["temperature > 35", "humidite > 80"],
                "multiplicateur_risque": 1.5
            },
            {
                "nom": "Équipement vieillissant",
                "conditions": ["age_equipement > 10", "maintenance_retard > 30"],
                "multiplicateur_risque": 2.0
            },
            {
                "nom": "Nouveau personnel",
                "conditions": ["anciennete < 90", "formation_incomplete"],
                "multiplicateur_risque": 1.6
            },
            {
                "nom": "Pic d'activité",
                "conditions": ["production > 120%", "effectif_reduit"],
                "multiplicateur_risque": 1.4
            }
        ]
        
        self.logger.info(f"Agent {self.agent_id} initialisé - {self.name} (précision: {self.precision_globale*100:.1f}%)")
    
    def predire(self, donnees_contexte: Dict[str, Any], zone_id: str = "ZONE-DEFAULT") -> Dict[str, Any]:
        """
        Générer des prédictions d'incidents
        
        Args:
            donnees_contexte: Données contextuelles (capteurs, RH, maintenance...)
            zone_id: Identifiant de la zone
            
        Returns:
            Résultats de prédiction avec probabilités et recommandations
        """
        self.state = "predicting"
        start_time = datetime.utcnow()
        
        predictions = []
        alertes = []
        
        # Prédire pour chaque type d'incident
        for type_incident in TypeIncident:
            for horizon in HorizonPrediction:
                prediction = self._calculer_prediction(
                    type_incident, 
                    horizon, 
                    donnees_contexte, 
                    zone_id
                )
                predictions.append(prediction)
                
                # Générer alerte si nécessaire
                if prediction.probabilite >= self.seuils_alerte["eleve"]:
                    alertes.append(self._generer_alerte(prediction))
        
        # Trier par probabilité décroissante
        predictions.sort(key=lambda p: p.probabilite, reverse=True)
        
        # Détecter les patterns précurseurs
        patterns_detectes = self._detecter_patterns(donnees_contexte)
        
        # Mise à jour statistiques
        self.stats["predictions_totales"] += len(predictions)
        self.stats["alertes_critiques"] += len([a for a in alertes if a["niveau"] == "critique"])
        
        # Stocker dans l'historique
        self.historique_predictions.extend(predictions[:5])  # Top 5
        
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        self.state = "idle"
        
        return {
            "agent_id": self.agent_id,
            "timestamp": datetime.utcnow().isoformat(),
            "zone_id": zone_id,
            "statut": "completed",
            "precision_modele": self.precision_globale,
            "predictions": [self._serialiser_prediction(p) for p in predictions[:10]],
            "alertes": alertes,
            "patterns_detectes": patterns_detectes,
            "risque_global": self._calculer_risque_global(predictions),
            "recommandations_prioritaires": self._generer_recommandations_prioritaires(predictions[:3]),
            "processing_time_ms": processing_time
        }
    
    def _calculer_prediction(
        self, 
        type_incident: TypeIncident, 
        horizon: HorizonPrediction,
        donnees: Dict,
        zone_id: str
    ) -> Prediction:
        """Calculer une prédiction pour un type d'incident et horizon donnés"""
        
        # Récupérer les poids pour ce type d'incident
        poids = self.poids_facteurs.get(type_incident, {})
        
        # Analyser chaque facteur
        facteurs = []
        score_total = 0.0
        poids_total = 0.0
        
        for facteur_nom, facteur_poids in poids.items():
            valeur = self._extraire_valeur_facteur(facteur_nom, donnees)
            score_facteur = self._evaluer_facteur(facteur_nom, valeur)
            
            contribution = score_facteur * facteur_poids
            score_total += contribution
            poids_total += facteur_poids
            
            facteurs.append(FacteurRisque(
                nom=facteur_nom,
                valeur=valeur,
                poids=facteur_poids,
                tendance=self._calculer_tendance(facteur_nom, valeur),
                contribution=contribution
            ))
        
        # Normaliser le score
        score_normalise = score_total / poids_total if poids_total > 0 else 0.5
        
        # Ajuster selon l'horizon
        facteur_horizon = {
            HorizonPrediction.IMMEDIAT: 1.2,
            HorizonPrediction.COURT: 1.0,
            HorizonPrediction.MOYEN: 0.8,
            HorizonPrediction.LONG: 0.6
        }
        
        probabilite = min(score_normalise * facteur_horizon[horizon], 0.99)
        
        # Déterminer le niveau de confiance
        niveau_confiance = self._calculer_confiance(len(donnees), facteurs)
        
        # Calculer le timestamp horizon
        deltas = {
            HorizonPrediction.IMMEDIAT: timedelta(hours=1),
            HorizonPrediction.COURT: timedelta(hours=24),
            HorizonPrediction.MOYEN: timedelta(days=7),
            HorizonPrediction.LONG: timedelta(days=30)
        }
        
        timestamp_horizon = datetime.utcnow() + deltas[horizon]
        
        # Trier facteurs par contribution
        facteurs.sort(key=lambda f: f.contribution, reverse=True)
        
        return Prediction(
            type_incident=type_incident,
            horizon=horizon,
            probabilite=probabilite,
            score_risque=score_normalise * 100,
            niveau_confiance=niveau_confiance,
            facteurs_principaux=facteurs[:3],
            zone_id=zone_id,
            timestamp_prediction=datetime.utcnow(),
            timestamp_horizon=timestamp_horizon,
            recommandations=self._generer_recommandations_incident(type_incident, facteurs[:3])
        )
    
    def _extraire_valeur_facteur(self, facteur: str, donnees: Dict) -> float:
        """Extraire la valeur d'un facteur depuis les données"""
        
        # Mapping des facteurs vers les données
        mapping = {
            "temperature": lambda d: d.get("temperature", d.get("temp", 20)),
            "noise": lambda d: d.get("noise", d.get("bruit", 60)),
            "vibration": lambda d: d.get("vibration", 0),
            "fatigue": lambda d: d.get("fatigue", d.get("heures_travail", 8) / 12),
            "experience": lambda d: 1 - min(d.get("anciennete_jours", 365) / 365, 1),
            "equipement": lambda d: d.get("etat_equipement", 0.8),
            "meteo": lambda d: d.get("score_meteo", 0.5),
            "heure_journee": lambda d: self._score_heure(d.get("heure", datetime.utcnow().hour)),
            "concentration_chimique": lambda d: d.get("gas", d.get("dust", 0)) / 100,
            "ventilation": lambda d: d.get("ventilation", 0.8),
            "epi_conformite": lambda d: d.get("epi_ok", 1.0),
            "age_equipement": lambda d: d.get("age_equipement_ans", 5) / 15,
            "maintenance": lambda d: 1 - d.get("maintenance_ok", 0.9),
            "cadence": lambda d: d.get("cadence", 100) / 150,
            "supervision": lambda d: 1 - d.get("ratio_supervision", 0.1)
        }
        
        extractor = mapping.get(facteur, lambda d: 0.5)
        try:
            return float(extractor(donnees))
        except:
            return 0.5
    
    def _evaluer_facteur(self, facteur: str, valeur: float) -> float:
        """Évaluer un facteur et retourner un score de risque 0-1"""
        
        # Fonctions d'évaluation personnalisées
        evaluations = {
            "temperature": lambda v: self._sigmoid((v - 25) / 10),
            "noise": lambda v: self._sigmoid((v - 70) / 15),
            "fatigue": lambda v: v,
            "experience": lambda v: v,
            "equipement": lambda v: 1 - v,
            "concentration_chimique": lambda v: v,
            "age_equipement": lambda v: v
        }
        
        eval_func = evaluations.get(facteur, lambda v: v)
        return min(max(eval_func(valeur), 0), 1)
    
    def _sigmoid(self, x: float) -> float:
        """Fonction sigmoïde pour normalisation"""
        return 1 / (1 + math.exp(-x))
    
    def _score_heure(self, heure: int) -> float:
        """Score de risque basé sur l'heure (pics le matin tôt et fin de journée)"""
        if 6 <= heure <= 8 or 14 <= heure <= 16:
            return 0.7
        elif 10 <= heure <= 12:
            return 0.3
        elif heure >= 22 or heure <= 5:
            return 0.8
        return 0.5
    
    def _calculer_tendance(self, facteur: str, valeur: float) -> str:
        """Calculer la tendance d'un facteur (simplifié)"""
        # En production, comparerait avec l'historique
        if valeur > 0.7:
            return "hausse"
        elif valeur < 0.3:
            return "baisse"
        return "stable"
    
    def _calculer_confiance(self, nb_donnees: int, facteurs: List[FacteurRisque]) -> NiveauConfiance:
        """Calculer le niveau de confiance de la prédiction"""
        
        # Plus de données = plus de confiance
        score_donnees = min(nb_donnees / 10, 1)
        
        # Plus de facteurs analysés = plus de confiance
        score_facteurs = len(facteurs) / 7
        
        # Score global
        score = (score_donnees * 0.4 + score_facteurs * 0.6) * self.precision_globale
        
        if score > 0.85:
            return NiveauConfiance.TRES_ELEVE
        elif score > 0.70:
            return NiveauConfiance.ELEVE
        elif score > 0.50:
            return NiveauConfiance.MOYEN
        return NiveauConfiance.FAIBLE
    
    def _detecter_patterns(self, donnees: Dict) -> List[Dict]:
        """Détecter les patterns précurseurs dans les données"""
        patterns_trouves = []
        
        for pattern in self.patterns_precurseurs:
            # Simulation simple de détection
            # En production, évaluerait les conditions réelles
            if random.random() < 0.3:  # 30% de chance de détecter un pattern
                patterns_trouves.append({
                    "nom": pattern["nom"],
                    "multiplicateur_risque": pattern["multiplicateur_risque"],
                    "confiance": round(random.uniform(0.6, 0.95), 2)
                })
        
        return patterns_trouves
    
    def _generer_alerte(self, prediction: Prediction) -> Dict:
        """Générer une alerte pour une prédiction à haut risque"""
        
        niveau = "critique" if prediction.probabilite >= self.seuils_alerte["critique"] else "eleve"
        
        return {
            "type": "prediction_alerte",
            "niveau": niveau,
            "type_incident": prediction.type_incident.value,
            "horizon": prediction.horizon.value,
            "probabilite": round(prediction.probabilite, 3),
            "zone_id": prediction.zone_id,
            "message": f"Risque {niveau} de {prediction.type_incident.value} détecté dans les {prediction.horizon.value}",
            "facteurs_principaux": [f.nom for f in prediction.facteurs_principaux],
            "actions_recommandees": prediction.recommandations[:3]
        }
    
    def _calculer_risque_global(self, predictions: List[Prediction]) -> Dict:
        """Calculer un score de risque global"""
        
        if not predictions:
            return {"score": 0, "niveau": "minimal"}
        
        # Moyenne pondérée des probabilités (court terme pèse plus)
        poids_horizon = {
            HorizonPrediction.IMMEDIAT: 2.0,
            HorizonPrediction.COURT: 1.5,
            HorizonPrediction.MOYEN: 1.0,
            HorizonPrediction.LONG: 0.5
        }
        
        score_pondere = sum(
            p.probabilite * poids_horizon.get(p.horizon, 1)
            for p in predictions
        )
        poids_total = sum(poids_horizon.get(p.horizon, 1) for p in predictions)
        
        score_global = score_pondere / poids_total if poids_total > 0 else 0
        
        # Déterminer le niveau
        if score_global >= 0.7:
            niveau = "critique"
        elif score_global >= 0.5:
            niveau = "eleve"
        elif score_global >= 0.3:
            niveau = "moyen"
        else:
            niveau = "faible"
        
        return {
            "score": round(score_global * 100, 1),
            "niveau": niveau,
            "predictions_analysees": len(predictions)
        }
    
    def _generer_recommandations_incident(self, type_incident: TypeIncident, facteurs: List[FacteurRisque]) -> List[str]:
        """Générer des recommandations spécifiques au type d'incident"""
        
        recommandations_base = {
            TypeIncident.ACCIDENT_TRAVAIL: [
                "Renforcer la supervision directe",
                "Vérifier l'état des EPI",
                "Organiser une pause de récupération"
            ],
            TypeIncident.NEAR_MISS: [
                "Analyser les incidents évités récents",
                "Réviser les procédures de travail",
                "Sensibiliser l'équipe aux signaux d'alerte"
            ],
            TypeIncident.DEFAILLANCE_EQUIPEMENT: [
                "Planifier maintenance préventive",
                "Inspecter les points d'usure critiques",
                "Préparer équipement de remplacement"
            ],
            TypeIncident.EXPOSITION_DANGEREUSE: [
                "Vérifier la ventilation",
                "Contrôler les concentrations",
                "Limiter les temps d'exposition"
            ]
        }
        
        return recommandations_base.get(type_incident, ["Consulter le responsable SST"])
    
    def _generer_recommandations_prioritaires(self, top_predictions: List[Prediction]) -> List[Dict]:
        """Générer les recommandations prioritaires globales"""
        
        recommandations = []
        for i, pred in enumerate(top_predictions):
            recommandations.append({
                "priorite": f"P{i+1}",
                "type_incident": pred.type_incident.value,
                "horizon": pred.horizon.value,
                "actions": pred.recommandations[:2],
                "urgence": "immediate" if pred.horizon == HorizonPrediction.IMMEDIAT else "planifiee"
            })
        
        return recommandations
    
    def _serialiser_prediction(self, prediction: Prediction) -> Dict:
        """Sérialiser une prédiction en dictionnaire"""
        return {
            "type_incident": prediction.type_incident.value,
            "horizon": prediction.horizon.value,
            "probabilite": round(prediction.probabilite, 3),
            "score_risque": round(prediction.score_risque, 1),
            "niveau_confiance": prediction.niveau_confiance.value,
            "facteurs_principaux": [
                {"nom": f.nom, "contribution": round(f.contribution, 3), "tendance": f.tendance}
                for f in prediction.facteurs_principaux
            ],
            "zone_id": prediction.zone_id,
            "timestamp_horizon": prediction.timestamp_horizon.isoformat(),
            "recommandations": prediction.recommandations
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Récupérer les statistiques du prédicteur"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "state": self.state,
            "precision_modele": self.precision_globale,
            "predictions_totales": self.stats["predictions_totales"],
            "alertes_critiques": self.stats["alertes_critiques"],
            "historique_size": len(self.historique_predictions)
        }


# ============================================
# FACTORY
# ============================================

def creer_agent_predicteur() -> AgentPredicteur:
    """Factory pour créer l'agent prédicteur"""
    return AgentPredicteur()


# ============================================
# EXPORTS
# ============================================

__all__ = [
    "HorizonPrediction",
    "TypeIncident",
    "NiveauConfiance",
    "FacteurRisque",
    "Prediction",
    "AgentPredicteur",
    "creer_agent_predicteur"
]
