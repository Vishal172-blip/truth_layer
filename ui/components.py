from __future__ import annotations

import html
import json
import streamlit as st
from schemas import Claim, Evidence, Verdict, Report


# ---------------------------------------------------------------------------
# inject_global_css
# ---------------------------------------------------------------------------

def inject_global_css() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700;800&display=swap');

        /* ── Variables ───────────────────────────────────────────────────── */
        :root {
          --bg-deep:      #0A0C17;
          --bg-surface:   #12142A;
          --bg-elevated:  #1A1D35;
          --bg-hover:     #202344;
          --border:       #252848;
          --border-hi:    #3A3E6A;
          --primary:      #7C6FFF;
          --primary-dim:  rgba(124, 111, 255, 0.14);
          --primary-glow: rgba(124, 111, 255, 0.30);
          --cyan:         #00D4FF;
          --green:        #00E676;
          --amber:        #FFB300;
          --red:          #FF4444;
          --text-1:       #EEF0FF;
          --text-2:       #9094C0;
          --text-3:       #555980;
        }

        /* ── Font & base ─────────────────────────────────────────────────── */
        html, body, [class*="css"] {
          font-family: 'Space Grotesk', system-ui, sans-serif !important;
          -webkit-font-smoothing: antialiased;
        }

        /* ── App background ──────────────────────────────────────────────── */
        .stApp { background: var(--bg-deep) !important; }

        /* ── Hide Streamlit chrome ───────────────────────────────────────── */
        #MainMenu { visibility: hidden; }
        footer     { visibility: hidden; }
        header     { visibility: hidden; }

        /* ── Scrollbar ───────────────────────────────────────────────────── */
        ::-webkit-scrollbar       { width: 5px; }
        ::-webkit-scrollbar-track { background: var(--bg-surface); }
        ::-webkit-scrollbar-thumb { background: var(--border-hi); border-radius: 4px; }
        ::-webkit-scrollbar-thumb:hover { background: var(--primary); }

        /* ── Layout ──────────────────────────────────────────────────────── */
        .block-container { padding-top: 1rem !important; max-width: 960px; }

        /* ── Buttons (base) ──────────────────────────────────────────────── */
        .stButton > button {
          font-family: 'Space Grotesk', sans-serif !important;
          font-weight: 600 !important;
          border-radius: 10px !important;
          transition: all 0.22s ease !important;
        }
        .stButton > button:hover {
          transform: translateY(-1px) !important;
          box-shadow: 0 6px 20px rgba(0,0,0,0.35) !important;
        }

        /* Primary */
        [data-testid="baseButton-primary"] {
          background: linear-gradient(135deg, #7C6FFF 0%, #9B5DE5 50%, #00D4FF 100%) !important;
          background-size: 200% 200% !important;
          animation: btnGradient 5s ease infinite !important;
          border: none !important;
          color: #fff !important;
          font-size: 1.05em !important;
          letter-spacing: 0.03em !important;
          padding: 0.65em 1.75em !important;
          border-radius: 12px !important;
        }
        [data-testid="baseButton-primary"]:hover {
          box-shadow: 0 8px 28px var(--primary-glow) !important;
          filter: brightness(1.08) !important;
        }

        /* Secondary */
        [data-testid="baseButton-secondary"] {
          background: var(--bg-elevated) !important;
          border: 1px solid var(--border-hi) !important;
          color: var(--text-2) !important;
        }
        [data-testid="baseButton-secondary"]:hover {
          background: var(--bg-hover) !important;
          color: var(--text-1) !important;
          border-color: var(--primary) !important;
        }

        /* ── File uploader ───────────────────────────────────────────────── */
        [data-testid="stFileUploader"] { border-radius: 16px !important; }
        [data-testid="stFileUploaderDropzone"] {
          background: linear-gradient(135deg, var(--bg-elevated), var(--bg-surface)) !important;
          border: 2px dashed var(--border-hi) !important;
          border-radius: 16px !important;
          padding: 48px 24px !important;
          transition: all 0.28s ease !important;
          cursor: pointer !important;
        }
        [data-testid="stFileUploaderDropzone"]:hover {
          border-color: var(--primary) !important;
          background: var(--primary-dim) !important;
          box-shadow: 0 0 0 4px rgba(124,111,255,0.07), 0 8px 32px rgba(0,0,0,0.3) !important;
        }
        [data-testid="stFileUploaderDropzoneInstructions"] > div > span {
          color: var(--text-2) !important;
          font-weight: 500 !important;
        }
        [data-testid="stFileUploaderDropzoneInstructions"] > div > small {
          color: var(--text-3) !important;
        }

        /* ── Progress bar ────────────────────────────────────────────────── */
        .stProgress > div > div > div {
          background: linear-gradient(90deg, var(--primary), var(--cyan)) !important;
          border-radius: 4px !important;
        }
        .stProgress > div > div {
          background: var(--border) !important;
          border-radius: 4px !important;
          height: 6px !important;
        }

        /* ── Alerts ──────────────────────────────────────────────────────── */
        .stAlert { border-radius: 12px !important; border: 1px solid var(--border) !important; }

        /* ── Download buttons ────────────────────────────────────────────── */
        [data-testid="stDownloadButton"] > button {
          background: var(--bg-elevated) !important;
          border: 1px solid var(--border-hi) !important;
          color: var(--text-2) !important;
          border-radius: 10px !important;
        }
        [data-testid="stDownloadButton"] > button:hover {
          border-color: var(--primary) !important;
          color: var(--text-1) !important;
          background: var(--bg-hover) !important;
        }

        /* ── Sidebar ─────────────────────────────────────────────────────── */
        [data-testid="stSidebar"] {
          background: var(--bg-surface) !important;
          border-right: 1px solid var(--border) !important;
        }
        [data-testid="stSidebar"] .block-container { padding-top: 2rem !important; }

        /* ── Caption ─────────────────────────────────────────────────────── */
        .stCaption { color: var(--text-3) !important; }

        /* ─────────────────────────────────────────────────────────────────
           Custom component classes
        ───────────────────────────────────────────────────────────────── */

        /* Landing hero */
        .tl-hero-wrapper {
          text-align: center;
          padding: 52px 20px 40px;
          position: relative;
          overflow: hidden;
        }
        .tl-hero-glow {
          position: absolute;
          top: 45%; left: 50%;
          transform: translate(-50%, -50%);
          width: 720px; height: 300px;
          background: radial-gradient(ellipse, rgba(124,111,255,0.13) 0%, transparent 65%);
          pointer-events: none;
          border-radius: 50%;
          animation: pulseGlow 5s ease-in-out infinite;
        }
        .tl-hero-badge {
          display: inline-block;
          background: rgba(124,111,255,0.12);
          border: 1px solid rgba(124,111,255,0.32);
          color: #A89FFF;
          border-radius: 100px;
          padding: 5px 18px;
          font-size: 0.76em;
          font-weight: 600;
          letter-spacing: 0.07em;
          text-transform: uppercase;
          margin-bottom: 24px;
        }
        .tl-hero-title {
          font-size: 3.9em;
          font-weight: 800;
          line-height: 1.05;
          margin: 0 0 18px;
          letter-spacing: -0.03em;
          color: var(--text-1);
        }
        .tl-gradient-text {
          background: linear-gradient(135deg, #7C6FFF 0%, #00D4FF 55%, #00E676 100%);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
        }
        .tl-hero-subtitle {
          font-size: 1.12em;
          color: var(--text-2);
          max-width: 620px;
          margin: 0 auto 36px;
          line-height: 1.6;
          font-weight: 400;
          text-align: center;
        }

        /* Feature card */
        .tl-feature-card {
          background: linear-gradient(160deg, #1A1D35 0%, #12142A 100%);
          border: 1px solid var(--border);
          border-radius: 18px;
          padding: 28px 20px 24px;
          text-align: center;
          min-height: 175px;
          transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
          position: relative;
          overflow: hidden;
        }
        .tl-feature-card::after {
          content: '';
          position: absolute;
          top: 0; left: 0; right: 0; bottom: auto;
          height: 1px;
          background: linear-gradient(90deg, transparent, rgba(124,111,255,0.55), transparent);
          opacity: 0;
          transition: opacity 0.25s ease;
        }
        .tl-feature-card:hover {
          transform: translateY(-5px);
          border-color: rgba(124,111,255,0.35);
          box-shadow: 0 20px 44px rgba(0,0,0,0.45), 0 0 0 1px rgba(124,111,255,0.1);
        }
        .tl-feature-card:hover::after { opacity: 1; }
        .tl-feature-icon {
          width: 54px; height: 54px;
          background: linear-gradient(135deg, rgba(124,111,255,0.22), rgba(0,212,255,0.1));
          border: 1px solid rgba(124,111,255,0.22);
          border-radius: 14px;
          display: flex; align-items: center; justify-content: center;
          font-size: 1.55em;
          margin: 0 auto 14px;
        }

        /* Verdict card */
        .tl-verdict-card {
          border-radius: 14px;
          padding: 20px 24px;
          margin-bottom: 14px;
          transition: transform 0.2s ease, box-shadow 0.2s ease;
          overflow: hidden;
          animation: fadeInUp 0.3s ease both;
        }
        .tl-verdict-card:hover {
          transform: translateX(4px);
          box-shadow: 0 10px 36px rgba(0,0,0,0.5);
        }

        /* Trust score section */
        .tl-trust-section {
          background: linear-gradient(160deg, #1A1D35 0%, #12142A 100%);
          border: 1px solid var(--border);
          border-radius: 18px;
          padding: 32px 28px;
          margin-bottom: 24px;
        }

        /* ── Animations ──────────────────────────────────────────────────── */
        @keyframes btnGradient {
          0%   { background-position: 0%   50%; }
          50%  { background-position: 100% 50%; }
          100% { background-position: 0%   50%; }
        }
        @keyframes topBarAnim {
          0%   { background-position: 0%   50%; }
          50%  { background-position: 100% 50%; }
          100% { background-position: 0%   50%; }
        }
        @keyframes fadeInUp {
          from { opacity: 0; transform: translateY(12px); }
          to   { opacity: 1; transform: translateY(0); }
        }
        @keyframes pulseGlow {
          0%   { opacity: 0.7; transform: translate(-50%,-50%) scale(0.96); }
          50%  { opacity: 1.0; transform: translate(-50%,-50%) scale(1.04); }
          100% { opacity: 0.7; transform: translate(-50%,-50%) scale(0.96); }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# render_landing_page
# ---------------------------------------------------------------------------

def render_landing_page() -> bool:
    """Render the TruthLayer landing page. Returns True if 'Get Started' clicked."""

    # Animated top accent bar
    st.markdown(
        """
        <div style="position: fixed; top: 0; left: 0; right: 0; height: 3px; z-index: 9999;
             background: linear-gradient(90deg, #7C6FFF, #00D4FF, #00E676, #7C6FFF);
             background-size: 300% 100%;
             animation: topBarAnim 5s ease infinite;"></div>
        """,
        unsafe_allow_html=True,
    )

    # Hero
    _, center, _ = st.columns([0.3, 3, 0.3])
    with center:
        st.markdown(
            """
            <div class="tl-hero-wrapper">
              <div class="tl-hero-glow"></div>
              <div class="tl-hero-badge">✦ AI-Powered Fact Verification</div>
              <h1 class="tl-hero-title">
                <span class="tl-gradient-text">TruthLayer</span>
              </h1>
              <p class="tl-hero-subtitle">
                Upload any PDF. Every claim is cross-checked against live web sources
                and returned with a confidence score.
              </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Feature cards
    feat_left, feat_mid, feat_right = st.columns(3)
    with feat_left:
        st.markdown(
            """
            <div class="tl-feature-card">
              <div class="tl-feature-icon">🔍</div>
              <div style="color:#EEF0FF;font-weight:600;font-size:.98em;margin-bottom:8px;">
                Instant Extraction
              </div>
              <p style="font-size:.87em;color:#9094C0;margin:0;line-height:1.55;">
                Automatically pulls every verifiable claim from your document
              </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with feat_mid:
        st.markdown(
            """
            <div class="tl-feature-card">
              <div class="tl-feature-icon">🌐</div>
              <div style="color:#EEF0FF;font-weight:600;font-size:.98em;margin-bottom:8px;">
                Live Verification
              </div>
              <p style="font-size:.87em;color:#9094C0;margin:0;line-height:1.55;">
                Cross-checks each claim against real-time web sources
              </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with feat_right:
        st.markdown(
            """
            <div class="tl-feature-card">
              <div class="tl-feature-icon">📊</div>
              <div style="color:#EEF0FF;font-weight:600;font-size:.98em;margin-bottom:8px;">
                Trust Score
              </div>
              <p style="font-size:.87em;color:#9094C0;margin:0;line-height:1.55;">
                Clear percentage score showing how accurate your document is
              </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")

    _, btn_col, _ = st.columns([1.5, 1, 1.5])
    with btn_col:
        clicked = st.button("Get Started →", use_container_width=True, type="primary")

    return clicked


# ---------------------------------------------------------------------------
# render_upload_section
# ---------------------------------------------------------------------------

def render_upload_section() -> bytes | None:
    """Render PDF upload UI. Returns raw bytes if Analyze clicked, else None."""

    back_col, _ = st.columns([1, 8])
    with back_col:
        if st.button("← Back"):
            st.session_state["started"] = False
            st.rerun()

    # ── Upload hero ────────────────────────────────────────────────────────
    st.markdown(
        """
        <div style="text-align:center;padding:40px 20px 28px;">
          <div style="display:inline-flex;align-items:center;justify-content:center;
               width:68px;height:68px;
               background:linear-gradient(135deg,rgba(124,111,255,0.18),rgba(0,212,255,0.08));
               border:1px solid rgba(124,111,255,0.3);
               border-radius:20px;font-size:1.85em;margin-bottom:20px;">📄</div>
          <h2 style="color:#EEF0FF;font-weight:700;font-size:2.1em;
               letter-spacing:-0.025em;margin:0 0 12px;">
            Upload your PDF
          </h2>
          <p style="color:#9094C0;font-size:1em;margin:0 auto;line-height:1.65;max-width:480px;">
            Drop in any document — we'll extract every factual claim and
            cross-check it against live web sources.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Dropzone (Streamlit native, centered) ──────────────────────────────
    _, up_col, _ = st.columns([1, 4, 1])
    with up_col:
        uploaded_file = st.file_uploader(
            "Upload PDF",
            type=["pdf"],
            label_visibility="collapsed",
        )

    raw_bytes: bytes | None = None

    if uploaded_file is not None:
        raw_bytes = uploaded_file.getvalue()
        size_bytes = len(raw_bytes)

        # Show KB for small files, MB for large — avoids "0.0 MB" for tiny PDFs
        if size_bytes >= 1024 * 1024:
            size_str = f"{size_bytes / (1024 * 1024):.2f} MB"
        else:
            size_str = f"{size_bytes / 1024:.1f} KB"

        if size_bytes > 10 * 1024 * 1024:
            st.warning("⚠️ PDF is too large. Please upload a PDF under 10 MB.")
            raw_bytes = None
        else:
            if size_bytes > 3 * 1024 * 1024:
                st.info("ℹ️ Large document detected. Analysis may take 2–3 minutes.")

            # ── File-selected card ─────────────────────────────────────────
            _, card_col, _ = st.columns([1, 4, 1])
            with card_col:
                st.markdown(
                    f"""
                    <div style="background:linear-gradient(135deg,
                           rgba(124,111,255,0.09),rgba(0,212,255,0.04));
                         border:1px solid rgba(124,111,255,0.28);
                         border-radius:14px;padding:16px 20px;
                         display:flex;align-items:center;gap:14px;
                         margin-top:8px;">
                      <div style="width:44px;height:44px;flex-shrink:0;
                           background:rgba(124,111,255,0.15);border-radius:11px;
                           display:flex;align-items:center;justify-content:center;
                           font-size:1.3em;">📄</div>
                      <div style="flex:1;min-width:0;">
                        <div style="color:#EEF0FF;font-weight:600;font-size:.95em;
                             white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">
                          {html.escape(uploaded_file.name)}
                        </div>
                        <div style="color:#7C6FFF;font-size:.82em;margin-top:3px;font-weight:500;">
                          {size_str} · PDF ready for analysis
                        </div>
                      </div>
                      <div style="color:#00E676;font-size:1.3em;flex-shrink:0;">✓</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    # ── CTA button ─────────────────────────────────────────────────────────
    st.write("")
    _, btn_col, _ = st.columns([1, 4, 1])
    with btn_col:
        analyze_clicked = st.button(
            "Analyze Document →",
            disabled=(raw_bytes is None),
            type="primary",
            use_container_width=True,
            key="analyze_btn",
        )

    if analyze_clicked and raw_bytes is not None:
        st.session_state["filename"] = uploaded_file.name
        return raw_bytes

    return None


# ---------------------------------------------------------------------------
# render_progress
# ---------------------------------------------------------------------------

def render_progress(current: int, total: int, claim_text: str) -> None:
    """Render a progress indicator for claim verification."""
    pct = int(current / total * 100)
    truncated = html.escape(claim_text[:90] + ("…" if len(claim_text) > 90 else ""))
    st.markdown(
        f"""
        <div style="background:linear-gradient(160deg,#1A1D35,#12142A);
             border:1px solid #252848;border-radius:14px;padding:20px 24px;margin-bottom:8px;">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
            <span style="color:#EEF0FF;font-weight:600;font-size:.95em;">
              Verifying claim {current} of {total}
            </span>
            <span style="color:#7C6FFF;font-weight:700;font-size:.9em;">{pct}%</span>
          </div>
          <div style="background:#252848;border-radius:4px;height:6px;overflow:hidden;">
            <div style="height:100%;width:{pct}%;
                 background:linear-gradient(90deg,#7C6FFF,#00D4FF);
                 border-radius:4px;transition:width .3s ease;"></div>
          </div>
          <p style="color:#555980;font-size:12px;font-style:italic;margin:10px 0 0;">
            {truncated}
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# render_report
# ---------------------------------------------------------------------------

_VERDICT_COLORS = {
    "VERIFIED":   "#00E676",
    "INACCURATE": "#FFB300",
    "FALSE":      "#FF4444",
}

_VERDICT_ICONS = {
    "VERIFIED":   "✓",
    "INACCURATE": "⚠",
    "FALSE":      "✕",
}


def render_report(report: Report) -> None:
    """Render the full verification report."""

    verified    = report.summary.get("verified", 0)
    inaccurate  = report.summary.get("inaccurate", 0)
    false_count = report.summary.get("false", 0)
    trust_score = report.summary.get("trust_score", 0.0)

    if trust_score > 70:
        score_color = "#00E676"
        score_label = "High Accuracy"
        score_msg   = "This document appears largely accurate"
    elif trust_score >= 40:
        score_color = "#FFB300"
        score_label = "Mixed Accuracy"
        score_msg   = "This document contains some inaccuracies — verify key claims"
    else:
        score_color = "#FF4444"
        score_label = "Low Accuracy"
        score_msg   = "This document contains significant misinformation"

    score_pct = f"{trust_score:.1f}"
    st.html(
        f"<div style='background:linear-gradient(160deg,#1A1D35 0%,#12142A 100%);"
        f"border:1px solid #252848;border-radius:18px;padding:32px 28px;'>"
        f"<div style='display:flex;align-items:center;justify-content:center;gap:40px;flex-wrap:wrap;'>"
        f"<div style='flex-shrink:0;width:150px;height:150px;border-radius:50%;"
        f"background:conic-gradient(from -90deg, {score_color} 0% {score_pct}%, #252848 {score_pct}%);"
        f"display:flex;align-items:center;justify-content:center;'>"
        f"<div style='width:128px;height:128px;border-radius:50%;"
        f"background:linear-gradient(160deg,#1A1D35 0%,#12142A 100%);"
        f"display:flex;flex-direction:column;align-items:center;justify-content:center;gap:4px;'>"
        f"<span style='font-size:1.75em;font-weight:700;color:{score_color};line-height:1;'>{trust_score:.0f}%</span>"
        f"<span style='font-size:.72em;color:#9094C0;letter-spacing:.04em;'>Trust Score</span>"
        f"</div></div>"
        f"<div style='min-width:200px;'>"
        f"<div style='font-size:1.15em;font-weight:700;color:{score_color};margin-bottom:5px;'>{score_label}</div>"
        f"<p style='color:#9094C0;font-size:.88em;line-height:1.5;margin:0 0 16px;'>{score_msg}</p>"
        f"<div style='display:flex;gap:10px;flex-wrap:wrap;'>"
        f"<div style='background:rgba(0,230,118,.09);border:1px solid rgba(0,230,118,.22);"
        f"border-radius:10px;padding:10px 18px;text-align:center;min-width:72px;'>"
        f"<div style='font-size:1.45em;font-weight:700;color:#00E676;'>{verified}</div>"
        f"<div style='font-size:.76em;color:#9094C0;margin-top:2px;'>Verified</div></div>"
        f"<div style='background:rgba(255,179,0,.09);border:1px solid rgba(255,179,0,.22);"
        f"border-radius:10px;padding:10px 18px;text-align:center;min-width:72px;'>"
        f"<div style='font-size:1.45em;font-weight:700;color:#FFB300;'>{inaccurate}</div>"
        f"<div style='font-size:.76em;color:#9094C0;margin-top:2px;'>Inaccurate</div></div>"
        f"<div style='background:rgba(255,68,68,.09);border:1px solid rgba(255,68,68,.22);"
        f"border-radius:10px;padding:10px 18px;text-align:center;min-width:72px;'>"
        f"<div style='font-size:1.45em;font-weight:700;color:#FF4444;'>{false_count}</div>"
        f"<div style='font-size:.76em;color:#9094C0;margin-top:2px;'>False</div></div>"
        f"</div></div></div></div>"
    )

    st.caption(
        f"File: **{report.filename}** · Analyzed at {report.timestamp.strftime('%Y-%m-%d %H:%M UTC')}"
    )

    st.html(
        """
        <div style="margin:24px 0 16px;">
          <h3 style="color:#EEF0FF;font-weight:700;font-size:1.35em;
               letter-spacing:-0.01em;margin:0;">
            Detailed Findings
          </h3>
        </div>
        """
    )

    if not report.verdicts:
        st.html(
            """
            <div style="text-align:center;padding:56px 0;">
              <div style="font-size:3.5em;margin-bottom:12px;">🔍</div>
              <h3 style="color:#EEF0FF;margin:0 0 8px;font-size:1.2em;">
                No verifiable claims found
              </h3>
              <p style="color:#9094C0;font-size:.92em;max-width:440px;margin:0 auto;">
                This document may contain only opinions, narrative text, or non-factual content.
                Try uploading a document with specific statistics, dates, or figures.
              </p>
            </div>
            """
        )
        if st.button("Try Another PDF", key="empty_try_another"):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()
        return

    for verdict in report.verdicts:
        verdict_color = _VERDICT_COLORS.get(verdict.label, "#6c757d")
        verdict_icon  = _VERDICT_ICONS.get(verdict.label, "•")
        conf_pct      = int(verdict.confidence * 100)

        safe_label       = html.escape(verdict.label)
        safe_claim_type  = html.escape(verdict.claim.claim_type)
        safe_claim_text  = html.escape(verdict.claim.text)
        safe_explanation = html.escape(verdict.explanation)

        sources_html = " ".join(
            f'<a href="{html.escape(url)}" target="_blank" rel="noopener noreferrer"'
            f' style="color:#7C6FFF;font-size:12px;text-decoration:underline;margin-left:8px;">'
            f"Source {i + 1}</a>"
            for i, url in enumerate(verdict.sources)
        )

        real_value_html = ""
        if verdict.label in ("INACCURATE", "FALSE") and verdict.real_value:
            safe_rv = html.escape(verdict.real_value)
            real_value_html = (
                f'<div style="background:rgba(255,179,0,.08);border:1px solid rgba(255,179,0,.22);'
                f"border-radius:8px;padding:8px 14px;color:#FFB300;font-size:13px;margin:8px 0;\">"
                f"⚡ Actual value: {safe_rv}</div>"
            )

        st.html(
            f"""
            <div class="tl-verdict-card"
                 style="background:linear-gradient(160deg,#14162B 0%,#0F1122 100%);
                        border-left:4px solid {verdict_color};">
              <div style="display:flex;justify-content:space-between;
                   align-items:center;margin-bottom:12px;">
                <span style="display:inline-flex;align-items:center;gap:5px;
                     background:{verdict_color}18;color:{verdict_color};
                     border:1px solid {verdict_color}40;
                     border-radius:8px;padding:4px 12px;
                     font-size:12px;font-weight:700;letter-spacing:.04em;">
                  {verdict_icon} {safe_label}
                </span>
                <span style="background:#1E2240;color:#9094C0;
                     border:1px solid #252848;
                     border-radius:8px;padding:4px 10px;font-size:11px;">
                  {safe_claim_type}
                </span>
              </div>

              <div style="font-size:15px;color:#EEF0FF;margin-bottom:10px;
                   line-height:1.55;font-weight:500;">
                {safe_claim_text}
              </div>

              {real_value_html}

              <div style="color:#9094C0;font-size:13px;font-style:italic;
                   margin:8px 0 14px;line-height:1.5;">
                {safe_explanation}
              </div>

              <div style="display:flex;justify-content:space-between;align-items:center;
                   padding-top:12px;border-top:1px solid #1E2240;">
                <div style="display:flex;align-items:center;gap:8px;">
                  <div style="width:64px;height:4px;background:#1E2240;
                       border-radius:2px;overflow:hidden;">
                    <div style="height:100%;width:{conf_pct}%;
                         background:{verdict_color};border-radius:2px;"></div>
                  </div>
                  <span style="color:#9094C0;font-size:12px;">{conf_pct}% confidence</span>
                </div>
                <div>{sources_html}</div>
              </div>
            </div>
            """
        )


# ---------------------------------------------------------------------------
# render_download_buttons
# ---------------------------------------------------------------------------

def render_download_buttons(report: Report) -> None:
    """Render JSON and Markdown download buttons side by side."""

    verdicts_list = [
        {
            "claim_text":  v.claim.text,
            "claim_type":  v.claim.claim_type,
            "page_number": v.claim.page_number,
            "label":       v.label,
            "real_value":  v.real_value,
            "explanation": v.explanation,
            "confidence":  v.confidence,
            "sources":     v.sources,
        }
        for v in report.verdicts
    ]
    json_payload = json.dumps(
        {
            "filename":  report.filename,
            "timestamp": report.timestamp.isoformat(),
            "summary":   report.summary,
            "verdicts":  verdicts_list,
        },
        indent=2,
    )

    trust_score = report.summary.get("trust_score", 0.0)
    md_lines = [
        "## TruthLayer Report",
        "",
        f"**File:** {report.filename}",
        f"**Timestamp:** {report.timestamp.strftime('%Y-%m-%d %H:%M UTC')}",
        f"**Trust Score:** {trust_score:.0f}%",
        "",
        "### Summary",
        f"- Verified: {report.summary.get('verified', 0)}",
        f"- Inaccurate: {report.summary.get('inaccurate', 0)}",
        f"- False: {report.summary.get('false', 0)}",
        "",
        "### Verdicts",
        "",
    ]

    for idx, v in enumerate(report.verdicts, start=1):
        md_lines += [
            f"#### {idx}. {v.claim.text}",
            f"- **Label:** {v.label}",
            f"- **Type:** {v.claim.claim_type}",
            f"- **Page:** {v.claim.page_number}",
        ]
        if v.label in ("INACCURATE", "FALSE"):
            md_lines.append(f"- **Real value:** {v.real_value}")
        md_lines += [
            f"- **Explanation:** {v.explanation}",
            f"- **Confidence:** {int(v.confidence * 100)}%",
        ]
        if v.sources:
            md_lines.append("- **Sources:**")
            for url in v.sources:
                md_lines.append(f"  - {url}")
        md_lines.append("")

    markdown_payload = "\n".join(md_lines)

    json_col, md_col = st.columns(2)

    with json_col:
        st.download_button(
            label="⬇ Download JSON Report",
            data=json_payload,
            file_name="truthlayer_report.json",
            mime="application/json",
            use_container_width=True,
            key="dl_json",
        )

    with md_col:
        st.download_button(
            label="⬇ Download Markdown Report",
            data=markdown_payload,
            file_name="truthlayer_report.md",
            mime="text/markdown",
            use_container_width=True,
            key="dl_markdown",
        )


# ---------------------------------------------------------------------------
# render_error
# ---------------------------------------------------------------------------

def render_error(message: str, suggestion: str) -> None:
    """Render a friendly error state with a Try Again button."""
    st.warning(f"⚠️ {message}")
    st.write(suggestion)
    if st.button("Try Again"):
        st.session_state.clear()
        st.rerun()
