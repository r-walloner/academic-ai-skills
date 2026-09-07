#!/usr/bin/env python3
"""
check_import.py — validate what an import is about to deliver, before delivering it.

The uni- framework's files are consumed by other skills in later sessions, where a
defect fails silently: a digest that cites figure F11 with no F11 index line sends
the tutor to a page that doesn't exist; a topic name of nine words breaks the state
file's budget; a lecturer example that lost its marker looks like a guess. None of
these are visible while writing. This script makes them visible, names the offending
ID or text, and exits non-zero so the digest is fixed before the student sees it.

Usage (typical lecture import — run from the skill directory):
  python scripts/check_import.py \\
      --digest  /mnt/user-data/outputs/digest-06-slug.md \\
      --state   /mnt/user-data/outputs/course-state.md \\
      --prev    /mnt/project/course-state.md \\
      --scratch /home/claude/<unit> \\
      --project /mnt/project \
      --sessions 1

Exam-brief import:
  python scripts/check_import.py --brief /mnt/user-data/outputs/exam-brief.md --state <course-state.md>

Options:
  --digest   the new digest file
  --state    the course-state.md about to be delivered (topic checks)
  --prev     the course-state.md the run started from (untouched-rows check)
  --scratch  directory holding lecturer-examples.md (provenance check)
  --brief    an exam-brief.md to check instead of / in addition to a digest
  --project  the project folder holding existing digests; enables the cross-digest
             checks (resolves-citations point at real Q-IDs; slug consistency)
  --sessions how many in-class sessions the imported material spans (default 1),
             used for the topic-count target
  --ignore-figs  comma-separated F-IDs to ignore as inline references, for a digest
             whose subject uses "F1"-style symbols for something else

Exit codes: 0 clean (warnings allowed), 1 errors found, 2 usage/file problem.
"""
import argparse
import difflib
import glob
import os
import re
import sys

# --- budgets (from the framework contract; see course-state.md header and spec §4) ---
TOPIC_NAME_MAX_WORDS = 8      # parentheticals count
TABLE_SOFT_CEILING = 50       # uni-assess walks every row; a longer form stops being a form
COURSE_TARGET_ROWS = 35       # design target for a full course; per-import target derives from it
DEFAULT_UNITS = 15            # one unit per teaching week when the student doesn't know
IMPORT_ROWS_SANITY_MAX = 10   # more rows than this from one import is almost always too fine
EXAM_ANGLES_RANGE = (3, 8)    # predicted angles only; (lecturer example) bullets don't count
# A hedge next to a formula means the source wasn't actually read. The fix is to
# rasterize the page and re-transcribe (or replace the entry with its figure-index
# pointer if genuinely illegible) — never to ship the guess with a warning label.
HEDGE_WORDS = ("schematic", "approximate", "approximately", "roughly", "presumably")
FUZZY_MATCH_RATIO = 0.85      # similarity that still counts a lecturer example as found (not verbatim)

STATUS_VALUES = {"new", "weak", "ok", "strong"}
# lowercase tokens that legitimately appear between multiplication dots
KNOWN_FUNCTIONS = {"sin", "cos", "tan", "cot", "log", "ln", "exp", "max", "min", "det", "tr",
                   "rank", "dim", "sgn", "sup", "inf", "lim", "mod", "diag", "and", "or", "not",
                   "xor", "grad", "div", "curl", "arg", "sinh", "cosh", "tanh", "rot", "sec"}
REQUIRED_DIGEST_SECTIONS = [
    "core concepts", "key relationships", "formulas", "likely exam angles",
    "open questions", "connections", "figure index", "topics registered",
]
REQUIRED_BRIEF_SECTIONS = [
    "exam facts", "question archetypes", "recurring past-exam tasks",
    "priorities", "watch-list",
]

errors, warnings, infos = [], [], []


def err(msg):
    errors.append(msg)


def warn(msg):
    warnings.append(msg)


def info(msg):
    infos.append(msg)


# ---------- generic helpers ----------

def read(path, what):
    if not path:
        return None
    if not os.path.isfile(path):
        print(f"usage: {what} not found: {path}")
        sys.exit(2)
    return open(path, encoding="utf-8", errors="replace").read()


def strip_html_comments(text):
    """Blank out HTML comments but keep their newlines, so reported line numbers match the file."""
    return re.sub(r"<!--.*?-->", lambda m: "\n" * m.group(0).count("\n"), text, flags=re.S)


def sections(text):
    """[(header_lower, header_line, body_text, first_line_no)] for every '## ' section."""
    out, header, body, start = [], None, [], 0
    for i, line in enumerate(text.splitlines(), 1):
        if line.startswith("## "):
            if header is not None:
                out.append((header.lower(), header, "\n".join(body), start))
            header, body, start = line[3:].strip(), [], i
        elif header is not None:
            body.append(line)
    if header is not None:
        out.append((header.lower(), header, "\n".join(body), start))
    return out


def section(secs, prefix):
    return next((s for s in secs if s[0].startswith(prefix)), None)


def bullets(body):
    """Top-level bullet blocks ('- ' lines with their indented continuations)."""
    blocks, cur = [], None
    for line in body.splitlines():
        if re.match(r"^- ", line):
            if cur:
                blocks.append(cur)
            cur = [line]
        elif cur is not None and line.strip() and line.startswith(" "):
            cur.append(line)
        else:
            if cur:
                blocks.append(cur)
            cur = None
    if cur:
        blocks.append(cur)
    return [" ".join(l.strip() for l in b) for b in blocks]


def normalize(s):
    s = s.lower()
    s = re.sub(r"\*\(lecturer example\)\*|\(lecturer example\)", " ", s)
    s = re.sub(r"\((?:p|pp|page|slide|slides)\.?\s*\d+[^)]*\)", " ", s)   # page annotations
    s = re.sub(r"[*_`\"“”‘’']", " ", s)
    s = re.sub(r"^\s*-\s+", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def has_page(s):
    return re.search(r"\b(?:p|pp)\.?\s*\d+|\bpages?\s*\d+|\bslides?\s*\d+|\bfolie\s*\d+", s, re.I) is not None


def has_file(s):
    return re.search(r"[\w\-. ]+\.(?:pdf|pptx|ppt|docx|md|txt|png|jpe?g)\b", s, re.I) is not None


def topic_ids(s):
    """Expand 'T07–T10, T12' into a set of 'T07'-style IDs."""
    ids = set()
    for a, b in re.findall(r"T(\d+)\s*[–—-]\s*T?(\d+)", s):
        for n in range(int(a), int(b) + 1):
            ids.add(f"T{n:02d}")
    for n in re.findall(r"\bT(\d+)\b", s):
        ids.add(f"T{int(n):02d}")
    return ids


# ---------- course-state.md ----------

def parse_state(text):
    header = {}
    for key in ("exam", "plan-mode", "units", "updated", "framework"):
        m = re.search(rf"^{key}:\s*(.*?)\s*(?:·|$)", text, re.M)
        if m:
            header[key] = m.group(1).strip()
    m = re.search(r"plan-mode:\s*(\S+)", text)
    if m:
        header["plan-mode"] = m.group(1)
    rows, malformed = {}, []
    for i, line in enumerate(text.splitlines(), 1):
        if not re.match(r"^\|\s*T\d+\s*\|", line):
            continue
        # split on unescaped pipes only: "\|" inside a cell is a literal pipe (P=K[R\|t])
        cells = [c.strip() for c in re.split(r"(?<!\\)\|", line.strip().strip("|"))]
        if len(cells) not in (5, 6):   # 6 = a legacy file with a Note column; read fine
            malformed.append((i, line.strip()))
            continue
        tid = cells[0]
        rows[tid] = dict(line=i, id=tid, unit=cells[1], topic=cells[2],
                         status=cells[3], last=cells[4], raw=line)
    sched = section(sections(text), "schedule")
    return header, rows, malformed, (sched[2] if sched else None)


def parse_units(header):
    raw = header.get("units", "")
    m = re.search(r"\d+", raw)
    assumed = "assumed" in raw.lower() or not m
    return (int(m.group()) if m else DEFAULT_UNITS), assumed, raw


def check_state(new_text, prev_text, sessions, count_added=True):
    header, rows, malformed, sched = parse_state(new_text)
    for ln, raw in malformed:
        err(f"state: malformed topic row at line {ln} (expected 5 cells: ID|Unit|Topic|Status|Last): {raw}")
    if "units" not in header:
        warn("state: no 'units:' header line — treated as 15 (assumed); add the line on write")
    units, assumed, units_raw = parse_units(header)

    ids = sorted(rows, key=lambda t: int(t[1:]))
    for i, tid in enumerate(ids, 1):
        if int(tid[1:]) != i:
            err(f"state: topic IDs are not sequential — expected T{i:02d} at position {i}, found {tid} "
                f"(IDs are permanent: never renumber; fill gaps only by appending)")
            break
    for tid in ids:
        r = rows[tid]
        words = len(r["topic"].split())
        if words > TOPIC_NAME_MAX_WORDS:
            err(f"state: {tid} topic name has {words} words (max {TOPIC_NAME_MAX_WORDS}, parentheticals count): "
                f"\"{r['topic']}\" — shorten it; the digest carries the detail")
        if r["status"] not in STATUS_VALUES:
            err(f"state: {tid} status \"{r['status']}\" not in {sorted(STATUS_VALUES)}")
        if not re.match(r"^(—|-|\d{4}-\d{2}-\d{2}(\s*\(self\))?)$", r["last"]):
            warn(f"state: {tid} 'Last' cell \"{r['last']}\" is not — or YYYY-MM-DD [(self)]")
    if len(rows) > TABLE_SOFT_CEILING:
        warn(f"state: topic table has {len(rows)} rows — past the soft ceiling of {TABLE_SOFT_CEILING}; "
             f"uni-assess walks every row, so go coarser on this and later imports")

    added = set(ids)
    if prev_text is not None:
        pheader, prows, pmal, psched = parse_state(prev_text)
        added = set(ids) - set(prows)
        for tid, pr in prows.items():
            if tid not in rows:
                err(f"state: pre-existing row {tid} is missing from the new file (rows are never deleted at import)")
                continue
            nr = rows[tid]
            for cell in ("unit", "topic", "status", "last"):
                if pr[cell] != nr[cell]:
                    err(f"state: pre-existing row {tid} changed its {cell}: \"{pr[cell]}\" → \"{nr[cell]}\" "
                        f"(existing rows stay byte-identical at import — no exceptions; "
                        f"a resolution belongs in the new digest's Connections, not here)")
        if psched is not None and psched.strip() != (sched or "").strip():
            err("state: the Schedule section changed — an import never touches the schedule "
                "(new topics get folded in by uni-plan)")
        if pheader.get("exam") != header.get("exam"):
            warn(f"state: 'exam:' header changed \"{pheader.get('exam')}\" → \"{header.get('exam')}\" — "
                 f"only allowed when the material announces the upcoming exam's own date")
        punits, passumed, praw = parse_units(pheader)
        if "units" in header and pheader.get("units") != header.get("units"):
            if passumed or "units" not in pheader:
                info(f"state: 'units:' set to \"{units_raw}\" (was \"{praw or 'absent'}\")")
            else:
                warn(f"state: 'units:' changed \"{praw}\" → \"{units_raw}\" although it was not marked assumed — "
                     f"say why to the student")
    else:
        warn("state: no --prev given — cannot verify that pre-existing rows are untouched; "
             "pass the course-state.md the run started from")

    if not count_added:          # brief-only run: no rows are added, nothing to compare
        return rows, header
    n_added = len(added)
    target = max(1, round(COURSE_TARGET_ROWS / units * sessions))
    sess = int(sessions) if float(sessions).is_integer() else sessions
    src = f"{COURSE_TARGET_ROWS} ÷ {units}{' (assumed)' if assumed else ''} units × {sess} session(s)"
    info(f"state: {n_added} row(s) added this import; target ≈ {target} ({src}); table now {len(rows)} rows")
    if n_added > IMPORT_ROWS_SANITY_MAX:
        warn(f"state: {n_added} rows from one import exceeds the sanity range (1–{IMPORT_ROWS_SANITY_MAX}) — "
             f"almost certainly too fine-grained; merge under parent themes")
    elif n_added > target + 2:
        warn(f"state: {n_added} rows added vs target ≈ {target} — go coarser unless the material is unusually broad")
    elif prev_text is not None and 0 < n_added < max(1, target - 1):
        warn(f"state: only {n_added} row(s) added vs target ≈ {target} — fine if the unit is thin; otherwise check "
             f"that themes worth rating separately weren't merged")
    return rows, header


# ---------- digest ----------

def digest_open_qids(text):
    """Q-IDs citable in a digest: explicit `Q<n> ·` IDs, or positional ones for a
    legacy digest without IDs (same numbering prior_digests.py prints)."""
    secs = sections(strip_html_comments(text))
    op = next((s for s in secs if s[0].startswith("open question")), None)
    if not op:
        return set()
    qids, pos = set(), 0
    for b in bullets(op[2]):
        if re.match(r"^-\s*—", b):
            continue
        pos += 1
        m = re.match(r"^-\s*Q(\d+)\s*·", b)
        qids.add(int(m.group(1)) if m else pos)
    return qids


def parse_scratch(scratch_dir):
    """Read lecturer-examples.md: `- task: "…" (p.N)` / `- rhetorical: …` entries.

    Untagged bullets (a scratch file written before the two classes existed, or a
    forgotten tag) are treated as tasks — the safe direction, since a task must
    reach the digest and the check will say so.
    """
    tasks, rhetoricals = [], []
    sfile = os.path.join(scratch_dir, "lecturer-examples.md")
    if not os.path.isfile(sfile):
        return None, None, sfile
    for b in bullets(open(sfile, encoding="utf-8", errors="replace").read()):
        body = re.sub(r"^-\s*", "", b).strip()
        m = re.match(r"(task|rhetorical)\s*:\s*(.+)$", body, re.I)
        if m and m.group(1).lower() == "rhetorical":
            rhetoricals.append(normalize(m.group(2)))
        else:
            tasks.append(normalize(m.group(2) if m else body))
    return tasks, rhetoricals, sfile


def check_digest(text, state_rows, prev_text, scratch_dir, ignore_figs, project_dir=None, digest_path=None):
    body_all = strip_html_comments(text)
    secs = sections(body_all)
    for name in REQUIRED_DIGEST_SECTIONS:
        if section(secs, name) is None:
            warn(f"digest: no '## {name.capitalize()}' section — the template has one; write '— none —' rather than omitting it")

    # --- figure index ---
    fig_sec = section(secs, "figure index")
    defined, dup = {}, []
    if fig_sec:
        for i, line in enumerate(fig_sec[2].splitlines(), fig_sec[3] + 1):
            rng = re.match(r"^\s*-\s*F(\d+)\s*[–—-]\s*F?(\d+)\b(.*)$", line)
            if rng:
                a, b = int(rng.group(1)), int(rng.group(2))
                err(f"digest: index entry F{a}–F{b} (line {i}) defines a range — one line per figure, each with its "
                    f"own page, or the tutor cannot rasterize F{a + 1}")
                for fid in range(a, b + 1):
                    defined[fid] = i          # count them as defined so the range error isn't repeated per ID
                continue
            m = re.match(r"^\s*-\s*F(\d+)\b(.*)$", line)
            if not m:
                continue
            fid, rest = int(m.group(1)), m.group(2)
            if fid in defined:
                dup.append(fid)
            defined[fid] = i
            if not has_file(rest):
                err(f"digest: figure F{fid} (line {i}) has no source file — the tutor needs `file` p.N to rasterize it")
            if not has_page(rest):
                err(f"digest: figure F{fid} (line {i}) has no page number — the tutor needs `file` p.N to rasterize it")
        for fid in dup:
            err(f"digest: figure F{fid} is defined more than once in the index")
        if defined:
            expected = set(range(1, max(defined) + 1))
            gaps = sorted(expected - set(defined))
            if gaps:
                warn(f"digest: figure IDs skip {', '.join('F%d' % g for g in gaps)} — fine if a figure was dropped, "
                     f"as long as nothing cites it (checked below)")
    else:
        err("digest: no Figure index section — every digest needs one (write '— none in this unit —' if truly figure-free)")

    # --- inline references outside the index ---
    body_wo_index = body_all
    if fig_sec:
        body_wo_index = body_all.replace(fig_sec[2], "")
    cited = {}
    for i, line in enumerate(body_wo_index.splitlines(), 1):
        for a, b in re.findall(r"\bF(\d+)\s*[–—-]\s*F?(\d+)\b", line):
            for n in range(int(a), int(b) + 1):
                cited.setdefault(n, i)
        for n in re.findall(r"\bF(\d+)\b", line):
            cited.setdefault(int(n), i)
    for fid in sorted(cited):
        if fid in ignore_figs:
            continue
        if fid not in defined:
            have = f"F1–F{max(defined)}" if defined else "nothing"
            err(f"digest: inline reference F{fid} (line ~{cited[fid]}) has no index entry — index defines {have}. "
                f"Add the index line (file + page) or fix the reference; never leave the tutor a dead pointer")

    # --- formulas: hedges, page refs, and the subscript-as-product heuristic ---
    form = section(secs, "formulas")
    non_examinable = bool(re.search(r"^\*\*Examinable:\*\*\s*no", text, re.M | re.I))
    if non_examinable:
        info("digest: title block says Examinable: no — exam-angle floor waived")
    if form:
        for b in bullets(form[2]):
            low = b.lower()
            hit = next((h for h in HEDGE_WORDS if h in low), None)
            if hit:
                err(f"digest: hedged formula (\"{hit}\") — a hedge means the source page wasn't read. "
                    f"Rasterize the page, transcribe what the image shows, and drop the hedge "
                    f"(or replace the entry with its figure-index pointer if genuinely illegible): \"{b[:90]}\"")
            if re.search(r"[=←→≈]", b) and not (has_page(b) or re.search(r"\bF\d+\b", b)):
                warn(f"digest: formula bullet has no (p.N) or F# source reference: \"{b[:80]}\"")
        for i, line in enumerate(form[2].splitlines(), form[3] + 1):
            for tok in re.findall(r"[A-Za-z0-9⁻¹²³)\]]·([a-z]{2,6})·", line):
                if tok not in KNOWN_FUNCTIONS:
                    warn(f"digest: line {i} has \"·{tok}·\"-style token — if \"{tok}\" is a subscript, write it with an "
                         f"underscore (X_{tok}); a middle dot means multiplication")
                    break

    # --- exam angles & lecturer questions (two classes) ---
    ang = section(secs, "likely exam angles")
    if ang:
        blocks = bullets(ang[2])
        real = [b for b in blocks if b.strip() and not b.strip().startswith("- —")]
        marked = [b for b in real if "lecturer example" in b.lower()]
        predicted = len(real) - len(marked)   # marked bullets are captured signal, not predictions
        lo, hi = EXAM_ANGLES_RANGE
        if predicted > hi:
            warn(f"digest: {predicted} predicted exam angles (excluding {len(marked)} lecturer examples), "
                 f"expected {lo}–{hi} — condense the predictions, never the captured examples")
        elif predicted < lo and not non_examinable:
            warn(f"digest: only {predicted} predicted exam angle(s) (excluding {len(marked)} lecturer examples), "
                 f"expected {lo}–{hi} — remember condensation never deletes an angle whose data moved "
                 f"to the figure index (an organizational unit can declare 'Examinable: no' instead)")
        info(f"digest: {predicted} predicted angle(s) + {len(marked)} lecturer example(s) in §Likely exam angles")
    all_blocks = bullets(body_all)
    if scratch_dir:
        tasks, rhetoricals, sfile = parse_scratch(scratch_dir)
        if tasks is None:
            warn(f"digest: {sfile} not found — if the material had lecturer-posed questions they were not captured "
                 f"at first sight; if it had none, fine")
        else:
            norm_blocks = [(normalize(b), b) for b in all_blocks]
            for e in [e for e in tasks if e]:
                hit = next(((nb, b) for nb, b in norm_blocks if e in nb), None)
                if hit is None:
                    best = max(norm_blocks, key=lambda x: difflib.SequenceMatcher(None, e, x[0]).ratio(), default=None)
                    ratio = difflib.SequenceMatcher(None, e, best[0]).ratio() if best else 0
                    if best and ratio >= FUZZY_MATCH_RATIO:
                        hit = best
                        warn(f"digest: lecturer example is present but not verbatim (similarity {ratio:.2f}): \"{e[:70]}…\" — "
                             f"restore the lecturer's exact wording")
                    else:
                        err(f"digest: task-class lecturer example from the scratch file is missing from the digest: \"{e[:90]}\"")
                        continue
                if "lecturer example" not in hit[1].lower():
                    err(f"digest: lecturer example is in the digest but NOT marked *(lecturer example)*: \"{e[:90]}\"")
            body_norm = normalize(body_all)
            for e in [e for e in (rhetoricals or []) if e]:
                if e in body_norm:
                    err(f"digest: rhetorical-class prompt from the scratch file appears in the digest — rhetorical "
                        f"teaching prompts are ignored entirely (not an exam angle, not an open question): \"{e[:90]}\"")
            info(f"digest: scratch checked — {len(tasks)} task(s) must be in, {len(rhetoricals)} rhetorical(s) must be out")
    else:
        info("digest: no --scratch given — lecturer-question provenance not verified")

    # --- open questions: Q-IDs, one gap per bullet ---
    op = section(secs, "open questions")
    open_qids = set()
    if op:
        expected = 0
        for b in [b for b in bullets(op[2]) if not re.match(r"^-\s*—", b)]:
            expected += 1
            m = re.match(r"^-\s*Q(\d+)\s*·\s*(.*)$", b)
            if not m:
                err(f"digest: open-question bullet without a 'Q<n> ·' ID (IDs are what later imports cite): \"{b[:80]}\"")
                continue
            qid = int(m.group(1))
            open_qids.add(qid)
            if qid != expected:
                err(f"digest: open-question IDs out of sequence — expected Q{expected}, found Q{qid}")
            body = m.group(2)
            if len(body) > 220 or body.count(",") >= 3 or " and " in body and body.count(",") >= 2:
                warn(f"digest: Q{qid} reads like a list — one specific gap per bullet, so a later unit can "
                     f"resolve it 1:1 (roadmap previews are not open questions): \"{body[:80]}\"")

    # --- connections: resolves lines cite an existing Q-ID ---
    con = section(secs, "connections")
    if con:
        content = [b for b in bullets(con[2]) if not re.match(r"^-\s*—\s*none", b)]
        prior_exists = project_dir is not None and glob.glob(os.path.join(project_dir, "digest-*.md"))
        if not content and prior_exists:
            warn("digest: §Connections is empty although earlier digests exist — run scripts/prior_digests.py and "
                 "link what this unit builds on or resolves (or confirm it truly stands alone)")
        for b in content:
            if not re.search(r"digest-\d+|\bT\d+\b|per the lecturer", b):
                warn(f"digest: Connections line names no digest or topic ID: \"{b[:80]}\"")
            if re.search(r"\bresolves\b", b, re.I):
                m = re.search(r"resolves\s+digest-(\d+)\s+Q(\d+)", b, re.I)
                if not m:
                    err(f"digest: 'resolves' line does not cite a Q-ID — the format is "
                        f"'resolves digest-NN Qk: <answer in one clause>': \"{b[:90]}\"")
                elif project_dir:
                    dn, qn = int(m.group(1)), int(m.group(2))
                    cands = sorted(glob.glob(os.path.join(project_dir, f"digest-{dn:02d}-*.md")) +
                                   glob.glob(os.path.join(project_dir, f"digest-{dn}-*.md")))
                    if not cands:
                        err(f"digest: 'resolves digest-{dn:02d} Q{qn}' cites a digest that is not in the project")
                    else:
                        qids = digest_open_qids(open(cands[0], encoding="utf-8", errors="replace").read())
                        if qn not in qids:
                            have = ", ".join(f"Q{q}" for q in sorted(qids)) or "none"
                            err(f"digest: 'resolves digest-{dn:02d} Q{qn}' — that digest has no Q{qn} "
                                f"(its open questions: {have})")
                else:
                    warn("digest: 'resolves' citation not verified — pass --project to check it against the cited digest")

    # --- slug consistency ---
    if digest_path and project_dir:
        m = re.match(r"digest-\d+-(.+)\.md$", os.path.basename(digest_path))
        if m:
            slug = m.group(1)
            base = re.sub(r"-\d+$", "", slug)
            for other in glob.glob(os.path.join(project_dir, "digest-*.md")):
                om = re.match(r"digest-\d+-(.+)\.md$", os.path.basename(other))
                if not om or os.path.basename(other) == os.path.basename(digest_path):
                    continue
                oslug = om.group(1)
                if oslug != slug and re.sub(r"-\d+$", "", oslug) == base:
                    warn(f"digest: slug '{slug}' differs from existing '{oslug}' only by a numeric suffix — "
                         f"number every part of a multi-part topic consistently")

    # --- topics registered ---
    top = section(secs, "topics registered")
    if top:
        m = re.search(r"Topics:\s*(.+)", top[2])
        if not m:
            err("digest: 'Topics registered' section has no 'Topics: T..–T..' line")
        elif state_rows is not None:
            for tid in sorted(topic_ids(m.group(1))):
                if tid not in state_rows:
                    err(f"digest: Topics registered cites {tid}, which is not in course-state.md")
        else:
            warn("digest: no --state given — Topics registered IDs not verified")

    # --- connections ---
    con = section(secs, "connections")
    if con:
        content = [b for b in bullets(con[2]) if not re.match(r"^-\s*—\s*none", b)]
        prior_exists = prev_text is not None and bool(parse_state(prev_text)[1])
        if not content and prior_exists:
            warn("digest: §Connections is empty although earlier units exist — run scripts/prior_digests.py and link "
                 "what this unit builds on or resolves (or confirm it truly stands alone)")
        for b in content:
            if not re.search(r"digest-\d+|\bT\d+\b|per the lecturer", b):
                warn(f"digest: Connections line names no digest or topic ID: \"{b[:80]}\"")


# ---------- exam-brief.md ----------

def check_brief(text, state_rows):
    body = strip_html_comments(text)
    secs = sections(body)
    for name in REQUIRED_BRIEF_SECTIONS:
        if section(secs, name) is None:
            warn(f"brief: no '## {name}' section — the template has one")
    for i, line in enumerate(body.splitlines(), 1):
        if re.search(r"\bFigure:|^\s*-\s*F\d+\s*·", line):
            if not has_file(line) or not has_page(line):
                err(f"brief: figure entry at line {i} lacks file + page: \"{line.strip()[:80]}\"")
        m = re.search(r"\(hits\s+([^)]*)\)", line)
        if m:
            if state_rows is None:
                warn(f"brief: archetype at line {i} cites topic IDs but no --state given to verify them")
            else:
                for tid in sorted(topic_ids(m.group(1))):
                    if tid not in state_rows:
                        err(f"brief: archetype at line {i} cites {tid}, which is not in course-state.md")


# ---------- main ----------

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--digest")
    ap.add_argument("--state")
    ap.add_argument("--prev")
    ap.add_argument("--scratch")
    ap.add_argument("--brief")
    ap.add_argument("--project")
    ap.add_argument("--sessions", type=float, default=1.0)
    ap.add_argument("--ignore-figs", default="")
    a = ap.parse_args()
    if not (a.digest or a.brief or a.state):
        ap.print_help()
        return 2

    state_text = read(a.state, "--state")
    prev_text = read(a.prev, "--prev")
    state_rows = None
    if state_text is not None:
        state_rows, _ = check_state(state_text, prev_text, a.sessions, count_added=bool(a.digest))
    if a.digest:
        ignore = {int(x.strip().lstrip("Ff")) for x in a.ignore_figs.split(",") if x.strip()}
        check_digest(read(a.digest, "--digest"), state_rows, prev_text, a.scratch, ignore,
                     project_dir=a.project, digest_path=a.digest)
    if a.brief:
        check_brief(read(a.brief, "--brief"), state_rows)

    for m in errors:
        print("ERROR  " + m)
    for m in warnings:
        print("WARN   " + m)
    for m in infos:
        print("info   " + m)
    if errors:
        print(f"\nSummary: {len(errors)} error(s), {len(warnings)} warning(s) — FIX AND RE-RUN BEFORE DELIVERING")
        return 1
    print(f"\nSummary: 0 errors, {len(warnings)} warning(s) — OK to deliver"
          + (" (read the warnings and say what you decided)" if warnings else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
