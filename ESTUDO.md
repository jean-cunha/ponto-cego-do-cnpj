# Guia de estudo: entender o ponto cego sem depender de ninguém

Este guia existe para que quem mantém o projeto consiga explicá-lo de cabeça e refazer a conta à mão. Cada afirmação aponta para um comando que a verifica.

## 1. O algoritmo oficial em 6 linhas

- `valor(c) = ASCII(c) − 48`. Dígitos valem 0 a 9; `A` vale 17, `B` 18, ..., `Z` 42.
- `DV1`: soma dos 12 primeiros valores com pesos `5 4 3 2 9 8 7 6 5 4 3 2`, módulo 11.
- `DV2`: igual, com pesos `6 5 4 3 2 9 8 7 6 5 4 3`, mais `2·DV1`, módulo 11.
- `f(r) = 0` se `r < 2`, senão `11 − r`.

Código: `pesquisa/cnpj_core.py`. Confira com o exemplo oficial `12.ABC.345/01DE-35`.

## 2. Por que existe o ponto cego

O DV só enxerga `valor mod 11`. Dois caracteres cujos valores diferem por múltiplo de 11 são **indistinguíveis** para ele. Nos dígitos, isso nunca acontecia (0 a 9 são todos diferentes mod 11). Com letras, acontece:

| resto mod 11 | caracteres |
|---|---|
| 6 | `6`, `A`, `L`, `W` |
| 7 | `7`, `B`, `M`, `X` |
| 0 | `0`, `F`, `Q` |

Exercício à mão: `A` vale 17, `L` vale 28, `W` vale 39. Diferenças de 11 e 22, logo, trocar um pelo outro soma `peso × 11k`, que é 0 mod 11. Os dois DVs não mudam. Verifique: `python3 reproduzir.py`, parte 1.

## 3. De onde vem 5,9%

Conta aproximada, que você pode fazer na mão: se o caractere trocado cai aleatoriamente em outro símbolo, a chance de cair na mesma classe de resto é

`(18·2 + 16·3 + 2·1) / (36·35) = 86/1260 ≈ 6,83%`

(classes de tamanho 3, 4 e 2; ver tabela da parte 2 do script). Isso vale para as 12 posições da raiz/ordem; nas 14 posições, as 2 posições do DV detectam tudo, e a taxa cai para `12/14` disso. O valor exato (6,864% e 5,883%) é um pouco maior porque há um segundo mecanismo, a **dobra**: `f(0) = f(1) = 0`, então restos 0 e 1 geram o mesmo DV. É isso também que explica os 0,035% do CNPJ numérico, que não tem classes repetidas.

Verifiquei por simulação aleatória independente: 6,9% para 12 posições (exato: 6,864%) e 0,042% no numérico (exato: 0,041% em 12 posições).

## 4. A regra proposta, sem matemática pesada

Ideia: acrescentar uma **terceira verificação** que enxergue o que o módulo 11 não enxerga (`valor ÷ 11`, a "camada"). Ela é calculada só sobre os 8 primeiros caracteres (a raiz):

`T = Σ 10^j · valor(c_j) mod 191 = 0`

Como é uma restrição sobre quais raízes são emitidas, não muda o DV de quem já existe. Duas condições são verificadas por força bruta em `reproduzir.py` (partes 3 e 4):

1. Nenhuma troca de 1 caractere mantém as três verificações em zero.
2. Nenhum par de trocas se cancela (isso dá distância mínima ≥ 3, e por isso o erro de 1 caractere pode ser corrigido, não só detectado).

Limite que importa: a prova é por varredura finita, sobre o alfabeto e as posições definidos aqui. Não é uma prova teórica geral.

## 5. Perguntas que você deve conseguir responder

1. **Por que 6 e A colidem?** `6` e `A` (17) diferem por 11.
2. **Por que não mudar o algoritmo do DV?** Está implantado em milhares de sistemas. Restringir a emissão é uma mudança de um único emissor.
3. **Por que 191 e não 173?** 173 é o menor módulo com garantia total. 191 foi escolhido porque os pesos são potências de 10 (decisão de estilo, ganho de 0,14 bit).
4. **Qual a maior fraqueza?** A taxa de 5,9% assume erro uniforme. Erros humanos reais não são uniformes. Isso **não foi medido**. Também não ajuda nos CNPJs com letras já emitidos.
5. **Por que o decodificador só sugere?** Com 2 erros, 2,1% dos consertos sairiam errados.
6. **O que seria preciso para refutar?** Achar uma troca de 1 caractere em raiz que obedeça à regra e mantenha o DV válido. O script diz que não existe.

## 6. Exercícios para fazer você mesmo

- [ ] Implementar o DV oficial em Java e comparar com `pesquisa/cnpj_core.py` em 1.000 CNPJs aleatórios.
- [ ] Achar à mão outra colisão (par de letras da mesma classe) e validar em um validador externo.
- [ ] Calcular `T` de `34.DC0.XNA/0001-72` com caneta e papel.
- [ ] Rodar `python3 reproduzir.py --mc 600` e comparar com a fração exata.
