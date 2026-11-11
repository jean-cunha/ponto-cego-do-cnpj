# Busca COMPLETA: menor primo p com garantia total (C1 + zero colisão 1<->5).
from cnpj_core import *
SY=[(val(c),rho(c)) for c in ALPHA36]
def primes(lo,hi): return [n for n in range(lo,hi) if all(n%k for k in range(2,int(n**.5)+1))]
D=set()
for (xc,rc) in SY:
    for (xy,ry) in SY:
        if xy==xc: continue
        r1=(ry-rc)%11
        if r1==0: continue
        for (x5,r5) in SY:
            for (xz,rz) in SY:
                if xz!=x5 and ((rz-r5)+3*r1)%11==0: D.add((xy-xc,xz-x5))
def zero_ratios(p):
    bad=set()
    for d1,d5 in D:
        if d1%p==0:
            if d5%p==0: return []
            continue
        bad.add((-d5*pow(d1,-1,p))%p)
    return [r for r in range(1,p) if r not in bad]
def S(b,p): return frozenset((b*11*e)%p for e in (1,2,3,-1,-2,-3))
def complete(p,ratios):
    allsets={}
    for b in range(1,p):
        s=S(b,p)
        if len(s)==6 and 0 not in s: allsets.setdefault(s,b)
    sets=list(allsets.items())
    for r in ratios:
        s1,s5=S(r,p),S(1,p)
        if len(s1)<6 or (s1&s5) or 0 in s1: continue
        cand=[(s,b) for s,b in sets if not (s&(s1|s5))]
        def dfs(start,used,chosen):
            if len(chosen)==6: return chosen
            if len(cand)-start < 6-len(chosen): return None
            for i in range(start,len(cand)):
                s,b=cand[i]
                if not (s&used):
                    res=dfs(i+1,used|s,chosen+[b])
                    if res: return res
            return None
        res=dfs(0,frozenset(),[])
        if res: return [r,res[0],res[1],res[2],1,res[3],res[4],res[5]]
    return None
found=None
for p in primes(53,200):
    z=zero_ratios(p); sol=complete(p,z) if z else None
    print(p,"razões sem colisão:",z if len(z)<8 else len(z),"| pesos:",sol,flush=True)
    if sol and not found: found=(p,sol); break
