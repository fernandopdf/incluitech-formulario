// Uso: node rasterizar.js entrada.svg saida.png largura   (requer @resvg/resvg-js)
const { Resvg } = require('@resvg/resvg-js');
const fs = require('fs');
const [, , src, out, w] = process.argv;
const r = new Resvg(fs.readFileSync(src, 'utf8'), { fitTo: { mode: 'width', value: +w } });
fs.writeFileSync(out, r.render().asPng());
