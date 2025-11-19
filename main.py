# main.py
from backend import create_app

# What gunicorn/App Engine uses: "main:app"
app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
