import os
from dotenv import load_dotenv

load_dotenv()

# ==========================
# GitHub
# ==========================
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# ==========================
# Gemini
# ==========================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ==========================
# Google Sheets
# ==========================
CLIENT_SECRET_FILE = "client_secret.json"

# Paste your Google Spreadsheet ID here
SPREADSHEET_ID = "1gbUM2cETYIYyzrgSV2pZzdOZE__gBtC5E85XmV9Q2EM"

# Name of the worksheet (tab)
WORKSHEET_NAME = "Logs of commits"

WEBHOOK_TOKEN = os.getenv("WEBHOOK_TOKEN")