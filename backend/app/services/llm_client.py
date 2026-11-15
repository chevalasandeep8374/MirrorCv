import os
import re
import json
import logging
from typing import Type, TypeVar, Optional, Any
from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


def get_llm_provider() -> str:
    """Detects available LLM provider: gemini, openai, or stub."""
    provider = os.getenv("LLM_PROVIDER", "").lower()
    if provider in ("gemini", "openai", "stub"):
        return provider
    if os.getenv("GEMINI_API_KEY"):
        return "gemini"
    if os.getenv("OPENAI_API_KEY"):
        return "openai"
    return "stub"


def call_llm_structured(
    prompt: str,
    response_model: Type[T],
    system_prompt: str = "",
    retry_count: int = 1,
) -> T:
    """Calls configured LLM provider and parses structured output into a Pydantic model.

    Retries once on validation failure.
    """
    provider = get_llm_provider()
    logger.info(f"Invoking LLM structured call using provider: {provider}")

    last_error: Optional[Exception] = None

    for attempt in range(retry_count + 1):
        try:
            if provider == "openai" and os.getenv("OPENAI_API_KEY"):
                import openai
                client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                response = client.chat.completions.create(
                    model=os.getenv("OPENAI_MODEL", "gpt-4o"),
                    messages=[
                        {"role": "system", "content": f"{system_prompt}\nReturn strictly valid JSON matching this schema:\n{json.dumps(response_model.model_json_schema())}"},
                        {"role": "user", "content": prompt},
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.2,
                )
                raw_json = response.choices[0].message.content
                return response_model.model_validate_json(raw_json)

            elif provider == "gemini" and os.getenv("GEMINI_API_KEY"):
                import httpx
                api_key = os.getenv("GEMINI_API_KEY")
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
                payload = {
                    "contents": [{"parts": [{"text": f"{system_prompt}\n\nTask:\n{prompt}\n\nOutput strictly JSON conforming to: {json.dumps(response_model.model_json_schema())}"}]}],
                    "generationConfig": {"response_mime_type": "application/json"},
                }
                res = httpx.post(url, json=payload, timeout=40.0)
                res.raise_for_status()
                data = res.json()
                raw_json = data["candidates"][0]["content"]["parts"][0]["text"]
                return response_model.model_validate_json(raw_json)

            else:
                # Deterministic High-Quality Fallback Stub for testing and zero-key environments
                return _stub_structured_response(prompt, response_model)

        except (ValidationError, Exception) as exc:
            logger.warning(f"LLM call attempt {attempt + 1} failed with error: {exc}")
            last_error = exc
            if attempt < retry_count:
                prompt += f"\n\nCRITICAL FIX: Your previous response caused error: {str(exc)}. Fix all formatting and return strictly valid JSON."

    if last_error:
        raise last_error
    raise RuntimeError("LLM structured call failed all attempts.")


def _stub_structured_response(prompt: str, response_model: Type[T]) -> T:
    """Produces realistic, valid structured outputs matching response_model

    for offline tests and zero-dependency environments.
    """
    model_name = response_model.__name__

    if model_name == "JDAnalysis":
        # Extract keywords and skills from prompt text
        p_lower = prompt.lower()
        skills = []
        candidates = [
            "python", "fastapi", "django", "flask", "typescript", "javascript", "react", "next.js",
            "vue", "angular", "node", "express", "java", "spring", "rust", "c++", "go", "sql",
            "postgresql", "postgres", "mysql", "redis", "mongodb", "elasticsearch",
            "docker", "kubernetes", "aws", "gcp", "azure", "terraform", "ci/cd",
            "graphql", "rest", "microservices", "playwright", "jest", "pytest", "tailwind", "git"
        ]
        for c in candidates:
            if re.search(r"\b" + re.escape(c) + r"\b", p_lower):
                skills.append(c.title() if c not in ("next.js", "ci/cd", "c++") else ("Next.js" if c == "next.js" else ("CI/CD" if c == "ci/cd" else "C++")))

        seniority = "Staff" if "staff" in p_lower else ("Senior" if "senior" in p_lower else ("Junior" if "junior" in p_lower else "Mid"))
        sen_map = {"Intern": 0, "Junior": 1, "Mid": 2, "Senior": 3, "Staff": 4, "Lead": 4, "Director": 5}
        sen_level = sen_map.get(seniority, 3)
        req = skills[:min(4, len(skills))] if skills else ["Python", "FastAPI"]
        pref = skills[4:] if len(skills) > 4 else []

        # Calculate keyword weights
        weights = {}
        for s in req:
            weights[s.lower()] = 1.0
        for s in pref:
            weights[s.lower()] = 0.6

        return response_model(
            job_title="Senior Software Engineer",
            company="Tech Corp",
            seniority=seniority,
            seniority_level=sen_level,
            years_required=5.0 if sen_level >= 3 else 2.0,
            required_skills=req,
            preferred_skills=pref,
            tools_and_tech=skills,
            responsibilities=[
                "Architect and scale distributed web services and document processing pipelines.",
                "Collaborate with cross-functional product and engineering teams.",
            ],
            keywords=[s.lower() for s in skills],
            weighted_keywords=weights,
            education_requirements=["Bachelor's degree in Computer Science or equivalent practical experience"],
            soft_skills=["Communication", "Leadership", "Problem Solving"],
            domain="Cloud SaaS / Systems Architecture",
        )

    if model_name == "BulletActionResponse":
        p_lower = prompt.lower()
        orig = ""
        action = "improve"
        # parse original text from prompt
        for line in prompt.split("\n"):
            if line.startswith("ORIGINAL:"):
                orig = line.replace("ORIGINAL:", "").strip()
            if line.startswith("ACTION:"):
                action = line.replace("ACTION:", "").strip()

        suggested = orig
        clarification = None

        if "add_impact" in action:
            if "METRIC_ANSWER:" in prompt and prompt.split("METRIC_ANSWER:")[1].strip() not in ("", "None"):
                metric = prompt.split("METRIC_ANSWER:")[1].strip()
                suggested = f"{orig.rstrip('.')} resulting in {metric}."
            else:
                clarification = "What metric or quantifiable outcome did you achieve (e.g. 35% latency drop, 10,000 active users, $40k cloud cost reduction)?"
                suggested = f"{orig} [Requires metric - e.g., reduced processing time by X%]"
        elif "shorten" in action:
            # Drop filler words
            words = orig.split()
            filtered = [w for w in words if w.lower() not in ("responsible", "for", "helped", "assisted", "in", "order", "to", "very", "actively")]
            suggested = " ".join(filtered)
            if not suggested.endswith("."):
                suggested += "."
        elif "fix_grammar" in action:
            suggested = orig.strip()
            if suggested and not suggested[0].isupper():
                suggested = suggested[0].upper() + suggested[1:]
            if not suggested.endswith("."):
                suggested += "."
        elif "change_tone" in action:
            if "executive" in prompt.lower():
                suggested = f"Spearheaded initiatives to {orig.lower().rstrip('.')} across key enterprise accounts."
            elif "technical" in prompt.lower():
                suggested = f"Architected high-throughput components to {orig.lower().rstrip('.')} with zero downtime."
            else:
                suggested = f"Led project delivery to {orig.lower().rstrip('.')}."
        else: # improve
            if orig.lower().startswith("worked on") or orig.lower().startswith("did"):
                suggested = f"Engineered and deployed scalable solutions for {orig[7:].strip().rstrip('.')}."
            elif orig.lower().startswith("helped"):
                suggested = f"Collaborated cross-functionally to drive {orig[6:].strip().rstrip('.')}."
            else:
                suggested = f"Optimized and executed {orig.rstrip('.')} with high efficiency."

        diff = f"- {orig}\n+ {suggested}"
        return response_model(
            original_text=orig,
            suggested_text=suggested,
            diff_summary=diff,
            clarification_needed=clarification,
            action=action,
            tokens_used=64,
            estimated_cost=0.0003,
        )

    if model_name == "SummaryGenerateResponse":
        job = "Full Stack Software Engineer"
        for line in prompt.split("\n"):
            if "JOB_TITLE:" in line:
                val = line.replace("JOB_TITLE:", "").strip()
                if val:
                    job = val
        summary = (
            f"Accomplished {job} with a proven track record of designing resilient architectures, "
            f"optimizing distributed systems, and leading high-velocity engineering deliverables. "
            f"Passionate about modern cloud technologies, code quality, and driving measurable product growth."
        )
        return response_model(
            suggested_summary=summary,
            key_themes=["System Architecture", "High Velocity Delivery", "Full Stack Development"],
            tokens_used=120,
            estimated_cost=0.0006,
        )

    if model_name == "SkillsSuggestResponse":
        # Extract keywords from prompt
        p_lower = prompt.lower()
        candidates = [
            ("Python", "Languages"),
            ("TypeScript", "Languages"),
            ("FastAPI", "Frameworks"),
            ("React", "Frameworks"),
            ("Next.js", "Frameworks"),
            ("PostgreSQL", "Databases"),
            ("Docker", "DevOps & Cloud"),
            ("Kubernetes", "DevOps & Cloud"),
            ("AWS", "DevOps & Cloud"),
            ("Playwright", "Testing"),
            ("Redis", "Databases"),
            ("GraphQL", "APIs & Protocols"),
        ]
        items = []
        for name, cat in candidates:
            if name.lower() in p_lower:
                items.append({
                    "skill": name,
                    "category": cat,
                    "source_context": f"Mentioned in project experience related to {name}."
                })
        if not items:
            items = [
                {"skill": "TypeScript", "category": "Languages", "source_context": "Found in experience highlights."},
                {"skill": "Python", "category": "Languages", "source_context": "Found in backend systems development."},
                {"skill": "PostgreSQL", "category": "Databases", "source_context": "Found in database operations."},
            ]
        return response_model(
            suggestions=items,
            tokens_used=95,
            estimated_cost=0.00045,
        )

    if model_name == "RepairedBulletResponse":
        orig = ""
        for line in prompt.split("\n"):
            if "Original Bullet:" in line:
                orig = line.replace("Original Bullet:", "").strip()
        repaired = orig if orig else "Engineered resilient backend components."
        return response_model(repaired_text=repaired, explanation="Restored grounded source text to resolve rule violation")

    if model_name == "SummaryFromBulletsResponse":
        return response_model(
            summary_text="Accomplished Senior Software Engineer with proven experience developing Python APIs and PostgreSQL systems.",
            key_facts_used=["Python APIs", "PostgreSQL"],
        )

    if model_name == "EntailmentCheckResponse":
        claim = ""
        premise = ""
        if "<CLAIM>" in prompt and "</CLAIM>" in prompt:
            claim = prompt.split("<CLAIM>")[1].split("</CLAIM>")[0].lower()
        if "<PREMISE>" in prompt and "</PREMISE>" in prompt:
            premise = prompt.split("<PREMISE>")[1].split("</PREMISE>")[0].lower()

        # If claim is in premise, it is strictly entailed
        if claim.strip() and claim.strip() in premise:
            return response_model(is_entailed=True, confidence=0.99, reason="Claim is directly stated in premise.", exaggeration_detected=False)

        # Flag ungrounded elevation verbs or wild claims not in premise
        for w in ("spearhead", "architect", "ceo", "president"):
            if w in claim and w not in premise:
                return response_model(is_entailed=False, confidence=0.95, reason=f"Unsubstantiated claim '{w}' not in premise.", exaggeration_detected=True)

        if "exaggerat" in claim or "unsubstantiated" in claim:
            return response_model(is_entailed=False, confidence=0.95, reason="Exaggeration detected in claim.", exaggeration_detected=True)

        return response_model(is_entailed=True, confidence=0.98, reason="Claim strictly grounded in premise.", exaggeration_detected=False)

    # For other models, construct default model
    return response_model.model_validate({})
