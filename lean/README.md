# Verificação formal em Lean 4

Provas, em aritmética racional exata (`Rat`), das identidades que sustentam os helpers
de `scripts/` e algumas afirmações de `references/`. Usa só o núcleo do Lean, sem
Mathlib nem outras dependências.

```bash
cd lean
lake build        # toolchain fixado em lean-toolchain
```

Todos os teoremas dependem apenas dos axiomas padrão do Lean (`propext`,
`Classical.choice`, `Quot.sound`). Não há `sorry` nem `native_decide`. Para conferir,
acrescente `#print axioms Analise.Dcf.converge` (ou outro nome) a um arquivo que importe `Analise`.

## O que está provado

| Módulo | Afirmação | Código ou texto correspondente |
|---|---|---|
| `Conversao` | Conservação: cotas inteiras × destino + residual = líquido total; `0 ≤ residual < destino`; razão exata `k` ⇒ `k` cotas e residual zero; `0 ≤ líquido ≤ origem` | `calculos.py`, modo `conversion` |
| `Conversao` | O algoritmo anterior (piso da razão arredondada a 28 dígitos) entrega 99 cotas e residual 30 para 300 cotas de 10 → destino 30, violando `residual < destino` | Corrigido com `divmod` exato |
| `Dcf` | `examples/dcf.json` vale exatamente `91840/1331`; o valor impresso difere no último dígito, com erro `< 10⁻²⁶` | `calculos.py`, modo `dcf` |
| `Dcf` | Com `−1 < g < r` (as guardas do script), `0 < (1+g)/(1+r) < 1`; soma parcial `S_n = TV(1 − qⁿ)`; cauda `TV·qⁿ`; convergência para `CF_N(1+g)/(r−g)` | `terminal_growth` |
| `TerminalRoic` | `TV − NOPAT/r = NOPAT·g·(ROIC − r) / (ROIC·r·(r − g))`: crescimento cria valor se `ROIC > r`, é neutro se `ROIC = r` e destrói se `ROIC < r` | `acoes.py`, modo `terminal_roic` |
| `TerminalRoic` | `g ≤ ROIC` ⇒ fluxo terminal não negativo; Gordon do modo `dcf` coincide com este terminal **somente** quando `CF_N(1+g) = NOPAT_{N+1}(1 − g/ROIC)` | Coerência entre os dois modos |
| `Ponte` | Perpetuidade sem crescimento com dívida perpétua: `FCFF/WACC − D = FCFE/Ke`; `FCFF/Ke − D` subavalia o acionista quando `kd(1−t) < Ke` e `D > 0` | "Não descontar FCFF por Ke" |
| `Fcff` | `examples/fcff.json` = 68; sem escudo fiscal, NOPAT de prejuízo ≤ NOPAT com escudo; variações de capital de giro somam `saldo final − saldo inicial` | `acoes.py`, modo `fcff` |
| `Metricas` | `1 − P/V = u/(1+u)` com `u = V/P − 1`; Bernoulli; DY composto ≥ `12·dy`; passo de reinvestimento autofinanciado | `metrics`, `reinvested_return` |
| `Tir` | Média de TIRs (100% e 10%) não é TIR da carteira; fluxos `−1, +5, −6` têm duas TIRs (100% e 200%) | Advertências de `calculos.md` e `fiis.md` |

## O que não está provado

- **Correspondência com o Python.** As definições em Lean foram escritas à mão a partir
  do código; não há extração nem geração de código. Um erro de transcrição não seria
  detectado. Os testes em `tests/` reduzem, mas não eliminam, esse risco.
- **Arredondamento de `Decimal`.** Os modelos usam racionais exatos. Só a conversão foi
  modelada com o arredondamento real, porque ali ele altera um resultado discreto.
- **Premissas econômicas.** Nenhum teorema diz se uma taxa, um crescimento ou um ROIC
  são adequados a um ativo. As provas tratam da consistência algébrica dos cálculos.
- **Gráficos, PDF e texto das referências** não são objetos formalizáveis aqui.
- **Valores reais** (`ℝ`) e limites exigiriam Mathlib; a convergência de Gordon foi
  provada na forma "para todo ε > 0 existe n", sem limites.
