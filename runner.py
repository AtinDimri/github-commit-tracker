from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple

from ai_summary import generate_ai_summary
from diff_engine import format_changes, parse_patch
from github_client import get_commit, get_files
from google_sheets import append_commit_file_rows


def load_event() -> Dict[str, Any]:
    event_path = os.getenv("GITHUB_EVENT_PATH")
    if not event_path:
        raise RuntimeError(
            "GITHUB_EVENT_PATH not found. This script should run inside GitHub Actions."
        )

    with open(event_path, "r", encoding="utf-8") as f:
        return json.load(f)


def _extract_repo_full_name(payload: Dict[str, Any]) -> str:
    repo = payload.get("repository") or {}
    return repo.get("full_name") or repo.get("name") or ""


def _extract_commit_sha(payload: Dict[str, Any]) -> str:
    return payload.get("after") or (payload.get("head_commit") or {}).get("id") or ""


def _extract_committer(payload: Dict[str, Any], commit_obj: Any) -> str:
    pusher = payload.get("pusher") or {}
    sender = payload.get("sender") or {}

    if pusher.get("name"):
        return str(pusher["name"])

    if sender.get("login"):
        return str(sender["login"])

    try:
        author = commit_obj.commit.author
        if author and author.name:
            return str(author.name)
    except Exception:
        pass

    return "Unknown"


def _extract_commit_message(payload: Dict[str, Any], commit_obj: Any) -> str:
    head_commit = payload.get("head_commit") or {}

    if head_commit.get("message"):
        return str(head_commit["message"])

    try:
        if commit_obj.commit and commit_obj.commit.message:
            return str(commit_obj.commit.message)
    except Exception:
        pass

    return ""


def _extract_commit_datetime(payload: Dict[str, Any], commit_obj: Any) -> datetime:
    try:
        author_date = commit_obj.commit.author.date
        if isinstance(author_date, datetime):
            return author_date
    except Exception:
        pass

    head_commit = payload.get("head_commit") or {}
    ts = head_commit.get("timestamp")

    if ts:
        try:
            if isinstance(ts, str) and ts.endswith("Z"):
                ts = ts.replace("Z", "+00:00")
            return datetime.fromisoformat(ts)
        except Exception:
            pass

    return datetime.now(timezone.utc)


def _format_date_time(dt: datetime) -> Tuple[str, str]:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    local_dt = dt.astimezone()
    return local_dt.strftime("%Y-%m-%d"), local_dt.strftime("%H:%M:%S")


def main() -> None:
    payload = load_event()

    repo_full_name = _extract_repo_full_name(payload)
    commit_sha = _extract_commit_sha(payload)

    if not repo_full_name:
        raise RuntimeError("Repository not found in GitHub event payload.")
    if not commit_sha:
        raise RuntimeError("Commit SHA not found in GitHub event payload.")

    commit_obj = get_commit(repo_full_name, commit_sha)
    files = get_files(commit_obj)

    committer = _extract_committer(payload, commit_obj)
    commit_message = _extract_commit_message(payload, commit_obj)

    commit_dt = _extract_commit_datetime(payload, commit_obj)
    date_str, time_str = _format_date_time(commit_dt)

    rows: List[List[str]] = []

    print("=" * 70)
    print("GitHub Event Loaded Successfully")
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