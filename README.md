# Análise de investimentos referenciada

Skill para Codex que organiza análises de ações e fundos imobiliários em português, com fontes rastreáveis, modelos financeiros explícitos, gráficos e relatórios em PDF.

## Instalação

Para instalar em um diretório de skills ainda não existente:

```bash
git clone https://github.com/g0dswer/analise-investimentos-referenciada.git ~/.codex/skills/analise-investimentos-referenciada
```

Se já houver uma instalação, preserve suas alterações e atualize os arquivos de forma consciente. A skill usa o mesmo nome de invocação:

```text
$analise-investimentos-referenciada Analise o ativo solicitado na data-base indicada e entregue relatório com fontes, premissas, riscos, gráficos e memória de cálculo.
```

## Recursos

- Roteiros para ações, bancos, seguradoras, concessões e fundos imobiliários.
- Helpers de FCFF, DCF, terminal com ROIC, ponte por ação/cota, cap rate e métricas.
- Figuras PNG/SVG e exportação de Markdown simples para PDF.
- Dados ausentes, cenários próprios e limites de reprodução explicitados.

Os exemplos são inteiramente sintéticos. O repositório não contém análises de ativos reais, documentos de terceiros, dados de clientes ou bases de mercado. Não há notas de desempenho ou alegações de validação de estratégias de investimento.

## Ferramentas opcionais

Os cálculos usam apenas a biblioteca padrão do Python. Para gráficos e PDF:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r scripts/requirements.txt
mkdir -p output
python scripts/acoes.py examples/fcff.json
python scripts/calculos.py examples/dcf.json
python scripts/graficos.py examples/chart.json output/receita
```

## Verificação

```bash
python3 -m unittest discover -s tests
cd lean && lake build
```

Os testes conferem os exemplos e as invariantes da conversão. O diretório [lean/](lean/README.md) prova em Lean 4 as identidades algébricas dos helpers e lista o que não é coberto: a correspondência com o Python é manual, e nenhuma prova valida premissas econômicas.

Consulte [SKILL.md](SKILL.md) e [as interfaces de cálculo](references/calculos.md). A skill precisa de documentos e dados adequados a cada análise; ela não inclui integração automática com provedores financeiros nem recomendações prontas.

## Licença

Código e instruções deste repositório sob [MIT](LICENSE).
