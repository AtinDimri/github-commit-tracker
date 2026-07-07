from __future__ import annotations

from ai_summary import generate_ai_summary

from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from config import WEBHOOK_TOKEN
from diff_engine import format_changes, parse_patch
from github_client import get_commit, get_files
from google_sheets import append_commit_file_rows

app = FastAPI(title="GitHub Commit Tracker", version="1.0.0")


@app.get("/health")
def health_check() -> Dict[str, str]:
    return {"ok": "true", "message": "service is running"}


def _require_token(request: Request) -> None:
    if WEBHOOK_TOKEN:
        token = request.query_params.get("token")
        if token != WEBHOOK_TOKEN:
            raise HTTPException(status_code=401, detail="Unauthorized")


def _extract_repo_full_name(payload: Dict[str, Any]) -> str:
    repo = payload.get("repository") or {}
    return repo.get("full_name") or repo.get("name") or ""


def _extract_commit_sha(payload: Dict[str, Any]) -> str:
    return (
        payload.get("after")
        or (payload.get("head_commit") or {}).get("id")
        or ""
    )


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


def _build_ai_summary(commit_message: str, file_name: str, changes_text: str) -> str:
    """
    Fallback summary for now.
    If ai_summary.py later defines generate_ai_summary(...),
    this function can be swapped to use it without changing app.py flow.
    """
    try:
        import ai_summary  # optional future module

        generator = getattr(ai_summary, "generate_ai_summary", None)
        if callable(generator):
            summary = generator(
                commit_message=commit_message,
                file_name=file_name,
                changes=changes_text,
            )
            if summary:
                return str(summary).strip()
    except Exception:
        pass

    if commit_message and file_name:
        return f"{commit_message} — {file_name}"
    if commit_message:
        return commit_message
    return f"Processed changes in {file_name}."


@app.get("/")
def root() -> Dict[str, str]:
    return {
        "ok": "true",
        "message": "GitHub Commit Tracker is live",
    }


@app.post("/webhook")
async def github_webhook(request: Request):
    _require_token(request)

    event_type = request.headers.get("X-GitHub-Event", "").lower()

    if event_type == "ping":
        return JSONResponse(
            {
                "ok": True,
                "message": "pong",
            }
        )

    if event_type != "push":
        return JSONResponse(
            {
                "ok": True,
                "message": f"ignored event: {event_type or 'unknown'}",
            }
        )

    payload = await request.json()

    repo_full_name = _extract_repo_full_name(payload)
    commit_sha = _extract_commit_sha(payload)

    if not repo_full_name:
        raise HTTPException(status_code=400, detail="Repository not found in payload")

    if not commit_sha:
        raise HTTPException(status_code=400, detail="Commit SHA not found in payload")

    commit_obj = get_commit(repo_full_name, commit_sha)
    files = get_files(commit_obj)

    committer = _extract_committer(payload, commit_obj)
    commit_message = _extract_commit_message(payload, commit_obj)
    processed_dt = datetime.now(timezone.utc)
    date_str, time_str = _format_date_time(processed_dt)

    rows: List[List[str]] = []

    for file_obj in files:
        file_name = getattr(file_obj, "filename", "unknown-file")
        patch = getattr(file_obj, "patch", None)

        if patch:
            changes_text = format_changes(parse_patch(patch))
        else:
            status = getattr(file_obj, "status", "modified")
            changes_text = f"No code patch available for this file.\nStatus: {status}"

        ai_summary = _build_ai_summary(commit_message, file_name, changes_text)

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

    if rows:
        append_commit_file_rows(rows)

    return JSONResponse(
        {
            "ok": True,
            "repository": repo_full_name,
            "commit_sha": commit_sha,
            "files_written": len(rows),
        }
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)