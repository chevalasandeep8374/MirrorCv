from app.schemas.tailoring import JDAnalysis
from app.services.llm_client import call_llm_structured


def analyze_job_description(jd_text: str) -> JDAnalysis:
    """Extracts structured seniority, required skills, preferred skills, tools, and keywords

    from the raw job description using structured LLM output.
    """
    if not jd_text or not jd_text.strip():
        raise ValueError("Job description text cannot be empty.")

    system_prompt = (
        "You are an expert technical recruiter and resume analyzer. Analyze the job description "
        "and extract seniority, required skills, preferred skills, tools, responsibilities, and keywords. "
        "Return structured JSON matching the JDAnalysis schema."
    )

    user_prompt = f"Analyze the following job description:\n\n---\n{jd_text}\n---"

    return call_llm_structured(
        prompt=user_prompt,
        response_model=JDAnalysis,
        system_prompt=system_prompt,
    )
