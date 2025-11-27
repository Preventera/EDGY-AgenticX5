# src/cartography/utils.py
import hashlib
import os
from typing import Optional, List, Dict, Any
from datetime import date

ANON_SALT = os.getenv('ANON_SALT', 'SafetyGraph_Loi25_2025')

def anonymize_matricule(matricule: str, salt: str = None) -> str:
    if not matricule:
        return None
    salt = salt or ANON_SALT
    return hashlib.sha256(f'{matricule}{salt}'.encode()).hexdigest()[:16]

def calculate_risk_score(probabilite: int, gravite: int) -> float:
    return max(1, min(5, probabilite)) * max(1, min(5, gravite))

def get_risk_level(score: float) -> str:
    if score >= 20: return 'CRITIQUE'
    elif score >= 15: return 'ELEVE'
    elif score >= 9: return 'MOYEN'
    return 'FAIBLE'

def generalize_age(birth_date: date) -> str:
    if not birth_date: return None
    today = date.today()
    age = today.year - birth_date.year
    if age <= 24: return '18-24'
    elif age <= 34: return '25-34'
    elif age <= 44: return '35-44'
    elif age <= 54: return '45-54'
    elif age <= 64: return '55-64'
    return '65+'
