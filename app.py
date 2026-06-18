from __future__ import annotations

import logging
import time

import streamlit as st

from schemas import Report
import config
from core.pipeline import FactCheckPipeline
from core.pdf_extractor import PDFExtractionError
from ui.components import (
    inject_global_css,
    render_landing_page,
    render_upload_section,
    render_report,
    render_download_buttons,
    render_error,
)

st.set_page_config(
    page_title="TruthLayer",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

inject_global_css()

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(name)s | %(message)s")
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# API key guard — halt before any content if no LLM provider is available
# ---------------------------------------------------------------------------
if not config.GROQ_API_KEY and not config.OPENROUTER_API_KEY:
    st.error(
        "No LLM API key configured. "
        "Please set GROQ_API_KEY or OPENROUTER_API_KEY in your .env file or Streamlit secrets."
    )
    st.stop()

# ---------------------------------------------------------------------------
# Session state initialisation
# ---------------------------------------------------------------------------
if "started" not in st.session_state:
    st.session_state["started"] = False

if "report" not in st.session_state:
    st.session_state["report"] = None

if "analyzing" not in st.session_state:
    st.session_state["analyzing"] = False

if "elapsed_time" not in st.session_state:
    st.session_state["elapsed_time"] = None

if "pipeline" not in st.session_state:
    st.session_state["pipeline"] = None

if "analyzed_filename" not in st.session_state:
    st.session_state["analyzed_filename"] = None

if "_cached_report" not in st.session_state:
    st.session_state["_cached_report"] = None

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### TruthLayer")
    st.write("Verifies PDF claims against live web sources.")
    st.divider()

    # Mirror LLMClient's primary-selection logic so the sidebar shows the
    # provider that actually runs first (OpenRouter when PREFER_OPENROUTER is on).
    _prefer_openrouter = config.PREFER_OPENROUTER and config.OPENROUTER_API_KEY
    if config.GROQ_API_KEY and not _prefer_openrouter:
        llm_provider = "Groq"
    elif config.OPENROUTER_API_KEY:
        llm_provider = "OpenRouter"
    else:
        llm_provider = "Groq"
    search_provider = "Tavily" if config.TAVILY_API_KEY else "DuckDuckGo"

    llm_dot = "🟢" if (config.GROQ_API_KEY or config.OPENROUTER_API_KEY) else "🟡"
    search_dot = "🟢" if config.TAVILY_API_KEY else "🟡"

    st.markdown(f"{llm_dot} **LLM:** {llm_provider}")
    st.markdown(f"{search_dot} **Search:** {search_provider}")

    if not config.TAVILY_API_KEY:
        st.warning("Tavily key not set — using DuckDuckGo for web search (may be slower)")

    if st.session_state.get("elapsed_time") is not None:
        st.divider()
        elapsed = st.session_state["elapsed_time"]
        _report = st.session_state.get("report")
        total_claims = len(_report.verdicts) if _report else 0
        st.caption(f"Last analysis: {elapsed:.1f}s · {total_claims} claims")

# ---------------------------------------------------------------------------
# Page routing
# ---------------------------------------------------------------------------
if not st.session_state["started"]:
    if render_landing_page():
        st.session_state["started"] = True
        st.rerun()

elif st.session_state["report"] is not None:
    _, btn_col = st.columns([4, 1])
    with btn_col:
        if st.button("🔄 Analyze Another", use_container_width=True):
            st.session_state["report"] = None
            st.session_state["analyzing"] = False
            st.session_state["elapsed_time"] = None
            st.rerun()

    render_report(st.session_state["report"])
    render_download_buttons(st.session_state["report"])

    if st.session_state.get("elapsed_time") is not None:
        _report = st.session_state["report"]
        total_claims = len(_report.verdicts) if _report else 0
        elapsed = st.session_state["elapsed_time"]
        st.markdown(
            f"<p style='text-align: center; color: #8B9AB0; font-size: 0.8em; margin-top: 24px;'>"
            f"Analysis completed in {elapsed:.1f} seconds · {total_claims} claims verified"
            f"</p>",
            unsafe_allow_html=True,
        )

else:
    pdf_bytes = render_upload_section()

    if pdf_bytes is not None and not st.session_state["analyzing"]:
        filename = st.session_state.get("filename", "document.pdf")

        # Filename-based cache check
        if (
            filename == st.session_state.get("analyzed_filename")
            and st.session_state.get("_cached_report") is not None
        ):
            st.warning(
                f"**{filename}** was already analyzed. "
                "Upload a different file or choose an option:"
            )
            col_cache, col_rerun = st.columns(2)
            with col_cache:
                if st.button("Use Cached Report", key="btn_use_cache"):
                    st.session_state["report"] = st.session_state["_cached_report"]
                    st.rerun()
            with col_rerun:
                if st.button("Re-analyze", key="btn_reanalyze"):
                    st.session_state["_cached_report"] = None
                    st.session_state["analyzed_filename"] = None
                    st.rerun()
        else:
            # Normal analysis flow
            st.session_state["analyzing"] = True
            print(f"[TruthLayer] Analysis triggered for: {filename}")

            # Native, always-visible progress feedback. st.status streams its
            # label updates to the browser as the synchronous pipeline runs, and
            # st.progress shows a moving bar as each claim is verified.
            with st.status(
                "🔍 Extracting claims from your document…", expanded=True
            ) as status:
                progress_bar = st.progress(
                    0.0, text="Parsing PDF and identifying verifiable facts…"
                )
                try:
                    pipeline = FactCheckPipeline()
                    st.session_state["pipeline"] = pipeline

                    def _progress_cb(current: int, total: int, verdict) -> None:
                        progress_bar.progress(
                            current / total,
                            text=f"Verifying claim {current} of {total}…",
                        )
                        status.update(label=f"Verifying claims… ({current}/{total})")

                    def _extraction_cb(count: int) -> None:
                        print(f"[TruthLayer] Extracted {count} claims — verification starting")
                        status.update(
                            label=f"Found {count} verifiable claims — verifying…"
                        )
                        progress_bar.progress(
                            0.0, text=f"Verifying claim 1 of {count}…"
                        )

                    _t0 = time.time()
                    report = pipeline.run_fact_check(
                        pdf_bytes=pdf_bytes,
                        filename=filename,
                        progress_callback=_progress_cb,
                        extraction_callback=_extraction_cb,
                    )
                    st.session_state["elapsed_time"] = time.time() - _t0
                    st.session_state["report"] = report
                    st.session_state["_cached_report"] = report
                    st.session_state["analyzed_filename"] = filename
                    st.session_state["analyzing"] = False
                    progress_bar.progress(1.0, text="Done")
                    status.update(
                        label="✅ Analysis complete", state="complete", expanded=False
                    )
                    print(f"[TruthLayer] Analysis complete — trust score: {report.summary.get('trust_score')}%")
                    st.rerun()
                except PDFExtractionError:
                    st.session_state["analyzing"] = False
                    status.update(label="Could not read the PDF file.", state="error")
                    render_error(
                        "Could not read the PDF file.",
                        "Try a different PDF — some encrypted or scanned-only PDFs cannot be parsed.",
                    )
                except Exception as exc:
                    logger.error("Pipeline failed: %s", exc)
                    st.session_state["analyzing"] = False
                    status.update(label="Analysis failed.", state="error")
                    render_error(
                        "Something went wrong during analysis.",
                        "Please try a different PDF or check your API keys in the .env file.",
                    )
