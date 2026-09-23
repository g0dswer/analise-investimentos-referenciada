# Ferramentas de cálculo

Os scripts recebem JSON, não coletam dados nem escolhem premissas. Taxas são frações (`0.10` corresponde a 10%). Os cálculos usam 40 dígitos significativos; resultados decimais saem como strings com até 28 dígitos, arredondados a partir do valor calculado, e zero sai como `"0"`. Campos booleanos exigem `true` ou `false` do JSON; strings como `"false"` são rejeitadas. Conservar entradas, saídas e fontes junto da análise.

## Desconto e métricas — `scripts/calculos.py`

Executar `python3 scripts/calculos.py entrada.json`.

| `mode` | Entradas | Resultado e convenção |
|---|---|---|
| `dcf` | `cashflows`, `discount_rate` ou `discount_factors`; opcionais `terminal_value` ou `terminal_growth`, e com este `terminal_nopat`, `ronic`, `terminal_tolerance` | Fluxos em t=1…N; fatores são denominadores acumulados |
| `cap_rate` | `annual_noi`, `cap_rate`, `units`; opcionais `other_net_assets`, `debt` | NOI/cap rate, ajustes patrimoniais e valor por cota |
| `metrics` | `price`; opcionais `target_price`, `nav_per_unit`, `monthly_dividend`, `entry_price`, `distributions_received` | Upside, margem sobre valor justo, P/VP, yields e retorno sem reinvestimento |
| `reinvested_return` | `initial_price`, `observations` com `date`, `price`, `dividend` | Reinvestimento integral por data, começando com uma cota |
| `conversion` | `source_value`, `target_value`, `cost_basis`, `tax_rate`, `source_units`; opcionais `old_dividend`, `new_dividend` | Simulação simplificada de conversão líquida, cotas inteiras e residual |

No DCF, `terminal_value` e `terminal_growth` são alternativas. Com crescimento, o terminal é `CF_N × (1+g)/(r−g)`, descontado em N. Se ambos forem omitidos, o código usa terminal zero: isso só representa uma avaliação completa quando há fundamento econômico para ausência de valor residual. Com fatores variáveis, calcular e informar o terminal explicitamente.

O Gordon usa `CF_N × (1+g)` como primeiro fluxo terminal e, portanto, mantém o reinvestimento do último ano projetado. Ele só coincide com o terminal por RONIC quando `CF_N × (1+g) = NOPAT_{N+1} × (1 − g/RONIC)`. A diferença entre os dois valores terminais é `NOPAT_{N+1} × (reinvestimento exigido − implícito)/(r−g)`, com implícito `1 − CF_N(1+g)/NOPAT_{N+1}` e exigido `g/RONIC`. Informar `terminal_nopat` (NOPAT de N+1) e `ronic` junto com `terminal_growth` faz o script comparar as duas taxas; diferença acima de `terminal_tolerance` (padrão `0.001`, isto é, 0,1 ponto percentual) é rejeitada. `terminal_check.status` vale `coerente` ou, sem esses campos, `não verificado`. Para dividendos ou FCFE, a coerência depende de retenção e ROE, não de RONIC. Não confundir taxa spot por prazo com taxa anual encadeada.

O modo `cap_rate` assume zero para ajustes patrimoniais opcionais omitidos. Em análise real, omissão de dívida/caixa não comprova ausência; informar valores confirmados ou interromper a ponte. Não somar cap rate e DCF sobre o mesmo imóvel como duas fontes independentes de valor.

Na conversão, imposto por cota = `max(valor de origem − custo, 0) × alíquota`. O saldo líquido determina cotas teóricas, cotas inteiras e residual pelo valor de destino; cotas inteiras e residual vêm de divisão exata, e entradas que exigiriam arredondamento são rejeitadas. É uma convenção simplificada, sem regras automáticas de tributação, compensação, leilão ou custos. Verificar as condições do evento antes de usar. O residual não recebe dividendos como se fosse cota.

DY anualizado simples e composto são convenções, não previsão. Retorno realizado de 12 meses exige proventos efetivos. No reinvestimento, preços e dividendos devem estar ajustados de forma compatível; não somar dividendos a preços já ajustados por retorno total. O helper não trata aportes, retiradas, impostos ou eventos societários.

O script não resolve TIR/XIRR. Para isso, montar fluxos com datas, investimento inicial negativo, proventos, custos e saída; usar um solver adequado, verificar VPL residual e investigar múltiplas raízes quando houver mudanças de sinal adicionais.

## Fluxo e ponte — `scripts/acoes.py`

Executar `python3 scripts/acoes.py entrada.json`.

- `fcff`: `unit` e lista `periods`; cada item exige `period`, `ebit`, `tax_rate`, `da`, `capex`, `delta_working_capital`. NOPAT = EBIT × (1−imposto); FCFF = NOPAT + D&A − CAPEX − ΔCG. EBIT negativo não gera escudo fiscal automático; `loss_tax_shield: true` requer fundamento separado.
- `terminal_roic`: `nopat_next`, `discount_rate`, `growth`, `ronic`. RONIC é o retorno sobre o capital novo, que pode diferir do ROIC da base existente; `roic` continua aceito como nome antigo do mesmo campo. Reinvestimento = g/RONIC; fluxo terminal = NOPAT seguinte × (1−g/RONIC); valor terminal = fluxo/(r−g). O helper restringe o regime a 0≤g<r e g≤RONIC. Outros regimes precisam de modelo explícito.
- `equity_bridge`: `cashflow_type`, `present_value`, `shares`, `money_scale`. Para `fcff`, informar também `cash`, `debt`, `other_nonoperating_assets`, `minorities`. Para `fcfe` ou `dividends`, o valor já pertence ao acionista e ajustes automáticos de caixa/dívida são rejeitados.

`shares` é quantidade real de ações; `money_scale` converte a unidade monetária da planilha para moeda por ação. `unit_composition` multiplica ações equivalentes apenas com `equal_economic_rights: true`; classes com direitos diferentes exigem avaliação própria.

## Exemplo sintético

Os arquivos em `examples/` usam números fictícios para demonstrar execução. Não são dados ou previsões de um ativo real.

```bash
python3 scripts/acoes.py examples/fcff.json
python3 scripts/calculos.py examples/dcf.json
```

O exemplo FCFF resulta em 68 unidades monetárias: `120 × (1−0,25) + 15 − 30 − 7`. O DCF contém três pagamentos fictícios e terminal explicitamente nulo.
