"""
faq_matcher.py

FR-03: Compares the user's question against stored FAQs using fuzzy matching.

Uses RapidFuzz's token_set_ratio scorer. Unlike WRatio, this scorer ignores
word order and extra/missing words (e.g. "reset password" vs "how do i
reset my password"), which matters a lot for short FAQ-style phrases where
several stored questions can share a common prefix like "how do i ...".
"""

from typing import List, Dict, Optional
from rapidfuzz import process, fuzz

# Minimum similarity score (0-100) required to consider a match "good enough".
# Tuned conservatively to avoid FR-05 false negatives turning into wrong answers.
MATCH_THRESHOLD = 60


def normalize(text: str) -> str:
    """
    FR-02: Normalize a message — lowercase and trim extra whitespace.
    """
    return " ".join(text.lower().strip().split())


def find_best_match(user_question: str, faqs: List[Dict]) -> Optional[Dict]:
    """
    FR-03/FR-04: Find the best matching FAQ for the user's question.

    Returns the matched FAQ dict if the similarity score is above
    MATCH_THRESHOLD, otherwise returns None (triggers FR-05 default reply).
    """
    if not faqs:
        return None

    normalized_question = normalize(user_question)
    choices = [faq["question"] for faq in faqs]

    result = process.extractOne(
        normalized_question,
        choices,
        scorer=fuzz.token_set_ratio,
        score_cutoff=MATCH_THRESHOLD,
    )

    if result is None:
        return None

    matched_text, score, index = result
    return faqs[index]
