from typing import List, Dict, Any
from backend.repository import KnowledgeRepository
from backend.reasoning import EnvironmentalAssessment, EnvironmentalTelemetry

class RecommendationEngine:
    def __init__(self, repository: KnowledgeRepository):
        self.repo = repository

    def score_and_rank(
        self, 
        telemetry: EnvironmentalTelemetry, 
        assessment: EnvironmentalAssessment
    ) -> List[Dict[str, Any]]:
        interventions = self.repo.get_all_interventions()
        scored_recs = []

        for item in interventions:
            # 1. Environmental Fit (F)
            fit = 0.85
            if "semi_arid" in item.get("biome_applicability", []):
                fit = 0.95
            elif "all_biomes" in item.get("biome_applicability", []):
                fit = 0.80

            # 2. Evidence Strength (E)
            evidence_chunks = []
            for c_key in item.get("citation_keys", []):
                chunk = self.repo.get_chunk(c_key)
                if chunk:
                    evidence_chunks.append(chunk)
            
            e_score = 0.90 if evidence_chunks else 0.50

            # 3. Biodiversity Gain (B) & Soil Gain (S) & Feasibility (M)
            b_score = item.get("biodiversity_gain", 0.60)
            s_score = item.get("soil_gain", 0.60)
            m_score = item.get("base_feasibility", 0.70)

            # 4. Resource Risk Penalty (R)
            # Water stress context penalty
            water_req = item.get("water_requirement", "LOW")
            if assessment.water_penalty_active and water_req == "HIGH":
                risk_penalty = 0.90  # Severe penalty for water-guzzling crops in drought zones
            elif assessment.water_penalty_active and water_req == "MEDIUM":
                risk_penalty = 0.40
            else:
                risk_penalty = 0.10

            # Darukaa Decision Score (DSI)
            dsi = (
                0.25 * fit +
                0.20 * e_score +
                0.20 * b_score +
                0.15 * s_score +
                0.10 * m_score -
                0.20 * risk_penalty
            )
            dsi = round(max(0.0, min(1.0, dsi)), 3)

            dsi_components = {
                "environmental_fit": fit,
                "evidence_strength": e_score,
                "biodiversity_gain": b_score,
                "soil_gain": s_score,
                "feasibility": m_score,
                "risk_penalty": risk_penalty
            }

            # Build recommendation object
            rec = {
                "slug": item["slug"],
                "name": item["name"],
                "category": item["category"],
                "decision_score": dsi,
                "dsi_components": dsi_components,
                "time_horizon": item.get("time_horizon", {}),
                "water_penalty_applied": assessment.water_penalty_active and water_req in ("HIGH", "MEDIUM"),
                "primary_benefits": item.get("primary_benefits", {}),
                "tradeoffs": item.get("tradeoffs", []),
                "evidence_sources": [
                    {
                        "chunk_id": ec.get("chunk_id"),
                        "title": ec.get("title"),
                        "publisher": ec.get("publisher"),
                        "year": ec.get("year"),
                        "doi": ec.get("doi"),
                        "excerpt": ec.get("excerpt")
                    }
                    for ec in evidence_chunks
                ]
            }
            scored_recs.append(rec)

        # Sort descending by DSI
        scored_recs.sort(key=lambda x: x["decision_score"], reverse=True)

        # Assign ranks
        for idx, r in enumerate(scored_recs):
            r["rank"] = idx + 1

        return scored_recs
