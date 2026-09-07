import re
from typing import Dict, Any, List, Optional, Tuple

REQUIRED_SLOTS = ["soc_percent", "annual_rainfall_mm", "land_use"]

class ConversationManager:
    @staticmethod
    def extract_slots(text: str) -> Dict[str, Any]:
        """Extracts environmental telemetry slots from freeform text."""
        extracted: Dict[str, Any] = {}

        # 1. Soil Organic Carbon (SOC)
        # Matches: 'soc 0.35%', 'soc is 0.35', 'carbon is 0.35%', '0.35% soc'
        soc_match = re.search(r'(?:soc|carbon|som)[\s:=is]+(\d+\.?\d*)\s*%?', text, re.IGNORECASE)
        if not soc_match:
            soc_match = re.search(r'(\d+\.?\d*)\s*%\s*(?:soc|carbon)', text, re.IGNORECASE)
        if soc_match:
            try:
                val = float(soc_match.group(1))
                if 0.0 <= val <= 20.0:
                    extracted["soc_percent"] = val
            except ValueError:
                pass

        # 2. Annual Rainfall
        # Matches: 'rainfall 450mm', 'rain is 450 mm', '450 mm rain', '450mm'
        rain_match = re.search(r'(?:rainfall|rain|precip)[\s:=is]+(\d+\.?\d*)\s*(?:mm)?', text, re.IGNORECASE)
        if not rain_match:
            rain_match = re.search(r'(\d+\.?\d*)\s*mm', text, re.IGNORECASE)
        if rain_match:
            try:
                val = float(rain_match.group(1))
                if 0.0 <= val <= 5000.0:
                    extracted["annual_rainfall_mm"] = val
            except ValueError:
                pass

        # 3. Maximum Temperature
        temp_match = re.search(r'(?:temp|temperature)[\s:=is]+(\d+\.?\d*)\s*(?:°?c)?', text, re.IGNORECASE)
        if temp_match:
            try:
                val = float(temp_match.group(1))
                if -20.0 <= val <= 60.0:
                    extracted["max_temp_celsius"] = val
            except ValueError:
                pass

        # 4. Soil pH
        ph_match = re.search(r'(?:soil\s*)?ph[\s:=is]+(\d+\.?\d*)', text, re.IGNORECASE)
        if ph_match:
            try:
                val = float(ph_match.group(1))
                if 2.0 <= val <= 12.0:
                    extracted["soil_ph"] = val
            except ValueError:
                pass

        # 5. Land Use / Crop (Prioritized longest-match first)
        text_lower = text.lower()
        land_use_patterns = [
            ("wheat monoculture", "wheat_monoculture"),
            ("wheat mono", "wheat_monoculture"),
            ("corn monoculture", "corn_monoculture"),
            ("maize monoculture", "corn_monoculture"),
            ("rice monoculture", "rice_monoculture"),
            ("soybean monoculture", "soybean_monoculture"),
            ("soy monoculture", "soybean_monoculture"),
            ("crop monoculture", "crop_monoculture"),
            ("monoculture", "crop_monoculture"),
            ("wheat crop", "wheat_crop"),
            ("wheat", "wheat_crop"),
            ("corn crop", "corn_crop"),
            ("corn", "corn_crop"),
            ("maize", "corn_crop"),
            ("rice paddy", "rice_paddy"),
            ("paddy fields", "rice_paddy"),
            ("paddy field", "rice_paddy"),
            ("paddy", "rice_paddy"),
            ("rice", "rice_paddy"),
            ("soybean crop", "soybean_crop"),
            ("soybean", "soybean_crop"),
            ("soy", "soybean_crop"),
            ("cotton crop", "cotton_crop"),
            ("cotton", "cotton_crop"),
            ("barley crop", "barley_crop"),
            ("barley", "barley_crop"),
            ("sorghum crop", "sorghum_crop"),
            ("sorghum", "sorghum_crop"),
            ("bare fallow", "bare_fallow"),
            ("fallow land", "bare_fallow"),
            ("bare land", "bare_fallow"),
            ("fallow", "bare_fallow"),
            ("pasture", "pasture"),
            ("grassland", "pasture"),
            ("agroforestry", "agroforestry"),
            ("orchard", "orchard"),
            ("vineyard", "orchard"),
            ("managed forest", "managed_forest"),
            ("forest", "managed_forest"),
            ("mixed cropping", "mixed_cropping"),
            ("mixed crops", "mixed_cropping"),
            ("intercropping", "intercropped_farmland"),
            ("intercropped", "intercropped_farmland"),
        ]
        for phrase, lu_val in land_use_patterns:
            if phrase in text_lower:
                extracted["land_use"] = lu_val
                break

        # 6. Optional: Species Richness
        if re.search(r'\b(?:low|poor|declining|depleted)\s+species\s+richness\b|\bspecies\s+richness\s+(?:is\s+)?(?:low|poor|depleted|declining)\b', text_lower):
            extracted["species_richness"] = "LOW"
        elif re.search(r'\b(?:high|rich|abundant)\s+species\s+richness\b|\bspecies\s+richness\s+(?:is\s+)?(?:high|rich|abundant)\b', text_lower):
            extracted["species_richness"] = "HIGH"

        # 7. Optional: Pollution / Deforestation Indicators
        if re.search(r'\b(?:pesticides?|chemical\s+runoff|pesticide\s+runoff|heavy\s+pesticides?|toxic\s+runoff|high\s+pollution)\b', text_lower):
            extracted["pollution_level"] = "HIGH"
        if re.search(r'\b(?:deforestation|forest\s+clearing|cleared\s+forest|tree\s+clearing)\b', text_lower):
            extracted["deforestation_pressure"] = "HIGH"

        return extracted

    @staticmethod
    def evaluate_turn(
        user_message: str, 
        current_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Updates profile with newly extracted slots, preserves previous context,
        and determines if clarification is needed.
        """
        new_slots = ConversationManager.extract_slots(user_message)
        
        # Merge new slots into current profile (preserves prior fields)
        accumulated_profile = {**current_profile, **new_slots}

        # Check required slots
        missing = [s for s in REQUIRED_SLOTS if accumulated_profile.get(s) is None]

        if missing:
            items = []
            if "soc_percent" in missing:
                items.append("Soil Organic Carbon (SOC %)")
            if "annual_rainfall_mm" in missing:
                items.append("Average annual rainfall (mm)")
            if "land_use" in missing:
                items.append("Current crop or land use type")

            prompt = (
                "To evaluate soil, water, and biodiversity degradation accurately, "
                f"please provide your: {', '.join(items)}."
            )

            return {
                "status": "CLARIFICATION_REQUIRED",
                "clarification_prompt": prompt,
                "missing_fields": missing,
                "profile": accumulated_profile
            }

        # Profile is complete
        return {
            "status": "READY_FOR_REASONING",
            "profile": accumulated_profile
        }
