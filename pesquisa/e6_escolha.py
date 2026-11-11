# Escolha de (p, pesos) para a regra da raiz, sob decodificação estrita (sem dobra).
# C1 exata (erros só de camada localizáveis)  +  menor probabilidade EXATA de
# confusão entre as posições 1 e 5 (as únicas da raiz com pesos proporcionais mod 11).
from cnpj_core import *
import itertools
SY=[(val(c),rho(c)) for c in ALPHA36]
def primes(lo,hi): return [n for n in range(lo,hi) if all(n%k for k in range(2,int(n**.5)+1))]
def c1(a,p):
    seen=set()
    for aj in a:
        for e in (1,2,3,-1,-2,-3):
            v=(aj*11*e)%p
            if v==0 or v in seen: return False
            seen.add(v)
    return True
def p15(a1,a5,p):
    """prob. exata de ambiguidade p/ erro de 1 caractere na posição 1 (e na 5),
    caracteres uniformes; devolve (P_erro_em_1, P_erro_em_5)"""
    out=[]
    for (aj,ak,wj,wk) in ((a1,a5,(5,6),(9,2)),(a5,a1,(9,2),(5,6))):
        # tabela: para cada (delta_rho necessário, valor t necessário) existe z_k?
        amb=0; tot=0
        # pré-computa por char em k: conjunto de (drho, ak*dx mod p) alcançáveis
        reach=[]
        for (xk,rk) in SY:
            s=set()
            for (xz,rz) in SY:
                if xz!=xk: s.add(((rz-rk)%11,(ak*(xz-xk))%p))
            reach.append(s)
        for (xc,rc) in SY:
            for (xy,ry) in SY:
                if xy==xc: continue
                d=(ry-rc)%11
                if d==0: continue          # só de camada: coberto por C1
                # precisa: wk*d'' = -wj*d (mod 11) nas duas equações
                need=None
                for dd in range(1,11):
                    if (wk[0]*dd+wj[0]*d)%11==0 and (wk[1]*dd+wj[1]*d)%11==0: need=dd
                t=(-aj*(xy-xc))%p
                for s in reach:
                    tot+=1
                    if need is not None and (need,t) in s: amb+=1
        out.append(amb/tot)
    return out
best=[]
for p in primes(53,200):
    cands=[]
    for g in range(2,p):
        a=[pow(g,j,p) for j in range(1,9)]
        if c1(a,p):
            e1,e5=p15(a[0],a[4],p)
            cands.append(((e1+e5)/2,g,a))
    cands.sort()
    if cands:
        print(p,"n_geo_C1=%d"%len(cands),"melhor g=%d"%cands[0][1],cands[0][2],"P(1<->5)=%.5f%%"%(cands[0][0]*100), " pior=%.4f%%"%(cands[-1][0]*100),flush=True)
    else:
        print(p,"sem progressão geométrica que satisfaça C1",flush=True)
