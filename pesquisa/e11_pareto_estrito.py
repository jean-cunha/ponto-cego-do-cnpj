import numpy as np, json
from sim2 import *
rng=np.random.default_rng(99)
W={5:[3,4,2,1,3,4,2,1],7:[1,2,3,4,1,2,3,4],13:[11,4,5,3,7,12,2,9],23:[19,16,5,3,11,2,15,9],37:[33,16,10,34,12,26,7,9],
   53:[13,10,24,47,28,46,15,36],97:[74,44,55,93,92,18,71,16],127:[50,87,32,76,117,8,19,61],173:[12,5,7,9,1,11,13,16],191:A_RAIZ}
out={}
for p,a in W.items():
    r={}
    for strict in (False,True):
        sch=Scheme('raiz+',p=p,a=a,strict=strict)
        e=evaluate(sch,'novo',err_sub,60000,rng,chunk=60000,swaps=False)
        r['estrito' if strict else 'comdobra']=dict(nd=float(e['nd']),ok=float(e['ok1']),amb=float(e['amb1']))
    out[p]=r
    print(p,round(np.log2(p),2),{k:(round(v['nd']*100,4),round(v['ok']*100,3)) for k,v in r.items()},flush=True)
json.dump(out,open('pareto_estrito.json','w'))
