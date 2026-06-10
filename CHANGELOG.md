# Changelog

All notable changes to **math-harness** are documented here. Format loosely follows
[Keep a Changelog](https://keepachangelog.com/); versions follow [SemVer](https://semver.org/).

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
