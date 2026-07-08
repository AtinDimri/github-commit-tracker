from __future__ import annotations

import os
from datetime import datetime
from typing import Any, List, Tuple
from zoneinfo import ZoneInfo

from ai_summary import generate_ai_summary
from diff_engine import format_changes, parse_patch
from github_client import get_commit, get_files
from google_sheets import append_commit_file_rows


def _get_env_value(*names: str, required: bool = True) -> str:
    for name in names:
        value = os.getenv(name)
        if value:
            return value.strip()

    if required:
        raise RuntimeError(
            f"Missing required environment variable. Tried: {', '.join(names)}"
        )

    return ""


def _extract_committer(commit_obj: Any) -> str:
    try:
        author = commit_obj.commit.author
        if author and author.name:
            return str(author.name)
    except Exception:
        pass
    return "Unknown"


def _extract_commit_message(commit_obj: Any) -> str:
    try:
        if commit_obj.commit and commit_obj.commit.message:
            return str(commit_obj.commit.message)
    except Exception:
        pass
    return ""


def _extract_commit_datetime(commit_obj: Any) -> datetime:
    try:
        author_date = commit_obj.commit.author.date
        if isinstance(author_date, datetime):
            return author_date
    except Exception:
        pass

    return datetime.now(ZoneInfo("UTC"))


def _format_date_time(dt: datetime) -> Tuple[str, str]:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=ZoneInfo("UTC"))

    ist = dt.astimezone(ZoneInfo("Asia/Kolkata"))
    return ist.strftime("%Y-%m-%d"), ist.strftime("%H:%M:%S")


def main() -> None:
    repo_full_name = _get_env_value("REPO_FULL_NAME", "GITHUB_REPOSITORY")
    commit_sha = _get_env_value("COMMIT_SHA", "GITHUB_SHA")

    commit_obj = get_commit(repo_full_name, commit_sha)
    files = get_files(commit_obj)

    committer = _extract_committer(commit_obj)
    commit_message = _extract_commit_message(commit_obj)

    commit_dt = _extract_commit_datetime(commit_obj)
    date_str, time_str = _format_date_time(commit_dt)

    rows: List[List[str]] = []

    print("=" * 70)
    print("Commit Tracker Started Successfully")
    print("=" * 70)
    print("Repository :", repo_full_name)
    print("Commit SHA :", commit_sha)
    print("Committer  :", committer)
    print("Message    :", commit_message)
    print("Files      :", len(files))
    print("=" * 70)

    for file_obj in files:
        file_name = getattr(file_obj, "filename", "unknown-file")
        patch = getattr(file_obj, "patch", None)

        if patch:
            changes_text = format_changes(parse_patch(patch))
        else:
            status = getattr(file_obj, "status", "modified")
            changes_text = f"No code patch available for this file.\nStatus: {status}"

        ai_summary = generate_ai_summary(commit_message, file_name, changes_text)

        rows.append(
            [
                repo_full_name,
                commit_sha,
                committer,
                file_name,
                changes_text,
                commit_message,
                date_str,
                time_str,
                ai_summary,
            ]
        )

        print(f"Processed file: {file_name}")

    if rows:
        append_commit_file_rows(rows)
        print(f"Appended {len(rows)} row(s) to Google Sheets.")
    else:
        print("No changed files to write.")


if __name__ == "__main__":
    main()