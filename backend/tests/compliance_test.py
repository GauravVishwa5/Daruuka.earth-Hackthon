"""
Compliance evidence-gathering script for Darukaa.Earth hackathon audit.
Run from project root: .\venv\Scripts\python.exe backend/tests/compliance_test.py
"""
import httpx
import json

BASE = "http://127.0.0.1:8005/api/v1"
c = httpx.Client(base_url=BASE, timeout=15)

results = {}

def section(title):
    print(f"\n{'='*60}")
    print(f" {title}")
    print('='*60)

# ── Health ──────────────────────────────────────────────────
section("HEALTH CHECK")
r = c.get("/health")
h = r.json()
results["health"] = h
print(json.dumps(h, indent=2))

# ── Interventions catalog ────────────────────────────────────
section("INTERVENTIONS CATALOG")
r = c.get("/interventions") if False else None  # no /interventions endpoint - check in analyze
print("No /interventions endpoint exposed (data comes from DB via analyze)")

# ── TURN 1: Vague query ───────────────────────────────────────
section("TURN 1: Vague biodiversity complaint")
r1 = c.post("/chat", json={"message": "Biodiversity is declining on my land"})
d1 = r1.json()
results["turn1"] = {"status": d1.get("status"), "missing": d1.get("missing_fields"), "response": d1.get("response")}
print("Status:", d1.get("status"))
print("Missing fields:", d1.get("missing_fields"))
print("Response:", d1.get("response"))
sid = d1["session_id"]

# ── TURN 2: SOC only ──────────────────────────────────────────
section("TURN 2: SOC only (partial info)")
r2 = c.post("/chat", json={"session_id": sid, "message": "SOC is 0.3%"})
d2 = r2.json()
print("Status:", d2.get("status"))
print("Profile now:", d2.get("profile"))
print("Still asking for:", d2.get("missing_fields"))

# ── TURN 3: Rainfall ─────────────────────────────────────────
section("TURN 3: Add rainfall")
r3 = c.post("/chat", json={"session_id": sid, "message": "rainfall is about 420mm per year"})
d3 = r3.json()
print("Status:", d3.get("status"))
print("Profile now:", d3.get("profile"))

# ── TURN 4: Land use - completes the profile ──────────────────
section("TURN 4: Land use - triggers full analysis")
r4 = c.post("/chat", json={"session_id": sid, "message": "crop is wheat monoculture"})
d4 = r4.json()
results["final_analysis"] = d4
print("Status:", d4.get("status"))
a = d4.get("assessment", {})
print("\nAssessment:")
print("  compound_risk:", a.get("compound_risk"))
print("  key_factors:", a.get("key_factors"))
print("  soil_stress (numeric):", a.get("soil_stress"))
print("  water_stress (numeric):", a.get("water_stress"))
print("  habitat_pressure (numeric):", a.get("habitat_pressure"))
print("  heuristic_label:", a.get("heuristic_label"))
print("  summary:", a.get("summary_text","")[:160])

recs = d4.get("recommendations", [])
print(f"\nRecommendations: {len(recs)}")
for rec in recs[:4]:
    ev_cnt = len(rec.get("evidence_sources", []))
    benefits = list(rec.get("primary_benefits", {}).keys())
    tradeoffs = [t["risk"] for t in rec.get("tradeoffs", [])]
    print(f"  #{rec['rank']} {rec['name']}  DSI={rec['decision_score']}  evidence={ev_cnt}  water_penalty={rec.get('water_penalty_applied')}")
    print(f"      Benefits: {benefits}")
    print(f"      Tradeoffs: {tradeoffs}")
    if rec.get("evidence_sources"):
        e = rec["evidence_sources"][0]
        print(f"      Source: {e.get('publisher')} ({e.get('year')}) DOI:{e.get('doi')}")

val = d4.get("validation", {})
print("\nValidation:")
print("  confidence:", val.get("confidence_badge"), val.get("confidence_score"))
print("  claims_evaluated:", val.get("claims_evaluated"))
print("  claims_supported:", val.get("claims_supported"))
print("  claims_stripped:", val.get("claims_stripped"))
ledger = val.get("evidence_ledger", [])
print(f"  ledger entries: {len(ledger)}")
for l in ledger[:3]:
    print(f"    [{l.get('action')}] {l.get('claim', '')[:80]}")

ev_sources = d4.get("evidence_sources", [])
print(f"\nEvidence sources returned: {len(ev_sources)}")
for ev in ev_sources:
    print(f"  {ev.get('publisher')} ({ev.get('year')}) doi:{ev.get('doi')}")
    print(f"  Excerpt: {ev.get('excerpt','')[:100]}")

# ── Structured /analyze ───────────────────────────────────────
section("STRUCTURED /analyze ENDPOINT")
r5 = c.post("/analyze", json={
    "soc_percent": 0.3,
    "annual_rainfall_mm": 420.0,
    "land_use": "wheat monoculture",
    "max_temp_celsius": 34.0,
    "soil_ph": 6.8
})
d5 = r5.json()
print("Success:", d5.get("success"))
a5 = d5.get("assessment", {})
print("compound_risk:", a5.get("compound_risk"))
print("key_factors:", a5.get("key_factors"))
print("heuristic_label:", a5.get("heuristic_label"))
print("Ranked recs:", len(d5.get("ranked_recommendations", [])))

# ── Evidence endpoint ─────────────────────────────────────────
section("EVIDENCE RETRIEVAL by chunk_id")
r6 = c.get("/evidence/fao_soil_bulletin_80_p42")
d6 = r6.json()
ev = d6.get("evidence", {})
print("DOI:", ev.get("doi"))
print("Publisher:", ev.get("publisher"))
print("Excerpt[:120]:", str(ev.get("excerpt",""))[:120])

# ── Edge: empty input ─────────────────────────────────────────
section("EDGE: EMPTY INPUT")
r7 = c.post("/chat", json={"message": " "})
print("HTTP:", r7.status_code)
if r7.status_code == 422:
    print("422 Validation error - pydantic min_length check working")
elif r7.status_code == 200:
    print("Response:", r7.json().get("response","")[:100])

# ── Edge: only one metric ─────────────────────────────────────
section("EDGE: SINGLE METRIC ONLY")
r8 = c.post("/chat", json={"message": "My SOC is 0.4%"})
d8 = r8.json()
print("Status:", d8.get("status"))
print("Missing:", d8.get("missing_fields"))

print("\n\n=== EVIDENCE COLLECTION COMPLETE ===")
