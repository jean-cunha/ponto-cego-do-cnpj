const c=require('./core.js');
const assert=require('assert');
assert.deepStrictEqual(c.dvOficial("12ABC34501DE"),[3,5]);
assert(c.validoOficial("12ABC34501DE35")); assert(c.validoOficial("00000000000191")); assert(c.validoOficial("11222333000181"));
assert(c.validoOficial("12LBC34501DE35")); assert(c.validoOficial("126BC34501DE35")); assert(!c.validoOficial("12ABC34501DE34"));
assert.deepStrictEqual(c.A_RAIZ,[1,2,3,4,5,6,7,8].map(j=>{let v=1;for(let i=0;i<j;i++)v=v*10%191;return v;}));
// tRaiz por Horner == soma direta
for(let n=0;n<2000;n++){let r="";for(let i=0;i<8;i++)r+=c.ALFA[Math.floor(Math.random()*36)];
  let t=0;for(let j=0;j<8;j++)t+=c.val(r[j])*c.A_RAIZ[j];assert.strictEqual(c.tRaiz(r),t%191);}
function run(esq,alfa,estrito,tipo,N){
  const v=c.validador(esq,estrito); const typing = esq==="legado"?c.DIG:alfa; const r={escapou:0,consertado:0,errado:0,barrado:0};
  for(let i=0;i<N;i++){const cw=c.gerar(esq,alfa,estrito); assert(v(cw),cw); const y=c.errar(cw,tipo,typing); r[c.julgar(cw,y,v,typing)]++;}
  for(const k in r) r[k]=(100*r[k]/N).toFixed(3); return r;}
const A31=c.ALFA.split("").filter(x=>!"IOUQF".includes(x)).join("");
console.log("legado sub1   ",run("legado",c.ALFA,false,"sub1",60000));
console.log("oficial sub1  ",run("oficial",c.ALFA,false,"sub1",60000));
console.log("oficial31 sub1",run("oficial",A31,false,"sub1",60000));
console.log("raiz+ sub1    ",run("raiz+",c.ALFA,false,"sub1",40000));
console.log("raiz+E sub1   ",run("raiz+",c.ALFA,true,"sub1",40000));
console.log("raiz+E transp ",run("raiz+",c.ALFA,true,"transp",40000));
console.log("raiz+E sub2   ",run("raiz+",c.ALFA,true,"sub2",40000));
console.log("oficial transp",run("oficial",c.ALFA,false,"transp",40000));
console.log("legado transp ",run("legado",c.ALFA,false,"transp",40000));
console.log("exemplo:",c.gerar("raiz+",c.ALFA,true),c.mascara(c.gerar("raiz+",c.ALFA,true)));
