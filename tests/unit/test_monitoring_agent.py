"""
Tests unitaires pour l'agent de monitoring SST.
"""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from src.agents.monitoring_agent import MonitoringAgent, RiskAlert
from src.utils.config import AgentConfig


@pytest.fixture
def mock_anthropic():
    """Mock du client Anthropic."""
    with patch('src.agents.base_agent.anthropic.Anthropic') as mock:
        yield mock


@pytest.fixture
def monitoring_agent(mock_anthropic):
    """Fixture pour créer un agent de monitoring de test."""
    config = AgentConfig(
        role_description="Test monitoring agent",
        capabilities=["monitoring", "detection"],
        max_concurrent_tasks=3
    )
    
    agent = MonitoringAgent(
        agent_id="test_monitor_01",
        name="Test Monitor",
        config=config,
        anthropic_api_key="test_key"
    )
    
    return agent


class TestMonitoringAgent:
    """Tests pour l'agent de monitoring."""
    
    def test_agent_initialization(self, monitoring_agent):
        """Test l'initialisation correcte de l'agent."""
        assert monitoring_agent.agent_id == "test_monitor_01"
        assert monitoring_agent.name == "Test Monitor"
        assert monitoring_agent.state.status == "idle"
        assert monitoring_agent.monitoring_active == False
        assert len(monitoring_agent.monitored_sources) == 0
    
    @pytest.mark.asyncio
    async def test_start_monitoring(self, monitoring_agent):
        """Test le démarrage de la surveillance."""
        sources = ["sensor_01", "sensor_02", "incident_reports"]
        
        await monitoring_agent.start_monitoring(
            data_sources=sources,
            alert_threshold="medium"
        )
        
        assert monitoring_agent.monitoring_active == True
        assert monitoring_agent.monitored_sources == sources
        assert monitoring_agent.state.status == "monitoring"
    
    @pytest.mark.asyncio
    async def test_stop_monitoring(self, monitoring_agent):
        """Test l'arrêt de la surveillance."""
        # Démarrer puis arrêter
        await monitoring_agent.start_monitoring(
            data_sources=["test_source"],
            alert_threshold="low"
        )
        
        await monitoring_agent.stop_monitoring()
        
        assert monitoring_agent.monitoring_active == False
        assert monitoring_agent.state.status == "idle"
    
    @pytest.mark.asyncio
    async def test_process_data_no_risks(self, monitoring_agent):
        """Test le traitement de données sans risques."""
        # Mock de la réponse Claude
        mock_response = """```json
{
    "summary": "Aucun risque détecté",
    "risk_indicators": [],
    "anomalies_detected": [],
    "context_factors": ["Conditions normales"]
}
```"""
        
        monitoring_agent.call_claude = AsyncMock(return_value=mock_response)
        
        input_data = {
            "sensor_id": "sensor_01",
            "temperature": 22.5,
            "humidity": 45
        }
        
        result = await monitoring_agent.process(input_data)
        
        assert result["status"] == "success"
        assert result["risks_detected"] == 0
        assert len(result["alerts"]) == 0
    
    @pytest.mark.asyncio
    async def test_process_data_with_high_risk(self, monitoring_agent):
        """Test le traitement de données avec risque élevé."""
        # Mock de la réponse Claude pour analyse
        mock_analysis = """```json
{
    "summary": "Température anormalement élevée détectée",
    "risk_indicators": [
        {
            "indicator": "temperature",
            "value": "45°C",
            "threshold": "30°C",
            "deviation": "50%",
            "severity": "high"
        }
    ],
    "anomalies_detected": ["Surchauffe détectée"],
    "context_factors": ["Zone de production"]
}
```"""
        
        # Mock pour génération d'alerte
        mock_alert = """```json
{
    "description": "Température critique dans la zone de production",
    "recommended_actions": [
        "Arrêt immédiat de l'équipement",
        "Évacuation de la zone",
        "Inspection par technicien qualifié"
    ],
    "location": "Zone Production A",
    "requires_immediate_action": true
}
```"""
        
        # Configurer les mocks
        monitoring_agent.call_claude = AsyncMock(
            side_effect=[mock_analysis, mock_alert, '["Action 1", "Action 2"]']
        )
        
        input_data = {
            "sensor_id": "temp_sensor_01",
            "temperature": 45,
            "location": "Production A"
        }
        
        result = await monitoring_agent.process(input_data)
        
        assert result["status"] == "success"
        assert result["risks_detected"] > 0
        assert len(result["alerts"]) > 0
        assert len(result["recommendations"]) > 0
    
    def test_get_active_alerts(self, monitoring_agent):
        """Test la récupération des alertes actives."""
        # Créer une alerte de test
        alert = RiskAlert(
            severity="high",
            risk_type="temperature",
            location="Zone A",
            description="Test alert",
            recommended_actions=["Action 1"],
            requires_immediate_action=True
        )
        
        monitoring_agent.active_alerts.append(alert)
        
        alerts = monitoring_agent.get_active_alerts()
        
        assert len(alerts) == 1
        assert alerts[0].severity == "high"
        assert alerts[0].risk_type == "temperature"
    
    def test_clear_alerts(self, monitoring_agent):
        """Test l'effacement des alertes."""
        # Ajouter des alertes
        for i in range(3):
            alert = RiskAlert(
                severity="medium",
                risk_type=f"risk_{i}",
                location="Zone A",
                description=f"Test {i}",
                recommended_actions=[]
            )
            monitoring_agent.active_alerts.append(alert)
        
        assert len(monitoring_agent.active_alerts) == 3
        
        monitoring_agent.clear_alerts()
        
        assert len(monitoring_agent.active_alerts) == 0
    
    def test_thresholds_configuration(self, monitoring_agent):
        """Test la configuration des seuils de détection."""
        expected_thresholds = {
            "critical": 0.9,
            "high": 0.75,
            "medium": 0.5,
            "low": 0.3
        }
        
        assert monitoring_agent.thresholds == expected_thresholds
    
    @pytest.mark.asyncio
    async def test_error_handling(self, monitoring_agent):
        """Test la gestion des erreurs."""
        # Simuler une erreur dans call_claude
        monitoring_agent.call_claude = AsyncMock(
            side_effect=Exception("API Error")
        )
        
        input_data = {"test": "data"}
        
        with pytest.raises(Exception):
            await monitoring_agent.process(input_data)
        
        # Vérifier que l'erreur est comptabilisée
        assert monitoring_agent.state.error_count > 0
        assert monitoring_agent.state.status == "error"


@pytest.mark.integration
class TestMonitoringAgentIntegration:
    """Tests d'intégration pour l'agent de monitoring."""
    
    @pytest.mark.asyncio
    async def test_real_claude_call(self):
        """
        Test avec un vrai appel à Claude (nécessite ANTHROPIC_API_KEY).
        Marqué comme test d'intégration.
        """
        import os
        
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            pytest.skip("ANTHROPIC_API_KEY non défini")
        
        agent = MonitoringAgent(
            agent_id="integration_test_01",
            name="Integration Test Monitor",
            anthropic_api_key=api_key
        )
        
        input_data = {
            "sensor_id": "test_01",
            "temperature": 25,
            "humidity": 50,
            "timestamp": datetime.now().isoformat()
        }
        
        result = await agent.process(input_data)
        
        assert result["status"] == "success"
        assert "analysis" in result
        assert "risks" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
