# backend/qr_routes.py
import time
import uuid

from flask import Blueprint, request, jsonify
import jwt

from .config import Config
from .db_config import db

qr_bp = Blueprint("qr", __name__)


def _get_current_user():
    """
    Decode JWT from Authorization: Bearer <token>.
    Returns payload dict or None.
    """
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None

    token = auth_header.split(" ", 1)[1].strip()
    try:
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
        return payload  # expected to contain at least: email, role
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


@qr_bp.route("/start", methods=["POST"])
def start_qr_session():
    """
    Teacher starts a QR session.
    Body JSON:
    {
      "classId": "CLS_...",
      "className": "Maths - Algebra",
      "subject": "Mathematics",
      "lat": 19.07,
      "lon": 72.87,
      "distanceLimit": 200,          # meters
      "durationMinutes": 5           # validity of QR
    }

    Response:
    {
      "session": { ...full session doc... },
      "qrPayload": { "sessionId": "QR_..." }
    }
    """
    user = _get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    if user.get("role") != "teacher":
        return jsonify({"error": "Only teachers can start QR sessions"}), 403

    data = request.get_json() or {}
    required = [
        "classId",
        "className",
        "subject",
        "lat",
        "lon",
        "distanceLimit",
        "durationMinutes",
    ]
    missing = [k for k in required if k not in data]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    now_ms = int(time.time() * 1000)
    duration_minutes = int(data["durationMinutes"])
    expiry_ms = now_ms + duration_minutes * 60_000

    session_id = "QR_" + uuid.uuid4().hex[:12]

    session_doc = {
        "sessionId": session_id,
        "teacherEmail": user["email"],
        "classId": data["classId"],
        "className": data["className"],
        "subject": data["subject"],
        "lat": float(data["lat"]),
        "lon": float(data["lon"]),
        "distanceLimit": float(data["distanceLimit"]),
        "expiry": expiry_ms,
        "createdAt": now_ms,
        "active": True,
    }

    db.collection("qr_sessions").document(session_id).set(session_doc)

    # This is what the frontend should encode inside the QR image
    qr_payload = {"sessionId": session_id}

    return jsonify({"session": session_doc, "qrPayload": qr_payload}), 200


@qr_bp.route("/session/<session_id>", methods=["GET"])
def get_qr_session(session_id: str):
    """
    Optional endpoint: fetch info about a QR session.
    Useful for debugging or future UI features.
    """
    doc = db.collection("qr_sessions").document(session_id).get()
    if not doc.exists:
        return jsonify({"error": "QR session not found"}), 404

    data = doc.to_dict()
    now_ms = int(time.time() * 1000)
    if data.get("expiry") and now_ms > data["expiry"]:
        data["active"] = False

    return jsonify(data), 200
