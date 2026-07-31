# CoreBase Contact Form Backend

A small Flask API with one job: take contact-form submissions from
corebase.az and create a `crm.lead` in Odoo via XML-RPC.

## Endpoints

- `POST /api/contact` — body: `{ "name": "...", "company": "...", "phone": "..." }`.
  Returns `{ "success": true, "lead_id": 123 }` or `{ "success": false, "error": "..." }`.
- `GET /healthz` — plain health check for uptime monitors / host health checks.

## Required environment variables

See `.env.example`. You'll need an Odoo API key (Settings → Users →
your user → Account Security → New API Key) rather than your login
password.

| Variable | Description |
|---|---|
| `ODOO_URL` | Base URL of your Odoo instance, e.g. `https://yourcompany.odoo.com` |
| `ODOO_DB` | Database name |
| `ODOO_USERNAME` | Login of the Odoo user the API key belongs to |
| `ODOO_API_KEY` | API key for that user |
| `ALLOWED_ORIGINS` | Comma-separated origins allowed to call the API (your live site + localhost for testing) |

## Running locally

```bash
cd backend
python3 -m venv venv
source venv/bin/activate   # venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env       # then fill in your real Odoo credentials
python3 app.py
```

Test it:

```bash
curl -X POST http://localhost:5000/api/contact \
  -H "Content-Type: application/json" \
  -d '{"name":"Test User","company":"Test Co","phone":"+994000000000"}'
```

## Deploying to Render (free tier)

1. Push this repo to GitHub (already done).
2. On [render.com](https://render.com), **New → Web Service**, connect
   this repository.
3. Set **Root Directory** to `backend`.
4. Build command: `pip install -r requirements.txt`
5. Start command: `gunicorn app:app`
6. Add the environment variables from the table above under the
   service's **Environment** tab (don't upload `.env` — Render doesn't
   need it, the dashboard vars replace it).
7. Deploy. Render gives you a URL like
   `https://corebase-backend.onrender.com`.
8. Update `CONTACT_API_URL` in `static/js/main.js` (repo root) to that
   URL, then commit and push — the static frontend is served
   separately via GitHub Pages.

Note: Render's free tier spins the service down after 15 minutes of
inactivity. The first request after idling takes ~30-60 seconds to
wake up; subsequent ones are fast. Fine for an occasional contact
form; upgrade to a paid instance if that delay becomes a problem.
