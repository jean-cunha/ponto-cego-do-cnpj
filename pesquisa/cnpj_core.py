"""
Núcleo: algoritmo OFICIAL do dígito verificador do CNPJ (numérico e alfanumérico)
e ferramentas de análise exata.

Regra oficial (Receita Federal, IN RFB 2.229/2024, Perguntas e Respostas):
  valor(c) = ASCII(c) - 48          (0..9 -> 0..9 ; A..Z -> 17..42)
  DV1 = f( sum_{i=1..12} w1[i]*valor(c_i) mod 11 )
  DV2 = f( sum_{i=1..12} w2[i]*valor(c_i) + 2*DV1 mod 11 )
  f(r) = 0 se r < 2, senão 11 - r
"""
from fractions import Fraction
from itertools import product

ALPHA36 = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
W1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
W2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3]  # + peso 2 para o DV1


def val(c):
    return ord(c) - 48


def rho(c):          # "raio": o que o DV oficial enxerga
    return val(c) % 11


def kappa(c):        # "camada": o que o DV oficial NAO enxerga
    return val(c) // 11


def f(r):
    return 0 if r < 2 else 11 - r


def dv(payload):
    s1 = sum(w * val(c) for w, c in zip(W1, payload)) % 11
    d1 = f(s1)
    s2 = (sum(w * val(c) for w, c in zip(W2, payload)) + 2 * d1) % 11
    return d1, f(s2)


def official_valid(s):
    if len(s) != 14 or any(ch not in ALPHA36 for ch in s[:12]) or not s[12:].isdigit():
        return False
    d1, d2 = dv(s[:12])
    return s[12] == str(d1) and s[13] == str(d2)


def classes(alphabet=ALPHA36):
    cl = {}
    for c in alphabet:
        cl.setdefault(rho(c), []).append(c)
    return cl


# ---------- análise exata por programação dinâmica ----------
def state_dist(alphabet, skip):
    """Distribuição exata (contagens) de (S1, S2pre) mod 11 sobre todos os
    payloads, somando apenas as posições fora de `skip`."""
    dist = {(0, 0): 1}
    for i in range(12):
        if i in skip:
            continue
        nd = {}
        for (a, b), n in dist.items():
            for c in alphabet:
                r = rho(c)
                k = ((a + W1[i] * r) % 11, (b + W2[i] * r) % 11)
                nd[k] = nd.get(k, 0) + n
        dist = nd
    return dist


def dvs_from_state(s1, s2pre):
    d1 = f(s1 % 11)
    return d1, f((s2pre + 2 * d1) % 11)


def exact_single_substitution(alphabet):
    """Probabilidade EXATA de um erro de 1 caractere no payload passar
    despercebido (payload uniforme, posição uniforme, caractere errado
    uniforme entre os demais do alfabeto)."""
    q = len(alphabet)
    und = 0
    tot = 0
    per_pos = []
    for i in range(12):
        dist = state_dist(alphabet, {i})
        u_i = 0
        t_i = 0
        for a in alphabet:
            for b in alphabet:
                if a == b:
                    continue
                for (s1, s2), n in dist.items():
                    o = dvs_from_state(s1 + W1[i] * rho(a), s2 + W2[i] * rho(a))
                    e = dvs_from_state(s1 + W1[i] * rho(b), s2 + W2[i] * rho(b))
                    t_i += n
                    if o == e:
                        u_i += n
        per_pos.append(Fraction(u_i, t_i))
        und += u_i
        tot += t_i
    return Fraction(und, tot), per_pos


def exact_adjacent_transposition(alphabet):
    """Probabilidade EXATA de uma troca de dois caracteres vizinhos distintos
    (dentro do payload) passar despercebida."""
    und = 0
    tot = 0
    for i in range(11):
        dist = state_dist(alphabet, {i, i + 1})
        for a in alphabet:
            for b in alphabet:
                if a == b:
                    continue
                for (s1, s2), n in dist.items():
                    o = dvs_from_state(s1 + W1[i] * rho(a) + W1[i + 1] * rho(b),
                                       s2 + W2[i] * rho(a) + W2[i + 1] * rho(b))
                    e = dvs_from_state(s1 + W1[i] * rho(b) + W1[i + 1] * rho(a),
                                       s2 + W2[i] * rho(b) + W2[i + 1] * rho(a))
                    tot += n
                    if o == e:
                        und += n
    return Fraction(und, tot)


if __name__ == "__main__":
    # 1) conferência com os exemplos públicos
    assert dv("12ABC34501DE") == (3, 5), dv("12ABC34501DE")      # exemplo oficial da Receita
    assert official_valid("12ABC34501DE35")
    assert official_valid("00000000000191")                      # Banco do Brasil
    assert official_valid("11222333000181")
    assert not official_valid("12ABC34501DE34")
    print("exemplos oficiais conferem")

    # 2) gêmeos invisíveis do exemplo oficial
    for s in ["126BC34501DE35", "12LBC34501DE35", "12WBC34501DE35"]:
        print(s, official_valid(s))

    # 3) classes
    for r, cl in sorted(classes().items()):
        print(r, cl, [kappa(c) for c in cl])
