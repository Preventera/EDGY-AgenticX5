#!/usr/bin/env python3
"""
Agent A1 - Collecteur de Données Terrain
EDGY-AgenticX5

Responsabilités:
- Collecte des données depuis les capteurs IoT
- Agrégation des autoévaluations terrain
- Normalisation des formats de données
- Validation et enrichissement des données brutes
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum
import json
import hashlib


# ============================================
# ÉNUMÉRATIONS
# ============================================

class SourceDonnees(str, Enum):
    """Types de sources de données"""
    CAPTEUR_IOT = "capteur_iot"
    AUTOEVALUATION = "autoevaluation"
    INSPECTION = "inspection"
    INCIDENT = "incident"
    MAINTENANCE = "maintenance"
    METEO = "meteo"
    RH = "ressources_humaines"


class StatutCollecte(str, Enum):
    """Statut de la collecte"""
    EN_ATTENTE = "pending"
    EN_COURS = "collecting"
    VALIDE = "validated"
    ERREUR = "error"
    ENRICHI = "enriched"


class TypeCapteur(str, Enum):
    """Types de capteurs supportés"""
    TEMPERATURE = "temperature"
    HUMIDITE = "humidity"
    BRUIT = "noise"
    VIBRATION = "vibration"
    GAZ = "gas"
    POUSSIERE = "dust"
    LUMINOSITE = "light"
    MOUVEMENT = "motion"
    PRESSION = "pressure"
    OXYGENE = "oxygen"


# ============================================
# MODÈLES DE DONNÉES
# ============================================

@dataclass
class DonneesBrutes:
    """Données brutes collectées"""
    source: SourceDonnees
    type_donnee: str
    valeur: Any
    unite: str
    timestamp: datetime
    zone_id: str
    capteur_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    hash_donnee: str = ""
    
    def __post_init__(self):
        if not self.hash_donnee:
            self.hash_donnee = self._calculer_hash()
    
    def _calculer_hash(self) -> str:
        """Calculer un hash unique pour la donnée"""
        data_str = f"{self.source}{self.type_donnee}{self.valeur}{self.timestamp}{self.zone_id}"
        return hashlib.md5(data_str.encode()).hexdigest()[:12]


@dataclass
class DonneesNormalisees:
    """Données normalisées et validées"""
    donnee_brute: DonneesBrutes
    valeur_normalisee: float
    unite_standard: str
    qualite_donnee: float  # 0-1
    timestamp_collecte: datetime
    statut: StatutCollecte
    validations: List[str] = field(default_factory=list)
    enrichissements: Dict[str, Any] = field(default_factory=dict)


# ============================================
# AGENT A1 - COLLECTEUR
# ============================================

class AgentCollecteur:
    """
    Agent A1 - Collecteur de Données Terrain
    
    Fonctionnalités:
    - Collecte multi-sources (IoT, autoévaluations, inspections)
    - Normalisation des unités et formats
    - Validation de la qualité des données
    - Enrichissement contextuel
    - Détection d'anomalies de collecte
    """
    
    def __init__(self):
        self.agent_id = "A1"
        self.name = "Collecteur_Donnees_Terrain"
        self.logger = logging.getLogger(f"EDGY.Agent.{self.agent_id}")
        
        self.state = "idle"
        self.buffer_collecte: List[DonneesNormalisees] = []
        self.buffer_max_size = 1000
        
        # Statistiques
        self.stats = {
            "donnees_collectees": 0,
            "donnees_validees": 0,
            "donnees_rejetees": 0,
            "erreurs_collecte": 0,
            "sources_actives": set()
        }
        
        # Configuration de normalisation
        self.config_normalisation = {
            "temperature": {"unite_standard": "C", "conversions": {"F": lambda x: (x - 32) * 5/9, "K": lambda x: x - 273.15}},
            "humidity": {"unite_standard": "%", "conversions": {}},
            "noise": {"unite_standard": "dB", "conversions": {}},
            "vibration": {"unite_standard": "m/s2", "conversions": {"mm/s2": lambda x: x / 1000}},
            "pressure": {"unite_standard": "Pa", "conversions": {"kPa": lambda x: x * 1000, "bar": lambda x: x * 100000}},
            "dust": {"unite_standard": "mg/m3", "conversions": {"ug/m3": lambda x: x / 1000}},
            "gas": {"unite_standard": "ppm", "conversions": {"%": lambda x: x * 10000}},
            "oxygen": {"unite_standard": "%", "conversions": {"ppm": lambda x: x / 10000}}
        }
        
        # Seuils de validation
        self.seuils_validation = {
            "temperature": {"min": -50, "max": 100},
            "humidity": {"min": 0, "max": 100},
            "noise": {"min": 0, "max": 150},
            "vibration": {"min": 0, "max": 50},
            "pressure": {"min": 80000, "max": 120000},
            "dust": {"min": 0, "max": 100},
            "gas": {"min": 0, "max": 50000},
            "oxygen": {"min": 0, "max": 25}
        }
        
        self.logger.info(f"Agent {self.agent_id} initialisé - {self.name}")
    
    def collecter(self, donnees_entree: List[Dict]) -> Dict[str, Any]:
        """
        Point d'entrée principal pour la collecte de données
        
        Args:
            donnees_entree: Liste de dictionnaires avec les données brutes
            
        Returns:
            Résultat de la collecte avec données normalisées
        """
        self.state = "collecting"
        start_time = datetime.utcnow()
        
        donnees_normalisees = []
        erreurs = []
        
        for donnee in donnees_entree:
            try:
                # Créer l'objet données brutes
                donnee_brute = self._creer_donnee_brute(donnee)
                
                # Normaliser
                donnee_norm = self._normaliser(donnee_brute)
                
                # Valider
                if self._valider(donnee_norm):
                    # Enrichir
                    donnee_enrichie = self._enrichir(donnee_norm)
                    donnees_normalisees.append(donnee_enrichie)
                    self.stats["donnees_validees"] += 1
                else:
                    self.stats["donnees_rejetees"] += 1
                    erreurs.append({
                        "donnee": donnee,
                        "raison": "validation_echouee"
                    })
                
                self.stats["donnees_collectees"] += 1
                self.stats["sources_actives"].add(donnee.get("source", "unknown"))
                
            except Exception as e:
                self.stats["erreurs_collecte"] += 1
                erreurs.append({
                    "donnee": donnee,
                    "raison": str(e)
                })
                self.logger.error(f"Erreur collecte: {e}")
        
        # Ajouter au buffer
        self._ajouter_buffer(donnees_normalisees)
        
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        self.state = "idle"
        
        return {
            "agent_id": self.agent_id,
            "timestamp": datetime.utcnow().isoformat(),
            "statut": "completed",
            "donnees_collectees": len(donnees_entree),
            "donnees_validees": len(donnees_normalisees),
            "donnees_rejetees": len(erreurs),
            "donnees": [self._serialiser_donnee(d) for d in donnees_normalisees],
            "erreurs": erreurs,
            "processing_time_ms": processing_time
        }
    
    def _creer_donnee_brute(self, donnee: Dict) -> DonneesBrutes:
        """Créer un objet DonneesBrutes à partir d'un dictionnaire"""
        return DonneesBrutes(
            source=SourceDonnees(donnee.get("source", "capteur_iot")),
            type_donnee=donnee.get("sensor_type", donnee.get("type", "unknown")),
            valeur=donnee.get("value", donnee.get("valeur", 0)),
            unite=donnee.get("unit", donnee.get("unite", "")),
            timestamp=datetime.fromisoformat(donnee.get("timestamp", datetime.utcnow().isoformat())),
            zone_id=donnee.get("zone_id", "ZONE-DEFAULT"),
            capteur_id=donnee.get("sensor_id", donnee.get("capteur_id")),
            metadata=donnee.get("metadata", {})
        )
    
    def _normaliser(self, donnee: DonneesBrutes) -> DonneesNormalisees:
        """Normaliser les données (unités, formats)"""
        type_donnee = donnee.type_donnee.lower()
        valeur = float(donnee.valeur)
        unite = donnee.unite
        
        # Obtenir la configuration de normalisation
        config = self.config_normalisation.get(type_donnee, {})
        unite_standard = config.get("unite_standard", unite)
        conversions = config.get("conversions", {})
        
        # Appliquer la conversion si nécessaire
        valeur_normalisee = valeur
        if unite in conversions:
            valeur_normalisee = conversions[unite](valeur)
        
        return DonneesNormalisees(
            donnee_brute=donnee,
            valeur_normalisee=valeur_normalisee,
            unite_standard=unite_standard,
            qualite_donnee=1.0,  # Sera ajusté par la validation
            timestamp_collecte=datetime.utcnow(),
            statut=StatutCollecte.VALIDE,
            validations=["normalisation_ok"]
        )
    
    def _valider(self, donnee: DonneesNormalisees) -> bool:
        """Valider la qualité des données"""
        type_donnee = donnee.donnee_brute.type_donnee.lower()
        valeur = donnee.valeur_normalisee
        
        # Vérifier les seuils
        seuils = self.seuils_validation.get(type_donnee)
        if seuils:
            if valeur < seuils["min"] or valeur > seuils["max"]:
                donnee.statut = StatutCollecte.ERREUR
                donnee.qualite_donnee = 0.0
                return False
        
        # Vérifier la fraîcheur des données (max 1 heure)
        age = datetime.utcnow() - donnee.donnee_brute.timestamp
        if age > timedelta(hours=1):
            donnee.qualite_donnee *= 0.5
            donnee.validations.append("donnee_ancienne")
        
        # Vérifier la complétude
        if not donnee.donnee_brute.zone_id:
            donnee.qualite_donnee *= 0.8
            donnee.validations.append("zone_manquante")
        
        donnee.validations.append("validation_complete")
        return donnee.qualite_donnee > 0.3
    
    def _enrichir(self, donnee: DonneesNormalisees) -> DonneesNormalisees:
        """Enrichir les données avec du contexte"""
        donnee.statut = StatutCollecte.ENRICHI
        
        # Enrichissements contextuels
        donnee.enrichissements = {
            "heure_collecte": donnee.timestamp_collecte.hour,
            "jour_semaine": donnee.timestamp_collecte.strftime("%A"),
            "periode_journee": self._get_periode_journee(donnee.timestamp_collecte.hour),
            "saison": self._get_saison(donnee.timestamp_collecte.month),
            "hash_donnee": donnee.donnee_brute.hash_donnee
        }
        
        # Détection d'anomalies simples
        type_donnee = donnee.donnee_brute.type_donnee.lower()
        seuils = self.seuils_validation.get(type_donnee, {})
        if seuils:
            plage = seuils["max"] - seuils["min"]
            position = (donnee.valeur_normalisee - seuils["min"]) / plage if plage > 0 else 0
            
            if position > 0.9 or position < 0.1:
                donnee.enrichissements["anomalie_detectee"] = True
                donnee.enrichissements["niveau_anomalie"] = "extreme" if position > 0.95 or position < 0.05 else "moderate"
        
        donnee.validations.append("enrichissement_complete")
        return donnee
    
    def _get_periode_journee(self, heure: int) -> str:
        """Déterminer la période de la journée"""
        if 6 <= heure < 12:
            return "matin"
        elif 12 <= heure < 14:
            return "midi"
        elif 14 <= heure < 18:
            return "apres-midi"
        elif 18 <= heure < 22:
            return "soir"
        else:
            return "nuit"
    
    def _get_saison(self, mois: int) -> str:
        """Déterminer la saison"""
        if mois in [12, 1, 2]:
            return "hiver"
        elif mois in [3, 4, 5]:
            return "printemps"
        elif mois in [6, 7, 8]:
            return "ete"
        else:
            return "automne"
    
    def _ajouter_buffer(self, donnees: List[DonneesNormalisees]):
        """Ajouter les données au buffer avec gestion de taille"""
        self.buffer_collecte.extend(donnees)
        
        # Purger si nécessaire
        if len(self.buffer_collecte) > self.buffer_max_size:
            self.buffer_collecte = self.buffer_collecte[-self.buffer_max_size:]
    
    def _serialiser_donnee(self, donnee: DonneesNormalisees) -> Dict:
        """Sérialiser une donnée normalisée en dictionnaire"""
        return {
            "source": donnee.donnee_brute.source.value,
            "type": donnee.donnee_brute.type_donnee,
            "valeur_brute": donnee.donnee_brute.valeur,
            "valeur_normalisee": donnee.valeur_normalisee,
            "unite": donnee.unite_standard,
            "zone_id": donnee.donnee_brute.zone_id,
            "capteur_id": donnee.donnee_brute.capteur_id,
            "qualite": donnee.qualite_donnee,
            "statut": donnee.statut.value,
            "timestamp_origine": donnee.donnee_brute.timestamp.isoformat(),
            "timestamp_collecte": donnee.timestamp_collecte.isoformat(),
            "validations": donnee.validations,
            "enrichissements": donnee.enrichissements,
            "hash": donnee.donnee_brute.hash_donnee
        }
    
    def get_buffer(self, limite: int = 100) -> List[Dict]:
        """Récupérer les dernières données du buffer"""
        return [self._serialiser_donnee(d) for d in self.buffer_collecte[-limite:]]
    
    def get_stats(self) -> Dict[str, Any]:
        """Récupérer les statistiques de collecte"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "state": self.state,
            "donnees_collectees": self.stats["donnees_collectees"],
            "donnees_validees": self.stats["donnees_validees"],
            "donnees_rejetees": self.stats["donnees_rejetees"],
            "erreurs_collecte": self.stats["erreurs_collecte"],
            "taux_validation": self.stats["donnees_validees"] / max(self.stats["donnees_collectees"], 1),
            "sources_actives": list(self.stats["sources_actives"]),
            "buffer_size": len(self.buffer_collecte)
        }
    
    def reset_stats(self):
        """Réinitialiser les statistiques"""
        self.stats = {
            "donnees_collectees": 0,
            "donnees_validees": 0,
            "donnees_rejetees": 0,
            "erreurs_collecte": 0,
            "sources_actives": set()
        }
        self.buffer_collecte = []


# ============================================
# FACTORY
# ============================================

def creer_agent_collecteur() -> AgentCollecteur:
    """Factory pour créer l'agent collecteur"""
    return AgentCollecteur()


# ============================================
# EXPORTS
# ============================================

__all__ = [
    "SourceDonnees",
    "StatutCollecte",
    "TypeCapteur",
    "DonneesBrutes",
    "DonneesNormalisees",
    "AgentCollecteur",
    "creer_agent_collecteur"
]
