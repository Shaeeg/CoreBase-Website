import logging
import os

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from odoo_client import OdooClient, OdooConnectionError

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

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


if __name__ == "__main__":
    app.run(port=int(os.environ.get("PORT", 5000)))
