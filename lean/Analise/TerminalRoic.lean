import Analise.Dcf

/-!
# Terminal com RONIC — modo `terminal_roic` de `scripts/acoes.py`

`TV = NOPAT_{N+1} × (1 − g/RONIC) / (r − g)`, com reinvestimento `g/RONIC`, em que
RONIC é o retorno sobre o capital novo.

Resultados:
* identidade da criação de valor pelo crescimento: o sinal de `TV − NOPAT/r`
  é o sinal de `RONIC − r`;
* com `RONIC = r`, o crescimento não altera o valor;
* as guardas do helper (`0 ≤ g ≤ RONIC`) tornam o fluxo terminal não negativo;
* o terminal de Gordon do modo `dcf` coincide com este apenas quando o fluxo
  `CF_N(1+g)` é igual a `NOPAT_{N+1}(1 − g/RONIC)`; é essa igualdade que o modo `dcf`
  verifica quando recebe `terminal_nopat` e `ronic`.
-/

namespace Analise.TerminalRoic

def valorTerminal (nopat r g ronic : Rat) : Rat := nopat * (1 - g / ronic) / (r - g)

/-- Valor criado pelo crescimento, relativo à perpetuidade sem crescimento `NOPAT/r`. -/
theorem criacao_de_valor {nopat r g ronic : Rat} (hr : 0 < r) (hronic : 0 < ronic) (hg : g < r) :
    valorTerminal nopat r g ronic - nopat / r
      = nopat * g * (ronic - r) / (ronic * r * (r - g)) := by
  have h1 : ronic ≠ 0 := Rat.ne_of_gt hronic
  have h2 : r ≠ 0 := Rat.ne_of_gt hr
  have h3 : r - g ≠ 0 := by grind
  unfold valorTerminal
  grind

/-- Com retorno igual ao custo de capital, o valor independe do crescimento. -/
theorem crescimento_neutro {nopat r g : Rat} (hr : 0 < r) (hg : g < r) :
    valorTerminal nopat r g r = nopat / r := by
  have := criacao_de_valor (nopat := nopat) (g := g) hr hr hg
  grind

private theorem pos_quociente {a b : Rat} (ha : 0 < a) (hb : 0 < b) : 0 < a / b := by
  rw [Rat.div_def]; exact Rat.mul_pos ha (Rat.inv_pos.mpr hb)

/-- Crescimento com RONIC acima da taxa cria valor. -/
theorem crescimento_cria_valor {nopat r g ronic : Rat} (hn : 0 < nopat) (hr : 0 < r)
    (hg0 : 0 < g) (hg : g < r) (hronic : r < ronic) :
    nopat / r < valorTerminal nopat r g ronic := by
  have hronic0 : 0 < ronic := by grind
  have hnum : 0 < nopat * g * (ronic - r) := Rat.mul_pos (Rat.mul_pos hn hg0) (by grind)
  have hden : 0 < ronic * r * (r - g) := Rat.mul_pos (Rat.mul_pos hronic0 hr) (by grind)
  have := criacao_de_valor (nopat := nopat) hr hronic0 hg
  have := pos_quociente hnum hden
  grind

/-- Crescimento com RONIC abaixo da taxa destrói valor. -/
theorem crescimento_destroi_valor {nopat r g ronic : Rat} (hn : 0 < nopat) (hr : 0 < r)
    (hg0 : 0 < g) (hg : g < r) (hronic0 : 0 < ronic) (hronic : ronic < r) :
    valorTerminal nopat r g ronic < nopat / r := by
  have hnum : 0 < nopat * g * (r - ronic) := Rat.mul_pos (Rat.mul_pos hn hg0) (by grind)
  have hden : 0 < ronic * r * (r - g) := Rat.mul_pos (Rat.mul_pos hronic0 hr) (by grind)
  have := criacao_de_valor (nopat := nopat) hr hronic0 hg
  have hq := pos_quociente hnum hden
  have : nopat * g * (ronic - r) / (ronic * r * (r - g))
      = -(nopat * g * (r - ronic) / (ronic * r * (r - g))) := by grind
  grind

/-- As guardas do helper garantem fluxo terminal não negativo (reinvestimento ≤ 100%). -/
theorem fluxo_terminal_nao_negativo {nopat g ronic : Rat} (hn : 0 ≤ nopat) (hronic : 0 < ronic)
    (hle : g ≤ ronic) : 0 ≤ nopat * (1 - g / ronic) := by
  have : g / ronic ≤ 1 := by
    rw [Rat.div_def]
    have := Rat.mul_le_mul_of_nonneg_right hle (Rat.le_of_lt (Rat.inv_pos.mpr hronic))
    rw [Rat.mul_inv_cancel _ (Rat.ne_of_gt hronic)] at this
    exact this
  exact Rat.mul_nonneg hn (by grind)

/-- O Gordon do modo `dcf` e este terminal coincidem exatamente quando o fluxo usado
por Gordon, `CF_N(1+g)`, é igual ao fluxo terminal implícito `NOPAT_{N+1}(1 − g/RONIC)`. -/
theorem coincide_com_gordon {cf nopat r g ronic : Rat} (hg : g < r) :
    Analise.Dcf.gordon cf g r = valorTerminal nopat r g ronic
      ↔ cf * (1 + g) = nopat * (1 - g / ronic) := by
  have hrg : r - g ≠ 0 := by grind
  unfold Analise.Dcf.gordon valorTerminal
  constructor
  · intro h
    have := congrArg (· * (r - g)) h
    rwa [Rat.div_mul_cancel hrg, Rat.div_mul_cancel hrg] at this
  · intro h; rw [h]

/-- A diferença entre o Gordon do modo `dcf` e este terminal é
`NOPAT × (exigido − implícito) / (r − g)`, com reinvestimento implícito
`1 − CF_N(1+g)/NOPAT` e exigido `g/RONIC`. O modo `dcf` limita `exigido − implícito`
por `terminal_tolerance`; o erro no valor terminal fica, assim, proporcional a
`NOPAT/(r − g)` e não depende do nível de reinvestimento. -/
theorem diferenca_entre_terminais {cf nopat r g ronic : Rat} (hn : nopat ≠ 0) (hg : g < r) :
    Analise.Dcf.gordon cf g r - valorTerminal nopat r g ronic
      = nopat * (g / ronic - (1 - cf * (1 + g) / nopat)) / (r - g) := by
  have hrg : r - g ≠ 0 := by grind
  unfold Analise.Dcf.gordon valorTerminal
  grind

end Analise.TerminalRoic
