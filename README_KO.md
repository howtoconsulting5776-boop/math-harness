<div align="center">

# math-harness

**Claude Code용 초중고 수학 교육 에이전트 팀 하네스.**

타이핑했든 사진을 찍었든, 수학 문제를 받아 **학년 수준에 맞는 단계별 풀이**로 바꾸고, **SymPy로 독립 검산**하고, **학생 눈높이로 설명**하며, 도형은 **정확한 SVG·좌표로 그리고·출제하고·푼다.**

[English README](./README.md) · [빠른 시작](./docs/quickstart.md) · [기여 가이드](./CONTRIBUTING.md)

</div>

---

## 왜 만들었나

LLM은 수학 설명은 유창하지만 계산·대수에서 조용히 실수하고, 학생 *눈높이*보다 자기 수준으로 설명하는 경향이 있다. `math-harness`는 **생성 → 검산 → 설명** 팀으로 둘 다 잡는다.

- **정확성을 바라지 않고 강제한다.** 모든 풀이를 Python+SymPy로 독립 재유도한다. 답이 맞아도 과정이 틀리면 FAIL.
- **설계부터 학년 적합.** 그 학년이 실제로 배운 도구(2022 개정 교육과정)로만 푼다 — 초4에게 미지수 `x` 방정식을 주지 않는다.
- **도형이 일급 시민.** 전용 에이전트가 의존성 없는 SVG로 그림을 그리고 `sympy.geometry`로 좌표 풀이해, **그림과 답이 항상 일치**한다.

## 팀 구성

| 에이전트 | 역할 | 스킬 |
|------|------|-----------|
| `math-solver` | 단계별 풀이, 개념 설명 | `math-solving` |
| `math-verifier` | SymPy 독립 검산(QA) | `math-verification` |
| `math-explainer` | 눈높이 설명, 오개념 진단 | `math-explanation` |
| `math-geometer` | 도형 작도·출제·좌표 풀이 | `geometry-figures` |

오케스트레이터는 **`math-tutor`** 스킬(하이브리드: 단일문제·개념·오답·도형은 에이전트 **팀**, 학습지 전체는 **팬아웃** 서브에이전트).

```
solver(풀이) ──► verifier(독립 재유도)
                   ├─ PASS ─► explainer(눈높이 설명) ─► 완료
                   └─ FAIL ─► 틀린 단계를 짚어 solver에 되돌림 (최대 2회)
```

## 무엇을 하나

- **풀이** — 단일 문제(텍스트/사진)를 학년 도구로 단계별 풀이.
- **개념 설명** — 초/중/고 수준 비유·발문으로 개념 자체를 설명.
- **오답 분석** — 오개념을 짚고, 학생 사고에 공감하며 교정 처방.
- **도형** — 그림 작도, 목표 개념 중심 출제, 두 갈래 풀이(교육용 합성 + 검산용 좌표).
- **학습지** — 문제 세트를 병렬로 풀고 채점해 해설지로 취합.

## 설치

```bash
claude plugin marketplace add howtoconsulting5776-boop/math-harness
claude plugin install math-harness@math-harness-marketplace
export CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1   # 팀 모드
```

**요구사항:** Claude Code v2.x+, Python 3 + `sympy`(필수)·`matplotlib`(선택, PNG 그래프용). SVG 그림은 추가 패키지 불필요.

```bash
pip install sympy matplotlib
```

5분 안내는 [docs/quickstart.md](./docs/quickstart.md).

## 사용

영어든 한국어든 그냥 요청하면 된다:

```bash
claude "이 사진 속 중2 일차함수 문제 풀어줘"
claude "왜 음수로 나누면 부등호가 뒤집혀? 중1 수준으로"
claude "우리 애가 -2x<6 을 x<-3 이라고 했어"
claude "직각삼각형 빗변 구하는 문제 그려서 풀어줘"
claude "이 학습지 10문제 풀이랑 채점해줘"
```

## 번들 도구

- `skills/math-verification/scripts/verify.py` — SymPy 검산 헬퍼(`assert_equal`, `check_solutions`, `sample_identity`, `check_steps`). `python … verify.py --demo`.
- `skills/geometry-figures/scripts/svg_figure.py` — 의존성 없는 SVG 작도기(삼각형·원·다각형·좌표평면·함수그래프·각/직각/등변 표시).
- `skills/geometry-figures/scripts/geo_verify.py` — `sympy.geometry` 도형 풀이(길이·각·넓이·평행/수직·닮음/합동).

## 라이선스

[Apache-2.0](./LICENSE).
