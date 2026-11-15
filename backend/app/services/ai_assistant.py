import difflib
from typing import Optional, List
from app.services.llm_client import call_llm_structured
from app.schemas.ai import (
    BulletActionRequest,
    BulletActionResponse,
    SummaryGenerateRequest,
    SummaryGenerateResponse,
    SkillsSuggestRequest,
    SkillsSuggestResponse,
)


def compute_text_diff(old_text: str, new_text: str) -> str:
    """Computes a clean unified-style diff between old and new text."""
    matcher = difflib.ndiff(old_text.splitlines(keepends=True), new_text.splitlines(keepends=True))
    diff_lines = list(matcher)
    if not diff_lines or old_text == new_text:
        return "No changes"
    return "".join(diff_lines).strip()


def run_bullet_action(req: BulletActionRequest) -> BulletActionResponse:
    """Executes a bullet action with strict anti-hallucination rules."""
    system_prompt = (
        "You are an expert executive resume editor and career strategist.\n"
        "RULES:\n"
        "1. DO NOT invent employers, dates, metrics, percentages, or dollar amounts.\n"
        "2. If the user requested 'add_impact' and provided a metric in METRIC_ANSWER, incorporate it naturally.\n"
        "3. If the user requested 'add_impact' but did NOT provide a metric, ask a clarifying question in 'clarification_needed'.\n"
        "4. Keep the bullet concise, active, and impact-driven using strong past-tense action verbs.\n"
        "5. Output valid JSON matching the schema."
    )

    user_prompt = (
        f"ORIGINAL: {req.text}\n"
        f"ACTION: {req.action}\n"
        f"TONE: {req.tone}\n"
        f"CONTEXT: {req.context or 'None'}\n"
        f"METRIC_ANSWER: {req.metric_answer or 'None'}\n"
    )

    resp = call_llm_structured(
        prompt=user_prompt,
        response_model=BulletActionResponse,
        system_prompt=system_prompt,
    )
    resp.original_text = req.text
    resp.diff_summary = compute_text_diff(req.text, resp.suggested_text)
    return resp


def run_generate_summary(req: SummaryGenerateRequest) -> SummaryGenerateResponse:
    """Generates an executive resume summary grounded strictly in provided bullets."""
    system_prompt = (
        "You are a professional resume writer.\n"
        "RULES:\n"
        "1. Generate a compelling 3-4 sentence professional summary.\n"
        "2. Ground every sentence strictly in the provided experience highlights and skills.\n"
        "3. NEVER invent companies, years of experience not implied by content, or unverifiable claims.\n"
        "4. Output valid JSON matching the schema."
    )

    highlights_str = "\n".join(f"- {b}" for b in req.experience_bullets) if req.experience_bullets else "None provided"
    skills_str = ", ".join(req.skills) if req.skills else "None provided"

    user_prompt = (
        f"JOB_TITLE: {req.job_title or 'Senior Professional'}\n"
        f"TONE: {req.tone or 'formal'}\n"
        f"EXPERIENCE HIGHLIGHTS:\n{highlights_str}\n"
        f"SKILLS:\n{skills_str}\n"
    )

    return call_llm_structured(
        prompt=user_prompt,
        response_model=SummaryGenerateResponse,
        system_prompt=system_prompt,
    )


def run_suggest_skills(req: SkillsSuggestRequest) -> SkillsSuggestResponse:
    """Extracts candidate skills from experience texts without inventing ones not evidenced."""
    system_prompt = (
        "You are an ATS optimization and technical skills analyzer.\n"
        "RULES:\n"
        "1. Extract skills, technologies, frameworks, and tools directly mentioned or strongly evidenced in the text.\n"
        "2. Do not invent skills that have no basis in the text.\n"
        "3. Exclude any skills already in the EXISTING_SKILLS list.\n"
        "4. Categorize each suggested skill and provide brief source context.\n"
        "5. Output valid JSON matching the schema."
    )

    texts_str = "\n".join(f"- {t}" for t in req.experience_texts)
    existing_str = ", ".join(req.existing_skills) if req.existing_skills else "None"

    user_prompt = (
        f"EXISTING_SKILLS: {existing_str}\n"
        f"EXPERIENCE_TEXTS:\n{texts_str}\n"
    )

    return call_llm_structured(
        prompt=user_prompt,
        response_model=SkillsSuggestResponse,
        system_prompt=system_prompt,
    )
