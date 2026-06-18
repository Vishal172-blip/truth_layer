from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal


@dataclass
class Claim:
    id: int
    text: str
    claim_type: Literal["stat", "date", "financial", "technical"]
    page_number: int

    def __str__(self) -> str:
        return f"Claim(id={self.id}, type={self.claim_type}, page={self.page_number}): {self.text[:80]}..."


@dataclass
class Evidence:
    title: str
    snippet: str
    url: str

    def __str__(self) -> str:
        return f"Evidence({self.title!r}): {self.snippet[:60]}... [{self.url}]"


@dataclass
class Verdict:
    claim: Claim
    label: str                           # one of config.VERDICT_* constants
    real_value: str                      # correct value when label is not VERIFIED
    explanation: str                     # 1-2 line human-readable justification
    confidence: float                    # 0.0 – 1.0
    sources: list[str] = field(default_factory=list)

    def __str__(self) -> str:
        return (
            f"Verdict(claim_id={self.claim.id}, label={self.label}, "
            f"confidence={self.confidence:.2f}): {self.explanation[:80]}"
        )


@dataclass
class Report:
    verdicts: list[Verdict]
    summary: dict                        # keys: verified, inaccurate, false, trust_score
    filename: str
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def __str__(self) -> str:
        return (
            f"Report(file={self.filename!r}, claims={len(self.verdicts)}, "
            f"trust_score={self.summary.get('trust_score', 0.0):.1f}%, "
            f"at={self.timestamp.isoformat()})"
        )
