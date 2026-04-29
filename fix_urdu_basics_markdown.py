#!/usr/bin/env python3
"""Fix common Markdown rendering issues in Urdu Basics chapters.

We keep changes minimal and mechanical:
- Ensure a blank line after </div> when a table starts next.
- Ensure a blank line before any Markdown table.
- Split merged headings like "## Title### Subtitle" into separate heading lines.
- Split cases like "###<div dir=...>" so the <div> starts on its own line.

We avoid touching content inside fenced code blocks.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass

BASICS_DIR = "basics"


@dataclass
class FixStats:
    files_changed: int = 0
    lines_changed: int = 0


def split_merged_heading_line(line: str) -> str:
    # Split patterns like:
    # "## Something### Another" -> "## Something\n\n### Another"
    # "## Something###<div dir=\"ltr\">" -> "## Something\n\n<div dir=\"ltr\">"

    # First, handle the "###<div" case explicitly.
    line = re.sub(r"(#{1,6}[^\n]*?)###\s*(<div\b)", r"\1\n\n\2", line)

    # Now split "...### ..." into a new heading.
    # Require something non-space before ### to avoid already-correct headings.
    line = re.sub(r"(#{1,6}[^\n]*?\S)###\s*", r"\1\n\n### ", line)

    # If a heading accidentally runs into a sentence (common after span removal),
    # e.g. "## Title?Sentence..." or "### ... (urdu)When ..."
    if re.match(r"^#{1,6} ", line):
        line = re.sub(r"\?(?=[A-Za-z])", "?\n\n", line)
        line = re.sub(r"\)(?=[A-Za-z])", ")\n\n", line)

        # If a table header row was appended to a heading line, split it out.
        # e.g. "### Title| Col | Col |" -> "### Title\n\n| Col | Col |"
        if "|" in line:
            idx = line.find("|")
            after = line[idx:]
            if after.count("|") >= 2 and not after.lstrip().startswith("|---"):
                before = line[:idx].rstrip()
                table_header = after.lstrip()
                if before.startswith("#") and table_header.startswith("|"):
                    line = f"{before}\n\n{table_header}"

        # If a heading contains an inline dash-list start, split to a bullet list.
        # e.g. "### Examples- **..." -> "### Examples\n\n- **..."
        line = re.sub(r"^(#{1,6} .*?)(\bExamples|sound)(-)\s+", r"\1\2\n\n- ", line)

        # If a fenced code block marker was glued onto a heading, split it.
        # e.g. "### Exercise ...```" -> heading then code fence on next line.
        if "```" in line and not line.strip().startswith("```"):
            fence_idx = line.find("```")
            if fence_idx > 0:
                before = line[:fence_idx].rstrip()
                after = line[fence_idx:]
                line = f"{before}\n\n{after.lstrip()}"

        # If bold content was glued directly onto a heading word (no space), split it.
        # We do this via string scanning to better handle hidden direction marks.
        bold_idx = line.find("**")
        if bold_idx > 0 and not line[bold_idx - 1].isspace() and line.lstrip().startswith("#"):
            line = line[:bold_idx] + "\n\n" + line[bold_idx:]

        # If a heading runs into a <div ...> tag, split it onto its own line (once).
        if "<div" in line and not line.lstrip().startswith("<div"):
            line = re.sub(r"\s*(<div\b)", r"\n\n\1", line, count=1)

        # If camelCase got introduced by concatenation (PreviewIn, CompleteCongratulations), split.
        line = re.sub(r"([a-z])([A-Z])", r"\1\n\n\2", line)

        # If a numbered item got glued to a heading via colon, split.
        line = re.sub(r":(?=\d+\.)", ":\n\n", line)

    return line


def fix_lines(lines: list[str]) -> tuple[list[str], int]:
    changed = 0
    out: list[str] = []

    in_fence = False
    pending_div_close_after_table = False
    in_table = False

    def is_table_line(s: str) -> bool:
        return s.lstrip().startswith("|")

    def is_table_separator_line(s: str) -> bool:
        sep = s.strip()
        if not sep.startswith("|"):
            return False
        body = sep.replace("|", "").strip()
        return (set(body) <= set("-: ")) and ("-" in body)

    def is_table_block_start(i: int) -> bool:
        if i < 0 or i >= len(lines):
            return False
        if not is_table_line(lines[i]):
            return False
        if i == 0:
            return True
        return not is_table_line(lines[i - 1])

    i = 0
    while i < len(lines):
        line = lines[i]

        # Track fenced code blocks
        if line.strip().startswith("```"):
            in_fence = not in_fence
            out.append(line)
            i += 1
            continue

        if in_fence:
            out.append(line)
            i += 1
            continue

        # If we just finished a table and we previously removed a </div> that split it,
        # re-insert the closing </div> after the table block.
        if in_table and not is_table_line(line):
            in_table = False
            if pending_div_close_after_table:
                # Ensure a clean break after the table before closing the div.
                if len(out) > 0 and out[-1].strip() != "":
                    out.append("\n")
                out.append("</div>\n")
                out.append("\n")
                pending_div_close_after_table = False
                changed += 1

        # Fix merged headings within a single line
        new_line = split_merged_heading_line(line)
        if new_line != line:
            # split_merged_heading_line may insert newlines; expand into multiple output lines
            parts = new_line.split("\n")
            out.extend([p + ("\n" if not p.endswith("\n") else "") for p in parts if p != ""])
            changed += 1
            i += 1
            continue

        # Ensure blank line between </div> and a following table (any table line)
        if line.strip() == "</div>":
            out.append(line)
            if i + 1 < len(lines) and is_table_line(lines[i + 1]) and lines[i + 1].strip() != "":
                out.append("\n")
                changed += 1
            i += 1
            continue

        # Ensure blank line before a table block start
        if is_table_block_start(i):
            if len(out) > 0 and out[-1].strip() != "":
                out.append("\n")
                changed += 1
            in_table = True

        # If a table header row is immediately followed by a stray </div> before the
        # separator row, remove that </div> and re-insert it after the table.
        if is_table_line(line):
            out.append(line)

            # Look ahead: optional blanks, then </div>, optional blanks, then separator.
            j = i + 1
            while j < len(lines) and lines[j].strip() == "":
                j += 1
            if j < len(lines) and lines[j].strip() == "</div>":
                k = j + 1
                while k < len(lines) and lines[k].strip() == "":
                    k += 1
                if k < len(lines) and is_table_line(lines[k]) and is_table_separator_line(lines[k]):
                    pending_div_close_after_table = True
                    # Skip over the stray </div> (and any blank lines we skipped).
                    i = k
                    changed += 1
                    continue

            i += 1
            continue

        out.append(line)
        i += 1

    # File ended while we were inside a table
    if in_table and pending_div_close_after_table:
        if len(out) > 0 and out[-1].strip() != "":
            out.append("\n")
        out.append("</div>\n")
        out.append("\n")
        changed += 1

    return out, changed


def process_file(path: str, stats: FixStats) -> None:
    with open(path, "r", encoding="utf-8") as f:
        original = f.readlines()

    fixed, changed = fix_lines(original)

    if fixed != original:
        with open(path, "w", encoding="utf-8") as f:
            f.writelines(fixed)
        stats.files_changed += 1
        stats.lines_changed += changed
        print(f"✓ Fixed: {path}")
    else:
        print(f"  OK: {path}")


def main() -> None:
    stats = FixStats()

    for filename in sorted(os.listdir(BASICS_DIR)):
        if not filename.endswith(".md"):
            continue
        process_file(os.path.join(BASICS_DIR, filename), stats)

    print(f"\n✅ Done. Files changed: {stats.files_changed}. Change blocks: {stats.lines_changed}.")


if __name__ == "__main__":
    main()
