# Contributing to math-harness

Thanks for helping improve **math-harness** — an agent-team harness for K-12 math education in Claude Code. Contributions of new skills, curriculum mappings, misconception entries, figure recipes, and bug fixes are all welcome.

## Ways to contribute

- **Bug reports** — a wrong solution, a failed verification, a broken figure, a mis-triggered skill. Open an issue with the exact prompt, the grade level, and what you expected.
- **Curriculum coverage** — extend `skills/math-solving/references/curriculum-map.md` for grades/units that are thin.
- **Misconception catalog** — add real classroom misconceptions to `skills/math-explanation/references/misconceptions.md` (student's reasoning + the correction).
- **Figure recipes** — add geometry figure patterns to `skills/geometry-figures/references/svg-recipes.md`.
- **New skills/agents** — propose via an issue first so we can discuss scope and avoid overlap.

## Project layout

```
.claude-plugin/   marketplace.json + plugin.json (manifests)
agents/           the four agent definitions
skills/           one folder per skill (SKILL.md + scripts/ + references/)
docs/             quickstart and guides
```

## Development setup

1. Clone the repo.
2. `pip install sympy pytest svglib` (SymPy required; pytest for the suite; svglib only to rasterize figures to PNG).
3. Run the regression suite (the real gate — must pass):
   ```bash
   python -m pytest -q tests/      # or, dependency-light: python tests/run_tests.py
   ```
4. Smoke the bundled scripts (illustrative `--demo`s):
   ```bash
   python skills/math-verification/scripts/verify.py --demo
   python skills/geometry-figures/scripts/geo_verify.py --demo
   python skills/geometry-figures/scripts/svg_figure.py --demo /tmp/fig.svg
   python skills/math-solving/scripts/grade_check.py --demo
   ```
5. Load locally: `claude plugin marketplace add ./` then `claude plugin install math-harness@math-harness-marketplace`.

## Conventions

- **Skill descriptions are the only trigger mechanism** — make them specific and "pushy," and include follow-up phrasing ("다시/수정/보완"). State near-miss boundaries so the wrong skill doesn't fire.
- **Explain the *why* in skill bodies**, not just rules — the model generalizes better from reasons. Keep each `SKILL.md` under ~500 lines; push depth into `references/`.
- **Correctness first.** Any claim a solution makes must be reproducible by `math-verifier` in SymPy. If you add math content, add or update a verification path.
- **Grade appropriateness.** Don't introduce tools above the stated grade band without flagging them.
- Scripts use only the standard library + `sympy` (and `svglib` for optional PNG export). SVG generation itself must stay dependency-free.

## Pull requests

- One focused change per PR. Describe the motivation and include a sample prompt + before/after.
- For solution/figure changes, paste the `--demo` output or a verification snippet showing it passes.
- Be kind. This project is used by teachers and students.
