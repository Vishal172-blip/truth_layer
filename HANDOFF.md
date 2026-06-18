# TruthLayer — Project Handoff

## Live App

[URL to be inserted after Streamlit Cloud deployment — see DEPLOY.md]

## What Was Built

TruthLayer is an AI-powered fact-checking web app. Upload any PDF document —
it extracts every verifiable factual claim, searches the live web for each one,
and delivers a colour-coded verdict report with Trust Score.

**No login required. No data stored. Runs entirely on free-tier APIs.**

## How to Test It

1. Open the live URL above
2. Click **Get Started**
3. Upload any PDF with factual claims (statistics, dates, financial figures)
4. Wait 1-3 minutes depending on document size and number of claims
5. Review the colour-coded report — green (VERIFIED), orange (INACCURATE), red (FALSE)

## Included Test Document

`assets/sample_trap.pdf` is a deliberately rigged document containing fake statistics
designed to demonstrate the detection capability. Upload it to see INACCURATE and FALSE
verdicts with the corrected real values and source links.

## What the Output Means

| Verdict | Meaning |
|---|---|
| **VERIFIED** | Evidence directly confirms the claim's specific value |
| **INACCURATE** | Evidence shows a different value — the correct value is shown |
| **FALSE** | No credible evidence supports the claim, or evidence directly contradicts it |

The **Trust Score** (0-100%) summarises overall document accuracy:
`(verified × 1.0 + inaccurate × 0.5 + false × 0.0) / total × 100`

## Tech Stack

| Component | Technology |
|---|---|
| Frontend | Streamlit (Python) |
| LLM Primary | Groq — llama-3.3-70b-versatile |
| LLM Fallback | OpenRouter — mistral-7b-instruct |
| Web Search Primary | Tavily |
| Web Search Fallback | DuckDuckGo (no key needed) |
| PDF Parsing | pdfplumber |
| Deployment | Streamlit Community Cloud |

## API Keys Required (all free tier)

| Service | Sign-up URL | Notes |
|---|---|---|
| Groq | https://console.groq.com | No credit card |
| OpenRouter | https://openrouter.ai | Free with `:free` models |
| Tavily | https://tavily.com | 1,000 free searches/month |

## Source Code

GitHub: [URL to be inserted after push]

## Local Setup

See [README.md](README.md) for complete local setup instructions (5 steps, ~5 minutes).

## Known Limitations

- English-language PDFs with machine-readable text only (no OCR for scanned documents)
- Maximum 12 claims processed per document (to manage API cost)
- LLM verdicts are probabilistic — always verify critical findings manually
- Tavily free tier: 1,000 searches/month — heavy use triggers the DuckDuckGo fallback automatically
