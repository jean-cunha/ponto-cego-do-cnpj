"""
Simulador v2 — representação completa de 14 posições.
Decodificador por força bruta: testa TODOS os vizinhos (substituição de 1
caractere e, opcionalmente, troca de 2 vizinhos). Nenhum atalho algébrico:
o resultado depende apenas da função `valid`.

Esquemas:
  'legado'   mundo antigo: só dígitos, DV oficial
  'oficial'  regra em vigor: 36 símbolos no payload, DV oficial (ASCII-48, mod 11)
  'raiz+'    oficial + REGRA DA RAIZ (proposta):
               raiz toda numérica  -> tratada como legado
               raiz com letras     -> exige >= 3 letras e T(raiz) ≡ 0 (mod p)
               ordem               -> numérica
             strict=True acrescenta "sem dobra": exige as equações exatas
               S1 + DV1 ≡ 0 e S2 + 2·DV1 + DV2 ≡ 0 (mod 11)  (resto 1 nunca é emitido)
"""
import numpy as np
from cnpj_core import ALPHA36, W1, W2

X   = np.array([ord(c) - 48 for c in ALPHA36])
RHO = X % 11
LET = (np.arange(36) >= 10).astype(np.int64)
W1a = np.array(W1); W2a = np.array(W2)
F   = np.array([0, 0, 9, 8, 7, 6, 5, 4, 3, 2, 1])

P_RAIZ = 191
A_RAIZ = [pow(10, j, P_RAIZ) for j in range(1, 9)]     # [10,100,45,68,107,115,4,40]


class Scheme:
    def __init__(self, kind, p=P_RAIZ, a=A_RAIZ, minlet=3, strict=False, alphabet=None):
        self.kind = kind; self.p = p; self.a = np.array(a); self.minlet = minlet
        self.strict = strict
        self.alpha = np.arange(36) if alphabet is None else np.array(alphabet)
        self.typing = np.arange(10) if kind == 'legado' else self.alpha

    # ---- validade de strings de 14 posições (índices 0..35) ----
    def valid(self, Y):
        P = Y[:, :12]; d1 = Y[:, 12]; d2 = Y[:, 13]
        fmt = (d1 < 10) & (d2 < 10)
        d1c = np.minimum(d1, 9); d2c = np.minimum(d2, 9)
        S1 = (RHO[P] * W1a).sum(1) % 11
        S2 = (RHO[P] * W2a).sum(1) % 11
        if self.kind == 'raiz+' and self.strict:
            off_strict = ((S1 + d1c) % 11 == 0) & ((S2 + 2 * d1c + d2c) % 11 == 0)
        off = (F[S1] == d1c) & (F[(S2 + 2 * d1c) % 11] == d2c)
        L = LET[P[:, :8]].sum(1); O = LET[P[:, 8:]].sum(1)
        if self.kind == 'oficial':
            return fmt & off
        if self.kind == 'legado':
            return fmt & off & (L == 0) & (O == 0)
        T = (X[P[:, :8]] * self.a).sum(1) % self.p
        new_ok = (L >= self.minlet) & (T == 0) & (off_strict if self.strict else off)
        return fmt & (O == 0) & (((L == 0) & off) | new_ok)

    def with_dv(self, P):
        S1 = (RHO[P] * W1a).sum(1) % 11; d1 = F[S1]
        S2 = ((RHO[P] * W2a).sum(1) + 2 * d1) % 11; d2 = F[S2]
        fold = (S1 == 1) | (S2 == 1)
        return np.concatenate([P, d1[:, None], d2[:, None]], 1), fold

    def sample(self, n, rng, mode):
        """'num': 12 dígitos | 'alnum': 12 alfanuméricos | 'novo': raiz na regra + ordem numérica"""
        out = []; got = 0
        while got < n:
            if mode == 'num':
                P = rng.integers(0, 10, (n, 12))
            elif mode == 'alnum':
                P = self.alpha[rng.integers(0, len(self.alpha), (n, 12))]
            else:
                R = self.alpha[rng.integers(0, len(self.alpha), (1500000, 8), dtype=np.int8)].astype(np.int64)
                ok = (LET[R].sum(1) >= self.minlet) & ((X[R] * self.a).sum(1) % self.p == 0)
                R = R[ok]
                P = np.concatenate([R, rng.integers(0, 10, (len(R), 4))], 1)
            Y, fold = self.with_dv(P)
            if self.kind == 'raiz+' and self.strict and mode == 'novo':
                Y = Y[~fold]
            out.append(Y); got += len(Y)
        return np.concatenate(out)[:n]

    # ---- decodificador por força bruta ----
    def count_neighbors(self, Y, swaps=True):
        n = len(Y); sub = np.zeros(n, dtype=np.int64); sw = np.zeros(n, dtype=np.int64)
        Z = Y.copy()
        for j in range(14):
            col = Y[:, j]
            for b in (self.typing if j < 12 else range(10)):
                m = col != b
                Z[:, j] = b
                sub += m & self.valid(Z)
            Z[:, j] = col
        if swaps:
            for j in range(13):
                m = Y[:, j] != Y[:, j + 1]
                Z[:, j] = Y[:, j + 1]; Z[:, j + 1] = Y[:, j]
                sw += m & self.valid(Z)
                Z[:, j] = Y[:, j]; Z[:, j + 1] = Y[:, j + 1]
        return sub, sw


# ---------------- modelos de erro ----------------
def _other(rng, cur, pool):
    r = pool[rng.integers(0, len(pool), len(cur))]
    bad = r == cur
    while bad.any():
        r[bad] = pool[rng.integers(0, len(pool), bad.sum())]; bad = r == cur
    return r

def err_sub(C, rng, sch, npos=14, k=1):
    """k substituições em posições distintas (uniformes em 0..npos-1)."""
    Y = C.copy(); n = len(C)
    pos = np.argsort(rng.random((n, npos)), axis=1)[:, :k]
    for t in range(k):
        for j in range(npos):
            m = np.where(pos[:, t] == j)[0]
            if len(m) == 0: continue
            pool = sch.typing if j < 12 else np.arange(10)
            Y[m, j] = _other(rng, C[m, j], pool)
    return Y, np.ones(n, dtype=bool)

def err_transp(C, rng, sch, gap=1, npos=14):
    """troca dos caracteres nas posições j e j+gap (devolve máscara: houve mudança?)."""
    Y = C.copy(); n = len(C)
    j = rng.integers(0, npos - gap, n); idx = np.arange(n)
    a = C[idx, j]; b = C[idx, j + gap]
    Y[idx, j] = b; Y[idx, j + gap] = a
    return Y, a != b

def err_twin(C, rng, sch):
    """erro gêmeo: aa -> bb em duas posições vizinhas do payload (só onde há aa)."""
    Y = C.copy(); n = len(C); ok = np.zeros(n, dtype=bool)
    eq = C[:, :11] == C[:, 1:12]
    has = eq.any(1)
    # escolhe a primeira ocorrência aleatória
    r = rng.random(eq.shape); r[~eq] = -1
    j = r.argmax(1); idx = np.arange(n)
    nb = _other(rng, C[idx, j], sch.typing)
    Y[idx[has], j[has]] = nb[has]; Y[idx[has], j[has] + 1] = nb[has]
    return Y, has


def evaluate(sch, mode, errfn, n, rng, chunk=100000, swaps=True, **kw):
    """Classifica cada evento de erro:
       nd   = não detectado (a string errada é válida)
       ok1  = decodificador-1 (só substituições) propõe exatamente 1 candidato e é o certo
       bad1 = propõe exatamente 1 candidato e é ERRADO
       amb1 = 2+ candidatos ; none1 = nenhum
       *2   = idem para o decodificador-2 (substituições + trocas vizinhas)"""
    keys = ['nd', 'ok1', 'bad1', 'amb1', 'none1', 'ok2', 'bad2', 'amb2', 'none2']
    acc = dict.fromkeys(keys, 0); tot = 0
    while tot < n:
        C = sch.sample(min(chunk, n - tot), rng, mode)
        Y, changed = errfn(C, rng, sch, **kw)
        C = C[changed]; Y = Y[changed]
        if len(C) == 0: continue
        v = sch.valid(Y)
        sub, sw = sch.count_neighbors(Y, swaps)
        diff = (C != Y)
        dist = diff.sum(1)
        truth_sub = dist == 1
        # verdade é vizinha por troca?  (2 posições adjacentes trocadas)
        truth_sw = np.zeros(len(C), dtype=bool)
        if swaps:
            for j in range(13):
                truth_sw |= (dist == 2) & diff[:, j] & diff[:, j + 1] & (C[:, j] == Y[:, j + 1]) & (C[:, j + 1] == Y[:, j])
        nv = ~v
        acc['nd'] += v.sum()
        acc['ok1'] += (nv & (sub == 1) & truth_sub).sum()
        acc['bad1'] += (nv & (sub == 1) & ~truth_sub).sum()
        acc['amb1'] += (nv & (sub >= 2)).sum()
        acc['none1'] += (nv & (sub == 0)).sum()
        # decodificador-2: prioriza substituição; só tenta troca se nenhuma substituição serve
        ok2 = ((sub == 1) & truth_sub) | ((sub == 0) & (sw == 1) & truth_sw)
        bad2 = ((sub == 1) & ~truth_sub) | ((sub == 0) & (sw == 1) & ~truth_sw)
        amb2 = (sub >= 2) | ((sub == 0) & (sw >= 2))
        none2 = (sub == 0) & (sw == 0)
        acc['ok2'] += (nv & ok2).sum(); acc['bad2'] += (nv & bad2).sum()
        acc['amb2'] += (nv & amb2).sum(); acc['none2'] += (nv & none2).sum()
        tot += len(C)
    return {k: acc[k] / tot for k in keys} | {'n': tot}
