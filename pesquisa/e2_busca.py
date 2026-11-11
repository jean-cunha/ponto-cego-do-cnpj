# Busca do menor módulo primo p e pesos a_1..a_8 para a "regra da raiz":
#   T(raiz) = sum a_i * valor(c_i)  ≡ 0 (mod p)
# Condições exatas (sem contar o efeito da dobra f(0)=f(1)=0, medido depois):
#  C1: erros "só de camada" (invisíveis ao DV) em posições diferentes da raiz têm
#      assinaturas diferentes:  a_j*11*e distintos, e in {±1,±2,±3}, j=1..8
#  C2: posições 1 e 5 (únicas da raiz com vetores de peso proporcionais mod 11)
#      nunca se confundem: a_1*d != a_5*d'  para d ≡ δ, d' ≡ 3δ (mod 11)
from cnpj_core import *
VALS = [val(c) for c in ALPHA36]
DIFFS = sorted({x-y for x in VALS for y in VALS if x!=y})
def primes(lo,hi):
    return [n for n in range(lo,hi) if all(n%k for k in range(2,int(n**.5)+1))]
def c1(a,p):
    seen=set()
    for aj in a:
        for e in (1,2,3,-1,-2,-3):
            v=(aj*11*e)%p
            if v==0 or v in seen: return False
            seen.add(v)
    return True
def c2(a,p):
    a1,a5=a[0],a[4]
    for d in DIFFS:
        for d2 in DIFFS:
            if (d2-3*d)%11==0 and d%11!=0:
                if (a1*d-a5*d2)%p==0: return False
    return True
print("diferenças possíveis entre valores:", len(DIFFS), "de", DIFFS[0], "a", DIFFS[-1])
# (a) pesos em progressão geométrica a_j = g^j
for p in primes(37,140):
    sols=[]
    for g in range(2,p):
        a=[pow(g,j,p) for j in range(1,9)]
        if c1(a,p) and c2(a,p): sols.append(g)
    print(p, "geradores g com C1 e C2:", sols[:12], "..." if len(sols)>12 else "")
