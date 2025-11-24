"""
SafetyGraph - Knowledge Graph SST pour Neo4j
EDGY-AgenticX5
"""

from .neo4j_connector import SafetyGraphConnector, Neo4jConfig, get_connector
from .safetygraph_schema import (
    get_ontology_summary,
    get_entity_labels,
    get_relation_types,
    NiveauRisque,
    GraviteIncident,
    TypeIncident
)

__all__ = [
    "SafetyGraphConnector",
    "Neo4jConfig", 
    "get_connector",
    "get_ontology_summary",
    "get_entity_labels",
    "get_relation_types"
]
