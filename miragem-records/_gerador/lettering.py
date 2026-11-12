"""Converte texto em contornos SVG (paths) com deformação opcional.

Todo texto das logos vira contorno vetorial: a logo não depende de fonte
instalada e renderiza igual em qualquer programa.
"""
import math
import os
from fontTools.ttLib import TTFont
from fontTools.pens.basePen import BasePen

FONT_DIR = os.path.join(os.path.dirname(__file__), "fonts")
FONTS = {
    "shrikhand": "shrikhand-latin-400-normal.woff",
    "rubikmono": "rubik-mono-one-latin-400-normal.woff",
    "fraunces900": "fraunces-latin-900-normal.woff",
    "fraunces700": "fraunces-latin-700-normal.woff",
    "fraunces600": "fraunces-latin-600-normal.woff",
    "dmserif": "dm-serif-display-latin-400-normal.woff",
    "dmserifit": "dm-serif-display-latin-400-italic.woff",
    "bagel": "bagel-fat-one-latin-400-normal.woff",
}
_cache = {}


def font(name):
    if name not in _cache:
        f = TTFont(os.path.join(FONT_DIR, FONTS[name]))
        _cache[name] = (f, f.getGlyphSet(), f.getBestCmap(), f["head"].unitsPerEm)
    return _cache[name]


class _Collect(BasePen):
    """Coleta contornos como listas de pontos (com subdivisão para deformar)."""

    def __init__(self, gs, tf, steps=6):
        super().__init__(gs)
        self.tf, self.steps = tf, steps
        self.contours, self.cur, self.last = [], None, None

    def _moveTo(self, p):
        self.cur = [("M", [self.tf(*p)])]
        self.contours.append(self.cur)
        self.last = p

    def _lineTo(self, p):
        a = self.last
        n = self.steps
        for i in range(1, n + 1):
            t = i / n
            self.cur.append(("L", [self.tf(a[0] + (p[0] - a[0]) * t, a[1] + (p[1] - a[1]) * t)]))
        self.last = p

    def _curveToOne(self, c1, c2, p):
        p0 = self.last
        n = 3
        # subdivide cubic in n pieces (de Casteljau)
        segs = []
        P = [p0, c1, c2, p]
        for i in range(n):
            t0, t1 = i / n, (i + 1) / n
            segs.append(_sub_cubic(P, t0, t1))
        for s in segs:
            self.cur.append(("C", [self.tf(*s[1]), self.tf(*s[2]), self.tf(*s[3])]))
        self.last = p

    def _closePath(self):
        self.cur.append(("Z", []))

    _endPath = _closePath


def _bez(P, t):
    a, b, c, d = P
    mt = 1 - t
    return (mt**3 * a[0] + 3 * mt * mt * t * b[0] + 3 * mt * t * t * c[0] + t**3 * d[0],
            mt**3 * a[1] + 3 * mt * mt * t * b[1] + 3 * mt * t * t * c[1] + t**3 * d[1])


def _dbez(P, t):
    a, b, c, d = P
    mt = 1 - t
    return (3 * mt * mt * (b[0] - a[0]) + 6 * mt * t * (c[0] - b[0]) + 3 * t * t * (d[0] - c[0]),
            3 * mt * mt * (b[1] - a[1]) + 6 * mt * t * (c[1] - b[1]) + 3 * t * t * (d[1] - c[1]))


def _sub_cubic(P, t0, t1):
    p0, p3 = _bez(P, t0), _bez(P, t1)
    d0, d1 = _dbez(P, t0), _dbez(P, t1)
    h = (t1 - t0) / 3
    return (p0, (p0[0] + d0[0] * h, p0[1] + d0[1] * h), (p3[0] - d1[0] * h, p3[1] - d1[1] * h), p3)


def layout(fname, text, size, tracking=0.0, kern=None):
    """Retorna [(glyphname, x_offset_em_units)] e largura total em px."""
    f, gs, cmap, upm = font(fname)
    hmtx = f["hmtx"]
    s = size / upm
    out, x = [], 0.0
    kern = kern or {}
    for i, ch in enumerate(text):
        if ch == " ":
            x += hmtx[cmap[32]][0] if 32 in cmap else upm * 0.3
            x += tracking * upm
            continue
        g = cmap[ord(ch)]
        out.append((g, x))
        x += hmtx[g][0] + tracking * upm
        if i + 1 < len(text):
            x += kern.get(text[i:i + 2], 0) * upm
    x -= tracking * upm
    return out, x * s


def contours(fname, text, size, x=0, y=0, tracking=0.0, kern=None, anchor="start"):
    """Contornos do texto em coordenadas SVG; y = linha de base."""
    f, gs, cmap, upm = font(fname)
    s = size / upm
    items, width = layout(fname, text, size, tracking, kern)
    if anchor == "middle":
        x -= width / 2
    elif anchor == "end":
        x -= width
    allc = []
    for g, gx in items:
        tf = (lambda gx: lambda px, py: (x + (gx + px) * s, y - py * s))(gx)
        pen = _Collect(gs, tf)
        gs[g].draw(pen)
        allc.extend(pen.contours)
    return allc, width


def bbox(cs):
    xs, ys = [], []
    for c in cs:
        for _, pts in c:
            for p in pts:
                xs.append(p[0]); ys.append(p[1])
    return min(xs), min(ys), max(xs), max(ys)


def warp(cs, fn):
    """Aplica fn(x, y, u, v) -> (x, y), com u, v normalizados no bbox."""
    x0, y0, x1, y1 = bbox(cs)
    w, h = x1 - x0, y1 - y0
    return [[(cmd, [fn(p[0], p[1], (p[0] - x0) / w, (p[1] - y0) / h) for p in pts]) for cmd, pts in c] for c in cs]


def transform(cs, fn):
    return [[(cmd, [fn(*p) for p in pts]) for cmd, pts in c] for c in cs]


def d(cs):
    parts = []
    for c in cs:
        for cmd, pts in c:
            parts.append(cmd + " ".join(f"{p[0]:.2f} {p[1]:.2f}" for p in pts))
    return "".join(parts)


def on_arc(fname, text, size, cx, cy, r, center_deg=0, bottom=False, tracking=0.0):
    """Texto em arco. Topo: linha de base no raio r, letras para fora.
    Base (bottom=True): lido da esquerda para direita, letras para dentro, r = topo das letras."""
    f, gs, cmap, upm = font(fname)
    s = size / upm
    items, width = layout(fname, text, size, tracking)
    hmtx = f["hmtx"]
    total = width / r
    start = math.radians(center_deg) - total / 2
    out = []
    for g, gx in items:
        adv = hmtx[g][0] * s
        mid = gx * s + adv / 2
        a = start + mid / r
        if not bottom:
            P = (cx + r * math.sin(a), cy - r * math.cos(a))
            T = (math.cos(a), math.sin(a))
            U = (math.sin(a), -math.cos(a))
        else:
            # bottom: a medido a partir da base, positivo para a esquerda->direita
            P = (cx - r * math.sin(-a), cy + r * math.cos(-a))
            P = (cx + r * math.sin(a), cy + r * math.cos(a))
            T = (math.cos(a), -math.sin(a))
            U = (-math.sin(a), -math.cos(a))
            # baseline deve ficar no raio r: deslocamos pela altura de capitular depois
        cap = f["OS/2"].sCapHeight * s if hasattr(f["OS/2"], "sCapHeight") else size * 0.7

        def tf(px, py, P=P, T=T, U=U, adv=adv):
            lx = px * s - adv / 2
            lu = py * s - (cap if bottom else 0)
            return (P[0] + lx * T[0] + lu * U[0], P[1] + lx * T[1] + lu * U[1])

        pen = _Collect(gs, tf, steps=2)
        gs[g].draw(pen)
        out.extend(pen.contours)
    return out


def cap_height(fname, size):
    f, gs, cmap, upm = font(fname)
    return f["OS/2"].sCapHeight * size / upm
