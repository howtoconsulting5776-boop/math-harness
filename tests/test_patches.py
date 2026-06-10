"""패치 회귀 테스트 — 부등식 검산, 동치 변형, vacuous PASS 차단, 학기 정밀
학년 린터, 정규화/구조 해시, 고정밀 닮음 정렬이 약속대로 동작하는가.

각 테스트는 실제로 발견됐던 허점(거짓 PASS·거짓음성·오탐)을 고정하는
픽스처다 — 여기가 깨지면 해당 허점이 되살아난 것이다.
"""
import os
import shutil
import tempfile

import sympy as sp

from verify import (assert_equal, sample_identity, check_inequality,
                    check_equation_steps)
from grade_check import check, parse_grade, parse_grade_semester
from bank import save_note, find_similar, _phash, _shash
from geo_verify import are_similar


# ---------------------------------------------------------------- 부등식 검산
def test_inequality_accepts_correct_direction():
    # 간판 시나리오: -2x < 6 의 옳은 답 x > -3
    ok, _ = check_inequality("-2*x < 6", "x", "x > -3")
    assert ok is True


def test_inequality_rejects_flipped_direction():
    # 대표 오개념: 부등호 방향을 안 뒤집은 x < -3 은 반드시 FAIL
    ok, msg = check_inequality("-2*x < 6", "x", "x < -3")
    assert ok is False
    assert "FAIL" in msg


def test_inequality_rejects_boundary_type_error():
    # < 와 <= 혼동(경계 포함 여부)도 잡아야 한다
    ok, _ = check_inequality("2*x < 6", "x", "x <= 3")
    assert ok is False


# ------------------------------------------------------------- 동치 변형 체인
def test_equation_steps_accepts_valid_chain():
    ok, _ = check_equation_steps(["2*x + 4 = 10", "2*x = 6", "x = 3"], "x")
    assert ok is True


def test_equation_steps_rejects_extraneous_root():
    # sqrt(x) = -2 는 해가 없는데 양변 제곱으로 x=4 가 생김 — 외래근
    ok, msgs = check_equation_steps(["sqrt(x) = -2", "x = 4"], "x")
    assert ok is False
    assert any("외래근" in m for m in msgs)


def test_equation_steps_rejects_lost_root():
    # x(x-1)=0 을 양변 x로 나눠 x=1 만 남김 — 해 누락
    ok, msgs = check_equation_steps(["x*(x-1) = 0", "x - 1 = 0"], "x")
    assert ok is False
    assert any("해 누락" in m for m in msgs)


# ------------------------------------------------- vacuous PASS 차단 (철칙 1)
def test_sample_identity_no_vacuous_pass():
    # 평가 가능한 표본이 0개면 PASS가 아니어야 한다 (발견된 실제 버그)
    ok, msg = sample_identity("zoo*x", "nan", "x")
    assert ok is False
    assert "UNDECIDED" in msg


def test_assert_equal_still_passes_true_identity():
    ok, msg = assert_equal("(x+1)**2", "x**2 + 2*x + 1")
    assert ok is True and "기호검증" in msg


# ----------------------------------------------------------- 학년 린터 정밀화
def test_parse_grade_backward_compatible():
    assert parse_grade("초5") == ("elem", 5)
    assert parse_grade("중2") == ("mid", 2)


def test_parse_grade_semester():
    assert parse_grade_semester("중3-1") == ("mid", 3, 1)
    assert parse_grade_semester("중2 2학기") == ("mid", 2, 2)


def test_korean_trig_terms_detected():
    # 발견된 거짓음성: 한글 표기 삼각비
    assert check("중2", "코사인 법칙을 쓰면")
    assert check("중1", "탄젠트 값은")


def test_negative_number_before_hangul_detected():
    # 발견된 거짓음성: '-3도' — 한글 인접 \b 문제
    assert check("초5", "온도가 -3도가 되었어요")


def test_high1_calculus_detected():
    # 발견된 거짓음성: 고1에 미적분 (curriculum-map엔 금지인데 린터가 놓침)
    assert check("고1", "이 함수를 적분하면")
    assert check("고2", "이 함수를 적분하면") == []


def test_semester_precision_trig_ratio():
    # 삼각비는 중3-2학기: 학기 명시 시 정밀, 학년만이면 관대(수료 기준)
    assert check("중3-1", "sin 30° = 1/2")
    assert check("중3", "sin 30° = 1/2") == []


def test_no_false_positive_hyphen_and_login():
    assert check("초4", "변의 길이가 3-4-5 인 삼각형") == []
    assert check("고1", "로그인 후 로그아웃") == []
    assert check("고1", "블로그에 정리했다") == []


def test_nospace_sin_detected():
    # 'sin30°' 무공백도 잡는다 (\b가 숫자 인접에서 깨지는 문제)
    assert check("중2", "sin30° = 1/2")


# --------------------------------------------------------- 문제은행 해시 강화
def test_unicode_minus_same_hash():
    # 발견된 허점: U+2212 마이너스로 적은 같은 문제가 다른 해시
    assert _phash("-2x<6 을 풀어라.") == _phash("−2x<6 을 풀어라.")


def test_structure_hash_clusters_number_variants():
    # 숫자만 바꾼 변형(+조사 변화)은 구조 해시가 같아야 한다
    assert _shash("3(x-2)=x+4 를 풀어라.") == _shash("5(x-1)=x+8 을 풀어라.")
    # 구조가 다르면 달라야 한다
    assert _shash("3(x-2)=x+4 를 풀어라.") != _shash("x**2-4=0 을 풀어라.")


def test_find_similar_returns_variant_not_duplicate():
    bank = tempfile.mkdtemp(prefix="bank_test_")
    try:
        save_note(bank, {"title": "원본", "grade": "중2", "unit": "일차방정식",
                         "verified": True, "verify_method": "해집합"},
                  problem="3(x-2)=x+4 를 풀어라.", sections={"풀이": "x=5"})
        sim = find_similar(bank, "7(x-3)=x+9 를 풀어라.")   # 변형 → 잡혀야
        assert [s["title"] for s in sim] == ["원본"]
        same = find_similar(bank, "3(x-2)=x+4 를 풀어라.")  # 정확 중복 → 제외
        assert same == []
    finally:
        shutil.rmtree(bank, ignore_errors=True)


def test_verify_method_in_frontmatter():
    bank = tempfile.mkdtemp(prefix="bank_test_")
    try:
        p, _ = save_note(bank, {"title": "t", "grade": "중2", "unit": "u",
                                "verified": True, "verify_method": "해집합"},
                         problem="q", sections={"풀이": "s"})
        text = open(p, encoding="utf-8").read()
        assert "verify_method: 해집합" in text
        assert "structure_hash:" in text
    finally:
        shutil.rmtree(bank, ignore_errors=True)


# ------------------------------------------------------- 닮음 고정밀 정렬
def test_similar_with_irrational_sides():
    # 1:1:√2 직각이등변 — 무리수 변 길이에서도 닮음비가 정확해야 한다
    same, ratio = are_similar(((0, 0), (1, 0), (0, 1)),
                              ((0, 0), (3, 0), (0, 3)))
    assert same is True
    assert sp.simplify(ratio - sp.Rational(1, 3)) == 0
