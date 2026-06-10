#!/usr/bin/env python3
"""math-verification 헬퍼 — SymPy 독립 검산 유틸리티.

수학 풀이를 검산할 때 반복되는 패턴(등가 확인, 방정식 해 대조, 표본 항등
검증, 단계별 항등 점검)을 통일된 PASS/FAIL 출력으로 제공한다.

CLI 데모:
    python verify.py --demo
import 사용:
    from verify import assert_equal, check_solutions, sample_identity, check_steps
"""
from __future__ import annotations

import argparse
import sys

import sympy as sp

# Windows 콘솔(cp949)에서도 한글을 안전하게 출력
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def _parse(expr):
    """문자열이면 sympy로 파싱, 이미 sympy 객체면 그대로."""
    if isinstance(expr, str):
        return sp.sympify(expr)
    return expr


def assert_equal(expr_a, expr_b, *, label="식 등가"):
    """두 식이 기호적으로 동일한지. 반환: (ok, message)."""
    a, b = _parse(expr_a), _parse(expr_b)
    diff = sp.simplify(a - b)
    ok = diff == 0
    msg = f"[{'PASS' if ok else 'FAIL'}] {label}: a-b 간단화 = {diff}"
    return ok, msg


def check_solutions(equation, var, claimed, *, label="해집합"):
    """방정식의 실제 해집합과 주장 해집합을 비교.

    equation: 'x**2 - 5*x + 6' 처럼 =0 형태의 식, 또는 sp.Eq.
    var: 변수 (문자열 가능). claimed: 주장 해 리스트.
    """
    eq = _parse(equation)
    v = sp.Symbol(var) if isinstance(var, str) else var
    actual = set(sp.solve(eq, v))
    claimed_set = {_parse(c) for c in claimed}
    # 기호적 동치 비교
    matched = set()
    for c in claimed_set:
        for a in actual:
            if sp.simplify(a - c) == 0:
                matched.add(a)
                break
    missing = actual - matched           # 빠뜨린 유효근
    extra = {c for c in claimed_set       # 외래근(실제 해 아님)
             if not any(sp.simplify(a - c) == 0 for a in actual)}
    ok = not missing and not extra
    msg = (f"[{'PASS' if ok else 'FAIL'}] {label}: 실제={sorted(actual, key=str)} "
           f"주장={sorted(claimed_set, key=str)}"
           + (f" | 누락(유효근)={sorted(missing, key=str)}" if missing else "")
           + (f" | 외래근={sorted(extra, key=str)}" if extra else ""))
    return ok, msg


def sample_identity(expr_a, expr_b, var, samples=(-2, -1, sp.Rational(1, 2), 1, 3, 7),
                    *, label="표본 항등"):
    """무작위 대신 지정 표본 대입으로 항등식을 점검(기호 간단화가 안 떨어질 때)."""
    a, b = _parse(expr_a), _parse(expr_b)
    v = sp.Symbol(var) if isinstance(var, str) else var
    bad = []
    for s in samples:
        try:
            va = complex(a.subs(v, s).evalf())
            vb = complex(b.subs(v, s).evalf())
        except Exception:
            continue
        if abs(va - vb) > 1e-9:
            bad.append((s, va, vb))
    ok = not bad
    msg = f"[{'PASS' if ok else 'FAIL'}] {label}: 표본 {len(samples)}개" + (
        "" if ok else f" | 불일치 {bad[:3]}")
    return ok, msg


def check_steps(steps, *, label="단계 항등"):
    """풀이 단계의 좌변-우변 항등을 일괄 점검.

    steps: [(lhs, rhs), ...]  각 변형이 항등(같은 값)이어야 한다.
    반환: (all_ok, [메시지...])
    """
    msgs = []
    all_ok = True
    for i, (lhs, rhs) in enumerate(steps, 1):
        ok, m = assert_equal(lhs, rhs, label=f"{label} 단계{i}")
        all_ok = all_ok and ok
        msgs.append(m)
    return all_ok, msgs


def _demo():
    print("=== math-verification verify.py 데모 ===")
    print(assert_equal("(x+1)**2", "x**2 + 2*x + 1")[1])
    print(assert_equal("(x+1)**2", "x**2 + 1")[1])          # FAIL 예시
    print(check_solutions("x**2 - 5*x + 6", "x", ["2", "3"])[1])
    print(check_solutions("x**2 - 5*x + 6", "x", ["2", "3", "5"])[1])  # 외래근
    print(check_solutions("x**2 - 4", "x", ["2"])[1])        # 유효근 누락
    print(sample_identity("sin(x)**2 + cos(x)**2", "1", "x")[1])
    ok, msgs = check_steps([("2*x + 4", "2*(x+2)"), ("2*(x+2)", "2*x + 4")])
    for m in msgs:
        print(m)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="SymPy 검산 헬퍼")
    ap.add_argument("--demo", action="store_true", help="데모 실행")
    args = ap.parse_args()
    if args.demo:
        _demo()
    else:
        ap.print_help()
