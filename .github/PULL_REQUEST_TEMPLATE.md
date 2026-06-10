# Pull request

## What & why
<!-- One or two sentences. Link the issue if there is one. -->

## Type
- [ ] Bug fix (wrong solution / verification / figure / trigger)
- [ ] Curriculum or misconception content
- [ ] New figure recipe
- [ ] New skill / agent (discussed in an issue first)
- [ ] Docs

## Verification
<!-- For math/figure changes, paste the relevant proof that it's correct. -->
- [ ] `python -m pytest -q tests/` passes (the gate)
- [ ] For new math/units: added/updated a fixture or assertion in `tests/`
- [ ] Sample prompt + before/after output included below

```
<!-- sample prompt and output -->
```

## Checklist
- [ ] Skill descriptions stay specific + include follow-up phrasing
- [ ] `SKILL.md` bodies under ~500 lines (depth pushed to references/)
- [ ] No tools introduced above the stated grade band (run `grade_check.py` on solution + explanation)
