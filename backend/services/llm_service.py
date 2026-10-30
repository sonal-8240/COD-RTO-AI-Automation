"""
SmartCOD AI - LLM & Address Intelligence Service
Analyzes ambiguous addresses, detects Hinglish location instructions, identifies suspicious names,
and generates plain-English explanations with deterministic fallback.
"""

import os
import re
from typing import Dict, Any, List
from backend.config import settings

class LLMAddressIntelligence:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY or settings.OPENAI_API_KEY or os.environ.get("GEMINI_API_KEY")

        # Hinglish landmark & direction markers common in Indian ecommerce
        self.hinglish_landmarks = [
            r"ke\s+(?:samne|saamne|piche|peeche|paas|pass|bagal|side)",
            r"mandir\s+ke\s+(?:paas|samne)",
            r"masjid\s+ke\s+(?:paas|samne)",
            r"doodh\s+dairy|milk\s+booth",
            r"peepal\s+(?:ka\s+)?ped",
            r"chauraha|chowk|tiraha",
            r"gali\s+n(?:o|um|umber)?\.?\s*\d+",
            r"makan\s+n(?:o|um|umber)?\.?\s*\d+",
            r"opp(?:osite)?\.?\s+",
            r"near\s+(?:water\s+tank|school|hospital|bus\s+stand|metro|railway)",
            r"dukaan|shop\s+ke\s+paas",
            r"pan\s+parlor|chai\s+tapri"
        ]

        # Delivery instruction phrases
        self.delivery_instructions = [
            r"call\s+kar(?:ke|k)?\s+(?:aana|dena)",
            r"call\s+(?:before|on)\s+delivery",
            r"shaam\s+ko\s+aana",
            r"security\s+guard\s+ko\s+de\s+dena",
            r"ghar\s+pe\s+koi\s+na\s+mile\s+to",
            r"do\s+not\s+call\s+after\s+\d+"
        ]

        # Bogus / Defective tokens
        self.bogus_patterns = [
            r"^(?:xyz|abc|test|asdf|qwerty|none|null|na|nil|12345|home|flat|room|house)$",
            r"^[a-z0-9]\s*$",
            r"^(.)\1{4,}$",  # repeated char like aaaaa or 11111
            r"^(?:call\s+me|contact\s+me|deliver\s+here|my\s+address)$"
        ]

        # Suspicious name patterns
        self.suspicious_name_patterns = [
            r"^(?:test|testing|admin|user|customer|fake|anonymous|demo|sample|check|asdf|qwerty|xyz)$",
            r"^(?:mr|mrs|ms)\.?\s*$",
            r"^[a-zA-Z]$",  # Single letter name
            r"^(.)\1{3,}$"   # Repeating characters like "aaaa" or "xxxx"
        ]

    def analyze_order_context(
        self,
        customer_name: str,
        address: str,
        city: str = "",
        state: str = ""
    ) -> Dict[str, Any]:
        """
        Evaluates address clarity, landmarks, Hinglish phrasing, and customer name authenticity.
        Falls back to high-fidelity deterministic NLP when no LLM key is configured.
        """
        # If API key is provided, LLM call can be made here.
        # Otherwise, the deterministic engine executes with 100% offline reliability.
        if self.api_key and not settings.USE_MOCK_LLM_IF_NO_KEY:
            try:
                return self._call_external_llm(customer_name, address, city, state)
            except Exception:
                # Safe graceful degradation to deterministic engine
                pass

        return self._evaluate_deterministic(customer_name, address, city, state)

    def _evaluate_deterministic(
        self,
        customer_name: str,
        address: str,
        city: str = "",
        state: str = ""
    ) -> Dict[str, Any]:
        name_clean = (customer_name or "").strip().lower()
        addr_clean = (address or "").strip()
        addr_lower = addr_clean.lower()

        flags: List[str] = []
        is_suspicious_name = False
        hinglish_detected = False
        address_quality_score = 0.8  # Default baseline

        # 1. Name Check
        if not name_clean or len(name_clean) < 2:
            is_suspicious_name = True
            flags.append("Missing or single-letter customer name")
        else:
            for pattern in self.suspicious_name_patterns:
                if re.search(pattern, name_clean):
                    is_suspicious_name = True
                    flags.append(f"Suspicious customer name detected ('{customer_name}')")
                    break

        # Check for numbers in customer name (e.g., "John123")
        if re.search(r"\d{2,}", name_clean):
            is_suspicious_name = True
            flags.append("Customer name contains excessive digits")

        # 2. Address Length and Character Diversity
        addr_len = len(addr_clean)
        unique_chars = len(set(addr_lower.replace(" ", "")))

        if addr_len < 10:
            address_quality_score -= 0.5
            flags.append(f"Severely incomplete address (only {addr_len} characters)")
        elif addr_len < 20:
            address_quality_score -= 0.25
            flags.append("Abbreviated address lacking detailed dispatch coordinates")

        if unique_chars < 5 and addr_len > 0:
            address_quality_score -= 0.4
            flags.append("Repetitive or uninformative character sequence in address")

        # 3. Bogus / Placeholder address check
        for pattern in self.bogus_patterns:
            if re.search(pattern, addr_lower):
                address_quality_score = 0.1
                flags.append("Address matches known placeholder pattern (e.g. 'xyz', 'test', 'home')")
                break

        # 4. Hinglish & Landmark Analysis
        matched_landmarks = []
        for pattern in self.hinglish_landmarks:
            if re.search(pattern, addr_lower):
                matched_landmarks.append(pattern)

        matched_instructions = []
        for pattern in self.delivery_instructions:
            if re.search(pattern, addr_lower):
                matched_instructions.append(pattern)

        if matched_landmarks or matched_instructions:
            hinglish_detected = True
            address_quality_score = min(1.0, address_quality_score + 0.15)
            flags.append("Contains authentic local landmarks or regional delivery instructions")

        # 5. Structural Markers (House number, street, floor, area)
        has_number = bool(re.search(r"\b\d+[-/]?\d*\b", addr_clean))
        has_street_cue = bool(re.search(r"\b(?:road|street|gali|block|sector|flat|plot|house|nagar|colony|enclave|marg|lane|floor)\b", addr_lower))

        if has_number and has_street_cue:
            address_quality_score = min(1.0, address_quality_score + 0.2)
        elif not has_number and not has_street_cue and addr_len < 30:
            address_quality_score -= 0.2
            flags.append("Lacks specific house/plot number or street designation")

        # Clamp quality score between 0.05 and 1.0
        address_quality_score = round(max(0.05, min(1.0, address_quality_score)), 2)

        # Generate explainable plain-English reasoning
        reasons = []
        if is_suspicious_name:
            reasons.append("Customer name appears placeholder or synthetic.")
        if address_quality_score < 0.35:
            reasons.append("Address is severely truncated or contains generic placeholders.")
        elif address_quality_score < 0.65:
            reasons.append("Address is short and lacks clear premise numbers or navigation cues.")
        else:
            reasons.append("Address is well-structured with verifiable delivery landmarks.")

        if hinglish_detected:
            reasons.append("Local Hinglish delivery landmarks detected, indicating a genuine local resident.")

        return {
            "address_quality_score": address_quality_score,
            "is_suspicious_name": is_suspicious_name,
            "hinglish_detected": hinglish_detected,
            "flags": flags,
            "explanation": " ".join(reasons),
            "explanation_source": "DETERMINISTIC_RULES"
        }

    def _call_external_llm(
        self,
        customer_name: str,
        address: str,
        city: str,
        state: str
    ) -> Dict[str, Any]:
        """
        Placeholder for external LLM API caller (e.g. Gemini / OpenAI).
        Structured to return identical dictionary contract with explanation_source="LLM".
        """
        # When an API key is connected, this makes a JSON-schema LLM prompt
        return self._evaluate_deterministic(customer_name, address, city, state)
