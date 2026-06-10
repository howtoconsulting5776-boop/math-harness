# Changelog

All notable changes to **math-harness** are documented here. Format loosely follows
[Keep a Changelog](https://keepachangelog.com/); versions follow [SemVer](https://semver.org/).

## [0.2.0] — 2026-06-10

### Added
- **PNG figure output (default for handouts).** `svg_figure.py` now exports student-ready
  PNG via `svglib` (`save("*.png")`, `save_both(stem)` → vector `.svg` + raster `.png`,
  2× resolution by default). SVG stays the dependency-free source of truth; PNG falls back
  to SVG when `svglib` is absent.
- **`problem-bank` skill** — accumulate solved problems / wrong-answer notes as structured
  Markdown with YAML frontmatter (grade, unit, concept, difficulty, type, answer, verified,
  tags), auto-filed under `<grade>/<unit>/`, deduplicated by problem hash, with an
  auto-generated `INDEX.md` (Obsidian/Dataview-friendly). Bundled `scripts/bank.py` +
  `assets/problem-note-template.md`. Wired into `math-tutor` as an opt-in save mode.
- **Finer grade control.** `curriculum-map.md` gains a semester-level *tool-unlock* table;
  new `academy-profile.md` config lets an academy declare its main courses, per-grade
  progress, preferred solution style, and textbooks — which `math-solver` reads and
  prioritizes over the standard curriculum.

### Changed
- Geometry default output is now PNG (handout) + SVG (source); docs updated.
- Dependency note: PNG export uses `svglib` (not matplotlib, which is no longer required).

## [0.1.0] — 2026-06-10

### Added
- Initial release: a K-12 math-education agent-team harness for Claude Code.
- **Agents (4):** `math-solver`, `math-verifier` (general-purpose, runs SymPy),
  `math-explainer`, `math-geometer` (general-purpose, runs Python for SVG / `sympy.geometry`).
- **Skills (5):** `math-tutor` (orchestrator), `math-solving`, `math-verification`,
  `math-explanation`, `geometry-figures`.
- **Bundled scripts:**
  - `math-verification/scripts/verify.py` — SymPy verification helpers.
  - `geometry-figures/scripts/svg_figure.py` — dependency-free SVG figure builder.
  - `geometry-figures/scripts/geo_verify.py` — `sympy.geometry` figure solver.
- **References:** Korea 2022 revised curriculum map, common-misconception catalog, SVG figure recipes.
- Hybrid execution: agent **team** (generate–verify–explain) for single problems / concepts /
  error analysis / geometry; **fan-out** sub-agents for worksheets.
- Plugin + marketplace manifests, Apache-2.0 license, quickstart, GitHub issue/PR templates.
