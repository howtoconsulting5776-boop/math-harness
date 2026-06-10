# Quickstart — 5 minutes to your first solved problem

**What you'll have at the end:** the `math-harness` plugin installed, the bundled tools smoke-tested, and one math problem solved → verified → explained.

**Prerequisites:**
- Claude Code **v2.x+** (`claude --version`)
- **Python 3** with SymPy: `pip install sympy` (and `svglib` if you want figures rasterized to PNG handouts)
- Network access to `github.com`

---

## Step 1 — Add the marketplace (60s)

```bash
claude plugin marketplace add howtoconsulting5776-boop/math-harness
```

> For purely local use (before pushing to GitHub), you can instead run `claude plugin marketplace add ./` from the repo root.

## Step 2 — Install the plugin + enable teams (40s)

```bash
claude plugin install math-harness@math-harness-marketplace
export CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1
```

*(Append the `export` line to `~/.bashrc` / `~/.zshrc` to persist it. On Windows PowerShell: `$env:CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS = "1"`.)*

The team mode powers the generate → verify → explain loop. Without it, the harness still runs but as a single agent rather than a self-coordinating team.

## Step 3 — Smoke-test the bundled tools (30s)

```bash
python skills/math-verification/scripts/verify.py --demo
python skills/geometry-figures/scripts/geo_verify.py --demo
python skills/geometry-figures/scripts/svg_figure.py --demo fig.svg
```

You should see PASS/FAIL demo lines from the verifier, a 3-4-5 triangle's measurements from the geo solver, and a `fig.svg` written to disk. If `sympy` is missing, `pip install sympy`.

## Step 4 — Solve your first problem (2 min)

```bash
claude "중2 수준으로: x에 대한 일차방정식 3(x-2) = x + 4 를 풀고 단계별로 설명해줘"
```

**What happens:** `math-tutor` detects a single-problem request, spins up the team — `math-solver` produces a step-by-step solution, `math-verifier` re-derives it in SymPy (`check_solutions`), and `math-explainer` rewrites it at a 중2 level with scaffolding questions.

**Try also:**
```bash
claude "직각을 낀 두 변이 6, 8인 직각삼각형을 그리고 빗변을 구해줘"   # geometry: draw + solve
claude "우리 애가 (x+3)^2 을 x^2+9 라고 했어. 뭐가 문제야?"          # error analysis
```

## Step 5 — Photo input (optional)

Hand Claude a photo of a textbook problem (drag the image in, or pass its path). `math-solver` reads the figure and numbers directly; if it's a geometry figure, `math-geometer` redraws it cleanly as SVG before solving.

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| Team doesn't form / only one agent answers | `export CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` in the *current* shell, re-run. |
| "verification skipped — sympy not found" | `pip install sympy`. Verifier falls back to hand re-derivation, but SymPy is strongly recommended. |
| Skill didn't trigger | Be explicit: include "풀어줘 / 설명해줘 / 그려줘 / 채점". Pure facts ("2의 제곱은?") are answered directly without the harness. |
| PNG export fails | `pip install svglib`. Figures fall back to SVG, which needs no extra packages and prints/scales even cleaner. |

Open an issue with your prompt, grade level, and `claude --version` if something this guide didn't cover bites you.
