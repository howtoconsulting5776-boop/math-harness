# SVG 도형 작도 레시피

> math-geometer가 도형 유형별로 참조. 각 레시피는 `svg_figure.Figure`와 `geo_verify`를 함께 쓴다(같은 정점 공유 → 그림·계산 일치). 좌표는 수학 좌표(y 위로 증가).

## 목차
1. 직각삼각형 (피타고라스)
2. 이등변·정삼각형
3. 닮음 두 삼각형
4. 원과 접선·현
5. 좌표기하(점·직선·교점)
6. 함수 그래프
7. 정다각형
8. 초등 격자 도형

---

## 1. 직각삼각형 (피타고라스)
```python
A,B,C=(0,0),(4,0),(0,3)
fig=Figure(view=(-1,6,-1,5)); fig.grid(); fig.axes()
fig.polygon([A,B,C], label_vertices=["A","B","C"])
fig.right_angle(A,B,C); fig.seg_label(A,B,"4"); fig.seg_label(A,C,"3"); fig.seg_label(B,C,"5")
```
검산: `length(B,C)` → 5, `triangle_area(A,B,C)` → 6.

## 2. 이등변·정삼각형
정삼각형 한 변 a: 꼭짓점 (0,0),(a,0),(a/2, a*√3/2).
```python
import sympy as sp
a=4; top=(a/2, float(a*sp.sqrt(3)/2))
fig.polygon([(0,0),(a,0),top], label_vertices=["A","B","C"])
fig.tick((0,0),(a,0),n=1); fig.tick((a,0),top,n=1); fig.tick((0,0),top,n=1)  # 세 변 등변
```
이등변은 등변 두 곳만 `tick(n=1)`, 밑변은 `tick(n=2)`로 구분.

## 3. 닮음 두 삼각형
작은 것과 닮음비 k배 큰 것을 나란히. `are_similar(t1,t2)`로 비율 확인, 넓이비=k².
```python
small=((0,0),(2,0),(0,1.5)); big=((3,0),(7,0),(3,3))   # k=2
fig=Figure(view=(-1,8,-1,4)); fig.grid()
fig.polygon(list(small)); fig.polygon(list(big))
# are_similar(small,big) -> (True, 1/2)  넓이비 -> 1/4
```

## 4. 원과 접선·현
```python
O=(2,2); r=2
fig.circle(O,r); fig.point(O,"O")
# 접선: 접점 T에서 OT ⊥ 접선. line_circle_intersection으로 교점/접점 확인
```
현·중심각·원주각: `angle_deg`로 중심각=2×원주각 검증.

## 5. 좌표기하(점·직선·교점)
```python
fig=Figure(view=(-5,5,-5,5)); fig.grid(); fig.axes()
fig.segment((-4,-1),(4,3)); fig.point((0,1),"P")
# 교점: intersection((-4,-1),(4,3), (0,-3),(0,3))
```

## 6. 함수 그래프
```python
fig=Figure(view=(-4,4,-2,8)); fig.grid(); fig.axes()
fig.func(lambda x: x**2)                 # 이차
fig.func(lambda x: 2*x+1, color="#16a34a")
fig.point((1,1),"(1,1)")
```
교점은 sympy로 `solve(Eq(x**2, 2*x+1))` 후 `fig.point`로 표시.

## 7. 정다각형
중심 O, 반지름 R, n각형 정점: (R cos(2πk/n + φ), R sin(...)).
```python
import math
n,R,O=6,2,(0,0); phi=math.pi/2
pts=[(O[0]+R*math.cos(2*math.pi*k/n+phi), O[1]+R*math.sin(2*math.pi*k/n+phi)) for k in range(n)]
fig.polygon(pts)
```

## 8. 초등 격자 도형 (좌표 라벨 없이)
```python
fig=Figure(view=(0,7,0,5)); fig.grid()       # axes() 생략
fig.polygon([(1,1),(5,1),(5,3),(1,3)])       # 직사각형
fig.seg_label((1,1),(5,1),"4 cm"); fig.seg_label((5,1),(5,3),"2 cm")
# 넓이=칸 세기로 설명, polygon_area로 검산(=8)
```

## 공통 팁
- 미지 정점은 눈대중 금지 → `symbols`+`solve`로 좌표를 구한 뒤 float로 그린다.
- `view`는 도형이 여백 있게 들어오도록 잡는다(잘림 방지).
- 같은 길이=같은 `tick` n, 직각=`right_angle`, 각=`angle_arc(text=...)`로 약속 기호를 일관되게.
- 그림과 `geo_verify` 계산이 어긋나면 좌표가 틀린 것 — 그림을 고치지 말고 좌표를 다시 구한다.
