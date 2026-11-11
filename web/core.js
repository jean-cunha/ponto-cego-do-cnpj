/* ===== núcleo: regra oficial do DV + regra da raiz (proposta) ===== */
const ALFA = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ";
const DIG = "0123456789";
const W1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2];
const W2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3];
const P_RAIZ = 191;                                   // módulo da regra da raiz
const A_RAIZ = [10, 100, 45, 68, 107, 115, 4, 40];    // 10^j mod 191, j = 1..8

const val = c => c.charCodeAt(0) - 48;                // regra oficial: ASCII - 48
const raio = c => val(c) % 11;                        // o que o DV enxerga
const camada = c => Math.floor(val(c) / 11);          // o que o DV não enxerga
const ehLetra = c => c >= "A" && c <= "Z";
const ehDig = c => c >= "0" && c <= "9";
const dobra = r => (r < 2 ? 0 : 11 - r);

function somas(p) {                                   // p: 12 caracteres
  let s1 = 0, s2 = 0;
  for (let i = 0; i < 12; i++) { const r = raio(p[i]); s1 += W1[i] * r; s2 += W2[i] * r; }
  return [s1 % 11, s2 % 11];
}
function dvOficial(p) {
  const [s1, s2] = somas(p);
  const d1 = dobra(s1), d2 = dobra((s2 + 2 * d1) % 11);
  return [d1, d2];
}
function formatoOk(s) {
  if (s.length !== 14) return false;
  for (let i = 0; i < 12; i++) if (ALFA.indexOf(s[i]) < 0) return false;
  return ehDig(s[12]) && ehDig(s[13]);
}
function validoOficial(s) {
  if (!formatoOk(s)) return false;
  const [d1, d2] = dvOficial(s);
  return +s[12] === d1 && +s[13] === d2;
}
function tRaiz(s) {                                   // T = soma 10^j * valor(c_j) mod 191
  let t = 0;
  for (let j = 7; j >= 0; j--) t = ((t + val(s[j])) * 10) % P_RAIZ;
  return t;
}
function nLetras(s, a, b) { let n = 0; for (let i = a; i < b; i++) if (ehLetra(s[i])) n++; return n; }

/* regra da raiz: raiz numérica = legado; raiz com letras exige >= 3 letras e T = 0;
   ordem numérica; estrito = "sem dobra" (equações exatas, resto 1 nunca emitido) */
function validoRaizMais(s, estrito) {
  if (!formatoOk(s)) return false;
  if (nLetras(s, 8, 12) > 0) return false;
  const L = nLetras(s, 0, 8);
  if (L === 0) return validoOficial(s);
  if (L < 3 || tRaiz(s) !== 0) return false;
  if (!estrito) return validoOficial(s);
  const [s1, s2] = somas(s), d1 = +s[12], d2 = +s[13];
  return (s1 + d1) % 11 === 0 && (s2 + 2 * d1 + d2) % 11 === 0;
}
function validoLegado(s) {
  for (let i = 0; i < 14; i++) if (!ehDig(s[i])) return false;
  return validoOficial(s);
}
function validador(nome, estrito) {
  if (nome === "legado") return validoLegado;
  if (nome === "oficial") return validoOficial;
  return s => validoRaizMais(s, estrito);
}

/* decodificador por força bruta: testa todos os vizinhos a 1 caractere;
   se nenhum servir, testa as 13 trocas de vizinhos */
function decodificar(s, valido, alfabeto) {
  const sub = [], troca = [];
  const a = s.split("");
  for (let j = 0; j < 14; j++) {
    const orig = a[j], pool = j < 12 ? alfabeto : DIG;
    for (let k = 0; k < pool.length; k++) {
      if (pool[k] === orig) continue;
      a[j] = pool[k];
      const z = a.join("");
      if (valido(z)) sub.push({ z, pos: j, de: orig, para: pool[k] });
    }
    a[j] = orig;
  }
  if (sub.length === 0) {
    for (let j = 0; j < 13; j++) {
      if (a[j] === a[j + 1]) continue;
      const t = a[j]; a[j] = a[j + 1]; a[j + 1] = t;
      const z = a.join("");
      if (valido(z)) troca.push({ z, pos: j, troca: true });
      a[j + 1] = a[j]; a[j] = t;
    }
  }
  return { sub, troca, cand: sub.length ? sub : troca };
}

/* ---------- geração e erros ---------- */
const rnd = n => Math.floor(Math.random() * n);
const sorteia = pool => pool[rnd(pool.length)];
function comDV(p) { const [d1, d2] = dvOficial(p); return p + d1 + d2; }
function temDobra(p) { const [s1, s2] = somas(p); const d1 = dobra(s1); return s1 === 1 || (s2 + 2 * d1) % 11 === 1; }

function gerar(esquema, alfabeto, estrito) {
  if (esquema === "legado") { let p = ""; for (let i = 0; i < 12; i++) p += sorteia(DIG); return comDV(p); }
  if (esquema === "oficial") { let p = ""; for (let i = 0; i < 12; i++) p += sorteia(alfabeto); return comDV(p); }
  for (;;) {                                           // raiz+: resolve o 8º caractere
    let r = ""; for (let i = 0; i < 7; i++) r += sorteia(ALFA);
    let t = 0; for (let j = 6; j >= 0; j--) t = (t + val(r[j]) * A_RAIZ[j]) % P_RAIZ;
    let x8 = -1;
    for (let k = 0; k < 36; k++) if ((t + val(ALFA[k]) * A_RAIZ[7]) % P_RAIZ === 0) { x8 = k; break; }
    if (x8 < 0) continue;
    r += ALFA[x8];
    if (nLetras(r, 0, 8) < 3) continue;
    for (let tent = 0; tent < 40; tent++) {
      let o = ""; for (let i = 0; i < 4; i++) o += sorteia(DIG);
      if (!estrito || !temDobra(r + o)) return comDV(r + o);
    }
  }
}
function outro(c, pool) { let b; do { b = sorteia(pool); } while (b === c); return b; }
/* tipo: 'sub1' 1 caractere trocado | 'transp' 2 vizinhos invertidos | 'sub2' 2 caracteres trocados */
function errar(s, tipo, alfabeto) {
  const a = s.split("");
  const troca1 = j => { a[j] = outro(a[j], j < 12 ? alfabeto : DIG); };
  if (tipo === "sub1") troca1(rnd(14));
  else if (tipo === "sub2") { const i = rnd(14); let j; do { j = rnd(14); } while (j === i); troca1(i); troca1(j); }
  else { let j, n = 0; do { j = rnd(13); n++; } while (a[j] === a[j + 1] && n < 60); const t = a[j]; a[j] = a[j + 1]; a[j + 1] = t; }
  return a.join("");
}
/* classifica um evento: 'escapou' | 'consertado' | 'errado' (conserto errado) | 'barrado' */
function julgar(certo, recebido, valido, alfabeto) {
  if (recebido === certo) return "igual";
  if (valido(recebido)) return "escapou";
  const d = decodificar(recebido, valido, alfabeto);
  if (d.cand.length === 1) return d.cand[0].z === certo ? "consertado" : "errado";
  return "barrado";
}
const mascara = s => s.slice(0, 2) + "." + s.slice(2, 5) + "." + s.slice(5, 8) + "/" + s.slice(8, 12) + "-" + s.slice(12);

if (typeof module !== "undefined") module.exports = { ALFA, DIG, W1, W2, P_RAIZ, A_RAIZ, val, raio, camada, dobra, somas, dvOficial, validoOficial, validoRaizMais, validoLegado, validador, tRaiz, decodificar, gerar, errar, julgar, mascara, temDobra, nLetras };
