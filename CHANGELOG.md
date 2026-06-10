# Changelog

All notable changes to **math-harness** are documented here. Format loosely follows
[Keep a Changelog](https://keepachangelog.com/); versions follow [SemVer](https://semver.org/).

## [0.4.0] — 2026-06-10

검산 커버리지의 구멍을 메우고, 교육과정 해금 표를 단일 소스로 만든 안전성 릴리스.

### 검산 (math-verification)
- **신규 `check_inequality`** — 부등식 해집합 직접 대조. 간판 시나리오(-2x<6 부등호 방향 오개념)가 기계 검산 가능해짐.
- **신규 `check_equation_steps`** — 방정식 풀이 체인의 동치 변형 검증. 외래근 도입(양변 제곱)·해 누락(0일 수 있는 식으로 나눔)을 단계 위치·원인까지 보고.
- **vacuous PASS 버그 수정** — `sample_identity`에서 평가된 표본이 0개(전부 예외/NaN/무한대)면 PASS가 아니라 UNDECIDED.
- **삼진 판정** — `assert_equal`이 simplify 실패 시 `equals()` 폴백(거짓 FAIL로 인한 불필요 재풀이 방지), 둘 다 실패하면 UNDECIDED.
- 모든 판정 메시지에 검증 방법 라벨([기호검증]/[해집합]/[수치표본]/[동치변형]) 표기 — `METHODS` 상수 공개.

### 학년 린터 (grade_check)
- **단일 소스화** — 해금 시점을 `references/curriculum-unlocks.json`에서 읽음(curriculum-map.md와 1:1, JSON 부재 시 내장 폴백).
- **학기 정밀 판정** — '중3-1', '중2 2학기' 파싱(`parse_grade_semester`). 학년만 주어지면 수료 기준으로 관대 판정(기존 동작 보존).
- **거짓음성 수정** — 한글 삼각비 표기(코사인·탄젠트·사인), 한글 인접 음수('-3도'), 무공백 'sin30°', 고1의 미적분·로그·삼각함수.
- **오탐 방지** — 로그인/로그아웃/블로그/카탈로그, 3-4-5 하이픈.

### 문제은행 (problem-bank)
- **정규화 해시** — NFKC + 수학기호 이형(−×÷≤≥ 등) 통일 후 해시. 유니코드 마이너스로 적은 같은 문제가 중복으로 잡힘.
- **구조 해시 + `find_similar`** — 숫자를 추상화한 structure_hash로 '숫자만 바꾼 변형' 군집 탐지(조사 변화 포함). 복습 추천·중복 출제 방지용.
- **`verify_method` 프런트매터** — 검증 '수준'(기호검증/해집합/수치표본/동치변형/좌표기하/미검증)을 노트와 INDEX에 기록 — '검증됨'의 의미를 교사가 구분 가능.

### 검산 독립성 (agents/skills)
- verifier에 **2단계 블라인드 프로토콜** 명문화 — solver 풀이를 읽기 전 독립 유도를 `blind.md`로 먼저 기록, 오케스트레이터가 태스크 의존성으로 순서 강제(앵커링의 구조적 차단).

### 도형 (geometry-figures)
- `are_similar` 변 정렬을 배정밀도 float → 50자리 고정밀로 — 무리수 변 길이의 오정렬로 인한 닮음 오판 방지.

### 테스트
- 신규 회귀 21건(`tests/test_patches.py`) — 위 허점들이 되살아나면 빨간불. 총 51건.

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
