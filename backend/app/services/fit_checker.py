import os
import fitz  # PyMuPDF
from typing import Dict, List, Tuple, Any, Optional
from app.schemas.content import ResumeContent


def check_pdf_fit_overflow(
    original_pdf_path: str,
    tailored_pdf_path: str,
    tailored_content: ResumeContent,
    original_content: ResumeContent,
) -> Tuple[bool, int, int, List[str], Dict[str, int]]:
    """Compares original vs tailored PDF page count and text layout using PyMuPDF.

    Returns:
    - fit_passed: bool (True if tailored page count <= original page count)
    - original_page_count: int
    - tailored_page_count: int
    - offending_bullet_ids: List[str]
    - stricter_budgets: Dict[str, int] (reduced character budgets for offending bullets)
    """
    if not os.path.exists(original_pdf_path) or not os.path.exists(tailored_pdf_path):
        return True, 1, 1, [], {}

    doc_orig = fitz.open(original_pdf_path)
    doc_tailored = fitz.open(tailored_pdf_path)

    orig_pages = len(doc_orig)
    tailored_pages = len(doc_tailored)

    doc_orig.close()
    doc_tailored.close()

    # If page count did not increase, document fits perfectly!
    if tailored_pages <= orig_pages:
        return True, orig_pages, tailored_pages, [], {}

    # Overflow detected! Locate bullets that grew in character count
    offending_bullet_ids: List[str] = []
    stricter_budgets: Dict[str, int] = {}

    orig_bullet_texts = {}
    for s in original_content.sections:
        for item in s.items:
            for b in item.bullets:
                orig_bullet_texts[b.id] = b.text

    for s in tailored_content.sections:
        for item in s.items:
            for b in item.bullets:
                orig_txt = orig_bullet_texts.get(b.id, "")
                if len(b.text) > len(orig_txt):
                    offending_bullet_ids.append(b.id)
                    # Reduce budget by 15% below original length to enforce compression
                    target_len = max(30, int(len(orig_txt) * 0.85))
                    stricter_budgets[b.id] = target_len

    # If no bullet grew longer than original, pick the longest bullets in experience
    if not offending_bullet_ids:
        for s in tailored_content.sections:
            if s.type == "experience":
                for item in s.items:
                    for b in item.bullets:
                        offending_bullet_ids.append(b.id)
                        stricter_budgets[b.id] = max(30, int(len(b.text) * 0.85))

    return False, orig_pages, tailored_pages, offending_bullet_ids, stricter_budgets
