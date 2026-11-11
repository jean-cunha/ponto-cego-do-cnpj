"""
VERIFICAÇÃO EXAUSTIVA (prova assistida por computador) de que o código
"raiz+ estrito" (p=191, pesos 10^j) tem distância mínima >= 3, i.e. nenhum par
de palavras-código difere em 1 ou 2 posições.  Varre TODAS as combinações de
símbolos para todos os pares de posições (não usa amostragem).

Palavra-código: (c1..c8 | o1..o4 | d1 d2) com
   T = sum 10^j * x(c_j) ≡ 0 (mod 191)           [raiz]
   E1 = sum W1*rho + d1 ≡ 0 (mod 11)              [estrito, sem dobra]
   E2 = sum W2*rho + 2*d1 + d2 ≡ 0 (mod 11)
   ordem e DVs: dígitos.
Duas palavras-código que diferem só nas posições i (e j) precisam ter
variação nula em T, E1 e E2. Basta mostrar que isso é impossível.
"""
from cnpj_core import *
from sim2 import P_RAIZ, A_RAIZ
import itertools
SYM=[(val(c),rho(c)) for c in ALPHA36]; DIG=SYM[:10]
# cada posição: (alfabeto, coef_T, coef_E1, coef_E2)
POS=[(SYM,A_RAIZ[j],W1[j],W2[j]) for j in range(8)]+[(DIG,0,W1[j],W2[j]) for j in range(8,12)]+[(DIG,0,1,2),(DIG,0,0,1)]
def deltas(pos):
    al,ct,c1,c2=pos
    out=set()
    for (x,r) in al:
        for (y,s) in al:
            if x!=y: out.add(((ct*(y-x))%P_RAIZ,(c1*(s-r))%11,(c2*(s-r))%11))
    return out
D=[deltas(p) for p in POS]
# distância 1: alguma mudança de 1 posição com variação nula?
d1=[i+1 for i in range(14) if (0,0,0) in D[i]]
print("posições onde 1 mudança mantém a palavra válida:",d1)
bad=[]
for i,j in itertools.combinations(range(14),2):
    neg={((-t)%P_RAIZ,(-a)%11,(-b)%11) for (t,a,b) in D[j]}
    inter=D[i]&neg
    if inter: bad.append((i+1,j+1,len(inter)))
print("pares de posições onde 2 mudanças se cancelam:",bad)
print("=> distância mínima >= 3" if not d1 and not bad else "=> FALHOU")
# transposições vizinhas: sempre detectadas?
tr=[]
for j in range(13):
    ali,cti,c1i,c2i=POS[j]; alj,ctj,c1j,c2j=POS[j+1]
    for (x,r) in ali:
        for (y,s) in alj:
            if x==y: continue
            # troca só é string bem-formada se os símbolos couberem nas duas posições
            if (y,s) not in ali or (x,r) not in alj: continue
            dt=(cti*(y-x)+ctj*(x-y))%P_RAIZ; da=(c1i*(s-r)+c1j*(r-s))%11; db=(c2i*(s-r)+c2j*(r-s))%11
            if (dt,da,db)==(0,0,0): tr.append((j+1,x,y))
print("transposições vizinhas não detectadas:",len(tr))
