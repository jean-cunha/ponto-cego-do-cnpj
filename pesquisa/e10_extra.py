import numpy as np, json, math
from sim2 import *
from cnpj_core import classes, rho, ALPHA36
rng=np.random.default_rng(5)
# (a) fração de (raiz, ordem) com "dobra" (resto 1 em algum DV)
sch=Scheme('raiz+')
Y=sch.sample(600000,rng,'novo')
P=Y[:,:12]
S1=(RHO[P]*W1a).sum(1)%11; d1=F[S1]; S2=((RHO[P]*W2a).sum(1)+2*d1)%11
fold=((S1==1)|(S2==1)).mean()
print("fração com resto 1 em algum DV:",fold, " (esperado 1-(10/11)^2 =",1-(10/11)**2,")")
# (b) capacidade
tot=36**8
p3=1-sum(math.comb(8,k)*(26/36)**k*(10/36)**(8-k) for k in range(3))
print("36^8 =",tot, " fração com >=3 letras:",p3)
cap=tot/191*p3
print("raízes na regra:",cap, " (x legado 1e8 =",cap/1e8,")  bits perdidos:",math.log2(191)-math.log2(p3))
print("com sem-dobra p/ ordem 0001:",cap*(1-fold), "bits totais:",math.log2(191)-math.log2(p3)-math.log2(1-fold))
print("limite inferior simples (esferas na raiz, DVs ajudando): log2(281/100) =",math.log2(281/100))
# (c) teclado QWERTY: vizinhos na mesma classe (invisíveis ao DV)
rows=["1234567890","QWERTYUIOP","ASDFGHJKL","ZXCVBNM"]
off=[0,0.5,0.75,1.25]
pos={}
for r,row in enumerate(rows):
    for i,ch in enumerate(row): pos[ch]=(r,i+off[r])
adj=[]
for a in pos:
    for b in pos:
        if a<b:
            (r1,x1),(r2,x2)=pos[a],pos[b]
            if (r1==r2 and abs(x1-x2)<=1.01) or (abs(r1-r2)==1 and abs(x1-x2)<=0.8): adj.append((a,b))
blind=[(a,b) for a,b in adj if rho(a)==rho(b)]
print("pares vizinhos no QWERTY:",len(adj)," invisíveis ao DV:",blind)
vis=[("0","O"),("0","Q"),("0","D"),("O","Q"),("O","D"),("1","I"),("1","L"),("I","L"),("2","Z"),("5","S"),("8","B"),("6","G"),("U","V"),("C","G"),("E","F"),("P","R"),("M","N"),("V","Y"),("7","T"),("4","A")]
print("confusões visuais invisíveis:",[(a,b) for a,b in vis if rho(a)==rho(b)],"de",len(vis))
fon=list("BCDEGPTVZ")
print("letras que rimam em 'ê' na mesma classe:",[(a,b) for i,a in enumerate(fon) for b in fon[i+1:] if rho(a)==rho(b)])
