---
name: math-verification
description: "수학 풀이를 Python+SymPy로 독립 검산하는 규약. 최종답·중간단계·정의역·단위를 재계산해 대조하고, 답이 맞아도 과정이 틀리면 잡아낸다. math-verifier 에이전트가 풀이를 검증할 때, 'R 코드 검증'이 아닌 '수학 풀이 검산/계산 확인/이 답 맞는지 확인' 요청 시 사용. 번들 scripts/verify.py 헬퍼 제공."
---

# Math Verification — SymPy 검산 규약

검산의 핵심은 **독립 재유도**다. solver의 식을 그대로 sympy에 넣어 "맞다"를 확인하는 것은 자기충족이다. 문제 조건만 받아 처음부터 다시 계산한 뒤 solver의 단계·답과 대조하라.

## 검산 절차
1. **문제를 sympy로 모델링** — 미지수를 `symbols`로 선언(정의역 가정 포함: `positive=True` 등), 방정식·함수·도형을 sympy 객체로 세운다.
2. **독립 계산** — `solve`, `simplify`, `diff`, `integrate`, `limit`, `Eq` 등으로 답을 직접 구한다.
3. **최종답 대조** — 내 값과 solver 답이 기호적으로 같은지: `simplify(mine - theirs) == 0` (등식) 또는 집합 비교(해집합).
4. **단계 점검** — solver의 각 변형을 `simplify(lhs - rhs) == 0`로 항등 확인. 한 단계라도 거짓이면 그 단계가 오류(답이 우연히 맞아도 FAIL).
5. **정의역·외래근** — `solve` 결과 중 분모 0·진수≤0·범위 밖 해가 버려졌는지 확인.
6. **단위·차원** — 실생활/도형 문제는 단위 일관성과 최종 단위를 확인.

## scripts/verify.py 사용
반복 패턴(등가 확인, 방정식 해 대조, 수치 표본 검증, 단계 항등 체크)을 헬퍼로 번들했다. 직접 sympy를 써도 되지만, 헬퍼가 출력 형식을 통일해 리포트 작성이 쉽다.

```bash
python skills/math-verification/scripts/verify.py --help
```
주요 함수(임포트해서 써도 됨):
- `assert_equal(expr_a, expr_b)` — 두 식이 기호적으로 같은가 (PASS/FAIL + 차이).
- `check_solutions(equation, var, claimed)` — 방정식의 실제 해집합 vs 주장 해집합.
- `sample_identity(expr_a, expr_b, var, samples)` — 무작위/지정 표본 대입으로 항등식 점검.
- `check_steps(steps)` — `[(lhs, rhs), ...]` 단계별 항등 일괄 점검.

## 판정 기준
- **PASS:** 최종답 일치 + 모든 단계 항등 + 정의역/단위 정상.
- **WARN:** 답·단계는 맞으나 학년 범위 초과, 표기 부정확, 정의역 명시 누락 등 비치명적.
- **FAIL:** 최종답 불일치, 또는 답은 맞아도 단계에 거짓 변형, 또는 정의역 위반(외래근 포함/유효근 누락).

## 출력 (리포트)
```
## 검증 항목: [이름]
- 상태: PASS | FAIL | WARN
- 독립 계산: [sympy로 얻은 값/스니펫]
- solver 값: [대조 대상]
- 발견: [불일치 위치·내용]
- 수정 방법: [FAIL/WARN 시]
---
## 종합 판정: PASS | FAIL  (검산 시도 N회)
```
실행한 스니펫·출력은 `_workspace/<id>_verify/`에 남겨 감사 추적을 만든다.

## 폴백
- Python/sympy 미설치 → "환경 setup 필요" 보고 + 손계산 독립 재유도로 가능한 검증 수행(풀이 FAIL로 처리하지 않음).
- 검산이 너무 복잡해 sympy로 안 떨어지면, 수치 표본 검증(`sample_identity`)으로 강한 반증/지지를 만든다.
- 도형 문제의 좌표 검산은 `geometry-figures` 스킬의 `scripts/geo_verify.py`(sympy.geometry)를 쓴다.
