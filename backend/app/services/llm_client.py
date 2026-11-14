import os
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
        candidates = ["python", "fastapi", "typescript", "react", "next.js", "docker", "kubernetes", "aws", "postgresql", "redis", "microservices", "graphql", "playwright"]
        for c in candidates:
            if c in p_lower:
                skills.append(c.title() if c != "next.js" else "Next.js")

        seniority = "Staff" if "staff" in p_lower else ("Senior" if "senior" in p_lower else "Lead")
        return response_model(
            job_title="Senior Software Engineer",
            seniority=seniority,
            required_skills=skills[:6] if skills else ["Python", "FastAPI", "TypeScript", "PostgreSQL"],
            preferred_skills=skills[6:10] if len(skills) > 6 else ["Docker", "Kubernetes", "AWS"],
            tools_and_tech=skills,
            responsibilities=[
                "Architect and scale distributed web services and document processing pipelines.",
                "Collaborate with cross-functional product and engineering teams.",
            ],
            keywords=[s.lower() for s in skills],
            domain="Cloud SaaS / Systems Architecture",
        )

    # For other models, construct default model
    return response_model.model_validate({})
