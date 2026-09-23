/-!
# Ponte FCFF → acionista — modo `equity_bridge` de `scripts/acoes.py`

A skill afirma: "Não descontar FCFF por Ke nem dividendos por WACC". No caso de
referência (perpetuidade sem crescimento, dívida perpétua `D` a custo `kd`, alíquota `t`,
pesos a valor de mercado), prova-se que

* `FCFF / WACC − D = E = FCFE / Ke`: as duas rotas coincidem;
* `FCFF / Ke − D = E − D (1 − kd(1−t)/Ke)`: descontar FCFF por Ke subavalia o
  acionista sempre que `kd(1−t) < Ke` e `D > 0`.

O caso é uma verificação de consistência das convenções, não um modelo geral de
estrutura de capital.
-/

namespace Analise.Ponte

variable (E D ke kd t : Rat)

/-- FCFE perpétuo de um acionista avaliado em `E` ao custo `ke`. -/
def fcfe : Rat := ke * E
/-- FCFF = FCFE + juros após impostos (sem amortização na perpetuidade). -/
def fcff : Rat := fcfe E ke + kd * (1 - t) * D
/-- WACC com pesos a valor de mercado. -/
def wacc : Rat := (E * ke + D * kd * (1 - t)) / (E + D)

theorem rotas_coincidem (hE : 0 < E) (hD : 0 ≤ D) (hke : 0 < ke) (hkd : 0 ≤ kd) (ht : t ≤ 1) :
    fcff E D ke kd t / wacc E D ke kd t - D = E := by
  have hden : 0 < E * ke + D * kd * (1 - t) := by
    have h1 : 0 < E * ke := Rat.mul_pos hE hke
    have h2 : 0 ≤ D * kd * (1 - t) := Rat.mul_nonneg (Rat.mul_nonneg hD hkd) (by grind)
    grind
  have hED : E + D ≠ 0 := by grind
  unfold fcff fcfe wacc
  have hn : E * ke + D * kd * (1 - t) ≠ 0 := Rat.ne_of_gt hden
  grind

theorem fcff_por_ke (hke : 0 < ke) :
    fcff E D ke kd t / ke - D = E - D * (1 - kd * (1 - t) / ke) := by
  have := Rat.ne_of_gt hke
  unfold fcff fcfe; grind

theorem fcff_por_ke_subavalia (hke : 0 < ke) (hD : 0 < D) (hk : kd * (1 - t) < ke) :
    fcff E D ke kd t / ke - D < E := by
  rw [fcff_por_ke E D ke kd t hke]
  have hq : kd * (1 - t) / ke < 1 := by
    rw [Rat.div_lt_iff hke]; grind
  have := Rat.mul_pos hD (by grind : (0 : Rat) < 1 - kd * (1 - t) / ke)
  grind

end Analise.Ponte
