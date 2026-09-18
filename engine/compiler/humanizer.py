"""
CareerOS AI Content Detector Sanity Checker & Humanizer Guardrail
================================================================
Calculates statistical perplexity/burstiness proxies, scans for generative AI
clichés, and applies human executive calibration to prevent resumes and pitches
from getting flagged by ATS AI detectors (GPTZero, Copyleaks, Turnitin, Winston).
"""

import math
import re
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Any


# Common generative AI giveaway buzzwords, transitions, and phrases
AI_CLICHE_PATTERNS = [
    r"\bspearheaded\b",
    r"\bleverag(ing|ed|es)\b",
    r"\btestament to\b",
    r"\bfoster(ed|ing|s)? a culture of\b",
    r"\bseamless(ly)?\b",
    r"\bpivotal role\b",
    r"\bbeacon\b",
    r"\btapestry\b",
    r"\bdelv(e|ing|ed)\b",
    r"\bholistic(ally)?\b",
    r"\bin order to\b",
    r"\brobust framework\b",
    r"\bgroundbreaking\b",
    r"\brevolutioniz(ed|ing|e)\b",
    r"\btransformative journey\b",
    r"\bin today'?s rapidly evolving\b",
    r"\bdynamic landscape\b",
    r"\bharness(ed|ing)\b",
    r"\bgame-changer\b",
    r"\bparadigm shift\b",
    r"\bnavigat(ing|ed) the complexities\b",
    r"\bunwavering commitment\b",
    r"\bmeticulous(ly)?\b",
    r"\bat the forefront of\b",
    r"\bsynerg(y|ies|istic)\b",
    r"\bcutting-edge\b",
    r"\bpoised to\b",
    r"\bchampion(ed|ing)\b",
    r"\bcatalyst for\b",
    r"\bintertwined\b",
    r"\brich tapestry\b",
    r"\bvibrant ecosystem\b",
    r"\bempowering teams to\b",
    r"\bdriving impactful change\b",
    r"\ba wide array of\b",
    r"\bunleash(ing)?\b",
]

# Replacement mapping: Swap vague generative clichés for grounded, direct executive verbs
HUMAN_VERB_REPLACEMENTS = {
    r"\bspearheaded the development of\b": "Directed delivery of",
    r"\bspearheaded\b": "Led",
    r"\bleveraging\b": "using",
    r"\bleveraged\b": "used",
    r"\bleverages\b": "uses",
    r"\bseamlessly integrated\b": "integrated",
    r"\bseamlessly\b": "smoothly",
    r"\bseamless\b": "direct",
    r"\bfostered a culture of\b": "built",
    r"\bfostering\b": "building",
    r"\bfosters?\b": "builds",
    r"\bpivotal role in\b": "direct role in",
    r"\bpivotal\b": "key",
    r"\bin order to\b": "to",
    r"\bdelve into\b": "examine",
    r"\bdelved into\b": "analyzed",
    r"\bdelving into\b": "reviewing",
    r"\bholistic approach\b": "end-to-end framework",
    r"\bholistic\b": "comprehensive",
    r"\brobust framework\b": "production architecture",
    r"\brobust\b": "resilient",
    r"\bharnessing the power of\b": "using",
    r"\bharnessing\b": "applying",
    r"\bharnessed\b": "applied",
    r"\brevolutionized\b": "modernized",
    r"\brevolutionizing\b": "modernizing",
    r"\brevolutionize\b": "modernize",
    r"\btransformative journey\b": "systemic migration",
    r"\btransformative\b": "structural",
    r"\bnavigating the complexities of\b": "managing",
    r"\bnavigating\b": "managing",
    r"\bnavigated\b": "managed",
    r"\bat the forefront of\b": "leading",
    r"\bcutting-edge\b": "modern",
    r"\bchampioned the adoption of\b": "introduced and scaled",
    r"\bchampioned\b": "drove",
    r"\bcatalyst for\b": "driver of",
    r"\bempowering teams to\b": "enabling squads to",
    r"\bempowered teams to\b": "enabled squads to",
    r"\ba wide array of\b": "multiple",
    r"\bgroundbreaking\b": "high-impact",
    r"\bdynamic landscape\b": "operating environment",
    r"\bvibrant ecosystem\b": "team environment",
    r"\bunleash(ing)?\b": "unlocking",
}


@dataclass
class AIDetectionReport:
    """Detailed audit metrics of text authenticity and AI probability."""
    score_ai_probability: float  # 0.0 (Pure Human) to 1.0 (Definite AI)
    authenticity_score: int       # 0 to 100 (100 = 100% Human authentic)
    verdict: str                  # "HUMAN_AUTHENTIC", "MODERATE_RISK", "HIGH_AI_RISK"
    burstiness_index: float       # Sentence length variance (higher is more human)
    token_diversity_ttr: float    # Type-Token Ratio (vocabulary richness)
    cliches_detected: List[str]   # List of flagged AI buzzwords
    sentence_count: int
    avg_sentence_length: float
    recommendations: List[str]


class HumanizerEngine:
    """
    Sanity checks text for AI hallmarks (low burstiness, repetitive tokens,
    characteristic buzzwords) and automatically humanizes it into natural executive prose.
    """

    @classmethod
    def analyze_text(cls, text: str) -> AIDetectionReport:
        """Computes statistical proxies for AI detection (Burstiness, TTR, and Cliché density)."""
        clean_text = text.strip()
        if not clean_text:
            return AIDetectionReport(
                score_ai_probability=0.0,
                authenticity_score=100,
                verdict="HUMAN_AUTHENTIC",
                burstiness_index=1.0,
                token_diversity_ttr=1.0,
                cliches_detected=[],
                sentence_count=0,
                avg_sentence_length=0.0,
                recommendations=[]
            )

        # Split sentences
        sentences = [s.strip() for s in re.split(r"[.!?]+(?:\s+|$)", clean_text) if s.strip()]
        if not sentences:
            sentences = [clean_text]

        sentence_lengths = [len(re.findall(r"\w+", s)) for s in sentences]
        avg_len = sum(sentence_lengths) / max(len(sentence_lengths), 1)

        # 1. Burstiness (Sentence Length Variance / Standard Deviation)
        # LLMs generate uniform sentence lengths (~18-24 words). Humans vary from 4 to 35 words.
        if len(sentence_lengths) > 1:
            variance = sum((l - avg_len) ** 2 for l in sentence_lengths) / len(sentence_lengths)
            std_dev = math.sqrt(variance)
            burstiness = std_dev / max(avg_len, 1.0)
        else:
            burstiness = 0.5  # Neutral for single sentence

        # 2. Type-Token Ratio (TTR - Vocabulary Diversity)
        words = [w.lower() for w in re.findall(r"\b[a-zA-Z]{3,}\b", clean_text)]
        unique_words = set(words)
        ttr = len(unique_words) / max(len(words), 1.0)

        # 3. AI Cliché Density
        cliches_found = []
        lower_text = clean_text.lower()
        for pattern in AI_CLICHE_PATTERNS:
            matches = re.findall(pattern, lower_text)
            if matches:
                clean_match = pattern.replace(r"\b", "").replace(r"\s+", " ")
                cliches_found.append(clean_match)

        # 4. Composite AI Probability Calculation
        ai_prob = 0.05  # Base floor

        if burstiness < 0.22 and len(sentences) >= 3:
            ai_prob += 0.30
        elif burstiness < 0.35 and len(sentences) >= 3:
            ai_prob += 0.15

        ai_prob += min(len(cliches_found) * 0.18, 0.55)

        if len(words) > 50 and ttr < 0.52:
            ai_prob += 0.15

        ai_prob = min(max(ai_prob, 0.02), 0.98)
        authenticity = int(round((1.0 - ai_prob) * 100))

        # Determine Verdict
        if authenticity >= 80:
            verdict = "HUMAN_AUTHENTIC"
        elif authenticity >= 60:
            verdict = "MODERATE_RISK"
        else:
            verdict = "HIGH_AI_RISK"

        recommendations = []
        if cliches_found:
            recommendations.append(f"Remove or replace flagged AI buzzwords: {', '.join(cliches_found[:4])}")
        if burstiness < 0.30 and len(sentences) >= 3:
            recommendations.append("Vary sentence length: mix punchy short statements (6-10 words) with detailed telemetry.")
        if ttr < 0.55 and len(words) > 50:
            recommendations.append("Increase technical vocabulary specificity with domain-specific tools or squad names.")

        return AIDetectionReport(
            score_ai_probability=round(ai_prob, 3),
            authenticity_score=authenticity,
            verdict=verdict,
            burstiness_index=round(burstiness, 3),
            token_diversity_ttr=round(ttr, 3),
            cliches_detected=cliches_found,
            sentence_count=len(sentences),
            avg_sentence_length=round(avg_len, 1),
            recommendations=recommendations,
        )

    @classmethod
    def humanize_text(cls, text: str) -> Tuple[str, AIDetectionReport]:
        """
        Removes generative AI giveaways, breaks monotone syntax, and transforms
        text into authentic human executive prose.
        """
        humanized = text

        # 1. Replace clichés with direct human executive phrasing
        for pattern, replacement in HUMAN_VERB_REPLACEMENTS.items():
            humanized = re.sub(pattern, replacement, humanized, flags=re.IGNORECASE)

        # 2. Break monotone compound sentences
        humanized = re.sub(
            r",\s*(thereby|thus|seamlessly)?\s*ensuring that\b",
            ". Ensured",
            humanized,
            flags=re.IGNORECASE
        )
        humanized = re.sub(
            r",\s*(thereby|thus)?\s*allowing teams to\b",
            ". Enabled squads to",
            humanized,
            flags=re.IGNORECASE
        )
        humanized = re.sub(
            r"\butilizing\b",
            "using",
            humanized,
            flags=re.IGNORECASE
        )

        # 3. Clean double spaces or awkward punctuation
        humanized = re.sub(r"\s{2,}", " ", humanized)
        humanized = re.sub(r"\s+([.,;:!?])", r"\1", humanized)

        # 4. Re-analyze to ensure it passes
        report = cls.analyze_text(humanized)
        return humanized, report
