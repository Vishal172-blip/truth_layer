from __future__ import annotations

import logging
import sys
import os
import traceback

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from llm.llm_client import LLMClient

from schemas import Claim, Evidence, Verdict
from config import VERDICT_VERIFIED, VERDICT_INACCURATE, VERDICT_FALSE
from llm.prompts import VERDICT_PROMPT, build_verdict_user_prompt
from utils.logger import get_logger

logger = get_logger(__name__)

_VALID_LABELS = {VERDICT_VERIFIED, VERDICT_INACCURATE, VERDICT_FALSE}


class VerdictEngine:
    def __init__(self, llm_client: "LLMClient") -> None:
        self._llm_client = llm_client

    def judge(self, claim: Claim, evidence: list[Evidence]) -> Verdict:
        if not evidence:
            return Verdict(
                claim=claim,
                label=VERDICT_FALSE,
                real_value="No evidence found",
                explanation="No web sources could be found to verify this claim.",
                confidence=0.1,
                sources=[],
            )

        try:
            user_prompt = build_verdict_user_prompt(claim, evidence)
            response: dict = self._llm_client.chat_json(
                system=VERDICT_PROMPT,
                user=user_prompt,
                tier="reasoning",
            )

            raw_label = response.get("label", "")
            label = raw_label if raw_label in _VALID_LABELS else VERDICT_FALSE

            real_value = response.get("real_value") or ""

            raw_explanation = response.get("explanation", "")
            explanation = str(raw_explanation) if raw_explanation else "No explanation provided."

            raw_confidence = response.get("confidence", 0.5)
            try:
                confidence = max(0.0, min(1.0, float(raw_confidence)))
            except (TypeError, ValueError):
                confidence = 0.5

            raw_sources = response.get("sources")
            if isinstance(raw_sources, list) and all(isinstance(s, str) for s in raw_sources):
                sources = raw_sources
            else:
                sources = [ev.url for ev in evidence if ev.url]

            return Verdict(
                claim=claim,
                label=label,
                real_value=real_value,
                explanation=explanation,
                confidence=confidence,
                sources=sources,
            )

        except Exception as exc:
            # Surface the real root cause loudly — do NOT silently swallow it.
            # Full traceback goes to the terminal (stderr) and the configured logger
            # so the actual provider/parse error is always visible during debugging.
            logger.error(
                "VerdictEngine.judge() failed for claim %d (%s: %s)",
                claim.id,
                type(exc).__name__,
                exc,
                exc_info=True,
            )
            traceback.print_exc()

            return Verdict(
                claim=claim,
                label=VERDICT_FALSE,
                real_value="",
                explanation=(
                    f"Could not verify this claim — the verification service errored "
                    f"({type(exc).__name__}: {exc})."
                ),
                confidence=0.0,
                sources=[ev.url for ev in evidence if ev.url],
            )


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(name)s: %(message)s")

    sample_claim = Claim(
        id=1,
        text="The Eiffel Tower is 330 meters tall.",
        claim_type="stat",
        page_number=3,
    )
    sample_evidence = [
        Evidence(
            title="Eiffel Tower - Wikipedia",
            snippet="The Eiffel Tower stands at 330 metres (1,083 ft) tall.",
            url="https://en.wikipedia.org/wiki/Eiffel_Tower",
        ),
        Evidence(
            title="Paris Tourist Guide",
            snippet="At 330 m, the Eiffel Tower is the tallest structure in Paris.",
            url="https://example.com/paris-guide",
        ),
    ]

    class _MockLLMClient:
        def chat_json(self, system: str, user: str, tier: str = "fast") -> dict:
            return {
                "label": VERDICT_VERIFIED,
                "real_value": "",
                "explanation": "Multiple sources confirm the Eiffel Tower is 330 metres tall.",
                "confidence": 0.95,
                "sources": ["https://en.wikipedia.org/wiki/Eiffel_Tower"],
            }

    engine = VerdictEngine(llm_client=_MockLLMClient())  # type: ignore[arg-type]

    verdict = engine.judge(sample_claim, sample_evidence)
    print("Normal verdict:")
    print(f"  label      : {verdict.label}")
    print(f"  real_value : {verdict.real_value!r}")
    print(f"  explanation: {verdict.explanation}")
    print(f"  confidence : {verdict.confidence}")
    print(f"  sources    : {verdict.sources}")

    print()
    no_ev_verdict = engine.judge(sample_claim, [])
    print("No-evidence verdict:")
    print(f"  label      : {no_ev_verdict.label}")
    print(f"  explanation: {no_ev_verdict.explanation}")
    print(f"  confidence : {no_ev_verdict.confidence}")
