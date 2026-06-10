# Quality Gates

This project is useful only when math output is reproducible, grade-appropriate, and
clear enough for a teacher or student to audit. These gates define the minimum checks to
run before changing skills, agents, or helper scripts.

## Baseline smoke tests

Run from the repository root:

```bash
python skills/math-verification/scripts/verify.py --demo
python skills/geometry-figures/scripts/geo_verify.py --demo
python skills/geometry-figures/scripts/svg_figure.py --demo fig_new.svg
python skills/problem-bank/scripts/bank.py --demo
```

Expected coverage:

- `verify.py` checks symbolic equivalence, equation solution sets, sampled identities,
  and step-by-step equality.
- `geo_verify.py` checks coordinate geometry measurements and similarity/congruence
  helpers through a 3-4-5 triangle demo.
- `svg_figure.py` confirms the dependency-free SVG builder can write a usable figure.
- `bank.py` confirms structured note creation, duplicate detection, and index rebuild.

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
  prompts.

## Known gaps

- The smoke tests are demos, not a full regression suite.
- OCR/photo interpretation is not tested in CI.
- Grade appropriateness still depends on the curriculum reference and the model following
  it.
- `svglib` is optional, so PNG export should degrade gracefully to SVG-only output.

