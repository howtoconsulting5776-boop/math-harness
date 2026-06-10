#!/usr/bin/env python3
"""grade_check — 풀이·설명이 '그 학년에 안 배운 도구'를 썼는지 잡는 린터.

목적: 학년 눈높이 보장을 사람 눈이 아니라 코드로 한 번 더 거른다. 풀이/설명
텍스트에서 해당 학년이 아직 배우지 않은 표기·도구(예: 초등 풀이에 미지수 x,
근호 √, 지수 ^; 중1·2 풀이에 삼각함수·미적분·로그)를 찾아 경고한다.

이건 '완벽한 분류기'가 아니라 **고신호 휴리스틱 가드**다. 거짓양성을 줄이려고
명백한 패턴만 본다. math-verifier가 검산과 함께 돌려 WARN을 띄우고, math-solver/
math-explainer는 풀이 확정 전에 스스로 점검하는 용도.

사용:
    from grade_check import check, parse_grade
    hits = check("초5", "x = 3 이므로 √2 를 더하면 ...")   # → [{'token':..,'reason':..}, ...]
CLI:
    python grade_check.py --demo
    python grade_check.py 중2 "sin x 를 적분하면 ..."     # 직접 점검
"""
from __future__ import annotations

import argparse
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# 학년 문자열 → (band, level)  band: elem|mid|high, level: 학교급 내 학년(1~)
_GRADE_RE = re.compile(r"(초|중|고|초등|중등|고등|elementary|middle|high)\s*([1-6])?", re.I)


def parse_grade(s):
    if not s:
        return (None, None)
    m = _GRADE_RE.search(str(s))
    if not m:
        return (None, None)
    head = m.group(1).lower()
    lvl = int(m.group(2)) if m.group(2) else None
    if head in ("초", "초등", "elementary"):
        return ("elem", lvl)
    if head in ("중", "중등", "middle"):
        return ("mid", lvl)
    return ("high", lvl)


# 도구 토큰: (정규식, 라벨, 사람이 읽는 사유)
_RULES = {
    "calc": (re.compile(r"(∫|\\int|d/dx|\blim\b|→\s*\d|미분|적분|극한|도함수)"),
             "미적분/극한", "미적분·극한은 고2 이상"),
    "log": (re.compile(r"(\blog\b|\bln\b|로그)"), "로그", "로그는 고2 이상"),
    "trig": (re.compile(r"(\bsin\b|\bcos\b|\btan\b|sin|cos|tan|삼각비|삼각함수)"),
             "삼각비/삼각함수", "삼각비는 중3, 삼각함수는 고2"),
    "sqrt": (re.compile(r"(√|\\sqrt|제곱근|루트)"), "근호/제곱근", "제곱근은 중3"),
    "exp_pow": (re.compile(r"[A-Za-z0-9\)]\s*\^\s*\d"), "지수 표기 ^",
                "거듭제곱 문자식은 중등"),
    "var_eq": (re.compile(r"(?<![A-Za-z])[a-zA-Z]\s*=(?!=)|(?<![<>=!])=\s*[a-zA-Z](?![A-Za-z])"),
               "미지수 문자 방정식", "문자 미지수·방정식은 중1 이상"),
    "neg": (re.compile(r"(?<![\d\)])\-\s*\d+\b"), "음수", "음수는 중1 이상"),
    "quantifier": (re.compile(r"(∀|∃|ε\s*-\s*δ|epsilon)"), "형식 논리/ε-δ",
                   "대학 수준 형식 표기"),
}

# band(+level)별 '금지' 규칙 키
# elem: 초등 — 문자식·음수·지수·근호·삼각·로그·미적분 전부 금지
# mid: 중등 — 미적분·로그 금지, 삼각은 중3부터 허용(중1·2 금지)
# high: 고등 — 대학 수준 형식 표기만 경고
def _forbidden_keys(band, level):
    if band == "elem":
        return ["var_eq", "neg", "exp_pow", "sqrt", "trig", "log", "calc"]
    if band == "mid":
        keys = ["calc", "log"]
        # 삼각비는 중3부터. 중1·2(또는 학년 미상 중등)는 삼각 금지.
        if level is None or level < 3:
            keys.append("trig")
        return keys
    if band == "high":
        return ["quantifier"]
    return []  # 학년 미상이면 점검 보류


def check(grade, text):
    """grade(예 '초5','중2','고1')와 풀이/설명 text를 받아 위반 토큰 목록 반환.

    반환: [{'key','token','reason','sample'}...]  비어 있으면 학년 적합.
    """
    band, level = parse_grade(grade)
    if band is None:
        return []
    hits = []
    for key in _forbidden_keys(band, level):
        rx, label, reason = _RULES[key]
        m = rx.search(text or "")
        if m:
            hits.append({"key": key, "token": label, "reason": reason,
                         "sample": m.group(0).strip()})
    return hits


def report(grade, text):
    hits = check(grade, text)
    band, level = parse_grade(grade)
    head = f"[grade_check] {grade} (band={band}, level={level})"
    if not hits:
        return f"{head}: OK — 학년 초과 도구 없음"
    lines = [f"{head}: WARN — 학년 초과 의심 {len(hits)}건"]
    for h in hits:
        lines.append(f"  - {h['token']} (예: '{h['sample']}') → {h['reason']}")
    return "\n".join(lines)


def _demo():
    cases = [
        ("초5", "정사각형 넓이는 한 변 × 한 변 = 4 × 4 = 16"),          # OK
        ("초5", "x = 3 이고 √2 를 더하면 ..."),                         # WARN(문자,근호)
        ("중2", "기울기를 구하면 y = 2x + 1 이다"),                      # OK(중2 함수)
        ("중2", "sin 30° = 1/2 이므로 ..."),                            # WARN(삼각, 중3부터)
        ("중3", "삼각비 sin 30° = 1/2 를 쓰면 ..."),                     # OK(중3 삼각비)
        ("중2", "이 함수를 적분하면 ..."),                              # WARN(미적분)
        ("고2", "f(x)=x^2 를 미분하면 f'(x)=2x"),                        # OK(고2 미적분)
    ]
    for g, t in cases:
        print(report(g, t))
        print()


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="학년 초과 도구 린터")
    ap.add_argument("--demo", action="store_true")
    ap.add_argument("grade", nargs="?", help="예: 초5, 중2, 고1")
    ap.add_argument("text", nargs="?", help="풀이/설명 텍스트")
    args = ap.parse_args()
    if args.demo:
        _demo()
    elif args.grade and args.text:
        print(report(args.grade, args.text))
    else:
        ap.print_help()
