# backend/db_config.py
import os
from google.cloud import firestore

def create_firestore_client():
    # On App Engine standard, GAE_ENV starts with "standard"
    if os.environ.get("GAE_ENV", "").startswith("standard"):
        # Use default service account (no key file)
        return firestore.Client()
    else:
        # Local dev: use your JSON key if you want
        key_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "gcp-key",
            "smart-attendance.json"
        )
        os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS", key_path)
        return firestore.Client()

db = create_firestore_client()
