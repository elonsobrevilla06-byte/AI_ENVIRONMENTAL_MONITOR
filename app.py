import os
import logging
from flask import Flask, render_template
import ee

from routes.country_bounds import country_bp
from routes.chat_bp import chat_bp
from routes.analysis_bp import analysis_bp
from routes.county_visits import country_visits_bp
from routes.admin import admin_bp
from database_models.country_bounds import get_country_bounds
from auth_middleware import jwt_required

ee.Initialize(project='golden-system-465607-e5')

# ── Logging setup ─────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "change-this-in-production")


# ── Blueprints ────────────────────────────────────────────────────────────────
app.register_blueprint(country_bp)
app.register_blueprint(chat_bp)
app.register_blueprint(analysis_bp)
app.register_blueprint(country_visits_bp)
app.register_blueprint(admin_bp)


# ── Public routes ─────────────────────────────────────────────────────────────

@app.route("/")
def home():
    data = get_country_bounds()
    raw = data["data"]
    countries = [
        {"country_code": row["country_code"], "bounds": row["bounds"]}
        for row in raw
    ]
    return render_template("index.html", countries=countries)


@app.route("/admin/login")
def admin_login():
    return render_template("admin_login.html")


# ── Protected routes (redirect to login without a valid JWT cookie) ────────────

@app.route("/admin/dashboard")
@jwt_required
def admin_dashboard():
    return render_template("dashboard.html")


@app.route("/admin/management")
@jwt_required
def admin_management():
    return render_template("admin_management.html")


@app.route("/admin/bounds")
@jwt_required
def admin_bounds():
    return render_template("admin_bounds.html")


if __name__ == "__main__":
    app.run(debug=True)