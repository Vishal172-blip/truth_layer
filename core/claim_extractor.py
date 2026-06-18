from __future__ import annotations

import logging
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from llm.llm_client import LLMClient

from schemas import Claim
from config import MAX_CLAIMS_TO_PROCESS
from llm.prompts import CLAIM_EXTRACTION_PROMPT, build_claim_extraction_user_prompt

logger = logging.getLogger(__name__)

_VALID_CLAIM_TYPES = {"stat", "date", "financial", "technical"}


class ClaimExtractionError(Exception):
    """Raised when claim extraction fails due to an LLM or parsing error."""


class ClaimExtractor:
    def __init__(self, llm_client: "LLMClient") -> None:
        self._llm_client = llm_client

    _MAX_TEXT_CHARS = 12_000

    def extract_claims(self, text: str, page_count: int) -> list[Claim]:
        text = text[: self._MAX_TEXT_CHARS]
        user_prompt = build_claim_extraction_user_prompt(text, page_count)

        try:
            response = self._llm_client.chat_json(
                system=CLAIM_EXTRACTION_PROMPT,
                user=user_prompt,
                tier="fast",
            )
        except Exception as exc:
            raise ClaimExtractionError(f"Claim extraction failed: {exc}") from exc

        if isinstance(response, dict):
            raw_list = response.get("claims", [])
            if not isinstance(raw_list, list):
                raw_list = []
        elif isinstance(response, list):
            raw_list = response
        else:
            raw_list = []

        claims: list[Claim] = []
        for item in raw_list:
            if not isinstance(item, dict):
                continue

            text_val = item.get("text", "")
            if not isinstance(text_val, str) or len(text_val) < 10:
                continue

            raw_type = item.get("claim_type", "stat")
            claim_type = raw_type if raw_type in _VALID_CLAIM_TYPES else "stat"

            try:
                claim_id = int(item.get("id", 0))
            except (TypeError, ValueError):
                claim_id = 0

            try:
                page_number = int(item.get("page", 1))
            except (TypeError, ValueError):
                page_number = 1

            claims.append(
                Claim(
                    id=claim_id,
                    text=text_val,
                    claim_type=claim_type,  # type: ignore[arg-type]
                    page_number=page_number,
                )
            )

        return claims[:MAX_CLAIMS_TO_PROCESS]


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    sample_claim = Claim(
        id=1,
        text="Revenue grew by 43% year-over-year in Q2 2024.",
        claim_type="stat",
        page_number=2,
    )
    print("Sample Claim dataclass:")
    print(sample_claim)

    class _MockLLMClient:
        def chat_json(self, system, user, tier="fast"):
            return [
                {
                    "id": 1,
                    "text": "Revenue grew by 43% year-over-year in Q2 2024.",
                    "claim_type": "stat",
                    "page": 2,
                },
                {
                    "id": 2,
                    "text": "The company raised $2.4 billion in Series D funding.",
                    "claim_type": "financial",
                    "page": 4,
                },
            ]

    extractor = ClaimExtractor(llm_client=_MockLLMClient())  # type: ignore[arg-type]
    results = extractor.extract_claims(text="Sample document text.", page_count=5)
    print(f"\nExtracted {len(results)} claim(s):")
    for c in results:
        print(f"  {c}")
