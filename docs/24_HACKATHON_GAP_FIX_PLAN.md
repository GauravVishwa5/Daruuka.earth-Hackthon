# 24 — Hackathon Gap Fix Plan

> **Derived from:** [23_HACKATHON_CHALLENGE_COMPLIANCE.md](./23_HACKATHON_CHALLENGE_COMPLIANCE.md)
>
> **Purpose:** Actionable implementation-only checklist for closing identified gaps before submission.
> **Estimated total effort:** ~6–7 hours of focused implementation.

---

## Fix Priority Summary

| Fix | File(s) | Time | Priority | Score Impact |
|:---|:---|:---|:---|:---|
| F1: Expand land use patterns | `backend/conversation.py` | 15 min | P1 | +1.5 |
| F2: Reject whitespace input | `backend/main.py` | 5 min | P2 | Minor |
| F3: Temperature in reasoning | `backend/reasoning.py` | 30 min | P1 | +3.0 |
| F4: Improve summary_text causal chain | `backend/reasoning.py` | 30 min | P1 | +2.0 |
| F5: Add time_horizon to recommendations | `data/interventions.json` + `backend/recommendation.py` | 20 min | P1 | +2.0 |
| F6: Add dsi_components to recommendation output | `backend/recommendation.py` | 20 min | P1 | +2.0 |
| F7: Add pH stressor to reasoning | `backend/reasoning.py` | 30 min | P2 | +1.5 |
| F8: Add /interventions endpoint | `backend/main.py` | 10 min | P2 | +0.5 |
| F9: Add 4 more corpus chunks | `data/scientific_corpus.json` + re-run init_db | 45 min | P1 | +2.5 |
| F10: Dynamic response text | `backend/main.py` | 45 min | P1 | +3.0 |

---

## F1 — Expand Land Use Patterns

**File:** `backend/conversation.py` → `extract_slots()`, lines 49-61

**Problem:** Only recognizes: wheat monoculture, monoculture, wheat, pasture/grassland, agroforestry.  
Users saying "I grow corn", "rice paddy", "soybean", "fallow land" get no land_use extracted.

**Fix:** Replace the `elif` chain with:
```python
# Extended land use recognition
LU_MAP = {
    "wheat monoculture": "wheat_monoculture",
    "wheat mono": "wheat_monoculture",
    "monoculture": "crop_monoculture",
    "wheat": "wheat_crop",
    "corn": "corn_crop",
    "maize": "corn_crop",
    "rice": "rice_paddy",
    "paddy": "rice_paddy",
    "soybean": "soybean_crop",
    "soy": "soybean_crop",
    "cotton": "cotton_crop",
    "barley": "barley_crop",
    "sorghum": "sorghum_crop",
    "fallow": "bare_fallow",
    "bare": "bare_fallow",
    "pasture": "pasture",
    "grassland": "pasture",
    "agroforestry": "agroforestry",
    "orchard": "orchard",
    "vineyard": "orchard",
    "forest": "managed_forest",
}
for keyword, lu_val in LU_MAP.items():
    if keyword in text_lower:
        extracted["land_use"] = lu_val
        break
```

---

## F2 — Reject Whitespace Input

**File:** `backend/main.py` → `handle_chat()`, immediately after `session_id` assignment.

**Fix:** Add one line:
```python
message = req.message.strip()
if not message:
    return {"success": False, "status": "INVALID_INPUT", "response": "Please enter a message describing your environmental situation."}
```

---

## F3 — Temperature in Reasoning Engine

**File:** `backend/reasoning.py` → `MultiMetricReasoningEngine.evaluate()`

**Scientific basis:** IPCC SRCCL Ch4 p185: "When summer temperatures exceed 32°C, evaporative demand compounds moisture deficits."  
Corpus chunk already present: `ipcc_srccl_ch4_p185` metrics: `["soc_percent", "annual_rainfall_mm", "max_temp_celsius"]`

**Fix:** Add after the water stress block (after line ~77):
```python
# 3b. Thermal Stress (IPCC SRCCL 2019: >32°C compounds moisture deficit)
if t.max_temp_celsius >= 38.0:
    s_thermal = "CRITICAL"
    causal_factors.append(CausalFactor(
        stressor="CRITICAL_THERMAL_EVAPORATIVE_STRESS",
        severity="CRITICAL",
        why=f"Maximum temperature of {t.max_temp_celsius}°C far exceeds 32°C IPCC threshold for compounding moisture deficits.",
        how="Evaporative demand at high temperatures accelerates soil moisture exhaustion and biological soil crust collapse.",
        what="Immediate shading, mulching, and windbreak establishment required to reduce surface temperature."
    ))
elif t.max_temp_celsius >= 32.0:
    s_thermal = "HIGH"
    causal_factors.append(CausalFactor(
        stressor="HIGH_THERMAL_EVAPORATIVE_STRESS",
        severity="HIGH",
        why=f"Maximum temperature {t.max_temp_celsius}°C exceeds 32°C IPCC moisture deficit compound threshold.",
        how="Evaporative loss at anthesis reduces grain filling efficiency and accelerates topsoil drying.",
        what="Cover crops with high reflectivity and deep-rooting windbreaks reduce surface temperatures."
    ))
else:
    s_thermal = "LOW"
stress_levels["thermal_stress"] = s_thermal
```

**Also update compound_state logic:** Include s_thermal in `severe_count`:
```python
severe_count = sum(1 for s in stress_levels.values() if s in ("CRITICAL", "HIGH"))
```

---

## F4 — Improve Causal Chain in summary_text

**File:** `backend/reasoning.py` → end of `evaluate()` method

**Problem:** Generic summary text. Judges need to see inter-variable causation, not just enumeration.

**Fix:** Generate summary_text dynamically based on actual stress combination:
```python
# Dynamic causal chain summary
factor_descs = []
if stress_levels.get("soil_stress") in ("CRITICAL", "HIGH"):
    factor_descs.append(f"critically depleted soil carbon ({t.soc_percent}% SOC) destroying the soil aggregate sponge")
if stress_levels.get("water_stress") in ("HIGH", "CRITICAL"):
    factor_descs.append(f"hydrological deficit ({t.annual_rainfall_mm}mm rainfall) compounding runoff and evaporative loss")
if stress_levels.get("biodiversity_stress") == "HIGH":
    factor_descs.append(f"monoculture pressure ({t.land_use}) eliminating floral diversity and pollinator corridors")
if stress_levels.get("thermal_stress") in ("CRITICAL", "HIGH"):
    factor_descs.append(f"thermal evaporative stress ({t.max_temp_celsius}°C) compounding moisture deficit")

if len(factor_descs) >= 2:
    summary_text = (
        f"{compound_risk.replace('_', ' ')}: "
        f"{' interacts with '.join(factor_descs)}. "
        f"These stressors form a self-reinforcing degradation cascade: low SOC reduces water infiltration, "
        f"water deficit worsens biodiversity stress, and monoculture prevents recovery."
    )
```

---

## F5 — Add time_horizon to Recommendations

**File:** `data/interventions.json` — add `time_horizon_seasons` and `time_horizon_note` to each entry.

**Examples:**
```json
// legume_intercropping
"time_horizon_seasons": 1,
"time_horizon_note": "Measurable SOC increase after 1 growing season; full 0.12%/yr benefit realized over 5 years (FAO 2020)."

// native_hedgerow_buffers
"time_horizon_seasons": 3,
"time_horizon_note": "Wild bee richness +35% observable after 3 seasons of hedgerow establishment (IPBES 2016)."

// agroforestry_windbreaks
"time_horizon_seasons": 6,
"time_horizon_note": "Wind speed reduction benefits emerge after 2 years; full microclimate effect at 3–5 years (IPCC 2022)."
```

**File:** `backend/recommendation.py` → add to the `rec` dict:
```python
"time_horizon_seasons": item.get("time_horizon_seasons"),
"time_horizon_note": item.get("time_horizon_note", "")
```

---

## F6 — Add DSI Breakdown to Recommendation Output

**File:** `backend/recommendation.py` → `score_and_rank()` rec dict

**Fix:** Add:
```python
"dsi_components": {
    "environmental_fit": round(fit, 2),
    "evidence_strength": round(e_score, 2),
    "biodiversity_gain": round(b_score, 2),
    "soil_gain": round(s_score, 2),
    "feasibility": round(m_score, 2),
    "risk_penalty": round(risk_penalty, 2)
}
```

This makes the "why is this ranked #1?" question answerable directly from the API response.

---

## F7 — Add pH Stressor to Reasoning

**File:** `backend/reasoning.py` → after thermal stress block

**Scientific basis:** Nutrient availability is severely constrained below pH 5.5 (acid) and above pH 8.0 (alkaline).

**Fix:**
```python
# pH Stress (if pH data available)
if t.soil_ph < 5.5:
    s_ph = "HIGH"
    causal_factors.append(CausalFactor(
        stressor="ACID_SOIL_NUTRIENT_LOCKOUT",
        severity="HIGH",
        why=f"Soil pH {t.soil_ph} below 5.5 locks phosphorus and causes aluminum/manganese toxicity.",
        how="Reduces root nutrient uptake, decreases plant diversity, and stunts mycorrhizal associations.",
        what="Lime application (0.5–2 t/ha) to raise pH to 6.0–6.5; apply biochar to buffer acidity."
    ))
elif t.soil_ph > 8.0:
    s_ph = "MODERATE"
    causal_factors.append(CausalFactor(
        stressor="ALKALINE_SOIL_MICRONUTRIENT_DEFICIT",
        severity="MODERATE",
        why=f"Soil pH {t.soil_ph} above 8.0 locks iron, manganese, zinc, and boron.",
        how="Reduces micronutrient availability for plant growth and suppresses soil acidifying bacteria.",
        what="Incorporate sulfur amendments or acidifying organic matter; select alkali-tolerant species."
    ))
else:
    s_ph = "LOW"
stress_levels["ph_stress"] = s_ph
```

---

## F8 — Add GET /api/v1/interventions Endpoint

**File:** `backend/main.py`

**Fix:** Add after the `/analyze` endpoint:
```python
@app.get("/api/v1/interventions")
def list_interventions():
    """Browse the full ecological intervention catalog."""
    interventions = repo.get_all_interventions()
    return {
        "success": True,
        "count": len(interventions),
        "interventions": interventions
    }
```

---

## F9 — Add 4 More Evidence Corpus Chunks

**File:** `data/scientific_corpus.json` — append 4 new entries:

1. **Soil pH and nutrient availability** (FAO Technical Paper) — covers acid soil remediation and lime application effects.
2. **Temperature stress on soil biology** (links to IPCC SRCCL excerpt already in corpus — extract a second page-level chunk for temperature > 35°C soil biology impacts).
3. **Species richness and agroecosystem diversity** (IPBES or IPCC reference on biodiversity metrics in agricultural landscapes).
4. **Deforestation and land degradation** (FAO 2020 State of the World's Forests).

**After adding:** Re-run `.\venv\Scripts\python.exe -m backend.db.init_db` to ingest new chunks into pgvector.

---

## F10 — Dynamic Response Text in /chat

**File:** `backend/main.py` → `handle_chat()` — replace the hardcoded `draft_narrative` template:

**Current (bad):**
```python
draft_narrative = (
    f"Based on your environmental telemetry ({telemetry.soc_percent}% SOC, ...)..."
    f"Scientific Evidence indicates that legume intercropping..."  # ALWAYS the same
)
```

**Fix:** Build narrative dynamically from actual retrieved evidence and top recommendation:
```python
# Dynamic narrative from actual retrieved evidence and top recommendation
top_rec = ranked_recs[0] if ranked_recs else None
top_ev = evidence_chunks[0] if evidence_chunks else None

rec_name = top_rec['name'] if top_rec else "Diversified Agroecological Management"
ev_excerpt = top_ev.get('excerpt', '')[:200] if top_ev else ""
ev_source = f"{top_ev.get('publisher', 'FAO')} ({top_ev.get('year', '')})" if top_ev else ""

draft_narrative = (
    f"**Environmental Assessment:** {assessment.summary_text}\n\n"
    f"**Top Recommendation:** {rec_name} (Darukaa Decision Score: {top_rec['decision_score'] if top_rec else 'N/A'}).\n\n"
    f"**Scientific Basis:** {ev_excerpt} — *{ev_source}*\n\n"
    f"**Key Risk Factors Identified:** {', '.join(assessment.key_factors)}.\n"
    f"**Evidence Confidence:** {val_report.get('confidence_badge', 'MEDIUM')}."
    if top_rec else
    f"Based on your profile: {assessment.summary_text}"
)
```

---

## After All Fixes: Run Tests

```powershell
.\venv\Scripts\python.exe -m pytest backend/tests/test_system.py -v
```

All 21 tests should still pass. If new fields are added to recommendation output, test_14 may need updating.

---

## Compliance Target After Fixes

| Category | Current | Target |
|:---|:---|:---|
| Depth of Reasoning | 7.5/10 | 9.0/10 |
| Scientific Grounding | 8.0/10 | 9.0/10 |
| Knowledge System | 7.0/10 | 8.5/10 |
| Conversational Intelligence | 8.5/10 | 9.0/10 |
| Output Clarity | 7.0/10 | 8.5/10 |
| **Overall** | **76/100** | **~87/100** |
