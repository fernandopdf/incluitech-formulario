"""Gera as 3 propostas de logo da Miragem Records (Etapa 1).

Saída: miragem-records/logo/propostas/<variacao>/<layout>-<fundo>.svg
       miragem-records/logo/propostas/comparativo.html
Uso:   python3 gerar_logos.py
"""
import math
import os
import lettering as L

OUT = os.path.join(os.path.dirname(__file__), "..", "logo", "propostas")

PAPEL = "#EADBB8"
PRETO = "#1C1611"
VERMELHO = "#B8321F"
MOSTARDA = "#D99A2B"
AZUL = "#1F3A4D"

CORES = {
    "claro": dict(fundo=PAPEL, texto=PRETO, acento=VERMELHO, sombra=PRETO),
    "escuro": dict(fundo=PRETO, texto=PAPEL, acento=MOSTARDA, sombra=VERMELHO),
}


def svg(w, h, body, pad=0):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{-pad} {-pad} {w + 2 * pad} {h + 2 * pad}" '
            f'width="{w + 2 * pad}" height="{h + 2 * pad}">\n{body}\n</svg>\n')


def path(cs, fill, extra=""):
    return f'<path d="{L.d(cs)}" fill="{fill}"{extra}/>'


def move(cs, dx, dy, k=1.0):
    return L.transform(cs, lambda x, y: (x * k + dx, y * k + dy))


def fit(cs, x0, y0, w=None, h=None, align="start"):
    """Escala/posiciona contornos para caber na largura w (ou altura h)."""
    a, b, c, d = L.bbox(cs)
    k = (w / (c - a)) if w else (h / (d - b))
    cs = L.transform(cs, lambda x, y: ((x - a) * k + x0, (y - b) * k + y0))
    return cs, (c - a) * k, (d - b) * k


# ---------------------------------------------------------------- 1. SELO
def selo(cx, cy, R, uid, modo):
    """Selo redondo de disco: rótulo vermelho, texto em anel, sol listrado no centro."""
    c = CORES[modo]
    top = L.on_arc("rubikmono", "MIRAGEM RECORDS", R * 0.135, cx, cy, R * 0.635, tracking=0.08)
    bot = L.on_arc("rubikmono", "IMAGINARY SOUNDS", R * 0.105, cx, cy, R * 0.66, bottom=True, tracking=0.12)
    rr = R * 0.47  # sol
    stripes = []
    # listras do pôr do sol: ficam mais grossas para baixo
    y = cy + rr * 0.08
    gap, i = rr * 0.07, 0
    while y < cy + rr:
        stripes.append(f'<rect x="{cx - rr}" y="{y:.2f}" width="{2 * rr}" height="{gap:.2f}" fill="{VERMELHO}"/>')
        y += gap + rr * (0.2 - i * 0.035)
        gap *= 1.45
        i += 1
    dot = lambda a: (cx + R * 0.705 * math.cos(math.radians(a)), cy + R * 0.705 * math.sin(math.radians(a)))
    (ax, ay), (bx, by) = dot(0), dot(180)
    ring = PAPEL
    return f'''<defs>
  <mask id="furo{uid}"><rect x="{cx - R - 1}" y="{cy - R - 1}" width="{2 * R + 2}" height="{2 * R + 2}" fill="#fff"/><circle cx="{cx}" cy="{cy}" r="{R * 0.055:.2f}" fill="#000"/></mask>
  <clipPath id="sol{uid}"><circle cx="{cx}" cy="{cy}" r="{rr:.2f}"/></clipPath>
</defs>
<g mask="url(#furo{uid})">
  <circle cx="{cx}" cy="{cy}" r="{R}" fill="{VERMELHO}"/>
  <circle cx="{cx}" cy="{cy}" r="{R * 0.925:.2f}" fill="none" stroke="{ring}" stroke-width="{R * 0.018:.2f}"/>
  <circle cx="{cx}" cy="{cy}" r="{R * 0.535:.2f}" fill="none" stroke="{ring}" stroke-width="{R * 0.012:.2f}"/>
  {path(top, ring)}
  {path(bot, ring)}
  <circle cx="{ax:.2f}" cy="{ay:.2f}" r="{R * 0.03:.2f}" fill="{MOSTARDA}"/>
  <circle cx="{bx:.2f}" cy="{by:.2f}" r="{R * 0.03:.2f}" fill="{MOSTARDA}"/>
  <g clip-path="url(#sol{uid})">
    <circle cx="{cx}" cy="{cy}" r="{rr:.2f}" fill="{MOSTARDA}"/>
    {"".join(stripes)}
  </g>
</g>'''


def nome_selo(modo):
    c = CORES[modo]
    m, mw, mh = fit(L.contours("fraunces900", "MIRAGEM", 100, tracking=0.02)[0], 0, 0, w=440)
    r, rw, rh = fit(L.contours("rubikmono", "RECORDS", 30, tracking=0.55)[0], 0, 0, w=300)
    return m, mw, mh, r, rw, rh, c


def v1(layout, modo):
    m, mw, mh, r, rw, rh, c = nome_selo(modo)
    if layout == "simbolo":
        return svg(200, 200, selo(100, 100, 100, "s", modo))
    if layout == "horizontal":
        S = 200
        gx = S + 44
        m = move(m, gx, 34)
        ry = 34 + mh + 26
        r = move(r, gx + (mw - rw) / 2, ry)
        rule_y = ry + rh / 2
        rules = (f'<rect x="{gx}" y="{rule_y - 2}" width="{(mw - rw) / 2 - 16}" height="4" fill="{c["acento"]}"/>'
                 f'<rect x="{gx + (mw + rw) / 2 + 16}" y="{rule_y - 2}" width="{(mw - rw) / 2 - 16}" height="4" fill="{c["acento"]}"/>')
        body = selo(100, 100, 100, "h", modo) + path(m, c["texto"]) + path(r, c["acento"]) + rules
        return svg(gx + mw, S, body, pad=12)
    # empilhada
    W = mw
    body = selo(W / 2, 100, 100, "e", modo)
    m2 = move(m, 0, 236)
    ry = 236 + mh + 24
    r2 = move(r, (W - rw) / 2, ry)
    rule_y = ry + rh / 2
    rules = (f'<rect x="0" y="{rule_y - 2}" width="{(W - rw) / 2 - 16}" height="4" fill="{c["acento"]}"/>'
             f'<rect x="{(W + rw) / 2 + 16}" y="{rule_y - 2}" width="{(W - rw) / 2 - 16}" height="4" fill="{c["acento"]}"/>')
    return svg(W, ry + rh, body + path(m2, c["texto"]) + path(r2, c["acento"]) + rules, pad=12)


# ------------------------------------------------------ 2. LETREIRO PSICODÉLICO
def miragem_psico(width, arco=0.32, onda=0.045):
    cs, _ = L.contours("shrikhand", "Miragem", 200, tracking=-0.01)

    def fn(x, y, u, v):
        x0, y0, x1, y1 = L.bbox(cs)
        h = y1 - y0
        base = y1
        # envelope: topo em arco (sobe no meio), base com onda suave de miragem
        lift = arco * h * math.sin(math.pi * u)
        wave = onda * h * math.sin(2 * math.pi * (u * 1.25 + 0.1))
        ny = base - (base - y) * (1 + lift / h * (1 - 0.0)) + wave
        return (x, ny)

    cs = L.warp(cs, fn)
    cs, w, h = fit(cs, 0, 0, w=width)
    return cs, w, h


def bloco_psico(cs, modo, off):
    c = CORES[modo]
    fill = VERMELHO if modo == "claro" else MOSTARDA
    sombra = PRETO if modo == "claro" else VERMELHO
    # sombra sólida em degraus (efeito "bloco" de serigrafia, sem gradiente)
    layers = "".join(path(move(cs, off * t / 6, off * t / 6), sombra) for t in range(6, 0, -1))
    return layers + path(cs, fill)


def simbolo_psico(cx, cy, R, modo, uid):
    m, _ = L.contours("shrikhand", "M", 200)

    def fn(x, y, u, v):
        # "M" inflado em lente (miragem): estica no centro
        k = 1 + 0.22 * math.sin(math.pi * u)
        x0, y0, x1, y1 = L.bbox(m)
        mid = (y0 + y1) / 2
        return (x, mid + (y - mid) * k)

    m = L.warp(m, fn)
    a, b, c_, d = L.bbox(m)
    k = (R * 1.02) / (c_ - a)
    m = L.transform(m, lambda x, y: ((x - (a + c_) / 2) * k + cx - R * 0.03, (y - (b + d) / 2) * k + cy - R * 0.03))
    rings = ""
    cores = [PRETO, MOSTARDA, PRETO, VERMELHO, PRETO]
    raios = [1.0, 0.93, 0.86, 0.80, 0.73]
    for col, rr in zip(cores, raios):
        rings += f'<circle cx="{cx}" cy="{cy}" r="{R * rr:.2f}" fill="{col}"/>'
    sh = "".join(path(move(m, R * 0.012 * t, R * 0.012 * t), VERMELHO) for t in range(6, 0, -1))
    return rings + sh + path(m, MOSTARDA)


def v2(layout, modo):
    c = CORES[modo]
    if layout == "simbolo":
        return svg(200, 200, simbolo_psico(100, 100, 100, modo, "s"))
    if layout == "horizontal":
        cs, w, h = miragem_psico(560, arco=0.18, onda=0.05)
        r, rw, rh = fit(L.contours("rubikmono", "RECORDS", 30, tracking=0.3)[0], 0, 0, h=22)
        # RECORDS na vertical? não: em pílula ao lado, alinhado à base
        px = w + 34
        pill_w, pill_h = rw + 40, rh + 26
        py = h - pill_h - 4
        body = (bloco_psico(cs, modo, 9)
                + f'<rect x="{px}" y="{py:.2f}" width="{pill_w:.2f}" height="{pill_h:.2f}" rx="{pill_h / 2:.2f}" fill="none" stroke="{c["texto"]}" stroke-width="4"/>'
                + path(move(r, px + 20, py + 13), c["texto"]))
        return svg(px + pill_w + 4, h + 10, body, pad=12)
    cs, w, h = miragem_psico(560, arco=0.34, onda=0.04)
    r, rw, rh = fit(L.contours("rubikmono", "RECORDS", 30, tracking=0.6)[0], 0, 0, h=26)
    ry = h + 40
    rx = (w - rw) / 2
    body = (bloco_psico(cs, modo, 10) + path(move(r, rx, ry), c["texto"])
            + f'<circle cx="{rx - 26}" cy="{ry + rh / 2}" r="6" fill="{c["acento"]}"/>'
            + f'<circle cx="{rx + rw + 26}" cy="{ry + rh / 2}" r="6" fill="{c["acento"]}"/>')
    return svg(w + 10, ry + rh, body, pad=12)


# ------------------------------------------------------ 3. SÍMBOLO + NOME
def icone_miragem(cx, cy, R, modo, uid):
    """Sol se pondo atrás de uma duna, com o reflexo da miragem embaixo."""
    sol_r = R * 0.46
    hy = cy + R * 0.12  # linha do horizonte
    sx, sy = cx, hy
    # duna: curva suave que corta o sol
    duna = (f'M{cx - R} {hy + R * 0.02:.2f} C{cx - R * 0.45:.2f} {hy - R * 0.2:.2f} {cx + R * 0.05:.2f} {hy - R * 0.2:.2f} '
            f'{cx + R * 0.35:.2f} {hy - R * 0.04:.2f} C{cx + R * 0.6:.2f} {hy + R * 0.06:.2f} {cx + R * 0.8:.2f} {hy:.2f} {cx + R} {hy:.2f} '
            f'L{cx + R} {cy + R} L{cx - R} {cy + R}Z')
    # reflexo: faixas horizontais que encurtam e afinam
    faixas = ""
    y = hy + R * 0.12
    for i, (wf, hf) in enumerate([(0.62, 0.075), (0.44, 0.06), (0.28, 0.045), (0.14, 0.035)]):
        faixas += f'<rect x="{cx - R * wf:.2f}" y="{y:.2f}" width="{2 * R * wf:.2f}" height="{R * hf:.2f}" rx="{R * hf / 2:.2f}" fill="{MOSTARDA}"/>'
        y += R * hf + R * 0.07
    borda = f'<circle cx="{cx}" cy="{cy}" r="{R * 0.985:.2f}" fill="none" stroke="{PAPEL}" stroke-width="{R * 0.03:.2f}"/>' if modo == "escuro" else ""
    return f'''<defs><clipPath id="ic{uid}"><circle cx="{cx}" cy="{cy}" r="{R}"/></clipPath></defs>
<g clip-path="url(#ic{uid})">
  <circle cx="{cx}" cy="{cy}" r="{R}" fill="{AZUL}"/>
  <circle cx="{sx}" cy="{sy - R * 0.02:.2f}" r="{sol_r:.2f}" fill="{MOSTARDA}"/>
  <path d="{duna}" fill="{VERMELHO}"/>
  {faixas}
</g>{borda}'''


def v3(layout, modo):
    c = CORES[modo]
    if layout == "simbolo":
        return svg(200, 200, icone_miragem(100, 100, 100, modo, "s"))
    m, mw, mh = fit(L.contours("dmserif", "Miragem", 200, tracking=-0.005)[0], 0, 0, h=128)
    r, rw, rh = fit(L.contours("rubikmono", "RECORDS", 30, tracking=0.62)[0], 0, 0, w=mw * 0.97)
    if layout == "horizontal":
        S = 210
        gx = S + 40
        body = icone_miragem(S / 2, S / 2, S / 2, modo, "h")
        top = (S - (mh + 22 + rh)) / 2
        body += path(move(m, gx, top), c["texto"]) + path(move(r, gx + (mw - rw) / 2, top + mh + 22), c["acento"])
        return svg(gx + mw, S, body, pad=12)
    S = 220
    W = mw
    body = icone_miragem(W / 2, S / 2, S / 2, modo, "e")
    body += path(move(m, 0, S + 34), c["texto"]) + path(move(r, (W - rw) / 2, S + 34 + mh + 22), c["acento"])
    return svg(W, S + 34 + mh + 22 + rh, body, pad=12)


VARIACOES = {
    "1-selo": ("Selo de gravadora", v1),
    "2-letreiro": ("Letreiro psicodélico", v2),
    "3-simbolo-nome": ("Símbolo + nome", v3),
}
LAYOUTS = ["horizontal", "empilhada", "simbolo"]


def main():
    for key, (_, fn) in VARIACOES.items():
        os.makedirs(os.path.join(OUT, key), exist_ok=True)
        for lay in LAYOUTS:
            for modo in CORES:
                with open(os.path.join(OUT, key, f"{lay}-{modo}.svg"), "w") as f:
                    f.write(fn(lay, modo))
    print("ok", OUT)


if __name__ == "__main__":
    main()
