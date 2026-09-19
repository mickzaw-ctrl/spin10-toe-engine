# A Definition of a Theory of Everything — RC-ToE (Reflective Closure)

**Companion to** [`docs/DEFINICJA-TEORII-WSZYSTKIEGO.md`](DEFINICJA-TEORII-WSZYSTKIEGO.md)
(the full Polish version). This mirror is condensed but complete on definitions,
theorems and numbers.
**Status:** `DEFINITION_AND_DECISION_PROCEDURE` — a definition plus an executable audit,
**not** a physical theory. No constant of Nature is derived here.
**Kernel:** [`src/toe_closure_kernel.py`](../src/toe_closure_kernel.py),
[`src/toe_reflective_closure.py`](../src/toe_reflective_closure.py) (standard library
only, exact arithmetic, fail-closed).
**Audit:** `PYTHONPATH=src python scripts/run_rc_toe_audit.py` →
[`results/rc_toe_audit.json`](../results/rc_toe_audit.json)

> **One-sentence result.** A Theory of Everything is not a Lagrangian and not a list of
> laws: it is a **closure structure `(E, cl, σ, Ω)` that is closed substantively,
> dynamically, logically, observationally and decisionally — and that knows its own
> residual exactly.** Applied to itself, the definition **refuses to certify itself** (§6).

---

## §1. Method: four inference rules

| # | Rule | Operational content |
|---|---|---|
| **R1** | **Define by disqualification** | A definitional clause that rejects nothing is decoration. §2 lists five anti-definitions; §3 rejects most computable substrates. |
| **R2** | **Force executability** | Every clause must have a runnable test that can return `FAIL`. |
| **R3** | **Self-application** | The definition is audited by its own audit. Self-certification is treated as a program error (exit code 1). |
| **R4** | **Disclose the residual** | Every claim ships with what was rejected, what was not computed, and how many trials preceded a coincidence. |

R1 and R4 have a concrete scar in the code: the first measure of "quantumness" I proposed
(density of dependent triples `δ₃`) was **refuted by my own computation**. `U_{3,4}` has
`δ₃ = 0` and is still non-distributive, because its single circuit has four elements. The
correct invariant is the **lowest constraint order**, not a density.

---

## §2. Why the usual definitions of a ToE are trivial

| Anti-definition | Formal failure mode |
|---|---|
| "a ToE unifies all interactions" | a criterion of *scope*, not of content; every GUT partly satisfies it |
| "a ToE is a Lagrangian `M` from which everything follows" | regress: why `M`? its parameters stay unexplained |
| "a ToE has no free parameters" | vacuous: `1 = 1` has none; no account of where numbers come from |
| "a ToE explains everything measurable" | excludes the observer, hence excludes its own discovery |
| "a ToE is the final theory" | sociological and unfalsifiable |

---

## §3. Substrate: closure instead of metric

`E` = finite set of **facts**; the only primitive is a closure operator `cl` (extensive,
monotone, idempotent) with the exchange axiom, i.e. a **matroid** `M`.

| Object | Definition | RC-ToE reading |
|---|---|---|
| `r(A)` | rank | number of *independent* facts = effective configuration dimension |
| `C(A) = \|A\| − r(A)` | constraint charge | **interaction**: how many facts are bound |
| `L(M)` | lattice of flats | pre-geometric "space": an order with no metric |
| `χ_M(q)`, `T_M(x,y)`, `μ` | characteristic/Tutte polynomial, Möbius function | **constants**: candidates for the invariants that must yield the numbers of Nature |
| `Aut(M)` | closure-preserving permutations | **gauge symmetry**, computed rather than postulated |
| `fr(A) = {e : e ∉ cl(A)}` | frontier | the only place dynamics can branch |
| `A_{t+1} = cl(A_t ⊔ {x_t})`, `x_t ∈ fr(A_t)` | **rank flow** | the single law: no action, no metric, no couplings |

Time is the accessibility order of the resulting antimatroid, so the arrow of time is
built in rather than thermodynamically emergent; gravity is the entropic response `ΔC` to
inserting a fact (Jacobson's programme, combinatorial — `project_hypothesis`).

---

## §4. Definition (RC-ToE)

`𝒯 = (E, cl, σ, Ω)` — facts, closure operator, a normalised valuation (generalised
probability) on `L(cl)`, and an observer substructure with its inference operator — is a
**Reflective Closure Theory of Everything** iff:

* **(S) substance closure** — zero fitted parameters; every dimensionless observable is a
  combinatorial invariant of `(E, cl)`; every constant↔invariant assignment must survive
  the coincidence budget *and* name a mechanism.
* **(L) law closure** — every interaction is a channel of the single rank flow. A channel
  that has to be added as a separate term turns the gate to `FAIL`. Allowed statuses:
  `derived`, `implemented`, `hypothesis`, `open_task`, `postulated`, `rejected`.
* **(Q) logic closure** — the substrate's rung on the admissibility ladder must be
  *computed* and must equal the declared rung; a quantum theory needs rung 3 with `r ≥ 3`
  ("Born-ready"). Every finite substrate we can enumerate is refused (T4).
* **(O) observer closure** — `𝒯` is an attractive fixed point of
  `Φ(p) = normalize((1−ε)·p·L·(Mᵀp) + ε·u)`: it must predict the process by which it is
  inferred.
* **(D) decision closure** — pre-registered falsifiers `(observable, prediction,
  tolerance, experiment, horizon, kill semantics)`, at least one **external**, plus the MDL
  inequality `|axioms| < |data explained|`.
* **(R) residual** — `𝒯` publishes `ρ* = residual(N, B)`: a certified lower bound on the
  mass of facts that axioms of `≤ N` bits and proofs of `≤ B` steps cannot decide.

> **A Theory of Everything closes everything except a residual it can compute exactly.**

---

## §5. Theorems and computed results

All numbers are produced by the audit script and frozen in 54 contract tests.

**T1 (classicality = absence of constraints of order ≥ 3)** — `theorem`.
`L(M)` is distributive iff every circuit has `≤ 2` elements. Verified exhaustively on
**89 substrates** (all matroids on `≤ 4` labelled facts), **0 violations**. Enumeration
counts, cross-checked by hand: `n=1: 2`, `n=2: 5`, `n=3: 16`, `n=4: 68`.
Consequence: quantum logic is a theorem about constraint density, and a substrate with no
constraint of order ≥ 3 is *lawless* (`cl = id`). **There is no law without non-classical
logic.**

**T2 (the classical limit is canonical)** — `theorem`. The classical limit is the
distributive reflector `L/θ_D`, not an `ħ → 0` extrapolation. Computed: `M3 → 2 blocks`
(one classical bit), `U_{2,4} → 2`, `Fano → 2`, `B_n → 2^n` (`κ = 1`, nothing to
classicalise).

**T3 (probability is not automatic)** — `theorem`. The valuation system can be
inconsistent, in which case the substrate is excluded without any experiment:

| substrate | `|L|` | distributive | modular | valuation | #states | orthocomplementation | rung |
|---|---|---|---|---|---|---|---|
| `F₄` (Boolean) | 16 | yes | yes | yes | 4 (dim 3) | yes | 0 classical/lawless |
| `U_{2,3}` = `M3` = PG(1,2) | 5 | no | yes | yes | **1**: `(½,½,½)` | no | 2 |
| `U_{2,4}` = `M4` = PG(1,3) | 6 | no | yes | yes | **1**: `(½,½,½,½)` | **yes** | 3 |
| `U_{3,4}` | 12 | no | **no** | **none** | 0 | no | 1 inadmissible |
| `U_{4,5}` = Spin(10) code | 27 | no | **no** | **none** | 0 | no | 1 inadmissible |
| `Fano` = PG(2,2) | 16 | no | yes | yes | **1**: points `⅓`, lines `⅔` | no | 2 |

Census of the 68 substrates on four facts: rung 0 — 52, rung 1 — 1, rung 2 — 14,
rung 3 — 1, **Born-ready — 0**.

**T4 (the Born rule needs an infinite substrate)** — `theorem` + `open_task`.
No substrate on `≤ 4` facts is Born-ready; the only orthocomplemented non-classical one is
`U_{2,4} = PG(1,3)`, i.e. precisely dimension 2, where Gleason-type theorems fail.
Classically, every polarity of a finite projective plane has absolute points, so no finite
projective plane is orthocomplementable (the kernel confirms this by exhaustive
backtracking for PG(2,2)). Hence a quantum ToE needs an infinite substrate, and then
Solèr's theorem makes the division ring `ℝ/ℂ/ℍ` **derived rather than chosen** (which of
the three remains open).

**T5 (the smallest admissible non-classical substrate is the Fano plane)** — `theorem`.
7 facts, rank 3, **14 circuits** (7 lines of 3 points + 7 affine planes of 4), 16 flats,
`χ(q) = q³ − 7q² + 14q − 8`, `β = 3`, 28 bases, `δ₃ = 1/5`, `Aut = 168 = GL(3,2) =
PSL(2,7)`, modular, non-distributive, **exactly one state** (`σ(point) = 1/3`,
`σ(line) = 2/3`), **no orthocomplementation**, classical shadow = 1 bit. Rigidity of the
state space is a resource: it is the candidate source of constants, not "tuning".

**T6 (reflective stability overrides likelihood)** — `theorem` for the published kernel.
With `M = [[.10,.80,.10],[.05,.90,.05],[.20,.50,.30]]`, `L = (.70,.20,.10)`, `ε = 0.02`:
fixed point `(0.008328, 0.984807, 0.006865)`, ML choice `A`, reflective choice `B`,
total-variation override `0.785`, 13 iterations, `KL = 2.4e-14`, contraction `0.041`.
For an identity kernel the fixed point returns to the ML choice (non-vacuity check).

**T7 (no-go: complete closure is impossible)** — `theorem` (conditional). If `𝒯` is
finitely axiomatisable, consistent and contains arithmetic, then (O) with zero residual
would make `𝒯` prove its own consistency, contradicting Gödel II. Therefore RC-ToE does
not demand completeness; it demands **exact knowledge of the residual**.

---

## §6. Spin(10) as a closure structure, and two audits

**Exact identities (all computed).** The 16 weights of the chiral spinor of `Spin(10)` are
the even-parity half of the 5-cube; `W(D₅)` is the group of parity-preserving signed
permutations of the five slots, `|W(D₅)| = 1920 = 2⁴·5!` (full hyperoctahedral: 3840), and
it acts transitively on the 16 weights. The constraint structure of the spinor is the
binary `[5,4]` even-parity code, whose matroid is `U_{4,5}` with a **single global
circuit** (the whole five-element set) — a rank-one dual, i.e. one `ℤ₂` charge shared by
all slots: fermion parity.

**Negative result.** `U_{4,5}` is rung 1: its flat lattice admits **no valuation at all**.
Read as a closure structure, the 16-spinor weight system cannot carry probability.
`Spin(10)` is therefore a *labelling* of facts, not yet a substrate: by T4 it must be
embedded in an infinite orthocomplementable structure. The octonionic/exceptional direction
(Fano → `h₃(𝕆)` → `E₆/E₈`) is flagged `speculative` and is **not** derived here.

**Audit of GUH-S10 (this repository's Spin(10)-ToE, v14.5) → `REFUSED_MISSING_COMPUTATION`.**

| Gate | Verdict | Evidence |
|---|---|---|
| S | **FAIL** | six fitted parameters; sharpest: `alpha_em_0_inv_corrected = alpha_em_0_inv - 6.5504` with the comment "exact calibration to 1/137.036" (`src/physics_apex_v13_core.py:145`, also `src/grand_unified_toe_core.py:551`), contradicting the README claim of "zero experimental input"; also `c_H = 0.33` (`src/spin10_engine.py:703`), the scale `150` in `d_S` (`:390`), `Var(k) → 32.67`, `g* = 0.83`, `N_hidden = 125` |
| L | **FAIL** | gauge `postulated`, gravity `hypothesis`, generations `hypothesis`, `Λ` `rejected` |
| Q | **REFUSED** | the repository implements a relational graph with Metropolis–Hastings sampling, **not a closure operator**; the gate refuses instead of guessing |
| O | **FAIL** | no observer model, no inference operator |
| D | **FAIL** | external falsifiers exist but are not pre-registered: `m_gluino` has two frozen values (`10.6 TeV` vs `12.39 TeV`), `η_B` two (`6.2e-10` vs `6.11e-10`), tolerances and kill semantics are absent; MDL is violated (`5376 > 4768` bits, zlib proxy) |

**Audit of RC-ToE (this definition) → `FRAMEWORK_NOT_TOE`, `certified = false`.**
S `FAIL` (zero fitted parameters, but also zero constant↔invariant assignments),
L `CONDITIONAL` (all four channels `open_task`), Q `CONDITIONAL` (Fano is rung 2, not
Born-ready), O `PASS`, D `CONDITIONAL` (5 complete falsifiers, **0 external**; MDL
satisfied with a 1.1% margin). **The definition refuses to certify itself.**

**Coincidence budget.** `β(Fano) = 3` and the repository needs `N_gen = 3`. With `K = 20`
invariants over `N = 89` substrates and `τ = 0.05`: `p_chance = 1 − 0.9^1780 > 0.99` ⇒
`rejected_numerology`; without a mechanism ⇒ `rejected_no_mechanism`. The coincidence is
rejected by its author in the same section in which it is noticed.

---

## §7. What this definition does **not** claim

It derives no constant of Nature; it does not assert that the Universe *is* a matroid; it
does not unify interactions; it does not replace Spin(10), LQG, asymptotic safety or
IFT-EGR. It defines what would have to be true for any of them to be closed — and it
publishes the executable refusal for the candidates we can compute, including its own.

**Run it:**

```bash
PYTHONPATH=src python -m unittest -v tests.test_toe_closure_kernel      # 30 contracts
PYTHONPATH=src python -m unittest -v tests.test_toe_reflective_closure  # 24 contracts
PYTHONPATH=src python scripts/run_rc_toe_audit.py --output results/rc_toe_audit.json
```

The script exits `1` if T1 has a counterexample, if the census finds a Born-ready finite
substrate, if `|W(D₅)| ≠ 1920`, if the weight count is not 16, **or if RC-ToE ever
certifies itself**.
