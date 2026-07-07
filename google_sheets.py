from pathlib import Path
from typing import Iterable, List

import gspread
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from gspread.exceptions import WorksheetNotFound

from datetime import datetime

from config import CLIENT_SECRET_FILE, SPREADSHEET_ID, WORKSHEET_NAME

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
TOKEN_FILE = "token.json"

HEADERS = [
    "Repository",
    "Commit SHA",
    "Committer",
    "File",
    "Changes",
    "Commit Message",
    "Date",
    "Time",
    "AI Summary",
]


def _load_credentials() -> Credentials:
    creds = None
    token_path = Path(TOKEN_FILE)
    client_secret_path = Path(CLIENT_SECRET_FILE)

    if token_path.exists():
        try:
            creds = Credentials.from_authorized_user_file(
                token_path.as_posix(),
                SCOPES,
            )
        except Exception:
            creds = None

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    elif not creds or not creds.valid:
        if not client_secret_path.exists():
            raise FileNotFoundError(
                f"{CLIENT_SECRET_FILE} not found in project root."
            )

        flow = InstalledAppFlow.from_client_secrets_file(
            client_secret_path.as_posix(),
            SCOPES,
        )
        creds = flow.run_local_server(port=0)

    token_path.write_text(creds.to_json(), encoding="utf-8")
    return creds


def get_client() -> gspread.Client:
    creds = _load_credentials()
    return gspread.authorize(creds)


def get_spreadsheet():
    if not SPREADSHEET_ID:
        raise ValueError("SPREADSHEET_ID is missing in config.py")

    client = get_client()
    return client.open_by_key(SPREADSHEET_ID)


def ensure_headers(ws) -> None:
    current = ws.row_values(1)

    if not current:
        ws.append_row(HEADERS, value_input_option="RAW")
    else:
        normalized = [str(cell).strip() for cell in current[: len(HEADERS)]]
        if normalized != HEADERS:
            raise ValueError(
                "Worksheet header mismatch.\n"
                f"Expected: {HEADERS}\n"
                f"Found:    {current}"
            )

    try:
        ws.format(
            f"A:I",
            {
                "wrapStrategy": "WRAP",
                "verticalAlignment": "TOP",
            },
        )
    except Exception:
        pass


def get_worksheet():
    spreadsheet = get_spreadsheet()

    try:
        ws = spreadsheet.worksheet(WORKSHEET_NAME)
    except WorksheetNotFound:
        ws = spreadsheet.add_worksheet(
            title=WORKSHEET_NAME,
            rows=1000,
            cols=len(HEADERS),
        )

    ensure_headers(ws)
    return ws


def append_commit_file_row(
    repository: str,
    commit_sha: str,
    committer: str,
    file_name: str,
    changes: str,
    commit_message: str,
    date_str: str,
    time_str: str,
    ai_summary: str,
) -> None:
    ws = get_worksheet()

    row = [
        repository,
        commit_sha,
        committer,
        file_name,
        changes,
        commit_message,
        date_str,
        time_str,
        ai_summary,
    ]

    ws.append_row(row, value_input_option="RAW")


def append_commit_file_rows(rows: Iterable[List[str]]) -> None:
    ws = get_worksheet()
    ws.append_rows(list(rows), value_input_option="RAW")


if __name__ == "__main__":
    # Temporary test row. Run once to authorize and verify writing works.
    now = datetime.now()

    append_commit_file_row(
        repository="Test_repo",
        commit_sha="TEST_SHA",
        committer="Atin",
        file_name="PUSHING.py",
        changes='Line 1\n\nRemoved:\nprint("Hello")\n\nAdded:\nprint("Hello World")',
        commit_message="Test write from google_sheets.py",
        date_str=now.strftime("%Y-%m-%d"),
        time_str=now.strftime("%H:%M:%S"),
        ai_summary="Test row written successfully.",
)
    print("Test row appended successfully.")