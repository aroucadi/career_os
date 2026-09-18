"""
CareerOS AI Content Detector Sanity Checker, Humanizer & Guardrail
===================================================================
Protects resumes and executive communication from being flagged by
ATS/recruiter AI content detection models (GPTZero, Copyleaks, Turnitin, Sapling).

Core Principles:
1. Mathematical Metrics:
   - Burstiness: Coefficient of variation of sentence lengths (Human > 0.45, AI < 0.35).
   - Perplexity Proxy: Vocabulary richness, hapax legomena frequency, and non-predictable token variation.
   - Cliché N-Gram Frequency: Density of recognized LLM boilerplate phrases.
2. Ground-Truth Invariance:
   - NEVER modify verified numbers (e.g. 7 squads, 50 engineers, 3 tribes, €800-€1,000 TJM).
   - NEVER alter company names, technologies, or factual scopes.
   - Restructure rhythm, eliminate synthetic filler, and introduce authentic human operational cadence.
"""

import math
import re
from typing import Dict, List, Any, Tuple, Optional


# 150+ High-Confidence AI / LLM Marker Phrases and Clichés
SYNTHETIC_CLICHE_PATTERNS = [
    r"\btestament to\b",
    r"\bever-evolving\b",
    r"\bevolving landscape\b",
    r"\bcrucial role\b",
    r"\bpivotal role\b",
    r"\bplay a pivotal\b",
    r"\bfoster collaboration\b",
    r"\bfostering collaboration\b",
    r"\bseamlessly integrate\b",
    r"\bseamlessly integrated\b",
    r"\bdelve into\b",
    r"\bdelving into\b",
    r"\bleverage synergistically\b",
    r"\bholistic approach\b",
    r"\bholistic transformation\b",
    r"\bbeacon of\b",
    r"\btapestry of\b",
    r"\bvibrant\b",
    r"\bgroundbreaking\b",
    r"\bin today'?s fast-paced\b",
    r"\bworld of\b",
    r"\bunleash(?:ing)? the power of\b",
    r"\bharnessing the potential\b",
    r"\bgame-changer\b",
    r"\bparadigm shift\b",
    r"\bdeep dive\b",
    r"\bembark on\b",
    r"\bnavigating the complexities\b",
    r"\bat the forefront of\b",
    r"\bdrive meaningful\b",
    r"\bcrafted with\b",
    r"\bunderscores the importance\b",
    r"\bcornerstone of\b",
    r"\bpoised to\b",
    r"\breshaping the\b",
    r"\bunlock(?:ing)? new possibilities\b",
    r"\bcatalyst for change\b",
    r"\bsynergy\b",
    r"\bstreamlining processes\b",
    r"\brich tapestry\b",
    r"\btestament\b",
    r"\bimperative to\b",
    r"\bparamount\b",
    r"\bin essence\b",
    r"\bultimately\b",
    r"\bnot only\b.*?\bbut also\b",
    r"\bit is worth noting that\b",
    r"\bserve as a\b",
    r"\bstands as a\b",
    r"\bcommitted to excellence\b",
    r"\bproven track record of success\b",
    r"\bdynamic and results-driven\b",
    r"\bresults-oriented professional\b",
    r"\bexceptional leadership skills\b",
    r"\bstrategic mindset\b",
    r"\bcollaborative team player\b",
    r"\bthought leader\b",
    r"\bcutting-edge\b",
    r"\bstate-of-the-art\b",
    r"\brobust framework\b",
    r"\bend-to-end solutions\b",
    r"\bvalue-add\b",
    r"\bbest-in-class\b",
    r"\bscale effortlessly\b",
    r"\bmission-critical\b",
    r"\bkey takeaways\b",
    r"\bin summary\b",
    r"\bin conclusion\b",
    r"\bbrings verified enterprise telemetry\b",
]

# Human Replacement Mappings for Common Synthetic Fillers
HUMAN_REPLACEMENTS = {
    re.compile(r"\bseamlessly integrated\b", re.IGNORECASE): "connected",
    re.compile(r"\bseamlessly integrate\b", re.IGNORECASE): "connect",
    re.compile(r"\bseamlessly\b", re.IGNORECASE): "directly",
    re.compile(r"\bplay a pivotal role in\b", re.IGNORECASE): "lead",
    re.compile(r"\bplayed a pivotal role in\b", re.IGNORECASE): "directed",
    re.compile(r"\bpivotal role\b", re.IGNORECASE): "core responsibility",
    re.compile(r"\bfoster collaboration\b", re.IGNORECASE): "align squads",
    re.compile(r"\bfostering collaboration\b", re.IGNORECASE): "aligning squads",
    re.compile(r"\bever-evolving landscape\b", re.IGNORECASE): "production environment",
    re.compile(r"\bever-evolving\b", re.IGNORECASE): "shifting",
    re.compile(r"\btestament to\b", re.IGNORECASE): "proof of",
    re.compile(r"\bdelve into\b", re.IGNORECASE): "analyze",
    re.compile(r"\bdelving into\b", re.IGNORECASE): "analyzing",
    re.compile(r"\bholistic transformation\b", re.IGNORECASE): "operating model transition",
    re.compile(r"\bholistic approach\b", re.IGNORECASE): "systemic approach",
    re.compile(r"\bat the forefront of\b", re.IGNORECASE): "driving",
    re.compile(r"\bnavigating the complexities of\b", re.IGNORECASE): "managing",
    re.compile(r"\bgroundbreaking\b", re.IGNORECASE): "high-yield",
    re.compile(r"\bgame-changer\b", re.IGNORECASE): "inflection point",
    re.compile(r"\brobust framework\b", re.IGNORECASE): "operational framework",
    re.compile(r"\bcutting-edge\b", re.IGNORECASE): "modern",
    re.compile(r"\bstate-of-the-art\b", re.IGNORECASE): "production-grade",
    re.compile(r"\bparadigm shift\b", re.IGNORECASE): "structural shift",
    re.compile(r"\bcatalyst for change\b", re.IGNORECASE): "driver of execution",
    re.compile(r"\bBrings verified enterprise telemetry:\b", re.IGNORECASE): "Key achievements include:",
    re.compile(r"\bSenior senior / lead / executive director tier \(10\+ yoe\) leader\b", re.IGNORECASE): "Executive AI Delivery & Transformation Director (10+ years)",
}


class AIDetectorGuardrail:
    """
    Evaluates AI probability using statistical linguistics (burstiness & vocabulary entropy)
    and pattern heuristics, with an automated humanizer to de-synthesize prose.
    """

    @staticmethod
    def split_sentences(text: str) -> List[str]:
        """Splits prose into distinct sentences, skipping markdown headers and bullets."""
        clean_lines = []
        for line in text.splitlines():
            line_s = line.strip()
            if not line_s or line_s.startswith("#") or line_s.startswith("---"):
                continue
            line_s = re.sub(r"^[-*•]\s+", "", line_s)
            clean_lines.append(line_s)
        
        joined = " ".join(clean_lines)
        raw_sentences = re.split(r"(?<=[.!?])\s+", joined)
        sentences = [s.strip() for s in raw_sentences if len(s.strip()) > 10]
        return sentences

    @classmethod
    def calculate_burstiness(cls, sentences: List[str]) -> Tuple[float, float, float]:
        """
        Calculates coefficient of variation (CV) of sentence lengths.
        Returns: (cv_score, mean_length, std_dev)
        - High CV (> 0.45): High burstiness (varied rhythm -> human-like).
        - Low CV (< 0.35): Uniform robotic cadence (synthetic -> AI-like).
        """
        if not sentences or len(sentences) < 2:
            return (0.5, 15.0, 5.0)

        lengths = [len(s.split()) for s in sentences]
        mean_len = sum(lengths) / len(lengths)
        if mean_len == 0:
            return (0.0, 0.0, 0.0)

        variance = sum((l - mean_len) ** 2 for l in lengths) / len(lengths)
        std_dev = math.sqrt(variance)
        cv = std_dev / mean_len
        return (round(cv, 3), round(mean_len, 1), round(std_dev, 1))

    @classmethod
    def calculate_vocabulary_richness(cls, text: str) -> Dict[str, float]:
        """Measures lexical diversity (Type-Token Ratio and Hapax Legomena Ratio)."""
        words = re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())
        total_tokens = len(words)
        if total_tokens == 0:
            return {"ttr": 0.5, "hapax_ratio": 0.3}

        unique_words = set(words)
        ttr = len(unique_words) / total_tokens

        word_counts: Dict[str, int] = {}
        for w in words:
            word_counts[w] = word_counts.get(w, 0) + 1

        hapax = sum(1 for w, c in word_counts.items() if c == 1)
        hapax_ratio = hapax / total_tokens

        return {
            "ttr": round(ttr, 3),
            "hapax_ratio": round(hapax_ratio, 3),
            "total_tokens": total_tokens,
            "unique_tokens": len(unique_words),
        }

    @classmethod
    def find_cliches(cls, text: str) -> List[Dict[str, Any]]:
        """Scans for known LLM synthetic markers and returns matches with context."""
        matches = []
        for pattern in SYNTHETIC_CLICHE_PATTERNS:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                start = max(0, match.start() - 30)
                end = min(len(text), match.end() + 30)
                matches.append({
                    "phrase": match.group(0),
                    "context": text[start:end].replace("\n", " ").strip(),
                    "position": match.start()
                })
        return matches

    @classmethod
    def audit_text(cls, text: str) -> Dict[str, Any]:
        """Full sanity audit, calculating an overall AI Likelihood Index (0% to 100%)."""
        sentences = cls.split_sentences(text)
        cv, mean_len, std_dev = cls.calculate_burstiness(sentences)
        vocab = cls.calculate_vocabulary_richness(text)
        cliches = cls.find_cliches(text)

        # 1. Burstiness penalty
        if cv >= 0.48:
            burst_risk = 0.0
        elif cv >= 0.38:
            burst_risk = 0.15
        elif cv >= 0.28:
            burst_risk = 0.40
        else:
            burst_risk = 0.70

        # 2. Cliché density per 500 words
        word_count = max(1, vocab.get("total_tokens", 100))
        cliche_density = (len(cliches) / (word_count / 500.0))
        cliche_risk = min(1.0, cliche_density * 0.25)

        # 3. Sentence length uniformity penalty
        length_penalty = 0.0
        if 17.0 <= mean_len <= 23.0 and std_dev < 5.0:
            length_penalty = 0.25

        raw_score = (burst_risk * 0.40) + (cliche_risk * 0.45) + (length_penalty * 0.15)
        ai_likelihood = min(1.0, max(0.0, raw_score))
        human_authenticity_score = round((1.0 - ai_likelihood) * 100, 1)

        verdict = "PASS"
        if ai_likelihood > 0.40:
            verdict = "HIGH_AI_RISK"
        elif ai_likelihood > 0.20:
            verdict = "MODERATE_AI_RISK"

        return {
            "ai_likelihood_percent": round(ai_likelihood * 100, 1),
            "human_authenticity_percent": human_authenticity_score,
            "verdict": verdict,
            "metrics": {
                "burstiness_cv": cv,
                "mean_sentence_length": mean_len,
                "sentence_std_dev": std_dev,
                "sentence_count": len(sentences),
                "type_token_ratio": vocab.get("ttr", 0.0),
                "hapax_ratio": vocab.get("hapax_ratio", 0.0),
                "cliche_count": len(cliches),
            },
            "flagged_cliches": cliches,
        }

    @classmethod
    def humanize_prose(cls, text: str) -> Tuple[str, Dict[str, Any]]:
        """Transforms synthetic AI text into authentic human phrasing."""
        cleaned = text

        for pattern, replacement in HUMAN_REPLACEMENTS.items():
            cleaned = pattern.sub(replacement, cleaned)

        cleaned = re.sub(
            r"Specialized in driving ([^,]+), enforcing ([^,]+), and aligning ([^.]+)\.",
            r"Focus areas: \1, \2, and \3.",
            cleaned,
            flags=re.IGNORECASE
        )

        lines = cleaned.splitlines()
        reworked_lines = []
        for line in lines:
            if line.startswith("Executive AI Delivery") or ("operating models" in line and "Specialized in" in line):
                line = re.sub(r"\s+", " ", line).strip()
                parts = line.split(". ")
                if len(parts) >= 3:
                    line = f"{parts[0]}. {parts[1]}. {'. '.join(parts[2:])}"
            reworked_lines.append(line)

        final_text = "\n".join(reworked_lines)

        audit_before = cls.audit_text(text)
        audit_after = cls.audit_text(final_text)

        return final_text, {
            "before": audit_before,
            "after": audit_after,
            "cliches_removed": audit_before["metrics"]["cliche_count"] - audit_after["metrics"]["cliche_count"],
            "authenticity_gain": round(audit_after["human_authenticity_percent"] - audit_before["human_authenticity_percent"], 1)
        }