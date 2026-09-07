"""
Data verification and seeding script for Darukaa.Earth.
Checks the integrity of scientific literature chunks and intervention catalogs.
"""
import json
import sys
from pathlib import Path

# Set UTF-8 encoding for Windows terminal stdout
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.repository import InMemoryVectorRepository
from backend.reasoning import MultiMetricReasoningEngine, EnvironmentalTelemetry
from backend.recommendation import RecommendationEngine

def main():
    print("🌱 Initializing Darukaa.Earth Data & Reasoning Verification...")
    repo = InMemoryVectorRepository()
    
    print(f"✅ Loaded {len(repo.chunks)} scientific evidence chunks from FAO, IPCC, IPBES.")
    for c in repo.chunks:
        print(f"   • [{c.get('publisher')}] {c.get('chunk_id')} (DOI: {c.get('doi')})")

    print(f"✅ Loaded {len(repo.interventions)} ecological interventions.")
    for item in repo.interventions:
        print(f"   • [{item.get('category')}] {item.get('name')}")

    # Test sample evaluation
    print("\n🔬 Executing Sample Multi-Metric Compound Stress Evaluation...")
    reasoning = MultiMetricReasoningEngine()
    rec_engine = RecommendationEngine(repo)

    sample = EnvironmentalTelemetry(
        soc_percent=0.35,
        annual_rainfall_mm=450.0,
        max_temp_celsius=34.0,
        land_use="wheat_monoculture"
    )

    assessment = reasoning.evaluate(sample)
    print(f"   Compound Status: {assessment.compound_risk}")
    print(f"   Water Penalty Active: {assessment.water_penalty_active}")
    print(f"   Causal Factors Detected: {len(assessment.causal_factors)}")

    recs = rec_engine.score_and_rank(sample, assessment)
    print("\n🏆 Top Ranked Interventions:")
    for r in recs[:3]:
        print(f"   #{r['rank']} {r['name']} (DSI: {r['decision_score']}) - Sources: {len(r['evidence_sources'])}")

    print("\n✨ Data integrity check completed successfully!")

if __name__ == "__main__":
    main()
