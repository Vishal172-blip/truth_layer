## What does this PR do?

Brief description of the change and why it's needed.

## How was it tested?

- [ ] Ran `streamlit run app.py` and tested the affected feature manually
- [ ] Uploaded `assets/sample_trap.pdf` and verified verdict output is unchanged
- [ ] Checked that all imports still work: `python -c "from core import FactCheckPipeline"`
- [ ] Confirmed no new secrets or API keys are hardcoded

## Checklist

- [ ] No `.env` or `secrets.toml` included in the diff
- [ ] `requirements.txt` updated if new packages added
- [ ] No new mutable default arguments introduced in dataclasses or functions
