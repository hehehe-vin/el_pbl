import uuid
import time
from backend.utils.firestore_client import set_doc, get_doc

def create_qr_session(teacher_email, class_id, location, distance_limit, duration_minutes):
    session_id = "QR_" + uuid.uuid4().hex[:12]

    expiry = int(time.time() * 1000) + duration_minutes * 60000

    data = {
        "sessionId": session_id,
        "teacherEmail": teacher_email,
        "classId": class_id,
        "lat": location["lat"],
        "lon": location["lon"],
        "distanceLimit": distance_limit,
        "expiry": expiry,
        "createdAt": int(time.time() * 1000)
    }

    set_doc("qr_sessions", session_id, data)
    return data

def get_session(session_id):
    doc = get_doc("qr_sessions", session_id)
    if not doc.exists:
        return None
    return doc.to_dict()
