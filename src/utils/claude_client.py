"""
Claude API Client - Interface pour communiquer avec Claude 4.5
"""
import os
import logging
import anthropic
from typing import Dict, List, Optional, Any
from pathlib import Path
import sys
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env
load_dotenv()

# Ajouter le dossier src au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.config_loader import config

class ClaudeClient:
    """Client pour interagir avec l'API Claude d'Anthropic."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Vérifier si on force le mode mock
        force_mock = os.getenv('CLAUDE_MOCK_MODE', 'false').lower() == 'true'
        
        # Récupérer la clé API depuis les variables d'environnement
        api_key_env = config.get('claude.api_key_env', 'ANTHROPIC_API_KEY')
        self.api_key = os.getenv(api_key_env)
        
        if not self.api_key or force_mock:
            self.logger.warning(f"Mode MOCK activé (force_mock={force_mock}, has_key={bool(self.api_key)})")
            self.logger.info("Les réponses seront simulées")
            self.mock_mode = True
            self.client = None
        else:
            self.mock_mode = False
            try:
                self.client = anthropic.Anthropic(api_key=self.api_key)
                self.logger.info("Client Claude initialisé avec API réelle")
            except Exception as e:
                self.logger.error(f"Erreur initialisation client: {e}")
                self.mock_mode = True
                self.client = None
        
        # Paramètres par défaut
        self.model = config.get('claude.model', 'claude-sonnet-4-20250514')
        self.max_tokens = config.get('claude.max_tokens', 4096)
        self.temperature = config.get('claude.temperature', 0.7)
        
        self.logger.info(f"ClaudeClient initialisé (Mock: {self.mock_mode})")
    
    def send_message(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        conversation_history: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Envoie un message à Claude et retourne la réponse.
        
        Args:
            prompt: Le prompt à envoyer
            system_prompt: Instructions système optionnelles
            max_tokens: Nombre maximum de tokens (défaut: config)
            temperature: Température de génération (défaut: config)
            conversation_history: Historique de conversation optionnel
            
        Returns:
            Dictionnaire contenant la réponse et les métadonnées
        """
        # Mode mock pour les tests sans API key
        if self.mock_mode:
            return self._mock_response(prompt)
        
        # Utiliser les valeurs par défaut si non spécifiées
        max_tokens = max_tokens or self.max_tokens
        temperature = temperature or self.temperature
        
        try:
            # Construire les messages
            messages = []
            
            # Ajouter l'historique si fourni
            if conversation_history:
                messages.extend(conversation_history)
            
            # Ajouter le message actuel
            messages.append({
                "role": "user",
                "content": prompt
            })
            
            # Appeler l'API Claude
            self.logger.info(f"Envoi message à Claude (tokens: {max_tokens})")
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt if system_prompt else "",
                messages=messages
            )
            
            # Extraire la réponse
            response_text = response.content[0].text
            
            result = {
                "success": True,
                "response": response_text,
                "model": response.model,
                "tokens_used": {
                    "input": response.usage.input_tokens,
                    "output": response.usage.output_tokens,
                    "total": response.usage.input_tokens + response.usage.output_tokens
                },
                "stop_reason": response.stop_reason
            }
            
            self.logger.info(f"Réponse reçue ({result['tokens_used']['total']} tokens)")
            return result
            
        except anthropic.APIError as e:
            if "credit balance" in str(e).lower():
                self.logger.warning("Crédits API insuffisants, basculement en mode MOCK")
                self.mock_mode = True
                return self._mock_response(prompt)
            else:
                self.logger.error(f"Erreur API Claude: {e}")
                return {
                    "success": False,
                    "error": str(e),
                    "response": None
                }
        except Exception as e:
            self.logger.error(f"Erreur lors de l'appel à Claude: {e}")
            return {
                "success": False,
                "error": str(e),
                "response": None
            }
    
    def _mock_response(self, prompt: str) -> Dict[str, Any]:
        """
        Génère une réponse mockée pour les tests.
        
        Args:
            prompt: Le prompt envoyé
            
        Returns:
            Réponse simulée
        """
        self.logger.info("Génération d'une réponse mockée")
        
        # Analyser le prompt pour donner une réponse contextuelle
        prompt_lower = prompt.lower()
        
        if "température" in prompt_lower or "temperature" in prompt_lower:
            mock_text = """
Analyse de la situation thermique :

**Diagnostic :**
La température de 95°C détectée est au seuil critique. Cela indique :
- Possible surchauffe du moteur
- Risque de défaillance imminente
- Besoin d'intervention urgente

**Recommandations immédiates :**
1. 🛑 Arrêt immédiat de l'équipement
2. 🌀 Activation du système de refroidissement
3. 📞 Alerte à l'équipe de maintenance
4. 🔍 Inspection visuelle requise

**Sévérité :** CRITIQUE
**Confiance :** 92%
"""
        elif "vibration" in prompt_lower:
            mock_text = """
Analyse des vibrations :

**Diagnostic :**
Vibrations anormales détectées au-delà des seuils normaux.

**Causes possibles :**
- Désalignement des composants
- Usure des roulements
- Fixations desserrées

**Actions recommandées :**
1. 🔍 Inspection visuelle immédiate
2. 📐 Mesure précise des vibrations
3. 🔧 Vérification alignement et fixations

**Sévérité :** ÉLEVÉE
**Confiance :** 89%
"""
        elif "pression" in prompt_lower or "pressure" in prompt_lower:
            mock_text = """
Analyse de pression :

**ALERTE CRITIQUE :**
Surpression système détectée !

**Risques :**
- Risque d'explosion
- Risque de rupture
- Danger immédiat

**ACTIONS URGENTES :**
1. 🚨 ÉVACUATION IMMÉDIATE de la zone
2. 🛑 Fermeture vannes de sécurité
3. 📞 Appel services d'urgence

**Sévérité :** CRITIQUE
**Confiance :** 95%
"""
        else:
            mock_text = f"""
Analyse de la situation :

J'ai reçu votre demande concernant : "{prompt[:100]}..."

**Évaluation :**
Situation nécessitant une analyse approfondie.

**Recommandations :**
1. Collecte de données supplémentaires
2. Surveillance accrue
3. Consultation avec l'équipe SST

**Sévérité :** MODÉRÉE
**Confiance :** 85%
"""
        
        return {
            "success": True,
            "response": mock_text.strip(),
            "model": f"{self.model} (MOCK)",
            "tokens_used": {
                "input": len(prompt.split()),
                "output": len(mock_text.split()),
                "total": len(prompt.split()) + len(mock_text.split())
            },
            "stop_reason": "end_turn",
            "mock": True
        }
    
    def analyze_sst_situation(self, situation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyse une situation SST avec Claude.
        
        Args:
            situation: Dictionnaire décrivant la situation
            
        Returns:
            Analyse et recommandations
        """
        # Construire le prompt
        prompt = f"""
Vous êtes un expert en santé et sécurité au travail (SST).

Analysez la situation suivante et fournissez :
1. Un diagnostic clair
2. Le niveau de sévérité (CRITIQUE, ÉLEVÉE, MODÉRÉE, FAIBLE)
3. Les risques identifiés
4. Les actions recommandées (priorisées)
5. Votre niveau de confiance (%)

**Situation :**
{situation.get('description', 'Non spécifiée')}

**Données techniques :**
"""
        
        # Ajouter les paramètres techniques
        params = situation.get('parameters', {})
        for key, value in params.items():
            prompt += f"- {key}: {value}\n"
        
        prompt += """

Fournissez une analyse structurée et des recommandations actionnables.
"""
        
        system_prompt = """Vous êtes un assistant IA spécialisé en santé et sécurité au travail.
Vous analysez les situations avec rigueur, identifiez les risques et proposez des actions concrètes.
Vous êtes direct, précis et orienté vers la prévention."""
        
        return self.send_message(
            prompt=prompt,
            system_prompt=system_prompt
        )


# Exemple d'utilisation
if __name__ == "__main__":
    # Configuration du logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("="*60)
    print("Test du Claude API Client")
    print("="*60)
    
    # Créer le client
    client = ClaudeClient()
    
    if client.mock_mode:
        print("\n⚠️  Mode MOCK activé")
        print("Les réponses seront simulées pour les tests.\n")
    else:
        print("\n✅ Client Claude initialisé avec API réelle\n")
    
    # Test 1: Analyse température
    print("\n" + "="*60)
    print("Test 1: Analyse de température critique")
    print("="*60)
    
    situation1 = {
        "description": "Température moteur anormalement élevée détectée",
        "parameters": {
            "temperature": "95°C",
            "machine_id": "M-47",
            "location": "Ligne production A"
        }
    }
    
    result1 = client.analyze_sst_situation(situation1)
    
    if result1['success']:
        print(f"\n✅ Analyse réussie")
        print(f"📊 Tokens utilisés: {result1['tokens_used']['total']}")
        print(f"\n📋 Réponse de Claude:\n")
        print(result1['response'])
    else:
        print(f"\n❌ Erreur: {result1.get('error', 'Unknown')}")
    
    # Test 2: Analyse vibrations
    print("\n" + "="*60)
    print("Test 2: Analyse de vibrations anormales")
    print("="*60)
    
    situation2 = {
        "description": "Vibrations anormales détectées sur presse hydraulique",
        "parameters": {
            "vibration": "8.2 mm/s",
            "machine_id": "PH-12",
            "normal_range": "< 3 mm/s"
        }
    }
    
    result2 = client.analyze_sst_situation(situation2)
    
    if result2['success']:
        print(f"\n✅ Analyse réussie")
        print(f"📊 Tokens utilisés: {result2['tokens_used']['total']}")
        print(f"\n📋 Réponse de Claude:\n")
        print(result2['response'])
    else:
        print(f"\n❌ Erreur: {result2.get('error', 'Unknown')}")
    
    print("\n" + "="*60)
    print("Tests terminés !")
    print("="*60)
