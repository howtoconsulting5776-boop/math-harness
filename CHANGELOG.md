# Changelog

All notable changes to **math-harness** are documented here. Format loosely follows
[Keep a Changelog](https://keepachangelog.com/); versions follow [SemVer](https://semver.org/).

## [0.3.0] — 2026-06-10

### Added — correctness & grade-fit enforced by code (review of Codex's docs PR)
- **Regression test suite (`tests/`)** that makes "no wrong solution reaches a student"
  executable: `test_verify.py` asserts the verifier **rejects** extraneous roots, missing
  roots, false identities, and broken steps (and accepts correct work); `test_geometry.py`
  checks coordinate-geometry measurements; `test_grade_check.py` checks the grade linter.
  Runs under `pytest` or the dependency-free `tests/run_tests.py`. 30 tests.
- **`grade_check.py` linter** (`skills/math-solving/scripts/`) — flags above-grade notation
  in a solution/explanation (e.g. variable equations or `√` in an elementary answer, trig
  before 중3, calculus in middle school). Wired into `math-verifier` (QA step) and the
  `math-solving`/`math-explanation` self-checks.
- **`math-tutor` 두 철칙** made explicit: never present an unverified solution as correct;
  never use above-grade tools — verified-but-unintelligible still counts as failure.

### Changed
- CI smoke workflow now **runs the test suite as the real gate** (it previously only ran
  demos, which pass even when `verify.py` prints example `FAIL` lines). Installs pytest.
- Renamed Codex's draft files to canonical names: `smoke_new.yml` → `smoke.yml`,
  `ROADMAP_new.md` → `ROADMAP.md`, `quality_gates_new.md` → `quality-gates.md`; fixed all
  references and the `fig_new.svg` demo path.
- `quality-gates.md` rewritten to distinguish the gating test suite from illustrative demos.

## [0.2.1] — 2026-06-10

### Added
- **Signature 4-step solution frame** (하우투수학): every solution is now structured as
  `1) 구하는 것 → 2) 주어진 것 → 3) 주어진 것을 이용하기 → 4) 배운 것과 연결하기` — a
  transferable problem-solving habit (Polya-style), not just an answer. Baked into
  `math-solving` output, the `math-explanation` scaffolding, the problem-bank note
  template, and filled into `academy-profile.md`. Overridable per-academy via the profile.

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
