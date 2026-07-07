import json
import os

from github_client import get_commit, get_files
from diff_engine import parse_patch, format_changes
from ai_summary import generate_ai_summary
from google_sheets import append_commit_file_rows


def load_event():
    """
    Load the GitHub Actions event payload.
    """

    event_path = os.getenv("GITHUB_EVENT_PATH")

    if not event_path:
        raise RuntimeError(
            "GITHUB_EVENT_PATH not found. "
            "This script should be executed from GitHub Actions."
        )

    with open(event_path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():

    payload = load_event()

    print("=" * 60)
    print("GitHub Event Loaded Successfully")
    print("=" * 60)

    print("Repository :", payload["repository"]["full_name"])
    print("Commit SHA :", payload["after"])
    print("Pusher     :", payload["pusher"]["name"])
    print("=" * 60)


if __name__ == "__main__":
    main()