# backend/config.py
import os


class Config:
    # change in production: set env var SECRET_KEY
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-this")

    # you can add more later (e.g. FIRESTORE project, etc.)
