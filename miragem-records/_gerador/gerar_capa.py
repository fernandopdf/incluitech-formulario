"""Gera youtube/capa-modelo.html: modelo editável de thumbnail 1280x720.

Abra o HTML no navegador, troque os textos, envie a arte da noite e baixe o PNG.
"""
import base64
import os
from gerar_logos import v3, PAPEL, PRETO, VERMELHO, MOSTARDA, AZUL
from gerar_final import interno, YT, AQUI


def b64(nome):
    with open(os.path.join(AQUI, "fonts", nome), "rb") as f:
        return base64.b64encode(f.read()).decode()


def main():
    vb, corpo = interno(v3("horizontal", "claro"))
    fontes = f"""@font-face{{font-family:'Shrikhand';src:url(data:font/woff;base64,{b64('shrikhand-latin-400-normal.woff')}) format('woff')}}
@font-face{{font-family:'Rubik Mono One';src:url(data:font/woff;base64,{b64('rubik-mono-one-latin-400-normal.woff')}) format('woff')}}
@font-face{{font-family:'DM Serif Display';font-style:italic;src:url(data:font/woff;base64,{b64('dm-serif-display-latin-400-italic.woff')}) format('woff')}}"""
    html = TEMPLATE
    for k, v in dict(FONTES=fontes, LOGO_VB=vb, LOGO=corpo, PAPEL=PAPEL, PRETO=PRETO, VERMELHO=VERMELHO,
                     MOSTARDA=MOSTARDA, AZUL=AZUL).items():
        html = html.replace("%%" + k + "%%", v)
    with open(os.path.join(YT, "capa-modelo.html"), "w") as f:
        f.write(html)
    print("ok")


TEMPLATE = r"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Capa · Miragem Records</title>
<style>
%%FONTES%%
:root{--papel:%%PAPEL%%;--preto:%%PRETO%%;--verm:%%VERMELHO%%}
*{box-sizing:border-box}
body{margin:0;background:#d8c9a6;color:var(--preto);font:15px/1.4 system-ui,sans-serif}
main{display:grid;grid-template-columns:320px 1fr;gap:24px;max-width:1500px;margin:0 auto;padding:24px 16px}
@media(max-width:860px){main{grid-template-columns:1fr}}
form{display:flex;flex-direction:column;gap:12px}
h1{font-size:18px;margin:0 0 4px}
label{display:flex;flex-direction:column;gap:4px;font-size:13px;font-weight:600}
input[type=text]{font:15px system-ui;padding:8px 10px;border:2px solid var(--preto);border-radius:6px;background:var(--papel);color:var(--preto)}
.bts{display:flex;gap:8px;flex-wrap:wrap}
button{font:600 14px system-ui;padding:10px 14px;border:0;border-radius:6px;background:var(--preto);color:var(--papel);cursor:pointer}
button.sec{background:transparent;color:var(--preto);border:2px solid var(--preto)}
.dica{font-size:12px;opacity:.7;margin:0}
#palco svg{width:100%;height:auto;display:block;box-shadow:0 4px 18px rgba(0,0,0,.25)}
</style></head><body><main>
<form id="f" onsubmit="return false">
  <h1>Capa da noite</h1>
  <p class="dica">Troque os campos e baixe o PNG em 1280×720.</p>
  <label>Título, linha 1 <input type="text" id="t1" value="CARAVANA"></label>
  <label>Título, linha 2 (pode deixar vazio) <input type="text" id="t2" value="DE FUEGO"></label>
  <label>Subtítulo <input type="text" id="sub" value="Flamenco Reggaeton &amp; Desert Fire"></label>
  <label>Selo <input type="text" id="selo" value="1 HOUR MIX"></label>
  <label>Número da caixa <input type="text" id="cx" value="CRATE No. 01"></label>
  <label>Arte da noite (imagem) <input type="file" id="arte" accept="image/*"></label>
  <p class="dica">A arte ocupa a área da esquerda (700×720) e é cortada para preencher.</p>
  <div class="bts"><button id="png">Baixar PNG</button><button id="svgb" class="sec">Baixar SVG</button></div>
</form>
<div id="palco">
<svg id="capa" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 1280 720" width="1280" height="720">
<defs>
  <style>%%FONTES%%</style>
  <clipPath id="areaArte"><rect width="700" height="720"/></clipPath>
  <filter id="grao" x="0" y="0" width="100%" height="100%" color-interpolation-filters="sRGB">
    <feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="2" seed="11" stitchTiles="stitch"/>
    <feColorMatrix type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0.88 0 0 0 -0.5"/>
  </filter>
</defs>
<rect width="1280" height="720" fill="%%PAPEL%%"/>
<g clip-path="url(#areaArte)">
  <g id="placeholder">
    <rect width="700" height="720" fill="%%AZUL%%"/>
    <rect x="28" y="28" width="644" height="664" fill="none" stroke="%%PAPEL%%" stroke-width="3" stroke-dasharray="14 10" opacity=".6"/>
    <text x="350" y="350" text-anchor="middle" font-family="Rubik Mono One" font-size="40" fill="%%PAPEL%%">ARTE DA NOITE</text>
    <text x="350" y="398" text-anchor="middle" font-family="Rubik Mono One" font-size="18" fill="%%MOSTARDA%%">700 × 720 px</text>
  </g>
  <image id="imgArte" x="0" y="0" width="700" height="720" preserveAspectRatio="xMidYMid slice" style="display:none"/>
</g>
<rect x="700" y="0" width="10" height="720" fill="%%PRETO%%"/>
<svg x="748" y="40" height="58" width="300" viewBox="%%LOGO_VB%%" preserveAspectRatio="xMinYMin meet">%%LOGO%%</svg>
<g id="titulo"></g>
<text id="subt" font-family="DM Serif Display" font-style="italic" fill="%%PRETO%%"></text>
<text id="caixa" x="836" y="672" font-family="Rubik Mono One" font-size="17" letter-spacing="3" fill="%%VERMELHO%%"></text>
<g transform="translate(705 590) rotate(-12)">
  <circle r="96" fill="%%MOSTARDA%%"/>
  <circle r="84" fill="none" stroke="%%PRETO%%" stroke-width="3"/>
  <text id="selo1" y="-4" text-anchor="middle" font-family="Rubik Mono One" font-size="26" fill="%%PRETO%%"></text>
  <text id="selo2" y="34" text-anchor="middle" font-family="Rubik Mono One" font-size="34" fill="%%PRETO%%"></text>
</g>
<rect width="1280" height="720" filter="url(#grao)" opacity=".4" pointer-events="none"/>
</svg>
</div>
</main>
<script>
const NS = 'http://www.w3.org/2000/svg';
const $ = id => document.getElementById(id);
const X0 = 748, LARG = 488;            // coluna de texto
const TOPO = 120, BASE = 520;          // faixa vertical do título + subtítulo

function linhaTitulo(txt) {
  const g = document.createElementNS(NS, 'g');
  const mk = (fill, dx) => {
    const t = document.createElementNS(NS, 'text');
    t.setAttribute('font-family', 'Shrikhand'); t.setAttribute('fill', fill);
    t.setAttribute('x', dx); t.setAttribute('y', dx); t.textContent = txt; return t;
  };
  for (let i = 6; i >= 1; i--) g.appendChild(mk('%%PRETO%%', i));   // sombra em bloco
  g.appendChild(mk('%%VERMELHO%%', 0));
  return g;
}

function ajustar(g, maxSize) {          // mede e escala a linha para caber na coluna
  [...g.children].forEach(t => t.setAttribute('font-size', 100));
  const w = g.lastChild.getBBox().width || 1;
  const s = Math.min(maxSize, 100 * LARG / w);
  [...g.children].forEach((t, i, a) => {
    t.setAttribute('font-size', s.toFixed(1));
    const d = (a.length - 1 - i) * s / 100;                       // sombra proporcional
    t.setAttribute('x', d.toFixed(2)); t.setAttribute('y', d.toFixed(2));
  });
  return s;
}

function render() {
  const tg = $('titulo'); tg.innerHTML = '';
  const linhas = [$('t1').value, $('t2').value].map(s => s.trim()).filter(Boolean);
  let y = 0; const pos = [];
  for (const l of linhas) {
    const g = linhaTitulo(l); tg.appendChild(g);
    const s = ajustar(g, linhas.length > 1 ? 118 : 150);
    y += s * 0.98; pos.push([g, y]); y += s * 0.06;
  }
  const st = $('subt'); st.textContent = $('sub').value;
  st.setAttribute('font-size', 40);
  const sw = st.getBBox().width || 1;
  const ss = Math.min(40, 40 * LARG / sw); st.setAttribute('font-size', ss.toFixed(1));
  const alturaBloco = y + 22 + ss;
  const top = TOPO + Math.max(0, (BASE - TOPO - alturaBloco) / 2);
  pos.forEach(([g, yy]) => g.setAttribute('transform', `translate(${X0} ${(top + yy).toFixed(1)})`));
  st.setAttribute('x', X0); st.setAttribute('y', (top + y + 22 + ss * 0.8).toFixed(1));
  const p = $('selo').value.trim(), k = p.lastIndexOf(' ');
  $('selo1').textContent = k > 0 ? p.slice(0, k) : '';
  $('selo2').textContent = k > 0 ? p.slice(k + 1) : p;
  $('caixa').textContent = $('cx').value;
}

function svgTexto() { return new XMLSerializer().serializeToString($('capa')); }

window.gerarPNG = function () {
  return new Promise((ok, erro) => {
    const img = new Image();
    img.onload = () => {
      const c = document.createElement('canvas'); c.width = 1280; c.height = 720;
      c.getContext('2d').drawImage(img, 0, 0, 1280, 720);
      ok(c.toDataURL('image/png'));
    };
    img.onerror = erro;
    img.src = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svgTexto());
  });
};

function nomeArquivo(ext) {
  const base = [$('t1').value, $('t2').value].join(' ').trim().toLowerCase()
    .normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
  return 'capa-' + (base || 'miragem') + '.' + ext;
}
function baixar(href, nome) { const a = document.createElement('a'); a.href = href; a.download = nome; a.click(); }

$('png').onclick = async () => baixar(await gerarPNG(), nomeArquivo('png'));
$('svgb').onclick = () => baixar(URL.createObjectURL(new Blob([svgTexto()], { type: 'image/svg+xml' })), nomeArquivo('svg'));
$('arte').onchange = e => {
  const f = e.target.files[0]; if (!f) return;
  const r = new FileReader();
  r.onload = () => {
    const im = $('imgArte'); im.setAttribute('href', r.result); im.setAttributeNS('http://www.w3.org/1999/xlink', 'xlink:href', r.result);
    im.style.display = ''; $('placeholder').style.display = 'none';
  };
  r.readAsDataURL(f);
};
document.querySelectorAll('input[type=text]').forEach(i => i.addEventListener('input', render));
Promise.all(['Shrikhand', 'Rubik Mono One', 'italic 40px "DM Serif Display"'].map(f => document.fonts.load(f.includes('px') ? f : '100px "' + f + '"'))).then(() => { render(); document.body.dataset.pronto = '1'; });
</script>
</body></html>
"""

if __name__ == "__main__":
    main()
