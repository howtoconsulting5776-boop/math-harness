#!/usr/bin/env python3
"""grade_check — 풀이·설명이 '그 학년에 안 배운 도구'를 썼는지 잡는 린터.

목적: 학년 눈높이 보장을 사람 눈이 아니라 코드로 한 번 더 거른다. 풀이/설명
텍스트에서 해당 학년·학기가 아직 배우지 않은 표기·도구(예: 초등 풀이에 미지수
x, 근호 √; 중1·2에 삼각비; 고1에 미적분·로그)를 찾아 경고한다.

설계: 도구별 해금 시점은 references/curriculum-unlocks.json **단일 소스**에서
읽는다(curriculum-map.md의 해금 표와 1:1). 문서와 린터가 어긋날 수 없다.
JSON을 못 찾으면 내장 폴백 데이터로 동작한다(번들 이동·복사 안전).

이건 '완벽한 분류기'가 아니라 **고신호 휴리스틱 가드**다. 학년만 주어지면
그 학년 과정을 마친 시점으로 관대하게 판정하고, 학기까지 주어지면(예:
'중3-1', '중2 2학기') 정밀 판정한다. math-verifier가 검산과 함께 돌려 WARN을
띄우고, math-solver/math-explainer는 풀이 확정 전에 스스로 점검하는 용도.

사용:
    from grade_check import check, parse_grade
    hits = check("초5", "x = 3 이므로 √2 를 더하면 ...")  # → [{'token':..}, ...]
    hits = check("중3-1", "sin 30° = 1/2")                # 학기 정밀: 삼각비 WARN
CLI:
    python grade_check.py --demo
    python grade_check.py 중2 "sin x 를 적분하면 ..."     # 직접 점검
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# ---------------------------------------------------------------- 해금 데이터
_UNLOCKS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             "..", "references", "curriculum-unlocks.json")

# JSON 부재 시 폴백(JSON과 동일 내용 유지 — 단일 소스는 JSON)
_FALLBACK = {
    "stages": {"elem-1": 1, "elem-2": 2, "elem-3": 3, "elem-4": 4, "elem-5": 5,
               "elem-6": 6, "mid-1-1": 11, "mid-1-2": 12, "mid-2-1": 13,
               "mid-2-2": 14, "mid-3-1": 15, "mid-3-2": 16, "high-1": 21,
               "high-2": 22, "high-3": 23, "university": 99},
    "tools": {
        "neg": {"unlock": "mid-1-1", "label": "음수", "reason": "음수는 중1-1학기"},
        "var_eq": {"unlock": "mid-1-1", "label": "미지수 문자 방정식",
                   "reason": "문자 미지수·방정식은 중1-1학기"},
        "exp_pow": {"unlock": "mid-1-1", "label": "지수 표기 ^",
                    "reason": "거듭제곱 표기는 중1부터"},
        "sqrt": {"unlock": "mid-3-1", "label": "근호/제곱근",
                 "reason": "제곱근·실수는 중3-1학기"},
        "trig_ratio": {"unlock": "mid-3-2", "label": "삼각비(sin·cos·tan)",
                       "reason": "삼각비는 중3-2학기"},
        "trig_func": {"unlock": "high-2", "label": "삼각함수",
                      "reason": "삼각함수는 고2(대수)"},
        "log": {"unlock": "high-2", "label": "로그", "reason": "지수·로그는 고2(대수)"},
        "calc": {"unlock": "high-2", "label": "미적분/극한",
                 "reason": "극한·다항함수 미적분은 고2(미적분Ⅰ)"},
        "vector": {"unlock": "high-3", "label": "벡터", "reason": "벡터는 고3/기하"},
        "quantifier": {"unlock": "university", "label": "형식 논리/ε-δ",
                       "reason": "대학 수준 형식 표기"},
    },
}


def _load_unlocks():
    try:
        with open(_UNLOCKS_PATH, encoding="utf-8") as f:
            data = json.load(f)
        if "stages" in data and "tools" in data:
            return data
    except Exception:
        pass
    return _FALLBACK


_DATA = _load_unlocks()
_STAGES = _DATA["stages"]
_TOOLS = _DATA["tools"]

# ------------------------------------------------------------- 도구 토큰 패턴
# 정규식만 코드에 둔다(해금 '시점'은 JSON이 소스). 한글 용어·한글 인접 경계를
# 처리한다 — Python re의 \b는 한글을 단어문자로 보므로 '-3도', 'sin30°' 같은
# 한글·숫자 인접에서 깨진다. 라틴 문자 lookaround로 직접 경계를 정의한다.
_PATTERNS = {
    "calc": re.compile(
        r"(∫|\\int|d/dx|(?<![A-Za-z])lim(?![A-Za-z])|리미트"
        r"|미분|적분|극한|도함수)"),
    "log": re.compile(  # '로그인'·'블로그' 오탐 방지
        r"((?<![A-Za-z])log(?![A-Za-z])|(?<![A-Za-z])ln(?![A-Za-z])"
        r"|(?<!블)(?<!탈)로그(?!인|아웃))"),
    "trig_func": re.compile(r"삼각함수"),
    "trig_ratio": re.compile(  # sin30° 같은 무공백, 한글 표기까지
        r"((?<![A-Za-z])(sin|cos|tan)(?![A-Za-z])"
        r"|삼각비|코사인|탄젠트|사인(?!펜))"),
    "sqrt": re.compile(r"(√|\\sqrt|제곱근|루트)"),
    "exp_pow": re.compile(r"[A-Za-z0-9\)]\s*\^\s*\d"),
    "var_eq": re.compile(
        r"(?<![A-Za-z])[a-zA-Z]\s*=(?!=)|(?<![<>=!])=\s*[a-zA-Z](?![A-Za-z])"),
    # 음수: 숫자·괄호·라틴문자 뒤 하이픈은 제외(3-4-5, x-2, (2)-3).
    # 끝 \b 제거 — '-3도'처럼 한글이 바로 붙어도 잡는다.
    "neg": re.compile(r"(?<![\d\)A-Za-z])-\s*\d+"),
    "quantifier": re.compile(r"(∀|∃|ε\s*-\s*δ|epsilon)"),
}

# ------------------------------------------------------------------ 학년 파싱
_GRADE_RE = re.compile(
    r"(초|중|고|초등|중등|고등|elementary|middle|high)\s*([1-6])?"
    r"(?:\s*[-–]\s*([12])|\s*([12])\s*학기)?", re.I)

_BAND_MAP = {"초": "elem", "초등": "elem", "elementary": "elem",
             "중": "mid", "중등": "mid", "middle": "mid",
             "고": "high", "고등": "high", "high": "high"}


def parse_grade(s):
    """학년 문자열 → (band, level). 기존 API 유지(테스트 호환)."""
    band, level, _sem = parse_grade_semester(s)
    return (band, level)


def parse_grade_semester(s):
    """학년(+학기) 문자열 → (band, level, semester|None).

    예: '초5'→('elem',5,None) / '중3-1'→('mid',3,1) / '중2 2학기'→('mid',2,2)
    """
    if not s:
        return (None, None, None)
    m = _GRADE_RE.search(str(s))
    if not m:
        return (None, None, None)
    band = _BAND_MAP.get(m.group(1).lower())
    lvl = int(m.group(2)) if m.group(2) else None
    sem = int(m.group(3) or m.group(4)) if (m.group(3) or m.group(4)) else None
    return (band, lvl, sem)


def _student_stage_order(band, level, semester):
    """학생의 진도 단계 order. 학기 미상이면 관대하게(그 학년 수료 기준)."""
    if band == "elem":
        return _STAGES.get(f"elem-{level or 6}", 6)
    if band == "mid":
        if level is None:
            return _STAGES["mid-3-2"]          # '중등'만 → 최대치(관대)
        sem = semester or 2                     # 학년만 → 그 학년 수료(관대)
        return _STAGES.get(f"mid-{level}-{sem}", _STAGES["mid-3-2"])
    if band == "high":
        return _STAGES.get(f"high-{level or 3}", _STAGES["high-3"])
    return None


# ------------------------------------------------------------------ 핵심 API
def check(grade, text):
    """grade(예 '초5','중2','중3-1','고1')와 풀이/설명 text의 위반 토큰 목록.

    반환: [{'key','token','reason','sample'}...]  비어 있으면 학년 적합.
    """
    band, level, semester = parse_grade_semester(grade)
    if band is None:
        return []
    order = _student_stage_order(band, level, semester)
    hits = []
    for key, tool in _TOOLS.items():
        if _STAGES.get(tool["unlock"], 99) <= order:
            continue                            # 이미 해금된 도구
        rx = _PATTERNS.get(key)
        if rx is None:
            continue
        m = rx.search(text or "")
        if m:
            hits.append({"key": key, "token": tool["label"],
                         "reason": tool["reason"], "sample": m.group(0).strip()})
    return hits


def report(grade, text):
    hits = check(grade, text)
    band, level, semester = parse_grade_semester(grade)
    sem = f"-{semester}" if semester else ""
    head = f"[grade_check] {grade} (band={band}, level={level}{sem})"
    if not hits:
        return f"{head}: OK — 학년 초과 도구 없음"
    lines = [f"{head}: WARN — 학년 초과 의심 {len(hits)}건"]
    for h in hits:
        lines.append(f"  - {h['token']} (예: '{h['sample']}') → {h['reason']}")
    return "\n".join(lines)


def _demo():
    cases = [
        ("초5", "정사각형 넓이는 한 변 × 한 변 = 4 × 4 = 16"),       # OK
        ("초5", "x = 3 이고 √2 를 더하면 ..."),                      # WARN(문자,근호)
        ("초5", "온도가 영하 3도, 즉 -3도가 되었어요"),               # WARN(음수·한글경계)
        ("중2", "기울기를 구하면 y = 2x + 1 이다"),                   # OK(중2 함수)
        ("중2", "sin30° = 1/2 이므로 ..."),                          # WARN(삼각, 무공백)
        ("중2", "코사인 법칙을 쓰면 ..."),                            # WARN(한글 표기)
        ("중3", "삼각비 sin 30° = 1/2 를 쓰면 ..."),                  # OK(중3 수료 기준)
        ("중3-1", "삼각비 sin 30° = 1/2 를 쓰면 ..."),                # WARN(학기 정밀)
        ("중2", "이 함수를 적분하면 ..."),                            # WARN(미적분)
        ("고1", "이 함수를 적분하면 ..."),                            # WARN(미적분은 고2)
        ("고1", "로그인 후 로그아웃 한다"),                           # OK(로그 오탐 방지)
        ("고2", "f(x)=x^2 를 미분하면 f'(x)=2x"),                     # OK(고2 미적분)
        ("초4", "변의 길이가 3-4-5 인 삼각형"),                       # OK(하이픈 오탐 없음)
    ]
    for g, t in cases:
        print(report(g, t))
        print()


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="학년 초과 도구 린터")
    ap.add_argument("--demo", action="store_true")
    ap.add_argument("grade", nargs="?", help="예: 초5, 중2, 중3-1, 고1")
    ap.add_argument("text", nargs="?", help="풀이/설명 텍스트")
    args = ap.parse_args()
    if args.demo:
        _demo()
    elif args.grade and args.text:
        print(report(args.grade, args.text))
    else:
        ap.print_help()
