import pytest
from backend.db.database import check_db_connection, SessionLocal
from backend.db.models import ScientificSource, EvidenceChunk, Intervention, Conversation
from backend.repository import get_repository, PostgresVectorRepository, InMemoryVectorRepository
from backend.reasoning import MultiMetricReasoningEngine, EnvironmentalTelemetry
from backend.recommendation import RecommendationEngine
from backend.validator import EvidenceValidator
from backend.conversation import ConversationManager
from backend.main import app
from fastapi.testclient import TestClient

@pytest.fixture
def repo():
    return get_repository()

@pytest.fixture
def reasoning():
    return MultiMetricReasoningEngine()

@pytest.fixture
def client():
    return TestClient(app)

# 1. PostgreSQL Connection Test
def test_01_postgresql_connection():
    status = check_db_connection()
    assert status["connected"] is True
    assert status["database"] == "darukaa"

# 2. pgvector Extension Availability
def test_02_pgvector_availability():
    status = check_db_connection()
    assert status["pgvector_active"] is True
    assert status["pgvector_version"] is not None

# 3. Database Initialization & Tables Check
def test_03_database_initialization_tables_exist():
    db = SessionLocal()
    try:
        assert db.query(ScientificSource).count() >= 0
        assert db.query(EvidenceChunk).count() >= 0
        assert db.query(Intervention).count() >= 0
    finally:
        db.close()

# 4. Seed Data Ingestion
def test_04_seed_ingestion():
    db = SessionLocal()
    try:
        assert db.query(ScientificSource).count() >= 5
        assert db.query(EvidenceChunk).count() >= 5
        assert db.query(Intervention).count() >= 8
    finally:
        db.close()

# 5. Embedding Storage & Dimensions (1536)
def test_05_embedding_storage_and_dimension():
    db = SessionLocal()
    try:
        chunk = db.query(EvidenceChunk).first()
        assert chunk is not None
        assert chunk.embedding is not None
        assert len(chunk.embedding) == 1536
    finally:
        db.close()

# 6. Vector Retrieval via pgvector Cosine Distance
def test_06_pgvector_vector_retrieval(repo):
    results = repo.search_chunks("legume intercropping nitrogen fixation", limit=2)
    assert len(results) > 0
    assert any("fao_soil_bulletin_80" in r["chunk_id"] for r in results)
    assert results[0]["doi"] is not None

# 7. Low SOC -> Increased Soil Stress
def test_07_low_soc_triggers_increased_soil_stress(reasoning):
    telemetry = EnvironmentalTelemetry(soc_percent=0.35, annual_rainfall_mm=800.0, land_use="pasture")
    res = reasoning.evaluate(telemetry)
    assert res.stress_levels["soil_stress"] == "CRITICAL"
    assert any(cf["stressor"] == "CRITICAL_SOC_DEPLETION" for cf in res.causal_factors)

# 8. Low Rainfall -> Increased Water Stress
def test_08_low_rainfall_triggers_increased_water_stress(reasoning):
    telemetry = EnvironmentalTelemetry(soc_percent=1.8, annual_rainfall_mm=450.0, max_temp_celsius=34.0, land_use="pasture")
    res = reasoning.evaluate(telemetry)
    assert res.stress_levels["water_stress"] == "HIGH"
    assert res.water_penalty_active is True

# 9. Monoculture -> Increased Habitat Pressure
def test_09_monoculture_triggers_increased_habitat_pressure(reasoning):
    telemetry = EnvironmentalTelemetry(soc_percent=2.0, annual_rainfall_mm=900.0, land_use="wheat_monoculture")
    res = reasoning.evaluate(telemetry)
    assert res.stress_levels["biodiversity_stress"] == "HIGH"
    assert any(cf["stressor"] == "MONOCULTURE_FLORAL_DESERT" for cf in res.causal_factors)

# 10. Multiple Metrics -> Compound Ecological Stress
def test_10_multiple_metrics_compound_reasoning(reasoning):
    telemetry = EnvironmentalTelemetry(soc_percent=0.35, annual_rainfall_mm=450.0, max_temp_celsius=34.0, land_use="wheat_monoculture")
    res = reasoning.evaluate(telemetry)
    assert res.compound_risk == "CRITICAL_COMPOUND_DEGRADATION"
    assert len(res.causal_factors) == 3

# 11. Missing Rainfall -> Clarification Question
def test_11_missing_rainfall_returns_clarification():
    turn = ConversationManager.evaluate_turn("SOC is 0.4% in wheat monoculture", {})
    assert turn["status"] == "CLARIFICATION_REQUIRED"
    assert "annual_rainfall_mm" in turn["missing_fields"]
    assert "Average annual rainfall" in turn["clarification_prompt"]

# 12. Missing SOC -> Clarification Question
def test_12_missing_soc_returns_clarification():
    turn = ConversationManager.evaluate_turn("Rainfall is 450 mm and I grow wheat", {})
    assert turn["status"] == "CLARIFICATION_REQUIRED"
    assert "soc_percent" in turn["missing_fields"]
    assert "Soil Organic Carbon" in turn["clarification_prompt"]

# 13. Conversation Context Retention
def test_13_conversation_context_retention():
    # Turn 1: User provides SOC
    turn1 = ConversationManager.evaluate_turn("Carbon is 0.35%", {})
    assert turn1["profile"]["soc_percent"] == 0.35
    
    # Turn 2: User provides Rainfall and Land Use
    turn2 = ConversationManager.evaluate_turn("Rainfall is 450 mm and wheat monoculture", turn1["profile"])
    assert turn2["status"] == "READY_FOR_REASONING"
    assert turn2["profile"]["soc_percent"] == 0.35
    assert turn2["profile"]["annual_rainfall_mm"] == 450.0
    assert turn2["profile"]["land_use"] == "wheat_monoculture"

# 14. Recommendation Ranking & Darukaa Decision Score (DSI)
def test_14_recommendation_ranking_and_dsi(repo, reasoning):
    rec_engine = RecommendationEngine(repo)
    telemetry = EnvironmentalTelemetry(soc_percent=0.35, annual_rainfall_mm=450.0, max_temp_celsius=34.0, land_use="wheat_monoculture")
    assessment = reasoning.evaluate(telemetry)
    
    recs = rec_engine.score_and_rank(telemetry, assessment)
    assert len(recs) >= 3
    assert recs[0]["rank"] == 1
    assert recs[0]["decision_score"] >= recs[1]["decision_score"]

# 15. Water Stress Penalty Behavior
def test_15_water_penalty_applied_to_high_water_crop(repo, reasoning):
    rec_engine = RecommendationEngine(repo)
    telemetry = EnvironmentalTelemetry(soc_percent=0.35, annual_rainfall_mm=450.0, max_temp_celsius=34.0, land_use="wheat_monoculture")
    assessment = reasoning.evaluate(telemetry)
    
    recs = rec_engine.score_and_rank(telemetry, assessment)
    clover_rec = next(r for r in recs if r["slug"] == "high_water_clover_cover")
    legume_rec = next(r for r in recs if r["slug"] == "legume_intercropping")
    
    assert clover_rec["water_penalty_applied"] is True
    assert legume_rec["decision_score"] > clover_rec["decision_score"]

# 16. Evidence Retrieval with DOI & Provenance
def test_16_evidence_endpoint_returns_valid_doi(client):
    response = client.get("/api/v1/evidence/fao_soil_bulletin_80_p42")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["evidence"]["doi"] == "10.4060/ca9280en"
    assert "Cicer arietinum" in data["evidence"]["excerpt"]

# 17. Supported Claim Accepted by Validator
def test_17_supported_claim_accepted(repo):
    chunks = repo.search_chunks("legume intercropping", limit=2)
    validator = EvidenceValidator(chunks)
    
    draft = "Legume intercropping achieves an annual soil organic carbon increase of 0.12% per year."
    res = validator.validate_and_sanitize(draft)
    assert "0.12%" in res["sanitized_text"]
    assert res["claims_supported"] >= 1
    assert any(l["status"] == "SUPPORTED" for l in res["evidence_ledger"])

# 18. Unsupported Numeric Claim Rejected & Sanitized
def test_18_unsupported_numeric_claim_rejected(repo):
    chunks = repo.search_chunks("legume intercropping", limit=2)
    validator = EvidenceValidator(chunks)
    
    draft = "Legume intercropping increases biodiversity by 85% and improves SOC by 0.12% per year."
    res = validator.validate_and_sanitize(draft)
    
    assert "85%" not in res["sanitized_text"]
    assert "[documented positive increase]" in res["sanitized_text"]
    assert res["claims_stripped"] >= 1
    assert any(l["status"] == "UNSUPPORTED" and l["action"] == "STRIPPED_NUMBER" for l in res["evidence_ledger"])

# 19. Unsupported Qualitative Claim Handled with Caveat
def test_19_unsupported_qualitative_claim_caveat(repo):
    chunks = repo.search_chunks("legume intercropping", limit=2)
    validator = EvidenceValidator(chunks)
    
    draft = "Synthetic chemical spray guarantees complete pest elimination without ecological consequence."
    res = validator.validate_and_sanitize(draft)
    assert any(l["action"] == "FLAGGED_CAVEAT" for l in res["evidence_ledger"])

# 20. Confidence Reflects Evidence & Data Quality
def test_20_confidence_reflects_evidence_quality(repo):
    chunks = repo.search_chunks("legume intercropping", limit=2)
    validator_with_evidence = EvidenceValidator(chunks)
    res_high = validator_with_evidence.validate_and_sanitize("Legume intercropping increases SOC by 0.12% per year.", completeness_ratio=1.0)
    
    validator_empty = EvidenceValidator([])
    res_low = validator_empty.validate_and_sanitize("Legume intercropping increases SOC by 0.12% per year.", completeness_ratio=0.5)
    
    assert res_high["confidence_score"] > res_low["confidence_score"]
    assert res_low["confidence_badge"] == "LOW"
    assert res_low["evidence_status"] == "INSUFFICIENT_EVIDENCE"

# 21. API End-to-End Chat Workflow
def test_21_api_end_to_end_chat_workflow(client):
    # Step 1: Incomplete query
    r1 = client.post("/api/v1/chat", json={"message": "My soil is degraded and dry"})
    assert r1.status_code == 200
    d1 = r1.json()
    assert d1["status"] == "CLARIFICATION_REQUIRED"
    sess_id = d1["session_id"]
    
    # Step 2: Complete telemetry
    r2 = client.post("/api/v1/chat", json={
        "session_id": sess_id,
        "message": "SOC is 0.35%, rainfall 450 mm, and we grow wheat monoculture"
    })
    assert r2.status_code == 200
    d2 = r2.json()
    assert d2["status"] == "ANALYSIS_COMPLETE"
    assert "compound_risk" in d2["assessment"]
    assert len(d2["recommendations"]) > 0
    assert d2["recommendations"][0]["slug"] == "legume_intercropping"
    assert len(d2["evidence_sources"]) > 0
    assert len(d2["validation"]["evidence_ledger"]) > 0

# 22. Temperature in Reasoning (F2)
def test_22_temperature_affects_reasoning(reasoning):
    t_normal = EnvironmentalTelemetry(soc_percent=1.5, annual_rainfall_mm=800.0, max_temp_celsius=26.0, land_use="pasture")
    res_normal = reasoning.evaluate(t_normal)
    assert res_normal.stress_levels["thermal_stress"] == "LOW"
    assert res_normal.thermal_stress <= 0.20

    t_extreme = EnvironmentalTelemetry(soc_percent=1.5, annual_rainfall_mm=800.0, max_temp_celsius=39.0, land_use="pasture")
    res_extreme = reasoning.evaluate(t_extreme)
    assert res_extreme.stress_levels["thermal_stress"] == "CRITICAL"
    assert res_extreme.thermal_stress >= 0.70
    assert any(cf["stressor"] == "EXTREME_THERMAL_STRESS" for cf in res_extreme.causal_factors)

# 23. Soil pH in Reasoning (F8)
def test_23_soil_ph_affects_reasoning(reasoning):
    t_neutral = EnvironmentalTelemetry(soc_percent=1.5, annual_rainfall_mm=800.0, soil_ph=6.8, land_use="pasture")
    res_neutral = reasoning.evaluate(t_neutral)
    assert res_neutral.stress_levels["ph_stress"] == "LOW"

    t_acid = EnvironmentalTelemetry(soc_percent=1.5, annual_rainfall_mm=800.0, soil_ph=5.1, land_use="pasture")
    res_acid = reasoning.evaluate(t_acid)
    assert res_acid.stress_levels["ph_stress"] == "HIGH"
    assert res_acid.ph_stress >= 0.60
    assert any(cf["stressor"] == "ACID_SOIL_TOXICITY" for cf in res_acid.causal_factors)

# 24. Expanded Land Use Slot Extraction (F4)
def test_24_expanded_land_use_extraction():
    test_cases = [
        ("I grow corn on my farm", "corn_crop"),
        ("Our fields are flooded rice paddy", "rice_paddy"),
        ("We cultivate soybean on 50 hectares", "soybean_crop"),
        ("The plot is bare fallow land", "bare_fallow"),
        ("We manage an apple orchard", "orchard"),
        ("We practice agroforestry with trees", "agroforestry"),
        ("Our system has sorghum crops", "sorghum_crop"),
    ]
    for msg, expected in test_cases:
        extracted = ConversationManager.extract_slots(msg)
        assert extracted.get("land_use") == expected, f"Failed for '{msg}', expected '{expected}', got '{extracted.get('land_use')}'"

# 25. Time Horizon in Recommendations (F3)
def test_25_time_horizon_in_recommendations(repo, reasoning):
    rec_eng = RecommendationEngine(repo)
    telemetry = EnvironmentalTelemetry(soc_percent=0.35, annual_rainfall_mm=450.0, land_use="wheat_monoculture")
    assessment = reasoning.evaluate(telemetry)
    recs = rec_eng.score_and_rank(telemetry, assessment)
    for r in recs:
        assert "time_horizon" in r
        th = r["time_horizon"]
        assert "category" in th
        assert th["category"] in ("short", "medium", "long")
        assert "seasons" in th
        assert th["seasons"] >= 1
        assert "note" in th
        assert len(th["note"]) > 5

# 26. DSI Components Breakdown (F6)
def test_26_dsi_components_breakdown(repo, reasoning):
    rec_eng = RecommendationEngine(repo)
    telemetry = EnvironmentalTelemetry(soc_percent=0.35, annual_rainfall_mm=450.0, land_use="wheat_monoculture")
    assessment = reasoning.evaluate(telemetry)
    recs = rec_eng.score_and_rank(telemetry, assessment)
    for r in recs:
        assert "dsi_components" in r
        comps = r["dsi_components"]
        for key in ["environmental_fit", "evidence_strength", "biodiversity_gain", "soil_gain", "feasibility", "risk_penalty"]:
            assert key in comps
            assert 0.0 <= comps[key] <= 1.0

# 27. Dynamic Response Changes with Input (F1)
def test_27_dynamic_response_changes_with_input(client):
    # Chat 1: Dry wheat monoculture
    r1 = client.post("/api/v1/chat", json={
        "message": "SOC is 0.35%, rainfall is 400 mm, and we grow wheat monoculture with 36C summer temp"
    })
    assert r1.status_code == 200
    d1 = r1.json()
    assert d1["status"] == "ANALYSIS_COMPLETE"

    # Chat 2: High rainfall pasture with acidic soil
    r2 = client.post("/api/v1/chat", json={
        "message": "SOC is 1.8%, rainfall is 900 mm, pasture with soil pH 5.0 and 24C temp"
    })
    assert r2.status_code == 200
    d2 = r2.json()
    assert d2["status"] == "ANALYSIS_COMPLETE"

    assert d1["response"] != d2["response"]
    assert d1["assessment"]["compound_risk"] != d2["assessment"]["compound_risk"]

# 28. Whitespace Message Rejected (F12)
def test_28_whitespace_message_rejected(client):
    r_empty = client.post("/api/v1/chat", json={"message": "   "})
    assert r_empty.status_code == 200
    data = r_empty.json()
    assert data["success"] is False
    assert data["status"] == "INVALID_INPUT"

# 29. Interventions Catalog Endpoint (F11)
def test_29_interventions_endpoint(client):
    r = client.get("/api/v1/interventions")
    assert r.status_code == 200
    data = r.json()
    assert data["success"] is True
    assert data["count"] >= 8
    assert len(data["interventions"]) >= 8
    slugs = [i["slug"] for i in data["interventions"]]
    assert "legume_intercropping" in slugs
    assert "swale_contour_water_buffering" in slugs

# 30. New Evidence Corpus Chunks Retrieval (F5)
def test_30_new_corpus_chunks_retrieval(repo):
    # Test soil pH chunk retrieval
    ph_chunk = repo.get_chunk("fao_swsr_2015_ch5")
    assert ph_chunk is not None
    assert "5.5" in ph_chunk["excerpt"]
    assert "aluminum" in ph_chunk["excerpt"].lower()
    assert ph_chunk["doi"] == "10.4060/i5199en"

    # Test thermal stress chunk retrieval
    thermal_chunk = repo.get_chunk("ipcc_srccl_ch2_p120")
    assert thermal_chunk is not None
    assert "34" in thermal_chunk["excerpt"]
    assert "10.1017/9781009157988" in thermal_chunk["doi"]

# 31. Optional Ecological Slots (F9, F10)
def test_31_optional_species_richness_and_pollution(reasoning):
    slots = ConversationManager.extract_slots("We have low species richness and pesticide runoff from neighboring farms")
    assert slots.get("species_richness") == "LOW"
    assert slots.get("pollution_level") == "HIGH"

    telemetry = EnvironmentalTelemetry(
        soc_percent=1.8,
        annual_rainfall_mm=800.0,
        land_use="pasture",
        species_richness="LOW",
        pollution_level="HIGH"
    )
    res = reasoning.evaluate(telemetry)
    assert res.stress_levels["biodiversity_stress"] == "HIGH"
    assert any(cf["stressor"] == "DEPLETED_SPECIES_RICHNESS" for cf in res.causal_factors)

# 32. Spatial Context and Bonus Coordinates (Hackathon Page 2 & 3)
def test_32_spatial_context_and_bonus_coordinates():
    msg = "My farm is in semi-arid region at lat 31.5, lon -102.3 with wheat monoculture"
    slots = ConversationManager.extract_slots(msg)
    assert slots.get("region") == "semi_arid"
    assert slots.get("latitude") == 31.5
    assert slots.get("longitude") == -102.3
    assert slots.get("land_use") == "wheat_monoculture"

# 33. User Baseline Telemetry Ground Truth Preservation
def test_33_user_telemetry_ground_truth_preservation(repo):
    chunks = repo.search_chunks("legume intercropping", limit=2)
    validator = EvidenceValidator(chunks)
    user_telemetry = {"soc_percent": 0.35, "annual_rainfall_mm": 450.0}
    
    draft = "Environmental Assessment: Severe soil carbon depletion (0.35% SOC) collides with hydrological deficit (450.0 mm/yr)."
    report = validator.validate_and_sanitize(draft, completeness_ratio=1.0, user_telemetry=user_telemetry)
    
    # Verify user numbers are retained as ground truth, not converted to [documented positive increase]
    assert "0.35%" in report["sanitized_text"]
    assert "450.0 mm" in report["sanitized_text"]
    assert any(l["action"] == "RETAINED" and "baseline" in l["detail"].lower() for l in report["evidence_ledger"])
