"""Match Scoring Engine.
Computes explainable, deterministic, hybrid match scores (0-100) using ONE unified formula
for both before and after tailoring.
Labels score as 'Estimated Match Score' (never 'ATS score', per Instruction #6).
Implements stuffing penalties with resume-wide keyword repetition caps (Instruction #12),
seniority ladder alignment, and 3-class missing skill classification (missing, present_not_visible, adjacent).
"""

import re
from typing import Dict, List, Any, Optional, Set, Tuple
from pydantic import BaseModel, ConfigDict, Field

from contracts.models.tailored_content import (
    ScoreBreakdown,
    MatchedSkill,
    MissingSkill,
    PresentNotVisibleSkill,
    AdjacentSkill,
    SkillsAnalysis,
)
from app.schemas.tailoring import JDAnalysis
from app.services.skill_taxonomy import skill_taxonomy_service
from app.services.resume_inventory import ResumeInventory, build_resume_inventory


class MatchScoringResult(BaseModel):
    model_config = ConfigDict(extra="forbid")
    estimated_match_score: float = Field(..., ge=0.0, le=100.0, description="Estimated match score")
    score_breakdown: ScoreBreakdown
    skills_analysis: SkillsAnalysis
    matched_keywords: List[str] = Field(default_factory=list)
    missing_keywords: List[str] = Field(default_factory=list)


def calculate_resume_seniority(inventory: ResumeInventory) -> int:
    """Calculates resume seniority level from 0 (Intern/Fresher) to 5 (Director/Executive)."""
    text_corpus = " ".join(list(inventory.entities) + list(inventory.bullet_map.values())).lower()

    if any(k in text_corpus for k in ["director", "vp", "head of engineering"]):
        return 5
    if any(k in text_corpus for k in ["staff engineer", "principal engineer", "lead architect"]):
        return 4
    if any(k in text_corpus for k in ["senior engineer", "senior developer", "sr."]):
        return 3
    if any(k in text_corpus for k in ["intern", "internship", "student", "graduate"]):
        return 0
    return 2  # Default Mid-Level


def compute_match_score(
    inventory: ResumeInventory,
    jd: JDAnalysis,
    master_items: Optional[List[Dict[str, Any]]] = None,
    accepted_changes: Optional[List[Any]] = None,
) -> MatchScoringResult:
    """Unified deterministic match scoring function used for both before and after tailoring.

    Weights:
    - 40% Required Skill Coverage
    - 15% Preferred Skill Coverage
    - 25% Semantic Relevance
    - 10% Seniority & Title Alignment
    - 10% ATS Readability & Placement
    - Penalty: Stuffing & keyword repetition cap
    """
    master_items = master_items or []
    accepted_changes = accepted_changes or []

    # Compile skills present in resume (including any accepted additions)
    active_skills: Dict[str, List[str]] = {}
    for c_name, item in inventory.skills.items():
        active_skills[c_name.lower()] = item.content_ids

    # Incorporate accepted changes
    for chg in accepted_changes:
        after_text = chg.after if hasattr(chg, "after") else (chg.get("after") if isinstance(chg, dict) else "")
        if isinstance(after_text, str):
            words = re.findall(r"\b[A-Za-z0-9\.\+\#\/\-]{2,20}\b", after_text)
            for w in words:
                norm = skill_taxonomy_service.normalize_term(w)
                if norm.is_mapped and norm.category != "Other":
                    active_skills.setdefault(norm.canonical_name.lower(), []).append(
                        getattr(chg, "target_content_id", None) or "tailored_bullet"
                    )

    # Compile master profile items
    master_skill_map: Dict[str, str] = {}
    for mi in master_items:
        m_text = mi.get("text", "")
        norm = skill_taxonomy_service.normalize_term(m_text)
        if norm.is_mapped and norm.status == "approved":
            master_skill_map[norm.canonical_name.lower()] = mi.get("id", "master_item")
        else:
            for w in re.findall(r"\b[A-Za-z0-9\.\+\#\/\-]{2,25}\b", m_text):
                w_norm = skill_taxonomy_service.normalize_term(w)
                if w_norm.is_mapped and w_norm.category != "Other":
                    master_skill_map[w_norm.canonical_name.lower()] = mi.get("id", "master_item")

    # 1. Required Skill Coverage (40%)
    req_skills = [s for s in jd.required_skills if s]
    matched_req = []
    missing_req = []

    matched_skills_list: List[MatchedSkill] = []
    missing_skills_list: List[MissingSkill] = []
    present_not_visible_list: List[PresentNotVisibleSkill] = []
    adjacent_skills_list: List[AdjacentSkill] = []

    for s in req_skills:
        s_norm = skill_taxonomy_service.normalize_term(s)
        s_key = s_norm.canonical_name.lower()

        if s_key in active_skills:
            matched_req.append(s_norm.canonical_name)
            matched_skills_list.append(
                MatchedSkill(
                    skill=s,
                    canonical_name=s_norm.canonical_name,
                    category=s_norm.category,
                    content_ids=active_skills[s_key],
                )
            )
        else:
            missing_req.append(s_norm.canonical_name)
            # Classify into 3 distinct classes (Instruction #4)
            if s_key in master_skill_map:
                present_not_visible_list.append(
                    PresentNotVisibleSkill(
                        skill=s,
                        canonical_name=s_norm.canonical_name,
                        master_item_id=master_skill_map[s_key],
                    )
                )
            else:
                missing_skills_list.append(
                    MissingSkill(
                        skill=s,
                        canonical_name=s_norm.canonical_name,
                        category=s_norm.category,
                        importance="required",
                    )
                )
                # Check for adjacent skills
                adj_candidates = skill_taxonomy_service.get_adjacent_skills(s_norm.canonical_name)
                for adj_skill, relation in adj_candidates:
                    if adj_skill.lower() in active_skills:
                        adjacent_skills_list.append(
                            AdjacentSkill(
                                jd_skill=s_norm.canonical_name,
                                resume_skill=adj_skill,
                                relation=relation,
                            )
                        )

    req_coverage_score = round(40.0 * (len(matched_req) / max(1, len(req_skills))), 2)

    # 2. Preferred Skill Coverage (15%)
    pref_skills = [s for s in jd.preferred_skills if s]
    matched_pref = []
    for s in pref_skills:
        s_norm = skill_taxonomy_service.normalize_term(s)
        s_key = s_norm.canonical_name.lower()
        if s_key in active_skills:
            matched_pref.append(s_norm.canonical_name)
            if s_norm.canonical_name not in [m.canonical_name for m in matched_skills_list]:
                matched_skills_list.append(
                    MatchedSkill(
                        skill=s,
                        canonical_name=s_norm.canonical_name,
                        category=s_norm.category,
                        content_ids=active_skills[s_key],
                    )
                )
        else:
            if s_key in master_skill_map:
                present_not_visible_list.append(
                    PresentNotVisibleSkill(
                        skill=s,
                        canonical_name=s_norm.canonical_name,
                        master_item_id=master_skill_map[s_key],
                    )
                )
            else:
                missing_skills_list.append(
                    MissingSkill(
                        skill=s,
                        canonical_name=s_norm.canonical_name,
                        category=s_norm.category,
                        importance="preferred",
                    )
                )
                # Check for adjacent skills
                adj_candidates = skill_taxonomy_service.get_adjacent_skills(s_norm.canonical_name)
                for adj_skill, relation in adj_candidates:
                    if adj_skill.lower() in active_skills:
                        adjacent_skills_list.append(
                            AdjacentSkill(
                                jd_skill=s_norm.canonical_name,
                                resume_skill=adj_skill,
                                relation=relation,
                            )
                        )

    pref_coverage_score = round(15.0 * (len(matched_pref) / max(1, len(pref_skills))), 2)

    # 3. Semantic Relevance of Experience to JD Responsibilities (25%)
    resp_tokens = set()
    for resp in jd.responsibilities:
        resp_tokens.update(re.findall(r"\b\w{4,15}\b", resp.lower()))

    bullet_corpus = " ".join(inventory.bullet_map.values()).lower()
    bullet_tokens = set(re.findall(r"\b\w{4,15}\b", bullet_corpus))

    semantic_ratio = len(resp_tokens.intersection(bullet_tokens)) / max(1, len(resp_tokens))
    semantic_score = round(25.0 * min(1.0, semantic_ratio * 1.5), 2)

    # 4. Seniority & Title Alignment (10%)
    res_sen = calculate_resume_seniority(inventory)
    jd_sen = jd.seniority_level
    delta = abs(res_sen - jd_sen)
    if delta == 0:
        sen_factor = 1.0
    elif delta == 1:
        sen_factor = 0.8
    elif delta == 2:
        sen_factor = 0.5
    else:
        sen_factor = 0.2

    # Freshers with internships match junior / entry perfectly (Instruction #12)
    if res_sen == 0 and jd_sen in (0, 1):
        sen_factor = 1.0

    seniority_score = round(10.0 * sen_factor, 2)

    # 5. ATS Readability & Placement (10%)
    # Keywords should appear in bullets and context, not merely in an isolated list
    in_bullet_count = sum(1 for c_name, item in inventory.skills.items() if any("_b" in cid for cid in item.content_ids))
    placement_ratio = in_bullet_count / max(1, len(inventory.skills))
    ats_score = round(10.0 * min(1.0, 0.4 + (0.6 * placement_ratio)), 2)

    # 6. Keyword Stuffing Penalty (Instruction #12: resume-wide repetition cap)
    stuffing_penalty = 0.0
    keyword_counts: Dict[str, int] = {}
    for kw in jd.keywords:
        kw_clean = kw.lower().strip()
        cnt = len(re.findall(r"\b" + re.escape(kw_clean) + r"\b", bullet_corpus))
        keyword_counts[kw_clean] = cnt
        # Resume-wide cap: max 5 repetitions of any single keyword across the resume
        if cnt > 5:
            excess = cnt - 5
            stuffing_penalty += excess * 1.0

    stuffing_penalty = min(20.0, round(stuffing_penalty, 2))

    # Total Estimated Match Score
    raw_total = req_coverage_score + pref_coverage_score + semantic_score + seniority_score + ats_score - stuffing_penalty
    total_score = max(0.0, min(100.0, round(raw_total, 1)))

    confidence_note = None
    if len(req_skills) < 3 or len(jd.responsibilities) < 2:
        confidence_note = "Job description is concise or missing explicit requirements; scoring reflects best-effort keyword and semantic alignment."

    breakdown = ScoreBreakdown(
        required_skill_coverage=req_coverage_score,
        preferred_skill_coverage=pref_coverage_score,
        semantic_relevance=semantic_score,
        seniority_fit=seniority_score,
        ats_readability=ats_score,
        stuffing_penalty=stuffing_penalty,
        confidence_note=confidence_note,
    )

    analysis = SkillsAnalysis(
        matched_skills=matched_skills_list,
        missing_skills=missing_skills_list,
        present_not_visible=present_not_visible_list,
        adjacent_skills=adjacent_skills_list,
    )

    all_matched = sorted(list({m.canonical_name for m in matched_skills_list}))
    all_missing = sorted(list({m.canonical_name for m in missing_skills_list}))

    return MatchScoringResult(
        estimated_match_score=total_score,
        score_breakdown=breakdown,
        skills_analysis=analysis,
        matched_keywords=all_matched,
        missing_keywords=all_missing,
    )


def calculate_match_score(content: Any, jd_analysis: Any):
    """Backward-compatible adapter for legacy pipeline nodes."""
    from app.schemas.tailoring import MatchScore
    content_dict = content.model_dump() if hasattr(content, "model_dump") else (content if isinstance(content, dict) else {})
    inv = build_resume_inventory(content_dict)
    res = compute_match_score(inv, jd_analysis)
    return MatchScore(
        total_score=int(round(res.estimated_match_score)),
        matched_keywords=res.matched_keywords,
        missing_keywords=res.missing_keywords,
        coverage_ratio=round(res.score_breakdown.required_skill_coverage / 40.0, 2),
        explanation=f"Estimated match score: {res.estimated_match_score}%",
    )
