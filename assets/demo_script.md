# TruthLayer Demo Script

## Pre-Recording Setup
- App running at `localhost:8501` via `streamlit run app.py`
- `assets/sample_trap.pdf` saved locally and ready to drag-and-drop
- `.env` file has valid `GROQ_API_KEY` and `TAVILY_API_KEY` set (green dots visible in sidebar)
- Incognito browser window open, navigated to `http://localhost:8501` — landing page fully loaded
- Browser zoom set to 100%; sidebar collapsed
- Screen recorder open (Loom, OBS, or similar), resolution at 1920x1080 or 1280x720 minimum
- Mic check done; quiet environment confirmed
- Do a single dry run first so Streamlit's initial compile delay does not appear on camera

---

## Shot 1 — Landing Page (0–5 sec)

Show the full TruthLayer landing page in its resting state.

- Pan the camera across the entire viewport slowly: the animated blue-to-green gradient bar running across the top of the browser, the large **TruthLayer** heading, the subtitle *"Upload any PDF. We verify every claim against the live web."*
- Let the viewer read the three feature cards — **Instant Extraction**, **Live Verification**, **Trust Score** — without rushing.
- End the shot with the mouse hovering over the **Get Started →** button (do not click yet).

**Goal:** Establish what the product is in the first five seconds without saying a word.

---

## Shot 2 — File Upload (5–12 sec)

Click **Get Started →** and upload the demo PDF.

- Click **Get Started →**. The page transitions to the Upload view ("Upload your PDF").
- Click the file uploader area ("Drop your PDF here") or drag `sample_trap.pdf` directly onto it.
- The app confirms the upload with a blue info banner: `sample_trap.pdf · 0.0 MB`.
- Pause one beat on the confirmed filename so the viewer can read it.
- Click **Analyze Document →**. The button becomes the clear call to action — click it decisively.

**Goal:** Show that the entire input flow is a single file drop plus one button click.

---

## Shot 3 — Live Analysis (12–25 sec)

Let the analysis pipeline run on screen — do not cut away.

- After clicking Analyze, the progress bar appears immediately. Hold on it.
- The status line reads *"Verifying claim X of Y"* and the italic caption beneath it shows a truncated excerpt of the claim currently being checked — for example:
  - *"India's GDP in 2023 was $2.1 trillion..."*
  - *"The global smartphone market shipped 2.5 billion units in 2023..."*
  - *"Python — which was created in 1998 by Guido van Rossum..."*
  - *"OpenAI, which was founded in 2013..."*
- Let the bar fill in real time. The pipeline typically processes 8–12 claims in 20–40 seconds with Groq + Tavily.
- A toast notification pops up briefly: *"Found N verifiable claims — starting verification..."* — let it appear naturally.

**Goal:** Build anticipation and demonstrate that the tool is doing real work claim-by-claim, not a canned result.

---

## Shot 4 — Report Reveal (25–35 sec)

Scroll slowly through the completed report to show the full output.

- The progress bar disappears and the report renders. Start at the top with the three metric summary cards:
  - Green **Verified** count
  - Amber **Inaccurate** count
  - Red **False** count
- Pause on the large **Trust Score** percentage (likely 50–65% for this document) with its color-coded horizontal bar and the verdict message, e.g. *"This document contains some inaccuracies — verify key claims."*
- Scroll down to **Detailed Findings**. Linger on two or three verdict cards that showcase the range of verdicts:
  1. An **INACCURATE** card — e.g. India's GDP claimed as $2.1T. The amber left-border, the amber "✦ Actual value:" correction line, the explanation, and the source links are all visible.
  2. A **FALSE** card — e.g. Python created in 1998 (actual: 1991). The red left-border and the corrected value stand out clearly.
  3. A **VERIFIED** card — e.g. the US having 50 states, or World War II ending in 1945. The green left-border shows the tool correctly confirms true claims too.
- Each card also shows the claim type badge (STATISTIC, DATE, HISTORICAL FACT, etc.) and the confidence percentage.

**Goal:** Demonstrate the full output quality — colour-coded verdicts, corrected values, source links, confidence scores, and the overall Trust Score — in one smooth scroll.

---

## Shot 5 — Download (35–42 sec)

Show the export options at the bottom of the report.

- Scroll to the bottom of the page where the two download buttons appear side by side.
- Hover over **Download JSON Report** briefly, then hover over **Download Markdown Report**.
- Click **Download Markdown Report** to trigger the browser download — the file `truthlayer_report.md` starts downloading.
- End the recording here or fade out. Do not show the file system or the file contents — the download action itself is the payoff.

**Goal:** Close the loop by showing that the output is portable and usable outside the app.

---

## Narration / Caption Script

Use these lines as either spoken narration (VO) or on-screen captions timed to each shot.

| Time | Shot | Line |
|------|------|------|
| 0–5s | Landing Page | *"TruthLayer — automated fact-checking for any PDF."* |
| 5–8s | Upload starts | *"Drop in a document..."* |
| 8–12s | Analyze clicked | *"...and hit Analyze."* |
| 12–18s | Progress bar | *"TruthLayer pulls every verifiable claim — statistics, dates, named figures — and checks each one against the live web."* |
| 18–25s | Claims scrolling | *"Each claim is searched independently. No cached results."* |
| 25–28s | Metric cards | *"The report shows exactly how many claims were verified, flagged as inaccurate, or found to be false."* |
| 28–33s | Trust Score | *"A single Trust Score summarises the document's overall accuracy."* |
| 33–38s | Verdict cards | *"Every finding includes the corrected value, an explanation, and links to the sources that decided the verdict."* |
| 38–42s | Download | *"Export the full report as JSON or Markdown — ready to share or archive."* |

**Alternative one-liner caption for social media clips (under 15 sec):**
> *"Upload any PDF. TruthLayer checks every claim against the live web and tells you what's wrong — and why."*

---

## Tips for a Clean Recording

1. **Do the dry run first.** Streamlit's first compile on a cold start can add a 2–3 second pause. Run the analysis once before recording so the cache is warm and the LLM connection is established.

2. **Keep the sidebar collapsed.** The sidebar shows the API provider status dots, which is useful for a technical audience but clutters a quick demo. Collapse it before recording unless your audience is developers.

3. **Move the mouse intentionally.** Hover, pause, then click. Rapid or jittery mouse movement looks unconfident on camera. Place the cursor on the next target before the current action finishes.

4. **Do not trim the analysis wait.** The live progress bar building in real time is the most compelling proof that TruthLayer is doing real work. Cutting it out or speeding it up undermines credibility. If the wait is longer than 30 seconds, consider switching to Tavily (faster than DuckDuckGo) or reducing `MAX_CLAIMS` in `config.py` temporarily for the recording.

5. **Choose which verdict cards to linger on before you record.** Know in advance that the India GDP card and the Python founding-year card are the two strongest examples of INACCURATE and FALSE respectively. Scroll past the others at a normal pace and slow down only for these.

6. **Record at 1x speed, export at 1x speed.** Speed-ramping or jump cuts make the pipeline feel fake. The entire demo fits comfortably inside 45 seconds at normal pace.

7. **Test your audio before the final take.** If narrating, record a 10-second test clip and play it back before committing. Room echo and mic distance are the two most common problems in screen-recording audio.
