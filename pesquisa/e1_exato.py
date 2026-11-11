from cnpj_core import *
import time
DIG = "0123456789"
A31 = "".join(c for c in ALPHA36 if c not in "IOUQF")
t=time.time()
for name, alph in [("legado numerico (10)", DIG), ("oficial alfanumerico (36)", ALPHA36), ("alfanumerico sem I,O,U,Q,F (31)", A31)]:
    p, per = exact_single_substitution(alph)
    tr = exact_adjacent_transposition(alph)
    q=len(alph)
    same = sum(len(c)*(len(c)-1) for c in classes(alph).values())
    print(f"{name}: subst 1 char nao detectada = {p} = {float(p)*100:.4f}%  | transposicao vizinha = {tr} = {float(tr)*100:.4f}%")
    print("   pares ordenados na mesma classe:", same, "de", q*(q-1), "=", f"{same/(q*(q-1))*100:.4f}%")
    print("   por posicao (%):", [round(float(x)*100,4) for x in per])
print(time.time()-t,"s")
# gêmeos: nº médio de strings com mesmos DVs que diferem só na camada
import math
cl=classes()
sizes=[len(cl[rho(c)]) for c in ALPHA36]
print("tamanho medio da classe de um caractere aleatorio:", sum(sizes)/36)
# media geometrica -> nº tipico de gemeos de um payload de 12
print("gemeos (media aritmetica) por payload:", (sum(sizes)/36)**12)
ex="12ABC34501DE"
g=1
for c in ex: g*=len(cl[rho(c)])
print("gemeos do exemplo oficial:", g)
