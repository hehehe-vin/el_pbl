# backend/auth_routes.py

from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import time

from .config import Config
from .db_config import db

auth_bp = Blueprint("auth", __name__)


def _make_token(email: str, role: str):
    """Create a signed JWT for the user."""
    payload = {
        "email": email,
        "role": role,
        "iat": int(time.time()),
        "exp": int(time.time()) + 7 * 24 * 3600,  # 7 days
    }
    token = jwt.encode(payload, Config.SECRET_KEY, algorithm="HS256")
    # PyJWT >= 2 returns str; older returns bytes
    if isinstance(token, bytes):
        token = token.decode("utf-8")
    return token


@auth_bp.route("/signup", methods=["POST"])
def signup():
    """
    Body:
      { "name": "...", "email": "...", "password": "...", "role": "teacher|student" }
    """
    try:
        data = request.get_json() or {}

        name = (data.get("name") or "").strip()
        email = (data.get("email") or "").strip().lower()
        password = data.get("password") or ""
        role = data.get("role") or ""

        if role not in ("teacher", "student"):
            return jsonify({"error": "Invalid role"}), 400

        if not name or not email or not password:
            return jsonify({"error": "All fields are required"}), 400

        # Firestore doc: users/<email>
        user_ref = db.collection("users").document(email)
        snap = user_ref.get()
        if snap.exists:
            return jsonify({"error": "User already exists"}), 409

        password_hash = generate_password_hash(password)

        user_doc = {
            "name": name,
            "email": email,
            "role": role,
            "passwordHash": password_hash,
            "createdAt": int(time.time() * 1000),
        }

        user_ref.set(user_doc)

        token = _make_token(email, role)

        return jsonify({
            "token": token,
            "email": email,
            "role": role,
            "name": name
        }), 200

    except Exception as e:
        # This will print in your terminal AND send an error message to the browser
        print("SIGNUP ERROR:", repr(e))
        return jsonify({"error": f"Internal error: {type(e).__name__}: {str(e)}"}), 500



@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Body:
      { "email": "...", "password": "..." }
    """
    try:
        data = request.get_json() or {}

        email = (data.get("email") or "").strip().lower()
        password = data.get("password") or ""

        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400

        user_ref = db.collection("users").document(email)
        snap = user_ref.get()
        if not snap.exists:
            return jsonify({"error": "User not found"}), 404

        user = snap.to_dict() or {}
        stored_hash = user.get("passwordHash", "")

        if not check_password_hash(stored_hash, password):
            return jsonify({"error": "Incorrect password"}), 401

        role = user.get("role", "student")
        name = user.get("name", "")

        token = _make_token(email, role)

        return jsonify({
            "token": token,
            "email": email,
            "role": role,
            "name": name
        }), 200

    except Exception as e:
        print("LOGIN ERROR:", repr(e))
        return jsonify({"error": f"Internal error: {type(e).__name__}: {str(e)}"}), 500
