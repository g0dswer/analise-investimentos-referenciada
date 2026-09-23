/-!
# FCFF — modo `fcff` de `scripts/acoes.py`

`NOPAT = EBIT × (1 − imposto)`, sem escudo fiscal automático para EBIT negativo;
`FCFF = NOPAT + D&A − CAPEX − ΔCG`.
-/

namespace Analise.Fcff

def nopat (ebit imposto : Rat) (escudo : Bool) : Rat :=
  if ebit < 0 ∧ escudo = false then ebit else ebit * (1 - imposto)

def fcff (ebit imposto da capex dcg : Rat) (escudo : Bool := false) : Rat :=
  nopat ebit imposto escudo + da - capex - dcg

/-- `examples/fcff.json`: `120 × (1 − 0,25) + 15 − 30 − 7 = 68`. -/
theorem exemplo_fcff : fcff 120 (1 / 4) 15 30 7 = 68 := by decide +kernel

/-- Sem escudo fiscal, o NOPAT de um prejuízo nunca excede o NOPAT com escudo:
a convenção padrão do helper é conservadora. -/
theorem sem_escudo_conservador {ebit imposto : Rat} (h : ebit < 0) (ht : 0 ≤ imposto) :
    nopat ebit imposto false ≤ nopat ebit imposto true := by
  unfold nopat
  have := Rat.mul_nonneg (by grind : (0 : Rat) ≤ -ebit) ht
  split <;> split <;> grind

/-- Soma de `f 0, …, f (n−1)`. -/
def somaAte (f : Nat → Rat) : Nat → Rat
  | 0 => 0
  | n + 1 => somaAte f n + f n

/-- "Aumento do saldo de capital de giro consome caixa; não subtrair o saldo inteiro a cada
ano": as variações anuais somam exatamente a diferença entre o saldo final e o inicial. -/
theorem variacoes_de_capital_de_giro (saldo : Nat → Rat) (n : Nat) :
    somaAte (fun t => saldo (t + 1) - saldo t) n = saldo n - saldo 0 := by
  induction n with
  | zero => simp only [somaAte]; grind
  | succ n ih => simp only [somaAte, ih]; grind

end Analise.Fcff
