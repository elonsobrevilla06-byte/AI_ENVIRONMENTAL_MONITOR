from flask import Blueprint, jsonify, request
from database_models.country_bounds  import get_country_bounds

country_bp = Blueprint(
    "country_bp",
    __name__,
    url_prefix="/api/countries"
)


@country_bp.route("/", methods=["GET"])
def fetch_countries():
    try:
        country_code = request.args.get("code")  # ?code=PH

        result = get_country_bounds(country_code)

        return jsonify(result)

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        })