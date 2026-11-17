"""Migration service re-exporting canonical normalizer from contracts."""

from contracts.normalizer import normalize_resume_tokens, format_structured_date

__all__ = ["normalize_resume_tokens", "format_structured_date"]
