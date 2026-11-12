"""Gera a capa (thumbnail 1280x720) de um capítulo da Miragem Records.

Exemplo:
  python3 gerar_capa.py --imagem arte/caravana-de-fuego.jpg \
      --titulo "CARAVANA" --titulo2 "DE FUEGO" --capitulo 1 --estilo A

Opções úteis:
  --foco X,Y,LARGURA   recorte 16:9 na imagem original (em pixels da imagem)
  --saida arquivo.png  padrão: saida/capa-<titulo>-<estilo>.png
Precisa de: Python 3, Pillow, numpy, fonttools  (pip install pillow numpy fonttools)
"""
import argparse
import math
import os
import re
import sys

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "..", "_gerador"))
import lettering as L  # noqa: E402

W, H = 1280, 720
SS = 3  # supersampling para bordas suaves
CREME = (242, 228, 196)
MOSTARDA = (217, 154, 43)
VERMELHO = (184, 50, 31)
SOMBRA = (34, 16, 10)
BRASA = (255, 128, 40)
LOGO = os.path.join(AQUI, "..", "logo", "miragem-records-horizontal-fundo-escuro-1024.png")


# ------------------------------------------------------------- imagem
def recortar(img, foco):
    x, y, w = foco
    h = w * 9 / 16
    x = max(0, min(x, img.width - w))
    y = max(0, min(y, img.height - h))
    return img.crop((round(x), round(y), round(x + w), round(y + h))).resize((W, H), Image.LANCZOS)


def tratar(img, grao=0.022, seed=7):
    """Cor de filme anos 70: mais quente, contraste leve, pretos levemente lavados, grão fino."""
    a = np.asarray(img).astype(np.float32) / 255
    lum = a @ np.array([0.299, 0.587, 0.114], dtype=np.float32)
    # aquece meios-tons e altas luzes (fogo e areia)
    peso = np.clip(lum * 1.4, 0, 1)[..., None]
    a = a * (1 + peso * np.array([0.07, 0.015, -0.10], dtype=np.float32))
    # curva em S suave
    s = a * a * (3 - 2 * a)
    a = np.clip(a * 0.62 + s * 0.38, 0, 1)
    # pretos levemente lavados, com tom marrom
    a = a * 0.955 + np.array([0.045, 0.030, 0.022], dtype=np.float32)
    # grão de película (monocromático, mais visível nos meios-tons)
    rng = np.random.default_rng(seed)
    n = rng.normal(0, 1, a.shape[:2]).astype(np.float32)
    n = np.asarray(Image.fromarray(((n * 0.25 + 0.5).clip(0, 1) * 255).astype(np.uint8))
                   .filter(ImageFilter.GaussianBlur(0.45))).astype(np.float32) / 255 - 0.5
    mid = (1 - np.abs(lum * 2 - 1))[..., None] * 0.7 + 0.3
    a = np.clip(a + n[..., None] * 4 * grao * mid, 0, 1)
    return Image.fromarray((a * 255 + 0.5).astype(np.uint8))


# ---------------------------------------------------------- lettering
def _flat(cs):
    """Contornos -> listas de pontos (curvas achatadas)."""
    out = []
    for c in cs:
        pts, last = [], None
        for cmd, ps in c:
            if cmd in ("M", "L"):
                pts.append(ps[0]); last = ps[0]
            elif cmd == "C":
                p0, (c1, c2, p3) = last, ps
                for i in range(1, 7):
                    t = i / 6; m = 1 - t
                    pts.append((m**3 * p0[0] + 3 * m * m * t * c1[0] + 3 * m * t * t * c2[0] + t**3 * p3[0],
                                m**3 * p0[1] + 3 * m * m * t * c1[1] + 3 * m * t * t * c2[1] + t**3 * p3[1]))
                last = p3
        if len(pts) > 2:
            out.append(pts)
    return out


def mascara(cs):
    """Máscara (L, tamanho W*SS x H*SS) preenchida com regra par-ímpar."""
    m = Image.new("L", (W * SS, H * SS), 0)
    for pts in _flat(cs):
        c = Image.new("L", m.size, 0)
        ImageDraw.Draw(c).polygon([(x * SS, y * SS) for x, y in pts], fill=255)
        m = ImageChops.logical_xor(m.convert("1"), c.convert("1")).convert("L")
    return m


def reduzir(m):
    return m.resize((W, H), Image.LANCZOS)


def colar(base, m, cor, alpha=1.0, dx=0, dy=0):
    camada = Image.new("RGBA", base.size, cor + (0,))
    if dx or dy:
        m = ImageChops.offset(m, round(dx), round(dy))
    camada.putalpha(m.point(lambda v: int(v * alpha)))
    base.alpha_composite(camada)


def caber(cs, x, y, largura=None, altura=None):
    a, b, c, d = L.bbox(cs)
    k = largura / (c - a) if largura else altura / (d - b)
    return L.transform(cs, lambda px, py: ((px - a) * k + x, (py - b) * k + y)), (c - a) * k, (d - b) * k


def texto(fonte, txt, tracking=0.0, arco=0.0, onda=0.0, inflar=0.0):
    cs, _ = L.contours(fonte, txt, 200, tracking=tracking)
    x0, y0, x1, y1 = L.bbox(cs)
    h = y1 - y0

    def fn(x, y, u, v):
        mid = (y0 + y1) / 2
        y = mid + (y - mid) * (1 + inflar * math.sin(math.pi * u))     # incha no meio
        y -= arco * h * math.sin(math.pi * u)                             # curva em arco
        y += onda * h * math.sin(2 * math.pi * u)                         # onda psicodélica
        return x, y

    return L.warp(cs, fn) if (arco or onda or inflar) else cs


# ------------------------------------------------------------- estilos
ESTILOS = {
    # A: letreiro gordo em arco, alinhado à esquerda, com brilho de fogueira
    "A": dict(fonte="shrikhand", tracking=0.0, l1=dict(arco=0.22, inflar=0.10), l2=dict(arco=0.12),
              x=40, y=22, larg1=730, larg2=480, alin2="centro", gap=0, cor2=CREME,
              brilho=True, bloco=7, selo="redondo"),
    # B: serifa macia anos 70, reta e grande, "DE FUEGO" deslocado à direita em mostarda
    "B": dict(fonte="fraunces900", tracking=0.01, l1=dict(inflar=0.0), l2=dict(),
              x=36, y=60, larg1=730, larg2=430, alin2="direita", gap=10, cor2=MOSTARDA,
              brilho=False, bloco=0, selo="pilula-topo"),
    # C: letras redondas com onda psicodélica, centralizado sobre o céu à esquerda
    "C": dict(fonte="bagel", tracking=0.02, l1=dict(onda=0.07, inflar=0.12), l2=dict(onda=-0.06),
              x=36, y=24, larg1=730, larg2=500, alin2="centro", gap=4, cor2=MOSTARDA,
              brilho=True, bloco=6, selo="pilula-base", contorno=VERMELHO),
}


def selo(base, tipo, cap, x, y, altura=17):
    """Selo 'CHAPTER N'."""
    d = ImageDraw.Draw(base)
    if tipo == "redondo":
        r = 54
        d.ellipse((x - r, y - r, x + r, y + r), fill=MOSTARDA + (255,))
        d.ellipse((x - r + 7, y - r + 7, x + r - 7, y + r - 7), outline=SOMBRA + (255,), width=3)
        t1, w1, h1 = caber(L.contours("rubikmono", "CHAPTER", 40, tracking=0.08)[0], 0, 0, largura=70)
        t2, w2, h2 = caber(L.contours("rubikmono", str(cap), 40)[0], 0, 0, altura=36)
        colar(base, reduzir(mascara(L.transform(t1, lambda a, b: (a + x - w1 / 2, b + y - 26)))), SOMBRA)
        colar(base, reduzir(mascara(L.transform(t2, lambda a, b: (a + x - w2 / 2, b + y - 6)))), SOMBRA)
        return
    t, w, h = caber(L.contours("rubikmono", f"CHAPTER {cap}", 40, tracking=0.18)[0], 0, 0, altura=altura)
    pw, ph = w + 36, h + 20
    d.rounded_rectangle((x, y, x + pw, y + ph), radius=ph / 2, fill=MOSTARDA + (255,))
    colar(base, reduzir(mascara(L.transform(t, lambda a, b: (a + x + 18, b + y + 10)))), SOMBRA)
    return pw, ph


def capa(imagem, titulo, titulo2, capitulo, estilo, foco):
    e = ESTILOS[estilo]
    foto = tratar(recortar(Image.open(imagem).convert("RGB"), foco)).convert("RGBA")

    l1, w1, h1 = caber(texto(e["fonte"], titulo, e["tracking"], **e["l1"]), e["x"], e["y"], largura=e["larg1"])
    linhas = [(l1, CREME)]
    fundo_y = e["y"] + h1
    if titulo2:
        l2 = texto(e["fonte"], titulo2, e["tracking"], **e["l2"])
        l2, w2, h2 = caber(l2, 0, 0, largura=e["larg2"])
        x2 = {"centro": e["x"] + (w1 - w2) / 2, "direita": e["x"] + w1 - w2}[e["alin2"]]
        l2 = L.transform(l2, lambda a, b: (a + x2, b + fundo_y + e["gap"]))
        linhas.append((l2, e["cor2"]))
        fundo_y += e["gap"] + h2

    mascaras = [(reduzir(mascara(cs)), cor) for cs, cor in linhas]
    if e.get("brilho"):
        for m, _ in mascaras:  # brilho quente de fogueira atrás das letras
            colar(foto, m.filter(ImageFilter.GaussianBlur(22)), BRASA, 0.55)
    for m, cor in mascaras:
        if e.get("contorno"):
            colar(foto, m.filter(ImageFilter.MaxFilter(9)), e["contorno"])
        if e["bloco"]:  # sombra em bloco, estilo serigrafia
            for t in range(e["bloco"], 0, -1):
                colar(foto, m.filter(ImageFilter.MaxFilter(3)), SOMBRA, 1, t, t)
        else:  # sombra escura macia
            colar(foto, m.filter(ImageFilter.GaussianBlur(10)), SOMBRA, 0.85, 4, 7)
            colar(foto, m, SOMBRA, 1, 3, 4)
        colar(foto, m, cor)

    if e["selo"] == "redondo":
        selo(foto, "redondo", capitulo, e["x"] + w1 - 70, fundo_y + 6)
    elif e["selo"] == "pilula-topo":
        selo(foto, "pilula", capitulo, e["x"] + 4, e["y"] - 44)
    else:  # embaixo da segunda linha, alinhado ao fim dela
        selo(foto, "pilula", capitulo, e["x"] + (w1 + w2) / 2 - 196, fundo_y + 8, altura=14)

    if os.path.exists(LOGO):  # logo pequena no canto superior direito
        lg = Image.open(LOGO).convert("RGBA")
        lg = lg.resize((round(lg.width * 40 / lg.height), 40), Image.LANCZOS)
        foto.alpha_composite(lg, (W - lg.width - 30, 26))
    return foto.convert("RGB")


def salvar_png(img, caminho, limite=2_000_000):
    img.save(caminho, optimize=True)
    if os.path.getsize(caminho) > limite:  # reduz cores com pontilhado fino se passar de 2 MB
        img.quantize(256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.FLOYDSTEINBERG).save(caminho, optimize=True)
    return os.path.getsize(caminho)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--imagem", required=True)
    p.add_argument("--titulo", required=True, help="linha 1 do título")
    p.add_argument("--titulo2", default="", help="linha 2 (opcional)")
    p.add_argument("--capitulo", default="1")
    p.add_argument("--estilo", default="A", choices=sorted(ESTILOS))
    p.add_argument("--foco", default="205,183,1050", help="X,Y,LARGURA do recorte 16:9")
    p.add_argument("--saida")
    a = p.parse_args()
    foco = [float(v) for v in a.foco.split(",")]
    img = capa(a.imagem, a.titulo.upper(), a.titulo2.upper(), a.capitulo, a.estilo, foco)
    slug = re.sub(r"[^a-z0-9]+", "-", f"{a.titulo} {a.titulo2}".lower()).strip("-")
    saida = a.saida or os.path.join(AQUI, "saida", f"capa-{slug}-{a.estilo}.png")
    os.makedirs(os.path.dirname(os.path.abspath(saida)), exist_ok=True)
    tam = salvar_png(img, saida)
    print(f"{saida}  ({tam / 1e6:.2f} MB)")


if __name__ == "__main__":
    main()
