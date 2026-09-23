import Analise.Dcf

/-!
# Terminal com ROIC — modo `terminal_roic` de `scripts/acoes.py`

`TV = NOPAT_{N+1} × (1 − g/ROIC) / (r − g)`, com reinvestimento `g/ROIC`.
Na literatura, o retorno relevante é o do capital novo (RONIC); o helper chama esse
parâmetro de `roic`.

Resultados:
* identidade da criação de valor pelo crescimento: o sinal de `TV − NOPAT/r`
  é o sinal de `ROIC − r`;
* com `ROIC = r`, o crescimento não altera o valor;
* as guardas do helper (`0 ≤ g ≤ ROIC`) tornam o fluxo terminal não negativo;
* o terminal de Gordon do modo `dcf` coincide com este apenas quando o fluxo
  `CF_N(1+g)` é igual a `NOPAT_{N+1}(1 − g/ROIC)`.
-/

namespace Analise.TerminalRoic

def valorTerminal (nopat r g roic : Rat) : Rat := nopat * (1 - g / roic) / (r - g)

/-- Valor criado pelo crescimento, relativo à perpetuidade sem crescimento `NOPAT/r`. -/
theorem criacao_de_valor {nopat r g roic : Rat} (hr : 0 < r) (hroic : 0 < roic) (hg : g < r) :
    valorTerminal nopat r g roic - nopat / r
      = nopat * g * (roic - r) / (roic * r * (r - g)) := by
  have h1 : roic ≠ 0 := Rat.ne_of_gt hroic
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

/-- Crescimento com ROIC acima da taxa cria valor. -/
theorem crescimento_cria_valor {nopat r g roic : Rat} (hn : 0 < nopat) (hr : 0 < r)
    (hg0 : 0 < g) (hg : g < r) (hroic : r < roic) :
    nopat / r < valorTerminal nopat r g roic := by
  have hroic0 : 0 < roic := by grind
  have hnum : 0 < nopat * g * (roic - r) := Rat.mul_pos (Rat.mul_pos hn hg0) (by grind)
  have hden : 0 < roic * r * (r - g) := Rat.mul_pos (Rat.mul_pos hroic0 hr) (by grind)
  have := criacao_de_valor (nopat := nopat) hr hroic0 hg
  have := pos_quociente hnum hden
  grind

/-- Crescimento com ROIC abaixo da taxa destrói valor. -/
theorem crescimento_destroi_valor {nopat r g roic : Rat} (hn : 0 < nopat) (hr : 0 < r)
    (hg0 : 0 < g) (hg : g < r) (hroic0 : 0 < roic) (hroic : roic < r) :
    valorTerminal nopat r g roic < nopat / r := by
  have hnum : 0 < nopat * g * (r - roic) := Rat.mul_pos (Rat.mul_pos hn hg0) (by grind)
  have hden : 0 < roic * r * (r - g) := Rat.mul_pos (Rat.mul_pos hroic0 hr) (by grind)
  have := criacao_de_valor (nopat := nopat) hr hroic0 hg
  have hq := pos_quociente hnum hden
  have : nopat * g * (roic - r) / (roic * r * (r - g))
      = -(nopat * g * (r - roic) / (roic * r * (r - g))) := by grind
  grind

/-- As guardas do helper garantem fluxo terminal não negativo (reinvestimento ≤ 100%). -/
theorem fluxo_terminal_nao_negativo {nopat g roic : Rat} (hn : 0 ≤ nopat) (hroic : 0 < roic)
    (hle : g ≤ roic) : 0 ≤ nopat * (1 - g / roic) := by
  have : g / roic ≤ 1 := by
    rw [Rat.div_def]
    have := Rat.mul_le_mul_of_nonneg_right hle (Rat.le_of_lt (Rat.inv_pos.mpr hroic))
    rw [Rat.mul_inv_cancel _ (Rat.ne_of_gt hroic)] at this
    exact this
  exact Rat.mul_nonneg hn (by grind)

/-- O Gordon do modo `dcf` e este terminal coincidem exatamente quando o fluxo usado
por Gordon, `CF_N(1+g)`, é igual ao fluxo terminal implícito `NOPAT_{N+1}(1 − g/ROIC)`. -/
theorem coincide_com_gordon {cf nopat r g roic : Rat} (hg : g < r) :
    Analise.Dcf.gordon cf g r = valorTerminal nopat r g roic
      ↔ cf * (1 + g) = nopat * (1 - g / roic) := by
  have hrg : r - g ≠ 0 := by grind
  unfold Analise.Dcf.gordon valorTerminal
  constructor
  · intro h
    have := congrArg (· * (r - g)) h
    rwa [Rat.div_mul_cancel hrg, Rat.div_mul_cancel hrg] at this
  · intro h; rw [h]

end Analise.TerminalRoic
