"""
Tests de chargement et validation de l'ontologie EDGY Core
"""

import pytest
from pathlib import Path
from rdflib import Graph, Namespace, RDF, RDFS, OWL
from rdflib.namespace import DCTERMS

# Importer les namespaces
from src.edgy_core.ontology.namespace import EDG, EDGY_CORE


def test_ontology_file_exists():
    """Test que le fichier ontologie existe"""
    ontology_path = Path("ontologies/edgy_core.ttl")
    assert ontology_path.exists(), "Fichier edgy_core.ttl manquant"


def test_load_edgy_core_ontology():
    """Test chargement ontologie EDGY Core"""
    graph = Graph()
    ontology_path = Path("ontologies/edgy_core.ttl")
    
    # Charger l'ontologie
    graph.parse(ontology_path, format="turtle")
    
    # Vérifier qu'il y a des triples
    assert len(graph) > 100, f"Ontologie trop petite: {len(graph)} triples"
    print(f"✅ Ontologie chargée: {len(graph)} triples")


def test_ontology_has_classes():
    """Test que les classes principales existent"""
    graph = Graph()
    graph.parse("ontologies/edgy_core.ttl", format="turtle")
    
    # Chercher les classes définies
    classes = list(graph.subjects(RDF.type, OWL.Class))
    
    assert len(classes) >= 8, f"Classes manquantes: {len(classes)} trouvées"
    print(f"✅ Classes trouvées: {len(classes)}")
    
    # Vérifier classes spécifiques
    edg_entity = EDG.Entity
    assert (edg_entity, RDF.type, OWL.Class) in graph, "Classe edg:Entity manquante"
    
    edg_person = EDG.Person
    assert (edg_person, RDFS.subClassOf, EDG.Entity) in graph, "Person devrait être sous-classe de Entity"


def test_ontology_has_properties():
    """Test que les propriétés principales existent"""
    graph = Graph()
    graph.parse("ontologies/edgy_core.ttl", format="turtle")
    
    # Propriétés objectales
    object_properties = list(graph.subjects(RDF.type, OWL.ObjectProperty))
    assert len(object_properties) >= 8, f"Object properties manquantes: {len(object_properties)}"
    
    # Propriétés de données
    datatype_properties = list(graph.subjects(RDF.type, OWL.DatatypeProperty))
    assert len(datatype_properties) >= 5, f"Datatype properties manquantes: {len(datatype_properties)}"
    
    print(f"✅ Object properties: {len(object_properties)}")
    print(f"✅ Datatype properties: {len(datatype_properties)}")


def test_ontology_metadata():
    """Test métadonnées ontologie"""
    graph = Graph()
    graph.parse("ontologies/edgy_core.ttl", format="turtle")
    
    # Vérifier métadonnées
    ontology_uri = EDGY_CORE[""]
    
    # Titre (utiliser DCTERMS correctement)
    titles = list(graph.objects(ontology_uri, DCTERMS.title))
    assert len(titles) >= 1, f"Titre ontologie manquant (trouvés: {len(titles)})"
    
    # Version
    versions = list(graph.objects(ontology_uri, OWL.versionInfo))
    assert len(versions) >= 1, f"Version ontologie manquante (trouvées: {len(versions)})"
    
    print(f"✅ Métadonnées présentes:")
    print(f"   Titres: {len(titles)}")
    print(f"   Versions: {len(versions)}")


def test_ontology_consistency():
    """Test cohérence ontologie (inférence OWL)"""
    from owlrl import DeductiveClosure, OWLRL_Semantics
    
    graph = Graph()
    graph.parse("ontologies/edgy_core.ttl", format="turtle")
    
    # Appliquer inférence OWL-RL
    try:
        DeductiveClosure(OWLRL_Semantics).expand(graph)
        print(f"✅ Ontologie cohérente après inférence OWL-RL")
        print(f"   Triples après inférence: {len(graph)}")
    except Exception as e:
        pytest.fail(f"Incohérence ontologie: {e}")


def test_count_all_entities():
    """Test comptage toutes entités ontologie"""
    graph = Graph()
    graph.parse("ontologies/edgy_core.ttl", format="turtle")
    
    # Compter classes
    classes = len(list(graph.subjects(RDF.type, OWL.Class)))
    
    # Compter propriétés
    obj_props = len(list(graph.subjects(RDF.type, OWL.ObjectProperty)))
    data_props = len(list(graph.subjects(RDF.type, OWL.DatatypeProperty)))
    
    print(f"\n📊 STATISTIQUES ONTOLOGIE:")
    print(f"   Total triples: {len(graph)}")
    print(f"   Classes: {classes}")
    print(f"   Object Properties: {obj_props}")
    print(f"   Datatype Properties: {data_props}")
    
    assert classes >= 8
    assert obj_props >= 8
    assert data_props >= 5