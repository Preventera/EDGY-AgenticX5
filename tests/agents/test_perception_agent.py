"""
Tests pour PerceptionAgent - Version simplifiée
"""

import sys
from pathlib import Path

# Ajouter src au path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from datetime import datetime
from src.agents.perception_agent import PerceptionAgent


def test_perception_agent_initialization():
    """Test initialization"""
    agent = PerceptionAgent(agent_id="perception_test_001")
    
    assert agent.agent_id == "perception_test_001"
    assert len(agent.supported_sensors) > 0
    assert "temperature" in agent.supported_sensors
    print("✅ PerceptionAgent initialized")


def test_process_temperature_normal():
    """Test température normale"""
    agent = PerceptionAgent()
    
    input_data = {
        "source": "iot_sensor",
        "sensor_type": "temperature",
        "value": 22.5,
        "unit": "°C",
        "location": "Workshop A",
        "timestamp": datetime.now().isoformat()
    }
    
    result = agent.process(input_data)
    
    assert "observation_id" in result
    assert result["alert_level"] == "normal"
    assert "rdf_graph" in result
    assert len(result["recommendations"]) == 0
    print("✅ Temperature normale traitée")


def test_process_temperature_warning():
    """Test température critique"""
    agent = PerceptionAgent()
    
    input_data = {
        "source": "iot_sensor",
        "sensor_type": "temperature",
        "value": 38.0,
        "unit": "°C",
        "location": "Workshop B"
    }
    
    result = agent.process(input_data)
    
    assert result["alert_level"] in ["warning", "critical"]
    assert len(result["recommendations"]) > 0
    print(f"✅ Alerte {result['alert_level']} avec {len(result['recommendations'])} recommandations")


def test_process_noise_critical():
    """Test bruit critique"""
    agent = PerceptionAgent()
    
    input_data = {
        "source": "iot_sensor",
        "sensor_type": "noise",
        "value": 95.0,
        "unit": "dB",
        "location": "Factory Floor"
    }
    
    result = agent.process(input_data)
    
    assert result["alert_level"] != "normal"
    assert any("protection auditive" in r.lower() for r in result["recommendations"])
    print("✅ Bruit critique détecté")


def test_rdf_generation():
    """Test génération RDF"""
    agent = PerceptionAgent()
    
    input_data = {
        "source": "iot_sensor",
        "sensor_type": "humidity",
        "value": 65.0,
        "unit": "%",
        "location": "Storage Room"
    }
    
    result = agent.process(input_data)
    
    rdf_graph = result["rdf_graph"]
    assert len(rdf_graph) > 0
    print(f"✅ Graphe RDF: {len(rdf_graph)} triples")


def test_agent_metrics():
    """Test métriques"""
    agent = PerceptionAgent()
    
    for i in range(3):
        input_data = {
            "source": "iot_sensor",
            "sensor_type": "temperature",
            "value": 20 + i,
            "location": f"Zone {i}"
        }
        agent.process(input_data)
    
    assert agent.state.metrics["observations_processed"] == 3
    print("✅ Métriques OK")


if __name__ == "__main__":
    # Tests manuels
    print("\n🧪 TESTS MANUELS PERCEPTIONAGENT\n")
    test_perception_agent_initialization()
    test_process_temperature_normal()
    test_process_temperature_warning()
    test_process_noise_critical()
    test_rdf_generation()
    test_agent_metrics()
    print("\n✅ TOUS LES TESTS PASSENT!\n")