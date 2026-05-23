import os
import logging
from functools import wraps
from flask import request, redirect, url_for
import jwt

SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "change-this-in-production")

logger = logging.getLogger(__name__)

# Routes that don't need a token
PUBLIC_ROUTES = {"/", "/admin/login"}


def jwt_required(f):
    """
    Decorator that protects a route with JWT auth.
    Reads the token from the 'access_token' httpOnly cookie.
    Redirects to '/admin/login' if the token is missing or invalid.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get("access_token")

        if not token:
            logger.warning("[jwt_required] No access_token cookie found — redirecting to login")
            return redirect(url_for("home"))

        try:
            decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            logger.debug("[jwt_required] Token valid for sub=%s", decoded.get("sub"))
        except jwt.ExpiredSignatureError:
            logger.warning("[jwt_required] Token expired — redirecting to login")
            return redirect(url_for("home"))
        except jwt.InvalidTokenError as e:
            logger.warning("[jwt_required] Invalid token (%s) — redirecting to login", e)
            return redirect(url_for("home"))

        return f(*args, **kwargs)

    return decorated


def protect_api(f):
    """
    Decorator for API (JSON) endpoints.
    Returns 401 JSON instead of a redirect when the token is missing/invalid.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get("access_token")

        if not token:
            return {"status": "error", "message": "Unauthorized"}, 401

        try:
            jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return {"status": "error", "message": "Token expired"}, 401
        except jwt.InvalidTokenError:
            return {"status": "error", "message": "Invalid token"}, 401

        return f(*args, **kwargs)

    return decorated