from flask import Blueprint, jsonify, request
from database_models.country_visits import get_country_visits, get_this_month_country_visits, get_today_country_visits, add_country_visit

country_visits_bp = Blueprint("country_visits_bp",__name__, url_prefix="/api/country_visits")



@country_visits_bp.route("/", methods=["GET"])
def fetch_country_visits():
    result = get_country_visits()
    return jsonify(result)

@country_visits_bp.route("/daily", methods=["GET"])
def fetch_daily_country_visits():
    result = get_today_country_visits()
    print(result)
    return jsonify(result)

@country_visits_bp.route("/monthly", methods=["GET"])
def fetch_monthly_country_visits():
    result = get_this_month_country_visits()
    return jsonify(result)




@country_visits_bp.route("/", methods=["POST"])
def create_country_visit():
    data = request.get_json()

    if not data or "country_code" not in data:
        return jsonify({
            "status": "error",
            "message": "country_code is required"
        }), 400

    country_code = data["country_code"]

    result = add_country_visit(country_code)
    return jsonify(result)