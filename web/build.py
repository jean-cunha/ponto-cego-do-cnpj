import json, re
core=open('core.js').read()
core=core[:core.index('if (typeof module')]
par=json.load(open('pareto_estrito.json'))
pareto=[dict(p=int(p),dobra=round(v['comdobra']['ok']*100,1),estrito=round(v['estrito']['ok']*100,1)) for p,v in sorted(par.items(),key=lambda kv:int(kv[0]))]
ref={
 "sub1":  {"legado":{"nd":"0,035%"},"oficial":{"nd":"5,883%"},"oficial31":{"nd":"6,116%"},"raiz":{"nd":"0,003%"},"raizE":{"nd":"0%"}},
 "transp":{"legado":{"nd":"0,11%"}, "oficial":{"nd":"5,95%"}, "oficial31":{"nd":"6,23%"}, "raiz":{"nd":"0,05%"}, "raizE":{"nd":"0%"}},
 "sub2":  {"legado":{"nd":"1,01%"}, "oficial":{"nd":"1,13%"}, "oficial31":{"nd":"1,21%"}, "raiz":{"nd":"0,008%"},"raizE":{"nd":"0%"}},
}
data=json.dumps({"ref":ref,"pareto":pareto},ensure_ascii=False)
t=open('page_template.html').read()
assert '/*__CORE__*/' in t and '/*__DATA__*/' in t
t=t.replace('/*__CORE__*/',core).replace('/*__DATA__*/',data)
import os; os.makedirs('dist',exist_ok=True)
open('dist/index.html','w').write(t)
# extrai os scripts para checagem de sintaxe
js="\n".join(re.findall(r'<script>(.*?)</script>',t,flags=re.S))
open('dist/_check.js','w').write(js)
print(len(t),'bytes'); print(pareto)
