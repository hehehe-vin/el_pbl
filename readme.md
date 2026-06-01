# Smart Attendance System

This is a comprehensive Smart Attendance System that utilizes QR codes for tracking attendance. The application is built using a Python/Flask backend and an HTML/JS frontend, fully integrated with Google Cloud Platform (Firestore for the database, App Engine for hosting).

## Project Structure

```text
el_pbl/
├── app.yaml                 # Google Cloud App Engine configuration
├── main.py                  # Entry point for the Flask application
├── requirements.txt         # Python dependencies
├── backend/                 # API and server logic
│   ├── auth_routes.py       # Authentication endpoints (/api/auth)
│   ├── classes_routes.py    # Class management endpoints (/api/classes)
│   ├── attendance_routes.py # Attendance tracking endpoints (/api/attendance)
│   ├── qr_routes.py         # QR code generation endpoints (/api/qr)
│   ├── config.py            # Flask configuration
│   ├── db_config.py         # Firestore initialization
│   └── utils/               # Helper modules (Firestore client, Auth middleware, etc.)
├── static/                  # Vanilla HTML/JS frontend 
│   ├── index.html           # Landing page
│   ├── dashboard.html       # Student / Teacher dashboard
│   ├── attendance.html      # View attendance records
│   ├── schedule.html        # View class schedules
│   ├── find.html            # Other tools
│   └── auth.js              # Frontend authentication logic
└── secrets/                 # Place your GCP Service Account JSON key here (for local dev)
    └── smart-attendance.json
```

## Features

- **Role-Based Authentication**: Secure login using JWT tokens for students, teachers, and admins.
- **Dynamic QR Code Generation**: Teachers can generate unique QR codes for their classes.
- **Automated Attendance Tracking**: Students mark themselves present by scanning the class QR code.
- **Google Cloud Platform Integration**: Fully integrated with Firestore for NoSQL document storage and optimized for Google Cloud App Engine.

## Stack Requirements

- Python 3.10+
- Google Cloud SDK (for deployment and local database access)
- A Google Cloud Project with Firestore enabled

## Setup and Local Development

### 1. Create a Virtual Environment and Install Dependencies

```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure Firestore Initialization (Local Environment)

For local development, the application expects a Google Cloud Service Account JSON key.
1. Go to the Google Cloud Console.
2. Select IAM & Admin -> Service Accounts.
3. Create a Service Account, assign it the `Cloud Datastore User` role, and generate a new JSON key.
4. Save the key inside the `secrets/` directory as `smart-attendance.json`. (Make sure you update the path in `backend/db_config.py` if needed).

*Note: In the live App Engine environment, the app uses the default service account so no JSON key is required.*

### 3. Start the Server

Run the Flask application locally:

```bash
python main.py
```

The application will be accessible at `http://localhost:8080/`.

## API Endpoints Overview

- `GET /api/health` - Basic health check of the API.
- `POST /api/auth/...` - Sign in, Register, and Token management.
- `GET/POST /api/classes/...` - Create or fetch class records.
- `GET/POST /api/attendance/...` - Mark or fetch attendance.
- `POST /api/qr/...` - Generate QR codes for specific class periods.

## Deployment to Google Cloud App Engine

This project uses Gunicorn to run in a production environment as defined in `app.yaml`:

```bash
# Preview changes locally
dev_appserver.py app.yaml

# Deploy to GCP
gcloud app deploy
```

Make sure you update the `SECRET_KEY` in `app.yaml` before deploying to a production environment.


