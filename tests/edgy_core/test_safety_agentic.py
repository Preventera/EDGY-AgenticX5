"""
Tests pour l'ontologie SafetyAgentic
Validation chargement, classes, propriétés et cohérence
"""

import pytest
from pathlib import Path
from rdflib import Graph, Namespace, RDF, RDFS, OWL

# Namespace SafetyAgentic
SA = Namespace("http://safety-agentic.preventera.ai/ontology#")
EDG = Namespace("http://example.org/edg-schema#")


def test_safety_agentic_file_exists():
    """Test que le fichier ontologie existe"""
    ontology_path = Path("ontologies/safety_agentic.ttl")
    assert ontology_path.exists(), "Fichier safety_agentic.ttl manquant"


def test_load_safety_agentic_ontology():
    """Test chargement ontologie SafetyAgentic"""
    graph = Graph()
    ontology_path = Path("ontologies/safety_agentic.ttl")
    
    # Charger l'ontologie
    graph.parse(ontology_path, format="turtle")
    
    # Vérifier qu'il y a des triples
    assert len(graph) > 100, f"Ontologie trop petite: {len(graph)} triples"
    print(f"✅ Ontologie SafetyAgentic chargée: {len(graph)} triples")


def test_safety_agentic_agent_classes():
    """Test que les classes Agent existent"""
    graph = Graph()
    graph.parse("ontologies/safety_agentic.ttl", format="turtle")
    
    # Classes Agent principales
    agent_classes = [
        SA.Agent,
        SA.PerceptionAgent,
        SA.AnalysisAgent,
        SA.DecisionAgent,
        SA.ActionAgent,
        SA.OrchestratorAgent
    ]
    
    for agent_class in agent_classes:
        assert (agent_class, RDF.type, OWL.Class) in graph, f"Classe {agent_class} manquante"
    
    # Vérifier hiérarchie
    assert (SA.PerceptionAgent, RDFS.subClassOf, SA.Agent) in graph
    assert (SA.AnalysisAgent, RDFS.subClassOf, SA.Agent) in graph
    
    print(f"✅ Classes Agent validées: {len(agent_classes)} classes")


def test_safety_agentic_task_classes():
    """Test que les classes Task existent"""
    graph = Graph()
    graph.parse("ontologies/safety_agentic.ttl", format="turtle")
    
    # Classes Task
    task_classes = [
        SA.Task,
        SA.PerceptionTask,
        SA.AnalysisTask,
        SA.DecisionTask,
        SA.ActionTask
    ]
    
    for task_class in task_classes:
        assert (task_class, RDF.type, OWL.Class) in graph, f"Classe {task_class} manquante"
    
    # Vérifier hiérarchie
    assert (SA.PerceptionTask, RDFS.subClassOf, SA.Task) in graph
    assert (SA.AnalysisTask, RDFS.subClassOf, SA.Task) in graph
    
    print(f"✅ Classes Task validées: {len(task_classes)} classes")


def test_safety_agentic_risk_event_classes():
    """Test que les classes RiskEvent existent"""
    graph = Graph()
    graph.parse("ontologies/safety_agentic.ttl", format="turtle")
    
    # Classes RiskEvent
    risk_classes = [
        SA.RiskEvent,
        SA.NearMiss,
        SA.Incident,
        SA.Accident
    ]
    
    for risk_class in risk_classes:
        assert (risk_class, RDF.type, OWL.Class) in graph, f"Classe {risk_class} manquante"
    
    # Vérifier hiérarchie
    assert (SA.NearMiss, RDFS.subClassOf, SA.RiskEvent) in graph
    assert (SA.Incident, RDFS.subClassOf, SA.RiskEvent) in graph
    
    print(f"✅ Classes RiskEvent validées: {len(risk_classes)} classes")


def test_safety_agentic_mitigation_classes():
    """Test que les classes Mitigation existent"""
    graph = Graph()
    graph.parse("ontologies/safety_agentic.ttl", format="turtle")
    
    # Classes Mitigation
    mitigation_classes = [
        SA.Mitigation,
        SA.PreventiveMitigation,
        SA.CorrectiveMitigation
    ]
    
    for mitigation_class in mitigation_classes:
        assert (mitigation_class, RDF.type, OWL.Class) in graph, f"Classe {mitigation_class} manquante"
    
    # Vérifier hiérarchie
    assert (SA.PreventiveMitigation, RDFS.subClassOf, SA.Mitigation) in graph
    
    print(f"✅ Classes Mitigation validées: {len(mitigation_classes)} classes")


def test_safety_agentic_object_properties():
    """Test que les propriétés objectales existent"""
    graph = Graph()
    graph.parse("ontologies/safety_agentic.ttl", format="turtle")
    
    # Propriétés objectales principales
    object_properties = [
        SA.executesTask,
        SA.hasCapability,
        SA.collaboratesWith,
        SA.detectsRisk,
        SA.requiresInput,
        SA.producesOutput,
        SA.triggeredBy,
        SA.requires,
        SA.implementedBy,
        SA.observedBy,
        SA.monitors,
        SA.protects,
        SA.affectsProcess
    ]
    
    for prop in object_properties:
        assert (prop, RDF.type, OWL.ObjectProperty) in graph, f"Propriété {prop} manquante"
    
    print(f"✅ Propriétés objectales validées: {len(object_properties)} propriétés")


def test_safety_agentic_datatype_properties():
    """Test que les propriétés de données existent"""
    graph = Graph()
    graph.parse("ontologies/safety_agentic.ttl", format="turtle")
    
    # Propriétés de données
    datatype_properties = [
        SA.hasConfidence,
        SA.hasPriority,
        SA.hasStatus,
        SA.hasSeverity,
        SA.detectedAt,
        SA.hasEffectiveness,
        SA.implementedAt
    ]
    
    for prop in datatype_properties:
        assert (prop, RDF.type, OWL.DatatypeProperty) in graph, f"Propriété {prop} manquante"
    
    print(f"✅ Propriétés de données validées: {len(datatype_properties)} propriétés")


def test_safety_agentic_metadata():
    """Test que les métadonnées ontologie sont présentes"""
    from rdflib.namespace import DCTERMS
    
    graph = Graph()
    graph.parse("ontologies/safety_agentic.ttl", format="turtle")
    
    # Vérifier métadonnées
    ontology_uri = SA[""]
    
    # Titre
    titles = list(graph.objects(ontology_uri, DCTERMS.title))
    assert len(titles) >= 1, "Titre ontologie manquant"
    
    # Version
    versions = list(graph.objects(ontology_uri, OWL.versionInfo))
    assert len(versions) >= 1, "Version ontologie manquante"
    
    print(f"✅ Métadonnées présentes:")
    print(f"   Titres: {len(titles)}")
    print(f"   Versions: {len(versions)}")


def test_safety_agentic_consistency():
    """Test cohérence ontologie avec inférence OWL"""
    from owlrl import DeductiveClosure, OWLRL_Semantics
    
    graph = Graph()
    graph.parse("ontologies/safety_agentic.ttl", format="turtle")
    
    # Appliquer inférence OWL-RL
    try:
        DeductiveClosure(OWLRL_Semantics).expand(graph)
        print(f"✅ Ontologie SafetyAgentic cohérente")
        print(f"   Triples après inférence: {len(graph)}")
    except Exception as e:
        pytest.fail(f"Incohérence ontologie: {e}")


def test_integration_with_edgy_core():
    """Test intégration avec ontologie EDGY Core"""
    graph = Graph()
    graph.parse("ontologies/safety_agentic.ttl", format="turtle")
    
    # Vérifier propriétés d'intégration
    integration_properties = [
        SA.monitors,      # Agent → RiskArea (EDGY)
        SA.protects,      # Agent → Entity (EDGY)
        SA.affectsProcess # RiskEvent → Process (EDGY)
    ]
    
    for prop in integration_properties:
        assert (prop, RDF.type, OWL.ObjectProperty) in graph, f"Propriété d'intégration {prop} manquante"
    
    print(f"✅ Propriétés d'intégration EDGY validées: {len(integration_properties)}")


def test_count_all_classes():
    """Test comptage total des classes"""
    graph = Graph()
    graph.parse("ontologies/safety_agentic.ttl", format="turtle")
    
    # Compter toutes les classes
    classes = list(graph.subjects(RDF.type, OWL.Class))
    
    print(f"\n📊 STATISTIQUES ONTOLOGIE SAFETY AGENTIC:")
    print(f"   Total triples: {len(graph)}")
    print(f"   Classes: {len(classes)}")
    
    # Compter par catégorie
    agent_classes = [c for c in classes if 'Agent' in str(c)]
    task_classes = [c for c in classes if 'Task' in str(c)]
    
    print(f"   - Classes Agent: {len(agent_classes)}")
    print(f"   - Classes Task: {len(task_classes)}")
    
    assert len(classes) >= 15, "Nombre de classes insuffisant"


def test_property_domains_and_ranges():
    """Test que les domaines et ranges des propriétés sont définis"""
    graph = Graph()
    graph.parse("ontologies/safety_agentic.ttl", format="turtle")
    
    # Vérifier quelques domaines/ranges clés
    assert (SA.executesTask, RDFS.domain, SA.Agent) in graph
    assert (SA.executesTask, RDFS.range, SA.Task) in graph
    
    assert (SA.detectsRisk, RDFS.domain, SA.Task) in graph
    assert (SA.detectsRisk, RDFS.range, SA.RiskEvent) in graph
    
    print("✅ Domaines et ranges validés")