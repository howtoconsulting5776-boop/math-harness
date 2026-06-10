---
name: geometry-figures
description: "도형(기하) 문제를 그리고·출제하고·푸는 규약. 의존성 없는 SVG로 삼각형·원·다각형·좌표평면·함수그래프를 정확히 작도하고, sympy.geometry로 길이·각·넓이·평행/수직·합동/닮음을 계산·검산한다. math-geometer 에이전트가 '도형 그려줘', '이 도형 문제 풀어줘', '삼각형 작도', '기하 문제 출제', '그림으로 보여줘' 요청 시 사용. 번들 scripts/svg_figure.py·geo_verify.py 제공."
---

# Geometry Figures — 도형 작도·출제·풀이 규약

도형 문제의 핵심은 **그림과 계산이 일치하는 것**이다. 같은 좌표(정점)에서 그리고 또 계산하면, 그림의 길이·각이 답과 자동으로 맞는다. 그래서 이 스킬은 좌표를 한 번 정하고, `svg_figure.py`로 그리고 `geo_verify.py`로 계산한다 — 둘은 같은 좌표를 공유한다.

## 작업 순서 (그리기·풀기 공통)
1. **좌표 배치:** 도형을 좌표평면에 앉힌다. 한 변을 x축에, 한 꼭짓점을 원점에 두면 계산이 깔끔하다. 직각은 축에 맞춘다.
2. **정점 확정:** 주어진 조건(길이·각·평행 등)으로 모든 꼭짓점 좌표를 정한다. 미지 좌표는 sympy `symbols` + 조건식 `solve`로 구한다 — 눈대중으로 좌표를 찍지 않는다(정확성).
3. **계산:** `geo_verify.py`로 길이·각·넓이·교점 등 필요한 값을 구한다.
4. **작도:** `svg_figure.py`에 같은 정점을 넘겨 그린다. 각 표시·직각 표시·등변 눈금·라벨을 더한다.
5. **검산 연계:** 좌표 계산 결과를 math-verifier에 넘겨 독립 재계산을 받는다.

## 그리기 — svg_figure.py
순수 표준 라이브러리(외부 패키지 불필요). 수학 좌표(y 위로 증가)로 입력하면 내부에서 SVG로 변환한다.
```python
import sys; sys.path.insert(0, "skills/geometry-figures/scripts")
from svg_figure import Figure
fig = Figure(width=420, height=420, view=(-1, 6, -1, 6))   # xmin,xmax,ymin,ymax
fig.grid(); fig.axes()
fig.polygon([(0,0),(4,0),(0,3)], label_vertices=["A","B","C"])
fig.right_angle((0,0),(4,0),(0,3))     # A의 직각 기호
fig.tick((0,0),(0,3), n=1)             # 등변 눈금(같은 n=같은 길이)
fig.seg_label((0,0),(4,0),"4")         # 변 길이 라벨
fig.angle_arc((4,0),(0,0),(0,3), text="θ")
fig.save("_workspace/fig.svg")
```
주요 메서드: `grid/axes/segment/polygon/circle/point/label/seg_label/right_angle/angle_arc/tick/func`. 함수 그래프는 `fig.func(lambda x: x**2)`.

> 도형 유형별 작도 레시피(이등변·정다각형·원과 접선·좌표기하·함수)는 `references/svg-recipes.md` 참조.

## 계산·검산 — geo_verify.py
sympy.geometry 기반. 같은 정점으로 정확한(기호) 값을 얻는다.
```python
from geo_verify import length, angle_deg, triangle_area, are_similar, intersection
length((0,0),(4,0))                 # 4
triangle_area((0,0),(4,0),(0,3))    # 6
angle_deg((0,0),(4,0),(0,3))        # 꼭짓점 (4,0)에서의 각(도)
are_similar(((0,0),(4,0),(0,3)), ((0,0),(8,0),(0,6)))  # (True, 1/2) → 넓이비=닮음비²
```
주요 함수: `length/midpoint/triangle_area/polygon_area/angle_deg/is_right_angle/are_parallel/are_perpendicular/intersection/line_circle_intersection/triangle_sides/are_similar/are_congruent`.

## 풀기 — 두 갈래 풀이
1. **합성(순수 기하) 풀이** — 학생이 배우는 방법: 보조선, 합동·닮음, 피타고라스, 원주각·접선 성질 등. **이것이 교육의 본체.**
2. **좌표 풀이** — `geo_verify.py`로 같은 답을 좌표로 재계산. **검산·확인용.**
둘의 답이 다르면 멈추고 어디가 틀렸는지 찾는다. 학생에게는 합성 풀이를 주(主)로, 좌표는 "이렇게도 확인할 수 있어요"로.

## 만들기 (출제)
- 사양(학년·단원·개념·난이도)을 받아 새 도형 문제를 만든다: **답을 먼저 sympy로 고정** → 그 답이 나오는 깔끔한 수치를 역설계 → 문제문 + 그림 + 정답 + 풀이.
- 정수 답이 나오게: 피타고라스 정수쌍(3-4-5, 5-12-13, 8-15-17), 정수 넓이·각도(30/45/60/90).
- 변형 세트는 각 변형의 답을 `geo_verify.py`로 재계산해 보장한다.

## 학년 적합성
| 학교급 | 도형 도구 |
|---|---|
| 초등 | 격자·모눈, 각도기·자 직관, 넓이=칸 세기, 대칭·쌓기나무. 좌표·삼각비 금지 |
| 중등 | 합동·닮음(닮음비/넓이비/부피비), 피타고라스, 원의 성질, 작도(컴퍼스·자) |
| 고등 | 좌표기하(도형의 방정식), 삼각비·삼각함수, 벡터, 이차곡선 |

초등 도형은 좌표 라벨 없이 격자·치수 위주로 그린다(`axes` 생략, `grid`만).

## 출력 형식
```
## 문제 (출제 시)
[문제문]  + 그림: _workspace/<id>_figure.svg
## 좌표 배치
A(0,0) B(4,0) C(0,3) ...  (배치 근거)
## 풀이
[합성 풀이: 보조선·성질] / [좌표 풀이: 검산]
## 측정값
길이/각/넓이 ...
## 정답
```

## 폴백
- matplotlib 미설치라도 SVG는 의존성이 없어 항상 가능 → SVG로 그린다. png가 꼭 필요할 때만 setup 블로커 보고.
- 불가능한 도형(삼각부등식 위반, 모순 조건)은 그리기 전에 보고하고 확인 요청.
