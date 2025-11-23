"""
Namespaces RDF pour EDGY Core
Définit tous les préfixes utilisés dans l'ontologie EDGY et SafetyAgentic
"""

from rdflib import Namespace

# ============================================================
# NAMESPACES EDGY
# ============================================================

# Namespace principal EDGY Schema
EDG = Namespace("http://example.org/edg-schema#")

# Namespace EDGY Core (Preventera)
EDGY_CORE = Namespace("http://edgy.preventera.ai/core#")

# ============================================================
# NAMESPACES SAFETYAGENTIC
# ============================================================

# Namespace principal SafetyAgentic
SA = Namespace("http://safetyagentic.org/ontology#")

# Namespaces spécialisés SafetyAgentic
SA_AGENT = Namespace("http://safetyagentic.org/agent#")
SA_TASK = Namespace("http://safetyagentic.org/task#")
SA_HAZARD = Namespace("http://safetyagentic.org/hazard#")
SA_INCIDENT = Namespace("http://safetyagentic.org/incident#")

# ============================================================
# NAMESPACES STANDARDS RDF/OWL
# ============================================================

from rdflib.namespace import RDF, RDFS, OWL, XSD, SKOS, DCTERMS

# ============================================================
# EXPORT
# ============================================================

__all__ = [
    # EDGY
    'EDG',
    'EDGY_CORE',
    # SafetyAgentic
    'SA',
    'SA_AGENT',
    'SA_TASK',
    'SA_HAZARD',
    'SA_INCIDENT',
    # Standards
    'RDF',
    'RDFS',
    'OWL',
    'XSD',
    'SKOS',
    'DCTERMS'
]