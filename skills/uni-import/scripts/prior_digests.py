#!/usr/bin/env python3
"""
prior_digests.py — print the cross-linking context of the digests that already exist.

An import needs to know what earlier units left open and what they connect to, so
the new digest can write "resolves digest-05 Q2: …" and "builds on T12". Reading
every existing digest into context to learn that is expensive (a whole course is
tens of thousands of words); this script prints only the parts that matter for
linking — per digest: the title line, the Open questions section (every question
with a citable Q-ID), the Connections section, and the Topics registered line. A
full course comes out at well under 100 lines.

Usage:
  python prior_digests.py                     # searches /mnt/project, then uploads
  python prior_digests.py /some/dir another/  # explicit directories

Exit 0 always (no digests found is a normal state — the first import of a course).
"""
import glob
import os
import re
import sys

DEFAULT_DIRS = ["/mnt/project", "/mnt/user-data/uploads"]

# Section headers are matched by prefix, case-insensitively, so both
# "## Open questions" and "## Open questions / to follow up" are found.
SECTION_PREFIXES = {
    "open": "## open questions",
    "connections": "## connections",
}


def find_digests(dirs):
    seen = {}
    for d in dirs:
        if not os.path.isdir(d):
            continue
        for path in sorted(glob.glob(os.path.join(d, "digest-*.md"))):
            name = os.path.basename(path)
            # The project copy wins over an uploads copy of the same digest.
            seen.setdefault(name, path)
    return [seen[k] for k in sorted(seen)]


def split_sections(text):
    """Return list of (header_line, body_lines) for every '## ' section."""
    sections = []
    header, body = None, []
    for line in text.splitlines():
        if line.startswith("## "):
            if header is not None:
                sections.append((header, body))
            header, body = line, []
        elif header is not None:
            body.append(line)
    if header is not None:
        sections.append((header, body))
    return sections


QID = re.compile(r"^-\s*Q(\d+)\s*·")


def with_qids(lines):
    """Ensure every open-question bullet carries a citable Q-ID.

    New digests write them (`- Q1 · …`); digests from before Q-IDs get positional
    ones (Q1, Q2, … in bullet order) so `resolves digest-NN Qk` works either way.
    A `— none —` placeholder bullet is not a question and gets no ID.
    """
    out, n = [], 0
    for line in lines:
        s = line.strip()
        if s.startswith("- ") and not re.match(r"^-\s*—", s):
            n += 1
            if not QID.match(s):
                line = re.sub(r"^(\s*)-\s*", rf"\1- Q{n} · ", line, count=1) + "   (positional ID)"
        out.append(line)
    return out


def strip_comments(lines):
    """Drop HTML comment blocks (template guidance) so only real content prints."""
    out, in_comment = [], False
    for line in lines:
        s = line.strip()
        if in_comment:
            if "-->" in s:
                in_comment = False
            continue
        if s.startswith("<!--"):
            if "-->" not in s:
                in_comment = True
            continue
        if s:
            out.append(line.rstrip())
    return out


def main():
    dirs = sys.argv[1:] or DEFAULT_DIRS
    paths = find_digests(dirs)
    if not paths:
        print(f"No existing digests found in {', '.join(dirs)} — nothing to link to.")
        print("This is the course's first digest: write '— none —' in §Connections.")
        return 0

    print(f"{len(paths)} existing digest(s) — open questions and connections:\n")
    for path in paths:
        text = open(path, encoding="utf-8", errors="replace").read()
        title = next((l[2:].strip() for l in text.splitlines() if l.startswith("# ")), "(no title)")
        topics = re.search(r"^Topics:\s*(.+)$", text, re.M)
        print(f"=== {os.path.basename(path)} — {title}")
        print(f"    {('Topics: ' + topics.group(1).strip()) if topics else '(no Topics registered line)'}")
        sections = split_sections(text)
        for key, prefix in SECTION_PREFIXES.items():
            match = next(((h, b) for h, b in sections if h.lower().startswith(prefix)), None)
            if match is None:
                print(f"    (no {key} section)" if key == "connections" else "    (no Open questions section)")
                continue
            body = strip_comments(match[1])
            if key == "open":
                body = with_qids(body)
            print(f"    {match[0]}")
            if not body:
                print("      (empty)")
            for line in body:
                print("      " + line)
        print()
    print("Use: 'resolves digest-NN Qk: <answer in one clause>' lines in the new digest's")
    print("§Connections. The state file is never edited for a resolution.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
