from __future__ import annotations

import logging
import time
from datetime import datetime
from typing import Callable

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.logger import get_logger
from schemas import Claim, Verdict, Report
from config import (
    MAX_CLAIMS_TO_PROCESS,
    INTER_CLAIM_DELAY_SECONDS,
    VERDICT_VERIFIED,
    VERDICT_INACCURATE,
    VERDICT_FALSE,
    WEIGHT_VERIFIED,
    WEIGHT_INACCURATE,
    WEIGHT_FALSE,
)
from llm.llm_client import LLMClient
from search.search_client import SearchClient
from core.claim_extractor import ClaimExtractor, ClaimExtractionError
from core.web_verifier import WebVerifier
from core.verdict_engine import VerdictEngine
import core.pdf_extractor as pdf_extractor
from core.pdf_extractor import PDFExtractionError

logger = get_logger(__name__)

_MAX_CONSECUTIVE_FAILURES = 3
_BURST_PAUSE_SECONDS = 10


class FactCheckPipeline:
    def __init__(self) -> None:
        llm_client = LLMClient()
        search_client = SearchClient()

        self._claim_extractor = ClaimExtractor(llm_client=llm_client)
        self._web_verifier = WebVerifier(search_client=search_client)
        self._verdict_engine = VerdictEngine(llm_client=llm_client)

        logger.info(
            "FactCheckPipeline initialised — LLM primary: %s | Search primary: %s",
            llm_client.primary_name,
            search_client._primary,
        )

    # ------------------------------------------------------------------
    # Trust score helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _compute_trust_score(verdicts: list[Verdict]) -> float:
        if not verdicts:
            return 0.0
        weight_map = {
            VERDICT_VERIFIED: WEIGHT_VERIFIED,
            VERDICT_INACCURATE: WEIGHT_INACCURATE,
            VERDICT_FALSE: WEIGHT_FALSE,
        }
        total_weight = sum(weight_map.get(v.label, 0.0) for v in verdicts)
        score = (total_weight / len(verdicts)) * 100.0
        return round(score, 1)

    @staticmethod
    def _build_summary(verdicts: list[Verdict]) -> dict:
        counts = {VERDICT_VERIFIED: 0, VERDICT_INACCURATE: 0, VERDICT_FALSE: 0}
        for v in verdicts:
            if v.label in counts:
                counts[v.label] += 1
        trust_score = FactCheckPipeline._compute_trust_score(verdicts)
        return {
            "verified": counts[VERDICT_VERIFIED],
            "inaccurate": counts[VERDICT_INACCURATE],
            "false": counts[VERDICT_FALSE],
            "total": len(verdicts),
            "trust_score": trust_score,
        }

    # ------------------------------------------------------------------
    # Main entry point
    # ------------------------------------------------------------------

    def run_fact_check(
        self,
        pdf_bytes: bytes,
        filename: str,
        progress_callback: Callable[[int, int, Verdict], None] | None = None,
        extraction_callback: Callable[[int], None] | None = None,
    ) -> Report:
        # ---- Step 1: PDF Extraction ----
        # PDFExtractionError propagates to caller (app.py) intentionally
        text = pdf_extractor.extract_text(pdf_bytes)
        pages = pdf_extractor.extract_pages(pdf_bytes)
        page_count = len(pages)
        logger.info(
            "PDF extracted — %d page(s), %d characters | file: %s",
            page_count,
            len(text),
            filename,
        )

        # ---- Step 2: Claim Extraction ----
        try:
            claims: list[Claim] = self._claim_extractor.extract_claims(text, page_count)
        except ClaimExtractionError as exc:
            logger.error("Claim extraction failed: %s", exc)
            claims = []

        if not claims:
            logger.info("No verifiable claims found in %s", filename)
            return Report(
                verdicts=[],
                summary={
                    "verified": 0,
                    "inaccurate": 0,
                    "false": 0,
                    "total": 0,
                    "trust_score": 0.0,
                    "message": "No verifiable claims found in this document.",
                },
                filename=filename,
                timestamp=datetime.utcnow(),
            )

        claims = claims[:MAX_CLAIMS_TO_PROCESS]
        total = len(claims)
        logger.info("%d claim(s) extracted from %s", total, filename)

        if extraction_callback is not None:
            try:
                extraction_callback(total)
            except Exception as cb_exc:
                logger.warning("extraction_callback raised: %s", cb_exc)

        # ---- Step 3: Verification Loop ----
        verdicts: list[Verdict] = []
        failed_count = 0
        consecutive_failures = 0

        for idx, claim in enumerate(claims, start=1):
            logger.info(
                "Verifying claim %d/%d: %s...",
                idx,
                total,
                claim.text[:60],
            )
            try:
                evidence = self._web_verifier.gather_evidence(claim)
                verdict = self._verdict_engine.judge(claim, evidence)
                verdicts.append(verdict)
                consecutive_failures = 0

                if progress_callback is not None:
                    try:
                        progress_callback(idx, total, verdict)
                    except Exception as cb_exc:
                        logger.warning("progress_callback raised: %s", cb_exc)
            except Exception as exc:
                logger.error(
                    "Claim %d verification failed entirely — skipping. Error: %s",
                    claim.id,
                    exc,
                )
                failed_count += 1
                consecutive_failures += 1
                if consecutive_failures >= _MAX_CONSECUTIVE_FAILURES:
                    logger.warning(
                        "%d consecutive failures — pausing %ds to handle burst rate limits",
                        _MAX_CONSECUTIVE_FAILURES,
                        _BURST_PAUSE_SECONDS,
                    )
                    time.sleep(_BURST_PAUSE_SECONDS)
                    consecutive_failures = 0

            if idx < total:
                time.sleep(INTER_CLAIM_DELAY_SECONDS)

        if failed_count > total / 2:
            logger.warning(
                "%d of %d claims failed — something systemic may be wrong with the pipeline.",
                failed_count,
                total,
            )

        # ---- Step 4: Report Assembly ----
        summary = self._build_summary(verdicts)
        report = Report(
            verdicts=verdicts,
            summary=summary,
            filename=filename,
            timestamp=datetime.utcnow(),
        )
        logger.info(
            "Report assembled — trust score: %.1f%% | verified: %d | inaccurate: %d | false: %d",
            summary["trust_score"],
            summary["verified"],
            summary["inaccurate"],
            summary["false"],
        )
        return report


if __name__ == "__main__":
    import pathlib

    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(name)s | %(message)s")

    sample_path = pathlib.Path("assets/sample_trap.pdf")
    if not sample_path.exists():
        print("Place a sample PDF at assets/sample_trap.pdf to test")
    else:
        pdf_bytes = sample_path.read_bytes()
        pipeline = FactCheckPipeline()

        def _progress(idx: int, total: int, verdict: Verdict) -> None:
            print(f"  [{idx}/{total}] {verdict.label} — {verdict.claim.text[:50]}...")

        report = pipeline.run_fact_check(
            pdf_bytes=pdf_bytes,
            filename=sample_path.name,
            progress_callback=_progress,
        )
        print(f"\n{report}")
        print(f"Summary: {report.summary}")
