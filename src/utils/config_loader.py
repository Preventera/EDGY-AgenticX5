"""
Configuration Loader - Charge la configuration depuis config.yaml
Version simplifiée sans dépendance externe problématique
"""
import yaml
import os
from pathlib import Path
from typing import Dict, Any, Optional

class ConfigLoader:
    """Charge et gère la configuration du projet."""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = Path(config_path)
        self.config: Dict[str, Any] = {}
        
        if self.config_path.exists():
            self.load_config()
        else:
            # Configuration par défaut minimale
            self.config = {
                'project': {
                    'name': 'EDGY-AgenticX5',
                    'version': '1.0.0',
                    'author': 'Mario Deshaies'
                },
                'claude': {
                    'model': 'claude-sonnet-4-20250514',
                    'max_tokens': 4096,
                    'temperature': 0.7,
                    'api_key_env': 'ANTHROPIC_API_KEY'
                },
                'agents': {
                    'monitoring': {'enabled': True},
                    'orchestrator': {'enabled': True},
                    'security': {'enabled': True}
                },
                'logging': {
                    'level': 'INFO'
                }
            }
    
    def load_config(self) -> None:
        """Charge la configuration depuis le fichier YAML."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f) or {}
        except Exception as e:
            print(f"Erreur chargement config: {e}")
            self.config = {}
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Récupère une valeur de configuration.
        
        Args:
            key_path: Chemin vers la clé (ex: 'agents.monitoring.enabled')
            default: Valeur par défaut si la clé n'existe pas
            
        Returns:
            Valeur de configuration
        """
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def get_env(self, env_var: str, default: str = "") -> str:
        """
        Récupère une variable d'environnement.
        
        Args:
            env_var: Nom de la variable d'environnement
            default: Valeur par défaut
            
        Returns:
            Valeur de la variable d'environnement
        """
        return os.getenv(env_var, default)


# Instance globale de configuration
config = ConfigLoader()


# Exemple d'utilisation
if __name__ == "__main__":
    print("=== Test du ConfigLoader ===\n")
    
    # Afficher quelques configurations
    print(f"Projet: {config.get('project.name')}")
    print(f"Version: {config.get('project.version')}")
    print(f"Auteur: {config.get('project.author')}")
    print(f"\nModèle Claude: {config.get('claude.model')}")
    print(f"Max tokens: {config.get('claude.max_tokens')}")
    
    print(f"\nMonitoringAgent activé: {config.get('agents.monitoring.enabled')}")
    print(f"\nNiveau de log: {config.get('logging.level')}")
    
    print("\n✅ Configuration chargée avec succès !")
