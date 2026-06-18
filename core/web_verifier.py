from __future__ import annotations

import logging
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from search.search_client import SearchClient

from schemas import Claim, Evidence
from config import MAX_SEARCH_RESULTS_PER_CLAIM
from utils.text_utils import build_search_query

logger = logging.getLogger(__name__)


class WebVerifier:
    def __init__(self, search_client: "SearchClient") -> None:
        self._search_client = search_client

    def gather_evidence(self, claim: Claim) -> list[Evidence]:
        query = build_search_query(claim.text)

        try:
            raw_results: list[dict] = self._search_client.search(query)
        except Exception as exc:
            logger.error("Search failed for claim %d (%r): %s", claim.id, query, exc)
            return []

        evidence: list[Evidence] = []
        for result in raw_results:
            title = result.get("title", "")
            snippet = result.get("snippet", "")
            url = result.get("url", "")

            if not snippet:
                continue

            evidence.append(Evidence(title=title, snippet=snippet, url=url))

        return evidence[:MAX_SEARCH_RESULTS_PER_CLAIM]


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    class _MockSearchClient:
        def search(self, query: str) -> list[dict]:
            print(f"Mock search called with query: {query!r}")
            return [
                {
                    "title": "India Population Census 2011",
                    "snippet": "According to the 2011 census, India's population was 1.21 billion.",
                    "url": "https://example.com/india-census-2011",
                },
                {
                    "title": "World Bank: India Demographics",
                    "snippet": "India had approximately 1.2 billion people as of 2011.",
                    "url": "https://example.com/worldbank-india",
                },
            ]

    sample_claim = Claim(
        id=1,
        text="The population of India was 1.2 billion in 2011",
        claim_type="stat",
        page_number=3,
    )

    verifier = WebVerifier(search_client=_MockSearchClient())  # type: ignore[arg-type]
    results = verifier.gather_evidence(sample_claim)

    print(f"\nGathered {len(results)} evidence item(s):")
    for ev in results:
        print(f"  {ev}")
