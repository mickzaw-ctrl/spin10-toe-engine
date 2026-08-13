# Necessary conditions for a Theory of Everything

**Status of this programme:** conditions **not** satisfied.  
**`is_toe`:** false.  
**Validated observational predictions:** 0.

A Theory of Everything is not “many modules in one repository.”
It is a single dynamical framework that contains gravity and the
Standard Model, is quantum-mechanically defined, recovers the known
limits, and survives a preregistered confrontation with official data.

Implementation: [`src/toe_conditions.py`](../src/toe_conditions.py).

---

## The rule

A TOE claim is allowed only if **T1–T12 are all MET**.  
Partial credit is not a TOE.  
The α-attractor contract NS-AT-INSTANT-01 is phenomenology, not a TOE.

---

## Necessary conditions

| ID | Condition | Now |
|---|---|---|
| **T1** | Internal consistency: classified axioms, named inputs and units, rejected shortcuts stay rejected. | **PARTIAL** |
| **T2** | One action / measure for gravity + SM gauge + matter. Imported LQC / α-attractor / RGE stacks do not count. Gate 4 writes the classical EYM candidate; T2 stays unmet while those modules still drive predictions. | **UNMET** |
| **T3** | Quantum definition: Hilbert space or Euclidean measure, gauge fixing, continuum / refinement limit. | **UNMET** |
| **T4** | Gravity limit: Einstein (or a specified alternative) with controlled extras. \(G_{\rm eff}=G_0/P\) is not the field equation unless \(\nabla P=0\). | **UNMET** |
| **T5** | SM content derived, including three generations. \(N_{\rm gen}=3\) as an input (A2) blocks a TOE claim. | **UNMET** |
| **T6** | No hidden calibration (A4). PDG knobs and entropy-matched Immirzi are not derivations. | **UNMET** |
| **T7** | Input-independent \(M_{\rm GUT}\), \(\Lambda\), \(\alpha_{\rm em}\), Yukawas \(m_D,M_R\). | **UNMET** |
| **T8** | ≥1 prediction from the *TOE dynamics* with independent derivation, inputs excluding the target, official likelihood, preregistered no-go. | **UNMET** |
| **T9** | No necessary consequence excluded by a frozen published limit under the theory’s own inputs. | **UNMET** (C3, \(\alpha_H=0.015\)) |
| **T10** | Official data products (Plik/CamSpec, Super-K/Hyper-K, MEG-II), not marketing proxies. | **UNMET** |
| **T11** | Independent gates bind. A NO-GO cannot be undone by putting the target back into the action. | **PARTIAL** |
| **T12** | Counters stay honest: no TOE flag and no increment of the validated count unless T1–T11 are MET. | **MET** (discipline only) |

T12 being MET only means the software refuses to lie.

---

## What is *not* sufficient

- Spin(10) contains the SM gauge algebra (A1). That is group theory.
- \(n_s=1-2/N\) with \(N\) from reheating (C1). That is an α-attractor hypothesis with a chosen \(\alpha\).
- A legacy table whose numbers sit near PDG values.
- Internal specification closure (v16.1).
- Gate 3 writing \(\int P R\) without deriving \(P(N,T)\).

---

## What is still missing in this repository (blocking T2–T10)

1. A microscopic derivation of \(P(N,T)\) or another gravity completion.
2. Three generations that are not an input.
3. \(\alpha_{\rm em}\) and \(\Lambda\) without calibration or illegal dimensions.
4. Yukawas that fix \(m_D\) and \(M_R\).
5. A causal GFT with a bulk–boundary map and a continuum limit.
6. Official Planck / MEG-II / Hyper-K likelihoods on a Spin(10)-derived signal.
7. A proton-lifetime estimate that is either derived and above Super-K, or the theory is excluded.

Until those are closed under T1–T12, the only honest statement is:

> This is not a Theory of Everything.

```bash
PYTHONPATH=src python -c "from toe_conditions import evaluate_toe_conditions; \
r=evaluate_toe_conditions(); print(r['is_toe'], r['n_met'], r['n_unmet'])"
```
