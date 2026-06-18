# TruthLayer — Architecture Overview

## Three-Layer Architecture

TruthLayer is organised into three clean layers with no cross-layer dependencies:

**UI Layer** (`ui/`, `app.py`) — Streamlit rendering only. Receives data objects, renders HTML. Makes no direct calls to LLM or search services.

**Logic Layer** (`core/`, `llm/`, `search/`) — All processing. `pipeline.py` is the sole orchestrator; the other modules (`claim_extractor`, `web_verifier`, `verdict_engine`) do one thing each and never call each other directly.

**Contracts Layer** (`schemas.py`, `config.py`) — Shared dataclasses and settings. Imported by every module; imports nothing from the project.

## Data Flow

```
User uploads PDF
       |
       v
app.py — reads PDF bytes, calls FactCheckPipeline.run_fact_check()
       |
       v
core/pdf_extractor.py — PDF bytes -> clean text with page markers
       |
       v
core/claim_extractor.py — text -> List[Claim] via LLM (fast model)
       |
       v
for each Claim:
  core/web_verifier.py  — Claim -> List[Evidence] via search
  core/verdict_engine.py — Claim + Evidence -> Verdict via LLM (reasoning model)
       |
       v
core/pipeline.py — assembles Report with all Verdicts + Trust Score
       |
       v
ui/components.py — renders colour-coded verdict cards + download buttons
```

## Module Responsibilities

| Module | Single Responsibility |
|---|---|
| `app.py` | Session state, page routing, pipeline trigger |
| `config.py` | All settings, constants, API key loading |
| `schemas.py` | Data contracts — Claim, Evidence, Verdict, Report |
| `core/pipeline.py` | Sole orchestrator — sequences all stages, assembles Report |
| `core/pdf_extractor.py` | PDF bytes → page-marked plain text |
| `core/claim_extractor.py` | Text → typed List[Claim] via LLM |
| `core/web_verifier.py` | Claim → List[Evidence] via SearchClient |
| `core/verdict_engine.py` | Claim + Evidence → Verdict via LLMClient |
| `llm/llm_client.py` | LLM API calls — Groq primary, OpenRouter fallback |
| `llm/prompts.py` | Prompt templates and builder functions |
| `search/search_client.py` | Web search — Tavily primary, DuckDuckGo fallback |
| `ui/components.py` | All Streamlit rendering — landing page, report, download |
| `utils/logger.py` | Centralised logging configuration |
| `utils/text_utils.py` | `build_search_query()` helper |

## Data Contracts

| Dataclass | Fields |
|---|---|
| `Claim` | `id: int`, `text: str`, `claim_type: Literal["stat","date","financial","technical"]`, `page_number: int` |
| `Evidence` | `title: str`, `snippet: str`, `url: str` |
| `Verdict` | `claim: Claim`, `label: str`, `real_value: str`, `explanation: str`, `confidence: float`, `sources: list[str]` |
| `Report` | `verdicts: list[Verdict]`, `summary: dict`, `filename: str`, `timestamp: datetime` |

## Fallback Chains

**LLM fallback:** `LLMClient` tries Groq first (llama-3.3-70b for verdict, llama-3.1-8b for extraction). On `RateLimitError` or `APIError`, it falls back to OpenRouter (mistral-7b-instruct). The calling code sees one interface — `client.chat()` — and is never aware of which provider responded.

**Search fallback:** `SearchClient` tries Tavily first. On any exception (missing key, rate limit, network error), it falls back to DuckDuckGo (`ddgs`). DuckDuckGo requires no API key. The calling code sees one interface — `client.search()`.

## Why pipeline.py Is the Only Orchestrator

Each stage module (`claim_extractor`, `web_verifier`, `verdict_engine`) is independently testable and has no knowledge of the stages before or after it. This means:

- Swapping the LLM provider only requires changing `llm_client.py`
- Swapping the search provider only requires changing `search_client.py`
- Adding a new stage (e.g., bias detection) only requires adding it to `pipeline.py`
- No circular imports are possible — the dependency graph is a strict DAG

## Memory Footprint

Peak memory per run is approximately `PDF size × 3` (bytes in memory + pdfplumber parsing overhead). For a 10 MB PDF this is ~30 MB — well within Streamlit Community Cloud's 1 GB limit. The 12-claim maximum also caps LLM response accumulation.
