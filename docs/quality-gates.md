# Quality Gates

This project is useful only when math output is reproducible, grade-appropriate, and
clear enough for a teacher or student to audit. These gates define the minimum checks to
run before changing skills, agents, or helper scripts.

## The gate: regression tests (must pass)

The primary gate is an assertion-based suite that **fails the build** on a regression —
not demos you read by eye. Run from the repository root:

```bash
python -m pytest -q tests/        # or, dependency-light: python tests/run_tests.py
```

It proves the safety net actually works:

- **The verifier rejects wrong answers.** `tests/test_verify.py` asserts that an
  extraneous root, a missing root, a false identity, and a broken intermediate step all
  return FAIL — and that correct work returns PASS. If the verifier ever regressed to
  rubber-stamping, these tests go red.
- **Geometry measurements are exact.** `tests/test_geometry.py` checks lengths, area,
  right angles, similarity ratio → area ratio, congruence, and a non-similar negative case.
- **The grade linter behaves.** `tests/test_grade_check.py` asserts above-grade tools are
  flagged (e.g. `x=`/`√` in an elementary solution, trig before 중3, calculus in middle
  school) and that grade-appropriate work passes.

CI runs this suite on every push and pull request
([smoke workflow](../.github/workflows/smoke.yml)).

## Baseline smoke demos

The bundled tools also each ship an illustrative `--demo` (these *show* behavior; the
tests above are what *gate* it):

```bash
python skills/math-verification/scripts/verify.py --demo
python skills/geometry-figures/scripts/geo_verify.py --demo
python skills/geometry-figures/scripts/svg_figure.py --demo fig.svg
python skills/problem-bank/scripts/bank.py --demo
python skills/math-solving/scripts/grade_check.py --demo
```

> Note: `verify.py --demo` intentionally prints some `FAIL` lines — those are *examples*
> of the verifier correctly catching wrong answers, not test failures. The pass/fail gate
> is the test suite, which asserts those rejections happen.

## What "verified" means

Verified means the answer or transformation was independently reproduced by deterministic
code, usually SymPy. It does not mean every pedagogical explanation is perfect, every OCR
reading is correct, or every diagram inference from a photo is complete.

When a solution is marked verified, the response should still show:

- The expression, equation, or geometry facts used for verification.
- The exact result returned by the verifier.
- Any assumptions made from a photographed or ambiguous problem statement.

## Manual review checklist

Use this checklist for pull requests that change math behavior:

- The solution uses tools available to the requested grade band.
- The final answer and every important intermediate claim can be checked by code or by a
  clearly stated theorem.
- A wrong intermediate step fails even if the final answer happens to be correct.
- Geometry diagrams and coordinate calculations describe the same points, lengths, and
  labels.
- Korean explanations avoid jumping to high-school notation for elementary or middle-school
  prompts — run `grade_check.py` on the solution *and* the explanation.

## Known gaps

- The regression suite covers the verification/geometry/grade helpers, not every possible
  problem; widen `tests/` fixtures as new units are added.
- OCR/photo interpretation is not tested in CI (no image fixtures yet).
- `grade_check.py` is a high-signal heuristic linter, not a perfect grade classifier — it
  can miss subtler above-grade reasoning, so the curriculum reference + model judgment still
  matter. It catches the obvious notation leaks.
- `svglib` is optional, so PNG export degrades gracefully to SVG-only output.

