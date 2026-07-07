from __future__ import annotations

import re
from typing import List


def _join_phrases(parts: List[str]) -> str:
    parts = [p for p in parts if p]
    if not parts:
        return "updated the code"
    if len(parts) == 1:
        return parts[0]
    if len(parts) == 2:
        return f"{parts[0]} and {parts[1]}"
    return ", ".join(parts[:-1]) + f", and {parts[-1]}"


def _extract_change_signals(changes: str) -> List[str]:
    text = changes or ""
    lowered = text.lower()
    signals: List[str] = []

    if "print(" in lowered:
        signals.append("replaced a print statement")

    if "range(" in lowered or re.search(r"\bfor\s+\w+\s+in\s+range\(", lowered):
        signals.append("adjusted the loop range")

    if re.search(r"^\s*def\s+\w+\s*\(", text, re.MULTILINE):
        signals.append("updated a function")

    if re.search(r"^\s*class\s+\w+\s*:", text, re.MULTILINE):
        signals.append("updated a class")

    if re.search(r"^\s*[A-Za-z_]\w*\s*=", text, re.MULTILINE):
        signals.append("changed an assignment")

    if "import " in lowered:
        signals.append("updated imports")

    if "return " in lowered:
        signals.append("changed return logic")

    if not signals:
        signals.append("updated the code")

    unique: List[str] = []
    for item in signals:
        if item not in unique:
            unique.append(item)

    return unique


def generate_ai_summary(commit_message: str, file_name: str, changes: str) -> str:
    """
    Zero-cost local summary generator.

    Returns a short readable summary based on the code changes.
    """
    phrases = _extract_change_signals(changes)
    phrase = _join_phrases(phrases)
    phrase = phrase[:1].upper() + phrase[1:] if phrase else "Updated the code"

    if commit_message:
        commit_message = commit_message.strip().rstrip(".")
        if commit_message and commit_message.lower() not in phrase.lower():
            return f"{phrase} in {file_name}. Commit note: {commit_message}."

    return f"{phrase} in {file_name}."


if __name__ == "__main__":
    sample = """Line 1

Removed:
print("Hello")

Added:
print("Hello World")

----------------------------------------

Line 6

Removed:
for i in range(12):

Added:
for i in range(18):
"""
    print(generate_ai_summary("Update print statements and loop range in PUSHING.py", "PUSHING.py", sample))