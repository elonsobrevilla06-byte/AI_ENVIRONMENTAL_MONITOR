import os
import datetime
from flask import Blueprint, jsonify, request, make_response
from database_models.admin import get_admin_accounts, create_admin_account, update_admin_account, delete_admin_account
from werkzeug.security import generate_password_hash, check_password_hash
from auth_middleware import protect_api
import jwt

SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "change-this-in-production")

admin_bp = Blueprint("admin_bp", __name__, url_prefix="/api/admin")


# ── Public ────────────────────────────────────────────────────────────────────

@admin_bp.route("/login", methods=["POST"])
def login_admin():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"status": "error", "message": "No data"}), 400

        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify({"status": "error", "message": "email and password required"}), 400

        result = get_admin_accounts()
        admins = result.get("data") or []

        admin = next((a for a in admins if a.get("email") == email), None)

        if not admin:
            return jsonify({"status": "error", "message": "Admin not found"}), 401

        stored_hash = admin.get("password_hash")
        if not stored_hash:
            return jsonify({"status": "error", "message": "Password hash missing in database"}), 500

        if not check_password_hash(stored_hash, password):
            return jsonify({"status": "error", "message": "Wrong password"}), 401

        # ── Issue JWT ──────────────────────────────────────────────────────────
        payload = {
            "sub": str(admin["id"]),
            "username": admin["username"],
            "email": admin["email"],
            "iat": datetime.datetime.utcnow(),
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=8),
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

        response = make_response(jsonify({
            "status": "success",
            "message": "Login successful",
            "admin": {
                "id": admin["id"],
                "username": admin["username"],
                "email": admin["email"],
            }
        }))

        # httpOnly prevents JavaScript from reading the cookie (XSS protection)
        response.set_cookie(
            "access_token",
            token,
            httponly=True,
            secure=False,       # Cloudflare handles HTTPS; Flask sees HTTP internally
            samesite="Lax",
            max_age=8 * 3600,   # match JWT expiry (8 h)
        )

        return response

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@admin_bp.route("/logout", methods=["POST"])
def logout_admin():
    response = make_response(jsonify({"status": "success", "message": "Logged out"}))
    response.delete_cookie("access_token")
    return response


# ── Protected ─────────────────────────────────────────────────────────────────

@admin_bp.route("/", methods=["GET"])
@protect_api
def fetch_admins():
    try:
        admin_id = request.args.get("id")
        result = get_admin_accounts(admin_id)
        return jsonify(result)

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@admin_bp.route("/", methods=["POST"])
@protect_api
def add_admin():
    try:
        data = request.get_json()

        if not data or "username" not in data or "email" not in data or "password" not in data:
            return jsonify({
                "status": "error",
                "message": "username, email, and password are required"
            }), 400

        username = data["username"]
        email = data["email"]
        password = data["password"]

        password_hash = generate_password_hash(password)
        result = create_admin_account(username, email, password_hash)
        return jsonify(result)

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@admin_bp.route("/<int:admin_id>", methods=["PUT"])
@protect_api
def update_admin(admin_id):
    try:
        data = request.get_json()

        if not data:
            return jsonify({"status": "error", "message": "No data provided"}), 400

        update_fields = {}

        if data.get("username"):
            update_fields["username"] = data["username"]

        if data.get("email"):
            update_fields["email"] = data["email"]

        if data.get("password"):
            update_fields["password_hash"] = generate_password_hash(data["password"])

        if data.get("is_active") is not None:
            update_fields["is_active"] = data["is_active"]

        if not update_fields:
            return jsonify({"status": "error", "message": "No valid fields to update"}), 400

        result = update_admin_account(admin_id, update_fields)
        return jsonify(result)

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@admin_bp.route("/<int:admin_id>", methods=["DELETE"])
@protect_api
def remove_admin(admin_id):
    try:
        result = delete_admin_account(admin_id)
        return jsonify(result)

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500