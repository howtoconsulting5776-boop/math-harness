"""학년 린터 회귀 테스트 — 학년 초과 도구를 잡고, 적합한 건 통과시키는가."""
from grade_check import check, parse_grade


def test_parse_grade():
    assert parse_grade("초5") == ("elem", 5)
    assert parse_grade("중2") == ("mid", 2)
    assert parse_grade("고1") == ("high", 1)
    assert parse_grade("") == (None, None)


# --- 학년 초과는 잡는다 ---
def test_elem_flags_variable_equation():
    assert check("초5", "x = 3 이므로 답은 3")


def test_elem_flags_sqrt():
    assert check("초6", "√2 를 더한다")


def test_mid_low_flags_trig():
    # 삼각비는 중3 — 중2 풀이에 sin 나오면 경고
    assert check("중2", "sin 30° = 1/2")


def test_mid_flags_calculus():
    assert check("중2", "이 식을 적분하면")


# --- 학년 적합은 통과 ---
def test_elem_allows_arithmetic():
    assert check("초5", "정사각형 넓이 = 4 × 4 = 16") == []


def test_mid_allows_linear_function():
    assert check("중2", "y = 2x + 1 의 기울기는 2") == []


def test_mid3_allows_trig_ratio():
    # 삼각비는 중3부터 허용
    assert check("중3", "삼각비 sin 30° = 1/2") == []


def test_high_allows_calculus():
    assert check("고2", "f(x)=x^2 를 미분하면 2x") == []


def test_unknown_grade_skips():
    # 학년 미상이면 점검 보류(빈 결과)
    assert check("", "무엇이든") == []
