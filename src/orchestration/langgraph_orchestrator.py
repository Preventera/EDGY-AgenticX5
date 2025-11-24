"""
LangGraph Orchestration - EDGY-AgenticX5
Orchestration avancée multi-agents avec graphe d'état

Version corrigée: Gestion robuste des imports et mode simulation
"""

import logging
import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional, TypedDict, Annotated
from enum import Enum
from dataclasses import dataclass
import operator

from pydantic import BaseModel, Field

# Import LangGraph avec gestion d'erreur robuste
LANGGRAPH_AVAILABLE = False
StateGraph = None
END = "END"
MemorySaver = None

try:
    from langgraph.graph import StateGraph, END
    from langgraph.checkpoint.memory import MemorySaver
    LANGGRAPH_AVAILABLE = True
except ImportError:
    pass
except Exception as e:
    # Gérer toute autre erreur (comme le conflit langchain.debug)
    logging.warning(f"LangGraph non disponible: {e}")


# ============================================
# TYPES ET ÉNUMÉRATIONS
# ============================================

class RiskLevel(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    MINIMAL = "minimal"


class WorkflowStage(str, Enum):
    PERCEPTION = "perception"
    NORMALIZATION = "normalization"
    ANALYSIS = "analysis"
    RECOMMENDATION = "recommendation"
    NOTIFICATION = "notification"
    COMPLETED = "completed"
    ERROR = "error"


class AlertPriority(str, Enum):
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"
    P4 = "P4"


# ============================================
# ÉTAT DU GRAPHE
# ============================================

class SensorReading(TypedDict):
    sensor_id: str
    sensor_type: str
    value: float
    unit: str
    timestamp: str
    zone_id: str
    location: str


class SafetyGraphState(TypedDict):
    workflow_id: str
    started_at: str
    current_stage: str
    sensor_readings: List[Dict]
    zone_id: str
    normalized_data: List[Dict]
    risk_analysis: Optional[Dict]
    recommendations: List[Dict]
    graph_context: Dict[str, Any]
    risk_level: str
    alerts_generated: List[Dict]
    notifications_sent: List[Dict]
    processing_times: Dict[str, float]
    errors: List[str]
    messages: List[str]


# ============================================
# ORCHESTRATEUR LANGGRAPH
# ============================================

class LangGraphOrchestrator:
    """
    Orchestrateur LangGraph pour pipeline SST multi-agents
    
    Fonctionne en mode simulation si LangGraph n'est pas disponible.
    """
    
    def __init__(
        self,
        neo4j_connector=None,
        enable_checkpointing: bool = True,
        mock_mode: bool = False
    ):
        self.logger = logging.getLogger("EDGY.LangGraph")
        self.neo4j = neo4j_connector
        self.mock_mode = mock_mode or not LANGGRAPH_AVAILABLE
        self.enable_checkpointing = enable_checkpointing
        
        self.stats = {
            "workflows_executed": 0,
            "workflows_successful": 0,
            "workflows_failed": 0,
            "total_processing_time_ms": 0,
            "alerts_generated": 0,
            "recommendations_generated": 0
        }
        
        self.graph = None
        self.compiled_graph = None
        
        if LANGGRAPH_AVAILABLE and not self.mock_mode:
            self._build_and_compile_graph()
        else:
            self.logger.info("Mode SIMULATION actif - LangGraph non disponible")
    
    def _build_and_compile_graph(self):
        """Construit et compile le graphe LangGraph"""
        try:
            self.graph = StateGraph(SafetyGraphState)
            
            # Ajouter les noeuds
            self.graph.add_node("perception", self._node_perception)
            self.graph.add_node("normalization", self._node_normalization)
            self.graph.add_node("analysis", self._node_analysis)
            self.graph.add_node("recommendation", self._node_recommendation)
            self.graph.add_node("notification", self._node_notification)
            self.graph.add_node("finalize", self._node_finalize)
            
            # Point d'entrée
            self.graph.set_entry_point("perception")
            
            # Transitions
            self.graph.add_edge("perception", "normalization")
            self.graph.add_edge("normalization", "analysis")
            
            # Branche conditionnelle après analysis
            self.graph.add_conditional_edges(
                "analysis",
                self._route_by_risk_level,
                {
                    "critical": "notification",
                    "high": "recommendation",
                    "medium": "recommendation",
                    "low": "finalize",
                    "minimal": "finalize"
                }
            )
            
            self.graph.add_conditional_edges(
                "recommendation",
                self._route_after_recommendation,
                {"notify": "notification", "skip": "finalize"}
            )
            
            self.graph.add_edge("notification", "finalize")
            self.graph.add_edge("finalize", END)
            
            # Compiler
            if self.enable_checkpointing and MemorySaver:
                self.compiled_graph = self.graph.compile(checkpointer=MemorySaver())
            else:
                self.compiled_graph = self.graph.compile()
                
            self.logger.info("Graphe LangGraph compilé avec succès")
            
        except Exception as e:
            self.logger.warning(f"Erreur compilation graphe: {e}")
            self.mock_mode = True
    
    # ==========================================
    # NOEUDS DU GRAPHE
    # ==========================================
    
    def _node_perception(self, state: SafetyGraphState) -> Dict:
        start_time = datetime.utcnow()
        
        validated = []
        for reading in state.get("sensor_readings", []):
            if reading.get("value") is not None:
                validated.append(reading)
        
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        return {
            "current_stage": "perception",
            "sensor_readings": validated,
            "processing_times": {**state.get("processing_times", {}), "perception": processing_time},
            "messages": state.get("messages", []) + [f"Perception: {len(validated)} lectures validées"]
        }
    
    def _node_normalization(self, state: SafetyGraphState) -> Dict:
        start_time = datetime.utcnow()
        
        normalized = []
        for reading in state.get("sensor_readings", []):
            norm_data = {
                "original_value": reading.get("value", 0),
                "normalized_value": self._convert_to_si(
                    reading.get("value", 0),
                    reading.get("unit", ""),
                    reading.get("sensor_type", "")
                ),
                "unit_si": self._get_si_unit(reading.get("sensor_type", "")),
                "quality_score": 0.95,
                "valid": True
            }
            normalized.append(norm_data)
        
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        return {
            "current_stage": "normalization",
            "normalized_data": normalized,
            "processing_times": {**state.get("processing_times", {}), "normalization": processing_time},
            "messages": state.get("messages", []) + [f"Normalization: {len(normalized)} données"]
        }
    
    def _node_analysis(self, state: SafetyGraphState) -> Dict:
        start_time = datetime.utcnow()
        
        # Enrichissement Neo4j
        graph_context = {}
        if self.neo4j and state.get("zone_id"):
            try:
                graph_context = self.neo4j.enrich_context_for_agent(zone_id=state.get("zone_id"))
            except:
                pass
        
        risk_score = 0.0
        alerts = []
        thresholds_exceeded = []
        
        readings = state.get("sensor_readings", [])
        normalized = state.get("normalized_data", [])
        
        for i, data in enumerate(normalized):
            reading = readings[i] if i < len(readings) else {}
            sensor_type = reading.get("sensor_type", "unknown")
            value = data.get("normalized_value", 0)
            
            threshold_result = self._check_thresholds(sensor_type, value)
            if threshold_result["exceeded"]:
                thresholds_exceeded.append(sensor_type)
                alerts.append({
                    "type": "threshold_exceeded",
                    "sensor_type": sensor_type,
                    "value": value,
                    "threshold": threshold_result["threshold"],
                    "severity": threshold_result["severity"]
                })
                risk_score = max(risk_score, threshold_result["risk_contribution"])
        
        risk_level = self._calculate_risk_level(risk_score)
        
        risk_analysis = {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "alerts": alerts,
            "hazard_category": "physical" if thresholds_exceeded else "none",
            "thresholds_exceeded": thresholds_exceeded
        }
        
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        self.stats["alerts_generated"] += len(alerts)
        
        return {
            "current_stage": "analysis",
            "risk_analysis": risk_analysis,
            "risk_level": risk_level,
            "alerts_generated": alerts,
            "graph_context": graph_context,
            "processing_times": {**state.get("processing_times", {}), "analysis": processing_time},
            "messages": state.get("messages", []) + [f"Analysis: Risk={risk_level}, Score={risk_score:.1f}"]
        }
    
    def _node_recommendation(self, state: SafetyGraphState) -> Dict:
        start_time = datetime.utcnow()
        
        recommendations = []
        risk_analysis = state.get("risk_analysis", {})
        
        for alert in risk_analysis.get("alerts", []):
            sensor_type = alert.get("sensor_type", "")
            severity = alert.get("severity", "medium")
            rec = self._generate_recommendation(sensor_type, severity)
            if rec:
                recommendations.append(rec)
        
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        self.stats["recommendations_generated"] += len(recommendations)
        
        return {
            "current_stage": "recommendation",
            "recommendations": recommendations,
            "processing_times": {**state.get("processing_times", {}), "recommendation": processing_time},
            "messages": state.get("messages", []) + [f"Recommendation: {len(recommendations)} actions"]
        }
    
    def _node_notification(self, state: SafetyGraphState) -> Dict:
        start_time = datetime.utcnow()
        
        risk_level = state.get("risk_level", "low")
        priority = self._get_alert_priority(risk_level)
        
        notification = {
            "id": f"NOTIF_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "priority": priority,
            "risk_level": risk_level,
            "zone_id": state.get("zone_id", "unknown"),
            "alerts_count": len(state.get("alerts_generated", [])),
            "channels": self._get_notification_channels(priority),
            "sent_at": datetime.utcnow().isoformat(),
            "status": "sent"
        }
        
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        return {
            "current_stage": "notification",
            "notifications_sent": [notification],
            "processing_times": {**state.get("processing_times", {}), "notification": processing_time},
            "messages": state.get("messages", []) + [f"Notification: {priority} envoyée"]
        }
    
    def _node_finalize(self, state: SafetyGraphState) -> Dict:
        start_time = datetime.utcnow()
        
        # Enregistrer dans Neo4j si risque détecté
        if self.neo4j and state.get("risk_level") in ["critical", "high"]:
            try:
                near_miss_id = f"NM-AUTO-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
                self.neo4j.create_near_miss(
                    near_miss_id=near_miss_id,
                    type_risque=state.get("risk_analysis", {}).get("hazard_category", "unknown"),
                    potentiel_gravite=state.get("risk_level", "unknown"),
                    description=f"Detection automatique - Zone {state.get('zone_id')}",
                    zone_id=state.get("zone_id"),
                    detecte_par_agent="LANGGRAPH_ORCHESTRATOR"
                )
            except Exception as e:
                self.logger.error(f"Erreur Neo4j: {e}")
        
        total_time = sum(state.get("processing_times", {}).values())
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        return {
            "current_stage": "completed",
            "processing_times": {
                **state.get("processing_times", {}),
                "finalize": processing_time,
                "total": total_time + processing_time
            },
            "messages": state.get("messages", []) + [f"Finalize: Workflow termine en {total_time + processing_time:.1f}ms"]
        }
    
    # ==========================================
    # ROUTAGE CONDITIONNEL
    # ==========================================
    
    def _route_by_risk_level(self, state: SafetyGraphState) -> str:
        return state.get("risk_level", "minimal")
    
    def _route_after_recommendation(self, state: SafetyGraphState) -> str:
        risk_level = state.get("risk_level", "low")
        return "notify" if risk_level in ["critical", "high"] else "skip"
    
    # ==========================================
    # UTILITAIRES
    # ==========================================
    
    def _convert_to_si(self, value: float, unit: str, sensor_type: str) -> float:
        if unit == "F" and sensor_type == "temperature":
            return (value - 32) * 5/9
        if unit == "psi" and sensor_type == "pressure":
            return value * 6894.76
        return value
    
    def _get_si_unit(self, sensor_type: str) -> str:
        units = {
            "temperature": "C", "pressure": "Pa", "noise": "dB",
            "humidity": "%", "luminosity": "lux", "gas": "ppm"
        }
        return units.get(sensor_type, "unit")
    
    def _check_thresholds(self, sensor_type: str, value: float) -> Dict:
        thresholds = {
            "temperature": {"warning": 30, "critical": 35, "max": 40},
            "noise": {"warning": 80, "critical": 85, "max": 90},
            "humidity": {"warning": 70, "critical": 80, "max": 90},
            "gas": {"warning": 500, "critical": 1000, "max": 2000}
        }
        
        t = thresholds.get(sensor_type, {"warning": 100, "critical": 200, "max": 300})
        
        if value >= t["max"]:
            return {"exceeded": True, "threshold": t["max"], "severity": "critical", "risk_contribution": 90}
        elif value >= t["critical"]:
            return {"exceeded": True, "threshold": t["critical"], "severity": "high", "risk_contribution": 70}
        elif value >= t["warning"]:
            return {"exceeded": True, "threshold": t["warning"], "severity": "medium", "risk_contribution": 40}
        
        return {"exceeded": False, "threshold": None, "severity": None, "risk_contribution": 0}
    
    def _calculate_risk_level(self, risk_score: float) -> str:
        if risk_score >= 80:
            return "critical"
        elif risk_score >= 60:
            return "high"
        elif risk_score >= 40:
            return "medium"
        elif risk_score >= 20:
            return "low"
        return "minimal"
    
    def _generate_recommendation(self, sensor_type: str, severity: str) -> Optional[Dict]:
        templates = {
            "temperature": {"title": "Controle temperature", "ref": "RSST art. 116-120"},
            "noise": {"title": "Protection auditive", "ref": "RSST art. 130-141"},
            "gas": {"title": "Ventilation locale", "ref": "RSST art. 101-108"}
        }
        
        template = templates.get(sensor_type)
        if not template:
            return None
        
        priority = "P1" if severity == "critical" else "P2" if severity == "high" else "P3"
        
        return {
            "id": f"REC-{sensor_type.upper()}-{datetime.utcnow().strftime('%H%M%S')}",
            "title": template["title"],
            "priority": priority,
            "action_type": "engineering",
            "estimated_reduction": 0.6,
            "regulatory_reference": template["ref"]
        }
    
    def _get_alert_priority(self, risk_level: str) -> str:
        return {"critical": "P1", "high": "P2", "medium": "P3"}.get(risk_level, "P4")
    
    def _get_notification_channels(self, priority: str) -> List[str]:
        channels = {
            "P1": ["sms", "push", "email", "dashboard"],
            "P2": ["push", "email", "dashboard"],
            "P3": ["email", "dashboard"],
            "P4": ["dashboard"]
        }
        return channels.get(priority, ["dashboard"])
    
    # ==========================================
    # MÉTHODES PUBLIQUES
    # ==========================================
    
    def process(self, sensor_readings: List[Dict], zone_id: str = "ZONE-001") -> Dict:
        """Exécute le workflow complet"""
        workflow_id = f"WF-{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"
        
        initial_state = {
            "workflow_id": workflow_id,
            "started_at": datetime.utcnow().isoformat(),
            "current_stage": "starting",
            "sensor_readings": sensor_readings,
            "zone_id": zone_id,
            "normalized_data": [],
            "risk_analysis": None,
            "recommendations": [],
            "graph_context": {},
            "risk_level": "minimal",
            "alerts_generated": [],
            "notifications_sent": [],
            "processing_times": {},
            "errors": [],
            "messages": [f"Workflow {workflow_id} demarre"]
        }
        
        self.stats["workflows_executed"] += 1
        
        try:
            if self.compiled_graph and not self.mock_mode:
                config = {"configurable": {"thread_id": workflow_id}}
                final_state = self.compiled_graph.invoke(initial_state, config)
            else:
                final_state = self._simulate_workflow(initial_state)
            
            self.stats["workflows_successful"] += 1
            self.stats["total_processing_time_ms"] += final_state.get("processing_times", {}).get("total", 0)
            
            return {
                "status": "completed",
                "workflow_id": workflow_id,
                "risk_level": final_state.get("risk_level"),
                "risk_score": final_state.get("risk_analysis", {}).get("risk_score", 0),
                "alerts": final_state.get("alerts_generated", []),
                "recommendations": final_state.get("recommendations", []),
                "notifications": final_state.get("notifications_sent", []),
                "processing_times": final_state.get("processing_times", {}),
                "messages": final_state.get("messages", [])
            }
            
        except Exception as e:
            self.stats["workflows_failed"] += 1
            self.logger.error(f"Erreur workflow: {e}")
            return {"status": "error", "workflow_id": workflow_id, "error": str(e)}
    
    def _simulate_workflow(self, state: Dict) -> Dict:
        """Simulation du workflow sans LangGraph"""
        state = {**state, **self._node_perception(state)}
        state = {**state, **self._node_normalization(state)}
        state = {**state, **self._node_analysis(state)}
        
        risk_level = state.get("risk_level", "minimal")
        
        if risk_level in ["critical", "high", "medium"]:
            state = {**state, **self._node_recommendation(state)}
        
        if risk_level in ["critical", "high"]:
            state = {**state, **self._node_notification(state)}
        
        state = {**state, **self._node_finalize(state)}
        
        return state
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques"""
        success_rate = 0
        if self.stats["workflows_executed"] > 0:
            success_rate = (self.stats["workflows_successful"] / self.stats["workflows_executed"]) * 100
        
        avg_time = 0
        if self.stats["workflows_successful"] > 0:
            avg_time = self.stats["total_processing_time_ms"] / self.stats["workflows_successful"]
        
        return {
            **self.stats,
            "success_rate": round(success_rate, 1),
            "average_processing_time_ms": round(avg_time, 2),
            "langgraph_available": LANGGRAPH_AVAILABLE,
            "mock_mode": self.mock_mode
        }
    
    def get_graph_visualization(self) -> str:
        """Retourne une représentation du graphe"""
        return """
========================================
     LANGGRAPH WORKFLOW - EDGY-AgenticX5
========================================

       [START]
          |
          v
     [PERCEPTION]
          |
          v
    [NORMALIZATION]
          |
          v
      [ANALYSIS]
          |
    ------+------
    |     |     |
    v     v     v
 CRIT  HIGH/  LOW
    |   MED    |
    v     |    |
NOTIFY    v    |
    |  RECOMM  |
    |     |    |
    +--+--+----+
       |
       v
    [FINALIZE]
       |
       v
      [END]

========================================
"""


def create_orchestrator(neo4j_connector=None, enable_checkpointing: bool = True) -> LangGraphOrchestrator:
    """Factory pour créer un orchestrateur"""
    return LangGraphOrchestrator(
        neo4j_connector=neo4j_connector,
        enable_checkpointing=enable_checkpointing
    )


__all__ = [
    "LangGraphOrchestrator",
    "SafetyGraphState",
    "RiskLevel",
    "WorkflowStage",
    "create_orchestrator",
    "LANGGRAPH_AVAILABLE"
]
