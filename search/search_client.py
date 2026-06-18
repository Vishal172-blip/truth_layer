from __future__ import annotations

import logging
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.logger import get_logger
from config import (
    TAVILY_API_KEY,
    TAVILY_SEARCH_DEPTH,
    TAVILY_MAX_RESULTS,
    MAX_SEARCH_RESULTS_PER_CLAIM,
    DDG_FALLBACK_ENABLED,
)

logger = get_logger(__name__)


class SearchClient:
    def __init__(self) -> None:
        self._tavily: object | None = None
        if TAVILY_API_KEY:
            try:
                from tavily import TavilyClient
                self._tavily = TavilyClient(api_key=TAVILY_API_KEY)
                self._primary = "tavily"
                logger.info("SearchClient: primary provider = Tavily")
            except Exception as exc:
                logger.warning("SearchClient: Tavily init failed (%s) — falling back to DDG", exc)
                self._tavily = None
                self._primary = "ddg"
        else:
            logger.warning("SearchClient: TAVILY_API_KEY not set — primary provider = DDG")
            self._primary = "ddg"

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _search_tavily(self, query: str) -> list[dict]:
        if self._tavily is None:
            return []
        try:
            response = self._tavily.search(  # type: ignore[attr-defined]
                query=query,
                search_depth=TAVILY_SEARCH_DEPTH,
                max_results=TAVILY_MAX_RESULTS,
            )
            raw = response.get("results", []) if isinstance(response, dict) else []
            return [
                {
                    "title": r.get("title", ""),
                    "snippet": r.get("content", ""),
                    "url": r.get("url", ""),
                }
                for r in raw
                if isinstance(r, dict)
            ]
        except Exception as exc:
            logger.error("Tavily search failed for query %r: %s", query, exc)
            return []

    def _search_ddg(self, query: str) -> list[dict]:
        try:
            from duckduckgo_search import DDGS
            results = DDGS().text(query, max_results=MAX_SEARCH_RESULTS_PER_CLAIM)
            return [
                {
                    "title": r.get("title", ""),
                    "snippet": r.get("body", ""),
                    "url": r.get("href", ""),
                }
                for r in (results or [])
                if isinstance(r, dict)
            ]
        except Exception as exc:
            logger.error("DDG search failed for query %r: %s", query, exc)
            return []

    @staticmethod
    def _clean(results: list[dict]) -> list[dict]:
        seen_urls: set[str] = set()
        cleaned: list[dict] = []
        for r in results:
            url = r.get("url", "")
            snippet = r.get("snippet", "")
            if not url or not url.startswith("http"):
                continue
            if len(snippet) < 20:
                continue
            if url in seen_urls:
                continue
            seen_urls.add(url)
            cleaned.append(r)
        return cleaned[:MAX_SEARCH_RESULTS_PER_CLAIM]

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def search(self, query: str) -> list[dict]:
        if self._primary == "tavily":
            results = self._search_tavily(query)
            if results:
                return self._clean(results)
            # Tavily returned nothing — fall through to DDG
            if DDG_FALLBACK_ENABLED:
                logger.info("Tavily returned no results for %r — trying DDG fallback", query)
                results = self._search_ddg(query)
        else:
            results = self._search_ddg(query)
            if not results and self._tavily is not None and DDG_FALLBACK_ENABLED:
                logger.info("DDG returned no results for %r — trying Tavily fallback", query)
                results = self._search_tavily(query)

        return self._clean(results)

    def search_with_fallback_query(
        self, primary_query: str, fallback_query: str
    ) -> list[dict]:
        results = self.search(primary_query)
        if len(results) < 2:
            logger.info(
                "Primary query %r returned < 2 results — trying fallback query %r",
                primary_query,
                fallback_query,
            )
            fallback_results = self.search(fallback_query)
            seen = {r["url"] for r in results}
            for r in fallback_results:
                if r["url"] not in seen:
                    results.append(r)
                    seen.add(r["url"])
        return results[:MAX_SEARCH_RESULTS_PER_CLAIM]


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(name)s | %(message)s")

    client = SearchClient()
    print(f"Primary provider: {client._primary}\n")

    query = "India GDP 2023"
    print(f"Searching for: {query!r}")
    results = client.search(query)
    print(f"Got {len(results)} result(s):")
    for i, r in enumerate(results, 1):
        print(f"  [{i}] {r['title']}")
        print(f"       URL    : {r['url']}")
        print(f"       Snippet: {r['snippet'][:100]}...")
        print()
