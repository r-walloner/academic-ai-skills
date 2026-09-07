# Interpreting pdf_triage.py output

Read this when the triage report needs judgment — most runs won't need it.

## Why the signals are what they are

The naive diagram detector — "few characters of text" — fails on real lecture
slides: nearly every slide carries header/footer boilerplate (course name, lecturer,
slide number), and diagrams contain text labels, so a diagram slide often has *more*
characters than a sparse bullet slide. The script therefore flags on **structural**
signals that ignore boilerplate:

- `vector_paths` — vector drawing objects on the page. Bullet-text slides have ~0;
  diagrams, graphs, and schematics have many. The primary signal.
- `image_area_frac` — fraction of the page covered by embedded raster images
  (photos, screenshots, scanned figures).
- `chars` — kept only as a backstop for near-empty pages.

The per-page table (chars · vpaths · imgs · img%) is printed so you can sanity-check;
the flag is a strong hint, not gospel. Skim the table and add pages your own reading
of the extracted text suggests are figure-heavy (e.g. text that reads like axis
labels or node names).

## The math column (equation pages)

Typeset equations extract as characters from the Mathematical Alphanumeric Symbols
unicode block; the triage table counts them per page (`math` column, `*` at ≥ 8) and
lists the equation pages. The marker is **not** a raster flag — it says "the formula
fidelity rule applies here." Concretely: the text layer of an equation page loses
grouping (parentheses vanish), flattens matrix and multi-line layout, and strips
super-/subscript structure, so what extracts as `K rect K −1` could be a product, a
subscripted matrix, or a function application. Transcribe from the text only when the
formula is simple, in standard notation, and its structure obviously survived; for
anything else — and always when you notice yourself unsure — rasterize that one page
(`raster --pages N`) and transcribe what the image shows. Standard textbook formulas
often come out right from mangled text because the model prior fills the gaps; the
course's *own* notation is exactly where that safety net is absent, and exactly what
the exam will use.

## Special cases the report calls out

- **Most pages flagged (≥ ~70%)** — a diagram-heavy deck. Rasterizing the whole deck
  at lower DPI (e.g. `--dpi 110`) and reading it visually is often simpler than
  interleaving text and selective rasters.
- **Nothing flagged on an obvious slide deck** — sample a page or two anyway to
  confirm the heuristic isn't missing label-only diagrams, or lower
  `--paths-threshold` (default 6). Genuine bullet-text decks legitimately flag
  nothing.
- **Scanned PDF (no text layer)** — the report warns. Treat every page as visual:
  rasterize and read, or OCR in bulk. For deeper PDF handling, consult the general
  pdf skill at `/mnt/skills/public/pdf/SKILL.md` if present.
- **Poppler fallback** — without PyMuPDF the script still runs but **cannot see
  vector diagrams** (it warns). Install the real detector first:
  `pip install pymupdf --break-system-packages`.

## Rasterization

```bash
python scripts/pdf_triage.py raster <file.pdf> --pages 2,4,9-11 --dpi 150 --outdir /home/claude/<unit>
```

150 DPI is right for reading a single slide; 110 for bulk skims. The command prints
the exact image paths — Read those files. Don't rasterize plain-text pages; the
extracted text already has them, and each rasterized page costs ~5x the tokens.
