from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from schemas import Claim, Evidence


CLAIM_EXTRACTION_PROMPT: str = """\
You are a precise fact-extraction engine for a document fact-checking system.

Your task is to identify and extract only hard, verifiable factual claims from the provided document text.

EXTRACT claims that contain:
- Specific numbers or quantities (e.g., "revenue grew by 43%", "3.2 million users")
- Exact dates or time periods (e.g., "launched on March 12, 2021", "as of Q3 2024")
- Financial figures (e.g., "$2.4 billion in funding", "net margin of 18.7%")
- Technical specifications (e.g., "latency under 50ms", "99.99% uptime", "uses AES-256 encryption")
- Named statistics or research findings with concrete values

SKIP claims that are:
- Opinions or subjective statements ("the best platform", "industry-leading quality")
- Predictions or forward-looking statements ("we expect growth next year")
- Vague improvements without measurable values ("performance improved significantly")
- Marketing language or general descriptions
- Claims with no specific, checkable value

OUTPUT RULES:
- Return a strict JSON array of objects — no markdown, no preamble, no explanation
- Each object must have exactly these keys:
  - "id": integer starting from 1
  - "text": the exact claim as it appears in the document (verbatim)
  - "claim_type": one of "stat" | "date" | "financial" | "technical"
  - "page": integer page number where the claim appears
- Maximum 12 claims — if more exist, prioritize the most specific and independently checkable ones
- If no verifiable claims are found, return an empty array: []
- Any claim too vague to fact-check must be excluded entirely

Return only the raw JSON array. Nothing else.\
"""


VERDICT_PROMPT: str = """\
You are a rigorous fact-checker. Your job is to determine whether a specific claim is accurate based on the web evidence provided.

This is where inaccurate statistics and fabricated figures get caught. Be skeptical. Be precise.

VERDICT RULES:
- Compare the claim's exact number, date, or value against what the evidence states
- "VERIFIED": evidence explicitly confirms the claim's specific value — the numbers, dates, or facts match directly and unambiguously
- "INACCURATE": evidence shows a different value from what the claim states — even a small discrepancy (e.g., claim says 43%, evidence says 41%) is INACCURATE; put the correct value in "real_value"
- "FALSE": evidence directly contradicts the claim, or no supporting evidence exists for the specific value claimed
- Never assign VERIFIED if evidence is vague, indirect, or only partially supports the claim — mark INACCURATE or FALSE
- Confidence score reflects how strongly the evidence supports your verdict, not how confident you are in the claim itself

OUTPUT FORMAT — return a strict JSON object with exactly these keys:
- "label": one of "VERIFIED" | "INACCURATE" | "FALSE"
- "real_value": the correct value as found in the evidence (use "" if label is "VERIFIED")
- "explanation": 1-2 sentences maximum — state plainly what the claim said and what the evidence shows
- "confidence": float between 0.0 and 1.0 — quality and clarity of the evidence
- "sources": list of URL strings from the evidence items that directly informed your verdict

Return only the raw JSON object. No markdown, no preamble, no extra text.\
"""


def build_claim_extraction_user_prompt(raw_text: str, page_count: int) -> str:
    return (
        f"Document total pages: {page_count}\n\n"
        f"Extract all verifiable factual claims from the following document text. "
        f"Claims may appear across any of the {page_count} page(s) — check the full text carefully.\n\n"
        f"--- DOCUMENT TEXT START ---\n"
        f"{raw_text.strip()}\n"
        f"--- DOCUMENT TEXT END ---\n\n"
        f"Return the JSON array of claims now."
    )


def build_verdict_user_prompt(claim: Claim, evidence_list: list[Evidence]) -> str:
    lines: list[str] = []

    lines.append("CLAIM TO VERIFY:")
    lines.append(f"  ID: {claim.id}")
    lines.append(f"  Type: {claim.claim_type}")
    lines.append(f"  Page: {claim.page_number}")
    lines.append(f"  Text: {claim.text}")
    lines.append("")

    if evidence_list:
        lines.append(f"EVIDENCE ({len(evidence_list)} source(s)):")
        for i, ev in enumerate(evidence_list, start=1):
            lines.append(f"\n[{i}] {ev.title}")
            lines.append(f"    URL: {ev.url}")
            lines.append(f"    Snippet: {ev.snippet.strip()}")
    else:
        lines.append("EVIDENCE: None retrieved.")

    lines.append("")
    lines.append("Compare the claim against the evidence and return your verdict as a JSON object.")

    return "\n".join(lines)


if __name__ == "__main__":
    separator: str = "\n" + "=" * 72 + "\n"

    print("CLAIM_EXTRACTION_PROMPT:")
    print(separator)
    print(CLAIM_EXTRACTION_PROMPT)
    print(separator)

    print("VERDICT_PROMPT:")
    print(separator)
    print(VERDICT_PROMPT)
    print(separator)

    dummy_claim = Claim(
        id=1,
        text="The platform processed over 4.2 billion transactions in Q2 2024.",
        claim_type="stat",
        page_number=3,
    )

    dummy_evidence: list[Evidence] = [
        Evidence(
            title="Company Q2 2024 Earnings Release",
            snippet=(
                "During the second quarter of 2024, the platform recorded 3.9 billion "
                "transactions, reflecting a 12% year-over-year increase."
            ),
            url="https://investor.example.com/press-releases/q2-2024-earnings",
        ),
        Evidence(
            title="TechCrunch: Example Co. Q2 Results",
            snippet=(
                "Example Co. reported 3.9B transactions in Q2 2024, falling short of "
                "analyst expectations of 4.1 billion."
            ),
            url="https://techcrunch.com/2024/08/01/example-co-q2-results",
        ),
    ]

    print("build_claim_extraction_user_prompt() output:")
    print(separator)
    sample_text = (
        "Page 1\nThis report covers our performance for fiscal year 2024.\n\n"
        "Page 3\nThe platform processed over 4.2 billion transactions in Q2 2024, "
        "driven by expansion into Southeast Asian markets."
    )
    print(build_claim_extraction_user_prompt(raw_text=sample_text, page_count=12))
    print(separator)

    print("build_verdict_user_prompt() output:")
    print(separator)
    print(build_verdict_user_prompt(claim=dummy_claim, evidence_list=dummy_evidence))
    print(separator)

    print("build_verdict_user_prompt() with empty evidence:")
    print(separator)
    print(build_verdict_user_prompt(claim=dummy_claim, evidence_list=[]))
    print(separator)
