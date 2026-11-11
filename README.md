# O ponto cego do CNPJ alfanumérico

O dígito verificador (DV) do CNPJ alfanumérico, em vigor desde 31/07/2026, deixa passar **5,9%** das trocas de um único caractere. No CNPJ numérico antigo eram **0,035%**. Este repositório mede esse ponto cego com contas exatas e propõe uma **regra de emissão** que o elimina sem alterar o algoritmo do DV.

**Página interativa:** https://jean-cunha.github.io/ponto-cego-do-cnpj/ (requer GitHub Pages ativo em `docs/`)

## Problema em 3 linhas

1. O DV oficial usa o valor `ASCII − 48` de cada caractere. Letras e dígitos passam a ter valores de 0 a 42, mas o módulo continua 11.
2. Caracteres cujos valores diferem por múltiplo de 11 (ex.: `6`, `A`, `L`, `W`) produzem o mesmo DV. Trocar um pelo outro não é detectado.
3. Não é preciso acreditar em mim: o teste abaixo leva 5 minutos.

## O teste de 5 minutos

Em qualquer validador de CNPJ alfanumérico que siga a regra oficial, teste:

| CNPJ | Esperado |
|---|---|
| `12.ABC.345/01DE-35` | válido (exemplo oficial da Receita) |
| `12.LBC.345/01DE-35` | **válido** (A trocado por L) |
| `12.WBC.345/01DE-35` | **válido** (A trocado por W) |
| `12.6BC.345/01DE-35` | **válido** (A trocado por 6) |

Eu (Rosario) testei `12.LBC.345/01DE-35` em um validador externo e ele foi aceito, o que confirma que a falha está na regra e não no código deste repositório. O script abaixo reproduz o mesmo resultado localmente.

## Números (exatos, erro uniforme nas 14 posições)

| Alfabeto | Troca de 1 caractere passa sem ser detectada |
|---|---|
| Numérico (antigo) | 0,035% |
| Alfanumérico (36 símbolos) | **5,883%** |
| Sem I, O, U, Q, F (31 símbolos) | 6,116% |
| Com a regra da raiz proposta (sem dobra) | **0%** |

Os valores são frações exatas calculadas por programação dinâmica (`pesquisa/cnpj_core.py`), conferidas por simulação de Monte Carlo e por força bruta.

## A regra proposta

Corrigir **na emissão**, não no algoritmo: o DV atual já está em milhares de sistemas, e a Receita é o único emissor e pode restringir quais raízes existem.

Para raízes novas com 3 ou mais letras, exigir `T = 0`, onde, com `valor = ASCII − 48`:

```
T = Σ 10^j · valor(c_j)  (mod 191),  j = 0..7 nos 8 primeiros caracteres
pesos = [10, 100, 45, 68, 107, 115, 4, 40]
```

Mais: ordem numérica e não emitir combinação com resto 1 no módulo 11 ("sem dobra"). Com isso:

- Distância mínima ≥ 3 entre CNPJs válidos: todo erro de 1 caractere tem **conserto único** (prova por varredura em `reproduzir.py`, parte 4).
- 100% dos erros de 1 caractere são consertáveis (97% sem a regra "sem dobra").
- O módulo 173 é o menor com garantia total. Escolhi 191 porque seus pesos são potências de 10.

Exemplo na regra: `34.DC0.XNA/0001-72`.

O decodificador **só sugere, nunca corrige sozinho**: com 2 erros, 2,1% dos consertos sairiam errados.

## Como rodar

Python 3, só biblioteca padrão:

```bash
python3 reproduzir.py            # partes 1 a 4, ~7 s
python3 reproduzir.py --mc 600   # + simulação de Monte Carlo
python3 reproduzir.py --busca    # + busca do módulo mínimo (minutos)
```

A página (HTML + JS puro, um arquivo):

```bash
cd web && python3 build.py   # gera web/dist/index.html, idêntico a docs/index.html
cd web && node test_core.js  # testes do núcleo JS contra os exemplos oficiais
```

Os scripts de `pesquisa/` usam numpy.

## Estrutura

```
reproduzir.py        refaz todos os números (começar por aqui)
docs/index.html      página interativa (GitHub Pages)
web/                 fonte da página, núcleo JS e testes
pesquisa/            experimentos (numpy) e resultados/ em JSON
```

## Limites

- CNPJs com letras já emitidos (desde 31/07/2026) não seguem a regra; ela só vale para raízes novas.
- A ordem de emissão com letras não está coberta.
- O custo mínimo real da regra fica entre 1,5 e 7,9 bits de espaço de raízes; não foi fechado.
- **Não medido:** quanto dos erros humanos reais (0↔Q, O↔D, A↔W no teclado) cai no ponto cego. Os 5,9% valem para erro uniforme, não para erro real.
- Não encontrei publicação anterior da medida exata com regra de emissão, mas a busca não é prova de ineditismo.

## Autoria

A análise matemática, o código e a página foram feitos com o **Claude** (Anthropic) e **validados por Rosario**, que reproduziu a saída do script em máquina própria (Ubuntu) e confirmou a falha em validador externo. A biblioteca Java com testes JUnit (parte autoral de Rosario) ainda não existe e será adicionada depois.

## Licença

MIT. Ver `LICENSE`.
