import os

port = os.environ.get("CITIZEN_FRONTEND_PORT", "8000")
bind = f"0.0.0.0:{port}"
