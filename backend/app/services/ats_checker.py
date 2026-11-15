import re
from typing import List, Dict, Any, Optional
from app.schemas.ats import AtsCheckItem, AtsStats, AtsAnalysisResponse
from app.schemas.content import ResumeContent
from app.schemas.tailoring import JDAnalysis, MatchScore
from app.services.jd_analyzer import analyze_job_description_sync
from app.services.match_scorer import calculate_match_score


STRONG_ACTION_VERBS = {
    "accelerated", "achieved", "architected", "automated", "built", "championed",
    "compiled", "consolidated", "constructed", "converted", "created", "decreased",
    "delivered", "deployed", "designed", "developed", "directed", "doubled",
    "engineered", "enhanced", "established", "executed", "expanded", "expedited",
    "founded", "generated", "guided", "headed", "implemented", "improved",
    "increased", "initiated", "installed", "integrated", "introduced", "launched",
    "led", "managed", "maximized", "mentored", "migrated", "minimized",
    "modernized", "negotiated", "optimized", "orchestrated", "overhauled",
    "pioneered", "reduced", "refactored", "resolved", "restructured", "revamped",
    "scaled", "simplified", "spearheaded", "standardized", "streamlined",
    "surpassed", "transformed", "unified", "upgraded", "yielded",
}

WEAK_PASSIVE_PHRASES = [
    "responsible for", "duties included", "helped to", "assisted with",
    "worked on", "participated in", "handled", "tasks involved",
    "attempted to", "tried to", "involved in", "helped with",
]

METRIC_PATTERNS = [
    re.compile(r"\b\d+(\.\d+)?%"),  # 45%, 12.5%
    re.compile(r"[\$€£₹]\s*\d+"),    # $50k, €1000
    re.compile(r"\b\d+x\b", re.IGNORECASE),  # 2x, 10x
    re.compile(r"\b\d+\s*(users|clients|customers|servers|endpoints|engineers|teams|downloads|requests|ms|seconds|min|hours|days|weeks|months|years|kb|mb|gb|tb)\b", re.IGNORECASE),
    re.compile(r"\b(10|[1-9]\d{1,})\b"),  # numbers 10 and above
]


def evaluate_resume_ats(
    content_dict: Dict[str, Any],
    style_dict: Optional[Dict[str, Any]] = None,
    job_description: Optional[str] = None,
) -> AtsAnalysisResponse:
    """Performs deep rule-based ATS analysis on resume content and styling,

    with optional JD keyword match scoring.
    """
    content = ResumeContent.model_validate(content_dict)

    checks: List[AtsCheckItem] = []
    total_bullets = 0
    bullets_with_metrics = 0
    strong_verbs = 0
    weak_verbs = 0
    bullet_char_lengths: List[int] = []

    # 1. Contact Information Checks
    header = content.header
    has_name = bool(header.name and len(header.name.strip()) >= 2)
    checks.append(AtsCheckItem(
        category="contact",
        name="Candidate Name",
        passed=has_name,
        severity="critical" if not has_name else "info",
        message="Full name is clearly provided at the top." if has_name else "Full candidate name is missing.",
        suggestion="Add your full first and last name to the resume header." if not has_name else None,
    ))

    email_pattern = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
    has_email = bool(header.email and re.search(email_pattern, header.email))
    checks.append(AtsCheckItem(
        category="contact",
        name="Email Address",
        passed=has_email,
        severity="critical" if not has_email else "info",
        message="Valid contact email is present." if has_email else "Missing or invalid email address.",
        suggestion="Add a professional personal email address (e.g., name@gmail.com)." if not has_email else None,
    ))

    digits = re.sub(r"\D", "", header.phone or "")
    has_phone = len(digits) >= 7
    checks.append(AtsCheckItem(
        category="contact",
        name="Phone Number",
        passed=has_phone,
        severity="warning" if not has_phone else "info",
        message="Contact phone number is present." if has_phone else "Missing or incomplete phone number.",
        suggestion="Add a phone number with country or area code for recruiter callbacks." if not has_phone else None,
    ))

    has_loc_or_links = bool(header.location or (header.links and len(header.links) > 0) or header.website)
    checks.append(AtsCheckItem(
        category="contact",
        name="Location & Professional Links",
        passed=has_loc_or_links,
        severity="warning" if not has_loc_or_links else "info",
        message="Location or portfolio links provided." if has_loc_or_links else "No location or professional links provided.",
        suggestion="Include your City, State and a LinkedIn or GitHub profile link." if not has_loc_or_links else None,
    ))

    # 2. Standard Section Headers
    section_types = {s.type for s in content.sections if s.visible}
    has_exp = "experience" in section_types
    has_edu = "education" in section_types
    has_skills = "skills" in section_types

    checks.append(AtsCheckItem(
        category="sections",
        name="Work Experience Section",
        passed=has_exp,
        severity="critical" if not has_exp else "info",
        message="Experience section is present and visible." if has_exp else "No Experience section found.",
        suggestion="ATS parsers prioritize work history; add an Experience section with job roles." if not has_exp else None,
    ))

    checks.append(AtsCheckItem(
        category="sections",
        name="Education Section",
        passed=has_edu,
        severity="warning" if not has_edu else "info",
        message="Education section is present." if has_edu else "No Education section found.",
        suggestion="Include your degrees, universities, or relevant certifications." if not has_edu else None,
    ))

    checks.append(AtsCheckItem(
        category="sections",
        name="Skills Section",
        passed=has_skills,
        severity="warning" if not has_skills else "info",
        message="Dedicated Skills section is present." if has_skills else "No dedicated Skills section found.",
        suggestion="Add a dedicated Skills section to help ATS match keywords quickly." if not has_skills else None,
    ))

    # 3. Bullet Density & Length Analysis
    exp_sections = [s for s in content.sections if s.type in ("experience", "projects") and s.visible]
    roles_with_zero_bullets = 0
    roles_with_excess_bullets = 0

    for sec in exp_sections:
        for item in sec.items:
            b_count = len(item.bullets) if item.bullets else 0
            if b_count == 0:
                roles_with_zero_bullets += 1
            elif b_count > 7:
                roles_with_excess_bullets += 1

            if item.bullets:
                for b in item.bullets:
                    text = b.text.strip()
                    if not text:
                        continue
                    total_bullets += 1
                    bullet_char_lengths.append(len(text))

                    # Check quantifiable metrics
                    has_metric = any(pat.search(text) for pat in METRIC_PATTERNS)
                    if has_metric:
                        bullets_with_metrics += 1

                    # Check action verbs
                    first_word = text.split()[0].lower().rstrip(",.:;") if text.split() else ""
                    if first_word in STRONG_ACTION_VERBS:
                        strong_verbs += 1

                    # Check weak phrases
                    text_lower = text.lower()
                    for weak in WEAK_PASSIVE_PHRASES:
                        if weak in text_lower:
                            weak_verbs += 1
                            break

    density_passed = (roles_with_zero_bullets == 0 and roles_with_excess_bullets == 0)
    checks.append(AtsCheckItem(
        category="bullets",
        name="Bullet Point Count Per Role",
        passed=density_passed,
        severity="warning" if not density_passed else "info",
        message="Optimal bullet density (1 to 7 bullets per role)." if density_passed else f"Found {roles_with_zero_bullets} roles without bullets, and {roles_with_excess_bullets} roles with >7 bullets.",
        suggestion="Keep 3-6 punchy accomplishment bullets per role to maximize recruiter attention." if not density_passed else None,
    ))

    # 4. Action Verbs Check
    verb_ratio = (strong_verbs / total_bullets) if total_bullets > 0 else 0.0
    verbs_passed = (verb_ratio >= 0.5) and (weak_verbs <= 2)
    checks.append(AtsCheckItem(
        category="verbs",
        name="Action Verbs & Active Voice",
        passed=verbs_passed,
        severity="warning" if not verbs_passed else "info",
        message=f"{strong_verbs} bullets start with strong active verbs ({int(verb_ratio * 100)}%)." if verbs_passed else f"Only {int(verb_ratio * 100)}% of bullets begin with strong action verbs. Found {weak_verbs} passive phrases.",
        suggestion="Replace passive phrases like 'worked on' or 'responsible for' with verbs like 'Architected', 'Spearheaded', or 'Delivered'." if not verbs_passed else None,
    ))

    # 5. Quantifiable Metrics Check
    metric_ratio = (bullets_with_metrics / total_bullets) if total_bullets > 0 else 0.0
    metrics_passed = metric_ratio >= 0.35
    checks.append(AtsCheckItem(
        category="metrics",
        name="Quantifiable Impact & Metrics",
        passed=metrics_passed,
        severity="warning" if not metrics_passed else "info",
        message=f"{bullets_with_metrics} of {total_bullets} bullets ({int(metric_ratio * 100)}%) include quantifiable results." if metrics_passed else f"Only {int(metric_ratio * 100)}% of bullets contain numbers or percentages (target: >= 35%).",
        suggestion="Add metrics such as percentage improvements, team sizes, dollar savings, or throughput numbers." if not metrics_passed else None,
    ))

    # 6. Date Formatting Consistency Check
    date_formats_found: List[str] = []
    for sec in content.sections:
        for item in sec.items:
            if item.dateRange and item.dateRange.strip():
                dr = item.dateRange.strip()
                if re.search(r"\d{4}\s*-\s*(\d{4}|present)", dr, re.IGNORECASE):
                    date_formats_found.append("year_range")
                elif re.search(r"[a-zA-Z]{3}\s*\d{4}", dr):
                    date_formats_found.append("month_year")

    consistent_dates = len(set(date_formats_found)) <= 1
    checks.append(AtsCheckItem(
        category="dates",
        name="Date Consistency",
        passed=consistent_dates,
        severity="info" if consistent_dates else "warning",
        message="Date formats are consistent across sections." if consistent_dates else "Mixed date formatting detected across roles.",
        suggestion="Use a single consistent format such as '2021 - Present' or 'Jan 2021 - Present' for all entries." if not consistent_dates else None,
    ))

    # 7. Typography / Style Checks (if style provided)
    if style_dict:
        typography = style_dict.get("typography", {})
        body_size = typography.get("fontSize", {}).get("body", 10.0)
        font_family = typography.get("fontFamily", {}).get("base", "Inter")
        safe_fonts = {"inter", "roboto", "montserrat", "liberation sans", "liberation serif", "merriweather", "cinzel", "system-ui", "sans-serif"}
        font_is_safe = any(f in font_family.lower() for f in safe_fonts)

        checks.append(AtsCheckItem(
            category="typography",
            name="ATS-Friendly Font & Sizing",
            passed=font_is_safe and (8.5 <= body_size <= 12.5),
            severity="info",
            message=f"Clean, readable font ({font_family}, {body_size}pt).",
            suggestion=None if font_is_safe else "Use standard open fonts like Inter, Roboto, or Liberation Sans for high ATS OCR accuracy.",
        ))

    # Calculate overall score (0 - 100)
    passed_count = sum(1 for c in checks if c.passed)
    total_checks = len(checks)
    base_score = int((passed_count / total_checks) * 100) if total_checks > 0 else 80

    jd_match_result: Optional[MatchScore] = None
    final_score = base_score

    if job_description and job_description.strip():
        jd_analysis = analyze_job_description_sync(job_description)
        jd_match_result = calculate_match_score(content, jd_analysis)
        # 60% rule checks, 40% JD keyword match
        final_score = int(base_score * 0.6 + jd_match_result.total_score * 0.4)

    # Determine letter grade
    if final_score >= 90:
        grade = "A+"
    elif final_score >= 80:
        grade = "A"
    elif final_score >= 70:
        grade = "B"
    elif final_score >= 60:
        grade = "C"
    else:
        grade = "Needs Improvement"

    summary_msg = f"Your resume achieved an ATS readiness score of {final_score}/100 ({grade})."
    if jd_match_result:
        summary_msg += f" Target JD keyword alignment is {jd_match_result.total_score}%."

    avg_chars = (sum(bullet_char_lengths) / len(bullet_char_lengths)) if bullet_char_lengths else 0.0

    stats = AtsStats(
        total_bullets=total_bullets,
        bullets_with_metrics=bullets_with_metrics,
        metrics_percentage=round((bullets_with_metrics / total_bullets * 100), 1) if total_bullets > 0 else 0.0,
        strong_verbs_count=strong_verbs,
        weak_verbs_count=weak_verbs,
        average_bullet_chars=round(avg_chars, 1),
    )

    return AtsAnalysisResponse(
        overall_score=final_score,
        grade=grade,
        summary=summary_msg,
        checks=checks,
        stats=stats,
        jd_match=jd_match_result,
    )
