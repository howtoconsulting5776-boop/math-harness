"""도형 검산 헬퍼 회귀 테스트 — 좌표 기하 측정이 정확한가."""
import sympy as sp
from geo_verify import (length, triangle_area, polygon_area, angle_deg,
                        is_right_angle, are_similar, are_congruent,
                        are_perpendicular)

A, B, C = (0, 0), (4, 0), (0, 3)  # 3-4-5 직각삼각형


def test_lengths():
    assert length(A, B) == 4
    assert length(A, C) == 3
    assert length(B, C) == 5


def test_area():
    assert triangle_area(A, B, C) == 6


def test_right_angle_at_A():
    assert is_right_angle(B, A, C) is True
    assert are_perpendicular(A, B, A, C) is True


def test_angle_is_90_degrees():
    assert sp.simplify(angle_deg(B, A, C) - 90) == 0


def test_similar_triangle_ratio_and_area():
    big = ((0, 0), (8, 0), (0, 6))   # 2배 닮음
    same, ratio = are_similar((A, B, C), big)
    assert same is True
    assert sp.simplify(ratio - sp.Rational(1, 2)) == 0
    # 넓이비 = 닮음비^2
    assert sp.simplify(triangle_area(*((A, B, C))) / triangle_area(*big)
                       - ratio**2) == 0


def test_congruent_detection():
    same = are_congruent((A, B, C), ((1, 1), (5, 1), (1, 4)))  # 평행이동
    assert same is True


def test_rectangle_area():
    rect = [(0, 0), (4, 0), (4, 2), (0, 2)]
    assert polygon_area(rect) == 8


def test_not_similar_when_shape_differs():
    same, _ = are_similar((A, B, C), ((0, 0), (5, 0), (0, 5)))  # 직각이등변
    assert same is False
