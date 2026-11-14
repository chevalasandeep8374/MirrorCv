import re
from typing import List, Set, Tuple
from app.schemas.content import ResumeContent
from app.schemas.tailoring import JDAnalysis, MatchScore


def calculate_match_score(content: ResumeContent, jd_analysis: JDAnalysis) -> MatchScore:
    """Calculates a simple, transparent keyword match score

    between the resume content and the job description requirements.
    """
    resume_text = content.model_dump_json().lower()

    required = [s.strip() for s in jd_analysis.required_skills if s.strip()]
    preferred = [s.strip() for s in jd_analysis.preferred_skills + jd_analysis.tools_and_tech if s.strip()]

    # Deduplicate
    all_keywords_map = {}
    for r in required:
        all_keywords_map[r] = 2.0  # Required skills weighted 2x
    for p in preferred:
        if p not in all_keywords_map:
            all_keywords_map[p] = 1.0  # Preferred weighted 1x

    if not all_keywords_map:
        return MatchScore(
            total_score=100,
            matched_keywords=[],
            missing_keywords=[],
            coverage_ratio=1.0,
            explanation="No specific keywords required in the job description.",
        )

    matched: List[str] = []
    missing: List[str] = []
    total_weight = sum(all_keywords_map.values())
    matched_weight = 0.0

    for kw, weight in all_keywords_map.items():
        kw_clean = kw.lower()
        # Word boundary or clean substring match
        pattern = r"\b" + re.escape(kw_clean) + r"\b"
        if re.search(pattern, resume_text) or kw_clean in resume_text:
            matched.append(kw)
            matched_weight += weight
        else:
            missing.append(kw)

    ratio = matched_weight / total_weight if total_weight > 0 else 1.0
    total_score = min(100, max(0, int(ratio * 100)))

    explanation = (
        f"Matched {len(matched)} of {len(all_keywords_map)} target skills/tools "
        f"({len([k for k in matched if all_keywords_map.get(k) == 2.0])} required, "
        f"{len([k for k in matched if all_keywords_map.get(k) == 1.0])} preferred)."
    )

    return MatchScore(
        total_score=total_score,
        matched_keywords=matched,
        missing_keywords=missing,
        coverage_ratio=round(ratio, 2),
        explanation=explanation,
    )
