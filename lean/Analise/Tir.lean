/-!
# TIR — advertências de `references/calculos.md` e `references/fiis.md`

Contraexemplos exatos para duas afirmações da skill:
* "a média de TIRs individuais não é TIR da carteira";
* "investigar múltiplas raízes quando houver mudanças de sinal adicionais".
-/

namespace Analise.Tir

/-- VPL de fluxos em `t = 0, 1, …, N`. -/
def vplDesde (r : Rat) (t : Nat) : List Rat → Rat
  | [] => 0
  | c :: cs => c / (1 + r) ^ t + vplDesde r (t + 1) cs

def vpl (r : Rat) (fluxos : List Rat) : Rat := vplDesde r 0 fluxos

/-- Ativo A: TIR 100% em um período. Ativo B: TIR 10% em dois períodos.
A carteira com os dois não tem TIR igual à média simples, 55%. -/
theorem media_das_tir_nao_e_tir_da_carteira :
    vpl 1 [-1, 2] = 0 ∧ vpl (1 / 10) [-1, 0, 121 / 100] = 0
      ∧ vpl (55 / 100) [-2, 2, 121 / 100] ≠ 0 := by
  decide +kernel

/-- Fluxos `−1, +5, −6` têm duas TIRs: 100% e 200%. -/
theorem duas_tir : vpl 1 [-1, 5, -6] = 0 ∧ vpl 2 [-1, 5, -6] = 0 := by
  decide +kernel

end Analise.Tir
