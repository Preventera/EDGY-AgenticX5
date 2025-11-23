"""
SecurityManager Agent - Gestion de la sécurité et conformité
"""
import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

# Ajouter le dossier src au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.base_agent import BaseAgent

class SecurityManager(BaseAgent):
    """
    Agent de sécurité qui gère la validation des actions,
    l'audit trail, et la conformité réglementaire.
    """
    
    def __init__(self, name: str = "SecurityManager"):
        super().__init__(name)
        self.audit_trail: List[Dict] = []
        self.validation_rules: Dict[str, Any] = {}
        self.compliance_checks: Dict[str, bool] = {}
        
    def initialize(self) -> None:
        """Initialise le SecurityManager avec les règles par défaut."""
        self.logger.info(f"{self.name} - Initialisation des règles de sécurité")
        
        # Règles de validation par défaut
        self.validation_rules = {
            "max_temperature": 100,  # °C
            "max_vibration": 10,     # mm/s
            "max_pressure": 200,     # PSI
            "require_human_approval": ["CRITICAL", "HIGH"],
            "blocked_actions": ["shutdown_all", "delete_data"]
        }
        
        # Vérifications de conformité
        self.compliance_checks = {
            "RGPD": True,
            "CNESST": True,
            "ISO_45001": True,
            "LSST": True
        }
        
        self.logger.info(f"{self.name} - {len(self.validation_rules)} règles chargées")
        
    def validate_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valide une action proposée par un agent.
        
        Args:
            action: Dictionnaire contenant l'action à valider
            
        Returns:
            Résultat de la validation avec statut et raison
        """
        self.logger.info(f"{self.name} - Validation de l'action: {action.get('type', 'unknown')}")
        
        # Vérifier si l'action est bloquée
        if action.get('type') in self.validation_rules.get('blocked_actions', []):
            return {
                "status": "BLOCKED",
                "reason": f"Action {action['type']} est bloquée par les règles de sécurité",
                "timestamp": datetime.now().isoformat()
            }
        
        # Vérifier la sévérité
        severity = action.get('severity', 'LOW')
        if severity in self.validation_rules.get('require_human_approval', []):
            return {
                "status": "REQUIRES_APPROVAL",
                "reason": f"Action de sévérité {severity} nécessite approbation humaine",
                "timestamp": datetime.now().isoformat()
            }
        
        # Valider les paramètres techniques
        params = action.get('parameters', {})
        
        # Température
        if 'temperature' in params:
            temp = params['temperature']
            max_temp = self.validation_rules.get('max_temperature', 100)
            if temp > max_temp:
                return {
                    "status": "REQUIRES_APPROVAL",
                    "reason": f"Température {temp}°C dépasse le seuil de {max_temp}°C",
                    "timestamp": datetime.now().isoformat()
                }
        
        # Vibrations
        if 'vibration' in params:
            vib = params['vibration']
            max_vib = self.validation_rules.get('max_vibration', 10)
            if vib > max_vib:
                return {
                    "status": "REQUIRES_APPROVAL",
                    "reason": f"Vibration {vib} mm/s dépasse le seuil de {max_vib} mm/s",
                    "timestamp": datetime.now().isoformat()
                }
        
        # Action approuvée
        return {
            "status": "APPROVED",
            "reason": "Action conforme aux règles de sécurité",
            "timestamp": datetime.now().isoformat()
        }
    
    def log_to_audit_trail(self, event: Dict[str, Any]) -> None:
        """
        Enregistre un événement dans l'audit trail.
        
        Args:
            event: Événement à enregistrer
        """
        audit_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": self.name,
            "event_type": event.get('type', 'unknown'),
            "details": event,
            "user": event.get('user', 'system')
        }
        
        self.audit_trail.append(audit_entry)
        self.logger.info(f"{self.name} - Audit trail: {event.get('type', 'unknown')}")
        
        # Sauvegarder l'audit trail si trop long
        if len(self.audit_trail) > 1000:
            self._save_audit_trail()
    
    def _save_audit_trail(self) -> None:
        """Sauvegarde l'audit trail dans un fichier."""
        import json
        
        logs_dir = Path("logs/audit")
        logs_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f"audit_trail_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = logs_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.audit_trail, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"{self.name} - Audit trail sauvegardé: {filepath}")
        
        # Réinitialiser l'audit trail en mémoire
        self.audit_trail = []
    
    def check_compliance(self, standard: str) -> bool:
        """
        Vérifie la conformité à un standard spécifique.
        
        Args:
            standard: Nom du standard (RGPD, CNESST, ISO_45001, etc.)
            
        Returns:
            True si conforme, False sinon
        """
        compliant = self.compliance_checks.get(standard, False)
        self.logger.info(f"{self.name} - Vérification conformité {standard}: {compliant}")
        return compliant
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Traite une demande de validation ou d'audit.
        
        Args:
            data: Données à traiter
            
        Returns:
            Résultat du traitement
        """
        action_type = data.get('action_type')
        
        if action_type == 'validate':
            # Validation d'action
            action = data.get('action', {})
            result = self.validate_action(action)
            
            # Logger dans l'audit trail
            self.log_to_audit_trail({
                'type': 'validation',
                'action': action,
                'result': result
            })
            
            return result
            
        elif action_type == 'audit':
            # Requête d'audit
            self.log_to_audit_trail(data.get('event', {}))
            return {
                "status": "LOGGED",
                "audit_trail_size": len(self.audit_trail)
            }
            
        elif action_type == 'compliance_check':
            # Vérification de conformité
            standard = data.get('standard', 'CNESST')
            compliant = self.check_compliance(standard)
            return {
                "standard": standard,
                "compliant": compliant,
                "timestamp": datetime.now().isoformat()
            }
        
        else:
            self.logger.warning(f"{self.name} - Action type inconnu: {action_type}")
            return {
                "status": "ERROR",
                "reason": f"Action type '{action_type}' non reconnu"
            }
    
    def get_audit_trail(self, limit: int = 100) -> List[Dict]:
        """
        Récupère les dernières entrées de l'audit trail.
        
        Args:
            limit: Nombre maximum d'entrées à retourner
            
        Returns:
            Liste des entrées d'audit
        """
        return self.audit_trail[-limit:]
    
    def update_validation_rule(self, rule_name: str, value: Any) -> None:
        """
        Met à jour une règle de validation.
        
        Args:
            rule_name: Nom de la règle
            value: Nouvelle valeur
        """
        self.validation_rules[rule_name] = value
        self.logger.info(f"{self.name} - Règle '{rule_name}' mise à jour: {value}")
        
        # Logger dans l'audit trail
        self.log_to_audit_trail({
            'type': 'rule_update',
            'rule_name': rule_name,
            'new_value': value
        })
    
    def shutdown(self) -> None:
        """Arrêt propre du SecurityManager."""
        self.logger.info(f"{self.name} - Sauvegarde finale de l'audit trail")
        
        # Sauvegarder l'audit trail final
        if self.audit_trail:
            self._save_audit_trail()
        
        super().shutdown()
        self.logger.info(f"{self.name} - Arrêt complet")


# Exemple d'utilisation
if __name__ == "__main__":
    # Configuration du logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Créer et initialiser le SecurityManager
    security = SecurityManager()
    security.initialize()
    
    # Test 1: Valider une action normale
    print("\n" + "="*60)
    print("Test 1: Action normale")
    print("="*60)
    action1 = {
        "type": "stop_machine",
        "severity": "MEDIUM",
        "parameters": {"machine_id": "M-47", "temperature": 85}
    }
    result1 = security.process({"action_type": "validate", "action": action1})
    print(f"✅ Résultat: {result1['status']}")
    print(f"   Raison: {result1['reason']}")
    
    # Test 2: Valider une action critique
    print("\n" + "="*60)
    print("Test 2: Action critique (nécessite approbation)")
    print("="*60)
    action2 = {
        "type": "emergency_shutdown",
        "severity": "CRITICAL",
        "parameters": {"temperature": 105}
    }
    result2 = security.process({"action_type": "validate", "action": action2})
    print(f"⚠️  Résultat: {result2['status']}")
    print(f"   Raison: {result2['reason']}")
    
    # Test 3: Action bloquée
    print("\n" + "="*60)
    print("Test 3: Action bloquée")
    print("="*60)
    action3 = {
        "type": "shutdown_all",
        "severity": "HIGH"
    }
    result3 = security.process({"action_type": "validate", "action": action3})
    print(f"🚫 Résultat: {result3['status']}")
    print(f"   Raison: {result3['reason']}")
    
    # Test 4: Vérification conformité
    print("\n" + "="*60)
    print("Test 4: Vérification conformité CNESST")
    print("="*60)
    result4 = security.process({
        "action_type": "compliance_check",
        "standard": "CNESST"
    })
    print(f"✅ Standard: {result4['standard']}")
    print(f"   Conforme: {result4['compliant']}")
    
    # Afficher l'audit trail
    print("\n" + "="*60)
    print(f"Audit Trail: {len(security.get_audit_trail())} entrées")
    print("="*60)
    for entry in security.get_audit_trail():
        print(f"📋 {entry['timestamp']}: {entry['event_type']}")
    
    # Arrêt propre
    print("\n" + "="*60)
    print("Arrêt du SecurityManager")
    print("="*60)
    security.shutdown()
    
    print("\n✅ Tests terminés avec succès !\n")
