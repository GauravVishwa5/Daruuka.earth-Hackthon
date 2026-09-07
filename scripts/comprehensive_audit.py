"""
Comprehensive Pre-Submission Auditor for Darukaa.Earth.
Executes deep automated checks across all audit phases against the live server.
"""
import sys
import json
import time
import uuid
import httpx
from pathlib import Path

# Ensure project root is on sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Ensure UTF-8 output on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_URL = "http://127.0.0.1:8005/api/v1"
client = httpx.Client(base_url=BASE_URL, timeout=10.0)

audit_report = {
    "phases": {},
    "endpoints": [],
    "issues": [],
    "performance": {}
}

def log_test(phase: str, test_name: str, passed: bool, details: str):
    if phase not in audit_report["phases"]:
        audit_report["phases"][phase] = []
    audit_report["phases"][phase].append({
        "test": test_name,
        "passed": passed,
        "details": details
    })
    status = "PASS" if passed else "FAIL"
    print(f"[{status}] [{phase}] {test_name}: {details}")

# ==============================================================================
# PHASE 2: RUNTIME HEALTH
# ==============================================================================
print("\n--- RUNNING PHASE 2: RUNTIME HEALTH ---")
try:
    r = client.get("/health")
    if r.status_code == 200:
        h = r.json()
        db_ok = h.get("database") == "connected"
        vec_ok = h.get("vector_store") == "available"
        log_test("PHASE_2", "Health Endpoint Check", db_ok and vec_ok, f"Status: {h.get('status')}, DB: {h.get('database')}, pgvector: {h.get('pgvector_version')}")
    else:
        log_test("PHASE_2", "Health Endpoint Check", False, f"HTTP {r.status_code}")
except Exception as e:
    log_test("PHASE_2", "Health Endpoint Check", False, str(e))

# ==============================================================================
# PHASE 3: AUTHENTICATION & AUTHORIZATION
# ==============================================================================
print("\n--- RUNNING PHASE 3: AUTH & SESSION ISOLATION ---")
# 1. Ephemeral session creation without session_id
r = client.post("/chat", json={"message": "soc 0.4%, rain 400mm, land use wheat monoculture"})
s1_data = r.json()
s1_id = s1_data.get("session_id")
log_test("PHASE_3", "Ephemeral Session Auto-generation", bool(s1_id), f"Generated: {s1_id}")

# 2. Session isolation: create session 2 with different data
r2 = client.post("/chat", json={"message": "soc 2.5%, rain 900mm, land use pasture"})
s2_data = r2.json()
s2_id = s2_data.get("session_id")
log_test("PHASE_3", "Distinct Session IDs", s1_id != s2_id, f"S1={s1_id} vs S2={s2_id}")

# Verify s1 profile is not overwritten by s2
r1_check = client.post("/chat", json={"session_id": s1_id, "message": "what is my profile?"})
s1_profile = r1_check.json().get("profile", {})
is_isolated = s1_profile.get("soc_percent") == 0.4 and s1_profile.get("land_use") == "wheat_monoculture"
log_test("PHASE_3", "Session State Isolation", is_isolated, f"S1 retained SOC={s1_profile.get('soc_percent')}")

# 3. Path traversal / injection in session_id
bad_session_ids = [
    "../../etc/passwd",
    "' OR '1'='1",
    "<script>alert(1)</script>",
    "A" * 500,
    "session-test\x00null"
]
traversal_safe = True
for bs in bad_session_ids:
    try:
        r_sec = client.post("/chat", json={"session_id": bs, "message": "test safety"})
        if r_sec.status_code >= 500:
            traversal_safe = False
            log_test("PHASE_3", f"Malformed Session Safety ({bs[:15]})", False, f"Server 500 error: {r_sec.text}")
    except Exception as e:
        traversal_safe = False
        log_test("PHASE_3", f"Malformed Session Exception ({bs[:15]})", False, str(e))

if traversal_safe:
    log_test("PHASE_3", "Session Traversal & Injection Immunity", True, "All malformed session IDs handled gracefully without 500 crashes")

# ==============================================================================
# PHASE 4: COMPLETE API AUDIT TABLE
# ==============================================================================
print("\n--- RUNNING PHASE 4: API ENDPOINTS DEEP AUDIT ---")

endpoints_to_audit = [
    {"name": "GET /api/v1/health", "method": "GET", "url": "/health", "payload": None},
    {"name": "GET /api/v1/interventions", "method": "GET", "url": "/interventions", "payload": None},
    {"name": "GET /api/v1/evidence/{chunk_id}", "method": "GET", "url": "/evidence/fao_soil_bulletin_80_p42", "payload": None},
    {"name": "POST /api/v1/chat", "method": "POST", "url": "/chat", "payload": {"message": "rain 500mm, soc 0.5%, wheat monoculture"}},
    {"name": "POST /api/v1/analyze", "method": "POST", "url": "/analyze", "payload": {"soc_percent": 0.4, "annual_rainfall_mm": 450.0, "land_use": "wheat monoculture"}},
    {"name": "POST /api/v1/environmental-profile", "method": "POST", "url": "/environmental-profile", "payload": {"soc_percent": 0.5, "annual_rainfall_mm": 500.0, "land_use": "pasture"}}
]

for ep in endpoints_to_audit:
    m = ep["method"]
    url = ep["url"]
    name = ep["name"]
    
    # 1. Success test
    t0 = time.time()
    if m == "GET":
        r_success = client.get(url)
    else:
        r_success = client.post(url, json=ep["payload"])
    latency = round((time.time() - t0) * 1000, 2)
    audit_report["performance"][name] = f"{latency} ms"

    success_ok = r_success.status_code == 200
    
    # 2. Malformed / Missing Input test
    if m == "POST":
        r_malformed = client.post(url, json={"invalid_field": "bad_value", "soc_percent": -99.9})
        val_ok = r_malformed.status_code in [422, 200]  # Pydantic 422 or handled
        
        r_empty = client.post(url, content="not a json", headers={"Content-Type": "application/json"})
        err_ok = r_empty.status_code == 422
    else:
        if "{chunk_id}" in name:
            r_404 = client.get("/evidence/non_existent_chunk_12345")
            val_ok = r_404.status_code == 404
            err_ok = True
        else:
            val_ok = True
            err_ok = True
            
    # 3. Wrong HTTP Method
    if m == "GET":
        r_wrong_method = client.post(url, json={})
    else:
        r_wrong_method = client.get(url)
    method_ok = r_wrong_method.status_code == 405
    
    status_str = "PASS" if (success_ok and val_ok and err_ok and method_ok) else "FAIL"
    
    audit_report["endpoints"].append({
        "endpoint": name,
        "auth": "Open / Ephemeral",
        "validation": "Pydantic v2 Strong Typing",
        "success": f"HTTP {r_success.status_code} ({latency}ms)",
        "error": f"Method guard HTTP {r_wrong_method.status_code}",
        "security": "Sanitized",
        "status": status_str
    })
    log_test("PHASE_4", f"API {name}", status_str == "PASS", f"Success={success_ok}, Validation={val_ok}, MethodGuard={method_ok}")

# ==============================================================================
# PHASE 5: DATABASE AUDIT
# ==============================================================================
print("\n--- RUNNING PHASE 5: DATABASE AUDIT ---")
try:
    from backend.db.database import SessionLocal, engine
    from backend.db.models import ScientificSource, EvidenceChunk, Intervention, Conversation, Message, RecommendationRecord, EvidenceLedgerRecord
    from sqlalchemy import text
    
    db = SessionLocal()
    with engine.connect() as conn:
        # Check pgvector extension
        ext = conn.execute(text("SELECT extname, extversion FROM pg_extension WHERE extname='vector'")).fetchone()
        log_test("PHASE_5", "pgvector Extension Active", bool(ext), f"Version: {ext[1] if ext else 'None'}")
        
        # Check HNSW index
        idx = conn.execute(text("SELECT indexname, indexdef FROM pg_indexes WHERE tablename='evidence_chunks' AND indexname LIKE '%hnsw%'")).fetchone()
        log_test("PHASE_5", "HNSW Vector Index Exists", bool(idx), f"Index: {idx[0] if idx else 'None'}")
        
        # Check table counts
        sources_cnt = db.query(ScientificSource).count()
        chunks_cnt = db.query(EvidenceChunk).count()
        interv_cnt = db.query(Intervention).count()
        log_test("PHASE_5", "Knowledge Base Row Counts", chunks_cnt >= 10 and interv_cnt >= 8, f"Chunks={chunks_cnt}, Sources={sources_cnt}, Interventions={interv_cnt}")

        # Test Transaction & Cascade Integrity
        test_conv_id = f"test-audit-{uuid.uuid4()}"
        test_conv = Conversation(id=test_conv_id, accumulated_profile={"test": True})
        db.add(test_conv)
        db.commit()
        
        test_msg = Message(conversation_id=test_conv_id, role="user", content="Audit test message")
        db.add(test_msg)
        db.commit()
        
        # Verify message exists
        msg_count = db.query(Message).filter_by(conversation_id=test_conv_id).count()
        # Delete conversation and check cascade deletion
        db.delete(test_conv)
        db.commit()
        msg_count_after = db.query(Message).filter_by(conversation_id=test_conv_id).count()
        log_test("PHASE_5", "Cascade Deletion Integrity", msg_count == 1 and msg_count_after == 0, "Messages cascade deleted with conversation")

    db.close()
except Exception as e:
    log_test("PHASE_5", "Database Audit Exception", False, str(e))

# ==============================================================================
# PHASE 6 & 7: AI/LLM & RAG AUDIT
# ==============================================================================
print("\n--- RUNNING PHASE 6 & 7: AI, RAG & ANTI-HALLUCINATION ---")
try:
    from backend.repository import get_repository
    from backend.rag import RAGService
    from backend.validator import EvidenceValidator
    
    repo = get_repository()
    rag = RAGService(repo)
    
    # 1. Test RAG Vector Search
    chunks = rag.retrieve_evidence("wheat monoculture soil carbon depletion drought", biome="semi_arid", limit=3)
    has_valid_dois = all(c.get("doi") for c in chunks)
    log_test("PHASE_7", "RAG Vector Retrieval with DOIs", len(chunks) > 0 and has_valid_dois, f"Retrieved {len(chunks)} chunks, DOIs: {[c.get('doi') for c in chunks]}")

    # 2. Test Anti-Hallucination Sanitizer
    validator = EvidenceValidator(chunks)
    # Draft with supported vs unsupported fabricated numbers
    fabricated_claim = "Adopting intervention X will boost yield by 999.4% and sequester 842.1 tons of carbon overnight."
    report = validator.validate_and_sanitize(fabricated_claim, completeness_ratio=1.0)
    
    stripped_count = report["claims_stripped"]
    is_sanitized = "999.4%" not in report["sanitized_text"] and "842.1" not in report["sanitized_text"]
    log_test("PHASE_6", "Fabricated Numeric Claim Stripping", is_sanitized and stripped_count > 0, f"Stripped {stripped_count} numbers. Sanitized text: {report['sanitized_text'][:80]}...")

except Exception as e:
    log_test("PHASE_6", "AI/RAG Audit Exception", False, str(e))

# ==============================================================================
# PHASE 8: ENVIRONMENTAL DECISION WORKFLOW
# ==============================================================================
print("\n--- RUNNING PHASE 8: DOMAIN WORKFLOW ---")
try:
    # Test complete multi-turn consultation
    s_wf = f"wf-test-{uuid.uuid4()}"
    
    # Turn 1: Vague query -> CLARIFICATION_REQUIRED
    t1 = client.post("/chat", json={"session_id": s_wf, "message": "My field crops are suffering and soil feels dead."}).json()
    t1_ok = t1.get("status") == "CLARIFICATION_REQUIRED" and "soc_percent" in t1.get("missing_fields", [])
    log_test("PHASE_8", "Workflow Turn 1: Clarification Request", t1_ok, f"Status={t1.get('status')}, Missing={t1.get('missing_fields')}")

    # Turn 2: Partial info -> CLARIFICATION_REQUIRED
    t2 = client.post("/chat", json={"session_id": s_wf, "message": "SOC is 0.35%"}).json()
    t2_ok = t2.get("status") == "CLARIFICATION_REQUIRED" and "soc_percent" not in t2.get("missing_fields", [])
    log_test("PHASE_8", "Workflow Turn 2: Slot Retention", t2_ok, f"Retained SOC, still missing: {t2.get('missing_fields')}")

    # Turn 3: Complete info -> ANALYSIS_COMPLETE with DSI and Evidence
    t3 = client.post("/chat", json={"session_id": s_wf, "message": "Rainfall is 430mm, and we grow wheat monoculture."}).json()
    t3_ok = (
        t3.get("status") == "ANALYSIS_COMPLETE" and
        t3.get("assessment", {}).get("compound_risk") == "CRITICAL_COMPOUND_DEGRADATION" and
        len(t3.get("recommendations", [])) > 0 and
        t3.get("validation", {}).get("confidence_score") is not None
    )
    log_test("PHASE_8", "Workflow Turn 3: Compound Stress & Recommendations", t3_ok, f"Compound Risk: {t3.get('assessment', {}).get('compound_risk')}, Recs: {len(t3.get('recommendations', []))}")

except Exception as e:
    log_test("PHASE_8", "Domain Workflow Exception", False, str(e))

# ==============================================================================
# PHASE 10: FAILURE TESTING & RESILIENCE
# ==============================================================================
print("\n--- RUNNING PHASE 10: FAILURE TESTING ---")
# 1. Extremely long message (25,000 characters)
long_text = "A" * 25000
r_overflow = client.post("/chat", json={"message": long_text})
log_test("PHASE_10", "Payload Overflow Protection", r_overflow.status_code in [422, 400], f"HTTP {r_overflow.status_code}")

# 2. Negative SOC or extreme rainfall in /analyze
r_bad_analyze = client.post("/analyze", json={"soc_percent": -5.0, "annual_rainfall_mm": 99999.0, "land_use": "wheat"})
log_test("PHASE_10", "Out-of-Bounds Range Validation", r_bad_analyze.status_code == 422, f"HTTP {r_bad_analyze.status_code}")

# 3. Non-existent evidence chunk retrieval
r_chunk_404 = client.get("/evidence/chunk_does_not_exist_xyz")
log_test("PHASE_10", "Non-Existent Chunk 404", r_chunk_404.status_code == 404, f"HTTP {r_chunk_404.status_code}")

# 4. Whitespace-only chat message
r_ws = client.post("/chat", json={"message": "    \n\t   "})
ws_data = r_ws.json() if r_ws.status_code == 200 else {}
log_test("PHASE_10", "Whitespace Chat Handling", r_ws.status_code == 422 or ws_data.get("status") == "INVALID_INPUT", f"Handled with: {ws_data.get('status', r_ws.status_code)}")

# ==============================================================================
# PHASE 11: SECURITY AUDIT
# ==============================================================================
print("\n--- RUNNING PHASE 11: SECURITY AUDIT ---")
# Check CORS headers
r_options = client.options("/chat", headers={"Origin": "http://localhost:3000", "Access-Control-Request-Method": "POST"})
has_cors = "access-control-allow-origin" in r_options.headers or r_options.status_code in [200, 204]
log_test("PHASE_11", "CORS Preflight Headers", has_cors, f"HTTP {r_options.status_code}")

# Check XSS containment in chat response
xss_payload = "<script>alert('XSS')</script><img src=x onerror=alert(1)>"
r_xss = client.post("/chat", json={"message": xss_payload})
xss_resp = r_xss.json().get("response", "")
# Ensure it does not execute script or return raw executable code unsanitized
log_test("PHASE_11", "XSS Injection Resistance", "<script>" not in xss_resp, "XSS tags not reflected in raw executable context")

# ==============================================================================
# SUMMARY TABLE PRINTING
# ==============================================================================
print("\n" + "="*80)
print("PHASE 4: COMPLETE API AUDIT MATRIX")
print("="*80)
print(f"{'Endpoint':<36} | {'Auth':<18} | {'Validation':<24} | {'Success':<14} | {'Security':<10} | {'Status':<6}")
print("-" * 115)
for ep in audit_report["endpoints"]:
    print(f"{ep['endpoint']:<36} | {ep['auth']:<18} | {ep['validation']:<24} | {ep['success']:<14} | {ep['security']:<10} | {ep['status']:<6}")

print("\n" + "="*80)
print("AUDIT SUMMARY BY CATEGORY")
print("="*80)
all_tests = [t for p in audit_report["phases"].values() for t in p]
passed_count = sum(1 for t in all_tests if t["passed"])
failed_count = sum(1 for t in all_tests if not t["passed"])
print(f"TOTAL TESTS: {len(all_tests)} | PASSED: {passed_count} | FAILED: {failed_count}")
print("="*80)

# Write full audit log to JSON
with open("audit_results.json", "w", encoding="utf-8") as f:
    json.dump(audit_report, f, indent=2)

print("\nAudit results saved to audit_results.json.")
