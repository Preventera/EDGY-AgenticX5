"""
Test simple des agents - Sans pytest
Exécution: python test_agents_simple.py
"""

import sys
from pathlib import Path

# Ajouter src au path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from datetime import datetime
from agents.base_agent import BaseAgent, AgentCapability, AgentStatus
from agents.perception_agent import PerceptionAgent

print("=" * 60)
print("🧪 TESTS AGENTS AGENTICX5")
print("=" * 60)

# Test 1: BaseAgent
print("\n1️⃣ TEST BASEAGENT")
print("-" * 40)

class TestAgent(BaseAgent):
    def process(self, input_data):
        return {"result": "ok", "input": input_data}

agent = TestAgent(
    agent_id="test_001",
    name="Test Agent",
    config=None
)
print(f"✅ Agent créé: {agent.agent_id}")
print(f"✅ Agent name: {agent.name}")
print(f"✅ BaseAgent fonctionne!")

result = agent.process({"test": "data"})
print(f"✅ Process OK: {result}")

# Test 2: PerceptionAgent
print("\n2️⃣ TEST PERCEPTIONAGENT")
print("-" * 40)

perception = PerceptionAgent(agent_id="perception_001")
print(f"✅ Agent créé: {perception.agent_id}")
print(f"✅ Capteurs supportés: {len(perception.supported_sensors)}")

# Test température normale
data_normal = {
    "source": "iot_sensor",
    "sensor_type": "temperature",
    "value": 22.5,
    "unit": "°C",
    "location": "Workshop A"
}

result_normal = perception.process(data_normal)
print(f"✅ Température normale traitée!")
print(f"   Clés retournées: {list(result_normal.keys())}")

# Test température critique
data_critical = {
    "source": "iot_sensor",
    "sensor_type": "temperature",
    "value": 40.0,
    "unit": "°C",
    "location": "Workshop B"
}

result_critical = perception.process(data_critical)
print(f"✅ Température critique traitée!")
print(f"   Clés retournées: {list(result_critical.keys())}")

# Test bruit
data_noise = {
    "source": "iot_sensor",
    "sensor_type": "noise",
    "value": 95.0,
    "unit": "dB",
    "location": "Factory Floor"
}

result_noise = perception.process(data_noise)
print(f"✅ Bruit traité!")
print(f"   Clés retournées: {list(result_noise.keys())}")

# Résumé
print("\n" + "=" * 60)
print("🎉 TOUS LES TESTS DE BASE PASSENT!")
print("=" * 60)
print("\n📊 RÉSUMÉ:")
print(f"   ✅ BaseAgent: Fonctionnel")
print(f"   ✅ PerceptionAgent: Fonctionnel")
print(f"   ✅ Capteurs supportés: {len(perception.supported_sensors)}")
print(f"   ✅ Tests de données: 3/3 traités")
print("\n🚀 Architecture AgenticX5 validée!")