import os
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN") or os.getenv("GH_PAT") or os.getenv("INPUT_GH_PAT")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

CLIENT_SECRET_FILE = "client_secret.json"
SPREADSHEET_ID = "1gbUM2cETYIYyzrgSV2pZzdOZE__gBtC5E85XmV9Q2EM"
WORKSHEET_NAME = "Logs of commits"

APPS_SCRIPT_WEBAPP_URL = os.getenv("APPS_SCRIPT_WEBAPP_URL") or os.getenv("INPUT_APPS_SCRIPT_WEBAPP_URL")
WEBHOOK_TOKEN = os.getenv("WEBHOOK_TOKEN")