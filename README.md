# EDGY-AgenticX5

[![Tests](https://img.shields.io/badge/tests-60%20passing-success)](https://github.com/Preventera/EDGY-AgenticX5)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

**Advanced Agentic AI Platform for Occupational Health & Safety**

EDGY-AgenticX5 is an enterprise-grade semantic knowledge graph platform combining EDGY ontology with autonomous safety agents for predictive HSE (Health, Safety, Environment) analytics.

---

## 🎯 Project Overview

### **Mission**
Transform workplace safety from reactive to predictive through AI-powered knowledge graphs and autonomous agents.

### **Key Features**
- 🧠 **Semantic Knowledge Graph**: 598 triples across 3 ontologies
- 🤖 **Autonomous Safety Agents**: Perception, Analysis, Decision, Action agents
- ✅ **SHACL Validation**: 15 constraint shapes ensuring data integrity
- 📊 **EDGY Core**: 9 entity classes modeling organizational structure
- 🔍 **SafetyAgentic**: 20 agent classes for HSE operations
- 🧪 **Comprehensive Testing**: 60 tests with 100% pass rate

---

## 📊 Project Statistics
```
Ontologies:          3 files (598 triples)
  - EDGY Core:       141 triples, 9 classes
  - SafetyAgentic:   227 triples, 20 classes
  - SHACL Shapes:    230 triples, 15 shapes

Code:                ~2,600 lines Python
Tests:               60 tests (100% passing)
  - Models:          6 tests
  - EDGY Core:       7 tests
  - RDF Mapper:      13 tests
  - SafetyAgentic:   13 tests
  - SHACL:           15 tests
  - Integration:     6 tests

Development Time:    ~7 hours (3 sessions)
```

---

## 🏗️ Architecture

### **Technology Stack**
- **Language**: Python 3.11+
- **Ontology**: RDF/Turtle (OWL 2)
- **Validation**: SHACL
- **Models**: Pydantic 2.x
- **RDF Library**: RDFLib
- **Testing**: Pytest
- **Inference**: OWL-RL

### **Core Components**
```
EDGY-AgenticX5/
├── src/
│   └── edgy_core/
│       ├── namespaces.py          # RDF namespace definitions
│       ├── models/
│       │   └── entity.py          # Pydantic models
│       └── transformers/
│           └── rdf_mapper.py      # Pydantic → RDF conversion
├── ontologies/
│   ├── edgy_core.ttl              # EDGY organizational ontology
│   ├── safety_agentic.ttl         # Autonomous agents ontology
│   └── shacl_shapes.ttl           # Validation constraints
└── tests/
    ├── test_models.py
    ├── test_integration.py
    └── edgy_core/
        ├── test_ontology_loading.py
        ├── test_rdf_mapper.py
        ├── test_safety_agentic.py
        └── test_shacl_validation.py
```

---

## 🚀 Quick Start

### **Prerequisites**
```bash
Python 3.11+
pip 23.0+
```

### **Installation**
```bash
# Clone repository
git clone https://github.com/Preventera/EDGY-AgenticX5.git
cd EDGY-AgenticX5

# Install dependencies
pip install -r requirements.txt --break-system-packages
```

### **Run Tests**
```bash
# Run all tests
pytest -v

# Run specific test suite
pytest tests/edgy_core/test_shacl_validation.py -v -s

# Run with coverage
pytest --cov=src --cov-report=html
```

---

## 💡 Usage Examples

### **1. Create and Validate Entities**
```python
from datetime import datetime
from src.edgy_core.models import Person, RiskArea
from src.edgy_core.transformers.rdf_mapper import person_to_rdf, risk_area_to_rdf
from rdflib import Graph
from pyshacl import validate

# Create entities
person = Person(
    id="person_001",
    name="Marie Tremblay",
    description="Senior HSE Inspector",
    created_date=datetime.now(),
    email="marie.tremblay@example.com"
)

risk_area = RiskArea(
    id="risk_001",
    name="Construction Zone - Floor 12",
    description="High-altitude work zone",
    created_date=datetime.now(),
    risk_level="high"
)

# Convert to RDF
graph = Graph()
person_to_rdf(person, graph)
risk_area_to_rdf(risk_area, graph)

# Validate with SHACL
shapes = Graph()
shapes.parse("ontologies/shacl_shapes.ttl", format="turtle")

conforms, results_graph, results_text = validate(
    graph,
    shacl_graph=shapes,
    inference='rdfs'
)

print(f"Valid: {conforms}")
```

### **2. Load and Query Ontologies**
```python
from rdflib import Graph, Namespace
from rdflib.namespace import RDF

# Load ontologies
onto = Graph()
onto.parse("ontologies/edgy_core.ttl", format="turtle")
onto.parse("ontologies/safety_agentic.ttl", format="turtle")

# Query agents
SA = Namespace("http://safety-agentic.preventera.ai/ontology#")
agents = list(onto.subjects(RDF.type, SA.Agent))

print(f"Found {len(agents)} agent definitions")
```

---

## 📚 Ontology Documentation

### **EDGY Core Classes**
- `Entity`: Base class for all organizational entities
- `Person`: Individual actors in the organization
- `Organization`: Organizational units
- `Process`: Business processes
- `RiskArea`: Zones with identified safety risks
- `Capability`: Organizational capabilities
- `Experience`: Domain expertise areas
- `Channel`: Communication channels
- `Asset`: Organizational assets

### **SafetyAgentic Agent Types**
- `PerceptionAgent`: Sensory data collection
- `AnalysisAgent`: Risk analysis and anomaly detection
- `DecisionAgent`: Recommendation generation
- `ActionAgent`: Prevention action execution
- `OrchestratorAgent`: Multi-agent coordination

### **SHACL Constraints**
- Cardinality constraints (min/max)
- Datatype validation (string, dateTime, float, integer)
- Value range validation (e.g., confidence 0.0-1.0)
- Enumerated values (e.g., risk levels: low/medium/high/critical)
- Business rules via SPARQL constraints

---

## 🧪 Testing Strategy

### **Test Coverage**
```
Unit Tests:          39 tests
Integration Tests:   6 tests
Validation Tests:    15 tests
Total:               60 tests (100% passing)
```

### **Test Categories**
1. **Models**: Pydantic model validation
2. **RDF Mapper**: Pydantic → RDF conversion
3. **Ontology Loading**: RDF parsing and inference
4. **SHACL Validation**: Constraint checking (positive/negative cases)
5. **Integration**: End-to-end workflows

---

## 🛣️ Roadmap

### **Sprint 1: EDGY Core** ✅ (Complete)
- Core ontologies
- RDF transformation pipeline
- SHACL validation
- Comprehensive testing

### **Sprint 2: Agent Intelligence** (Planned)
- LangGraph integration
- Agent decision trees
- Real-time monitoring
- Alert systems

### **Sprint 3: CNESST Integration** (Planned)
- Quebec CNESST data integration
- Sector-specific risk prediction
- Predictive analytics dashboard
- Historical injury analysis

### **Sprint 4: Enterprise Deployment** (Planned)
- AWS infrastructure
- API Gateway
- Authentication & authorization
- Performance optimization

---

## 👥 Team

**GenAISafety / Preventera**
- Mario Deshaies - Chief AI Strategy Officer
- SquadrAI Team - AI Engineers & HSE Experts

---

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

Contributions welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## 📞 Contact

- **Website**: [https://genaisafety.ai](https://genaisafety.ai)
- **Email**: contact@genaisafety.ai
- **GitHub**: [https://github.com/Preventera/EDGY-AgenticX5](https://github.com/Preventera/EDGY-AgenticX5)

---

## 🎉 Acknowledgments

Built with ❤️ for workplace safety innovation.

**Technologies**: Python • RDFLib • Pydantic • SHACL • OWL • Pytest

---

*Last Updated: November 23, 2025*