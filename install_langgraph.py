#!/usr/bin/env python3
"""
AUTO-INSTALL LangGraph Orchestration
EDGY-AgenticX5
"""

import os
from pathlib import Path

def create_file(path, content):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"  [OK] {path}")

def main():
    print("\n" + "=" * 60)
    print("  INSTALLATION LANGGRAPH ORCHESTRATION")
    print("  EDGY-AgenticX5")
    print("=" * 60 + "\n")
    
    if not os.path.exists("src/agents"):
        print("[ERREUR] Executez depuis le dossier EDGY-AgenticX5")
        return False
    
    print("Creation du dossier orchestration...\n")
    
    # Creer __init__.py
    create_file("src/orchestration/__init__.py", '''"""
LangGraph Orchestration - EDGY-AgenticX5
"""

from .langgraph_orchestrator import (
    LangGraphOrchestrator,
    SafetyGraphState,
    RiskLevel,
    WorkflowStage,
    create_orchestrator,
    LANGGRAPH_AVAILABLE
)

__all__ = [
    "LangGraphOrchestrator",
    "SafetyGraphState", 
    "RiskLevel",
    "WorkflowStage",
    "create_orchestrator",
    "LANGGRAPH_AVAILABLE"
]
''')

    print("\n" + "=" * 60)
    print("  TELECHARGEMENT REQUIS")
    print("=" * 60)
    print("""
  Telechargez ces fichiers depuis Claude:
  
  1. langgraph_orchestrator.py -> src/orchestration/
  2. test_langgraph_integration.py -> racine du projet
  
  Commandes:
  
  Copy-Item "$env:USERPROFILE\\Downloads\\langgraph_orchestrator.py" src/orchestration/
  Copy-Item "$env:USERPROFILE\\Downloads\\test_langgraph_integration.py" .
  
  Puis:
  python test_langgraph_integration.py
""")
    
    print("=" * 60)
    print("  [OK] Dossier src/orchestration cree!")
    print("=" * 60 + "\n")
    
    return True

if __name__ == "__main__":
    main()
