"""Monta saida/comparativo.png: as variações em 640x360 e em 320x180 (tamanho de feed)."""
import sys
from PIL import Image, ImageDraw, ImageFont

def main(arquivos, rotulos, saida):
    def F(s):
        for nome in ("DejaVuSans.ttf", "arial.ttf", "Arial.ttf", "LiberationSans-Regular.ttf"):
            try:
                return ImageFont.truetype(nome, s)
            except OSError:
                pass
        return ImageFont.load_default(size=s)
    n = len(arquivos)
    W = 40 + n * 680
    img = Image.new("RGB", (W, 740), (15, 15, 15))  # fundo escuro, como o YouTube
    d = ImageDraw.Draw(img)
    d.text((40, 24), "Caravana de Fuego · 3 variações de capa", font=F(28), fill=(240, 240, 240))
    for i, (arq, rot) in enumerate(zip(arquivos, rotulos)):
        x = 40 + i * 680
        cap = Image.open(arq).convert("RGB")
        d.text((x, 76), rot, font=F(24), fill=(242, 228, 196))
        img.paste(cap.resize((640, 360), Image.LANCZOS), (x, 112))
        # tamanho de feed no celular, com a duração no canto como o YouTube mostra
        p = cap.resize((320, 180), Image.LANCZOS)
        dp = ImageDraw.Draw(p)
        dp.rounded_rectangle((262, 154, 314, 174), radius=4, fill=(0, 0, 0))
        dp.text((267, 157), "1:02:15", font=F(13), fill=(255, 255, 255))
        img.paste(p, (x, 500))
        d.text((x, 690), "320 × 180 (feed)", font=F(16), fill=(170, 170, 170))
        d.text((x, 712), "Como deve aparecer no feed do celular", font=F(16), fill=(120, 120, 120))
    img.save(saida, optimize=True)

if __name__ == "__main__":
    main(sys.argv[1:4], ["A · arco gordo + brilho de fogueira", "B · serifa anos 70, reta", "C · letras redondas em onda"], "saida/comparativo.png")
