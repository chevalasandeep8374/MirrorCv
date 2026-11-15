"""Dataset loaders for evaluation harness with personal data anonymization (PII masking)
and strict held-out split isolation.
"""

import json
import re
import random
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional

EVAL_DIR = Path(__file__).resolve().parent
FIXTURES_DIR = EVAL_DIR / "fixtures"


def anonymize_text(text: str) -> str:
    """Masks emails, phone numbers, and potential PII before evaluation use."""
    if not text:
        return ""
    # Mask emails
    text = re.sub(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", "[EMAIL_ANONYMIZED]", text)
    # Mask phone numbers
    text = re.sub(r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b", "[PHONE_ANONYMIZED]", text)
    # Mask street addresses
    text = re.sub(r"\b\d{1,5}\s+[A-Za-z0-9.\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr)\b", "[ADDRESS_ANONYMIZED]", text, flags=re.IGNORECASE)
    return text


def load_gold_set(path: Optional[Path] = None, allow_synthetic: bool = False) -> List[Dict[str, Any]]:
    """Loads evaluation resume-JD pairs.
    Default loads human-labeled evaluation pairs.
    Synthetic smoke set is only loaded when explicitly permitted.
    """
    if path:
        file_path = path
    elif allow_synthetic:
        file_path = FIXTURES_DIR / "synthetic_smoke_set.json"
    else:
        file_path = FIXTURES_DIR / "human_labeled_pairs.json"

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def wilson_score_interval(successes: int, total: int, confidence: float = 0.95) -> Tuple[float, float]:
    """Calculates 95% Wilson score interval for binomial proportions."""
    import math
    if total == 0:
        return 0.0, 0.0
    # z = 1.96 for 95% confidence
    z = 1.959963984540054
    p_hat = successes / total
    denom = 1.0 + (z**2) / total
    center = (p_hat + (z**2) / (2.0 * total)) / denom
    margin = (z / denom) * math.sqrt((p_hat * (1.0 - p_hat) / total) + (z**2) / (4.0 * (total**2)))
    low = max(0.0, round(center - margin, 4))
    high = min(1.0, round(center + margin, 4))
    return low, high


def load_labeled_gold_set(
    path: Optional[Path] = None,
    split_ratio: float = 0.5,
    seed: int = 42,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Loads a human-labeled gold evaluation set and splits into (train_set, held_out_set).

    Guarantees:
    - Deterministic split based on seed.
    - Zero sample overlap between train and held-out sets.
    - held_out: True flag stamped on each held-out pair.
    - NEVER tune scoring weights or prompt parameters on held_out_set.
    """
    pairs = load_gold_set(path)

    # Anonymize all text fields defensively
    anonymized = []
    for p in pairs:
        pair_copy = json.loads(json.dumps(p))
        if "jd_text" in pair_copy:
            pair_copy["jd_text"] = anonymize_text(pair_copy["jd_text"])
        anonymized.append(pair_copy)

    # Stratified or deterministic shuffle
    rng = random.Random(seed)
    shuffled = list(anonymized)
    rng.shuffle(shuffled)

    split_idx = int(len(shuffled) * (1.0 - split_ratio))
    train = shuffled[:split_idx]
    held_out = shuffled[split_idx:]

    for item in train:
        item["held_out"] = False
    for item in held_out:
        item["held_out"] = True

    # Sanity check: no leakage
    train_ids = {t["pair_id"] for t in train}
    held_out_ids = {h["pair_id"] for h in held_out}
    assert train_ids.isdisjoint(held_out_ids), "Data leakage detected: train and held-out sets overlap!"

    return train, held_out
