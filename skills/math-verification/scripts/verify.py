#!/usr/bin/env python3
"""math-verification 헬퍼 — SymPy 독립 검산 유틸리티.

수학 풀이를 검산할 때 반복되는 패턴(등가 확인, 방정식 해 대조, 표본 항등
검증, 단계별 항등 점검)을 통일된 PASS/FAIL 출력으로 제공한다.

CLI 데모:
    python verify.py --demo
import 사용:
    from verify import (assert_equal, check_solutions, sample_identity,
                        check_steps, check_inequality, check_equation_steps)
"""
from __future__ import annotations

import argparse
import math
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


# 검증 방법 라벨 — problem-bank의 verify_method 프런트매터와 짝을 이룬다.
METHODS = {
    "symbolic": "기호검증",      # simplify/equals 기반 등가
    "solveset": "해집합",        # 방정식·부등식 해집합 대조
    "sampling": "수치표본",      # 표본 대입 점검
    "equiv": "동치변형",         # 방정식 체인의 해집합 보존
    "geometry": "좌표기하",      # sympy.geometry (geo_verify)
    "unverified": "미검증",
}


def assert_equal(expr_a, expr_b, *, label="식 등가"):
    """두 식이 기호적으로 동일한지. 반환: (ok, message).

    판정은 3단계: ① simplify(a-b)==0 → PASS. ② 안 떨어지면 sympy의
    구조적·수치적 동등성 검사 `Expr.equals()`로 폴백 — True면 PASS(거짓
    FAIL로 인한 불필요한 재풀이 루프 방지), False면 FAIL. ③ equals()가
    None(판정 불능)이면 UNDECIDED — ok=False로 보수적으로 처리하되,
    메시지에 '오류 확정'이 아니라 '판정 불능'임을 명시한다(verifier는
    이 경우 표본 검증 등 다른 방법으로 보강해야 한다).
    """
    a, b = _parse(expr_a), _parse(expr_b)
    diff = sp.simplify(a - b)
    if diff == 0:
        return True, f"[PASS][{METHODS['symbolic']}] {label}: a-b 간단화 = 0"
    # simplify가 못 떨어뜨린 참 항등식 구제 (equals는 수치 검증 포함)
    try:
        eq = a.equals(b)
    except Exception:
        eq = None
    if eq is True:
        return True, (f"[PASS][{METHODS['symbolic']}] {label}: "
                      f"simplify 미해결이나 equals() 폴백으로 등가 확인")
    if eq is False:
        return False, f"[FAIL][{METHODS['symbolic']}] {label}: a-b 간단화 = {diff}"
    return False, (f"[UNDECIDED][{METHODS['symbolic']}] {label}: "
                   f"simplify/equals 모두 판정 불능 (a-b = {diff}) — "
                   f"sample_identity 등으로 보강 검증 필요")


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
    msg = (f"[{'PASS' if ok else 'FAIL'}][{METHODS['solveset']}] {label}: "
           f"실제={sorted(actual, key=str)} "
           f"주장={sorted(claimed_set, key=str)}"
           + (f" | 누락(유효근)={sorted(missing, key=str)}" if missing else "")
           + (f" | 외래근={sorted(extra, key=str)}" if extra else ""))
    return ok, msg


def sample_identity(expr_a, expr_b, var, samples=(-2, -1, sp.Rational(1, 2), 1, 3, 7),
                    *, label="표본 항등"):
    """무작위 대신 지정 표본 대입으로 항등식을 점검(기호 간단화가 안 떨어질 때).

    안전 규칙: 평가에 성공한 표본이 **0개면 PASS가 아니라 UNDECIDED**다.
    (모든 표본이 평가 불가능했는데 '불일치 없음'을 PASS로 해석하면
    공허한 참(vacuous pass)으로 틀린 풀이가 통과할 수 있다.)
    """
    a, b = _parse(expr_a), _parse(expr_b)
    v = sp.Symbol(var) if isinstance(var, str) else var
    bad = []
    evaluated = 0
    for s in samples:
        try:
            va = complex(a.subs(v, s).evalf())
            vb = complex(b.subs(v, s).evalf())
        except Exception:
            continue
        # NaN/무한대는 '평가 성공'이 아니다 — NaN은 모든 비교가 False라
        # 불일치로도 안 잡혀 공허한 PASS를 만든다.
        if not all(math.isfinite(t) for t in
                   (va.real, va.imag, vb.real, vb.imag)):
            continue
        evaluated += 1
        if abs(va - vb) > 1e-9:
            bad.append((s, va, vb))
    if evaluated == 0:
        return False, (f"[UNDECIDED][{METHODS['sampling']}] {label}: "
                       f"표본 {len(samples)}개 중 평가 성공 0개 — 판정 불능. "
                       f"표본을 바꾸거나 기호 검증으로 보강할 것")
    ok = not bad
    msg = (f"[{'PASS' if ok else 'FAIL'}][{METHODS['sampling']}] {label}: "
           f"평가 {evaluated}/{len(samples)}개" + ("" if ok else f" | 불일치 {bad[:3]}"))
    return ok, msg


def check_steps(steps, *, label="단계 항등"):
    """풀이 단계의 좌변-우변 항등을 일괄 점검.

    steps: [(lhs, rhs), ...]  각 변형이 항등(같은 값)이어야 한다.
    반환: (all_ok, [메시지...])

    주의: 이 함수는 **식 변형(항등)** 전용이다. '2x+4=10 → 2x=6' 같은
    방정식 풀이 단계는 항등이 아니라 동치 변형이므로 check_equation_steps를 쓸 것.
    """
    msgs = []
    all_ok = True
    for i, (lhs, rhs) in enumerate(steps, 1):
        ok, m = assert_equal(lhs, rhs, label=f"{label} 단계{i}")
        all_ok = all_ok and ok
        msgs.append(m)
    return all_ok, msgs


def _to_relational(s):
    """문자열/객체를 sympy 관계식(Eq/부등식)으로. 'lhs=rhs'(단일 =)도 허용."""
    if isinstance(s, (sp.Equality, sp.Rel)):
        return s
    if isinstance(s, str):
        t = s.strip()
        # 단일 '='를 Eq로 (==, <=, >=, != 는 보존)
        if "=" in t and not any(op in t for op in ("==", "<=", ">=", "!=", "<", ">")):
            lhs, _, rhs = t.partition("=")
            return sp.Eq(sp.sympify(lhs), sp.sympify(rhs))
        return sp.sympify(t)
    return s


def _solset(rel, v):
    """관계식의 실수 해집합. 등식은 solveset, 부등식은 as_set 기반."""
    rel = _to_relational(rel)
    if isinstance(rel, sp.Equality):
        return sp.solveset(rel, v, domain=sp.S.Reals)
    # 부등식: solve_univariate_inequality 경유가 가장 견고
    sol = sp.solve_univariate_inequality(rel, v, relational=False)
    return sol


def check_inequality(inequality, var, claimed, *, label="부등식 해"):
    """부등식의 실제 해집합과 주장 해(부등식 또는 구간)를 대조.

    inequality: '-2*x < 6' 같은 부등식(문자열 또는 sympy 관계식).
    var: 변수. claimed: 'x > -3' 같은 주장 부등식(문자열/관계식) 또는 sympy Set.
    반환: (ok, message). 집합 포함 관계가 양방향으로 성립해야 PASS.
    판정 불능(is_subset이 None)이면 경계 안팎 표본 대입으로 폴백한다.

    예: check_inequality('-2*x < 6', 'x', 'x > -3')  → PASS
        check_inequality('-2*x < 6', 'x', 'x < -3')  → FAIL (부등호 방향 오개념)
    """
    v = sp.Symbol(var) if isinstance(var, str) else var
    actual = _solset(inequality, v)
    if isinstance(claimed, sp.Set):
        cset = claimed
    else:
        cset = _solset(claimed, v)

    a_in_c = actual.is_subset(cset)
    c_in_a = cset.is_subset(actual)
    if a_in_c is not None and c_in_a is not None:
        ok = bool(a_in_c and c_in_a)
        detail = ""
        if not ok:
            missing = sp.simplify(actual - cset)   # 주장이 빠뜨린 해
            extra = sp.simplify(cset - actual)     # 주장에만 있는 가짜 해
            if missing != sp.S.EmptySet:
                detail += f" | 누락된 해 ⊆ {missing}"
            if extra != sp.S.EmptySet:
                detail += f" | 잘못 포함된 값 ⊆ {extra}"
        return ok, (f"[{'PASS' if ok else 'FAIL'}][{METHODS['solveset']}] {label}: "
                    f"실제={actual} 주장={cset}{detail}")

    # 폴백: 기호 포함 판정 불능 → 표본 점검 (UNDECIDED 가능)
    rel_a = _to_relational(inequality)
    rel_c = _to_relational(claimed) if not isinstance(claimed, sp.Set) else None
    tested = mismatched = 0
    for s in (-10, -3, sp.Rational(-5, 2), -1, 0, 1, 3, 10):
        try:
            ta = bool(rel_a.subs(v, s))
            tc = (s in cset) if rel_c is None else bool(rel_c.subs(v, s))
        except Exception:
            continue
        tested += 1
        if ta != tc:
            mismatched += 1
    if tested == 0:
        return False, (f"[UNDECIDED][{METHODS['solveset']}] {label}: "
                       f"집합 비교·표본 모두 판정 불능")
    ok = mismatched == 0
    return ok, (f"[{'PASS' if ok else 'FAIL'}][{METHODS['sampling']}] {label}: "
                f"표본 폴백 {tested}점 중 불일치 {mismatched}점")


def check_equation_steps(steps, var, *, label="동치 변형"):
    """방정식/부등식 풀이 체인의 각 단계가 해집합을 보존하는지 점검.

    steps: ['2*x + 4 = 10', '2*x = 6', 'x = 3'] 같은 관계식 나열.
    연속한 두 관계식의 실수 해집합이 같아야 동치 변형이다. 깨진 단계에서
    해가 늘었으면(외래근 도입: 양변 제곱 등) '외래근', 줄었으면(해 소실:
    0일 수 있는 식으로 양변 나누기 등) '해 누락'으로 원인까지 짚어준다.

    반환: (all_ok, [메시지...]).
    """
    v = sp.Symbol(var) if isinstance(var, str) else var
    msgs = []
    all_ok = True
    prev_rel, prev_set = None, None
    for i, raw in enumerate(steps, 1):
        rel = _to_relational(raw)
        try:
            cur = _solset(rel, v)
        except Exception as e:
            all_ok = False
            msgs.append(f"[UNDECIDED][{METHODS['equiv']}] {label} 단계{i}: "
                        f"해집합 계산 불능({type(e).__name__}) — 수동 확인 필요")
            prev_rel, prev_set = rel, None
            continue
        if prev_set is not None:
            gained = sp.simplify(cur - prev_set)   # 새로 생긴 해 = 외래근
            lost = sp.simplify(prev_set - cur)     # 사라진 해 = 해 누락
            same = (gained == sp.S.EmptySet) and (lost == sp.S.EmptySet)
            if same:
                msgs.append(f"[PASS][{METHODS['equiv']}] {label} 단계{i-1}→{i}: "
                            f"해집합 보존 ({cur})")
            else:
                all_ok = False
                why = []
                if gained != sp.S.EmptySet:
                    why.append(f"외래근 도입 {gained} (양변 제곱·곱 의심)")
                if lost != sp.S.EmptySet:
                    why.append(f"해 누락 {lost} (0일 수 있는 식으로 나눔 의심)")
                msgs.append(f"[FAIL][{METHODS['equiv']}] {label} 단계{i-1}→{i}: "
                            f"{prev_set} → {cur} | " + " · ".join(why))
        prev_rel, prev_set = rel, cur
    return all_ok, msgs


def _demo():
    print("=== math-verification verify.py 데모 ===")
    print(assert_equal("(x+1)**2", "x**2 + 2*x + 1")[1])
    print(assert_equal("(x+1)**2", "x**2 + 1")[1])          # FAIL 예시
    print(check_solutions("x**2 - 5*x + 6", "x", ["2", "3"])[1])
    print(check_solutions("x**2 - 5*x + 6", "x", ["2", "3", "5"])[1])  # 외래근
    print(check_solutions("x**2 - 4", "x", ["2"])[1])        # 유효근 누락
    print(sample_identity("sin(x)**2 + cos(x)**2", "1", "x")[1])
    print(sample_identity("zoo*x", "nan", "x")[1])           # 평가 불능 → UNDECIDED
    ok, msgs = check_steps([("2*x + 4", "2*(x+2)"), ("2*(x+2)", "2*x + 4")])
    for m in msgs:
        print(m)
    # 부등식 — 대표 오개념: -2x<6 을 x<-3 으로 (방향 안 뒤집음)
    print(check_inequality("-2*x < 6", "x", "x > -3")[1])    # PASS
    print(check_inequality("-2*x < 6", "x", "x < -3")[1])    # FAIL
    # 동치 변형 체인 — 양변 제곱으로 외래근이 생기는 사례
    ok, msgs = check_equation_steps(["2*x + 4 = 10", "2*x = 6", "x = 3"], "x")
    for m in msgs:
        print(m)
    ok, msgs = check_equation_steps(["sqrt(x) = -2", "x = 4"], "x")  # 외래근
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
