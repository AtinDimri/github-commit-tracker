from __future__ import annotations

from typing import Any, Dict, Iterable, List, Sequence

import requests

from config import APPS_SCRIPT_WEBAPP_URL

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


def _row_list_to_dict(row: Sequence[Any]) -> Dict[str, str]:
    if len(row) != 9:
        raise ValueError(
            f"Expected 9 values per row, got {len(row)}. "
            f"Expected order: {HEADERS}"
        )

    return {
        "repository": str(row[0]),
        "commit_sha": str(row[1]),
        "committer": str(row[2]),
        "file_name": str(row[3]),
        "changes": str(row[4]),
        "commit_message": str(row[5]),
        "date": str(row[6]),
        "time": str(row[7]),
        "ai_summary": str(row[8]),
    }


def _normalize_rows(rows: Iterable[Any]) -> List[Dict[str, str]]:
    normalized: List[Dict[str, str]] = []

    for row in rows:
        if isinstance(row, dict):
            required = [
                "repository",
                "commit_sha",
                "committer",
                "file_name",
                "changes",
                "commit_message",
                "date",
                "time",
                "ai_summary",
            ]

            missing = [key for key in required if key not in row]
            if missing:
                raise ValueError(f"Missing row keys: {missing}")

            normalized.append({key: str(row[key]) for key in required})

        elif isinstance(row, (list, tuple)):
            normalized.append(_row_list_to_dict(row))

        else:
            raise TypeError(
                "Each row must be either a dict or a list/tuple of 9 values."
            )

    return normalized


def append_commit_file_rows(rows: Iterable[Any]) -> Dict[str, Any]:
    if not APPS_SCRIPT_WEBAPP_URL:
        raise ValueError("APPS_SCRIPT_WEBAPP_URL is missing in config.py")

    payload = {"rows": _normalize_rows(rows)}

    response = requests.post(
        APPS_SCRIPT_WEBAPP_URL,
        json=payload,
        timeout=30,
    )

    try:
        data = response.json()
    except Exception:
        raise RuntimeError(
            f"Apps Script returned non-JSON response.\n"
            f"Status: {response.status_code}\n"
            f"Body: {response.text}"
        )

    if response.status_code != 200:
        raise RuntimeError(
            f"Apps Script request failed.\n"
            f"Status: {response.status_code}\n"
            f"Response: {data}"
        )

    if not data.get("success"):
        raise RuntimeError(f"Apps Script reported failure: {data}")

    return data


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
) -> Dict[str, Any]:
    return append_commit_file_rows(
        [[
            repository,
            commit_sha,
            committer,
            file_name,
            changes,
            commit_message,
            date_str,
            time_str,
            ai_summary,
        ]]
    )


if __name__ == "__main__":
    # Temporary smoke test: this should append one row to your "Logs of commits" tab.
    result = append_commit_file_row(
        repository="Test_repo",
        commit_sha="TEST_SHA",
        committer="Atin",
        file_name="PUSHING.py",
        changes='Line 1\n\nRemoved:\nprint("Hello")\n\nAdded:\nprint("Hello World")',
        commit_message="Test write from google_sheets.py",
        date_str="2026-07-07",
        time_str="12:00:00",
        ai_summary="Test row written successfully.",
    )
    print(result)