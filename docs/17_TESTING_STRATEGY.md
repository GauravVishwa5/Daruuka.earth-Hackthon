# 17 — Testing Strategy & Benchmark Test Cases

> **Navigation:** [Index](./00_DOCUMENTATION_INDEX.md) | **Previous:** [Security & Reliability](./16_SECURITY_RELIABILITY.md) | **Next:** [MVP Implementation Plan](./18_MVP_IMPLEMENTATION_PLAN.md)

---

## 1. Multi-Tier Testing Methodology

To validate both deterministic software components and non-deterministic AI pipelines within a 24-hour hackathon, testing is divided into three layers:
1. **Unit Tests (Fast / Local):** Validates normalization functions, threshold edge cases, and JSON schema parsing.
2. **Integration Tests (Containerized):** Validates PostgreSQL connection, pgvector cosine distance queries, and FastAPI endpoint contracts.
3. **AI & Multi-Metric Reasoning Benchmarks (Evaluation):** 10 curated end-to-end test cases evaluating compound stress calculation, slot filling, anti-hallucination pruning, and evidence traceability.

---

## 2. 10 End-to-End Benchmark Test Cases

| ID | Test Scenario | Input Data Payload | Expected Deterministic Assertion |
| :--- | :--- | :--- | :--- |
| **TC-01** | **Critical Semi-Arid Monoculture** | SOC: `0.35%`, Rain: `450mm`, Monoculture: `1.0` | `compound_risk >= 0.90`, status = `"CRITICAL"`, Rank 1 = `"legume_intercropping"`, high-water crops forbidden. |
| **TC-02** | **Incomplete Telemetry (Slot Filling)** | Message: `"My soil is turning hard and dusty"` | Status = `"CLARIFICATION_REQUIRED"`, `missing_fields` contains `["soc_percent", "annual_rainfall_mm"]`. |
| **TC-03** | **Healthy Diversified Agroecosystem** | SOC: `2.6%`, Rain: `900mm`, Monoculture: `0.1` | `compound_risk <= 0.15`, status = `"LOW"`, advice focuses on maintenance and habitat enhancement. |
| **TC-04** | **Extreme Water Stress + Adequate Carbon** | SOC: `2.1%`, Rain: `320mm`, Temp: `36°C` | `water_stress >= 0.95`, `soil_stress <= 0.20`, Water buffering diagnostic active. |
| **TC-05** | **Biological Outlier Rejection** | SOC: `45.0%`, Soil pH: `13.5` | HTTP 422 Unprocessable Entity, validation message identifying impossible soil values. |
| **TC-06** | **Anti-Hallucination Numeric Pruning** | LLM draft text claims `"Increases carbon by 75%"` (chunk says `0.12%`) | Evidence validator flags ungrounded claim; replaces number with qualitative text; lowers confidence score. |
| **TC-07** | **Citation Traceability Verification** | Recommendation payload generated | Every item in `recommendations[].citations` resolves to a valid `scientific_sources.citation_key` in the database. |
| **TC-08** | **Conversational Profile Correction** | Turn 1: SOC `0.3%`. Turn 2: `"Actually SOC is 0.6%"` | `conversations.accumulated_profile` updates `soc_percent` to `0.6` without dropping rainfall or biome. |
| **TC-09** | **Hybrid RAG Semantic Retrieval** | Query: `"nitrogen fixation semi-arid cereal"` | Top retrieved chunk is `fao_soil_bulletin_80` with cosine distance $< 0.35$. |
| **TC-10** | **Acidic Tropical Soil Assessment** | SOC: `1.2%`, pH: `4.5`, Rain: `1800mm` | Detects severe acidification stress; recommends agricultural liming / agroforestry; avoids alkaline-tolerant species. |

---

## 3. Pytest Implementation Example (`tests/test_reasoning.py`)

```python
import pytest
from backend.services.reasoning_engine import MultiMetricReasoningEngine, EnvironmentalState

@pytest.fixture
def engine():
    return MultiMetricReasoningEngine()

def test_tc01_critical_semi_arid_monoculture(engine):
    state = EnvironmentalState(
        soc_percent=0.35,
        annual_rainfall_mm=450.0,
        max_temp_celsius=34.0,
        monoculture_score=1.0,
        soil_ph=7.8
    )
    result = engine.evaluate(state)
    
    assert result.risk_level == "CRITICAL"
    assert result.compound_risk >= 0.90
    assert result.soil_stress >= 0.80
    assert result.water_stress >= 0.70
    assert "high_water_demand_cover_crop" in result.forbidden_intervention_tags
    assert "drought_tolerant_legume" in result.allowed_intervention_tags

def test_tc05_biophysical_bounds_rejection():
    from backend.schemas.environmental import StrictEnvironmentalInput
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        StrictEnvironmentalInput(
            soc_percent=45.0,  # Invalid
            annual_rainfall_mm=450.0,
            soil_ph=13.5       # Invalid
        )
```

---

## 4. Test Execution Instructions

Run unit and integration tests inside the backend container:

```bash
# Execute full test suite
docker-compose exec backend pytest -v

# Run only multi-metric reasoning benchmarks
docker-compose exec backend pytest tests/test_reasoning.py -v

# Run anti-hallucination validator tests
docker-compose exec backend pytest tests/test_validation.py -v
```

---

## 5. Cross-Document Navigation

* To see the 24-hour sprint plan detailing when to run these tests, see [18_MVP_IMPLEMENTATION_PLAN.md](./18_MVP_IMPLEMENTATION_PLAN.md).
* For the live demo scenario exercising TC-01 and TC-02, see [19_DEMO_SCRIPT.md](./19_DEMO_SCRIPT.md).
* For defending test methodology to hackathon judges, see [20_JUDGE_QA.md](./20_JUDGE_QA.md).
