/-!
# Métricas — modos `metrics` e `reinvested_return` de `scripts/calculos.py`
-/

namespace Analise.Metricas

/-- `margin_to_fair_value = 1 − P/V` é a transformação `u/(1+u)` do `upside = V/P − 1`. -/
theorem margem_e_upside {p v : Rat} (hp : 0 < p) (hv : 0 < v) :
    1 - p / v = (v / p - 1) / (v / p) := by
  have := Rat.ne_of_gt hp; have := Rat.ne_of_gt hv
  grind

/-- Desigualdade de Bernoulli: `1 + n·x ≤ (1+x)ⁿ` para `x ≥ 0`. -/
theorem bernoulli {x : Rat} (hx : 0 ≤ x) (n : Nat) : 1 + n * x ≤ (1 + x) ^ n := by
  induction n with
  | zero => simp [Rat.pow_zero]; grind
  | succ n ih =>
    rw [Rat.pow_succ, Rat.natCast_add, Rat.natCast_ofNat]
    have hn : (0 : Rat) ≤ n := Rat.natCast_nonneg
    have h1 := Rat.mul_le_mul_of_nonneg_right ih (by grind : (0 : Rat) ≤ 1 + x)
    have h2 := Rat.mul_nonneg (Rat.mul_nonneg hn hx) hx
    grind

/-- O rendimento anual composto nunca fica abaixo do simples (`12·dy`) quando `dy ≥ 0`. -/
theorem composto_ao_menos_simples {dy : Rat} (h : 0 ≤ dy) : 12 * dy ≤ (1 + dy) ^ 12 - 1 := by
  have := bernoulli h 12
  simp only [Rat.natCast_ofNat] at this
  grind

/-- Um passo do reinvestimento integral é autofinanciado: o valor da posição após
reinvestir é o valor antes do provento mais o caixa recebido. -/
theorem reinvestimento_autofinanciado {cotas preco provento : Rat} (hp : preco ≠ 0) :
    (cotas + cotas * provento / preco) * preco = cotas * preco + cotas * provento := by
  grind

end Analise.Metricas
