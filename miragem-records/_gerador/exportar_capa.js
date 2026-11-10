// Exporta youtube/capa-modelo.png usando o próprio capa-modelo.html (mesmo código do botão "Baixar PNG").
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
(async () => {
  const yt = path.join(__dirname, '..', 'youtube');
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1600, height: 1000 } });
  await p.goto('file://' + path.join(yt, 'capa-modelo.html'));
  await p.waitForSelector('body[data-pronto="1"]');
  const fontes = await p.evaluate(() => ['Shrikhand', 'Rubik Mono One', 'DM Serif Display']
    .map(f => f + ': ' + document.fonts.check('40px "' + f + '"')));
  console.log(fontes.join(' | '));
  const url = await p.evaluate(() => gerarPNG());
  fs.writeFileSync(path.join(yt, 'capa-modelo-1280x720.png'), Buffer.from(url.split(',')[1], 'base64'));
  const svg = await p.evaluate(() => new XMLSerializer().serializeToString(document.getElementById('capa')));
  fs.writeFileSync(path.join(yt, 'capa-modelo.svg'), svg);
  await b.close();
})();
