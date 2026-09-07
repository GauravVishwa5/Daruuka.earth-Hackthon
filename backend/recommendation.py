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

        # Determine actual biophysical biome from precipitation
        rainfall = telemetry.annual_rainfall_mm or 500.0
        if rainfall < 500:
            target_biome = "semi_arid"
        elif rainfall >= 700:
            target_biome = "temperate_humid"
        else:
            target_biome = "temperate_steppe"

        for item in interventions:
            biomes = item.get("biome_applicability", [])

            # 1. Environmental Fit (F) based on actual precipitation & biome
            if target_biome in biomes:
                fit = 0.95
            elif "all_biomes" in biomes:
                fit = 0.88
            elif "semi_arid" in biomes and target_biome == "temperate_steppe":
                fit = 0.82
            elif target_biome == "temperate_humid" and "semi_arid" in biomes:
                fit = 0.65  # Suboptimal: drought-focused interventions in high-moisture zones
            else:
                fit = 0.55

            # 2. Evidence Strength (E)
            evidence_chunks = []
            for c_key in item.get("citation_keys", []):
                chunk = self.repo.get_chunk(c_key)
                if chunk:
                    evidence_chunks.append(chunk)
            
            e_score = 0.90 if evidence_chunks else 0.50

            # 3. Biodiversity Gain (B), Soil Gain (S), Feasibility (M)
            b_score = item.get("biodiversity_gain", 0.60)
            s_score = item.get("soil_gain", 0.60)
            m_score = item.get("base_feasibility", 0.70)

            # --- Dynamically adjust for diagnosed stress constraints ---
            # Critical SOC crisis: prioritize high soil carbon builders (Biochar, Conservation Tillage)
            if assessment.soil_stress == "CRITICAL" and s_score >= 0.80:
                s_score = min(1.0, s_score + 0.10)

            # Acid stress (pH < 5.5): Biochar / compost offers vital CEC and Al neutralization (FAO SWSR 2015)
            if telemetry.soil_ph and telemetry.soil_ph < 5.5 and item.get("category") == "soil_enhancement":
                s_score = min(1.0, s_score + 0.08)

            # Thermal stress (>= 35C): Canopy & soil armor shield evaporative loss
            if telemetry.max_temp_celsius and telemetry.max_temp_celsius >= 35.0:
                if item.get("category") in ("soil_and_water_conservation", "agroforestry"):
                    fit = min(1.0, fit + 0.05)

            # Existing agroforestry: farm already has tree canopy; prioritize perimeter habitat or soil care
            if "agroforestry" in telemetry.land_use.lower() and item.get("category") == "agroforestry":
                fit = max(0.65, fit - 0.15)

            # 4. Resource Risk Penalty (R)
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
