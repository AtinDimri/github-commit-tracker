import os
from dotenv import load_dotenv

# Load .env only if it exists.
# On GitHub Actions, environment variables come from GitHub Secrets.
load_dotenv()

# ==========================================================
# GitHub
# ==========================================================
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# ==========================================================
# Gemini (Optional)
# ==========================================================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ==========================================================
# Google OAuth (Local only)
# ==========================================================
CLIENT_SECRET_FILE = "client_secret.json"

# ==========================================================
# Google Sheet
# ==========================================================
SPREADSHEET_ID = "1gbUM2cETYIYyzrgSV2pZzdOZE__gBtC5E85XmV9Q2EM"
WORKSHEET_NAME = "Logs of commits"

# ==========================================================
# Apps Script Web App
# Local  -> .env
# GitHub -> Repository Secret
# ==========================================================
APPS_SCRIPT_WEBAPP_URL = os.getenv("APPS_SCRIPT_WEBAPP_URL")

# ==========================================================
# Optional webhook token
# ==========================================================
WEBHOOK_TOKEN = os.getenv("WEBHOOK_TOKEN")