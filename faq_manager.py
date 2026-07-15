"""
faq_manager.py

Handles all access to FAQ data.

FR-06: FAQs stored in a JSON file (Version 1).
NFR (Scalability): All FAQ access goes through this class. To migrate to a
real database later (e.g. SQLite/Postgres), you only need to rewrite the
methods in this file — nothing else in the codebase touches faqs.json
directly.
"""

import json
import os
from typing import List, Dict


class FAQManager:
    def __init__(self, filepath: str = "data/faqs.json"):
        self.filepath = filepath
        self._faqs: List[Dict] = []
        self.load()

    def load(self) -> None:
        """Load FAQs from the JSON file into memory."""
        if not os.path.exists(self.filepath):
            self._faqs = []
            return

        with open(self.filepath, "r", encoding="utf-8") as f:
            self._faqs = json.load(f)

    def save(self) -> None:
        """Persist the in-memory FAQ list back to the JSON file."""
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(self._faqs, f, ensure_ascii=False, indent=2)

    def get_all(self) -> List[Dict]:
        """Return all stored FAQs."""
        return self._faqs

    def add_faq(self, question: str, answer: str, category: str = "") -> None:
        """Add a new FAQ and persist it. Used by future admin commands."""
        self._faqs.append({
            "question": question.strip().lower(),
            "answer": answer.strip(),
            "category": category.strip(),
        })
        self.save()

    def delete_faq(self, index: int) -> bool:
        """Delete an FAQ by its position in the list. Returns True on success."""
        if 0 <= index < len(self._faqs):
            del self._faqs[index]
            self.save()
            return True
        return False
