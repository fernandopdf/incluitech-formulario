"""Etapa 2: logo final (proposta 3) + perfil, banner e marca d'água do YouTube.

Uso: NODE_PATH=<node_modules com @resvg/resvg-js> python3 gerar_final.py
A capa-modelo é gerada por capa-modelo.html (ver exportar_capa.js).
"""
import os
import random
import subprocess
import lettering as L
from gerar_logos import v3, icone_miragem, PAPEL, PRETO, VERMELHO, MOSTARDA, AZUL, svg, path, move, fit

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.join(AQUI, "..")
LOGO = os.path.join(RAIZ, "logo")
YT = os.path.join(RAIZ, "youtube")


def rasterizar(src, out, largura):
    subprocess.run(["node", os.path.join(AQUI, "rasterizar.js"), src, out, str(largura)], check=True)


def salvar(p, conteudo):
    with open(p, "w") as f:
        f.write(conteudo)


def interno(svg_txt):
    """Extrai viewBox e corpo de um SVG gerado, para aninhar em outra peça."""
    head, rest = svg_txt.split(">", 1)
    vb = head.split('viewBox="')[1].split('"')[0]
    return vb, rest.rsplit("</svg>", 1)[0]


def aninhar(svg_txt, x, y, w=None, h=None):
    vb = [float(v) for v in interno(svg_txt)[0].split()]
    if w is None:
        w = h * vb[2] / vb[3]
    if h is None:
        h = w * vb[3] / vb[2]
    corpo = interno(svg_txt)[1]
    return f'<svg x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" viewBox="{" ".join(map(str, vb))}">{corpo}</svg>', w, h


# textura de impressão: pontinhos finos e esparsos, sem borrar nada
def grao(uid, cor="#1C1611", forca=0.55, freq=0.85):
    return f'''<filter id="grao{uid}" x="0" y="0" width="100%" height="100%" color-interpolation-filters="sRGB">
  <feTurbulence type="fractalNoise" baseFrequency="{freq}" numOctaves="2" seed="11" stitchTiles="stitch"/>
  <feColorMatrix type="matrix" values="0 0 0 0 {int(cor[1:3],16)/255:.3f}  0 0 0 0 {int(cor[3:5],16)/255:.3f}  0 0 0 0 {int(cor[5:7],16)/255:.3f}  {forca * 2.2:.2f} 0 0 0 {-forca * 1.25:.2f}"/>
</filter>'''


# ------------------------------------------------------------------ LOGO
def logo():
    os.makedirs(LOGO, exist_ok=True)
    nomes = {"horizontal": "miragem-records-horizontal", "empilhada": "miragem-records-empilhada", "simbolo": "miragem-records-simbolo"}
    for lay, base in nomes.items():
        for modo, suf in [("claro", "fundo-claro"), ("escuro", "fundo-escuro")]:
            p = os.path.join(LOGO, f"{base}-{suf}.svg")
            salvar(p, v3(lay, modo))
            for w in (512, 1024, 2048):
                rasterizar(p, p.replace(".svg", f"-{w}.png"), w)


# ---------------------------------------------------------------- PERFIL
def perfil():
    W = 800
    body = f'''<defs>{grao("p", PRETO, 0.35)}</defs>
<rect width="{W}" height="{W}" fill="{PAPEL}"/>
{icone_miragem(W / 2, W / 2, 330, "claro", "perfil")}
<rect width="{W}" height="{W}" filter="url(#graop)" opacity="0.5"/>'''
    p = os.path.join(YT, "perfil-800x800.svg")
    salvar(p, svg(W, W, body))
    rasterizar(p, p.replace(".svg", ".png"), W)
    os.remove(p)


# ----------------------------------------------------------- MARCA D'ÁGUA
def marca():
    p = os.path.join(YT, "marca-dagua-150x150.svg")
    salvar(p, svg(150, 150, icone_miragem(75, 75, 74, "escuro", "md")))
    rasterizar(p, p.replace(".svg", ".png"), 150)
    os.remove(p)


# ---------------------------------------------------------------- BANNER
def dunas(pontos, base, cor):
    d = f"M{pontos[0][0]} {pontos[0][1]}"
    for i in range(1, len(pontos)):
        (x0, y0), (x1, y1) = pontos[i - 1], pontos[i]
        mx = (x0 + x1) / 2
        d += f" C{mx:.1f} {y0} {mx:.1f} {y1} {x1} {y1}"
    d += f" L{pontos[-1][0]} {base} L{pontos[0][0]} {base}Z"
    return f'<path d="{d}" fill="{cor}"/>'


def banner():
    W, H = 2560, 1440
    sx, sy, sw, sh = (W - 1546) / 2, (H - 423) / 2, 1546, 423  # área segura
    rnd = random.Random(4)
    estrelas = ""
    for _ in range(140):
        x, y = rnd.uniform(0, W), rnd.uniform(0, 900)
        if sx - 30 < x < sx + sw + 30 and sy - 30 < y < sy + sh:
            continue
        if (x - 2290) ** 2 + (y - 600) ** 2 < 260 ** 2:
            continue
        r = rnd.choice([2, 2, 2.5, 3, 4])
        estrelas += f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r}" fill="{PAPEL}" opacity="{rnd.choice([0.5, 0.7, 0.9])}"/>'

    # sol listrado à direita (fora da área segura)
    cx, cy, R = 2290, 600, 190
    listras = ""
    y, gap, i = cy + 10, 10, 0
    while y < cy + R:
        listras += f'<rect x="{cx - R}" y="{y:.1f}" width="{2 * R}" height="{gap:.1f}" fill="{AZUL}"/>'
        y += gap + 34 - i * 5
        gap *= 1.4
        i += 1
    sol = f'''<clipPath id="solb"><circle cx="{cx}" cy="{cy}" r="{R}"/></clipPath>
<g clip-path="url(#solb)"><circle cx="{cx}" cy="{cy}" r="{R}" fill="{MOSTARDA}"/>{listras}</g>'''
    # lua crescente à esquerda
    lua = (f'<circle cx="300" cy="640" r="74" fill="{MOSTARDA}"/>'
           f'<circle cx="328" cy="624" r="66" fill="{AZUL}"/>')

    camadas = (
        dunas([(0, 820), (260, 760), (560, 960), (1280, 990), (1990, 960), (2280, 790), (2560, 840)], H, "#7E2A1A")
        + dunas([(0, 900), (380, 860), (900, 1000), (1600, 985), (2200, 880), (2560, 930)], H, VERMELHO)
        + dunas([(0, 1060), (500, 1010), (1150, 1100), (1900, 1040), (2560, 1090)], H, PRETO)
    )
    # reflexo de miragem na parte de baixo (só aparece na TV)
    reflexo = ""
    y = 1200
    for wf, hf in [(900, 16), (640, 12), (400, 9), (200, 7)]:
        reflexo += f'<rect x="{W / 2 - wf / 2}" y="{y}" width="{wf}" height="{hf}" rx="{hf / 2}" fill="{MOSTARDA}" opacity="0.85"/>'
        y += hf + 26

    # conteúdo (dentro da área segura)
    logo_svg, lw, lh = aninhar(v3("horizontal", "escuro"), 0, 0, h=215)
    lx, ly = W / 2 - lw / 2, sy + 12
    logo_svg, _, _ = aninhar(v3("horizontal", "escuro"), lx, ly, h=215)
    frase, fw, fh = fit(L.contours("dmserifit", "Imaginary records from places that might have existed.", 100)[0], 0, 0, h=50)
    frase = move(frase, W / 2 - fw / 2, ly + lh + 34)
    sub, subw, subh = fit(L.contours("rubikmono", "A NEW CRATE EVERY WEEK", 40, tracking=0.32)[0], 0, 0, h=24)
    suby = ly + lh + 34 + fh + 26
    sub = move(sub, W / 2 - subw / 2, suby)
    assert suby + subh <= sy + sh, "texto fora da área segura"
    assert fw <= sw and lw <= sw

    body = f'''<defs>{grao("b", "#000000", 0.4)}</defs>
<rect width="{W}" height="{H}" fill="{AZUL}"/>
{estrelas}{sol}{lua}{camadas}{reflexo}
{logo_svg}
{path(frase, PAPEL)}
<rect x="{W / 2 - subw / 2 - 70}" y="{suby + subh / 2 - 2:.1f}" width="44" height="4" fill="{MOSTARDA}"/>
<rect x="{W / 2 + subw / 2 + 26}" y="{suby + subh / 2 - 2:.1f}" width="44" height="4" fill="{MOSTARDA}"/>
{path(sub, MOSTARDA)}
<rect width="{W}" height="{H}" filter="url(#graob)" opacity="0.45"/>'''
    p = os.path.join(YT, "banner-2560x1440.svg")
    salvar(p, svg(W, H, body))
    rasterizar(p, p.replace(".svg", ".png"), W)
    # versão de conferência com a área segura marcada
    guia = body + (f'<rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" fill="none" stroke="#00E5FF" stroke-width="4" stroke-dasharray="18 10"/>'
                   f'<rect x="0" y="{sy}" width="{W}" height="{sh}" fill="none" stroke="#FF00AA" stroke-width="3" stroke-dasharray="8 8"/>')
    pg = os.path.join(YT, "_banner-guia.svg")
    salvar(pg, svg(W, H, guia))
    rasterizar(pg, os.path.join(YT, "banner-conferencia-area-segura.png"), 1280)
    os.remove(pg)
    os.remove(p)


if __name__ == "__main__":
    os.makedirs(YT, exist_ok=True)
    logo()
    perfil()
    marca()
    banner()
    print("ok")
