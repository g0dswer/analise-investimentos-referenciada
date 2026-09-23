/-!
# Desconto e perpetuidade — modo `dcf` de `scripts/calculos.py`

* Valor presente com taxa constante e fluxos em `t = 1…N`.
* O exemplo `examples/dcf.json` em aritmética exata.
* A fórmula de Gordon usada pelo script, `CF_N × (1+g)/(r−g)`, é exatamente o limite da
  soma dos fluxos pós-horizonte `CF_N (1+g)^k / (1+r)^k`, quando `−1 < g < r` (as mesmas
  condições que o script exige). Prova-se a forma fechada da soma parcial, a cauda
  `TV · qⁿ` e a convergência, sem recorrer a números reais.
-/

namespace Analise.Dcf

/-- Valor presente de fluxos datados `t+1, t+2, …` com taxa constante `r`. -/
def vpDesde (r : Rat) (t : Nat) : List Rat → Rat
  | [] => 0
  | c :: cs => c / (1 + r) ^ (t + 1) + vpDesde r (t + 1) cs

/-- Valor presente de fluxos em `t = 1…N`, como no script. -/
def vp (r : Rat) (fluxos : List Rat) : Rat := vpDesde r 0 fluxos

/-- `examples/dcf.json`: fluxos 24, 28 e 32 a 10% com terminal nulo. -/
theorem exemplo_dcf : vp (1 / 10) [24, 28, 32] = 91840 / 1331 := by decide +kernel

/-- Valor impresso pelo script: `69.00075131480090157776108190` (28 dígitos). -/
def valorImpresso : Rat := 6900075131480090157776108190 / 10 ^ 26

/-- O último dígito impresso não é exato (arredondamentos intermediários de `Decimal`),
mas o erro é inferior a `10⁻²⁶`: irrelevante economicamente, relevante apenas para não
tratar os 28 dígitos como significativos. -/
theorem impresso_aproxima_exato :
    valorImpresso ≠ 91840 / 1331 ∧ 0 < valorImpresso - 91840 / 1331
      ∧ valorImpresso - 91840 / 1331 < 1 / 10 ^ 26 := by
  decide +kernel

/-! ## Perpetuidade de Gordon -/

/-- Valor terminal na data `N`: `CF_N × (1+g)/(r−g)`. -/
def gordon (cf g r : Rat) : Rat := cf * (1 + g) / (r - g)

/-- Razão entre fluxos consecutivos descontados após o horizonte. -/
def fator (g r : Rat) : Rat := (1 + g) / (1 + r)

/-- Valor em `N` dos `n` primeiros fluxos pós-horizonte `CF_N (1+g)^k`, `k = 1…n`. -/
def somaParcial (cf g r : Rat) : Nat → Rat
  | 0 => 0
  | n + 1 => somaParcial cf g r n + cf * (1 + g) ^ (n + 1) / (1 + r) ^ (n + 1)

/-- As condições que o script exige (`−1 < g < r`) garantem `0 < q < 1`. -/
theorem fator_entre_zero_e_um {g r : Rat} (h1 : -1 < g) (h2 : g < r) :
    0 < fator g r ∧ fator g r < 1 := by
  have hr : 0 < 1 + r := by grind
  unfold fator
  refine ⟨?_, ?_⟩
  · rw [Rat.lt_div_iff hr]; grind
  · rw [Rat.div_lt_iff hr]; grind

theorem potencia_fator (g r : Rat) (hr : 0 < 1 + r) (n : Nat) :
    fator g r ^ n = (1 + g) ^ n / (1 + r) ^ n := by
  induction n with
  | zero => simp [Rat.pow_zero]; grind
  | succ n ih =>
    have hp : (1 + r) ^ n ≠ 0 := Rat.ne_of_gt (Rat.pow_pos hr)
    have hr' : 1 + r ≠ 0 := Rat.ne_of_gt hr
    rw [Rat.pow_succ, ih, Rat.pow_succ, Rat.pow_succ]
    unfold fator
    grind

theorem gordon_vezes_complemento {cf g r : Rat} (h1 : -1 < g) (h2 : g < r) :
    gordon cf g r * (1 - fator g r) = cf * fator g r := by
  have hr : 1 + r ≠ 0 := by grind
  have hrg : r - g ≠ 0 := by grind
  unfold gordon fator
  grind

/-- Forma fechada: `S_n = TV · (1 − qⁿ)`. -/
theorem soma_parcial_fechada {cf g r : Rat} (h1 : -1 < g) (h2 : g < r) (n : Nat) :
    somaParcial cf g r n = gordon cf g r * (1 - fator g r ^ n) := by
  have hr : 0 < 1 + r := by grind
  have key := gordon_vezes_complemento (cf := cf) h1 h2
  induction n with
  | zero => simp [somaParcial, Rat.pow_zero]; grind
  | succ n ih =>
    have hq := potencia_fator g r hr (n + 1)
    have hdiv : cf * (1 + g) ^ (n + 1) / (1 + r) ^ (n + 1) = cf * fator g r ^ (n + 1) := by
      rw [hq]; grind
    simp only [somaParcial]
    rw [ih, hdiv, Rat.pow_succ]
    grind

/-- Cauda: o que falta somar após `n` períodos é `TV · qⁿ`. -/
theorem cauda {cf g r : Rat} (h1 : -1 < g) (h2 : g < r) (n : Nat) :
    gordon cf g r - somaParcial cf g r n = gordon cf g r * fator g r ^ n := by
  rw [soma_parcial_fechada h1 h2]; grind

/-- Desigualdade do tipo Bernoulli: `qⁿ · (1 + n(1−q)) ≤ 1` para `0 ≤ q ≤ 1`. -/
theorem potencia_limitada {q : Rat} (hq0 : 0 ≤ q) (n : Nat) :
    q ^ n * (1 + n * (1 - q)) ≤ 1 := by
  induction n with
  | zero => simp [Rat.pow_zero]; grind
  | succ n ih =>
    have hqn : 0 ≤ q ^ n := Rat.pow_nonneg hq0
    have hn : (0 : Rat) ≤ (n : Rat) + 1 := by
      have := Rat.natCast_nonneg (a := n); grind
    have hsq : 0 ≤ (1 - q) * (1 - q) := by
      by_cases h : 0 ≤ 1 - q
      · exact Rat.mul_nonneg h h
      · have h' : 0 ≤ q - 1 := by grind
        have := Rat.mul_nonneg h' h'; grind
    have hprod := Rat.mul_nonneg (Rat.mul_nonneg hqn hsq) hn
    rw [Rat.pow_succ, Rat.natCast_add, Rat.natCast_ofNat]
    grind

/-- Convergência: a soma parcial aproxima o valor de Gordon tanto quanto se queira. -/
theorem converge {cf g r : Rat} (h1 : -1 < g) (h2 : g < r) (hcf : 0 ≤ cf)
    (ε : Rat) (hε : 0 < ε) : ∃ n : Nat, gordon cf g r - somaParcial cf g r n < ε := by
  obtain ⟨hq0, hq1⟩ := fator_entre_zero_e_um h1 h2
  have hrg : 0 < r - g := by grind
  have htv : 0 ≤ gordon cf g r := by
    unfold gordon
    have : 0 ≤ cf * (1 + g) := Rat.mul_nonneg hcf (by grind)
    have hinv : 0 ≤ (r - g)⁻¹ := Rat.le_of_lt (Rat.inv_pos.mpr hrg)
    rw [Rat.div_def]; exact Rat.mul_nonneg this hinv
  have hd : 0 < ε * (1 - fator g r) := Rat.mul_pos hε (by grind)
  -- n ≥ TV / (ε (1 − q))
  let x := gordon cf g r / (ε * (1 - fator g r))
  refine ⟨x.ceil.toNat, ?_⟩
  have hx : x ≤ (x.ceil.toNat : Rat) := by
    have h1' : x ≤ (x.ceil : Rat) := Rat.le_ceil
    have h2' : x.ceil ≤ (x.ceil.toNat : Int) := Int.self_le_toNat _
    have h3' : (x.ceil : Rat) ≤ ((x.ceil.toNat : Int) : Rat) := Rat.intCast_le_intCast.mpr h2'
    rw [Rat.intCast_natCast] at h3'
    grind
  have hxd : gordon cf g r ≤ (x.ceil.toNat : Rat) * (ε * (1 - fator g r)) := by
    have := Rat.mul_le_mul_of_nonneg_right hx (Rat.le_of_lt hd)
    rwa [Rat.div_mul_cancel (Rat.ne_of_gt hd)] at this
  rw [cauda h1 h2]
  have hb := potencia_limitada (Rat.le_of_lt hq0) x.ceil.toNat
  have hb' := Rat.mul_le_mul_of_nonneg_left hb htv
  -- Se TV·qⁿ ≥ ε, então TV ≥ TV·qⁿ·(1+n(1−q)) ≥ ε(1+n(1−q)) > TV.
  apply Classical.byContradiction
  intro hneg
  have hge : ε ≤ gordon cf g r * fator g r ^ x.ceil.toNat := by grind
  have hpos : 0 ≤ 1 + (x.ceil.toNat : Rat) * (1 - fator g r) := by
    have := Rat.mul_nonneg (Rat.natCast_nonneg (a := x.ceil.toNat)) (by grind : (0 : Rat) ≤ 1 - fator g r)
    grind
  have := Rat.mul_le_mul_of_nonneg_right hge hpos
  grind

end Analise.Dcf
