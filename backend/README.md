# CoreBase Contact Form Backend

A small Flask API with two jobs: take contact-form submissions from
corebase.az and create a `crm.lead` in Odoo via XML-RPC, and record
anonymous page-view/click analytics viewable from a password-protected
`/admin` dashboard.

## Endpoints

- `POST /api/contact` — body: `{ "name": "...", "company": "...", "phone": "..." }`.
  Returns `{ "success": true, "lead_id": 123 }` or `{ "success": false, "error": "..." }`.
- `POST /api/track/pageview` — body: `{ "path", "referrer", "visitor_id", "lang" }`. Called
  automatically by `static/js/main.js` on every page load.
- `POST /api/track/click` — body: `{ "name", "path", "visitor_id" }`. Called on phone/email
  link clicks, contact form submissions, and any element with a `data-track="..."` attribute.
- `GET /admin` — login form for the analytics dashboard.
- `GET /admin/dashboard` — page views, unique visitors, top pages/clicks, 14-day trend.
  Requires signing in at `/admin` first.
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
| `DATABASE_URL` | Postgres connection string for analytics (free tier from [Neon](https://neon.tech) or [Supabase](https://supabase.com) works fine). Tables are created automatically on first use. |
| `ADMIN_PASSWORD` | Password for the `/admin` dashboard. |
| `SECRET_KEY` | Random string used to sign the admin session cookie — generate with `python -c "import secrets; print(secrets.token_hex(32))"`. Without it, admin sessions get invalidated every time the server restarts. |

If `DATABASE_URL` isn't set, `/api/track/*` calls silently no-op (the
site keeps working) and `/admin/dashboard` shows an "analytics
unavailable" message instead of crashing.

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
