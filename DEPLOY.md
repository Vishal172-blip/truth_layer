# Deploy TruthLayer to Streamlit Community Cloud

## Prerequisites

- GitHub account with the `truthlayer` repo pushed to it
- Free accounts at: [groq.com](https://console.groq.com), [openrouter.ai](https://openrouter.ai), [tavily.com](https://tavily.com)

## Steps

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click **New app**
4. Repository: `YOUR_USERNAME/truthlayer`
5. Branch: `main`
6. Main file path: `app.py`
7. Click **Advanced settings**
8. Under **Secrets**, paste exactly:

```toml
GROQ_API_KEY = "gsk_your_actual_key"
OPENROUTER_API_KEY = "sk-or-your_actual_key"
TAVILY_API_KEY = "tvly-your_actual_key"
```

9. Click **Save**
10. Click **Deploy**
11. Wait 2-3 minutes for the first deploy to complete
12. Your app URL will be: `https://YOUR_USERNAME-truthlayer-app-XXXXX.streamlit.app`

## Verify deploy worked

- Open the URL
- You should see the TruthLayer landing page with the "Get Started" button
- Upload `assets/sample_trap.pdf`
- Wait ~60-90 seconds for the pipeline to run
- Verify at least 3 claims are marked **INACCURATE** or **FALSE**

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| App shows "module not found" | requirements.txt missing a package | Add the package and redeploy |
| All claims show FALSE | API key not set | Check Secrets in app dashboard |
| App won't start | Syntax error in secrets | Ensure keys are in `KEY = "value"` format |
| Slow first load | Cold start | Normal — subsequent loads are faster |

## Notes on secrets handling

Streamlit Cloud injects secrets from the dashboard as environment variables. The app
reads them with `os.getenv()` in `config.py` — no code changes needed for cloud vs local.
On local, the same keys come from `.env` via `python-dotenv`. The mechanism is identical.
