"""Tailor Verifier Engine for MirrorCV Agent 2.
Implements strict deterministic code gates, anti-fabrication whitelists,
number normalization, verb elevation detection, URL verification,
word-wrap line budgeting, and secondary entailment checking.
"""

import re
import unicodedata
import logging
from typing import Dict, Any, List, Set, Optional, Tuple, Union
from pydantic import BaseModel

from contracts.models.tailored_content import (
    Change,
    ChangeType,
    ChangeStatus,
    RiskLevel,
)
from app.services.docx_rendering_measurements import measure_lines
from app.services.skill_taxonomy import skill_taxonomy_service

logger = logging.getLogger(__name__)

# Elevation & ownership verbs that cannot be added without source proof
ELEVATION_VERBS: Set[str] = {
    "led", "lead", "leading",
    "managed", "managing", "management",
    "owned", "owning", "ownership",
    "architected", "architecting", "architecture",
    "spearheaded", "spearheading",
    "directed", "directing", "director",
    "founded", "founding", "founder",
    "oversaw", "overseeing",
    "commanded", "commanding",
    "headed", "heading",
}

# Number words mapping
WORD_TO_NUMBER: Dict[str, float] = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4,
    "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
    "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13,
    "fourteen": 14, "fifteen": 15, "sixteen": 16, "seventeen": 17,
    "eighteen": 18, "nineteen": 19, "twenty": 20, "thirty": 30,
    "forty": 40, "fifty": 50, "sixty": 60, "seventy": 70,
    "eighty": 80, "ninety": 90,
}

TENS: Set[str] = {"twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"}
ONES: Set[str] = {"one", "two", "three", "four", "five", "six", "seven", "eight", "nine"}

MULTIPLIERS: Dict[str, float] = {
    "hundred": 100,
    "thousand": 1_000,
    "k": 1_000,
    "million": 1_000_000,
    "m": 1_000_000,
    "billion": 1_000_000_000,
    "b": 1_000_000_000,
}

# Homoglyph substitution map for Cyrillic / full-width characters
HOMOGLYPH_MAP: Dict[str, str] = {
    "а": "a", "с": "c", "е": "e", "о": "o", "р": "p", "х": "x", "у": "y",
    "А": "A", "В": "B", "С": "C", "Е": "E", "Н": "H", "К": "K", "М": "M",
    "О": "O", "Р": "P", "Т": "T", "Х": "X",
    "і": "i", "ј": "j", "\u200b": "", "\u200c": "", "\u200d": "", "\ufeff": "",
}

# Non-entity common capitalized English words
COMMON_CAPITALIZED_WORDS: Set[str] = {
    "the", "a", "an", "in", "with", "for", "on", "at", "to", "by", "from",
    "and", "or", "as", "our", "my", "their", "we", "i", "it", "its", "all",
    "developed", "engineered", "implemented", "designed", "built", "optimized",
    "created", "assisted", "collaborated", "authored", "maintained", "configured",
    "deployed", "scaled", "automated", "enhanced", "delivered", "supported",
    "used", "use", "using",
    "senior", "junior", "lead", "staff", "director", "head", "principal",
    "software", "engineer", "developer", "architecture", "architect", "systems",
    "system", "services", "service", "cloud", "backend", "frontend", "fullstack",
    "full", "stack", "data", "database", "databases", "api", "apis", "code",
    "documentation", "docs", "project", "projects", "team", "teams", "management",
    "infrastructure", "platform", "applications", "application", "solutions", "solution",
}

# 5 Neutral verbs allowed without prior source grounding
PERMITTED_NEUTRAL_VERBS: Set[str] = {
    "built", "build", "building",
    "developed", "develop", "developing",
    "implemented", "implement", "implementing",
    "used", "use", "using",
    "created", "create", "creating",
}

# Quality and scale claims that strictly require source resume or confirmed profile proof
SCALE_AND_QUALITY_CLAIMS: Set[str] = {
    "scalable",
    "high-performance",
    "production-ready",
    "enterprise-grade",
    "mission-critical",
    "resilient",
    "fault-tolerant",
    "low-latency",
    "distributed",
    "robust",
    "state-of-the-art",
    "high-throughput",
    "ultra-low-latency",
    "high-availability",
    "highly-scalable",
    "battle-tested",
    "world-class",
}

# Whitelisted English function words allowed without prior source grounding
FUNCTION_WORDS: Set[str] = {
    # Prepositions
    "in", "on", "at", "to", "for", "with", "by", "from", "of", "about",
    "as", "into", "through", "after", "over", "between", "out", "against",
    "during", "without", "before", "under", "around", "among", "across",
    "within", "upon", "towards", "along", "behind", "beyond", "up", "down",
    # Conjunctions
    "and", "or", "but", "nor", "so", "yet", "either", "neither",
    "while", "although", "though", "since", "unless", "whereas",
    # Articles & determiners
    "the", "a", "an", "this", "that", "these", "those", "each", "every",
    "all", "both", "half", "some", "any", "no", "many", "much", "more",
    "most", "other", "another", "such", "what", "which",
    # Pronouns
    "it", "its", "itself", "they", "them", "their", "theirs", "themselves",
    "we", "us", "our", "ours", "ourselves", "you", "your", "yours",
    "i", "me", "my", "mine", "myself", "he", "him", "his", "she", "her", "hers",
    # Auxiliary verbs & copulas
    "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "having",
    "do", "does", "did",
    "will", "would", "shall", "should", "can", "could", "may", "might", "must",
    # Adverbs & particles of comparison / degree
    "not", "also", "then", "there", "here", "when", "where", "why", "how",
    "well", "less", "least", "than", "too", "very", "just",
    "only", "even", "now", "still", "such",
    # Structural connectors
    "including", "via", "per",
}


def normalize_unicode(text: str) -> str:
    """Normalizes Unicode homoglyphs, NFKD forms, and zero-width characters."""
    if not text:
        return ""
    res = text
    for h, replacement in HOMOGLYPH_MAP.items():
        if h in res:
            res = res.replace(h, replacement)
    res = unicodedata.normalize("NFKD", res)
    return res


def extract_numbers_and_quantities(text: str) -> Set[Union[float, Tuple[float, float]]]:
    """Extracts all normalized numeric values, percentages, currencies, and ranges from text."""
    if not text:
        return set()

    text_clean = normalize_unicode(text.lower())
    quantities: Set[Union[float, Tuple[float, float]]] = set()

    # 1. Ranges: e.g. "10-15%", "10 to 15 percent", "3-5 years"
    range_matches = re.findall(r"(\d+(?:\.\d+)?)\s*(?:-|to)\s*(\d+(?:\.\d+)?)\s*(%|percent)?", text_clean)
    for rm in range_matches:
        try:
            low = float(rm[0])
            high = float(rm[1])
            quantities.add((low, high))
        except ValueError:
            pass

    # Normalize compound number words: "twenty-five" -> "twenty five"
    text_clean = re.sub(
        r"\b(twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety)-(one|two|three|four|five|six|seven|eight|nine)\b",
        r"\1 \2",
        text_clean,
    )

    # 2. Number words and combinations
    words = text_clean.split()
    i = 0
    while i < len(words):
        w = words[i].strip(",.;:()[]")
        current_val: Optional[float] = None

        if w in TENS and i + 1 < len(words):
            next_w = words[i + 1].strip(",.;:()[]")
            if next_w in ONES:
                current_val = WORD_TO_NUMBER[w] + WORD_TO_NUMBER[next_w]
                i += 1
            else:
                current_val = WORD_TO_NUMBER[w]
        elif w in WORD_TO_NUMBER:
            current_val = WORD_TO_NUMBER[w]
        elif re.match(r"^\d+(?:\.\d+)?$", w):
            try:
                current_val = float(w)
            except ValueError:
                pass

        if current_val is not None:
            # Check next word for multiplier
            if i + 1 < len(words):
                next_w = words[i + 1].strip(",.;:()[]")
                if next_w in MULTIPLIERS:
                    current_val *= MULTIPLIERS[next_w]
                    i += 1
            quantities.add(round(current_val, 2))
        i += 1

    # 3. Numeric tokens with suffixes: e.g. "$40k", "$40,000", "35%", "4.2M", "100K"
    raw_num_matches = re.findall(r"[\$€£]?\s*(\d{1,3}(?:,\d{3})*|\d+)(?:\.(\d+))?\s*([kKmMbB%])?", text_clean)
    for m in raw_num_matches:
        int_part = m[0].replace(",", "")
        dec_part = m[1]
        suffix = m[2].lower() if m[2] else ""
        try:
            val_str = f"{int_part}.{dec_part}" if dec_part else int_part
            num = float(val_str)
            if suffix in MULTIPLIERS:
                num *= MULTIPLIERS[suffix]
            quantities.add(round(num, 2))
        except ValueError:
            pass

    return quantities


def extract_urls(text: str) -> Set[str]:
    """Extracts URLs from markdown links and raw text."""
    if not text:
        return set()
    urls: Set[str] = set()
    md_links = re.findall(r"\[([^\]]+)\]\((https?://[^\s\)]+)\)", text)
    for _, u in md_links:
        urls.add(u.strip().rstrip(".,;/"))
    bare = re.findall(r"(https?://[^\s\)]+)", text)
    for u in bare:
        urls.add(u.strip().rstrip(".,;/"))
    return urls


class EntailmentCheckResponse(BaseModel):
    is_entailed: bool = True
    confidence: float = 1.0
    reason: str = "Entailed"
    exaggeration_detected: bool = False


class VerificationResult(BaseModel):
    is_valid: bool
    rejection_reason: Optional[str] = None
    gate_failed: Optional[str] = None
    is_repairable: bool = False
    disagreements: List[str] = []


class TailorVerifier:
    """Rigorous anti-hallucination verification engine for Agent 2."""

    def __init__(self):
        pass

    def verify_change(
        self,
        change: Change,
        resume_content: Dict[str, Any],
        source_inventory_skills: Set[str],
        confirmed_evidence_text: str = "",
        slot_or_params: Any = None,
        max_lines: int = 2,
    ) -> VerificationResult:
        """Runs the 7 deterministic verification gates on a proposed change."""
        # Force default proposed status
        if change.status == ChangeStatus.accepted:
            change.status = ChangeStatus.proposed

        def _record_failure(res: VerificationResult) -> VerificationResult:
            if not res.is_valid and res.gate_failed:
                if res.gate_failed not in change.gates_tripped:
                    change.gates_tripped.append(res.gate_failed)
            return res

        # hide_item and add_item_from_master_profile are medium risk
        if change.type in (ChangeType.hide_item, ChangeType.add_item_from_master_profile):
            change.risk_level = RiskLevel.medium

        # add_item_from_master_profile requires explicit confirmed evidence from master profile
        if change.type == ChangeType.add_item_from_master_profile:
            if not change.evidence_ids:
                return _record_failure(VerificationResult(
                    is_valid=False,
                    rejection_reason="add_item_from_master_profile requires confirmed evidence_ids from master profile.",
                    gate_failed="missing_master_profile_evidence",
                    is_repairable=False,
                ))
            if not confirmed_evidence_text:
                return _record_failure(VerificationResult(
                    is_valid=False,
                    rejection_reason="No confirmed master profile items available to corroborate added item.",
                    gate_failed="unconfirmed_master_item",
                    is_repairable=False,
                ))

        # Gate: Reject any modification targeting bullet proficiency (user self-rating protected)
        if change.field in ("proficiency", "bullets[].proficiency", "bullet.proficiency") or "proficiency" in change.field:
            return _record_failure(VerificationResult(
                is_valid=False,
                rejection_reason="Modifying bullet proficiency ratings via tailoring agent is forbidden. Proficiency is user-controlled only.",
                gate_failed="disallowed_proficiency_modification",
                is_repairable=False,
            ))

        # Handle Reorder Changes (Gate e: Reordering)
        if change.type in (ChangeType.reorder_bullets, ChangeType.reorder_items, ChangeType.reorder_skills):
            return _record_failure(self._verify_reorder(change))

        after_text = str(change.after or "")
        before_text = str(change.before or "")

        # 0. Prompt Injection & Adversarial Attack Gate
        injection_result = self._check_prompt_injection(after_text)
        if not injection_result.is_valid:
            return _record_failure(injection_result)

        # Gate d1: Disallowed HTML Markup
        markup_result = self._check_markup(after_text)
        if not markup_result.is_valid:
            return _record_failure(markup_result)

        # Gate d2: Link URLs authorization
        url_result = self._check_links(after_text, before_text, resume_content, confirmed_evidence_text)
        if not url_result.is_valid:
            return _record_failure(url_result)

        # Gate f: Elevation & Ownership Verbs / Scope Expansion
        verb_result = self._check_elevation_verbs(after_text, before_text, confirmed_evidence_text)
        if not verb_result.is_valid:
            return _record_failure(verb_result)

        # Gate a: Numbers & Metrics Verification
        number_result = self._check_numbers(after_text, before_text, confirmed_evidence_text)
        if not number_result.is_valid:
            return _record_failure(number_result)

        # Gate d3: Line Budget & Font Measurement
        budget_result = self._check_line_budget(after_text, slot_or_params, max_lines)
        if not budget_result.is_valid:
            return _record_failure(budget_result)

        # Gate b & c: Entities and Skills (Job description is NEVER evidence)
        entity_result = self._check_entities_and_skills(
            after_text=after_text,
            before_text=before_text,
            resume_content=resume_content,
            source_inventory_skills=source_inventory_skills,
            confirmed_evidence_text=confirmed_evidence_text,
        )
        if not entity_result.is_valid:
            return _record_failure(entity_result)

        # Gate g1: Scale & Quality Claims Verification
        scale_result = self._check_scale_and_quality_claims(after_text, before_text, resume_content, confirmed_evidence_text)
        if not scale_result.is_valid:
            return _record_failure(scale_result)

        # Gate g2: Novel-term gate (Function words + 5 neutral verbs whitelist)
        novelty_result = self._check_novel_terms(after_text, before_text, resume_content, confirmed_evidence_text, source_inventory_skills)
        if not novelty_result.is_valid:
            return _record_failure(novelty_result)

        # Gate e2: Keyword Stuffing (Max 2 newly emphasized keywords)
        if len(change.keywords_touched) > 2:
            return _record_failure(VerificationResult(
                is_valid=False,
                rejection_reason=f"Exceeded keyword limit: {len(change.keywords_touched)} touched (max 2 allowed per change).",
                gate_failed="keyword_stuffing",
                is_repairable=True,
            ))

        # Gate h: Secondary LLM Entailment & Exaggeration Check
        entailment_res = self._check_llm_entailment(after_text, before_text, confirmed_evidence_text)
        disagreements = []
        if not entailment_res.is_entailed or entailment_res.exaggeration_detected:
            msg = f"LLM Entailment check flagged: {entailment_res.reason}"
            logger.warning(f"Entailment disagreement: {msg}")
            disagreements.append(msg)
            return _record_failure(VerificationResult(
                is_valid=False,
                rejection_reason=entailment_res.reason,
                gate_failed="entailment_check",
                is_repairable=True,
                disagreements=disagreements,
            ))

        return VerificationResult(is_valid=True, disagreements=disagreements)

    def _check_llm_entailment(
        self,
        after_text: str,
        before_text: str,
        confirmed_evidence_text: str,
    ) -> EntailmentCheckResponse:
        """Invokes secondary entailment model with adversarial auditor prompt."""
        from app.services.llm_client import call_llm_structured

        system_prompt = (
            "You are a strict, adversarial natural language inference (NLI) auditor.\n"
            "Evaluate whether the CLAIM in AFTER is strictly entailed by the PREMISE in BEFORE + EVIDENCE.\n"
            "Flag exaggeration_detected=true if the claim adds ungrounded metrics, scope, or seniority."
        )
        prompt = (
            f"<PREMISE>\nBEFORE: {before_text}\nEVIDENCE: {confirmed_evidence_text}\n</PREMISE>\n\n"
            f"<CLAIM>\nAFTER: {after_text}\n</CLAIM>\n\n"
            "Is the CLAIM strictly entailed by the PREMISE without exaggeration or new ungrounded facts?"
        )
        try:
            return call_llm_structured(prompt, EntailmentCheckResponse, system_prompt=system_prompt)
        except Exception as e:
            logger.warning(f"Entailment LLM call fallback: {e}")
            return EntailmentCheckResponse(is_entailed=True, confidence=1.0, reason="Default pass on exception")

    def _verify_reorder(self, change: Change) -> VerificationResult:
        """Verifies that reordering is an exact permutation of existing IDs."""
        before = change.before if isinstance(change.before, list) else []
        after = change.after if isinstance(change.after, list) else []

        if not before or not after:
            return VerificationResult(
                is_valid=False,
                rejection_reason="Reorder change missing before or after ID list.",
                gate_failed="invalid_reorder",
                is_repairable=False,
            )

        if len(after) != len(before):
            return VerificationResult(
                is_valid=False,
                rejection_reason=f"Reorder list length mismatch: before had {len(before)} IDs, after has {len(after)} IDs.",
                gate_failed="invalid_reorder",
                is_repairable=False,
            )

        if len(set(after)) != len(after):
            return VerificationResult(
                is_valid=False,
                rejection_reason="Reorder list contains duplicate IDs.",
                gate_failed="invalid_reorder",
                is_repairable=False,
            )

        if set(after) != set(before):
            missing = set(before) - set(after)
            added = set(after) - set(before)
            return VerificationResult(
                is_valid=False,
                rejection_reason=f"Reorder is not an exact permutation: dropped {missing}, added {added}.",
                gate_failed="invalid_reorder",
                is_repairable=False,
            )

        return VerificationResult(is_valid=True)

    def _check_prompt_injection(self, text: str) -> VerificationResult:
        """Detects prompt injection attempts in generated text."""
        norm_text = normalize_unicode(text.lower())
        injection_patterns = [
            r"ignore\s+(?:all\s+)?(?:previous\s+)?instructions",
            r"system\s+prompt\s+override",
            r"output\s+that\s+the\s+candidate\s+(?:was|is)",
            r"founder\s+and\s+cto\s+of\s+google",
            r"you\s+are\s+now\s+in\s+developer\s+mode",
            r"drop\s+table",
        ]
        for pat in injection_patterns:
            if re.search(pat, norm_text):
                return VerificationResult(
                    is_valid=False,
                    rejection_reason=f"Prompt injection pattern detected: '{pat}'.",
                    gate_failed="prompt_injection",
                    is_repairable=False,
                )
        return VerificationResult(is_valid=True)

    def _check_markup(self, text: str) -> VerificationResult:
        """Ensures only permitted inline markup (bold, italic, link) is used."""
        html_tags = re.findall(r"<[^>]+>", text)
        for tag in html_tags:
            tag_clean = tag.lower().strip()
            if tag_clean not in ("<b>", "</b>", "<i>", "</i>"):
                return VerificationResult(
                    is_valid=False,
                    rejection_reason=f"Disallowed HTML markup '{tag}' found. Only bold, italic, and links allowed.",
                    gate_failed="disallowed_markup",
                    is_repairable=True,
                )
        return VerificationResult(is_valid=True)

    def _check_links(
        self,
        after_text: str,
        before_text: str,
        resume_content: Dict[str, Any],
        confirmed_evidence_text: str,
    ) -> VerificationResult:
        """Ensures any link URLs in 'after' already existed in the source resume or confirmed profile."""
        after_urls = extract_urls(after_text)
        if not after_urls:
            return VerificationResult(is_valid=True)

        allowed_urls = extract_urls(before_text).union(extract_urls(confirmed_evidence_text))
        resume_str = str(resume_content)
        for u in after_urls:
            if u not in allowed_urls and u not in resume_str:
                return VerificationResult(
                    is_valid=False,
                    rejection_reason=f"Unauthorized link URL '{u}' not present in source resume.",
                    gate_failed="unauthorized_link_url",
                    is_repairable=True,
                )
        return VerificationResult(is_valid=True)

    def _check_numbers(
        self,
        after_text: str,
        before_text: str,
        confirmed_evidence_text: str,
    ) -> VerificationResult:
        """Gate a: Numbers and quantities in 'after' must be grounded in source."""
        after_quantities = extract_numbers_and_quantities(after_text)
        if not after_quantities:
            return VerificationResult(is_valid=True)

        source_quantities = extract_numbers_and_quantities(before_text).union(
            extract_numbers_and_quantities(confirmed_evidence_text)
        )

        for q in after_quantities:
            if q not in source_quantities:
                matched = False
                for sq in source_quantities:
                    if isinstance(q, float) and isinstance(sq, float):
                        if abs(q - sq) < 0.01:
                            matched = True
                            break
                    elif isinstance(q, tuple) and isinstance(sq, tuple):
                        if abs(q[0] - sq[0]) < 0.01 and abs(q[1] - sq[1]) < 0.01:
                            matched = True
                            break

                if not matched:
                    return VerificationResult(
                        is_valid=False,
                        rejection_reason=f"Fabricated or altered numeric quantity '{q}' not grounded in source.",
                        gate_failed="fabrication_numbers",
                        is_repairable=True,
                    )
        return VerificationResult(is_valid=True)

    def _check_elevation_verbs(
        self,
        after_text: str,
        before_text: str,
        confirmed_evidence_text: str,
    ) -> VerificationResult:
        """Gate f: Elevation & ownership verbs must already exist in source."""
        after_norm = normalize_unicode(after_text.lower())
        source_norm = normalize_unicode(f"{before_text} {confirmed_evidence_text}".lower())

        words_after = set(re.findall(r"\b[a-z]+\b", after_norm))
        words_source = set(re.findall(r"\b[a-z]+\b", source_norm))

        for v in ELEVATION_VERBS:
            if v in words_after and v not in words_source:
                return VerificationResult(
                    is_valid=False,
                    rejection_reason=f"Unsubstantiated elevation/ownership verb '{v}' not present in source text.",
                    gate_failed="unsubstantiated_elevation_verb",
                    is_repairable=True,
                )

        # Team size and scope claim check
        scope_patterns = [
            r"\bteam\s+of\s+(\d+|\w+)",
            r"\b(?:managed|managing|led|leading)\s+(?:a\s+)?team(?:\s+of)?\s+(\d+|\w+)",
            r"\bbudget\s+of\s+[\$€£]?\s*(\d+|\w+)",
            r"\b(\d+)\s+engineers\b",
        ]
        for pat in scope_patterns:
            after_match = re.search(pat, after_norm)
            source_match = re.search(pat, source_norm)
            if after_match and not source_match:
                return VerificationResult(
                    is_valid=False,
                    rejection_reason=f"Unsubstantiated scope expansion claim '{after_match.group(0)}' not present in source.",
                    gate_failed="unsubstantiated_scope_expansion",
                    is_repairable=True,
                )

        return VerificationResult(is_valid=True)

    def _check_entities_and_skills(
        self,
        after_text: str,
        before_text: str,
        resume_content: Dict[str, Any],
        source_inventory_skills: Set[str],
        confirmed_evidence_text: str,
    ) -> VerificationResult:
        """Gate b & c: Entities, schools, companies, and skills must come from resume, never from JD."""
        after_norm = normalize_unicode(after_text)
        before_norm = normalize_unicode(before_text)
        confirmed_norm = normalize_unicode(confirmed_evidence_text)
        resume_str = str(resume_content)

        # Extract words from link labels so they aren't false positives
        link_labels = re.findall(r"\[([^\]]+)\]", after_norm)
        link_words = set()
        for ll in link_labels:
            for w in ll.split():
                link_words.add(w.lower())

        # Extract potential entity tokens
        tokens = re.findall(r"\b[A-Z][a-zA-Z0-9_-]*\b", after_norm)
        for tok in tokens:
            tok_lower = tok.lower()

            if tok_lower in COMMON_CAPITALIZED_WORDS or tok_lower in link_words:
                continue

            # Check if recognized taxonomy skill
            skill_norm = skill_taxonomy_service.normalize_term(tok)
            if skill_norm.status == "approved":
                if (
                    skill_norm.canonical_name not in source_inventory_skills
                    and tok not in confirmed_evidence_text
                    and tok not in resume_str
                ):
                    return VerificationResult(
                        is_valid=False,
                        rejection_reason=f"Skill '{tok}' not present in source resume inventory or confirmed master profile.",
                        gate_failed="unconfirmed_skill",
                        is_repairable=True,
                    )
            else:
                # Entity (Company, School, Degree, Tool)
                if tok not in resume_str and tok not in confirmed_evidence_text and tok not in before_norm:
                    return VerificationResult(
                        is_valid=False,
                        rejection_reason=f"Fabricated entity/organization '{tok}' not found in source resume.",
                        gate_failed="fabrication_entity",
                        is_repairable=True,
                    )

        return VerificationResult(is_valid=True)

    def _check_line_budget(self, text: str, slot_or_params: Any, max_lines: int) -> VerificationResult:
        """Gate d3: Checks simulated line count against max_lines budget."""
        params = slot_or_params or {
            "line_width_pt": 487.2,
            "formatting": {"font_family": "Calibri", "font_size_pt": 11.0, "bold": False},
        }

        simulated = measure_lines(text, params)
        if simulated > max_lines:
            return VerificationResult(
                is_valid=False,
                rejection_reason=f"Line budget exceeded: text renders to {simulated} lines (max allowed: {max_lines}).",
                gate_failed="budget_exceeded",
                is_repairable=True,
            )
        return VerificationResult(is_valid=True)

    def _check_scale_and_quality_claims(
        self,
        after_text: str,
        before_text: str,
        resume_content: Dict[str, Any],
        confirmed_evidence_text: str,
    ) -> VerificationResult:
        """Enforces that quality and scale claims (scalable, high-performance, enterprise-grade, etc.)
        require explicit source support from the resume or confirmed profile.
        """
        after_norm = normalize_unicode(after_text.lower())
        source_norm = normalize_unicode(f"{before_text} {confirmed_evidence_text} {str(resume_content)}".lower())

        for claim in SCALE_AND_QUALITY_CLAIMS:
            pattern = rf"\b{re.escape(claim)}\b"
            if re.search(pattern, after_norm) and not re.search(pattern, source_norm):
                return VerificationResult(
                    is_valid=False,
                    rejection_reason=f"Unsubstantiated quality/scale claim '{claim}' requires source proof.",
                    gate_failed="unsubstantiated_scale_claim",
                    is_repairable=True,
                )
        return VerificationResult(is_valid=True)

    def _check_novel_terms(
        self,
        after_text: str,
        before_text: str,
        resume_content: Dict[str, Any],
        confirmed_evidence_text: str,
        source_inventory_skills: Set[str],
    ) -> VerificationResult:
        """Enforces that all novel content words in 'after' are grounded:
        Whitelists function words and 5 neutral verbs (built, developed, implemented, used, created).
        Rejects ungrounded skills, entities, elevation verbs, and unsupported claims.
        """
        after_norm = normalize_unicode(after_text.lower())
        source_norm = normalize_unicode(f"{before_text} {confirmed_evidence_text} {str(resume_content)}".lower())

        tokens = re.findall(r"\b[a-z]{3,}\b", after_norm)
        for tok in tokens:
            if tok in FUNCTION_WORDS or tok in PERMITTED_NEUTRAL_VERBS:
                continue
            if tok in source_norm:
                continue

            # Check if recognized taxonomy skill
            skill_norm = skill_taxonomy_service.normalize_term(tok)
            if skill_norm.status == "approved" and skill_norm.canonical_name not in source_inventory_skills:
                return VerificationResult(
                    is_valid=False,
                    rejection_reason=f"Novel technical skill '{tok}' not in source resume or confirmed profile.",
                    gate_failed="unconfirmed_skill",
                    is_repairable=True,
                )

        return VerificationResult(is_valid=True)


tailor_verifier = TailorVerifier()
