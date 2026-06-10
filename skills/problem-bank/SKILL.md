---
name: problem-bank
description: "푼 수학 문제를 구조화 마크다운 노트로 누적 저장해 문제은행·오답노트를 만드는 규약. 학년·단원·개념·난이도·검증상태·정답을 YAML 프런트매터로 달아 Obsidian/Dataview로 검색·복습할 수 있게 하고, 학년>단원 인덱스를 자동 생성한다. math-tutor가 '저장해줘', '문제은행에 넣어', '오답노트 만들어', '노트로 정리', '누적', '복습자료' 요청 시 사용. 번들 scripts/bank.py·assets/problem-note-template.md 제공."
---

# Problem Bank — 문제은행·오답노트 누적 저장 규약

푼 문제를 한 번 쓰고 버리지 않는다. **구조화 노트로 쌓으면** 학원의 문제은행·오답노트·복습자료가 되고, 학년·단원·개념·난이도로 다시 찾을 수 있다. 핵심은 **검증된 풀이만 저장**(verified 플래그)하고, **중복을 막는 것**(같은 문제는 한 번만)이다.

## 언제 저장하나
- 사용자가 명시적으로 "저장/문제은행/오답노트/노트로 정리/누적/복습자료"를 요청할 때.
- math-tutor가 저장 모드로 동작할 때(풀이→검산 PASS→설명 완료 후).
- 저장은 **선택**이다. 단순 1회 풀이 요청이면 대화 답변만 하고 저장하지 않는다(불필요한 누적 방지).

## 무엇을 저장하나 — 프런트매터 스키마
`assets/problem-note-template.md` 양식을 따른다. 필수/권장 필드:
| 필드 | 의미 | 예 |
|---|---|---|
| `title` | 노트 제목 | 일차방정식 3(x-2)=x+4 |
| `grade` | 학년 | 중2 |
| `unit` | 교육과정 단원 | 일차방정식 |
| `concept` | 핵심 개념(리스트) | [이항, 일차방정식] |
| `difficulty` | 난이도 | 하 / 중 / 상 |
| `type` | 노트 유형 | 풀이 / 오답노트 / 개념 / 출제 |
| `answer` | 정답 | x=5 |
| `verified` | math-verifier PASS 여부 | true / false |
| `tags` | 태그(리스트) | [수학, 중2, 일차함수] |
| `source` | 출처(교재·시험·사진) | 학원 7월 모의 12번 |
| `created` | 작성일 | 2026-06-10 |
| `problem_hash` | 중복 판별 해시(자동) | (bank.py가 채움) |

본문 섹션: `문제 / (그림) / 풀이 / 눈높이 설명 / (오답 분석) / 핵심 개념 / 추가 연습`.

## 저장·인덱스 — scripts/bank.py
표준 라이브러리만 사용. 노트 작성과 인덱스 생성을 한다.
```python
import sys; sys.path.insert(0, "skills/problem-bank/scripts")
from bank import save_note, rebuild_index
path, created = save_note(
    "problem-bank",                       # 은행 루트(사용자 지정 경로 우선)
    meta={"title":"...", "grade":"중2", "unit":"일차방정식",
          "concept":["이항"], "difficulty":"중", "type":"풀이",
          "answer":"x=5", "verified":True, "tags":["수학","중2"],
          "source":"...", "created":"2026-06-10"},
    problem="3(x-2)=x+4 를 풀어라.",
    sections={"풀이":"...", "눈높이 설명":"...", "오답 분석":"...", "핵심 개념":"..."},
    figure="../_figure.png")              # 도형이면 상대경로
rebuild_index("problem-bank")             # INDEX.md 재생성
```
- 경로: `<bank>/<학년>/<단원>/<제목>-<해시>.md` 로 자동 분류 저장.
- **중복 방지:** 같은 문제(공백 무시 해시)가 이미 있으면 새로 쓰지 않고 기존 경로를 돌려준다(`created=False`). 재저장이 필요하면 `overwrite=True`.
- **인덱스:** `rebuild_index`가 전체를 스캔해 `INDEX.md`를 학년>단원으로 묶고, Dataview 쿼리 블록도 넣는다.
- `created` 날짜는 `meta`에 직접 넣는다(스크립트는 시계를 읽지 않음 — 오케스트레이터가 오늘 날짜를 전달).

## 저장 위치
- 사용자가 경로를 지정하면 그 경로(예: Obsidian 볼트의 `수학 문제은행/`).
- 없으면 현재 작업 폴더의 `problem-bank/`를 기본으로 쓰고, 위치를 알린다.
- 학원 운영이라면 학년별/반별 볼트 폴더로 모으면 Dataview로 진도·오답 패턴을 한눈에 본다.

## 오답노트 모드
`type: 오답노트`로 저장하고, 본문에 **오답 분석**(학생 사고 → 오개념 → 교정)을 반드시 포함한다(math-explainer 산출 활용). 같은 학생의 반복 오개념은 `tags`에 오개념명을 달아 모이게 한다.

## 품질 규칙
- **verified=false는 "검토 필요"로 표시**하고 저장하되, 인덱스에서 ⬜로 구분된다. 미검증 풀이를 검증된 것처럼 섞지 않는다.
- 정답·풀이는 math-verifier PASS본을 쓴다(틀린 풀이가 문제은행에 박히면 두고두고 해롭다).
- 한 문제 = 한 노트. 변형 문제는 별도 노트(다른 해시)로.
