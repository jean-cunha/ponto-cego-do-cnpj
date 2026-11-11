#!/usr/bin/env python3
"""
reproduzir.py — refaz os números da página "CNPJ que se conserta sozinho".
Só usa a biblioteca padrão do Python 3.

    python3 reproduzir.py            # partes 1 a 4 (cerca de 1 minuto)
    python3 reproduzir.py --busca    # + busca completa do módulo mínimo (alguns minutos)
    python3 reproduzir.py --mc 2000  # + simulação por força bruta com 2000 erros por regra

Parte 1  regra oficial e exemplos públicos
Parte 2  o ponto cego: classes e taxas EXATAS (frações, sem sorteio)
Parte 3  regra da raiz: condições de projeto
Parte 4  PROVA por varredura completa: distância mínima >= 3
"""
import sys, itertools, random
from fractions import Fraction

ALFA = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
DIG = ALFA[:10]
W1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
W2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3]          # o 1º DV entra com peso 2
P = 191                                             # módulo da regra da raiz
A = [pow(10, j, P) for j in range(1, 9)]            # pesos 10^j mod 191

val = lambda c: ord(c) - 48                         # regra oficial: ASCII - 48
raio = lambda c: val(c) % 11                        # o que o DV enxerga
camada = lambda c: val(c) // 11                     # o que o DV não enxerga
dobra = lambda r: 0 if r < 2 else 11 - r


def somas(p):
    return (sum(w * raio(c) for w, c in zip(W1, p)) % 11,
            sum(w * raio(c) for w, c in zip(W2, p)) % 11)


def dv(p):
    s1, s2 = somas(p)
    d1 = dobra(s1)
    return d1, dobra((s2 + 2 * d1) % 11)


def valido_oficial(s):
    if len(s) != 14 or any(c not in ALFA for c in s[:12]) or not s[12:].isdigit():
        return False
    return (int(s[12]), int(s[13])) == dv(s[:12])


def t_raiz(s):
    return sum(a * val(c) for a, c in zip(A, s[:8])) % P


def valido_raiz(s, estrito=True):
    """oficial + regra da raiz. Raiz toda numérica = legado."""
    if len(s) != 14 or any(c not in ALFA for c in s[:12]) or not s[12:].isdigit():
        return False
    if any(c.isalpha() for c in s[8:12]):
        return False
    letras = sum(c.isalpha() for c in s[:8])
    if letras == 0:
        return valido_oficial(s)
    if letras < 3 or t_raiz(s) != 0:
        return False
    if not estrito:
        return valido_oficial(s)
    s1, s2 = somas(s[:12]); d1, d2 = int(s[12]), int(s[13])
    return (s1 + d1) % 11 == 0 and (s2 + 2 * d1 + d2) % 11 == 0


# ------------------------------------------------------------------ parte 1
def parte1():
    print("== 1. Regra oficial ==")
    assert dv("12ABC34501DE") == (3, 5)
    for s in ["12ABC34501DE35", "00000000000191", "11222333000181"]:
        assert valido_oficial(s)
    print("exemplos públicos conferem (12.ABC.345/01DE-35, Banco do Brasil)")
    for s in ["12LBC34501DE35", "126BC34501DE35", "12WBC34501DE35"]:
        print("  ", s, "-> válido pela regra em vigor:", valido_oficial(s))


# ------------------------------------------------------------------ parte 2
def dist_estados(alf, fora):
    d = {(0, 0): 1}
    for i in range(12):
        if i in fora:
            continue
        nd = {}
        for (a, b), n in d.items():
            for c in alf:
                r = raio(c)
                k = ((a + W1[i] * r) % 11, (b + W2[i] * r) % 11)
                nd[k] = nd.get(k, 0) + n
        d = nd
    return d


def dvs(s1, s2):
    d1 = dobra(s1 % 11)
    return d1, dobra((s2 + 2 * d1) % 11)


def exato_substituicao(alf):
    und = tot = 0
    for i in range(12):
        dist = dist_estados(alf, {i})
        for a in alf:
            for b in alf:
                if a == b:
                    continue
                for (s1, s2), n in dist.items():
                    tot += n
                    if dvs(s1 + W1[i] * raio(a), s2 + W2[i] * raio(a)) == dvs(s1 + W1[i] * raio(b), s2 + W2[i] * raio(b)):
                        und += n
    return Fraction(und, tot)


def exato_transposicao(alf):
    und = tot = 0
    for i in range(11):
        dist = dist_estados(alf, {i, i + 1})
        for a in alf:
            for b in alf:
                if a == b:
                    continue
                for (s1, s2), n in dist.items():
                    tot += n
                    o = dvs(s1 + W1[i] * raio(a) + W1[i + 1] * raio(b), s2 + W2[i] * raio(a) + W2[i + 1] * raio(b))
                    e = dvs(s1 + W1[i] * raio(b) + W1[i + 1] * raio(a), s2 + W2[i] * raio(b) + W2[i + 1] * raio(a))
                    if o == e:
                        und += n
    return Fraction(und, tot)


def parte2():
    print("\n== 2. O ponto cego ==")
    cl = {}
    for c in ALFA:
        cl.setdefault(raio(c), []).append(c)
    for r in sorted(cl):
        print("  raio %2d: %s" % (r, " ".join(cl[r])))
    g = 1
    for c in "12ABC34501DE":
        g *= len(cl[raio(c)])
    print("cadeias com os mesmos raios do exemplo oficial:", g)
    a31 = "".join(c for c in ALFA if c not in "IOUQF")
    for nome, alf in [("numérico antigo", DIG), ("com letras (36 símbolos)", ALFA), ("sem I,O,U,Q,F (31)", a31)]:
        p = exato_substituicao(alf); t = exato_transposicao(alf)
        print("  %-26s troca de 1 caractere passa: %.4f%% (12 posições) = %.4f%% (14 posições) | vizinhos invertidos: %.4f%%"
              % (nome, float(p) * 100, float(p) * 100 * 12 / 14, float(t) * 100))
        if alf == ALFA:
            print("     fração exata:", p)


# ------------------------------------------------------------------ parte 3
SIM = [(val(c), raio(c)) for c in ALFA]


def c1(a, p):
    """erros só de camada: as 48 assinaturas a_j*11*e são distintas"""
    seen = set()
    for aj in a:
        for e in (1, 2, 3, -1, -2, -3):
            v = (aj * 11 * e) % p
            if v == 0 or v in seen:
                return False
            seen.add(v)
    return True


def pares_perigosos():
    """(d1, d5): diferenças de valor nas posições 1 e 5 que se cancelam nos dois DVs"""
    D = set()
    for (xc, rc) in SIM:
        for (xy, ry) in SIM:
            r1 = (ry - rc) % 11
            if xy == xc or r1 == 0:
                continue
            for (x5, r5) in SIM:
                for (xz, rz) in SIM:
                    if xz != x5 and ((rz - r5) + 3 * r1) % 11 == 0:
                        D.add((xy - xc, xz - x5))
    return D


def razoes_sem_colisao(p, D):
    ruins = set()
    for d1, d5 in D:
        if d1 % p == 0:
            if d5 % p == 0:
                return []
            continue
        ruins.add((-d5 * pow(d1, -1, p)) % p)
    return [r for r in range(1, p) if r not in ruins]


def parte3():
    print("\n== 3. Regra da raiz: T = soma 10^j * valor(c_j) mod 191 ==")
    print("pesos:", A)
    print("C1 (48 assinaturas de erro de camada distintas):", c1(A, P))
    D = pares_perigosos()
    z = razoes_sem_colisao(P, D)
    razao = (A[0] * pow(A[4], -1, P)) % P
    print("posições 1 e 5 nunca se confundem:", razao in z)
    print("exemplo de CNPJ na regra: 34.DC0.XNA/0001-72 ->", valido_raiz("34DC0XNA000172"),
          "| com A trocado por L:", valido_raiz("34DC0XNL000172"), "(regra em vigor:", valido_oficial("34DC0XNL000172"), ")")


def busca():
    print("\n== busca completa do menor módulo primo com garantia total ==")
    D = pares_perigosos()
    S = lambda b, p: frozenset((b * 11 * e) % p for e in (1, 2, 3, -1, -2, -3))
    primos = [n for n in range(53, 200) if all(n % k for k in range(2, int(n ** .5) + 1))]
    for p in primos:
        z = razoes_sem_colisao(p, D); sol = None
        todos = {}
        for b in range(1, p):
            s = S(b, p)
            if len(s) == 6 and 0 not in s:
                todos.setdefault(s, b)
        for r in z:
            s1, s5 = S(r, p), S(1, p)
            if len(s1) < 6 or (s1 & s5) or 0 in s1:
                continue
            cand = [(s, b) for s, b in todos.items() if not (s & (s1 | s5))]

            def dfs(i0, usados, esc):
                if len(esc) == 6:
                    return esc
                for i in range(i0, len(cand)):
                    s, b = cand[i]
                    if not (s & usados):
                        res = dfs(i + 1, usados | s, esc + [b])
                        if res:
                            return res
                return None
            res = dfs(0, frozenset(), [])
            if res:
                sol = [r, res[0], res[1], res[2], 1, res[3], res[4], res[5]]; break
        print("  p = %3d  razões a1/a5 sem colisão: %3d  pesos: %s" % (p, len(z), sol))
        if sol:
            print("  -> menor módulo com garantia total:", p); break


# ------------------------------------------------------------------ parte 4
def parte4():
    print("\n== 4. Prova por varredura: distância mínima >= 3 ==")
    # posição: (alfabeto, coeficiente em T, em E1, em E2).  E1: S1 + d1 = 0 ; E2: S2 + 2 d1 + d2 = 0 (mod 11)
    D10 = SIM[:10]
    POS = [(SIM, A[j], W1[j], W2[j]) for j in range(8)] + [(D10, 0, W1[j], W2[j]) for j in range(8, 12)] + [(D10, 0, 1, 2), (D10, 0, 0, 1)]

    def deltas(pos):
        al, ct, c1_, c2_ = pos
        return {((ct * (y - x)) % P, (c1_ * (s - r)) % 11, (c2_ * (s - r)) % 11) for (x, r) in al for (y, s) in al if x != y}
    Dl = [deltas(p) for p in POS]
    um = [i + 1 for i in range(14) if (0, 0, 0) in Dl[i]]
    dois = []
    for i, j in itertools.combinations(range(14), 2):
        neg = {((-t) % P, (-a) % 11, (-b) % 11) for (t, a, b) in Dl[j]}
        if Dl[i] & neg:
            dois.append((i + 1, j + 1))
    print("posições onde 1 troca mantém as três contas zeradas:", um)
    print("pares de posições onde 2 trocas se cancelam:", dois)
    print("=> distância mínima >= 3: todo erro de 1 caractere tem conserto único" if not um and not dois else "=> FALHOU")


# ------------------------------------------------------------------ simulação
def gerar(esq, rng):
    if esq == "legado":
        p = "".join(rng.choice(DIG) for _ in range(12))
    elif esq == "oficial":
        p = "".join(rng.choice(ALFA) for _ in range(12))
    else:
        while True:
            r = "".join(rng.choice(ALFA) for _ in range(8))
            if t_raiz(r) or sum(c.isalpha() for c in r) < 3:
                continue
            p = r + "".join(rng.choice(DIG) for _ in range(4))
            s1, s2 = somas(p)
            if s1 != 1 and (s2 + 2 * dobra(s1)) % 11 != 1:
                break
    d1, d2 = dv(p)
    return p + str(d1) + str(d2)


def mc(n):
    print("\n== simulação por força bruta: 1 caractere trocado, %d erros por regra ==" % n)
    rng = random.Random(2026)
    regras = [("numérico antigo", "legado", lambda s: s.isdigit() and valido_oficial(s), DIG),
              ("com letras, em vigor", "oficial", valido_oficial, ALFA),
              ("regra da raiz, sem dobra", "raiz", valido_raiz, ALFA)]
    for nome, esq, ok, pool in regras:
        passa = conserta = 0
        for _ in range(n):
            c = gerar(esq, rng); j = rng.randrange(14); pj = pool if j < 12 else DIG
            y = c[:j] + rng.choice([x for x in pj if x != c[j]]) + c[j + 1:]
            if ok(y):
                passa += 1; continue
            viz = [y[:k] + x + y[k + 1:] for k in range(14) for x in (pool if k < 12 else DIG) if x != y[k]]
            bons = [z for z in viz if ok(z)]
            if bons == [c]:
                conserta += 1
        print("  %-26s passam %.2f%%   consertados %.1f%%" % (nome, 100 * passa / n, 100 * conserta / n))


if __name__ == "__main__":
    parte1(); parte2(); parte3(); parte4()
    if "--busca" in sys.argv:
        busca()
    if "--mc" in sys.argv:
        mc(int(sys.argv[sys.argv.index("--mc") + 1]))
