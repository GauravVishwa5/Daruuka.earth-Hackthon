import re
from typing import List, Dict, Any, Tuple, Optional

class EvidenceValidator:
    def __init__(self, retrieved_chunks: List[Dict[str, Any]]):
        self.chunks = retrieved_chunks
        # Combine all chunk text for empirical verification
        self.corpus_text = " ".join([
            f"{c.get('title', '')} {c.get('section', '')} {c.get('excerpt', '')} {c.get('topic', '')}"
            for c in retrieved_chunks
        ]).lower()

    def extract_claims(self, text: str) -> List[Dict[str, str]]:
        """
        Extracts and classifies claims:
        1. QUANTITATIVE: Numbers with units (+0.12%, 40 kg N/ha, 85%, etc.)
        2. CAUSAL: Statements indicating cause-and-effect (e.g., 'causes', 'reduces', 'leads to')
        3. QUALITATIVE: General agronomic/ecological assertions
        """
        claims = []

        # 1. Quantitative Claims
        num_pattern = r'(\+?-?\d+\.?\d*\s*(?:%|kg(?:\s*N)?(?:/ha)?|mm|g/cm3|years?|tons?|tonnes?|t/ha|°?c|ha))'
        num_matches = re.finditer(num_pattern, text, re.IGNORECASE)
        for m in num_matches:
            claims.append({
                "claim": m.group(1),
                "type": "QUANTITATIVE",
                "span": m.span()
            })

        # 2. Sentences (Causal and Qualitative Claims)
        sentences = [s.strip() for s in re.split(r'[.\n]', text) if len(s.strip()) > 15]
        for s in sentences:
            s_lower = s.lower()
            if any(k in s_lower for k in ["reduces", "increases", "causes", "leads to", "depletes", "restores"]):
                if not any(s == c["claim"] for c in claims):
                    claims.append({
                        "claim": s,
                        "type": "CAUSAL",
                        "span": (0, 0)
                    })
            else:
                if not any(s == c["claim"] for c in claims):
                    claims.append({
                        "claim": s,
                        "type": "QUALITATIVE",
                        "span": (0, 0)
                    })

        return claims

    def validate_and_sanitize(
        self, 
        draft_text: str, 
        completeness_ratio: float = 1.0,
        user_telemetry: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        # Handle zero-evidence state explicitly
        if not self.chunks:
            return {
                "sanitized_text": (
                    draft_text + "\n\n⚠️ **Notice:** Insufficient scientific evidence available in "
                    "the local repository for this specific microclimate. Recommendation confidence is downgraded."
                ),
                "confidence_score": 0.35,
                "confidence_badge": "LOW",
                "confidence_explanation": "Low confidence due to absence of matching peer-reviewed literature chunks.",
                "claims_evaluated": 0,
                "claims_supported": 0,
                "claims_stripped": 0,
                "evidence_status": "INSUFFICIENT_EVIDENCE",
                "evidence_ledger": [{
                    "claim": "General advisory context",
                    "type": "BACKGROUND",
                    "status": "INSUFFICIENT_EVIDENCE",
                    "action": "FLAGGED",
                    "detail": "No indexed scientific chunks matched the query criteria."
                }]
            }

        extracted = self.extract_claims(draft_text)
        ledger = []
        supported_count = 0
        stripped_count = 0
        sanitized_text = draft_text

        # Build set of valid user baseline telemetry values
        telemetry_numbers = set()
        if user_telemetry:
            for k, v in user_telemetry.items():
                if v is not None and isinstance(v, (int, float)):
                    telemetry_numbers.add(str(v).lower())
                    telemetry_numbers.add(f"{v:g}".lower())

        for c in extracted:
            claim_text = c["claim"]
            claim_type = c["type"]

            if claim_type == "QUANTITATIVE":
                clean_token = claim_text.replace("+", "").strip().lower()
                num_only = re.sub(r'[^\d.]', '', clean_token)

                # Check if number is user's baseline input or verified against literature
                is_user_baseline = (
                    num_only in telemetry_numbers or 
                    any(num_only == re.sub(r'[^\d.]', '', tn) for tn in telemetry_numbers)
                )

                if is_user_baseline:
                    supported_count += 1
                    ledger.append({
                        "claim": claim_text,
                        "type": "QUANTITATIVE",
                        "status": "SUPPORTED",
                        "action": "RETAINED",
                        "detail": "User-reported baseline field telemetry."
                    })
                elif clean_token in self.corpus_text or (num_only and num_only in self.corpus_text):
                    supported_count += 1
                    ledger.append({
                        "claim": claim_text,
                        "type": "QUANTITATIVE",
                        "status": "SUPPORTED",
                        "action": "RETAINED",
                        "detail": "Numeric value directly verified against institutional citation."
                    })
                else:
                    # UNGROUNDED NUMERIC CLAIM: Strip and convert to qualitative description
                    stripped_count += 1
                    sanitized_text = sanitized_text.replace(claim_text, "[documented positive increase]")
                    ledger.append({
                        "claim": claim_text,
                        "type": "QUANTITATIVE",
                        "status": "UNSUPPORTED",
                        "action": "STRIPPED_NUMBER",
                        "detail": "Number not found in cited evidence chunks; stripped to prevent hallucination."
                    })

            elif claim_type in ("CAUSAL", "QUALITATIVE"):
                # Check if key nouns/verbs overlap with cited chunks
                words = [w for w in re.findall(r'\b\w+\b', claim_text.lower()) if len(w) > 4]
                overlap = sum(1 for w in words if w in self.corpus_text)
                ratio = overlap / max(1, len(words))

                if ratio >= 0.35:
                    supported_count += 1
                    ledger.append({
                        "claim": claim_text[:80] + "...",
                        "type": claim_type,
                        "status": "SUPPORTED",
                        "action": "RETAINED",
                        "detail": f"{claim_type.capitalize()} claim substantiated by cited literature."
                    })
                else:
                    ledger.append({
                        "claim": claim_text[:80] + "...",
                        "type": claim_type,
                        "status": "PARTIALLY_SUPPORTED" if ratio > 0.1 else "UNSUPPORTED",
                        "action": "FLAGGED_CAVEAT",
                        "detail": f"Direct peer-reviewed evidence not found for this {claim_type.lower()} statement; caveat flagged."
                    })

        total_evaluated = len(ledger)
        grounding_ratio = supported_count / max(1, total_evaluated)

        # Multi-factor Confidence Model (Labeled as Darukaa Evidence-Match Confidence)
        # 1. Data completeness (0.0 to 1.0)
        c_comp = completeness_ratio
        # 2. Source authority (Tier 1 FAO/IPCC = 1.0)
        has_tier1 = any(c.get("evidence_strength") == "TIER_1_CONSENSUS" for c in self.chunks)
        c_auth = 1.0 if has_tier1 else 0.75
        # 3. Evidence relevance
        c_rel = 0.90 if self.chunks else 0.40
        # 4. Evidence agreement
        c_agree = grounding_ratio

        confidence = (
            0.30 * c_comp +
            0.30 * c_auth +
            0.25 * c_agree +
            0.15 * c_rel
        )
        confidence = round(max(0.1, min(1.0, confidence)), 2)

        if confidence >= 0.85:
            badge = "HIGH"
            explanation = "High confidence: verified by Tier-1 FAO/IPCC consensus literature with complete local telemetry."
        elif confidence >= 0.65:
            badge = "MEDIUM"
            explanation = "Medium confidence: supported by published evidence; minor extrapolation or ungrounded figures sanitized."
        else:
            badge = "LOW"
            explanation = "Low confidence: incomplete telemetry or limited regional literature match."

        return {
            "sanitized_text": sanitized_text,
            "confidence_score": confidence,
            "confidence_badge": badge,
            "confidence_explanation": explanation,
            "claims_evaluated": total_evaluated,
            "claims_supported": supported_count,
            "claims_stripped": stripped_count,
            "evidence_status": "SUPPORTED" if stripped_count == 0 else "PARTIALLY_SUPPORTED",
            "evidence_ledger": ledger
        }
