#!/usr/bin/env python3
"""
pdf_triage.py — cheap-first triage for lecture PDFs.

Goal: figure out which slides are worth a VISUAL look (rasterize + read) without
rasterizing the whole deck (~1,600 tokens/page vs ~300 for text). The naive signal —
"few characters of text" — does NOT work on real lecture slides: almost every slide
carries header/footer boilerplate (course name, lecturer, slide number) and diagrams
have text labels inside them, so a diagram slide often has MORE characters than a
sparse title slide. Char count is therefore a poor diagram detector.

Instead we use STRUCTURAL signals that are largely independent of boilerplate text:
  * vector_paths — number of vector drawing objects on the page (lines, rects,
    curves). Bullet-text slides have ~0; diagrams/figures/graphs have many.
  * image_area  — fraction of the page covered by embedded raster images (photos,
    screenshots, scanned figures).
  * chars       — kept only as a weak backstop for near-empty pages.

A page is flagged "look at this visually" if it has enough vector drawing content OR a
meaningful embedded image OR almost no text. The script prints a per-page signal table
and the deck-level picture so you can sanity-check and adjust — the flag is a strong
hint, not gospel.

Best results need PyMuPDF (`pip install pymupdf --break-system-packages`). Without it,
the script falls back to poppler (raster-image detection + char count only) and warns
that vector-diagram detection is OFF.

Subcommands:
  triage   Write per-page text to <outdir>/text/page-NNN.txt and a manifest of signals.
  raster   Rasterize specific pages to <outdir>/img/ and print exact paths.

Examples:
  python pdf_triage.py triage lecture.pdf --outdir /home/claude/L2
  python pdf_triage.py raster lecture.pdf --pages 2,4,5 --dpi 150 --outdir /home/claude/L2
"""
import argparse
import json
import os
import re
import subprocess
import sys

try:
    import fitz  # PyMuPDF
    HAVE_FITZ = True
except Exception:
    HAVE_FITZ = False


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


# ---------- signal extraction ----------

def signals_fitz(pdf, text_dir, pad):
    """Per-page signals using PyMuPDF: chars, vector_paths, images, image_area_frac."""
    doc = fitz.open(pdf)
    n = doc.page_count
    pad = max(pad, len(str(n)))
    pages = []
    for i in range(n):
        page = doc[i]
        text = page.get_text("text")
        chars = len(text.strip())
        try:
            vpaths = len(page.get_drawings())
        except Exception:
            vpaths = 0
        imgs = page.get_images(full=True)
        parea = float(page.rect.width * page.rect.height) or 1.0
        iarea = 0.0
        for im in imgs:
            try:
                for r in page.get_image_rects(im[0]):
                    iarea += r.width * r.height
            except Exception:
                pass
        fname = os.path.join(text_dir, f"page-{i+1:0{pad}d}.txt")
        with open(fname, "w") as f:
            f.write(text)
        pages.append({
            "page": i + 1, "chars": chars, "vector_paths": vpaths,
            "images": len(imgs), "image_area_frac": round(min(iarea / parea, 1.0), 3),
            "text_file": fname,
        })
    return n, pages, pad


def page_count_poppler(pdf):
    out = run(["pdfinfo", pdf])
    m = re.search(r"^Pages:\s+(\d+)", out.stdout, re.M)
    if not m:
        raise SystemExit("pdfinfo failed; is poppler-utils installed?")
    return int(m.group(1))


def signals_poppler(pdf, text_dir, pad):
    """Degraded fallback: char count + raster-image presence only (NO vector paths)."""
    n = page_count_poppler(pdf)
    pad = max(pad, len(str(n)))
    full = run(["pdftotext", "-layout", pdf, "-"])
    raw = full.stdout.split("\x0c")
    if len(raw) > n:
        raw = raw[:n]
    while len(raw) < n:
        raw.append("")
    # raster images per page via pdfimages -list
    img_counts = {p: 0 for p in range(1, n + 1)}
    il = run(["pdfimages", "-list", pdf])
    for line in il.stdout.splitlines():
        m = re.match(r"\s*(\d+)\s+", line)
        if m:
            p = int(m.group(1))
            if 1 <= p <= n:
                img_counts[p] = img_counts.get(p, 0) + 1
    pages = []
    for i in range(n):
        text = raw[i]
        fname = os.path.join(text_dir, f"page-{i+1:0{pad}d}.txt")
        with open(fname, "w") as f:
            f.write(text)
        pages.append({
            "page": i + 1, "chars": len(text.strip()), "vector_paths": None,
            "images": img_counts.get(i + 1, 0), "image_area_frac": None,
            "text_file": fname,
        })
    return n, pages, pad


# ---------- flagging ----------

# Typeset equations extract as characters from the Mathematical Alphanumeric
# Symbols unicode block (U+1D400-U+1D7FF) — italic/bold math letters that ordinary
# prose never produces. 8+ such characters means a real equation, not a stray
# symbol: on the deck this was calibrated against, the threshold marked exactly
# the equation pages (their counts were 19-37) with zero false positives, and a
# single inline variable mention stays safely below it.
MATH_GLYPHS_MIN = 8
_MATH_BLOCK = re.compile("[\U0001D400-\U0001D7FF]")


def count_math_glyphs(text):
    return len(_MATH_BLOCK.findall(text))


def flag_pages(pages, paths_thresh, img_area_thresh, char_thresh, img_count_thresh):
    flagged = []
    for pg in pages:
        reasons = []
        vp = pg["vector_paths"]
        if vp is not None and vp >= paths_thresh:
            reasons.append(f"vector_paths={vp}")
        iaf = pg["image_area_frac"]
        if iaf is not None and iaf >= img_area_thresh:
            reasons.append(f"image_area={iaf:.0%}")
        # In fallback mode (no area), use raw image count as the image signal.
        if iaf is None and pg["images"] >= img_count_thresh:
            reasons.append(f"images={pg['images']}")
        if pg["chars"] < char_thresh:
            reasons.append(f"sparse_text={pg['chars']}c")
        pg["flagged"] = bool(reasons)
        pg["reasons"] = reasons
        if reasons:
            flagged.append(pg["page"])
        # Math marker, separate from the raster flags: equations live on this page,
        # so the formula fidelity rule applies when transcribing it (rasterize THIS
        # page if grouping/notation is in doubt). It does not by itself mean raster.
        try:
            with open(pg["text_file"], encoding="utf-8", errors="replace") as f:
                pg["math_glyphs"] = count_math_glyphs(f.read())
        except OSError:
            pg["math_glyphs"] = 0
        pg["math"] = pg["math_glyphs"] >= MATH_GLYPHS_MIN
    return flagged


# ---------- subcommands ----------

def cmd_triage(args):
    pdf = args.pdf
    if not os.path.exists(pdf):
        raise SystemExit(f"File not found: {pdf}")
    text_dir = os.path.join(args.outdir, "text")
    os.makedirs(text_dir, exist_ok=True)
    pad = 3

    if HAVE_FITZ:
        n, pages, pad = signals_fitz(pdf, text_dir, pad)
        mode = "pymupdf"
    else:
        n, pages, pad = signals_poppler(pdf, text_dir, pad)
        mode = "poppler-fallback"

    total_chars = sum(p["chars"] for p in pages)
    scanned = total_chars < 5 * n  # essentially no text layer anywhere

    flagged = flag_pages(pages, args.paths_threshold, args.img_area_threshold,
                         args.char_threshold, args.img_count_threshold)

    manifest = {
        "pdf": os.path.abspath(pdf), "page_count": n, "mode": mode,
        "scanned": scanned, "text_dir": os.path.abspath(text_dir),
        "thresholds": {
            "vector_paths": args.paths_threshold,
            "image_area_frac": args.img_area_threshold,
            "image_count_fallback": args.img_count_threshold,
            "sparse_chars": args.char_threshold,
        },
        "flagged_pages": flagged, "pages": pages,
    }
    mpath = os.path.join(args.outdir, "manifest.json")
    with open(mpath, "w") as f:
        json.dump(manifest, f, indent=2)

    # ---- human-readable report ----
    print(f"PDF: {pdf}   ({n} pages, mode={mode})")
    if mode == "poppler-fallback":
        print("WARNING: PyMuPDF not found — vector-diagram detection is OFF.")
        print("  Install it for accurate detection: pip install pymupdf --break-system-packages")
    if scanned:
        print("WARNING: little/no text layer (scanned?). Treat ALL pages as visual:")
        print("  rasterize and read, or OCR in bulk (see pdf-reading skill).")
    print(f"Per-page text: {text_dir}/page-NNN.txt   Manifest: {mpath}")
    print()
    hdr = f"{'pg':>3} {'chars':>6} {'vpaths':>7} {'imgs':>5} {'img%':>5} {'math':>5}  flagged / why"
    print(hdr); print("-" * len(hdr))
    for p in pages:
        vp = "-" if p["vector_paths"] is None else p["vector_paths"]
        iaf = "-" if p["image_area_frac"] is None else f"{p['image_area_frac']*100:.0f}"
        mg = p.get("math_glyphs", 0)
        mcol = f"{mg}*" if p.get("math") else (str(mg) if mg else "")
        mark = "**" if p["flagged"] else "  "
        why = ", ".join(p["reasons"]) if p["flagged"] else ""
        print(f"{p['page']:>3} {p['chars']:>6} {str(vp):>7} {p['images']:>5} {iaf:>5} {mcol:>5}  {mark} {why}")
    print()
    frac = len(flagged) / n if n else 0
    print(f"Flagged for visual inspection ({len(flagged)}/{n}): {flagged or 'none'}")
    math_pages = [p["page"] for p in pages if p.get("math")]
    if math_pages:
        print(f"Equation pages (math glyphs in text layer): {math_pages}")
        print("  Formulas on these pages: transcribe simple standard-notation ones from the")
        print("  text; rasterize the page first when grouping is ambiguous, layout is")
        print("  matrix/multi-line, or the notation is the course's own.")
    if frac >= 0.7:
        print("  NOTE: most pages flagged — this is a diagram-heavy deck. It may be")
        print("  simpler to rasterize the whole deck at lower DPI (e.g. -r 110) and skim.")
    elif not flagged and not scanned:
        print("  NOTE: nothing flagged. If this is a slide deck, sample 1-2 pages anyway")
        print("  to confirm the heuristic isn't missing label-only diagrams; or lower")
        print("  --paths-threshold. Bullet-text decks legitimately flag nothing.")
    print()
    print("Rasterize the flagged (or any you judge figure-heavy) with:")
    fl = ",".join(str(p) for p in (flagged or [1]))
    print(f"  python {os.path.basename(__file__)} raster '{pdf}' --pages {fl} --outdir {args.outdir}")


def parse_pages(spec, n):
    pages = set()
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            a, b = part.split("-", 1)
            for p in range(int(a), int(b) + 1):
                pages.add(p)
        else:
            pages.add(int(part))
    return sorted(p for p in pages if 1 <= p <= n)


def cmd_raster(args):
    pdf = args.pdf
    if not os.path.exists(pdf):
        raise SystemExit(f"File not found: {pdf}")
    n = fitz.open(pdf).page_count if HAVE_FITZ else page_count_poppler(pdf)
    pages = parse_pages(args.pages, n)
    if not pages:
        raise SystemExit("No valid pages to rasterize.")
    img_dir = os.path.join(args.outdir, "img")
    os.makedirs(img_dir, exist_ok=True)
    written = []
    for p in pages:
        prefix = os.path.join(img_dir, "page")
        out = run(["pdftoppm", "-jpeg", "-r", str(args.dpi),
                   "-f", str(p), "-l", str(p), pdf, prefix])
        if out.returncode != 0:
            print(f"page {p}: pdftoppm failed: {out.stderr.strip()}", file=sys.stderr)
            continue
        matches = [os.path.join(img_dir, f) for f in os.listdir(img_dir)
                   if re.match(rf"page-0*{p}\.jpg$", f)]
        written.extend(sorted(matches))
    for path in sorted(set(written)):
        print(path)


def main():
    ap = argparse.ArgumentParser(description="Cheap-first triage for lecture PDFs.")
    sub = ap.add_subparsers(dest="command", required=True)

    t = sub.add_parser("triage", help="Per-page text + structural diagram signals.")
    t.add_argument("pdf")
    t.add_argument("--outdir", required=True)
    t.add_argument("--paths-threshold", type=int, default=6,
                   help="Flag pages with >= this many vector drawing paths (default 6).")
    t.add_argument("--img-area-threshold", type=float, default=0.10,
                   help="Flag pages where images cover >= this fraction (default 0.10).")
    t.add_argument("--img-count-threshold", type=int, default=1,
                   help="Fallback (no pymupdf): flag pages with >= this many images.")
    t.add_argument("--char-threshold", type=int, default=30,
                   help="Backstop: flag near-empty pages below this many chars.")
    t.set_defaults(func=cmd_triage)

    r = sub.add_parser("raster", help="Rasterize pages and print their paths.")
    r.add_argument("pdf")
    r.add_argument("--pages", required=True, help="e.g. '2,4,5' or '9-11'")
    r.add_argument("--dpi", type=int, default=150)
    r.add_argument("--outdir", required=True)
    r.set_defaults(func=cmd_raster)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
