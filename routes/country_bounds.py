from flask import Blueprint, jsonify, request
from database_models.country_bounds import get_country_bounds, create_country_bounds, update_country_bounds, delete_country_bounds

country_bp = Blueprint("country_bp", __name__, url_prefix="/api/country_bounds")


@country_bp.route("/", methods=["GET"])
def fetch_countries():
    try:
        country_code = request.args.get("code")  # ?code=PH
        result = get_country_bounds(country_code)
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@country_bp.route("/", methods=["POST"])
def add_country():
    try:
        data = request.get_json()

        if not data or "country_code" not in data or "bounds" not in data:
            return jsonify({
                "status": "error",
                "message": "country_code and bounds are required"
            }), 400

        country_code = data["country_code"].strip().upper()
        bounds = data["bounds"]

        # Validate bounds structure: [[sw_lat, sw_lng], [ne_lat, ne_lng]]
        if (not isinstance(bounds, list) or len(bounds) != 2
                or not all(isinstance(c, list) and len(c) == 2 for c in bounds)):
            return jsonify({
                "status": "error",
                "message": "bounds must be [[sw_lat, sw_lng], [ne_lat, ne_lng]]"
            }), 400

        result = create_country_bounds(country_code, bounds)
        status_code = 201 if result.get("status") == "success" else 500
        return jsonify(result), status_code

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@country_bp.route("/<int:country_id>", methods=["PUT"])
def update_country(country_id):
    try:
        data = request.get_json()

        if not data:
            return jsonify({"status": "error", "message": "No data provided"}), 400

        country_code = data.get("country_code")
        if country_code:
            country_code = country_code.strip().upper()

        bounds = data.get("bounds")

        result = update_country_bounds(country_id, country_code=country_code, bounds=bounds)
        status_code = 200 if result.get("status") == "success" else 404 if "not found" in result.get("message", "") else 500
        return jsonify(result), status_code

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@country_bp.route("/<int:country_id>", methods=["DELETE"])
def remove_country(country_id):
    try:
        result = delete_country_bounds(country_id)
        status_code = 200 if result.get("status") == "success" else 404 if "not found" in result.get("message", "") else 500
        return jsonify(result), status_code
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500