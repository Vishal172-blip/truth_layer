# Push TruthLayer to GitHub

## Step 1 — Create the repo on GitHub

1. Go to [github.com/new](https://github.com/new)
2. Repository name: `truthlayer`
3. Visibility: Public (required for free Streamlit Cloud deploy)
4. Do NOT initialise with README or .gitignore — the repo already has these
5. Click **Create repository**

## Step 2 — Push from your terminal

Run these commands in the `truth_layer/` directory:

```bash
git init
git add .
git commit -m "Initial commit: TruthLayer AI fact-check agent"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/truthlayer.git
git push -u origin main
```

Replace `YOUR_USERNAME` with your actual GitHub username.

## Step 3 — Verify

After pushing, open `https://github.com/YOUR_USERNAME/truthlayer` and confirm:

- `app.py` is visible at the root
- `assets/sample_trap.pdf` is present
- `.env` is NOT listed (it's gitignored)
- `.streamlit/secrets.toml` is NOT listed (it's gitignored)

## Next step

See [DEPLOY.md](DEPLOY.md) to deploy to Streamlit Community Cloud.
