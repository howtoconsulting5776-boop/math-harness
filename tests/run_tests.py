#!/usr/bin/env python3
"""의존성 없는 테스트 러너 — pytest가 없어도 회귀 테스트를 돌리고, 하나라도
실패하면 종료코드 1로 끝낸다. CI가 콘솔을 사람 눈으로 읽지 않아도 회귀를 잡는다.

pytest가 있으면 `pytest -q tests/`가 더 낫지만, 이 러너는 최소 환경 보장용.
사용: python tests/run_tests.py
"""
import importlib
import os
import sys
import traceback

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
for _d in ["skills/math-verification/scripts", "skills/geometry-figures/scripts",
           "skills/problem-bank/scripts", "skills/math-solving/scripts"]:
    sys.path.insert(0, os.path.join(_ROOT, *_d.split("/")))
sys.path.insert(0, _HERE)


def main():
    test_mods = [f[:-3] for f in os.listdir(_HERE)
                 if f.startswith("test_") and f.endswith(".py")]
    passed = failed = 0
    failures = []
    for modname in sorted(test_mods):
        mod = importlib.import_module(modname)
        for name in sorted(dir(mod)):
            if not name.startswith("test_"):
                continue
            fn = getattr(mod, name)
            if not callable(fn):
                continue
            try:
                fn()
                passed += 1
            except Exception:
                failed += 1
                failures.append(f"{modname}.{name}\n{traceback.format_exc()}")
    print(f"\n=== tests: {passed} passed, {failed} failed ===")
    for f in failures:
        print("\nFAIL:", f)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
