#!/usr/bin/env python3
"""geometry-figures 헬퍼 — 의존성 없는 SVG 도형 작도기.

순수 표준 라이브러리만 사용(외부 패키지 불필요)하여, 초중고 기하에서 자주
쓰는 요소(좌표평면·격자, 점·라벨, 선분·다각형, 원, 각 표시, 직각 표시,
등변 눈금)를 정확한 SVG로 조립한다.

핵심 설계: 좌표는 '수학 좌표(y가 위로 증가)'로 입력하고, 내부에서 SVG 좌표
(y가 아래로 증가)로 변환한다. sympy.geometry로 구한 정점을 그대로 넘기면
그림과 계산이 일치한다.

사용:
    from svg_figure import Figure
    fig = Figure(width=400, height=400, view=(-1, 6, -1, 6))   # xmin,xmax,ymin,ymax
    fig.grid()
    fig.axes()
    fig.polygon([(0,0),(4,0),(0,3)], label_vertices=["A","B","C"])
    fig.right_angle((0,0),(4,0),(0,3))      # A에서의 직각
    fig.tick((0,0),(0,3), n=1)              # 등변 눈금
    fig.save("triangle.svg")

CLI 데모:
    python svg_figure.py --demo out.svg
"""
from __future__ import annotations

import argparse
import math
import sys

# Windows 콘솔(cp949)에서도 한글을 안전하게 출력
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


class Figure:
    def __init__(self, width=400, height=400, view=(-1, 6, -1, 6), padding=10):
        self.w = width
        self.h = height
        self.xmin, self.xmax, self.ymin, self.ymax = view
        self.pad = padding
        self.elems: list[str] = []

    # --- 좌표 변환: 수학 좌표 -> SVG 픽셀 ---
    def _sx(self, x):
        span = self.xmax - self.xmin
        return self.pad + (x - self.xmin) / span * (self.w - 2 * self.pad)

    def _sy(self, y):
        span = self.ymax - self.ymin
        # y 뒤집기
        return self.h - (self.pad + (y - self.ymin) / span * (self.h - 2 * self.pad))

    def _p(self, pt):
        return self._sx(pt[0]), self._sy(pt[1])

    # --- 기본 요소 ---
    def grid(self, step=1, color="#e3e8ef"):
        x = math.ceil(self.xmin)
        while x <= self.xmax:
            x1, y1 = self._p((x, self.ymin))
            x2, y2 = self._p((x, self.ymax))
            self.elems.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" '
                              f'y2="{y2:.1f}" stroke="{color}" stroke-width="1"/>')
            x += step
        y = math.ceil(self.ymin)
        while y <= self.ymax:
            x1, y1 = self._p((self.xmin, y))
            x2, y2 = self._p((self.xmax, y))
            self.elems.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" '
                              f'y2="{y2:.1f}" stroke="{color}" stroke-width="1"/>')
            y += step

    def axes(self, color="#94a3b8"):
        if self.ymin <= 0 <= self.ymax:
            x1, y1 = self._p((self.xmin, 0))
            x2, y2 = self._p((self.xmax, 0))
            self.elems.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" '
                              f'y2="{y2:.1f}" stroke="{color}" stroke-width="1.5"/>')
        if self.xmin <= 0 <= self.xmax:
            x1, y1 = self._p((0, self.ymin))
            x2, y2 = self._p((0, self.ymax))
            self.elems.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" '
                              f'y2="{y2:.1f}" stroke="{color}" stroke-width="1.5"/>')

    def segment(self, a, b, color="#1e293b", width=2):
        x1, y1 = self._p(a)
        x2, y2 = self._p(b)
        self.elems.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" '
                          f'y2="{y2:.1f}" stroke="{color}" stroke-width="{width}"/>')

    def polygon(self, pts, stroke="#1e293b", fill="rgba(59,130,246,0.10)",
                width=2, label_vertices=None):
        d = " ".join(f"{self._sx(x):.1f},{self._sy(y):.1f}" for x, y in pts)
        self.elems.append(f'<polygon points="{d}" fill="{fill}" stroke="{stroke}" '
                          f'stroke-width="{width}" stroke-linejoin="round"/>')
        if label_vertices:
            cx = sum(p[0] for p in pts) / len(pts)
            cy = sum(p[1] for p in pts) / len(pts)
            for (x, y), name in zip(pts, label_vertices):
                # 라벨을 무게중심 반대쪽으로 살짝 밀기
                ox = 12 if x >= cx else -12
                oy = -8 if y >= cy else 16
                self.point((x, y), name, dx=ox, dy=oy)

    def circle(self, center, r, stroke="#1e293b", fill="none", width=2):
        cx, cy = self._p(center)
        # 반지름을 x축 스케일로 환산
        rx = r / (self.xmax - self.xmin) * (self.w - 2 * self.pad)
        self.elems.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{rx:.1f}" '
                          f'fill="{fill}" stroke="{stroke}" stroke-width="{width}"/>')

    def point(self, pt, label=None, dx=10, dy=-8, color="#dc2626"):
        cx, cy = self._p(pt)
        self.elems.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="3.2" fill="{color}"/>')
        if label:
            self.elems.append(f'<text x="{cx + dx:.1f}" y="{cy + dy:.1f}" '
                              f'font-family="serif" font-size="16" font-style="italic" '
                              f'fill="#0f172a">{label}</text>')

    def label(self, pt, text, dx=0, dy=0, size=14, color="#0f172a"):
        cx, cy = self._p(pt)
        self.elems.append(f'<text x="{cx + dx:.1f}" y="{cy + dy:.1f}" text-anchor="middle" '
                          f'font-family="sans-serif" font-size="{size}" fill="{color}">{text}</text>')

    def seg_label(self, a, b, text, offset=14, **kw):
        """선분 ab의 중점 옆에 길이 등을 표기."""
        mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
        self.label(mid, text, dy=-offset, **kw)

    def right_angle(self, vertex, p1, p2, size=0.4, color="#475569"):
        """vertex에서 p1, p2 방향으로 직각 기호(작은 사각형)."""
        v = vertex
        u1 = _unit(v, p1)
        u2 = _unit(v, p2)
        a = (v[0] + u1[0] * size, v[1] + u1[1] * size)
        b = (a[0] + u2[0] * size, a[1] + u2[1] * size)
        c = (v[0] + u2[0] * size, v[1] + u2[1] * size)
        d = " ".join(f"{self._sx(x):.1f},{self._sy(y):.1f}" for x, y in [v, a, b, c])
        self.elems.append(f'<polyline points="{d}" fill="none" stroke="{color}" '
                          f'stroke-width="1.5"/>')

    def angle_arc(self, vertex, p1, p2, r=0.6, color="#2563eb", text=None):
        """vertex의 각을 호로 표시(+선택 라벨)."""
        a1 = math.atan2(p1[1] - vertex[1], p1[0] - vertex[0])
        a2 = math.atan2(p2[1] - vertex[1], p2[0] - vertex[0])
        start = (vertex[0] + r * math.cos(a1), vertex[1] + r * math.sin(a1))
        end = (vertex[0] + r * math.cos(a2), vertex[1] + r * math.sin(a2))
        sx, sy = self._p(start)
        ex, ey = self._p(end)
        rx = r / (self.xmax - self.xmin) * (self.w - 2 * self.pad)
        large = 1 if abs(a2 - a1) > math.pi else 0
        sweep = 1 if (a2 - a1) < 0 else 0
        self.elems.append(f'<path d="M {sx:.1f} {sy:.1f} A {rx:.1f} {rx:.1f} 0 '
                          f'{large} {sweep} {ex:.1f} {ey:.1f}" fill="none" '
                          f'stroke="{color}" stroke-width="1.5"/>')
        if text:
            mid_a = (a1 + a2) / 2
            lab = (vertex[0] + (r + 0.3) * math.cos(mid_a),
                   vertex[1] + (r + 0.3) * math.sin(mid_a))
            self.label(lab, text, size=13, color=color)

    def tick(self, a, b, n=1, color="#16a34a", size=0.12):
        """선분 ab 중앙에 등변 표시 눈금 n개(같은 n=같은 길이 약속)."""
        mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
        u = _unit(a, b)
        perp = (-u[1], u[0])
        gap = 0.12
        for i in range(n):
            off = (i - (n - 1) / 2) * gap
            c = (mid[0] + u[0] * off, mid[1] + u[1] * off)
            p = (c[0] + perp[0] * size, c[1] + perp[1] * size)
            q = (c[0] - perp[0] * size, c[1] - perp[1] * size)
            self.segment(p, q, color=color, width=1.6)

    def func(self, f, color="#7c3aed", width=2, samples=200):
        """함수 y=f(x)를 view 범위에서 그린다."""
        pts = []
        for i in range(samples + 1):
            x = self.xmin + (self.xmax - self.xmin) * i / samples
            try:
                y = f(x)
                if self.ymin - 1 <= y <= self.ymax + 1:
                    pts.append((self._sx(x), self._sy(y)))
                else:
                    pts.append(None)
            except Exception:
                pts.append(None)
        d = []
        pen = False
        for p in pts:
            if p is None:
                pen = False
                continue
            d.append(("L" if pen else "M") + f" {p[0]:.1f} {p[1]:.1f}")
            pen = True
        self.elems.append(f'<path d="{" ".join(d)}" fill="none" stroke="{color}" '
                          f'stroke-width="{width}"/>')

    def svg(self):
        body = "\n  ".join(self.elems)
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" '
                f'height="{self.h}" viewBox="0 0 {self.w} {self.h}">\n'
                f'  <rect width="{self.w}" height="{self.h}" fill="white"/>\n'
                f'  {body}\n</svg>\n')

    def save_svg(self, path):
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.svg())
        return path

    def save_png(self, path, scale=2.0):
        """SVG를 PNG로 래스터화(학생 배포용). svglib+reportlab 사용.

        scale=2.0이면 2배 해상도(또렷한 인쇄·캡처). 변환기가 없으면 명확한
        에러를 던지니, 호출측에서 SVG 폴백을 결정한다.
        """
        try:
            import io as _io
            from svglib.svglib import svg2rlg
            from reportlab.graphics import renderPM
        except Exception as e:  # pragma: no cover
            raise RuntimeError(
                "PNG 변환에는 svglib가 필요합니다: pip install svglib "
                "(없으면 .svg로 저장하세요 — 벡터라 인쇄·확대에 더 강함)"
            ) from e
        drawing = svg2rlg(_io.StringIO(self.svg()))
        if scale and scale != 1.0:
            drawing.width *= scale
            drawing.height *= scale
            drawing.scale(scale, scale)
        renderPM.drawToFile(drawing, path, fmt="PNG", bg=0xFFFFFF)
        return path

    def save(self, path, scale=2.0):
        """확장자로 형식 분기. .png면 래스터화, 그 외엔 SVG."""
        if str(path).lower().endswith(".png"):
            return self.save_png(path, scale=scale)
        return self.save_svg(path)

    def save_both(self, stem, scale=2.0):
        """벡터 원본(.svg)과 배포용(.png)을 함께 저장. 반환: (svg_path, png_path|None)."""
        svg_path = self.save_svg(stem + ".svg")
        try:
            png_path = self.save_png(stem + ".png", scale=scale)
        except RuntimeError:
            png_path = None
        return svg_path, png_path


def _unit(a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    n = math.hypot(dx, dy) or 1.0
    return dx / n, dy / n


def _demo(path):
    fig = Figure(width=420, height=420, view=(-1, 6, -1, 6))
    fig.grid()
    fig.axes()
    fig.polygon([(0, 0), (4, 0), (0, 3)], label_vertices=["A", "B", "C"])
    fig.right_angle((0, 0), (4, 0), (0, 3))
    fig.seg_label((0, 0), (4, 0), "4")
    fig.seg_label((0, 0), (0, 3), "3", offset=-18)
    fig.seg_label((4, 0), (0, 3), "5")
    fig.angle_arc((4, 0), (0, 0), (0, 3), text="θ")
    saved = fig.save(path)
    print(f"saved {saved}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="의존성 없는 SVG 도형 작도기")
    ap.add_argument("--demo", action="store_true")
    ap.add_argument("out", nargs="?", default="figure_demo.svg")
    args = ap.parse_args()
    if args.demo:
        _demo(args.out)
    else:
        ap.print_help()
