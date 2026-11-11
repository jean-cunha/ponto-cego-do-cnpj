"""
Simulador vetorizado: palavra-código aleatória -> erro -> decodificador por
força bruta (testa TODOS os vizinhos a 1 caractere). Sem atalhos algébricos:
o que conta é só a função `valido`.
"""
import numpy as np
from cnpj_core import ALPHA36, W1, W2

X   = np.array([ord(c)-48 for c in ALPHA36])          # valor oficial
RHO = X % 11
KAP = X // 11
LET = (np.arange(36) >= 10).astype(np.int64)
W1a = np.array(W1); W2a = np.array(W2)
F   = np.array([0,0,9,8,7,6,5,4,3,2,1])               # f(r)

class Scheme:
    """kind: 'legado' (só dígitos), 'oficial' (36 símbolos, só DV),
             'raiz+' (oficial + regra da raiz mod p, pesos a; ordem numérica;
                      raiz nova tem >= minlet letras; raiz toda numérica = legado)"""
    def __init__(self, kind, p=None, a=None, minlet=3, alphabet=None):
        self.kind=kind; self.p=p; self.minlet=minlet
        self.a=np.array(a) if a is not None else np.zeros(8,dtype=np.int64)
        self.alpha = np.arange(36) if alphabet is None else np.array(alphabet)

    def stats(self, P):
        """P: N x 12 índices. devolve S1,S2pre,T,L,O"""
        S1=(RHO[P]*W1a).sum(1)%11; S2=(RHO[P]*W2a).sum(1)%11
        T =(X[P[:,:8]]*self.a).sum(1)%self.p if self.p else np.zeros(len(P),dtype=np.int64)
        L =LET[P[:,:8]].sum(1); O=LET[P[:,8:]].sum(1)
        return S1,S2,T,L,O

    def valid(self,S1,S2,T,L,O,d1,d2):
        off=(F[S1%11]==d1)&(F[(S2+2*d1)%11]==d2)
        if self.kind=='oficial': return off
        if self.kind=='legado':  return off&(L==0)&(O==0)
        return off&(O==0)&((L==0)|((L>=self.minlet)&(T%self.p==0)))

    def dvs(self,P):
        S1,S2,_,_,_=self.stats(P); d1=F[S1]; d2=F[(S2+2*d1)%11]; return d1,d2

    def sample(self,n,rng,mode):
        """mode: 'num' = 12 dígitos; 'alnum' = 12 alfanuméricos uniformes;
                 'novo' = raiz na regra da raiz, ordem numérica"""
        if mode=='num':   return rng.integers(0,10,(n,12))
        if mode=='alnum': return self.alpha[rng.integers(0,len(self.alpha),(n,12))]
        out=[]; got=0
        while got<n:
            R=self.alpha[rng.integers(0,len(self.alpha),(1500000,8),dtype=np.int8)].astype(np.int64)
            ok=(LET[R].sum(1)>=self.minlet)
            if self.p: ok&=((X[R]*self.a).sum(1)%self.p==0)
            R=R[ok]; out.append(R); got+=len(R)
        R=np.concatenate(out)[:n]
        return np.concatenate([R,rng.integers(0,10,(n,4))],1)

    def neighbors(self,P,d1,d2,truth=None):
        """para cada string recebida (P,d1,d2): ela é válida? quantos vizinhos
        a 1 caractere são válidos? (truth: payload+DV corretos, p/ saber se o
        vizinho válido é o verdadeiro)"""
        n=len(P); S1,S2,T,L,O=self.stats(P)
        self_ok=self.valid(S1,S2,T,L,O,d1,d2)
        cnt=np.zeros(n,dtype=np.int64)
        for j in range(12):
            yj=P[:,j]
            for b in self.alpha if self.kind!='legado' else range(10):
                m=(yj!=b)
                dr=RHO[b]-RHO[yj]
                S1n=S1+W1a[j]*dr; S2n=S2+W2a[j]*dr
                if j<8:
                    Tn=T+self.a[j]*(X[b]-X[yj]) if self.p else T
                    Ln=L+LET[b]-LET[yj]; On=O
                else:
                    Tn=T; Ln=L; On=O+LET[b]-LET[yj]
                cnt+=(m&self.valid(S1n,S2n,Tn,Ln,On,d1,d2))
        for d in range(10):
            cnt+=((d1!=d)&self.valid(S1,S2,T,L,O,np.full(n,d),d2))
            cnt+=((d2!=d)&self.valid(S1,S2,T,L,O,d1,np.full(n,d)))
        return self_ok,cnt

def single_error(P,d1,d2,rng,sch,payload_only=False,same_alpha=None):
    """1 caractere errado em posição uniforme (14 posições, ou só payload)."""
    n=len(P); Y=P.copy(); e1=d1.copy(); e2=d2.copy()
    pos=rng.integers(0,12 if payload_only else 14,n)
    alpha = sch.alpha if sch.kind!='legado' else np.arange(10)
    for j in range(12):
        m=np.where(pos==j)[0]
        if len(m)==0: continue
        r=alpha[rng.integers(0,len(alpha),len(m))]
        bad=(r==P[m,j])
        while bad.any():
            r[bad]=alpha[rng.integers(0,len(alpha),bad.sum())]; bad=(r==P[m,j])
        Y[m,j]=r
    for arr,j in ((e1,12),(e2,13)):
        m=np.where(pos==j)[0]
        if len(m): arr[m]=(arr[m]+rng.integers(1,10,len(m)))%10
    return Y,e1,e2,pos

def run_single(sch,mode,n,rng,payload_only=False,chunk=100000):
    und=uni=amb=0; tot=0
    while tot<n:
        m=min(chunk,n-tot)
        P=sch.sample(m,rng,mode); d1,d2=sch.dvs(P)
        Y,e1,e2,_=single_error(P,d1,d2,rng,sch,payload_only)
        ok,cnt=sch.neighbors(Y,e1,e2)
        und+=ok.sum(); uni+=((~ok)&(cnt==1)).sum(); amb+=((~ok)&(cnt>=2)).sum()
        assert ((~ok)&(cnt==0)).sum()==0
        tot+=m
    return dict(n=n,nao_detectado=und/n,corrigido=uni/n,ambiguo=amb/n)
