# TruthLayer

**Automated fact-checking for PDF documents -- powered by LLMs and live web search.**

**[Python 3.10+]** | **[Streamlit]** | **[Groq + OpenRouter]**

---

## What it does

Documents -- reports, news articles, white papers, research briefs -- frequently contain statistics, figures, and claims that are outdated, distorted, or simply fabricated. Manually fact-checking even a single page is time-consuming and unreliable; doing it at scale is impractical for most people and organisations.

TruthLayer automates that process. It reads any PDF, identifies every verifiable factual claim (statistics, dates, named figures, event descriptions), and independently searches the live web for corroborating or contradicting evidence. An LLM then compares what the document says against what the evidence shows and delivers a verdict.

The result is a colour-coded report -- **VERIFIED**, **INACCURATE**, or **FALSE** -- for each claim, complete with the corrected real value where applicable, source links, a per-claim confidence score, and an overall **Trust Score** percentage that summarises how accurate the document is as a whole.

---

## How it works

```
PDF Upload -> Text Extraction -> Claim Detection -> Web Search -> LLM Verdict -> Report
```

| Stage | Tool Used | Output |
|---|---|---|
| PDF Upload | Streamlit file uploader | Raw PDF bytes |
| Text Extraction | pdfplumber | Clean text with page markers |
| Claim Detection | Groq LLM (llama-3.1-8b) | List of typed factual claims |
| Web Search | Tavily / DuckDuckGo | Evidence snippets + source URLs |
| LLM Verdict | Groq LLM (llama-3.3-70b) | VERIFIED / INACCURATE / FALSE + explanation |

---

## Tech stack

| Layer | Technology | Why |
|---|---|---|
| Frontend | Streamlit | Zero-config Python UI, instant deploy |
| PDF Parsing | pdfplumber | Reliable text + table extraction |
| LLM Primary | Groq (llama-3.3-70b) | Fast, free tier available |
| LLM Fallback | OpenRouter | Automatic if Groq rate-limits |
| Search Primary | Tavily | Structured web search API |
| Search Fallback | DuckDuckGo (ddgs) | No API key needed |
| Deploy | Streamlit Community Cloud | Free public URL |

---

## Local setup

**Step 1 -- Clone**

```bash
git clone https://github.com/yourusername/truthlayer.git
cd truthlayer
```

**Step 2 -- Install dependencies**

```bash
pip install -r requirements.txt
```

**Step 3 -- Set up API keys**

```bash
cp .env.example .env
# Edit .env and add your keys
```

**Step 4 -- Get free API keys**

| Service | URL | Notes |
|---|---|---|
| Groq | https://console.groq.com | Free, no credit card required |
| OpenRouter | https://openrouter.ai | Free tier with `:free` models |
| Tavily | https://tavily.com | Free tier -- 1,000 searches/month |

> **Note:** Groq or OpenRouter is required (at least one). Tavily is optional -- the app falls back to DuckDuckGo automatically if the key is not set.

**Step 5 -- Run**

```bash
streamlit run app.py
```

Open `http://localhost:8501` in your browser.

---

## Streamlit Cloud deployment

1. Push this repository to GitHub (make sure `.env` and `.streamlit/secrets.toml` are not committed -- both are in `.gitignore`)
2. Go to https://share.streamlit.io and connect your GitHub account
3. Select your repository, set **Main file path** to `app.py`, and click **Deploy**
4. In the app dashboard, open **Settings -> Secrets** and paste the following, replacing placeholder values with your real keys:

```toml
GROQ_API_KEY = "gsk_your_groq_key_here"
OPENROUTER_API_KEY = "sk-or-your_openrouter_key_here"
TAVILY_API_KEY = "tvly-your_tavily_key_here"
```

5. Click **Save** -- Streamlit Cloud restarts the app and injects the secrets automatically.

> **Warning:** Never commit `.env` or `.streamlit/secrets.toml` to version control. Both files are listed in `.gitignore` and contain live API credentials.

---

## Project structure

```
truthlayer/
|-- app.py                    # Streamlit entry point -- page routing, session state
|-- config.py                 # All settings, API keys, model names, pipeline limits
|-- schemas.py                # Dataclasses -- Claim, Evidence, Verdict, Report
|-- requirements.txt          # Python dependencies
|-- runtime.txt               # Python version for Streamlit Cloud
|-- packages.txt              # System packages for Streamlit Cloud (none required)
|-- Makefile                  # Developer shortcuts (install, run, clean)
|
|-- core/
|   |-- pdf_extractor.py      # PDF bytes -> clean text with page markers
|   |-- claim_extractor.py    # Text -> List[Claim] via LLM
|   |-- web_verifier.py       # Claim -> List[Evidence] via web search
|   |-- verdict_engine.py     # Claim + Evidence -> Verdict via LLM
|   `-- pipeline.py           # Full orchestration -- ties all stages together
|
|-- llm/
|   |-- llm_client.py         # LLMClient -- Groq primary, OpenRouter fallback
|   `-- prompts.py            # Prompt templates and builder functions
|
|-- search/
|   `-- search_client.py      # SearchClient -- Tavily primary, DuckDuckGo fallback
|
|-- ui/
|   `-- components.py         # All Streamlit rendering functions
|
|-- utils/
|   |-- logger.py             # Centralised logging configuration
|   `-- text_utils.py         # build_search_query helper
|
|-- assets/
|   `-- sample_trap.pdf       # Sample PDF with deliberate fake statistics for testing
|
`-- .streamlit/
    |-- config.toml           # Streamlit theme + server configuration
    `-- secrets.toml          # API keys for Streamlit Cloud (gitignored)
```

---

## How the verdict engine works

Each claim receives one of three verdicts:

- **VERIFIED** -- the evidence found online supports the claim as stated. Confidence reflects how strongly the evidence agrees.
- **INACCURATE** -- the evidence found a different value or contradicts a specific figure. The corrected real value is shown alongside the verdict.
- **FALSE** -- no credible evidence supports the claim, or the evidence directly contradicts it without providing an alternative value.

The **confidence score** (0-100%) reflects the LLM's certainty in its verdict given the available evidence. Low confidence on a VERIFIED claim means the evidence was thin; low confidence on a FALSE claim means the LLM could not find strong counter-evidence.

The **Trust Score** is calculated as: `(verified x 1.0 + inaccurate x 0.5 + false x 0.0) / total claims x 100`. A document with 8 VERIFIED and 2 FALSE claims scores 80%.

---

## Known limitations

- Works best on English-language PDFs with machine-readable text
- Scanned or image-only PDFs cannot be processed -- no OCR is included
- Maximum 12 claims processed per document to manage API usage and cost
- Tavily's free tier has a monthly search limit (1,000 requests) -- heavy use triggers the DuckDuckGo fallback
- LLM verdicts are probabilistic -- the model can be wrong, especially on highly specialised or very recent claims. Always verify critical findings manually before acting on them

---

## License

MIT -- free to use, modify, and distribute.
