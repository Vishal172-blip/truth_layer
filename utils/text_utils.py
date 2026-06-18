from __future__ import annotations

import re

_FILLER_WORDS = {
    "the", "a", "an", "is", "was", "were", "are", "has", "have", "had",
    "that", "which", "this", "these", "those", "with", "from", "their",
    "its", "our", "your", "of", "in", "on", "at", "to", "by", "for",
    "and", "or", "but", "not", "be", "been", "being",
}


def build_search_query(claim_text: str) -> str:
    tokens = re.split(r"\s+", claim_text.strip())
    kept = [t for t in tokens if t.lower() not in _FILLER_WORDS]
    query = " ".join(kept).strip()
    if len(query) < 5:
        return claim_text[:120]
    return query


if __name__ == "__main__":
    examples = [
        "The population of India was 1.2 billion in 2011",
        "The company raised $2.4 billion in Series D funding in 2023",
        "Revenue grew by 43% year-over-year in Q2 2024",
        "The platform processed over 4.2 billion transactions in Q2 2024",
    ]
    for ex in examples:
        print(f"IN : {ex}")
        print(f"OUT: {build_search_query(ex)}")
        print()
