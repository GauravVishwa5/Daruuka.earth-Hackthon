import sys
import uuid
from pathlib import Path
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Ensure project root is in sys.path so 'backend' package is always resolvable
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

try:
    from backend.config import settings
    from backend.repository import get_repository
    from backend.reasoning import MultiMetricReasoningEngine, EnvironmentalTelemetry
    from backend.recommendation import RecommendationEngine
    from backend.rag import RAGService
    from backend.validator import EvidenceValidator
    from backend.conversation import ConversationManager
except ImportError:
    from config import settings
    from repository import get_repository
    from reasoning import MultiMetricReasoningEngine, EnvironmentalTelemetry
    from recommendation import RecommendationEngine
    from rag import RAGService
    from validator import EvidenceValidator
    from conversation import ConversationManager

try:
    from backend.db.database import check_db_connection
except ImportError:
    from db.database import check_db_connection

app = FastAPI(
    title="Darukaa.Earth AI Biodiversity Decision Engine",
    version="1.0.0",
    description="Evidence-Grounded Multi-Metric Environmental Intelligence Platform"
)

# CORS configuration - strict origins from config
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins or ["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Core Services Initialization
repo = get_repository()
reasoning_engine = MultiMetricReasoningEngine()
rec_engine = RecommendationEngine(repo)
rag_service = RAGService(repo)

# Request & Response Schemas
class ChatRequest(BaseModel):
    session_id: Optional[str] = Field(None, max_length=128, pattern=r"^[a-zA-Z0-9_\-\.]+$")
    message: str = Field(..., min_length=1, max_length=2000)

class ProfileUpdateRequest(BaseModel):
    session_id: Optional[str] = Field(None, max_length=128, pattern=r"^[a-zA-Z0-9_\-\.]+$")
    soc_percent: Optional[float] = Field(None, ge=0.0, le=20.0)
    annual_rainfall_mm: Optional[float] = Field(None, ge=0.0, le=5000.0)
    max_temp_celsius: Optional[float] = Field(None, ge=-20.0, le=60.0)
    land_use: Optional[str] = None
    soil_ph: Optional[float] = Field(None, ge=3.0, le=11.0)
    species_richness: Optional[str] = None
    pollution_level: Optional[str] = None
    deforestation_pressure: Optional[str] = None
    region: Optional[str] = None
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0)

class AnalyzeRequest(BaseModel):
    soc_percent: float = Field(..., ge=0.0, le=20.0)
    annual_rainfall_mm: float = Field(..., ge=0.0, le=5000.0)
    land_use: str = Field(...)
    max_temp_celsius: float = Field(30.0, ge=-20.0, le=60.0)
    soil_ph: float = Field(7.0, ge=3.0, le=11.0)
    species_richness: Optional[str] = None
    pollution_level: Optional[str] = None
    deforestation_pressure: Optional[str] = None
    region: Optional[str] = "semi_arid"
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0)

@app.get("/api/v1/health")
def health_check():
    db_status = check_db_connection()
    is_healthy = db_status.get("connected", False) and db_status.get("pgvector_active", False)
    active_repo = get_repository()
    return {
        "status": "healthy" if is_healthy else "unhealthy",
        "database": "connected" if db_status.get("connected") else "disconnected",
        "vector_store": "available" if db_status.get("pgvector_active") else "unavailable",
        "llm": "configured" if (settings.openai_api_key and not settings.openai_api_key.startswith("your_")) else "mock_fallback",
        "database_name": db_status.get("database"),
        "pgvector_version": db_status.get("pgvector_version"),
        "active_repository": active_repo.__class__.__name__,
        "app_env": settings.app_env
    }

@app.post("/api/v1/chat")
def handle_chat(req: ChatRequest):
    session_id = req.session_id or str(uuid.uuid4())
    message = req.message.strip()
    if not message:
        return {
            "success": False,
            "status": "INVALID_INPUT",
            "response": "Please enter a message describing your environmental situation.",
            "profile": {},
            "assessment": None,
            "recommendations": []
        }
    
    # Load session state
    session_data = repo.get_conversation(session_id) or {
        "accumulated_profile": {},
        "messages": []
    }
    current_profile = session_data.get("accumulated_profile", {})
    messages = session_data.get("messages", [])

    # Evaluate turn for slot-filling
    turn_eval = ConversationManager.evaluate_turn(req.message, current_profile)
    updated_profile = turn_eval["profile"]
    
    messages.append({"role": "user", "content": req.message})

    # Case A: Missing Information (Slot-filling prompt)
    if turn_eval["status"] == "CLARIFICATION_REQUIRED":
        assistant_reply = turn_eval["clarification_prompt"]
        messages.append({"role": "assistant", "content": assistant_reply})
        repo.save_conversation(session_id, updated_profile, messages)
        
        return {
            "success": True,
            "session_id": session_id,
            "status": "CLARIFICATION_REQUIRED",
            "response": assistant_reply,
            "missing_fields": turn_eval["missing_fields"],
            "profile": updated_profile,
            "assessment": None,
            "recommendations": []
        }

    # Case B: Ready for Multi-Metric Reasoning
    telemetry = EnvironmentalTelemetry(
        soc_percent=float(updated_profile["soc_percent"]),
        annual_rainfall_mm=float(updated_profile["annual_rainfall_mm"]),
        land_use=str(updated_profile["land_use"]),
        max_temp_celsius=float(updated_profile.get("max_temp_celsius", 32.0)),
        soil_ph=float(updated_profile.get("soil_ph", 7.2)),
        species_richness=updated_profile.get("species_richness"),
        pollution_level=updated_profile.get("pollution_level"),
        deforestation_pressure=updated_profile.get("deforestation_pressure"),
        region=str(updated_profile.get("region", "semi_arid")),
        latitude=updated_profile.get("latitude"),
        longitude=updated_profile.get("longitude")
    )

    # 1. Deterministic Multi-Metric Assessment
    assessment = reasoning_engine.evaluate(telemetry)

    # 2. Algorithmic Recommendation Ranking (DSI)
    ranked_recs = rec_engine.score_and_rank(telemetry, assessment)

    # 3. Scientific RAG Retrieval
    query_context = f"{telemetry.land_use} soil carbon {telemetry.soc_percent} rainfall {telemetry.annual_rainfall_mm}"
    evidence_chunks = rag_service.retrieve_evidence(query_context, biome=telemetry.region or "semi_arid", limit=3)

    # 4. Synthesize Dynamic Evidence Grounding & Draft Text
    top_rec = ranked_recs[0] if ranked_recs else None
    top_ev = evidence_chunks[0] if evidence_chunks else None

    rec_name = top_rec['name'] if top_rec else "Diversified Agroecological Management"
    ev_excerpt = top_ev.get('excerpt', '') if top_ev else ""
    ev_source = f"{top_ev.get('publisher', 'Scientific Literature')} ({top_ev.get('year', '')})" if top_ev else ""

    horizon_info = ""
    if top_rec and top_rec.get("time_horizon"):
        th = top_rec["time_horizon"]
        horizon_info = f"**Management Horizon:** {th.get('category', 'medium').capitalize()} term ({th.get('seasons', 1)} seasons). {th.get('note', '')}"

    benefits_str = "N/A"
    if top_rec and top_rec.get("primary_benefits"):
        benefits_str = ", ".join([
            f"{k.replace('_', ' ').capitalize()}: +{v}" if isinstance(v, (int, float)) else f"{k.replace('_', ' ').capitalize()}: {v}"
            for k, v in top_rec["primary_benefits"].items()
        ])

    draft_narrative = (
        f"**Environmental Assessment:** {assessment.summary_text}\n\n"
        f"**Top Recommendation:** {rec_name} (Decision Score: {top_rec['decision_score'] if top_rec else 'N/A'})\n\n"
        f"**Impacted Metrics:** {benefits_str}\n\n"
        f"{horizon_info}\n\n"
        f"**Scientific Grounding ({ev_source}):** {ev_excerpt}\n\n"
        f"**Identified Risk Factors:** {', '.join(assessment.key_factors) if assessment.key_factors else 'Baseline conditions'}."
    )

    # 5. Evidence Validation & Anti-Hallucination Sanitizer
    validator = EvidenceValidator(evidence_chunks)
    val_report = validator.validate_and_sanitize(draft_narrative, completeness_ratio=1.0, user_telemetry=telemetry.__dict__)

    confidence_badge = val_report["confidence_badge"]
    confidence_pct = round(val_report["confidence_score"] * 100)
    assistant_reply = val_report["sanitized_text"] + f"\n\n**Confidence Level:** {confidence_badge} ({confidence_pct}% evidence-grounded)"

    messages.append({"role": "assistant", "content": assistant_reply})
    repo.save_conversation(session_id, updated_profile, messages)
    repo.save_ledger_and_recs(session_id, ranked_recs[:4], val_report["evidence_ledger"])

    return {
        "success": True,
        "session_id": session_id,
        "status": "ANALYSIS_COMPLETE",
        "response": assistant_reply,
        "profile": updated_profile,
        "assessment": {
            "compound_risk": assessment.compound_risk,
            "stress_levels": assessment.stress_levels,
            "causal_factors": assessment.causal_factors,
            "water_penalty_active": assessment.water_penalty_active,
            "summary_text": assessment.summary_text,
            "soil_stress": assessment.soil_stress,
            "water_stress": assessment.water_stress,
            "habitat_pressure": assessment.habitat_pressure,
            "thermal_stress": assessment.thermal_stress,
            "ph_stress": assessment.ph_stress,
            "compound_state": assessment.compound_state,
            "key_factors": assessment.key_factors,
            "heuristic_label": assessment.heuristic_label
        },
        "recommendations": ranked_recs[:4],
        "evidence_sources": evidence_chunks,
        "validation": {
            "confidence_score": val_report["confidence_score"],
            "confidence_badge": val_report["confidence_badge"],
            "confidence_explanation": val_report.get("confidence_explanation", ""),
            "claims_evaluated": val_report["claims_evaluated"],
            "claims_supported": val_report["claims_supported"],
            "claims_stripped": val_report["claims_stripped"],
            "evidence_ledger": val_report["evidence_ledger"]
        }
    }

@app.post("/api/v1/environmental-profile")
def update_profile(req: ProfileUpdateRequest):
    session_id = req.session_id or str(uuid.uuid4())
    session_data = repo.get_conversation(session_id) or {"accumulated_profile": {}, "messages": []}
    profile = session_data.get("accumulated_profile", {})

    # Update non-null fields
    update_dict = req.model_dump(exclude_unset=True, exclude={"session_id"})
    profile.update(update_dict)
    repo.save_conversation(session_id, profile, session_data.get("messages", []))

    return {
        "success": True,
        "session_id": session_id,
        "profile": profile,
        "is_complete": all(profile.get(k) is not None for k in ["soc_percent", "annual_rainfall_mm", "land_use"])
    }

@app.post("/api/v1/analyze")
def analyze_pure(req: AnalyzeRequest):
    telemetry = EnvironmentalTelemetry(
        soc_percent=req.soc_percent,
        annual_rainfall_mm=req.annual_rainfall_mm,
        land_use=req.land_use,
        max_temp_celsius=req.max_temp_celsius,
        soil_ph=req.soil_ph,
        species_richness=req.species_richness,
        pollution_level=req.pollution_level,
        deforestation_pressure=req.deforestation_pressure,
        region=req.region or "semi_arid",
        latitude=req.latitude,
        longitude=req.longitude
    )
    assessment = reasoning_engine.evaluate(telemetry)
    recs = rec_engine.score_and_rank(telemetry, assessment)
    return {
        "success": True,
        "assessment": {
            "compound_risk": assessment.compound_risk,
            "stress_levels": assessment.stress_levels,
            "causal_factors": assessment.causal_factors,
            "water_penalty_active": assessment.water_penalty_active,
            "summary": assessment.summary_text,
            "soil_stress": assessment.soil_stress,
            "water_stress": assessment.water_stress,
            "habitat_pressure": assessment.habitat_pressure,
            "thermal_stress": assessment.thermal_stress,
            "ph_stress": assessment.ph_stress,
            "compound_state": assessment.compound_state,
            "key_factors": assessment.key_factors,
            "heuristic_label": assessment.heuristic_label
        },
        "ranked_recommendations": recs[:3]
    }

@app.get("/api/v1/interventions")
def list_interventions():
    """Browse the full ecological intervention catalog."""
    interventions = repo.get_all_interventions()
    return {
        "success": True,
        "count": len(interventions),
        "interventions": interventions
    }

@app.get("/api/v1/evidence/{chunk_id}")
def get_evidence(chunk_id: str):
    chunk = repo.get_chunk(chunk_id)
    if not chunk:
        raise HTTPException(status_code=404, detail=f"Evidence chunk '{chunk_id}' not found.")
    return {
        "success": True,
        "evidence": chunk
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=settings.port, reload=True)
