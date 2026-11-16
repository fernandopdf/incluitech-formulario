"""Capa estilo pôster anos 70 (formas chapadas): rua colonial de Cusco à noite.

Uso: NODE_PATH=<node_modules com @resvg/resvg-js> python3 poster_cusco.py ["TÍTULO 1" "TÍTULO 2"]
"""
import math
import os
import random
import subprocess
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "..", "_gerador"))
import lettering as L  # noqa: E402
from gerar_logos import v3  # noqa: E402
from gerar_final import aninhar  # noqa: E402

W, H = 1280, 720
CEU1, CEU2 = "#142235", "#1F3A4D"
MONT1, MONT2 = "#2C4B5E", "#24394A"
CREME = "#F2E4C4"
MOSTARDA = "#D99A2B"
VERMELHO = "#B8321F"
MAGENTA = "#C8216E"
TURQUESA = "#1E8C8C"
PRETO = "#1C1611"
LUZ = "#FFC46B"
PELE = "#A0653F"

rnd = random.Random(21)
V = (600, 400)  # ponto de fuga


def poly(pts, fill, extra=""):
    return f'<polygon points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" fill="{fill}"{extra}/>'


def halo(x, y, r):
    return "".join(f'<circle cx="{x}" cy="{y}" r="{r * k:.0f}" fill="{LUZ}" opacity="{a}"/>'
                   for k, a in [(.75, .06), (.5, .09), (.3, .16)])


def ceu():
    s = f'<rect width="{W}" height="{H}" fill="{CEU2}"/>'
    for _ in range(90):
        x, y = rnd.uniform(0, W), rnd.uniform(0, 330)
        s += f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{rnd.choice([1.2, 1.5, 2, 2.5])}" fill="{CREME}" opacity="{rnd.choice([.4, .6, .85])}"/>'
    # lua cheia atrás das montanhas, à direita
    s += f'<circle cx="1010" cy="130" r="40" fill="{MOSTARDA}" opacity=".9"/>'
    return s


def montanhas():
    def cume(pts, base, cor):
        d = f"M0 {base} " + " ".join(f"L{x} {y}" for x, y in pts) + f" L{W} {base} Z"
        return f'<path d="{d}" fill="{cor}"/>'
    return (cume([(0, 330), (140, 270), (260, 320), (420, 250), (560, 330), (700, 280), (860, 340), (1000, 265), (1140, 320), (1280, 290)], 470, MONT1)
            + cume([(0, 370), (180, 330), (330, 380), (520, 340), (690, 385), (880, 350), (1060, 390), (1280, 345)], 470, MONT2))


def igreja():
    """Torre colonial genérica, iluminada de leve, no fundo da rua."""
    cor, sombra = "#C98A45", "#9C6533"
    s = poly([(560, 470), (560, 330), (640, 330), (640, 470)], cor)
    s += poly([(552, 330), (648, 330), (640, 318), (560, 318)], sombra)
    s += poly([(572, 318), (572, 262), (628, 262), (628, 318)], cor)
    s += f'<path d="M584 318 V292 a16 16 0 0 1 32 0 V318Z" fill="{PRETO}"/>'   # arco do sino
    s += f'<path d="M574 262 Q600 222 626 262Z" fill="{sombra}"/>'           # cúpula
    s += f'<rect x="598" y="206" width="4" height="22" fill="{sombra}"/><rect x="592" y="212" width="16" height="4" fill="{sombra}"/>'
    s += f'<path d="M585 470 V420 a15 15 0 0 1 30 0 V470Z" fill="{PRETO}" opacity=".85"/>'
    s += f'<rect x="572" y="345" width="12" height="20" rx="6" fill="{LUZ}"/><rect x="616" y="345" width="12" height="20" rx="6" fill="{LUZ}"/>'
    return halo(600, 360, 120) + s


def muro_inca():
    """Muro de pedras poligonais encaixadas, em perspectiva (lado esquerdo)."""
    def P(u, v):
        x = 470 * u
        yb = 720 - 250 * u
        yt = 230 + 130 * u
        return (x, yb + (yt - yb) * v)
    s = poly([P(0, 0), P(1, 0), P(1, 1), P(0, 1)], "#2E1F17")  # juntas escuras
    linhas = 7
    cores = ["#8A5A3B", "#9A6842", "#7A4E33", "#A47048", "#87583A"]
    for i in range(linhas):
        v0, v1 = i / linhas, (i + 1) / linhas
        u = 0
        while u < 1:
            du = rnd.uniform(0.08, 0.16) * (1 - u * 0.5)
            u1 = min(1, u + du)
            g = 0.006
            j = lambda: rnd.uniform(-0.012, 0.012)
            pts = [P(u + g, v0 + g + j()), P((u + u1) / 2, v0 + g + j() * 0.5), P(u1 - g, v0 + g + j()),
                   P(u1 - g + j() * .3, (v0 + v1) / 2), P(u1 - g, v1 - g + j()), P(u + g, v1 - g + j()),
                   P(u + g + j() * .3, (v0 + v1) / 2)]
            luz = max(0, 1 - abs(u - 0.42) * 2.2) * max(0, 1 - abs(v0 - 0.55) * 1.6)
            s += poly(pts, rnd.choice(cores), f' opacity="{0.55 + 0.45 * luz:.2f}"')
            u = u1
    return s


def predio_direita():
    """Casarão colonial com sacada de madeira e porta com degraus."""
    def P(u, v):
        x = 760 + 520 * u
        yb = 470 + 250 * u
        yt = 345 - 165 * u
        return (x, yb + (yt - yb) * v)
    s = poly([P(0, 0), P(1, 0), P(1, 1), P(0, 1)], "#A88F6A")
    s += poly([P(0, 0), P(1, 0), P(1, .28), P(0, .28)], "#6E5A48")          # base de pedra
    s += poly([P(0, .98), P(1, .98), P(1, 1.06), P(0, 1.06)], "#7A3B22")      # beiral de telhas
    # janelas iluminadas
    for u in (0.12, 0.32):
        s += poly([P(u, .45), P(u + .07, .45), P(u + .07, .7), P(u, .7)], LUZ, ' opacity=".9"')
    # sacada de madeira (marca de Cusco)
    s += poly([P(.45, .5), P(.95, .5), P(.95, .8), P(.45, .8)], "#3B2A1E")
    for k in range(11):
        u = .47 + k * .045
        s += poly([P(u, .52), P(u + .018, .52), P(u + .018, .74), P(u, .74)], "#5C4330")
    s += poly([P(.43, .8), P(.97, .8), P(.97, .84), P(.43, .84)], "#2A1D14")
    # porta escura atrás do músico
    s += poly([P(.24, .02), P(.4, .02), P(.4, .42), P(.24, .42)], "#2A1D14")
    return s


def rua():
    s = poly([(0, 720), (470, 470), (760, 470), (1280, 720)], "#2A211D")
    # fiadas de paralelepípedo convergindo para o fundo
    for k in range(-14, 15):
        x = 615 + k * 95
        s += f'<line x1="{V[0] + k * 9}" y1="470" x2="{x}" y2="720" stroke="#3A2E28" stroke-width="2"/>'
    y = 476
    gap = 6
    while y < 720:
        s += f'<line x1="0" y1="{y:.0f}" x2="{W}" y2="{y:.0f}" stroke="#3A2E28" stroke-width="2"/>'
        y += gap
        gap *= 1.28
    # reflexo dos postes na pedra molhada (traços quebrados)
    for (x, y0, larg) in [(205, 520, 110), (905, 500, 95), (600, 480, 40)]:
        y = y0
        for i in range(9):
            w = larg * (1 - i * 0.07) * rnd.uniform(.7, 1.1)
            h = 3 + i * 0.9
            s += f'<rect x="{x - w / 2 + rnd.uniform(-5, 5):.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{h / 2:.1f}" fill="{LUZ}" opacity="{0.55 - i * .045:.2f}"/>'
            y += h + 6 + i * 2
    return s.replace(f'<line x1="0"', '<line clip-path="url(#chao)" x1="0"').replace('<line x1=', '<line clip-path="url(#chao)" x1=')


def postes():
    s = ""
    for x, y, lado in [(205, 400, 1), (905, 290, -1)]:
        s += halo(x, y + 18, 150)
        s += f'<path d="M{x - 34 * lado} {y - 8} H{x} V{y + 2}" stroke="{PRETO}" stroke-width="5" fill="none"/>'
        s += f'<path d="M{x - 14} {y + 4} H{x + 14} L{x + 10} {y + 34} H{x - 10}Z" fill="{LUZ}" stroke="{PRETO}" stroke-width="4"/>'
        s += f'<path d="M{x - 18} {y + 4} L{x} {y - 6} L{x + 18} {y + 4}Z" fill="{PRETO}"/>'
    return s


def degraus():
    s = ""
    for i, (y, x0, x1) in enumerate([(560, 840, 1080), (592, 825, 1100), (624, 810, 1120)]):
        s += poly([(x0, y), (x1, y), (x1 + 6, y + 32), (x0 - 6, y + 32)], ["#6E5A48", "#7C6650", "#665240"][i])
        s += f'<rect x="{x0}" y="{y}" width="{x1 - x0}" height="5" fill="#9C8466"/>'
    return s


def musico():
    """Músico sentado, de poncho listrado e chullo, tocando charango."""
    cx = 960
    s = ""
    # pernas e pés
    s += poly([(915, 560), (960, 560), (950, 626), (925, 626)], "#2A1E18")
    s += poly([(965, 560), (1010, 560), (1000, 626), (975, 626)], "#2A1E18")
    s += f'<ellipse cx="932" cy="628" rx="18" ry="7" fill="{PRETO}"/><ellipse cx="992" cy="628" rx="18" ry="7" fill="{PRETO}"/>'
    # poncho: trapézio com faixas
    pon = [(cx - 34, 452), (cx + 34, 452), (cx + 78, 566), (cx - 78, 566)]
    s += f'<clipPath id="poncho"><polygon points="{" ".join(f"{x},{y}" for x, y in pon)}"/></clipPath>'
    faixas = [(452, VERMELHO), (474, MOSTARDA), (484, VERMELHO), (500, MAGENTA), (512, TURQUESA), (522, VERMELHO),
              (538, MOSTARDA), (546, MAGENTA), (558, VERMELHO)]
    g = ""
    for i, (y, cor) in enumerate(faixas):
        y2 = faixas[i + 1][0] if i + 1 < len(faixas) else 570
        g += f'<rect x="{cx - 90}" y="{y}" width="180" height="{y2 - y}" fill="{cor}"/>'
    # zigue-zague andino
    zz = " ".join(f"{cx - 90 + k * 12},{512 if k % 2 else 504}" for k in range(16))
    g += f'<polyline points="{zz}" fill="none" stroke="{CREME}" stroke-width="3"/>'
    zz = " ".join(f"{cx - 90 + k * 10},{532 if k % 2 else 526}" for k in range(19))
    g += f'<polyline points="{zz}" fill="none" stroke="{PRETO}" stroke-width="2.5"/>'
    s += f'<g clip-path="url(#poncho)">{g}</g>'
    # cabeça e chullo
    s += f'<rect x="{cx - 9}" y="434" width="18" height="20" fill="{PELE}"/>'
    s += f'<ellipse cx="{cx}" cy="428" rx="20" ry="23" fill="{PELE}"/>'
    s += f'<path d="M{cx - 9} 431 h6 M{cx + 3} 431 h6" stroke="{PRETO}" stroke-width="2.5" stroke-linecap="round"/>'
    s += f'<path d="M{cx - 7} 442 q7 4 14 0" stroke="#5A2E1A" stroke-width="2" fill="none" stroke-linecap="round"/>'
    s += f'<path d="M{cx - 23} 418 Q{cx - 24} 382 {cx} 374 Q{cx + 24} 382 {cx + 23} 418Z" fill="{VERMELHO}"/>'
    s += f'<rect x="{cx - 23}" y="398" width="46" height="6" fill="{MOSTARDA}"/><rect x="{cx - 23}" y="408" width="46" height="4" fill="{TURQUESA}"/>'
    s += f'<path d="M{cx - 23} 414 L{cx - 26} 440 L{cx - 18} 440 L{cx - 16} 418Z" fill="{VERMELHO}"/>'
    s += f'<path d="M{cx + 23} 414 L{cx + 26} 440 L{cx + 18} 440 L{cx + 16} 418Z" fill="{VERMELHO}"/>'
    s += f'<line x1="{cx - 22}" y1="440" x2="{cx - 22}" y2="456" stroke="{MOSTARDA}" stroke-width="2"/><line x1="{cx + 22}" y1="440" x2="{cx + 22}" y2="456" stroke="{MOSTARDA}" stroke-width="2"/>'
    s += f'<circle cx="{cx}" cy="371" r="6" fill="{MOSTARDA}"/>'
    # charango: corpo em gota + braço, inclinado
    s += f'''<g transform="translate({cx + 6} 520) rotate(-22)">
  <rect x="-108" y="-5" width="80" height="10" rx="3" fill="#5A3A22"/>
  <rect x="-124" y="-8" width="20" height="16" rx="3" fill="#3E2716"/>
  <path d="M-36 0 C-36 -26 6 -30 26 -18 C40 -10 40 10 26 18 C6 30 -36 26 -36 0Z" fill="#C07A3A"/>
  <circle cx="-4" cy="0" r="7" fill="{PRETO}"/>
  <line x1="-120" y1="-2" x2="28" y2="-2" stroke="{CREME}" stroke-width=".8"/><line x1="-120" y1="2" x2="28" y2="2" stroke="{CREME}" stroke-width=".8"/>
</g>'''
    s += f'<circle cx="{cx - 72}" cy="500" r="8" fill="{PELE}"/><circle cx="{cx + 12}" cy="530" r="8" fill="{PELE}"/>'
    return s


def mulher():
    """Mulher de manta magenta passando, levemente desfocada."""
    x = 300
    s = f'<g filter="url(#desfoque)">'
    s += f'<path d="M{x - 52} 640 Q{x} 520 {x + 52} 640Z" fill="{TURQUESA}"/>'                     # pollera
    s += f'<rect x="{x - 50}" y="618" width="100" height="10" fill="{MOSTARDA}"/>'
    s += f'<rect x="{x - 18}" y="640" width="10" height="16" fill="{PRETO}"/><rect x="{x + 8}" y="636" width="10" height="18" fill="{PRETO}"/>'
    s += f'<path d="M{x - 30} 470 L{x + 30} 470 L{x + 46} 580 L{x - 46} 580Z" fill="{MAGENTA}"/>'     # manta
    s += f'<path d="M{x - 30} 470 L{x + 30} 470 L{x} 560Z" fill="#A3185A"/>'
    s += f'<rect x="{x - 46}" y="572" width="92" height="8" fill="{MOSTARDA}"/>'
    s += f'<circle cx="{x}" cy="448" r="18" fill="{PELE}"/>'
    s += f'<path d="M{x - 14} 452 Q{x - 22} 482 {x - 16} 500" stroke="{PRETO}" stroke-width="7" fill="none"/>'  # trança
    s += f'<rect x="{x - 26}" y="428" width="52" height="7" rx="3" fill="{PRETO}"/><path d="M{x - 15} 430 Q{x} 404 {x + 15} 430Z" fill="{PRETO}"/>'
    return s + "</g>"


def titulo(t1, t2):
    def caber(cs, x, y, w):
        a, b, c, d = L.bbox(cs)
        k = w / (c - a)
        return L.transform(cs, lambda px, py: ((px - a) * k + x, (py - b) * k + y)), (c - a) * k, (d - b) * k

    def arco(cs, amt):
        x0, y0, x1, y1 = L.bbox(cs)
        return L.warp(cs, lambda x, y, u, v: (x, y - amt * (y1 - y0) * math.sin(math.pi * u)))

    l1, w1, h1 = caber(arco(L.contours("shrikhand", t1, 200)[0], .16), 40, 26, 560)
    out = [(l1, CREME)]
    if t2:
        l2, w2, h2 = caber(arco(L.contours("shrikhand", t2, 200)[0], .08), 0, 0, 470)
        l2 = L.transform(l2, lambda a, b: (a + 40 + (w1 - w2) / 2, b + 26 + h1 - 2))
        out.append((l2, MOSTARDA))
    s = ""
    for cs, _ in out:
        s += f'<path d="{L.d(cs)}" fill="{LUZ}" opacity=".55" filter="url(#brilho)"/>'
    for cs, cor in out:
        d = L.d(cs)
        s += "".join(f'<path d="{d}" fill="#22100A" transform="translate({t} {t})"/>' for t in range(7, 0, -1))
        s += f'<path d="{d}" fill="{cor}"/>'
    return s


def main():
    t1 = sys.argv[1] if len(sys.argv) > 1 else "NOCHE EN"
    t2 = sys.argv[2] if len(sys.argv) > 2 else "CUSCO"
    logo, _, _ = aninhar(v3("horizontal", "escuro"), 0, 0, h=40)
    lw = float(logo.split('width="')[1].split('"')[0])
    logo, _, _ = aninhar(v3("horizontal", "escuro"), W - lw - 30, 26, h=40)
    corpo = f'''<defs>
  <clipPath id="chao"><polygon points="0,720 470,470 760,470 1280,720"/></clipPath>
  <filter id="desfoque" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="1.6"/></filter>
  <filter id="brilho" x="-20%" y="-40%" width="140%" height="180%"><feGaussianBlur stdDeviation="16"/></filter>
  <filter id="grao" x="0" y="0" width="100%" height="100%" color-interpolation-filters="sRGB">
    <feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="2" seed="5" stitchTiles="stitch"/>
    <feColorMatrix type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0.9 0 0 0 -0.5"/>
  </filter>
</defs>
{ceu()}{montanhas()}{igreja()}{rua()}{muro_inca()}{predio_direita()}{postes()}{degraus()}{mulher()}{musico()}
{titulo(t1, t2)}
{logo}
<rect width="{W}" height="{H}" filter="url(#grao)" opacity=".35"/>'''
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">{corpo}</svg>'
    os.makedirs(os.path.join(AQUI, "saida"), exist_ok=True)
    p = os.path.join(AQUI, "saida", "capa-cusco-poster.svg")
    open(p, "w").write(svg)
    subprocess.run(["node", os.path.join(AQUI, "..", "_gerador", "rasterizar.js"), p, p.replace(".svg", ".png"), str(W)], check=True)
    print(p.replace(".svg", ".png"))


if __name__ == "__main__":
    main()
