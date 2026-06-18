## Demo

The quickest way to see TruthLayer in action is to run it against `assets/sample_trap.pdf` — a four-page "Global Technology & Market Report 2024" from a fictional Horizon Research Institute. The document contains a deliberate mix of correct facts and quietly wrong statistics, making it an ideal stress-test for the pipeline.

1. **Start the app** — run `streamlit run app.py` and open `http://localhost:8501`. The landing page loads with the TruthLayer heading, three feature cards (Instant Extraction, Live Verification, Trust Score), and a single **Get Started →** button.

2. **Upload the PDF** — click **Get Started →**, then drop `assets/sample_trap.pdf` onto the file uploader. The app confirms the filename and file size in a blue banner. Click **Analyze Document →** to begin.

3. **Watch the live pipeline** — a progress bar tracks each claim as it is searched and judged. The caption beneath the bar shows the claim currently under review, for example: *"India's GDP in 2023 was $2.1 trillion..."* or *"Python — which was created in 1998 by Guido van Rossum..."* The pipeline typically finishes in 20–40 seconds.

4. **Read the report** — the results page opens with a summary row (Verified / Inaccurate / False counts), a colour-coded Trust Score, and a scrollable list of verdict cards. Each card shows the original claim, the verdict label with a colour-coded left border, the corrected real value where applicable, a plain-language explanation, a confidence percentage, and numbered source links. Expect the sample PDF to score roughly 50–65%, reflecting a document with real errors embedded in otherwise plausible content.

5. **Export the findings** — two download buttons at the bottom of the report let you save the full output as `truthlayer_report.json` (machine-readable, suitable for downstream processing) or `truthlayer_report.md` (human-readable, suitable for sharing or pasting into a brief).

> *"TruthLayer pulls every verifiable claim — statistics, dates, named figures — and checks each one against the live web. Each claim is searched independently. No cached results."*

> *"Every finding includes the corrected value, an explanation, and links to the sources that decided the verdict."*

**About the sample PDF:** `assets/sample_trap.pdf` is a purpose-built test document. It intentionally contains several wrong figures — including a significantly understated India GDP, an incorrect founding year for OpenAI, a wrong creation year for Python, and an inflated global smartphone shipment figure — embedded alongside a number of genuinely accurate facts such as the US state count, the end of World War II, and the speed of light. This mixed-accuracy design exercises all three verdict types (VERIFIED, INACCURATE, FALSE) in a single analysis run.
