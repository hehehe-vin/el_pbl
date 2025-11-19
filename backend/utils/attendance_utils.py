import time
import math
from backend.utils.firestore_client import add_to_collection

def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

def write_attendance(session, student):
    data = {
        "classId": session["classId"],
        "sessionId": session["sessionId"],
        "studentEmail": student["email"],
        "studentName": student["name"],
        "rollno": student.get("rollno"),
        "timestamp": int(time.time() * 1000),
        "date": time.strftime("%Y-%m-%d"),
        "status": "Present",
        "distance": student["distance"],
        "lat": student["lat"],
        "lon": student["lon"]
    }
    add_to_collection("attendance_records", data)
    return data
