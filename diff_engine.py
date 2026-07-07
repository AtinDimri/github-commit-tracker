from dataclasses import dataclass, field
from typing import List
import re


@dataclass
class Change:
    line: int
    removed: List[str] = field(default_factory=list)
    added: List[str] = field(default_factory=list)


@dataclass
class Hunk:
    old_start: int
    old_length: int
    new_start: int
    new_length: int
    lines: List[str]


def extract_hunks(patch: str) -> List[Hunk]:
    if not patch:
        return []

    hunks = []
    current_hunk = None

    pattern = re.compile(r"^@@ -(\d+),?(\d*) \+(\d+),?(\d*) @@")

    for line in patch.splitlines():
        match = pattern.match(line)

        if match:
            if current_hunk:
                hunks.append(current_hunk)

            current_hunk = Hunk(
                old_start=int(match.group(1)),
                old_length=int(match.group(2) or 1),
                new_start=int(match.group(3)),
                new_length=int(match.group(4) or 1),
                lines=[]
            )
            continue

        if current_hunk:
            current_hunk.lines.append(line)

    if current_hunk:
        hunks.append(current_hunk)

    return hunks


def parse_hunk(hunk: Hunk) -> List[Change]:
    changes = []

    old_line = hunk.old_start
    new_line = hunk.new_start

    current_change = None

    for line in hunk.lines:

        if line.startswith("-"):
            if current_change is None:
                current_change = Change(line=new_line)

            current_change.removed.append(line[1:])
            old_line += 1
            continue

        if line.startswith("+"):
            if current_change is None:
                current_change = Change(line=new_line)

            current_change.added.append(line[1:])
            new_line += 1
            continue

        if current_change:
            changes.append(current_change)
            current_change = None

        old_line += 1
        new_line += 1

    if current_change:
        changes.append(current_change)

    return changes


def parse_patch(patch: str) -> List[Change]:
    all_changes = []

    hunks = extract_hunks(patch)

    for hunk in hunks:
        all_changes.extend(parse_hunk(hunk))

    return all_changes


def format_changes(changes: List[Change]) -> str:
    if not changes:
        return "No code changes available."

    blocks = []

    for change in changes:
        block = [f"Line {change.line}"]

        if change.removed:
            block.append("")
            block.append("Removed:")
            block.extend(change.removed)

        if change.added:
            block.append("")
            block.append("Added:")
            block.extend(change.added)

        blocks.append("\n".join(block))

    return "\n\n" + "\n\n----------------------------------------\n\n".join(blocks) + "\n"


if __name__ == "__main__":
    patch = """@@ -1,9 +1,9 @@
-print("Pushing testing docking")
+print("Pushing testing good testing best docking")


 print("My logic THIS THIS TEstIng for this code")

-for i in range(12):
+for i in range(18):
    print("This is iteration number:", i)
"""

    changes = parse_patch(patch)
    report = format_changes(changes)
    print(report)