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

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

TYPE_EMOJI = {"풀이": "📝", "오답노트": "🔧", "개념": "💡", "출제": "✏️"}


def _slug(text, maxlen=50):
    t = re.sub(r"\s+", "-", text.strip())
    t = re.sub(r"[^\w가-힣\-]", "", t)
    return (t[:maxlen] or "note").strip("-")


def _phash(problem):
    norm = re.sub(r"\s+", "", problem or "")
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
        "tags": meta.get("tags", []),
        "source": meta.get("source", ""),
        "created": meta.get("created", _today()),
        "problem_hash": phash,
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
    out += ["```dataview", "TABLE grade, unit, difficulty, type, verified, answer",
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
                out.append(f"- {emo} {chk} [[{e['_path']}|{e.get('title')}]] "
                           f"<sub>{diff} · 답: {ans}</sub>")
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
    idx, n = rebuild_index(bank)
    print(f"saved: {p1} (created={c1})")
    print(f"saved: {p2} (created={c2})")
    print(f"dup check: created={c3} (False이면 중복 방지 동작)")
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
