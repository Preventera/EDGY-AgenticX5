"""
Script pour corriger automatiquement le fichier .env
"""
import os
from pathlib import Path

def fix_env_file():
    """Commente la ligne claude_mock_mode dans .env"""
    env_path = Path(".env")
    
    if not env_path.exists():
        print("❌ Fichier .env introuvable")
        return False
    
    # Lire le contenu
    with open(env_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Modifier les lignes
    modified = False
    new_lines = []
    for line in lines:
        if line.strip().startswith('claude_mock_mode='):
            new_lines.append(f"# {line}")
            modified = True
            print(f"✅ Ligne commentée : {line.strip()}")
        else:
            new_lines.append(line)
    
    if modified:
        # Sauvegarder
        with open(env_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        print("\n✅ Fichier .env corrigé avec succès!")
        return True
    else:
        print("ℹ️  Aucune ligne 'claude_mock_mode' trouvée dans .env")
        return False

if __name__ == "__main__":
    print("🔧 Correction du fichier .env...")
    fix_env_file()
