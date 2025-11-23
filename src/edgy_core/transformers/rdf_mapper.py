"""
RDF Mapper - Transformation entités Pydantic → RDF Graph
Convertit les modèles EDGY en triples RDF
"""

from typing import Optional, List
from datetime import datetime
from rdflib import Graph, Literal, URIRef
from rdflib.namespace import RDF, RDFS, XSD

from ..ontology.namespace import EDG, EDGY_CORE
from ..models.edgy_entity import (
    EDGYEntity,
    EDGYProcess,
    EDGYRiskArea,
    EDGYDataFlow,
    EDGYEntityType,
    RiskLevel
)


class RDFMapper:
    """
    Mapper principal pour convertir entités EDGY → RDF
    """
    
    def __init__(self, base_uri: str = "http://edgy.preventera.ai/instances/"):
        """
        Initialise le mapper RDF
        
        Args:
            base_uri: URI de base pour les instances
        """
        self.base_uri = base_uri
        self.graph = Graph()
        
        # Bind namespaces pour sérialisation propre
        self.graph.bind("edg", EDG)
        self.graph.bind("edgy", EDGY_CORE)
        self.graph.bind("rdf", RDF)
        self.graph.bind("rdfs", RDFS)
        self.graph.bind("xsd", XSD)
    
    def _create_uri(self, entity_id: str) -> URIRef:
        """Crée URI pour une entité"""
        return URIRef(f"{self.base_uri}{entity_id}")
    
    def _add_literal(self, subject: URIRef, predicate: URIRef, 
                     value: Optional[str], datatype=None) -> None:
        """Ajoute un triple avec literal si valeur existe"""
        if value is not None:
            if datatype:
                self.graph.add((subject, predicate, Literal(value, datatype=datatype)))
            else:
                self.graph.add((subject, predicate, Literal(value)))
    
    def map_entity_to_rdf(self, entity: EDGYEntity) -> URIRef:
        """
        Convertit EDGYEntity → RDF
        
        Args:
            entity: Instance EDGYEntity
            
        Returns:
            URIRef de l'entité créée
        """
        # Créer URI instance
        entity_uri = self._create_uri(entity.id)
        
        # Déterminer classe OWL selon type
        owl_class_map = {
            EDGYEntityType.PERSON: EDG.Person,
            EDGYEntityType.TEAM: EDG.Team,
            EDGYEntityType.ROLE: EDG.Role,
            EDGYEntityType.ORGANIZATION: EDG.Organization
        }
        
        owl_class = owl_class_map.get(entity.type, EDG.Entity)
        
        # Ajouter type RDF
        self.graph.add((entity_uri, RDF.type, owl_class))
        
        # Propriétés de données
        self._add_literal(entity_uri, EDG.hasName, entity.name)
        self._add_literal(entity_uri, EDG.hasDescription, entity.description)
        
        # Dates
        if entity.created_at:
            self._add_literal(
                entity_uri, 
                EDG.createdDate, 
                entity.created_at.isoformat(),
                datatype=XSD.dateTime
            )
        
        if entity.updated_at:
            self._add_literal(
                entity_uri,
                EDG.lastModified,
                entity.updated_at.isoformat(),
                datatype=XSD.dateTime
            )
        
        # Relation supervision
        if entity.supervisor_id:
            supervisor_uri = self._create_uri(entity.supervisor_id)
            self.graph.add((supervisor_uri, EDG.supervises, entity_uri))
        
        # Propriétés additionnelles (comme annotations)
        for key, value in entity.properties.items():
            prop_uri = EDGY_CORE[f"property_{key}"]
            self._add_literal(entity_uri, prop_uri, value)
        
        return entity_uri
    
    def map_process_to_rdf(self, process: EDGYProcess) -> URIRef:
        """
        Convertit EDGYProcess → RDF
        
        Args:
            process: Instance EDGYProcess
            
        Returns:
            URIRef du processus créé
        """
        process_uri = self._create_uri(process.id)
        
        # Type
        self.graph.add((process_uri, RDF.type, EDG.Process))
        
        # Propriétés
        self._add_literal(process_uri, EDG.hasName, process.name)
        self._add_literal(process_uri, EDG.hasDescription, process.description)
        
        # Propriétaire
        if process.owner_id:
            owner_uri = self._create_uri(process.owner_id)
            self.graph.add((owner_uri, EDG.executesProcess, process_uri))
        
        # Date création
        if process.created_at:
            self._add_literal(
                process_uri,
                EDG.createdDate,
                process.created_at.isoformat(),
                datatype=XSD.dateTime
            )
        
        # Inputs/Outputs (comme URIs)
        for input_id in process.inputs:
            input_uri = self._create_uri(input_id)
            self.graph.add((process_uri, EDG.hasInput, input_uri))
        
        for output_id in process.outputs:
            output_uri = self._create_uri(output_id)
            self.graph.add((process_uri, EDG.hasOutput, output_uri))
        
        return process_uri
    
    def map_risk_area_to_rdf(self, risk: EDGYRiskArea) -> URIRef:
        """
        Convertit EDGYRiskArea → RDF
        
        Args:
            risk: Instance EDGYRiskArea
            
        Returns:
            URIRef de la zone de risque créée
        """
        risk_uri = self._create_uri(risk.id)
        
        # Type
        self.graph.add((risk_uri, RDF.type, EDG.RiskArea))
        
        # Propriétés
        self._add_literal(risk_uri, EDG.hasName, risk.name)
        self._add_literal(risk_uri, EDG.hasDescription, risk.description)
        
        # CORRECTION: Gérer risk_level qui peut être enum ou string
        risk_level_value = risk.risk_level.value if hasattr(risk.risk_level, 'value') else str(risk.risk_level)
        self._add_literal(risk_uri, EDG.hasRiskLevel, risk_level_value)
        
        # Date création
        if risk.created_at:
            self._add_literal(
                risk_uri,
                EDG.createdDate,
                risk.created_at.isoformat(),
                datatype=XSD.dateTime
            )
        
        # Mesures d'atténuation
        for mitigation_id in risk.mitigations:
            mitigation_uri = self._create_uri(mitigation_id)
            self.graph.add((mitigation_uri, EDG.mitigates, risk_uri))
        
        # Entités exposées
        for entity_id in risk.affected_entities:
            entity_uri = self._create_uri(entity_id)
            self.graph.add((entity_uri, EDG.exposedTo, risk_uri))
        
        return risk_uri
    
    def map_dataflow_to_rdf(self, dataflow: EDGYDataFlow) -> URIRef:
        """
        Convertit EDGYDataFlow → RDF
        
        Args:
            dataflow: Instance EDGYDataFlow
            
        Returns:
            URIRef du flux de données créé
        """
        flow_uri = self._create_uri(dataflow.id)
        
        # Type
        self.graph.add((flow_uri, RDF.type, EDG.DataFlow))
        
        # Propriétés
        self._add_literal(flow_uri, EDG.hasName, dataflow.name)
        
        # Source et cible
        if dataflow.source_id:
            source_uri = self._create_uri(dataflow.source_id)
            self.graph.add((flow_uri, EDGY_CORE.hasSource, source_uri))
        
        if dataflow.target_id:
            target_uri = self._create_uri(dataflow.target_id)
            self.graph.add((flow_uri, EDGY_CORE.hasTarget, target_uri))
        
        # Type de données
        if dataflow.data_type:
            self._add_literal(flow_uri, EDGY_CORE.hasDataType, dataflow.data_type)
        
        return flow_uri
    
    def export_turtle(self) -> str:
        """
        Exporte le graphe RDF en format Turtle
        
        Returns:
            Chaîne Turtle
        """
        return self.graph.serialize(format='turtle')
    
    def export_rdfxml(self) -> str:
        """
        Exporte le graphe RDF en format RDF/XML
        
        Returns:
            Chaîne RDF/XML
        """
        return self.graph.serialize(format='xml')
    
    def get_graph(self) -> Graph:
        """Retourne le graphe RDF"""
        return self.graph
    
    def clear(self) -> None:
        """Vide le graphe RDF"""
        self.graph = Graph()
        # Re-bind namespaces
        self.graph.bind("edg", EDG)
        self.graph.bind("edgy", EDGY_CORE)


# ============================================================
# FONCTIONS UTILITAIRES
# ============================================================

def entity_to_rdf(entity: EDGYEntity, base_uri: str = None) -> Graph:
    """
    Fonction utilitaire: convertit une entité en graphe RDF
    
    Args:
        entity: Entité EDGY
        base_uri: URI de base optionnelle
        
    Returns:
        Graph RDF
    """
    mapper = RDFMapper(base_uri) if base_uri else RDFMapper()
    mapper.map_entity_to_rdf(entity)
    return mapper.get_graph()


def process_to_rdf(process: EDGYProcess, base_uri: str = None) -> Graph:
    """
    Fonction utilitaire: convertit un processus en graphe RDF
    
    Args:
        process: Processus EDGY
        base_uri: URI de base optionnelle
        
    Returns:
        Graph RDF
    """
    mapper = RDFMapper(base_uri) if base_uri else RDFMapper()
    mapper.map_process_to_rdf(process)
    return mapper.get_graph()


def risk_to_rdf(risk: EDGYRiskArea, base_uri: str = None) -> Graph:
    """
    Fonction utilitaire: convertit une zone de risque en graphe RDF
    
    Args:
        risk: Zone de risque EDGY
        base_uri: URI de base optionnelle
        
    Returns:
        Graph RDF
    """
    mapper = RDFMapper(base_uri) if base_uri else RDFMapper()
    mapper.map_risk_area_to_rdf(risk)
    return mapper.get_graph()