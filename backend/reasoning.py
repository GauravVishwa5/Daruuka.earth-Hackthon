from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class EnvironmentalTelemetry:
    soc_percent: float
    annual_rainfall_mm: float
    land_use: str
    max_temp_celsius: float = 30.0
    soil_ph: float = 7.0
    species_richness: Optional[str] = None
    pollution_level: Optional[str] = None
    deforestation_pressure: Optional[str] = None
    region: Optional[str] = "semi_arid"
    latitude: Optional[float] = None
    longitude: Optional[float] = None

@dataclass
class CausalFactor:
    stressor: str
    severity: str
    why: str
    how: str
    what: str

@dataclass
class EnvironmentalAssessment:
    stress_levels: Dict[str, str]
    compound_risk: str
    causal_factors: List[Dict[str, str]]
    water_penalty_active: bool
    summary_text: str
    soil_stress: float = 0.0
    water_stress: float = 0.0
    habitat_pressure: float = 0.0
    thermal_stress: float = 0.0
    ph_stress: float = 0.0
    compound_state: str = "BALANCED"
    key_factors: List[str] = field(default_factory=list)
    heuristic_label: str = "Darukaa Compound Stress Heuristic"

class MultiMetricReasoningEngine:
    def evaluate(self, t: EnvironmentalTelemetry) -> EnvironmentalAssessment:
        causal_factors: List[CausalFactor] = []
        stress_levels: Dict[str, str] = {}

        # 1. Soil Organic Matter State (FAO 2017 baseline: mineral soil < 0.5% SOC is critical)
        if t.soc_percent < 0.5:
            s_soil = "CRITICAL"
            causal_factors.append(CausalFactor(
                stressor="CRITICAL_SOC_DEPLETION",
                severity="CRITICAL",
                why=f"Soil Organic Carbon of {t.soc_percent}% breaches the FAO critical structural aggregate threshold (<0.5%).",
                how="Impairs micropore development and biological cementing, reducing soil available water retention by up to 40%.",
                what="Accelerates surface crusting, increases water erosion risk, and leaves soil vulnerable to compaction."
            ))
        elif t.soc_percent < 1.2:
            s_soil = "HIGH"
            causal_factors.append(CausalFactor(
                stressor="MODERATE_SOC_DEFICIT",
                severity="HIGH",
                why=f"Soil Organic Carbon of {t.soc_percent}% is below sustainable regenerative thresholds (1.5 - 2.5%).",
                how="Limits mycorrhizal glomalin production and microbial nitrogen mineralization.",
                what="Requires supplemental external fertilizer inputs and limits root depth penetration."
            ))
        else:
            s_soil = "LOW"
        stress_levels["soil_stress"] = s_soil

        # 2. Hydrological Stress (FAO Aridity & Water Balance)
        if t.annual_rainfall_mm < 400 or (t.annual_rainfall_mm < 550 and t.max_temp_celsius > 32):
            s_water = "HIGH"
            causal_factors.append(CausalFactor(
                stressor="HYDROLOGICAL_DEFICIT",
                severity="HIGH",
                why=f"Low precipitation ({t.annual_rainfall_mm} mm/yr) combined with elevated thermal stress ({t.max_temp_celsius}°C).",
                how="Collides with low carbon sponge capacity, preventing effective rainwater infiltration and causing rapid surface runoff.",
                what="Severely restricts biomass accumulation and creates extreme vulnerability to seasonal droughts."
            ))
        elif t.annual_rainfall_mm < 700:
            s_water = "MODERATE"
            causal_factors.append(CausalFactor(
                stressor="SEASONAL_WATER_LIMITATION",
                severity="MODERATE",
                why=f"Moderate precipitation ({t.annual_rainfall_mm} mm/yr) is sufficient for cereals but requires moisture conservation.",
                how="Early vegetative growth can deplete subsoil moisture before critical anthesis stages.",
                what="Requires moisture-conserving practices and careful cover crop termination timing."
            ))
        else:
            s_water = "LOW"
        stress_levels["water_stress"] = s_water

        # 3. Habitat & Biodiversity Pressure (IPBES 2019 Monoculture Framework)
        if "monoculture" in t.land_use.lower() or "wheat" in t.land_use.lower():
            s_bio = "HIGH"
            causal_factors.append(CausalFactor(
                stressor="MONOCULTURE_FLORAL_DESERT",
                severity="HIGH",
                why=f"Continuous cropping of single genus ({t.land_use}) lacks non-crop flowering plants.",
                how="Depletes native soil microbiome diversity and completely severs wild pollinator foraging corridors.",
                what="Leads to collapse of wild bee richness and predatory pest-control insects."
            ))
        elif t.species_richness == "LOW":
            s_bio = "HIGH"
            causal_factors.append(CausalFactor(
                stressor="DEPLETED_SPECIES_RICHNESS",
                severity="HIGH",
                why="Local field ecological surveys indicate depleted baseline floral and faunal species richness.",
                how="Reduces functional redundancy and impairs natural pest predation networks.",
                what="Leaves agroecosystem susceptible to pest outbreaks and soil functional degradation."
            ))
        elif t.pollution_level == "HIGH":
            s_bio = "HIGH"
            causal_factors.append(CausalFactor(
                stressor="CHEMICAL_POLLUTION_PRESSURE",
                severity="HIGH",
                why="Intensive agrochemical application and pesticide runoff degrade local ecological health.",
                how="Suppresses beneficial soil macrofauna (earthworms, mycorrhizae) and off-target pollinators.",
                what="Impairs biological soil restructuring and increases ecological toxicity."
            ))
        elif t.deforestation_pressure == "HIGH":
            s_bio = "HIGH"
            causal_factors.append(CausalFactor(
                stressor="DEFORESTATION_FRAGMENTATION",
                severity="HIGH",
                why="Surrounding landscape exhibits rapid forest clearing and tree canopy loss.",
                how="Fragments ecological wildlife corridors and increases windward evaporative exposure.",
                what="Increases microclimate extremes and accelerates landscape-scale biodiversity decline."
            ))
        else:
            s_bio = "LOW"
        stress_levels["biodiversity_stress"] = s_bio

        # 4. Thermal Stress (Darukaa Thermal Stress Heuristic - IPCC SRCCL Ch4)
        if t.max_temp_celsius >= 38.0:
            s_thermal = "CRITICAL"
            causal_factors.append(CausalFactor(
                stressor="EXTREME_THERMAL_STRESS",
                severity="CRITICAL",
                why=f"Ambient temperature of {t.max_temp_celsius}°C exceeds critical physiological thresholds (>=38°C).",
                how="Drives extreme vapor pressure deficit (VPD) and accelerates soil respiration while denaturing photosynthetic enzymes.",
                what="Induces rapid soil moisture desiccation and acute heat stress in crops and soil biology."
            ))
        elif t.max_temp_celsius >= 32.0:
            s_thermal = "HIGH"
        else:
            s_thermal = "LOW"
        stress_levels["thermal_stress"] = s_thermal

        # 5. Soil pH Stress (Darukaa Soil-pH Heuristic - FAO SWSR 2015 Ch5)
        if t.soil_ph < 5.5:
            s_ph = "HIGH"
            causal_factors.append(CausalFactor(
                stressor="ACID_SOIL_TOXICITY",
                severity="HIGH",
                why=f"Soil pH of {t.soil_ph} indicates strong acidity (below 5.5 threshold, FAO SWSR 2015).",
                how="Mobilizes soluble aluminum and manganese ions while fixing essential orthophosphates.",
                what="Severely inhibits root elongation and restricts plant uptake of phosphorus and base cations."
            ))
        elif t.soil_ph > 8.0:
            s_ph = "MODERATE"
            causal_factors.append(CausalFactor(
                stressor="ALKALINE_SOIL_STRESS",
                severity="MODERATE",
                why=f"Soil pH of {t.soil_ph} exceeds optimal agronomic range (>8.0).",
                how="Limits bioavailability of micronutrients including iron, zinc, and manganese.",
                what="Causes micronutrient deficiencies and reduces crop vigor."
            ))
        else:
            s_ph = "LOW"
        stress_levels["ph_stress"] = s_ph

        # 6. Deterministic Compound Stress Assessment
        severe_count = sum(1 for s in stress_levels.values() if s in ("CRITICAL", "HIGH"))
        if severe_count >= 3:
            compound_risk = "CRITICAL_COMPOUND_DEGRADATION"
            summary_text = (
                f"CRITICAL COMPOUND COLLAPSE: Severe soil carbon depletion ({t.soc_percent}% SOC) collides with hydrological "
                f"deficit ({t.annual_rainfall_mm} mm/yr) and land pressure ({t.land_use}). Thermal stress ({t.max_temp_celsius}°C) "
                f"and low carbon destroy the soil sponge, making precipitation ineffective through runoff and evaporative loss."
            )
        elif severe_count >= 2:
            compound_risk = "HIGH_COMPOUND_STRESS"
            summary_text = (
                f"HIGH COMPOUND STRESS: Multiple environmental stressors interact to compromise ecosystem resilience. "
                f"Active factors ({', '.join([k.replace('_', ' ') for k, v in stress_levels.items() if v in ('CRITICAL', 'HIGH')])}) "
                f"demand interventions balancing carbon rebuilding with moisture conservation."
            )
        elif severe_count == 1:
            compound_risk = "MODERATE_ECOLOGICAL_VULNERABILITY"
            summary_text = "MODERATE VULNERABILITY: Targeted ecological interventions can readily stabilize current stress drivers."
        else:
            compound_risk = "LOW_STRESS_BALANCED"
            summary_text = "BALANCED AGROECOSYSTEM: Current environmental metrics reflect resilient, healthy baseline conditions."

        # Key auditable factors and numeric heuristic stresses
        soil_stress_val = round(max(0.1, min(1.0, 1.0 - (t.soc_percent / 2.0))), 2)
        water_stress_val = round(max(0.1, min(1.0, 1.0 - (t.annual_rainfall_mm / 1200.0))), 2)
        habitat_pressure_val = 0.75 if ("monoculture" in t.land_use.lower() or "wheat" in t.land_use.lower()) else 0.20
        thermal_stress_val = round(max(0.1, min(1.0, (t.max_temp_celsius - 15.0) / 30.0)), 2) if t.max_temp_celsius >= 32.0 else 0.15
        ph_stress_val = round(min(1.0, max(0.1, (6.5 - t.soil_ph) / 2.0)), 2) if t.soil_ph < 5.5 else (round(min(1.0, max(0.1, (t.soil_ph - 7.5) / 2.5)), 2) if t.soil_ph > 8.0 else 0.10)

        key_factors = []
        if t.soc_percent < 1.0:
            key_factors.append(f"Low soil organic carbon ({t.soc_percent}%)")
        if t.annual_rainfall_mm < 600:
            key_factors.append(f"Low rainfall ({t.annual_rainfall_mm} mm)")
        if habitat_pressure_val >= 0.5:
            key_factors.append(f"Monoculture cropping pressure ({t.land_use})")
        if t.max_temp_celsius >= 32.0:
            key_factors.append(f"Elevated temperature ({t.max_temp_celsius}°C)")
        if t.soil_ph < 5.5:
            key_factors.append(f"Soil acidity stress (pH {t.soil_ph})")
        elif t.soil_ph > 8.0:
            key_factors.append(f"Soil alkalinity stress (pH {t.soil_ph})")
        if t.species_richness == "LOW":
            key_factors.append("Depleted species richness")
        if t.pollution_level == "HIGH":
            key_factors.append("Chemical/pesticide runoff pressure")
        if t.deforestation_pressure == "HIGH":
            key_factors.append("Deforestation/habitat clearance pressure")

        state_mapping = {
            "CRITICAL_COMPOUND_DEGRADATION": "CRITICAL",
            "HIGH_COMPOUND_STRESS": "HIGH",
            "MODERATE_ECOLOGICAL_VULNERABILITY": "MODERATE",
            "LOW_STRESS_BALANCED": "BALANCED"
        }

        return EnvironmentalAssessment(
            stress_levels=stress_levels,
            compound_risk=compound_risk,
            causal_factors=[cf.__dict__ for cf in causal_factors],
            water_penalty_active=(s_water in ("HIGH", "CRITICAL")),
            summary_text=summary_text,
            soil_stress=soil_stress_val,
            water_stress=water_stress_val,
            habitat_pressure=habitat_pressure_val,
            thermal_stress=thermal_stress_val,
            ph_stress=ph_stress_val,
            compound_state=state_mapping.get(compound_risk, "MODERATE"),
            key_factors=key_factors,
            heuristic_label="Darukaa Compound Stress Heuristic"
        )
