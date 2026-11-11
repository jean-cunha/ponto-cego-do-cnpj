import numpy as np, json, sys, time
from sim2 import *
part=int(sys.argv[1])
A31=[i for i,c in enumerate(ALPHA36) if c not in "IOUQF"]
ROWS=[("legado|num",      Scheme('legado'),'num'),
      ("oficial|alnum",   Scheme('oficial'),'alnum'),
      ("oficial|num",     Scheme('oficial'),'num'),
      ("oficial31|alnum", Scheme('oficial',alphabet=A31),'alnum'),
      ("raiz+|novo",      Scheme('raiz+'),'novo'),
      ("raiz+estrito|novo",Scheme('raiz+',strict=True),'novo'),
      ("raiz+estrito|num",Scheme('raiz+',strict=True),'num')]
ERRS=[("sub1",err_sub,{},400000),("transp",err_transp,{},120000),("salto",err_transp,{'gap':2},120000),
      ("gemeo",err_twin,{},120000),("sub2",err_sub,{'k':2},120000)]
rng=np.random.default_rng(20261110+part)
out={}
t=time.time()
for i,(name,sch,mode) in enumerate(ROWS):
    if i%2!=part: continue
    for en,fn,kw,n in ERRS:
        r=evaluate(sch,mode,fn,n,rng,**kw)
        out[name+"|"+en]={k:float(v) for k,v in r.items()}
        print(name,en,{k:round(float(v)*100,4) for k,v in r.items() if k!='n'},r['n'],round(time.time()-t),'s',flush=True)
        json.dump(out,open(f'tabelas_{part}.json','w'),indent=1)
