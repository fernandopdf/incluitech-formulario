"""Monta logo/propostas/comparativo.html (as 3 variações lado a lado)."""
import os
from gerar_logos import OUT, VARIACOES, PAPEL, PRETO

NOTAS = {
    "1-selo": "Rótulo de disco vermelho com o nome em anel e um sol listrado no centro. "
              "Nome em serifa macia anos 70 (Fraunces Black).",
    "2-letreiro": "“Miragem” em lettering em arco, com base ondulada como miragem de calor e sombra em bloco. "
                  "Símbolo: “M” inflado dentro de anéis concêntricos.",
    "3-simbolo-nome": "Sol se pondo atrás da duna, com o reflexo da miragem em faixas. "
                      "Nome em serifa de capa de disco (DM Serif Display).",
}


def bloco(key, modo):
    bg = PAPEL if modo == "claro" else PRETO
    fg = PRETO if modo == "claro" else PAPEL
    return f'''<div class="painel" style="background:{bg};color:{fg}">
  <div class="tam"><img src="{key}/horizontal-{modo}.svg" style="height:110px"><span>horizontal</span></div>
  <div class="tam"><img src="{key}/empilhada-{modo}.svg" style="height:200px"><span>empilhada</span></div>
  <div class="tam"><img src="{key}/simbolo-{modo}.svg" style="height:140px"><span>símbolo</span></div>
  <div class="tam peq">
    <div><img src="{key}/simbolo-{modo}.svg" width="64" height="64"> <img src="{key}/simbolo-{modo}.svg" width="32" height="32"> <img src="{key}/simbolo-{modo}.svg" width="16" height="16"></div>
    <img src="{key}/horizontal-{modo}.svg" style="height:32px"><span>64 / 32 / 16 px · horizontal a 32 px</span></div>
</div>'''


def main():
    secs = ""
    for key, (nome, _) in VARIACOES.items():
        n = key.split("-")[0]
        secs += f'''<section>
  <h2><b>{n}</b> {nome}</h2><p>{NOTAS[key]}</p>
  {bloco(key, "claro")}
  {bloco(key, "escuro")}
</section>'''
    html = f'''<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Miragem Records · logos</title>
<style>
  body{{margin:0;background:#d8c9a6;color:{PRETO};font:15px/1.45 system-ui,sans-serif}}
  main{{max-width:1180px;margin:0 auto;padding:32px 16px 60px}}
  h1{{font-size:22px;margin:0 0 4px}} .sub{{margin:0 0 28px;opacity:.75}}
  section{{margin:0 0 44px}} h2{{font-size:19px;margin:0 0 2px}} h2 b{{display:inline-block;width:28px;height:28px;border-radius:50%;background:{PRETO};color:{PAPEL};text-align:center;line-height:28px;font-size:15px;margin-right:6px}}
  section p{{margin:0 0 12px;max-width:760px}}
  .painel{{display:flex;flex-wrap:wrap;align-items:flex-end;gap:36px;padding:28px;border-radius:10px;margin-bottom:10px}}
  .tam{{display:flex;flex-direction:column;align-items:flex-start;gap:8px}} .tam img{{max-width:100%}}
  .tam span{{font-size:12px;opacity:.65}} .peq div{{display:flex;align-items:center;gap:14px}}
</style></head><body><main>
<h1>Miragem Records · Etapa 1: três propostas de logo</h1>
<p class="sub">Cada proposta em fundo claro e escuro: horizontal, empilhada, símbolo e teste em tamanho pequeno.</p>
{secs}
</main></body></html>'''
    with open(os.path.join(OUT, "comparativo.html"), "w") as f:
        f.write(html)


if __name__ == "__main__":
    main()
