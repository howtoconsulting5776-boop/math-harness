#!/usr/bin/env python3
"""geometry-figures 헬퍼 — sympy.geometry 기반 도형 검산기.

좌표평면에 도형을 배치하고 길이·각·넓이·교점·평행/수직·합동/닮음을
정확히(기호) 계산한다. svg_figure.Figure에 넘긴 것과 같은 정점을 쓰면
그림과 계산이 자동 일치한다.

사용:
    from geo_verify import length, angle_deg, triangle_area, are_similar
    length((0,0),(4,0))            # 4
    triangle_area((0,0),(4,0),(0,3))  # 6
    angle_deg((4,0),(0,0),(0,3))   # 꼭짓점 (0,0)에서의 각

CLI 데모:
    python geo_verify.py --demo
"""
from __future__ import annotations

import argparse
import sys

import sympy as sp
from sympy import Point, Segment, Line, Circle, Triangle, Polygon, Rational, pi, deg

# Windows 콘솔(cp949)에서도 한글·기호(≈ 등)를 안전하게 출력
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def P(pt):
    return Point(*[sp.nsimplify(c) if not isinstance(c, sp.Expr) else c for c in pt])


def length(a, b):
    """선분 길이(기호)."""
    return Point(*a).distance(Point(*b))


def midpoint(a, b):
    return Point(*a).midpoint(Point(*b))


def triangle_area(a, b, c):
    """삼각형 넓이(기호, 양수)."""
    return sp.Abs(Triangle(Point(*a), Point(*b), Point(*c)).area)


def polygon_area(pts):
    return sp.Abs(Polygon(*[Point(*p) for p in pts]).area)


def angle_deg(p1, vertex, p2):
    """vertex에서 p1, p2가 이루는 각(도, 기호)."""
    v = Point(*vertex)
    a = Point(*p1) - v
    b = Point(*p2) - v
    cos_t = a.dot(b) / (sp.sqrt(a.dot(a)) * sp.sqrt(b.dot(b)))
    return deg(sp.acos(sp.simplify(cos_t)))


def is_right_angle(p1, vertex, p2):
    v = Point(*vertex)
    a = Point(*p1) - v
    b = Point(*p2) - v
    return sp.simplify(a.dot(b)) == 0


def are_parallel(a, b, c, d):
    """선분 ab와 cd가 평행한가."""
    return Line(Point(*a), Point(*b)).is_parallel(Line(Point(*c), Point(*d)))


def are_perpendicular(a, b, c, d):
    return Line(Point(*a), Point(*b)).is_perpendicular(Line(Point(*c), Point(*d)))


def intersection(a, b, c, d):
    """직선 ab와 cd의 교점."""
    return Line(Point(*a), Point(*b)).intersection(Line(Point(*c), Point(*d)))


def line_circle_intersection(a, b, center, r):
    return Line(Point(*a), Point(*b)).intersection(Circle(Point(*center), r))


def triangle_sides(a, b, c):
    """세 변 길이 (a대변, b대변, c대변) = (BC, CA, AB)."""
    A, B, C = Point(*a), Point(*b), Point(*c)
    return B.distance(C), C.distance(A), A.distance(B)


def are_similar(t1, t2):
    """두 삼각형(각각 3점 튜플)이 닮음인지 + 닮음비.

    반환: (bool, ratio 또는 None). 변 길이를 정렬해 비율 일치로 판정.
    """
    s1 = sorted(triangle_sides(*t1), key=lambda e: float(e))
    s2 = sorted(triangle_sides(*t2), key=lambda e: float(e))
    ratios = [sp.simplify(x / y) for x, y in zip(s1, s2)]
    same = all(sp.simplify(ratios[0] - r) == 0 for r in ratios)
    return same, (sp.nsimplify(ratios[0]) if same else None)


def are_congruent(t1, t2):
    ok, ratio = are_similar(t1, t2)
    return ok and sp.simplify(ratio - 1) == 0


def pretty(x):
    """기호 결과를 보기 좋게."""
    s = sp.nsimplify(x) if x.free_symbols == set() else x
    return f"{s}  (≈ {float(x):.4f})" if x.free_symbols == set() else str(s)


def _demo():
    print("=== geo_verify.py 데모 (3-4-5 직각삼각형) ===")
    A, B, C = (0, 0), (4, 0), (0, 3)
    print("AB =", length(A, B), "| AC =", length(A, C), "| BC =", length(B, C))
    print("넓이 =", triangle_area(A, B, C))
    print("∠A 직각? ", is_right_angle(B, A, C))
    print("∠B =", pretty(angle_deg(A, B, C)))
    print("AB ⟂ AC? ", are_perpendicular(A, B, A, C))
    # 닮음: 2배 확대
    ok, ratio = are_similar((A, B, C), ((0, 0), (8, 0), (0, 6)))
    print("닮음? ", ok, " 닮음비 =", ratio, "→ 넓이비 =", ratio**2 if ratio else None)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="sympy.geometry 도형 검산기")
    ap.add_argument("--demo", action="store_true")
    args = ap.parse_args()
    if args.demo:
        _demo()
    else:
        ap.print_help()
