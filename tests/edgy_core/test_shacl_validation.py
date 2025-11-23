"""
Tests de validation SHACL
Validation des contraintes sur les données RDF
"""

import pytest
from pathlib import Path
from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, XSD
from pyshacl import validate

# Namespaces
EDG = Namespace("http://example.org/edg-schema#")
SA = Namespace("http://safety-agentic.preventera.ai/ontology#")
EX = Namespace("http://example.org/data#")


def load_shapes_graph():
    """Charge le graphe des shapes SHACL"""
    shapes_graph = Graph()
    shapes_graph.parse("ontologies/shacl_shapes.ttl", format="turtle")
    return shapes_graph


def test_shacl_shapes_file_exists():
    """Test que le fichier shapes existe"""
    shapes_path = Path("ontologies/shacl_shapes.ttl")
    assert shapes_path.exists(), "Fichier shacl_shapes.ttl manquant"


def test_load_shacl_shapes():
    """Test chargement des shapes SHACL"""
    shapes_graph = load_shapes_graph()
    assert len(shapes_graph) > 50, f"Shapes trop petites: {len(shapes_graph)} triples"
    print(f"✅ SHACL shapes chargées: {len(shapes_graph)} triples")


def test_valid_entity():
    """Test validation d'une entité valide"""
    shapes_graph = load_shapes_graph()
    
    # Créer données valides
    data_graph = Graph()
    entity = EX.Person001
    data_graph.add((entity, RDF.type, EDG.Person))
    data_graph.add((entity, EDG.hasName, Literal("Jean Dupont")))
    data_graph.add((entity, EDG.createdDate, Literal("2025-11-23T10:00:00", datatype=XSD.dateTime)))
    
    # Valider
    conforms, results_graph, results_text = validate(
        data_graph,
        shacl_graph=shapes_graph,
        inference='rdfs',
        abort_on_first=False
    )
    
    assert conforms, f"Validation échouée:\n{results_text}"
    print("✅ Entité valide conforme")


def test_invalid_entity_no_name():
    """Test validation échoue si entité sans nom"""
    shapes_graph = load_shapes_graph()
    
    # Créer données invalides (pas de nom)
    data_graph = Graph()
    entity = EX.Person002
    data_graph.add((entity, RDF.type, EDG.Person))
    # Pas de hasName!
    
    # Valider
    conforms, results_graph, results_text = validate(
        data_graph,
        shacl_graph=shapes_graph,
        inference='rdfs',
        abort_on_first=False
    )
    
    assert not conforms, "Validation aurait dû échouer (pas de nom)"
    assert "nom" in results_text.lower() or "name" in results_text.lower()
    print("✅ Validation échoue correctement (entité sans nom)")


def test_valid_agent_with_capability():
    """Test validation d'un agent valide avec capacité"""
    shapes_graph = load_shapes_graph()
    
    # Créer données valides
    data_graph = Graph()
    agent = EX.Agent001
    capability = EX.Cap001
    
    data_graph.add((agent, RDF.type, SA.Agent))
    data_graph.add((agent, EDG.hasName, Literal("Agent Perception")))
    data_graph.add((agent, SA.hasCapability, capability))
    data_graph.add((capability, RDF.type, SA.AgentCapability))
    
    # Valider
    conforms, results_graph, results_text = validate(
        data_graph,
        shacl_graph=shapes_graph,
        inference='rdfs',
        abort_on_first=False
    )
    
    assert conforms, f"Validation échouée:\n{results_text}"
    print("✅ Agent avec capacité valide")


def test_invalid_agent_no_capability():
    """Test validation échoue si agent sans capacité"""
    shapes_graph = load_shapes_graph()
    
    # Créer données invalides (agent sans capacité)
    data_graph = Graph()
    agent = EX.Agent002
    data_graph.add((agent, RDF.type, SA.Agent))
    data_graph.add((agent, EDG.hasName, Literal("Agent Sans Capacité")))
    # Pas de hasCapability!
    
    # Valider
    conforms, results_graph, results_text = validate(
        data_graph,
        shacl_graph=shapes_graph,
        inference='rdfs',
        abort_on_first=False
    )
    
    assert not conforms, "Validation aurait dû échouer (pas de capacité)"
    assert "capacité" in results_text.lower() or "capability" in results_text.lower()
    print("✅ Validation échoue correctement (agent sans capacité)")


def test_valid_task_with_status():
    """Test validation d'une tâche valide avec statut"""
    shapes_graph = load_shapes_graph()
    
    # Créer données valides
    data_graph = Graph()
    task = EX.Task001
    data_graph.add((task, RDF.type, SA.Task))
    data_graph.add((task, EDG.hasName, Literal("Inspection équipements")))
    data_graph.add((task, SA.hasStatus, Literal("pending")))
    data_graph.add((task, SA.hasPriority, Literal(5, datatype=XSD.integer)))
    
    # Valider
    conforms, results_graph, results_text = validate(
        data_graph,
        shacl_graph=shapes_graph,
        inference='rdfs',
        abort_on_first=False
    )
    
    assert conforms, f"Validation échouée:\n{results_text}"
    print("✅ Tâche avec statut valide")


def test_invalid_task_bad_status():
    """Test validation échoue si statut invalide"""
    shapes_graph = load_shapes_graph()
    
    # Créer données invalides (statut incorrect)
    data_graph = Graph()
    task = EX.Task002
    data_graph.add((task, RDF.type, SA.Task))
    data_graph.add((task, EDG.hasName, Literal("Tâche test")))
    data_graph.add((task, SA.hasStatus, Literal("invalid_status")))  # Statut invalide!
    
    # Valider
    conforms, results_graph, results_text = validate(
        data_graph,
        shacl_graph=shapes_graph,
        inference='rdfs',
        abort_on_first=False
    )
    
    assert not conforms, "Validation aurait dû échouer (statut invalide)"
    print("✅ Validation échoue correctement (statut invalide)")


def test_valid_risk_event():
    """Test validation d'un événement de risque valide"""
    shapes_graph = load_shapes_graph()
    
    # Créer données valides
    data_graph = Graph()
    risk_event = EX.Risk001
    mitigation = EX.Mit001
    agent = EX.Agent005
    
    data_graph.add((risk_event, RDF.type, SA.RiskEvent))
    data_graph.add((risk_event, EDG.hasName, Literal("Chute de hauteur détectée")))
    data_graph.add((risk_event, SA.hasSeverity, Literal("high")))
    data_graph.add((risk_event, SA.detectedAt, Literal("2025-11-23T14:30:00", datatype=XSD.dateTime)))
    data_graph.add((risk_event, SA.requires, mitigation))
    
    # Mitigation complète avec description et agent
    data_graph.add((mitigation, RDF.type, SA.Mitigation))
    data_graph.add((mitigation, EDG.hasDescription, Literal("Installation de garde-corps de sécurité")))
    data_graph.add((mitigation, SA.implementedBy, agent))
    
    # Agent avec capacité
    capability = EX.Cap005
    data_graph.add((agent, RDF.type, SA.Agent))
    data_graph.add((agent, EDG.hasName, Literal("Agent Sécurité")))
    data_graph.add((agent, SA.hasCapability, capability))
    data_graph.add((capability, RDF.type, SA.AgentCapability))
    
    # Valider
    conforms, results_graph, results_text = validate(
        data_graph,
        shacl_graph=shapes_graph,
        inference='rdfs',
        abort_on_first=False
    )
    
    assert conforms, f"Validation échouée:\n{results_text}"
    print("✅ Événement de risque valide")


def test_invalid_risk_event_no_detection_date():
    """Test validation échoue si événement sans date"""
    shapes_graph = load_shapes_graph()
    
    # Créer données invalides (pas de date)
    data_graph = Graph()
    risk_event = EX.Risk002
    mitigation = EX.Mit002
    agent = EX.Agent006
    capability = EX.Cap006
    
    data_graph.add((risk_event, RDF.type, SA.RiskEvent))
    data_graph.add((risk_event, EDG.hasName, Literal("Événement test")))
    data_graph.add((risk_event, SA.hasSeverity, Literal("medium")))
    # Pas de detectedAt!
    data_graph.add((risk_event, SA.requires, mitigation))
    
    data_graph.add((mitigation, RDF.type, SA.Mitigation))
    data_graph.add((mitigation, EDG.hasDescription, Literal("Mesure corrective standard")))
    data_graph.add((mitigation, SA.implementedBy, agent))
    
    data_graph.add((agent, RDF.type, SA.Agent))
    data_graph.add((agent, EDG.hasName, Literal("Agent Test")))
    data_graph.add((agent, SA.hasCapability, capability))
    data_graph.add((capability, RDF.type, SA.AgentCapability))
    
    # Valider
    conforms, results_graph, results_text = validate(
        data_graph,
        shacl_graph=shapes_graph,
        inference='rdfs',
        abort_on_first=False
    )
    
    assert not conforms, "Validation aurait dû échouer (pas de date de détection)"
    print("✅ Validation échoue correctement (événement sans date)")


def test_valid_risk_area_with_level():
    """Test validation d'une zone de risque valide"""
    shapes_graph = load_shapes_graph()
    
    # Créer données valides
    data_graph = Graph()
    risk_area = EX.RiskArea001
    data_graph.add((risk_area, RDF.type, EDG.RiskArea))
    data_graph.add((risk_area, EDG.hasName, Literal("Zone travaux en hauteur")))
    data_graph.add((risk_area, EDG.hasRiskLevel, Literal("high")))
    
    # Valider
    conforms, results_graph, results_text = validate(
        data_graph,
        shacl_graph=shapes_graph,
        inference='rdfs',
        abort_on_first=False
    )
    
    assert conforms, f"Validation échouée:\n{results_text}"
    print("✅ Zone de risque valide")


def test_invalid_risk_area_bad_level():
    """Test validation échoue si niveau de risque invalide"""
    shapes_graph = load_shapes_graph()
    
    # Créer données invalides (niveau incorrect)
    data_graph = Graph()
    risk_area = EX.RiskArea002
    data_graph.add((risk_area, RDF.type, EDG.RiskArea))
    data_graph.add((risk_area, EDG.hasName, Literal("Zone test")))
    data_graph.add((risk_area, EDG.hasRiskLevel, Literal("super_high")))  # Invalide!
    
    # Valider
    conforms, results_graph, results_text = validate(
        data_graph,
        shacl_graph=shapes_graph,
        inference='rdfs',
        abort_on_first=False
    )
    
    assert not conforms, "Validation aurait dû échouer (niveau de risque invalide)"
    print("✅ Validation échoue correctement (niveau de risque invalide)")


def test_observation_confidence_range():
    """Test validation de la plage de confiance d'une observation"""
    shapes_graph = load_shapes_graph()
    
    # Créer données valides (confiance dans [0, 1])
    data_graph = Graph()
    observation = EX.Obs001
    agent = EX.Agent003
    capability = EX.Cap003
    
    data_graph.add((observation, RDF.type, SA.Observation))
    data_graph.add((observation, SA.hasConfidence, Literal(0.85, datatype=XSD.float)))
    data_graph.add((observation, SA.observedBy, agent))
    
    # Agent complet avec capacité
    data_graph.add((agent, RDF.type, SA.Agent))
    data_graph.add((agent, EDG.hasName, Literal("Agent Perception")))
    data_graph.add((agent, SA.hasCapability, capability))
    data_graph.add((capability, RDF.type, SA.AgentCapability))
    
    # Valider
    conforms, results_graph, results_text = validate(
        data_graph,
        shacl_graph=shapes_graph,
        inference='rdfs',
        abort_on_first=False
    )
    
    assert conforms, f"Validation échouée:\n{results_text}"
    print("✅ Observation avec confiance valide")


def test_invalid_observation_confidence_out_of_range():
    """Test validation échoue si confiance hors limites"""
    shapes_graph = load_shapes_graph()
    
    # Créer données invalides (confiance > 1.0)
    data_graph = Graph()
    observation = EX.Obs002
    agent = EX.Agent004
    capability = EX.Cap004
    
    data_graph.add((observation, RDF.type, SA.Observation))
    data_graph.add((observation, SA.hasConfidence, Literal(1.5, datatype=XSD.float)))  # > 1.0!
    data_graph.add((observation, SA.observedBy, agent))
    
    data_graph.add((agent, RDF.type, SA.Agent))
    data_graph.add((agent, EDG.hasName, Literal("Agent Test")))
    data_graph.add((agent, SA.hasCapability, capability))
    data_graph.add((capability, RDF.type, SA.AgentCapability))
    
    # Valider
    conforms, results_graph, results_text = validate(
        data_graph,
        shacl_graph=shapes_graph,
        inference='rdfs',
        abort_on_first=False
    )
    
    assert not conforms, "Validation aurait dû échouer (confiance > 1.0)"
    print("✅ Validation échoue correctement (confiance hors limites)")


def test_count_shape_definitions():
    """Test comptage des définitions de shapes"""
    from rdflib.namespace import SH
    
    shapes_graph = load_shapes_graph()
    
    # Compter les NodeShapes
    node_shapes = list(shapes_graph.subjects(RDF.type, SH.NodeShape))
    
    print(f"\n📊 STATISTIQUES SHACL SHAPES:")
    print(f"   Total triples: {len(shapes_graph)}")
    print(f"   NodeShapes: {len(node_shapes)}")
    
    assert len(node_shapes) >= 10, "Pas assez de NodeShapes définis"
    print("✅ Shapes SHACL bien définies")