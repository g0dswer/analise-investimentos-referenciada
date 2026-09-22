# Evidências e revisão

## Base de dados

Manter uma tabela com indicador, valor, unidade, denominador, período, fonte e classificação. Diferenciar data de publicação, data do preço e período financeiro. Uma tabela extraída pode misturar moedas, escalas ou períodos; conferir seus cabeçalhos visualmente antes de modelar.

Campos ausentes ficam indisponíveis. Distinguir ausência no pacote recebido de ausência no documento original. Um ponto sem data não deve entrar silenciosamente em um vetor anual. Usar campo separado, com ano nulo, e rotular qualquer comparação com cenário datado como condicional.

## Construção do cenário

- Separar receita de segmentos e reconciliar eliminações. Uma razão entre duas receitas não demonstra que uma esteja contida na outra.
- Classificar saldos versus fluxos, valores brutos versus líquidos e consolidado versus participação econômica.
- Aplicar regras temporais explicitamente: degrau em um ano não é interpolação; mudanças de incentivos devem afetar todas as linhas relacionadas.
- Identificar interpolação e extrapolação próprias. Não converter receita histórica multiplicada por margem normalizada ou imposto projetado em resultado histórico observado.
- Explicar a base, unidade, sinal e período de ajustes tributários, arrendamento, sinergias e itens extraordinários. Evitar dupla contagem de benefícios já presentes no resultado-base.
- Um segmento material indisponível impede chamar o subtotal dos demais de receita total.

## Governança e riscos

Analisar controle, acordos, composição do conselho, incentivos, diluição e transações relacionadas. Separar remuneração prevista e observada; não somar participações de datas diferentes. Ao discutir controvérsias, distinguir alegação, resposta da companhia e conclusão comprovada.

Organizar cada risco por evidência, transmissão econômica, possível mitigante, limite do mitigante e indicador de acompanhamento. Não transformar riscos qualitativos em ajustes arbitrários de valor sem cenário explícito.

## Revisão

Gerar tabelas e gráficos a partir da mesma memória de cálculo. Conferir somas, unidades e pelo menos uma identidade material em cada etapa. Uma correção deve alcançar texto, tabela, metadados, script, JSON, gráfico e conclusão.

Confrontar taxa, inflação, moeda e periodicidade. Dados ajustados por desdobramentos e dividendos precisam usar convenções compatíveis. Separar testes sintéticos de software de evidência econômica sobre uma empresa real.

Comparações históricas não demonstram coleta autônoma nem previsão fora da amostra. Publicar a extensão efetiva da verificação e as entradas que continuam indisponíveis.
