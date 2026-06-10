"""검산 안전망 자체를 검증한다 — 헬퍼가 '옳은 건 통과, 틀린 건 거부'하는가.

이 테스트가 통과해야 '틀린 풀이가 나오면 안 된다'는 약속을 코드로 보장할 수
있다. 헬퍼가 오답을 못 잡으면(거짓 PASS) 여기서 빨간불이 나야 한다.
"""
from verify import assert_equal, check_solutions, sample_identity, check_steps


# --- 옳은 것은 PASS ---
def test_assert_equal_accepts_true_identity():
    ok, _ = assert_equal("(x+1)**2", "x**2 + 2*x + 1")
    assert ok is True


def test_check_solutions_accepts_correct_set():
    ok, _ = check_solutions("x**2 - 5*x + 6", "x", ["2", "3"])
    assert ok is True


def test_sample_identity_accepts_pythagorean():
    ok, _ = sample_identity("sin(x)**2 + cos(x)**2", "1", "x")
    assert ok is True


def test_check_steps_accepts_valid_chain():
    ok, _ = check_steps([("2*x + 4", "2*(x+2)"), ("2*(x+2)", "2*x + 4")])
    assert ok is True


# --- 틀린 것은 반드시 FAIL (안전망의 핵심) ---
def test_assert_equal_rejects_false_identity():
    ok, _ = assert_equal("(x+1)**2", "x**2 + 1")
    assert ok is False


def test_check_solutions_rejects_extraneous_root():
    # 5는 가짜 해 — 잡아야 한다
    ok, _ = check_solutions("x**2 - 5*x + 6", "x", ["2", "3", "5"])
    assert ok is False


def test_check_solutions_rejects_missing_root():
    # x^2-4=0 의 해는 ±2 — -2를 빠뜨리면 FAIL
    ok, _ = check_solutions("x**2 - 4", "x", ["2"])
    assert ok is False


def test_check_steps_rejects_broken_step():
    # 둘째 단계가 거짓(부호 오류) — 최종이 우연히 맞아도 FAIL
    ok, _ = check_steps([("2*x + 4", "2*(x+2)"), ("2*(x+2)", "2*x - 4")])
    assert ok is False


def test_sample_identity_rejects_nonidentity():
    ok, _ = sample_identity("x**2", "x", "x")
    assert ok is False


# --- 실제 문제 회귀 픽스처 (헬퍼가 옳은 답에 옳은 판정을 주는가) ---
def test_fixture_linear_equation():
    # 3(x-2) = x + 4  → x = 5
    ok, _ = check_solutions("3*(x-2) - (x+4)", "x", ["5"])
    assert ok is True


def test_fixture_factorization_identity():
    ok, _ = assert_equal("x**2 - 9", "(x-3)*(x+3)")
    assert ok is True


def test_fixture_system_substitution():
    # x+y=10, x-y=2 → x=6, y=4 : 두 식에 대입해 항등 확인
    ok1, _ = assert_equal("6 + 4", "10")
    ok2, _ = assert_equal("6 - 4", "2")
    assert ok1 and ok2
