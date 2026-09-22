# Relatório, figuras e PDF

## Estrutura adaptável

1. Ativo, data-base, fontes e resumo da tese.
2. Negócio, setor, concorrência e drivers econômicos.
3. Governança, contratos, qualidade dos ativos e alocação de capital.
4. Histórico financeiro com reconciliações e unidades.
5. Premissas, projeção, desconto, terminal e ponte por ação/cota.
6. Sensibilidades e riscos com mecanismos e indicadores.
7. Conclusão condicionada e dados que mudariam a avaliação.
8. Fontes e memória de cálculo.

Adaptar a extensão à pergunta e ao material disponível. Explicar conceitos com evidência e interpretação, evitando uma ficha de múltiplos sem tese. Separar preço atual, valor justo presente, alvo futuro e teto de compra.

## Figuras

Executar `python3 scripts/graficos.py entrada.json output/figura` para gerar PNG e SVG. O JSON exige `title`, `unit`, `source`, `labels` e `series` com `name`/`values`; admite `kind` (`line` ou `bar`), `x_label`, `note` e `forecast_start` (índice da primeira projeção). Valores `null` representam lacunas, não zero.

Escolher gráficos que esclareçam mix, margem, volume/preço, concentração, dívida, reinvestimento ou sensibilidade. Identificar unidade, fonte e período; distinguir realizado e projetado. Não digitalizar valores ilegíveis como se fossem observações precisas.

```bash
python3 scripts/graficos.py examples/chart.json output/receita
```

## PDF

Instalar dependências de `scripts/requirements.txt` em ambiente virtual. Executar:

```bash
python3 scripts/relatorio_pdf.py relatorio.md output/relatorio.pdf
```

Criar o diretório de saída antes. O renderizador suporta títulos, parágrafos, listas simples, tabelas, blocos de código e imagens locais. Caminhos de imagem são relativos ao Markdown. Links ficam como texto; não é um conversor completo de Markdown. Ajustar manualmente documentos com tabelas largas, fórmulas extensas ou exigências editoriais específicas.

Renderizar e conferir as páginas finais: tabelas legíveis, imagens com fonte e unidade, títulos sem sobreposição e conclusão presente. Guardar Markdown, entradas e saídas do cálculo para que a apresentação possa ser regenerada.
