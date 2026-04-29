#!/usr/bin/env python3
"""Targeted Markdown rendering fixes for Urdu Basics chapters.

Goal: fix tables/sections not rendering because of:
- merged headings ("## Title### Subtitle")
- heading line containing a table header ("## Title| Col | Col |")
- heading line containing an inline list item ("### Title- item")
- a stray </div> inserted between a table header row and its separator row

This script intentionally avoids aggressive transformations that can break
bold markers or move <div> tags into paragraphs.

It skips fenced code blocks.
"""

from __future__ import annotations

import os
import re

BASICS_DIR = "basics"


def is_fence(line: str) -> bool:
    return line.strip().startswith("```")


def is_table_line(line: str) -> bool:
    return line.lstrip().startswith("|")


def is_table_separator(line: str) -> bool:
    s = line.strip()
    if not s.startswith("|"):
        return False
    body = s.replace("|", "").strip()
    return ("-" in body) and (set(body) <= set("-: "))


def split_merged_headings(line: str) -> str:
    if re.match(r"^#{1,6} ", line):
        # Fix accidental concatenations inside headings (safe: only inserts spaces)
        line = re.sub(r"([a-z])([A-Z])", r"\1 \2", line)
        line = re.sub(r"(\d)([A-Za-z])", r"\1 \2", line)

    # "## Something### More" -> two headings (be forgiving about what precedes ###)
    line = re.sub(r"(#{1,6}[^\n]*?)###\s*", r"\1\n\n### ", line)
    # "###<div ...>" -> start div on a new line
    line = re.sub(r"(#{1,6}[^\n]*?)###\s*(<div\b)", r"\1\n\n\2", line)
    return line


def split_heading_with_table_header(line: str) -> str:
    # If a heading contains a table header row appended with | ... | ... |
    if not re.match(r"^#{1,6} ", line):
        return line
    if "|" not in line:
        return line

    idx = line.find("|")
    after = line[idx:]
    if after.count("|") < 3:
        return line

    before = line[:idx].rstrip()
    table_header = after.strip()
    if not table_header.startswith("|"):
        return line

    # Only do this when the part before the '|' looks like a real heading.
    if not before.startswith("#"):
        return line

    return f"{before}\n\n{table_header}\n"


def split_heading_with_inline_list(line: str) -> str:
    # "### Real Word Examples- **..." -> heading then bullet list item
    if not re.match(r"^#{1,6} ", line):
        return line
    # Only split when there's a dash used like a list separator, not negative numbers.
    m = re.match(r"^(#{1,6} .+?)\s*-\s+(\S.*)$", line)
    if not m:
        return line
    head = m.group(1).rstrip()
    item = m.group(2).rstrip()
    return f"{head}\n\n- {item}\n"


def normalize_div_tags(line: str) -> str:
    # Put inline HTML div tags onto their own lines so they don't break Markdown.
    # Preserve original order: prefix stays before the tag.
    if "</div><div dir=\"ltr\">" in line:
        line = line.replace("</div><div dir=\"ltr\">", "</div>\n\n<div dir=\"ltr\">")

    # Split any inline opening <div dir="ltr"> that appears after other text.
    if "<div dir=\"ltr\">" in line and not line.lstrip().startswith('<div dir="ltr">'):
        line = line.replace('<div dir="ltr">', '\n\n<div dir="ltr">')

    # Split any inline closing </div> that shares a line with other text.
    if "</div>" in line and line.strip() != "</div>":
        # Ensure the closing tag ends its own line.
        line = line.replace("</div>", "\n</div>\n\n")

    return line


def move_div_close_out_of_table(lines: list[str]) -> list[str]:
    out: list[str] = []
    in_fence_block = False
    i = 0

    while i < len(lines):
        line = lines[i]

        if is_fence(line):
            in_fence_block = not in_fence_block
            out.append(line)
            i += 1
            continue

        if in_fence_block:
            out.append(line)
            i += 1
            continue

        # If we are at a table header row and the next non-empty line is </div>
        # and the next non-empty after that is a separator row, remove </div>
        # and re-insert it after the table block.
        if is_table_line(line):
            # Ensure blank line before a new table block
            if len(out) > 0 and not is_table_line(out[-1]) and out[-1].strip() != "":
                out.append("\n")

            # Lookahead for the "header -> blanks -> </div> -> blanks -> separator" pattern
            j = i + 1
            while j < len(lines) and lines[j].strip() == "":
                j += 1

            if j < len(lines) and lines[j].strip() == "</div>":
                k = j + 1
                while k < len(lines) and lines[k].strip() == "":
                    k += 1

                if k < len(lines) and is_table_line(lines[k]) and is_table_separator(lines[k]):
                    # Emit header row
                    out.append(line)
                    # Emit separator + remaining table rows
                    t = k
                    while t < len(lines) and is_table_line(lines[t]):
                        out.append(lines[t])
                        t += 1
                    # Close the div after the table
                    out.append("\n")
                    out.append("</div>\n")
                    out.append("\n")
                    i = t
                    continue

            # Default: just emit the line as-is
            out.append(line)
            i += 1
            continue

        out.append(line)
        i += 1

    return out


def process_file(path: str) -> bool:
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    original = "".join(lines)

    fixed_lines: list[str] = []
    in_fence_block = False

    for line in lines:
        if is_fence(line):
            in_fence_block = not in_fence_block
            fixed_lines.append(line)
            continue

        if in_fence_block:
            fixed_lines.append(line)
            continue

        new_line = normalize_div_tags(line)
        new_line = split_merged_headings(new_line)
        new_line = split_heading_with_table_header(new_line)
        new_line = split_heading_with_inline_list(new_line)
        fixed_lines.append(new_line)

    fixed_lines = move_div_close_out_of_table(fixed_lines)

    fixed = "".join(fixed_lines)
    if fixed != original:
        with open(path, "w", encoding="utf-8") as f:
            f.write(fixed)
        return True
    return False


def main() -> None:
    changed = 0
    for name in sorted(os.listdir(BASICS_DIR)):
        if not name.endswith(".md"):
            continue
        path = os.path.join(BASICS_DIR, name)
        if process_file(path):
            print(f"✓ Fixed: {path}")
            changed += 1
        else:
            print(f"  OK: {path}")

    print(f"\n✅ Done. Files changed: {changed}.")


if __name__ == "__main__":
    main()
