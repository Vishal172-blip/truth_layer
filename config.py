from __future__ import annotations

import os
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# API Keys
# Keys loaded from environment variables.
# Local: set in .env file (loaded by python-dotenv above)
# Streamlit Cloud: set in App Settings > Secrets (auto-injected as env vars)
# ---------------------------------------------------------------------------
GROQ_API_KEY: str | None = os.getenv("GROQ_API_KEY")
OPENROUTER_API_KEY: str | None = os.getenv("OPENROUTER_API_KEY")
TAVILY_API_KEY: str | None = os.getenv("TAVILY_API_KEY")

# ---------------------------------------------------------------------------
# LLM Base URLs
# ---------------------------------------------------------------------------
GROQ_BASE_URL: str = "https://api.groq.com/openai/v1"
OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"

# ---------------------------------------------------------------------------
# LLM Models
# ---------------------------------------------------------------------------
GROQ_FAST_MODEL: str = "llama-3.1-8b-instant"         # claim extraction — cheap + fast
GROQ_REASONING_MODEL: str = "llama-3.3-70b-versatile"  # verdict reasoning — powerful
OPENROUTER_FALLBACK_MODEL: str = "meta-llama/llama-3.3-70b-instruct"

# ---------------------------------------------------------------------------
# Provider priority
# When both keys are set, this decides which provider is primary. Set to True
# to make OpenRouter primary (Groq becomes the fallback) — useful while Groq's
# daily free-tier token quota (TPD) is exhausted, to avoid wasting retries on a
# provider that will only 429. Flip back to False once Groq's quota resets.
# Override at runtime with the PREFER_OPENROUTER env var (true/false).
# ---------------------------------------------------------------------------
PREFER_OPENROUTER: bool = os.getenv("PREFER_OPENROUTER", "true").strip().lower() in (
    "1",
    "true",
    "yes",
)

# ---------------------------------------------------------------------------
# Search Settings
# ---------------------------------------------------------------------------
TAVILY_SEARCH_DEPTH: str = "basic"
TAVILY_MAX_RESULTS: int = 4
DDG_FALLBACK_ENABLED: bool = True
MAX_SEARCH_RESULTS_PER_CLAIM: int = 4

# ---------------------------------------------------------------------------
# Pipeline Limits
# ---------------------------------------------------------------------------
MAX_CLAIMS_TO_PROCESS: int = 12
MAX_PDF_PAGES: int = 50
LLM_TIMEOUT_SECONDS: int = 30
MAX_RETRIES_ON_FAILURE: int = 2

# ---------------------------------------------------------------------------
# Verdict Labels
# ---------------------------------------------------------------------------
VERDICT_VERIFIED: str = "VERIFIED"
VERDICT_INACCURATE: str = "INACCURATE"
VERDICT_FALSE: str = "FALSE"

# ---------------------------------------------------------------------------
# Trust Score Weights
# ---------------------------------------------------------------------------
WEIGHT_VERIFIED: float = 1.0
WEIGHT_INACCURATE: float = 0.5
WEIGHT_FALSE: float = 0.0

# ---------------------------------------------------------------------------
# Runtime / Deployment
# ---------------------------------------------------------------------------
IS_STREAMLIT_CLOUD: bool = os.getenv("STREAMLIT_SHARING_MODE") is not None
INTER_CLAIM_DELAY_SECONDS: float = 0.5
