from __future__ import annotations

from typing import Any, Dict, Iterable, List, Sequence

import requests

from config import APPS_SCRIPT_WEBAPP_URL


HEADERS = [
    "Project",
    "Assigned to",
    "Task",
    "Date & Time",
    "Remark",
    "Status",
]


def _row_list_to_dict(row: Sequence[Any]) -> Dict[str, str]:

    if len(row) != 6:
        raise ValueError(
            f"Expected 6 values per row, got {len(row)}. "
            f"Expected order: {HEADERS}"
        )

    return {
        "project": str(row[0]),
        "assigned_to": str(row[1]),
        "task": str(row[2]),
        "date_time": str(row[3]),
        "remark": str(row[4]),
        "status": str(row[5]),
    }


def _normalize_rows(
    rows: Iterable[Any],
) -> List[Dict[str, str]]:

    normalized: List[Dict[str, str]] = []

    required = [
        "project",
        "assigned_to",
        "task",
        "date_time",
        "remark",
        "status",
    ]

    for row in rows:

        if isinstance(row, dict):

            missing = [
                key
                for key in required
                if key not in row
            ]

            if missing:
                raise ValueError(
                    f"Missing row keys: {missing}"
                )

            normalized.append(
                {
                    key: str(row[key])
                    for key in required
                }
            )

        elif isinstance(row, (list, tuple)):

            normalized.append(
                _row_list_to_dict(row)
            )

        else:

            raise TypeError(
                "Each row must be either a dict "
                "or a list/tuple of 6 values."
            )

    return normalized


def append_commit_file_rows(
    rows: Iterable[Any],
) -> Dict[str, Any]:

    if not APPS_SCRIPT_WEBAPP_URL:
        raise ValueError(
            "APPS_SCRIPT_WEBAPP_URL is missing in config.py"
        )

    payload = {
        "rows": _normalize_rows(rows)
    }

    response = requests.post(
        APPS_SCRIPT_WEBAPP_URL,
        json=payload,
        timeout=30,
    )

    try:
        data = response.json()

    except Exception:

        raise RuntimeError(
            "Apps Script returned non-JSON response.\n"
            f"Status: {response.status_code}\n"
            f"Body: {response.text}"
        )

    if response.status_code != 200:

        raise RuntimeError(
            "Apps Script request failed.\n"
            f"Status: {response.status_code}\n"
            f"Response: {data}"
        )

    if not data.get("success"):

        raise RuntimeError(
            f"Apps Script reported failure: {data}"
        )

    return data


if __name__ == "__main__":

    # Temporary smoke test

    result = append_commit_file_rows(
        [[
            "Test_repo",
            "Atin Dimri",
            "Test Google Sheets integration",
            "2026-08-10 13:00:00",
            "Test row written successfully.",
            "",
        ]]
    )

    print(result)
