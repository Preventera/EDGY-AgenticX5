"""
Tests unitaires pour RDF Mapper
Validation transformation Pydantic → RDF
"""

import pytest
from datetime import datetime
from rdflib import Graph, Literal, URIRef, Namespace
from rdflib.namespace import RDF, RDFS, XSD

from src.edgy_core.ontology.namespace import EDG, EDGY_CORE
from src.edgy_core.models.edgy_entity import (
    EDGYEntity,
    EDGYProcess,
    EDGYRiskArea,
    EDGYDataFlow,
    EDGYEntityType,
    RiskLevel
)
from src.edgy_core.transformers.rdf_mapper import (
    RDFMapper,
    entity_to_rdf,
    process_to_rdf,
    risk_to_rdf
)


def test_rdf_mapper_initialization():
    """Test initialisation RDF Mapper"""
    mapper = RDFMapper()
    
    assert mapper.base_uri == "http://edgy.preventera.ai/instances/"
    assert len(mapper.graph) == 0
    
    # Vérifier namespaces bindés
    namespaces = dict(mapper.graph.namespaces())
    assert 'edg' in namespaces
    assert 'edgy' in namespaces


def test_map_person_entity_to_rdf():
    """Test mapping Person → RDF"""
    mapper = RDFMapper()
    
    # Créer entité Person
    person = EDGYEntity(
        id="P001",
        type=EDGYEntityType.PERSON,
        name="Jean Dupont",
        description="Chef SST",
        supervisor_id="P002"
    )
    
    # Mapper vers RDF
    person_uri = mapper.map_entity_to_rdf(person)
    
    # Vérifications
    assert person_uri == URIRef("http://edgy.preventera.ai/instances/P001")
    
    # Type RDF
    assert (person_uri, RDF.type, EDG.Person) in mapper.graph
    
    # Nom
    assert (person_uri, EDG.hasName, Literal("Jean Dupont")) in mapper.graph
    
    # Description
    assert (person_uri, EDG.hasDescription, Literal("Chef SST")) in mapper.graph
    
    # Supervision
    supervisor_uri = URIRef("http://edgy.preventera.ai/instances/P002")
    assert (supervisor_uri, EDG.supervises, person_uri) in mapper.graph
    
    print(f"✅ Person entity mapped: {len(mapper.graph)} triples")


def test_map_team_entity_to_rdf():
    """Test mapping Team → RDF"""
    mapper = RDFMapper()
    
    team = EDGYEntity(
        id="T001",
        type=EDGYEntityType.TEAM,
        name="Équipe HSE",
        properties={"department": "SST", "size": "5"}
    )
    
    team_uri = mapper.map_entity_to_rdf(team)
    
    # Type Team
    assert (team_uri, RDF.type, EDG.Team) in mapper.graph
    
    # Propriétés custom (annotations)
    prop_dept_uri = EDGY_CORE["property_department"]
    assert (team_uri, prop_dept_uri, Literal("SST")) in mapper.graph
    
    print(f"✅ Team entity mapped: {len(mapper.graph)} triples")


def test_map_process_to_rdf():
    """Test mapping Process → RDF"""
    mapper = RDFMapper()
    
    process = EDGYProcess(
        id="PROC001",
        name="Inspection sécurité",
        description="Inspection hebdomadaire équipements",
        owner_id="P001",
        inputs=["DF001"],
        outputs=["DF002"]
    )
    
    process_uri = mapper.map_process_to_rdf(process)
    
    # Type Process
    assert (process_uri, RDF.type, EDG.Process) in mapper.graph
    
    # Nom
    assert (process_uri, EDG.hasName, Literal("Inspection sécurité")) in mapper.graph
    
    # Owner
    owner_uri = URIRef("http://edgy.preventera.ai/instances/P001")
    assert (owner_uri, EDG.executesProcess, process_uri) in mapper.graph
    
    # Inputs
    input_uri = URIRef("http://edgy.preventera.ai/instances/DF001")
    assert (process_uri, EDG.hasInput, input_uri) in mapper.graph
    
    # Outputs
    output_uri = URIRef("http://edgy.preventera.ai/instances/DF002")
    assert (process_uri, EDG.hasOutput, output_uri) in mapper.graph
    
    print(f"✅ Process mapped: {len(mapper.graph)} triples")


def test_map_risk_area_to_rdf():
    """Test mapping RiskArea → RDF"""
    mapper = RDFMapper()
    
    risk = EDGYRiskArea(
        id="R001",
        name="Zone travaux hauteur",
        risk_level=RiskLevel.HIGH,
        description="Risque chute > 3m",
        mitigations=["PROC002", "PROC003"],
        affected_entities=["P001", "T001"]
    )
    
    risk_uri = mapper.map_risk_area_to_rdf(risk)
    
    # Type RiskArea
    assert (risk_uri, RDF.type, EDG.RiskArea) in mapper.graph
    
    # Niveau de risque
    assert (risk_uri, EDG.hasRiskLevel, Literal("high")) in mapper.graph
    
    # Mitigations
    mitigation_uri = URIRef("http://edgy.preventera.ai/instances/PROC002")
    assert (mitigation_uri, EDG.mitigates, risk_uri) in mapper.graph
    
    # Entités affectées
    entity_uri = URIRef("http://edgy.preventera.ai/instances/P001")
    assert (entity_uri, EDG.exposedTo, risk_uri) in mapper.graph
    
    print(f"✅ Risk area mapped: {len(mapper.graph)} triples")


def test_map_dataflow_to_rdf():
    """Test mapping DataFlow → RDF"""
    mapper = RDFMapper()
    
    dataflow = EDGYDataFlow(
        id="DF001",
        name="Rapport inspection",
        source_id="PROC001",
        target_id="P001",
        data_type="document"
    )
    
    flow_uri = mapper.map_dataflow_to_rdf(dataflow)
    
    # Type DataFlow
    assert (flow_uri, RDF.type, EDG.DataFlow) in mapper.graph
    
    # Nom
    assert (flow_uri, EDG.hasName, Literal("Rapport inspection")) in mapper.graph
    
    # Source
    source_uri = URIRef("http://edgy.preventera.ai/instances/PROC001")
    assert (flow_uri, EDGY_CORE.hasSource, source_uri) in mapper.graph
    
    # Target
    target_uri = URIRef("http://edgy.preventera.ai/instances/P001")
    assert (flow_uri, EDGY_CORE.hasTarget, target_uri) in mapper.graph
    
    print(f"✅ DataFlow mapped: {len(mapper.graph)} triples")


def test_export_turtle():
    """Test export Turtle"""
    mapper = RDFMapper()
    
    entity = EDGYEntity(
        id="E001",
        type=EDGYEntityType.PERSON,
        name="Test Person"
    )
    
    mapper.map_entity_to_rdf(entity)
    
    turtle_str = mapper.export_turtle()
    
    # Vérifier format Turtle (assertions plus flexibles)
    assert len(turtle_str) > 0, "Export Turtle vide"
    assert "Person" in turtle_str, "Classe Person manquante"
    assert "Test Person" in turtle_str, "Nom entité manquant"
    
    # Vérifier qu'au moins un prefix existe
    has_prefix = ("@prefix" in turtle_str or 
                  "PREFIX" in turtle_str.upper() or
                  "edg:" in turtle_str or
                  "http://example.org/edg-schema" in turtle_str)
    
    assert has_prefix, "Aucun namespace trouvé dans export Turtle"
    
    print(f"✅ Turtle export: {len(turtle_str)} chars")
    print(f"   Preview: {turtle_str[:150]}...")


def test_export_rdfxml():
    """Test export RDF/XML"""
    mapper = RDFMapper()
    
    entity = EDGYEntity(
        id="E001",
        type=EDGYEntityType.ROLE,
        name="Responsable SST"
    )
    
    mapper.map_entity_to_rdf(entity)
    
    xml_str = mapper.export_rdfxml()
    
    # Vérifier format XML
    assert '<?xml version="1.0"' in xml_str
    assert 'rdf:RDF' in xml_str
    
    print(f"✅ RDF/XML export: {len(xml_str)} chars")


def test_utility_function_entity_to_rdf():
    """Test fonction utilitaire entity_to_rdf"""
    entity = EDGYEntity(
        id="E002",
        type=EDGYEntityType.TEAM,
        name="Équipe test"
    )
    
    graph = entity_to_rdf(entity)
    
    assert len(graph) > 0
    entity_uri = URIRef("http://edgy.preventera.ai/instances/E002")
    assert (entity_uri, RDF.type, EDG.Team) in graph
    
    print(f"✅ Utility entity_to_rdf: {len(graph)} triples")


def test_utility_function_process_to_rdf():
    """Test fonction utilitaire process_to_rdf"""
    process = EDGYProcess(
        id="P999",
        name="Test Process"
    )
    
    graph = process_to_rdf(process)
    
    assert len(graph) > 0
    process_uri = URIRef("http://edgy.preventera.ai/instances/P999")
    assert (process_uri, RDF.type, EDG.Process) in graph
    
    print(f"✅ Utility process_to_rdf: {len(graph)} triples")


def test_mapper_clear():
    """Test vidage du graphe"""
    mapper = RDFMapper()
    
    # Ajouter entité
    entity = EDGYEntity(id="E001", type=EDGYEntityType.PERSON, name="Test")
    mapper.map_entity_to_rdf(entity)
    
    assert len(mapper.graph) > 0
    
    # Clear
    mapper.clear()
    
    assert len(mapper.graph) == 0
    
    print("✅ Graph cleared successfully")


def test_datetime_mapping():
    """Test mapping dates avec XSD:dateTime"""
    mapper = RDFMapper()
    
    now = datetime.now()
    entity = EDGYEntity(
        id="E003",
        type=EDGYEntityType.PERSON,
        name="Test Dates",
        created_at=now,
        updated_at=now
    )
    
    entity_uri = mapper.map_entity_to_rdf(entity)
    
    # Vérifier présence dates avec type XSD:dateTime
    dates_created = list(mapper.graph.objects(entity_uri, EDG.createdDate))
    assert len(dates_created) == 1
    assert dates_created[0].datatype == XSD.dateTime
    
    print(f"✅ DateTime mapping validated")


def test_multiple_entities_in_same_graph():
    """Test mapping multiples entités dans même graphe"""
    mapper = RDFMapper()
    
    # Créer plusieurs entités
    person = EDGYEntity(id="P001", type=EDGYEntityType.PERSON, name="Person 1")
    team = EDGYEntity(id="T001", type=EDGYEntityType.TEAM, name="Team 1")
    process = EDGYProcess(id="PROC001", name="Process 1")
    
    # Mapper toutes
    mapper.map_entity_to_rdf(person)
    mapper.map_entity_to_rdf(team)
    mapper.map_process_to_rdf(process)
    
    # Vérifier toutes présentes
    assert len(mapper.graph) > 10  # Au moins 10 triples
    
    person_uri = URIRef("http://edgy.preventera.ai/instances/P001")
    team_uri = URIRef("http://edgy.preventera.ai/instances/T001")
    process_uri = URIRef("http://edgy.preventera.ai/instances/PROC001")
    
    assert (person_uri, RDF.type, EDG.Person) in mapper.graph
    assert (team_uri, RDF.type, EDG.Team) in mapper.graph
    assert (process_uri, RDF.type, EDG.Process) in mapper.graph
    
    print(f"✅ Multiple entities: {len(mapper.graph)} triples total")