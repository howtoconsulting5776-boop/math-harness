<div align="center">

# math-harness

**An agent-team harness for K-12 math education in Claude Code.**

Turn a math problem — typed or photographed — into a grade-appropriate, step-by-step solution that is **independently verified with SymPy**, **explained at the student's level**, and (for geometry) **drawn, authored, and solved** as precise SVG / coordinate figures.

[한국어 README](./README_KO.md) · [Quickstart](./docs/quickstart.md) · [Contributing](./CONTRIBUTING.md)

</div>

---

## Status

`math-harness` is currently a Claude Code plugin package, not a standalone web app. The
GitHub page is the product surface: it should make the plugin's promise, install path,
and quality checks obvious in under a minute.

**Current improvement focus**

- Make the first screen explain the generate → verify → explain loop without requiring prior agent-team knowledge.
- Keep every bundled helper smoke-testable from a clean Python environment.
- Document what "verified" means so teachers can trust the output without over-trusting the model.
- Make future work visible through a short roadmap instead of leaving improvement ideas in issue threads.

## Why

LLMs are fluent at math prose but quietly make arithmetic and algebra slips, and they tend to explain *at* a student rather than *for* one. `math-harness` fixes both with a **generate → verify → explain** team:

- **Correctness is enforced, not hoped for.** Every solution is re-derived independently in Python + SymPy. A right answer reached by a wrong step still fails.
- **Grade-appropriate by design.** Solutions are restricted to the tools a given grade has actually learned (Korea's 2022 revised curriculum), so a 4th grader never gets an equation with `x`.
- **Geometry is first-class.** A dedicated agent draws figures as dependency-free SVG and solves them on coordinates with `sympy.geometry`, so the picture and the answer always agree.

## The team

| Agent | Role | Backed by |
|------|------|-----------|
| `math-solver` | Step-by-step solution, concept explanation | `math-solving` skill |
| `math-verifier` | Independent SymPy re-derivation (QA) | `math-verification` skill |
| `math-explainer` | Level-appropriate explanation, misconception diagnosis | `math-explanation` skill |
| `math-geometer` | Draw / author / solve geometry figures | `geometry-figures` skill |

Orchestrated by the **`math-tutor`** skill (hybrid: an agent **team** for single problems / concepts / error analysis / geometry, and **fan-out** sub-agents for whole worksheets).

```
solver (solution) ──► verifier (independent re-derivation)
                          ├─ PASS ─► explainer (student-level explanation) ─► done
                          └─ FAIL ─► back to solver with the exact broken step (≤2 retries)
```

## What it does

- **Solve** a single problem (text or photo) with grade-checked, step-by-step reasoning.
- **Explain** any concept at elementary / middle / high-school level, with analogies and scaffolding questions.
- **Diagnose wrong answers** — name the misconception, empathize with the student's reasoning, and prescribe a fix.
- **Geometry** — draw a figure (PNG handout + SVG source), author a new problem around a target concept, or solve a figure two ways (synthetic for teaching, coordinates for verification).
- **Worksheets** — solve and grade a whole problem set in parallel, then compile a solution sheet.
- **Problem bank** — accumulate solved problems and wrong-answer notes as structured, searchable Markdown (filed by grade/unit, deduplicated, Obsidian/Dataview-ready).
- **Academy-aware** — tailor grade/tool restrictions to your academy's actual progress and style via `academy-profile.md`.

## Install

```bash
claude plugin marketplace add howtoconsulting5776-boop/math-harness
claude plugin install math-harness@math-harness-marketplace
export CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1   # team mode
```

**Requirements:** Claude Code v2.x+, Python 3 with `sympy` (required) and `svglib` (optional — only to rasterize figures to PNG handouts). SVG figures need no extra packages.

```bash
pip install sympy svglib
```

See [docs/quickstart.md](./docs/quickstart.md) for a 5-minute walkthrough.

## Quality gates

The real gate is a regression suite that asserts the verifier **rejects wrong answers**
(extraneous roots, broken steps, false identities) and that the geometry and grade-level
checks behave — so "no wrong solution reaches a student" is enforced by code, not hope:

```bash
python -m pytest -q tests/      # or, with no extra deps: python tests/run_tests.py
```

The bundled tools also each ship a `--demo`:

```bash
python skills/math-verification/scripts/verify.py --demo
python skills/geometry-figures/scripts/geo_verify.py --demo
python skills/geometry-figures/scripts/svg_figure.py --demo fig.svg
python skills/problem-bank/scripts/bank.py --demo
python skills/math-solving/scripts/grade_check.py --demo   # grade-appropriateness linter
```

See [Quality Gates](./docs/quality-gates.md) for what each check proves and what it does
not prove. CI runs the suite on every push ([smoke workflow](./.github/workflows/smoke.yml)).

## Use

Just ask, in English or Korean:

```bash
claude "이 사진 속 중2 일차함수 문제 풀어줘"            # solve from a photo
claude "왜 음수로 나누면 부등호가 뒤집혀? 중1 수준으로"   # explain a concept
claude "우리 애가 -2x<6 을 x<-3 이라고 했어"            # diagnose a wrong answer
claude "직각삼각형 빗변 구하는 문제 그려서 풀어줘"        # draw + solve geometry
claude "이 학습지 10문제 풀이랑 채점해줘"               # whole worksheet
```

## Bundled tools

- `skills/math-verification/scripts/verify.py` — SymPy verification helpers (`assert_equal` with PASS/FAIL/UNDECIDED, `check_solutions`, `check_inequality`, `check_equation_steps` — catches extraneous/lost roots, `sample_identity`, `check_steps`). Run `python … verify.py --demo`.
- `skills/geometry-figures/scripts/svg_figure.py` — dependency-free SVG figure builder (triangles, circles, polygons, coordinate planes, function graphs, angle/right-angle/equal-side marks); exports student-ready PNG via `svglib` (`save_both`).
- `skills/geometry-figures/scripts/geo_verify.py` — `sympy.geometry` figure solver (length, angle, area, parallel/perpendicular, similarity/congruence).
- `skills/problem-bank/scripts/bank.py` — save solved problems as frontmattered notes (filed by grade/unit, deduplicated) and rebuild a Dataview-friendly `INDEX.md`.
- `skills/math-solving/scripts/grade_check.py` — grade-appropriateness linter; flags above-grade notation in a solution/explanation for a given grade.

## Roadmap

Near-term development is tracked in [ROADMAP.md](./ROADMAP.md). The priorities are
teacher-facing trust signals, richer Korean curriculum coverage, stronger geometry QA,
and small reproducible demos that make regressions easy to catch.

## License

[Apache-2.0](./LICENSE).
