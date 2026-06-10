"""pytest 부트스트랩 — 번들 스크립트 디렉터리를 import 경로에 추가.

pytest는 conftest.py를 자동 로드하므로, 테스트가 `from verify import ...`처럼
스크립트를 바로 임포트할 수 있다. 단독 러너(run_tests.py)도 같은 경로를 넣는다.
"""
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SCRIPT_DIRS = [
    "skills/math-verification/scripts",
    "skills/geometry-figures/scripts",
    "skills/problem-bank/scripts",
    "skills/math-solving/scripts",
]
for _d in _SCRIPT_DIRS:
    p = os.path.join(_ROOT, *_d.split("/"))
    if p not in sys.path:
        sys.path.insert(0, p)
