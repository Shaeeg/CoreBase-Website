import logging
import os
import secrets
from datetime import timedelta
from functools import wraps

from dotenv import load_dotenv
from flask import Flask, jsonify, redirect, render_template, request, session, url_for
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from db import AnalyticsUnavailable, get_stats, record_click, record_page_view
from odoo_client import OdooClient, OdooConnectionError

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
if not os.environ.get("SECRET_KEY"):
    logger.warning("SECRET_KEY not set — admin sessions won't survive a restart.")
app.permanent_session_lifetime = timedelta(days=14)
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

allowed_origins = [o.strip() for o in os.environ.get("ALLOWED_ORIGINS", "*").split(",")]
CORS(app, resources={r"/api/*": {"origins": allowed_origins}})

limiter = Limiter(get_remote_address, app=app, default_limits=[])

_odoo_client = None


def get_odoo_client():
    global _odoo_client
    if _odoo_client is None:
        _odoo_client = OdooClient()
    return _odoo_client


@app.get("/")
@app.get("/healthz")
def health():
    return jsonify(status="ok")


@app.post("/api/contact")
@limiter.limit("10 per hour")
def contact():
    data = request.get_json(silent=True) or {}

    # Honeypot: a hidden field real visitors never fill in. Bots that fill
    # every field get a fake success without ever touching Odoo.
    if data.get("website"):
        return jsonify(success=True)

    name = (data.get("name") or "").strip()
    company = (data.get("company") or "").strip()
    phone = (data.get("phone") or "").strip()

    if not name or not company or not phone:
        return jsonify(success=False, error="name, company, and phone are all required."), 400

    try:
        lead_id = get_odoo_client().create_lead(name=name, company=company, phone=phone)
    except OdooConnectionError as exc:
        logger.error("Failed to create Odoo lead: %s", exc)
        return jsonify(success=False, error="Could not submit to our CRM right now. Please try again shortly."), 502

    return jsonify(success=True, lead_id=lead_id)


@app.post("/api/track/pageview")
@limiter.limit("60 per minute")
def track_pageview():
    data = request.get_json(silent=True) or {}
    path = (data.get("path") or "").strip()[:500]
    visitor_id = (data.get("visitor_id") or "").strip()[:100]

    if path and visitor_id:
        try:
            record_page_view(
                path=path,
                referrer=(data.get("referrer") or "").strip()[:500],
                visitor_id=visitor_id,
                user_agent=request.headers.get("User-Agent", "")[:300],
                lang=(data.get("lang") or "").strip()[:10],
            )
        except AnalyticsUnavailable as exc:
            logger.warning("Could not record page view: %s", exc)

    return jsonify(success=True)


@app.post("/api/track/click")
@limiter.limit("120 per minute")
def track_click():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()[:100]
    visitor_id = (data.get("visitor_id") or "").strip()[:100]

    if name and visitor_id:
        try:
            record_click(
                name=name,
                path=(data.get("path") or "").strip()[:500],
                visitor_id=visitor_id,
            )
        except AnalyticsUnavailable as exc:
            logger.warning("Could not record click: %s", exc)

    return jsonify(success=True)


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("admin"):
            return redirect(url_for("admin_login"))
        return view(*args, **kwargs)
    return wrapped


@app.get("/admin")
def admin_login():
    if session.get("admin"):
        return redirect(url_for("admin_dashboard"))
    return render_template("admin_login.html", error=None)


@app.post("/admin")
@limiter.limit("10 per minute")
def admin_login_submit():
    admin_password = os.environ.get("ADMIN_PASSWORD")
    submitted = request.form.get("password", "")

    if admin_password and secrets.compare_digest(submitted, admin_password):
        session.clear()
        session["admin"] = True
        session.permanent = True
        return redirect(url_for("admin_dashboard"))

    return render_template("admin_login.html", error="Incorrect password."), 401


@app.get("/admin/logout")
def admin_logout():
    session.clear()
    return redirect(url_for("admin_login"))


@app.get("/admin/dashboard")
@admin_required
def admin_dashboard():
    try:
        stats = get_stats()
        error = None
    except AnalyticsUnavailable as exc:
        stats = None
        error = str(exc)

    return render_template("admin_dashboard.html", stats=stats, error=error)


if __name__ == "__main__":
    app.run(port=int(os.environ.get("PORT", 5000)))
