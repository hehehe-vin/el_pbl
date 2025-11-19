# backend/attendance_routes.py
import time
import math

from flask import Blueprint, request, jsonify
import jwt

from .config import Config
from .db_config import db

attendance_bp = Blueprint("attendance", __name__)


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
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def _haversine_meters(lat1, lon1, lat2, lon2):
    """
    Distance between two lat/lon points in meters.
    """
    R = 6371000  # Earth radius meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(
        dlambda / 2
    ) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


@attendance_bp.route("/mark", methods=["POST"])
def mark_attendance():
    """
    Student marks attendance by scanning QR.

    Body JSON:
    {
      "sessionId": "QR_...",
      "lat": 19.07,
      "lon": 72.87,
      "device": "Android" or "Web",
      "studentName": "optional, for display",
      "rollno": "optional"
    }

    Uses:
    - QR session from qr_sessions collection
    - Student identity from JWT token (email + role)
    """

    user = _get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    if user.get("role") != "student":
        return jsonify({"error": "Only students can mark attendance"}), 403

    body = request.get_json() or {}
    session_id = body.get("sessionId")
    lat = body.get("lat")
    lon = body.get("lon")
    device = body.get("device", "web")
    student_name = body.get("studentName")
    rollno = body.get("rollno")

    if not session_id or lat is None or lon is None:
        return jsonify({"error": "sessionId, lat and lon are required"}), 400

    # Fetch QR session
    session_doc = db.collection("qr_sessions").document(session_id).get()
    if not session_doc.exists:
        return jsonify({"error": "Invalid session"}), 404

    session = session_doc.to_dict()
    now_ms = int(time.time() * 1000)

    if session.get("expiry") and now_ms > session["expiry"]:
        return jsonify({"error": "Session expired"}), 400

    # Distance check
    try:
        lat = float(lat)
        lon = float(lon)
        teacher_lat = float(session["lat"])
        teacher_lon = float(session["lon"])
    except (ValueError, TypeError, KeyError):
        return jsonify({"error": "Invalid coordinates"}), 400

    distance_limit = float(session.get("distanceLimit", 999999))
    distance = _haversine_meters(lat, lon, teacher_lat, teacher_lon)

    if distance > distance_limit:
        return jsonify(
            {
                "error": "too_far",
                "message": "Student is outside allowed distance",
                "distance": distance,
                "distanceLimit": distance_limit,
            }
        ), 400

    # Build attendance record
    timestamp_ms = now_ms
    date_str = time.strftime("%Y-%m-%d", time.localtime(timestamp_ms / 1000.0))
    time_str = time.strftime("%H:%M", time.localtime(timestamp_ms / 1000.0))

    record = {
        "sessionId": session_id,
        "classId": session["classId"],
        "className": session.get("className"),
        "subject": session.get("subject"),
        "teacherEmail": session.get("teacherEmail"),

        "studentEmail": user["email"],
        "studentName": student_name,
        "rollno": rollno,

        "status": "Present",
        "timestamp": timestamp_ms,
        "date": date_str,
        "time": time_str,

        "device": device,
        "distanceMeters": distance,
        "studentLocation": {
            "lat": lat,
            "lon": lon,
        },
    }

    db.collection("attendance_records").add(record)

    return jsonify({"ok": True, "record": record}), 200


@attendance_bp.route("/class/<class_id>", methods=["GET"])
def get_attendance_for_class(class_id: str):
    """
    Teacher: get all attendance for a class.
    Optional query param: ?date=YYYY-MM-DD

    Frontend:
      - schedule.html
      - find.html
    """

    user = _get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    if user.get("role") != "teacher":
        return jsonify({"error": "Only teachers can view class attendance"}), 403

    date_filter = request.args.get("date")

    query = db.collection("attendance_records").where("classId", "==", class_id)

    # Optionally restrict to this teacher's classes
    # (remove this filter if multiple teachers share classes)
    query = query.where("teacherEmail", "==", user["email"])

    if date_filter:
        query = query.where("date", "==", date_filter)

    docs = query.stream()
    results = []
    for d in docs:
        obj = d.to_dict()
        obj["id"] = d.id
        results.append(obj)

    return jsonify(results), 200


@attendance_bp.route("/student", methods=["GET"])
def get_attendance_for_student():
    """
    Student: see all their own attendance.

    Used by: attendance.html (student view)
    """

    user = _get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    if user.get("role") != "student":
        return jsonify({"error": "Only students can view their own attendance"}), 403

    email = user["email"]
    query = db.collection("attendance_records").where("studentEmail", "==", email)

    docs = query.stream()
    results = []
    for d in docs:
        obj = d.to_dict()
        obj["id"] = d.id
        results.append(obj)

    return jsonify(results), 200
