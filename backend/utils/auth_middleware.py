# backend/utils/auth_middleware.py
from functools import wraps
from flask import request, jsonify, current_app
import jwt


def require_token(roles=None):
    """
    Decorator to protect routes.
    roles: list like ["teacher"] or ["student", "teacher"].
           If None, just checks that token is valid.
    """
    roles = roles or []

    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            auth_header = request.headers.get("Authorization", "")

            # Expect header: "Bearer <token>"
            if not auth_header.startswith("Bearer "):
                return jsonify({"error": "Missing or invalid Authorization header"}), 401

            token = auth_header.split(" ", 1)[1].strip()
            try:
                payload = jwt.decode(
                    token,
                    current_app.config["SECRET_KEY"],
                    algorithms=["HS256"],
                )
            except jwt.ExpiredSignatureError:
                return jsonify({"error": "Token expired"}), 401
            except jwt.InvalidTokenError:
                return jsonify({"error": "Invalid token"}), 401

            # Check roles if required
            if roles and payload.get("role") not in roles:
                return jsonify({"error": "Insufficient permissions"}), 403

            # Attach user info to request so handlers can use it
            request.user = payload
            return f(*args, **kwargs)

        return wrapper

    return decorator
