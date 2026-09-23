/-!
# Conversão de cotas — modo `conversion` de `scripts/calculos.py`

Especificação em aritmética racional exata. Cotas inteiras são
`⌊cotas × líquido / destino⌋` e o residual é o valor líquido total menos o valor
das cotas inteiras. As provas mostram conservação de valor e `0 ≤ residual < destino`.

A seção final modela o algoritmo original do script, que obtinha as cotas inteiras
a partir da razão arredondada a 28 dígitos, e prova que ele viola `residual < destino`
num caso com razão exata 1:3.
-/

namespace Analise.Conversao

/-- Imposto por cota: `max(valor de origem − custo, 0) × alíquota`. -/
def impostoPorCota (origem custo aliquota : Rat) : Rat :=
  max (origem - custo) 0 * aliquota

/-- Valor líquido por cota após o imposto simplificado. -/
def liquidoPorCota (origem custo aliquota : Rat) : Rat :=
  origem - impostoPorCota origem custo aliquota

/-- Cotas inteiras recebidas: piso do valor líquido total dividido pelo valor de destino. -/
def cotasInteiras (cotas liquido destino : Rat) : Int :=
  (cotas * liquido / destino).floor

/-- Residual pelo valor de destino: líquido total menos o valor das cotas inteiras. -/
def residual (cotas liquido destino : Rat) : Rat :=
  cotas * liquido - cotasInteiras cotas liquido destino * destino

/-- Conservação: cotas inteiras × destino + residual = valor líquido total. -/
theorem conservacao (cotas liquido destino : Rat) :
    cotasInteiras cotas liquido destino * destino + residual cotas liquido destino
      = cotas * liquido := by
  unfold residual; grind

theorem residual_nao_negativo (cotas liquido destino : Rat) (h : 0 < destino) :
    0 ≤ residual cotas liquido destino := by
  have hle := Rat.floor_le (cotas * liquido / destino)
  have hmul := Rat.mul_le_mul_of_nonneg_right hle (Rat.le_of_lt h)
  rw [Rat.div_mul_cancel (Rat.ne_of_gt h)] at hmul
  unfold residual cotasInteiras; grind

theorem residual_menor_que_destino (cotas liquido destino : Rat) (h : 0 < destino) :
    residual cotas liquido destino < destino := by
  have hlt := Rat.lt_floor_add_one (cotas * liquido / destino)
  have hmul := Rat.mul_lt_mul_of_pos_right hlt h
  rw [Rat.div_mul_cancel (Rat.ne_of_gt h)] at hmul
  unfold residual cotasInteiras
  simp only [Rat.intCast_add, Rat.intCast_one] at hmul
  grind

/-- Se o valor líquido total corresponde exatamente a `k` cotas de destino,
recebem-se `k` cotas inteiras e residual zero. -/
theorem conversao_exata (cotas liquido destino : Rat) (k : Int) (h : 0 < destino)
    (hk : cotas * liquido = k * destino) :
    cotasInteiras cotas liquido destino = k ∧ residual cotas liquido destino = 0 := by
  have hq : cotas * liquido / destino = (k : Rat) := by
    rw [hk, Rat.mul_div_cancel (Rat.ne_of_gt h)]
  have hk' : cotasInteiras cotas liquido destino = k := by
    unfold cotasInteiras; rw [hq, Rat.floor_intCast]
  refine ⟨hk', ?_⟩
  unfold residual; rw [hk', hk]; grind

/-- O imposto simplificado nunca torna o valor líquido negativo nem maior que a origem,
desde que origem, custo e alíquota estejam nas faixas aceitas pelo script. -/
theorem liquido_nao_negativo (origem custo aliquota : Rat) (ho : 0 ≤ origem)
    (hc : 0 ≤ custo) (ha1 : aliquota ≤ 1) :
    0 ≤ liquidoPorCota origem custo aliquota := by
  unfold liquidoPorCota impostoPorCota
  by_cases hg : origem - custo ≤ 0
  · have : max (origem - custo) 0 = 0 := by grind
    rw [this]; grind
  · have hm : max (origem - custo) 0 = origem - custo := by grind
    rw [hm]
    have h1 := Rat.mul_le_mul_of_nonneg_left ha1 (by grind : (0 : Rat) ≤ origem - custo)
    grind

theorem liquido_le_origem (origem custo aliquota : Rat) (ha0 : 0 ≤ aliquota) :
    liquidoPorCota origem custo aliquota ≤ origem := by
  unfold liquidoPorCota impostoPorCota
  have := Rat.mul_nonneg (by grind : (0 : Rat) ≤ max (origem - custo) 0) ha0
  grind

/-! ## Algoritmo original do script: contraexemplo

`calculos.py` calculava `ratio = net / target` com a precisão padrão de `Decimal`
(28 dígitos significativos), depois `theoretical_units = units × ratio` e
`whole = floor(theoretical_units)`. Para 300 cotas com líquido 10,00 e destino 30,00,
a razão exata é 1/3; arredondada, vira 0,333…3 com 28 algarismos. -/

/-- `Decimal('10') / Decimal('30')` com 28 dígitos significativos. -/
def razaoArredondada : Rat := 3333333333333333333333333333 / 10 ^ 28

/-- Cotas inteiras pelo algoritmo original: piso de `300 × razão arredondada`. -/
def cotasInteirasOriginal : Int := (300 * razaoArredondada).floor

/-- Residual pelo algoritmo original: `units × net − whole × target`. -/
def residualOriginal : Rat := 300 * 10 - cotasInteirasOriginal * 30

theorem original_perde_uma_cota : cotasInteirasOriginal = 99 := by decide +kernel

/-- O algoritmo original devolve um residual igual ao valor de uma cota inteira. -/
theorem original_viola_invariante : ¬ residualOriginal < 30 := by decide +kernel

/-- A especificação exata entrega 100 cotas e residual zero no mesmo caso. -/
theorem especificacao_no_mesmo_caso :
    cotasInteiras 300 10 30 = 100 ∧ residual 300 10 30 = 0 :=
  conversao_exata 300 10 30 100 (by decide +kernel) (by decide +kernel)

end Analise.Conversao
