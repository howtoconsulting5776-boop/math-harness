# Roadmap

The strongest next version of `math-harness` should make teacher trust visible, expand
Korean curriculum coverage, and turn the current demos into repeatable regression checks.

## 1. Trust and verification

- Add small fixture problems for linear equations, inequalities, factorization, functions,
  and right-triangle geometry.
- Convert the current demo scripts into explicit pass/fail smoke tests that CI can run
  without reading console output by hand.
- Add examples of failed verification and solver retry prompts so the team loop is easier
  to inspect.
- Document the difference between symbolic verification, numeric sampling, and pedagogical
  review.

## 2. Korean classroom fit

- Expand `curriculum-map.md` with more semester-level unlocks and examples.
- Add misconception entries from real Korean middle-school topics: sign errors, distributive
  law, inequality direction, function slope, similar triangles, and area/volume units.
- Add teacher-facing response styles: concise answer key, tutoring dialogue, wrong-answer
  note, and parent explanation.

## 3. Geometry reliability

- Add figure recipes for parallel lines, angle chasing, circle theorems, similarity, and
  coordinate-plane function graphs.
- Keep SVG as the source of truth and record the coordinates used by `geo_verify.py` beside
  each generated figure.
- Add visual fixture outputs so layout regressions can be spotted quickly.

## 4. Problem-bank workflow

- Add import/export examples for Obsidian and Dataview users.
- Make duplicate detection explain which existing note was reused.
- Add a lightweight schema document for frontmatter fields.

## 5. Packaging and onboarding

- Keep README, Korean README, and quickstart aligned.
- Add a short "local plugin development" guide after the CI smoke path stabilizes.
- Add release checklist items for version bump, smoke tests, changelog, and marketplace
  manifest review.

