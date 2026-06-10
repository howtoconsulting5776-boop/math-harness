#!/usr/bin/env python3
"""problem-bank 헬퍼 — 푼 문제를 구조화 노트로 저장하고 인덱스를 만든다.

표준 라이브러리만 사용(외부 패키지 불필요). 노트는 YAML 프런트매터 +
섹션 본문으로 구성되어 Obsidian/Dataview에서 학년·단원·개념·난이도·검증
상태로 질의할 수 있다. 같은 문제(problem_hash)는 중복 저장하지 않는다.

사용(파이썬):
    from bank import save_note, rebuild_index
    save_note("problem-bank",
        meta={"title":"일차방정식 3(x-2)=x+4", "grade":"중2", "unit":"일차방정식",
              "concept":["이항","일차방정식"], "difficulty":"중", "type":"풀이",
              "answer":"x=5", "verified":True, "tags":["수학","중2"]},
        problem="3(x-2)=x+4 를 풀어라.",
        sections={"풀이":"...","눈높이 설명":"...","핵심 개념":"..."})
    rebuild_index("problem-bank")

CLI:
    python bank.py --demo
    python bank.py --index problem-bank      # 인덱스만 재생성
"""
from __future__ import annotations

import argparse
import hashlib
import os
import re
import sys
import unicodedata

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

TYPE_EMOJI = {"풀이": "📝", "오답노트": "🔧", "개념": "💡", "출제": "✏️"}


def _slug(text, maxlen=50):
    t = re.sub(r"\s+", "-", text.strip())
    t = re.sub(r"[^\w가-힣\-]", "", t)
    return (t[:maxlen] or "note").strip("-")


# 수학 기호 이형(異形) → ASCII 표준형. 같은 문제가 −(U+2212)와 -(하이픈)로
# 적혔다는 이유로 다른 해시가 되는 것을 막는다.
_SYMBOL_MAP = str.maketrans({
    "−": "-", "–": "-", "—": "-",            # 마이너스/대시 이형
    "×": "*", "·": "*", "∙": "*", "⋅": "*",  # 곱셈
    "÷": "/", "∕": "/",                       # 나눗셈
    "≤": "<=", "≥": ">=", "≠": "!=",
    "²": "^2", "³": "^3",
    "（": "(", "）": ")", "［": "[", "］": "]",
    "，": ",", "．": ".", "：": ":",
})


def _normalize(problem):
    """해시 전 정규화: NFKC + 수학기호 통일 + 공백 제거 + 라틴 소문자화."""
    t = unicodedata.normalize("NFKC", problem or "")
    t = t.translate(_SYMBOL_MAP)
    t = re.sub(r"\s+", "", t)
    return t.casefold()


def _phash(problem):
    """정확 중복 해시 — 정규화 후 동일 텍스트면 같은 문제."""
    return hashlib.sha1(_normalize(problem).encode("utf-8")).hexdigest()[:10]


def _shash(problem):
    """구조 해시 — 숫자를 #로 추상화해 '숫자만 바꾼 변형'이 같은 값을 갖는다.

    예: '3(x-2)=x+4'와 '5(x-1)=x+7'은 phash는 다르지만 shash는 같다.
    숫자가 바뀌면 뒤따르는 조사도 바뀌므로(4를→8을) 받침 유무 조사쌍을
    통일한다. 변형 문제 군집·유사 문제 추천(복습 루프)의 키로 쓴다.
    """
    norm = re.sub(r"\d+(\.\d+)?", "#", _normalize(problem))
    for pair, rep in ((r"[을를]", "을"), (r"[이가]", "이"),
                      (r"[은는]", "은"), (r"[과와]", "과")):
        norm = re.sub(rf"(?<=#){pair}", rep, norm)
    return hashlib.sha1(norm.encode("utf-8")).hexdigest()[:10]


def _fm_value(v):
    """프런트매터 값 직렬화: 리스트는 [a, b], 불리언/문자열 처리."""
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (list, tuple)):
        inner = ", ".join(str(x) for x in v)
        return f"[{inner}]"
    return str(v)


def _today():
    """resume-안전: 환경변수 MATH_BANK_DATE가 있으면 사용, 없으면 빈 값."""
    return os.environ.get("MATH_BANK_DATE", "")


def save_note(bank_dir, meta, problem, sections, *, figure=None, overwrite=False):
    """노트 1개를 저장. 반환: (path, created:bool).

    bank_dir/<grade>/<unit>/<slug>-<hash>.md 에 쓴다. 같은 problem_hash가 이미
    있으면 overwrite=False일 때 건너뛰고 기존 경로 반환(중복 방지).
    """
    grade = str(meta.get("grade", "기타"))
    unit = str(meta.get("unit", "기타"))
    phash = _phash(problem)
    title = meta.get("title") or (problem or "note")[:40]
    folder = os.path.join(bank_dir, _slug(grade), _slug(unit))
    os.makedirs(folder, exist_ok=True)

    # 중복 검사: 같은 폴더에 같은 hash가 박힌 파일이 있는가
    for fn in os.listdir(folder):
        if fn.endswith(f"-{phash}.md") and not overwrite:
            return os.path.join(folder, fn), False

    path = os.path.join(folder, f"{_slug(title)}-{phash}.md")

    fm = {
        "title": title,
        "grade": grade,
        "unit": unit,
        "concept": meta.get("concept", []),
        "difficulty": meta.get("difficulty", ""),
        "type": meta.get("type", "풀이"),
        "answer": meta.get("answer", ""),
        "verified": bool(meta.get("verified", False)),
        # 검증 '수준' — 무엇이 기계로 보장됐는지. verify.py의 METHODS와 짝:
        # 기호검증 | 해집합 | 수치표본 | 동치변형 | 좌표기하 | 미검증
        "verify_method": str(meta.get("verify_method", "")
                             or ("미검증" if not meta.get("verified") else "")),
        "tags": meta.get("tags", []),
        "source": meta.get("source", ""),
        "created": meta.get("created", _today()),
        "problem_hash": phash,
        "structure_hash": _shash(problem),
    }
    lines = ["---"]
    for k, v in fm.items():
        lines.append(f"{k}: {_fm_value(v)}")
    lines.append("---\n")
    lines.append(f"# {title}\n")
    lines.append("## 문제")
    lines.append(problem.strip() + "\n")
    if figure:
        lines.append(f"![figure]({figure})\n")
    for name, content in sections.items():
        lines.append(f"## {name}")
        lines.append(str(content).strip() + "\n")

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return path, True


def _read_frontmatter(path):
    """미니 프런트매터 파서(우리 템플릿 전용). dict 반환."""
    out = {}
    with open(path, encoding="utf-8") as f:
        text = f.read()
    m = re.match(r"^---\n(.*?)\n---", text, re.S)
    if not m:
        return out
    for line in m.group(1).splitlines():
        if ":" not in line:
            continue
        k, _, v = line.partition(":")
        k, v = k.strip(), v.strip()
        if v.startswith("[") and v.endswith("]"):
            v = [x.strip() for x in v[1:-1].split(",") if x.strip()]
        elif v in ("true", "false"):
            v = (v == "true")
        out[k] = v
    return out


def find_similar(bank_dir, problem):
    """같은 구조(숫자만 다른 변형)의 기존 노트를 찾는다.

    반환: [{'path','title','grade','unit','answer'}...] — 정확 중복(phash 동일)은
    제외하고 구조 해시만 같은 변형들. '이 학생이 틀린 문제의 구조적 쌍둥이'를
    복습 추천하거나, 출제 시 기존 변형과의 충돌을 확인하는 데 쓴다.
    """
    target_s, target_p = _shash(problem), _phash(problem)
    out = []
    if not os.path.isdir(bank_dir):
        return out
    for root, _, files in os.walk(bank_dir):
        for fn in files:
            if not fn.endswith(".md") or fn == "INDEX.md":
                continue
            p = os.path.join(root, fn)
            fm = _read_frontmatter(p)
            if (fm.get("structure_hash") == target_s
                    and fm.get("problem_hash") != target_p):
                out.append({"path": os.path.relpath(p, bank_dir).replace("\\", "/"),
                            "title": fm.get("title", ""),
                            "grade": fm.get("grade", ""),
                            "unit": fm.get("unit", ""),
                            "answer": fm.get("answer", "")})
    return out


def rebuild_index(bank_dir):
    """bank_dir 전체를 스캔해 INDEX.md를 학년>단원으로 묶어 생성."""
    entries = []
    for root, _, files in os.walk(bank_dir):
        for fn in files:
            if fn.endswith(".md") and fn != "INDEX.md":
                p = os.path.join(root, fn)
                fm = _read_frontmatter(p)
                if fm:
                    fm["_path"] = os.path.relpath(p, bank_dir).replace("\\", "/")
                    entries.append(fm)

    by_grade = {}
    for e in entries:
        by_grade.setdefault(str(e.get("grade", "기타")), {}).setdefault(
            str(e.get("unit", "기타")), []).append(e)

    out = ["# 📚 문제은행 INDEX", "",
           f"총 {len(entries)}문제. 학년 > 단원으로 정리. "
           "Dataview가 있으면 아래 쿼리로 동적 표를 볼 수 있다.", ""]
    # Dataview 동적 표(옵션)
    out += ["```dataview", "TABLE grade, unit, difficulty, type, verified, verify_method, answer",
            "FROM \"\"", "WHERE problem_hash", "SORT grade ASC, unit ASC", "```", ""]
    for grade in sorted(by_grade):
        out.append(f"## {grade}")
        for unit in sorted(by_grade[grade]):
            out.append(f"### {unit}")
            for e in sorted(by_grade[grade][unit], key=lambda x: str(x.get("title"))):
                emo = TYPE_EMOJI.get(str(e.get("type", "")), "•")
                chk = "✅" if e.get("verified") else "⬜"
                diff = e.get("difficulty", "")
                ans = e.get("answer", "")
                vm = e.get("verify_method", "")
                vm_s = f" · {vm}" if vm and vm != "미검증" else ""
                out.append(f"- {emo} {chk} [[{e['_path']}|{e.get('title')}]] "
                           f"<sub>{diff} · 답: {ans}{vm_s}</sub>")
            out.append("")
    path = os.path.join(bank_dir, "INDEX.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(out))
    return path, len(entries)


def _demo():
    bank = os.path.join(os.environ.get("TMPDIR", "_workspace"), "_bank_demo")
    p1, c1 = save_note(bank,
        {"title": "일차방정식 3(x-2)=x+4", "grade": "중2", "unit": "일차방정식",
         "concept": ["이항", "일차방정식"], "difficulty": "중", "type": "풀이",
         "answer": "x=5", "verified": True, "tags": ["수학", "중2"]},
        problem="3(x-2)=x+4 를 풀어라.",
        sections={"풀이": "3x-6=x+4 → 2x=10 → x=5", "핵심 개념": "이항"})
    p2, c2 = save_note(bank,
        {"title": "부등식 부호 오류", "grade": "중1", "unit": "일차부등식",
         "concept": ["부등식"], "difficulty": "하", "type": "오답노트",
         "answer": "x>-3", "verified": True, "tags": ["수학", "오답"]},
        problem="-2x<6 을 풀어라.",
        sections={"오답 분석": "음수로 나눌 때 부등호 방향이 바뀐다."})
    # 중복 저장 시도(같은 문제)
    p3, c3 = save_note(bank,
        {"title": "중복", "grade": "중2", "unit": "일차방정식"},
        problem="3(x-2)=x+4 를 풀어라.", sections={"풀이": "x"})
    # 유니코드 마이너스(−)로 적은 같은 문제 — 정규화로 중복 잡혀야 함
    p4, c4 = save_note(bank,
        {"title": "유니코드 중복", "grade": "중1", "unit": "일차부등식"},
        problem="−2x<6 을 풀어라.", sections={"풀이": "x"})
    # 숫자만 바꾼 변형 — find_similar로 군집 탐지
    sim = find_similar(bank, "5(x-1)=x+8 을 풀어라.")
    idx, n = rebuild_index(bank)
    print(f"saved: {p1} (created={c1})")
    print(f"saved: {p2} (created={c2})")
    print(f"dup check: created={c3} (False이면 중복 방지 동작)")
    print(f"unicode dup: created={c4} (False이면 정규화 해시 동작)")
    print(f"similar variants of '5(x-1)=x+8': {[s['title'] for s in sim]}")
    print(f"index: {idx} ({n}문제)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="문제은행 저장·인덱스 헬퍼")
    ap.add_argument("--demo", action="store_true")
    ap.add_argument("--index", metavar="BANK_DIR", help="해당 폴더의 INDEX.md만 재생성")
    args = ap.parse_args()
    if args.demo:
        _demo()
    elif args.index:
        idx, n = rebuild_index(args.index)
        print(f"index rebuilt: {idx} ({n}문제)")
    else:
        ap.print_help()
