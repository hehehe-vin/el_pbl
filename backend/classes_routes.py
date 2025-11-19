# backend/classes_routes.py
from flask import Blueprint, request, jsonify
from .db_config import db
from .utils.auth_middleware import require_token
import datetime
import uuid

classes_bp = Blueprint("classes", __name__)


@classes_bp.route("/", methods=["GET"])
@require_token(roles=["teacher"])
def get_my_classes():
    teacher_email = request.user["email"]
    classes_ref = db.collection("classes").where("teacherEmail", "==", teacher_email).get()
    classes = []
    for c in classes_ref:
        obj = c.to_dict()
        obj["id"] = c.id
        # convert timestamp to ISO string for frontend, if present
        if isinstance(obj.get("createdAt"), datetime.datetime):
            obj["createdAt"] = obj["createdAt"].isoformat()
        classes.append(obj)
    return jsonify(classes), 200


@classes_bp.route("/", methods=["POST"])
@require_token(roles=["teacher"])
def create_class():
    data = request.get_json() or {}
    name = data.get("name")
    subject = data.get("subject")

    if not name or not subject:
        return jsonify({"error": "name and subject required"}), 400

    teacher_email = request.user["email"]
    class_id = str(uuid.uuid4())
    now = datetime.datetime.utcnow()

    doc = {
        "name": name,
        "subject": subject,
        "teacherEmail": teacher_email,
        "createdAt": now,
    }

    db.collection("classes").document(class_id).set(doc)
    doc["id"] = class_id
    doc["createdAt"] = now.isoformat()
    return jsonify(doc), 201


@classes_bp.route("/<class_id>", methods=["PUT"])
@require_token(roles=["teacher"])
def update_class(class_id):
    data = request.get_json() or {}
    updates = {}
    if "name" in data:
        updates["name"] = data["name"]
    if "subject" in data:
        updates["subject"] = data["subject"]

    if not updates:
        return jsonify({"error": "nothing to update"}), 400

    db.collection("classes").document(class_id).update(updates)
    return jsonify({"message": "class updated"}), 200


@classes_bp.route("/<class_id>", methods=["DELETE"])
@require_token(roles=["teacher"])
def delete_class(class_id):
    # delete class
    db.collection("classes").document(class_id).delete()
    # optionally: delete attendance of that class later
    return jsonify({"message": "class deleted"}), 200
