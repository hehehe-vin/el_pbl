# backend/__init__.py
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import os

from .config import Config
from .auth_routes import auth_bp
from .classes_routes import classes_bp
from .attendance_routes import attendance_bp
from .qr_routes import qr_bp

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app)

    # ---- API blueprints ----
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(classes_bp, url_prefix="/api/classes")
    app.register_blueprint(attendance_bp, url_prefix="/api/attendance")
    app.register_blueprint(qr_bp, url_prefix="/api/qr")

    @app.route("/api/health")
    def health():
        return jsonify({"status": "ok"})

    # ---- FRONTEND ROUTES ----
    @app.route("/")
    def index():
        return send_from_directory(FRONTEND_DIR, "index.html")

    @app.route("/<path:path>")
    def frontend_files(path):
        # Anything not starting with api/ is treated as frontend
        if path.startswith("api/"):
            return jsonify({"error": "Not found"}), 404
        return send_from_directory(FRONTEND_DIR, path)

    return app
