# Przebudowa Sektora Inflacji i Danych — Raport (wrzesień 2026)

**Moduły:** [`src/inflacja_alpha_attractor.py`](../src/inflacja_alpha_attractor.py),
[`src/konfrontacja_inflacja.py`](../src/konfrontacja_inflacja.py) ·
**Runner:** [`scripts/konfrontuj_inflacje.py`](../scripts/konfrontuj_inflacje.py) ·
**Kontrakty (32):** [`tests/test_inflacja_konfrontacja.py`](../tests/test_inflacja_konfrontacja.py) ·
**Ledger:** [`docs/LEDGER_INFLACJA.json`](LEDGER_INFLACJA.json) ·
**Artefakty:** [`results/konfrontacja_inflacja.json`](../results/konfrontacja_inflacja.json),
`results/inflacja/konfrontacja_inflacja.png`

---

## 1. Co było nie tak w starym sektorze

1. **Arbitralne N = 60** — silnik zakładał sztywno 60 e-folds; fizycznie N_⋆
   ustala zgodność podhoryzontalnej ewolucji z termodynamiką podgrzewania.
2. **Wzory pierwszego rzędu** n_s = 1−2/N, r = 12α/N² — pomijają poprawki
   O(ln N/N) w konwencji ε_H(N), które przy obecnej precyzji danych
   (σ(n_s) = 0.0034) są istotne.
3. **Tabela danych sprzed 2021** — aktualne okno to ACT DR6 (2025), DESI DR2,
   SH0ES/Pantheon+, KiDS/DES-Y3 joint.
4. **Brak równań α_s, β_s** i napięć późnego Wszechświata (H₀, S₈).

## 2. Co zrobiła przebudowa

### 2.1 Dokładne tło (moduł `inflacja_alpha_attractor`)

E-model α-attractor V = V₀(1−e^{−λφ})², λ = √(2/(3α)), α = 3.75:

- Pełne równania Friedmanna–Klein–Gordona całkowane w czasie e-foldowym
  (φ′=u, u′=−(3−u²/2)(u+V′/V)) do ε_H=1 — walidacja: dN/dφ=V/V′ dokładnie
  (kontrakt testowy), ε₁(end)=1, atraktor u=−V′/V z dokładnością 2%.
- Parametry przepływu Hubble'a ε₁, ε₂, ε₃ z tła; obserwable drugiego rzędu
  (Lidsey i in. 1997): n_s, r, oraz α_s, β_s różniczką po tle.
- Wynik dla N=60: **n_s = 0.96844, r = 0.00967, α_s = −5.1×10⁻⁴,
  β_s = +1.7×10⁻⁵** (wzory LO dają 0.9667, 0.0125 — spread metody 0.005
  ujęty w ledgerze IN‑U001; silnikowy MS‑solver: 0.96353).

### 2.2 Podgrzewanie (fizyczne N_⋆)

Standardowy łańcuch entropowy (Liddle–Leach): ρ_end = (3/2)V_end (ε_H=1),
skalowanie ρ ∝ a^{−3(1+w)}, ρ_rh = (π²/30)g*T⁴, a_rh z zachowania entropii.
Dla w_rh=0:

| T_rh [GeV] | N_⋆ | n_s | r |
|---|---|---|---|
| 1 | 43.9 | 0.9572 | 0.0170 |
| 1e7 | 49.6 | 0.9620 | 0.0137 |
| 1e15 | 55.3 | 0.9658 | 0.0112 |
| instant (~1e16) | ~56.5 | ~0.9656 | ~0.0111 |

**Sztywne N=60 jest fizycznie niedostępne** (wymagałoby T_rh > ρ_end^{1/4})
— wpis IN‑F001 w ledgerze. Maksymalne vanilla n_s = **0.9658**.

### 2.3 Aktualna tabela danych

| Obserwabla | Wartość | Kombinacja | Źródło |
|---|---|---|---|
| n_s | 0.9649 ± 0.0042 | Planck 2018 | [1807.06209](https://arxiv.org/abs/1807.06209) |
| n_s | 0.9709 ± 0.0038 | P‑ACT (DR6) | ACT Collab 2025 |
| n_s | 0.9743 ± 0.0034 | P‑ACT‑LB (+DESI) | ACT Collab 2025 |
| r (0.05) | < 0.036 (95%) | BK18 | [2110.00483](https://arxiv.org/abs/2110.00483) |
| r combo | < 0.038 (95%) | P‑ACT‑LB‑BK18 | po 2606.24131 |
| α_s (ext.) | +0.0119 ± 0.0063 | ACT+P z β_s | [2511.01612](https://arxiv.org/abs/2511.01612) |
| H₀ | 67.36±0.54 / 73.04±1.04 | Planck / SH0ES | [2112.04510](https://arxiv.org/abs/2112.04510) |
| S₈ | 0.832±0.013 / 0.790±0.016 | Planck / KiDS+DES-Y3 | joint 2024 |

## 3. Werdykty konfrontacji

| Wiersz | Pull | Werdykt |
|---|---|---|
| n_s vanilla LO (N=60) vs Planck 2018 | +0.42σ | AGREE |
| n_s vanilla LO vs P‑ACT | −1.11σ | AGREE |
| n_s vanilla LO vs **P‑ACT‑LB** | **−2.25σ** | **TENSION** |
| n_s vanilla NLO (N=60) vs P‑ACT‑LB | −1.72σ | AGREE |
| n_s podgrzewanie (najlepsze T_rh) vs P‑ACT‑LB | **−2.49σ** | **TENSION** |
| n_s podgrzewanie (typowe log T_rh) vs P‑ACT‑LB | **−3.77σ** | **EXCLUDED** |
| r (wszystkie warianty) vs BK18/combo | margines ×2.1–3.9 | AGREE |
| α_s(N=60 NLO) vs Planck18 | +0.54σ | AGREE |
| α_s vs ACT+P (fit z β_s; wskazanie α_s>0) | −1.97σ | AGREE (kierunek odwrotny — obserwować) |
| A_s | = wejście | *measured input* (V₀ liniowo) |
| H₀ (model ← ΛCDM 67.36 vs SH0ES) | 4.85σ | TENSION-CONTEXT |
| S₈ (brak sektora LSS) | 2.04σ | NO-DATA |

**Werdykt sektora: VANILLA_IN_TENSION_WITH_ACT_DR6_PLB** — zgodność z Planck
2018 i P‑ACT, napięcie 2.3–2.6σ z najmocniejszą kombinacją P‑ACT‑LB dla
*każdego* fizycznie obranialnego punktu vanilla α-attractor (α=3.75).

## 4. Co to znaczy dla modelu Spin(10)

1. **Falsyfikowalny rozwidlenik**: jeśli P‑ACT‑LB się utrzyma (Euclid, CMB‑S4
   w 2027+), model musi (a) zdeformować potencjał (w literaturze δ ≈ 0.017
   rozwiązuje problem bez naruszania r — warunek IN‑R001), lub (b)
   porzucić wiązanie α = dim/12, co zmienia też podejście w ledgerze Λ
   (warunek krzyżowy α_eff).
2. **Krzyżówka z sektorem Λ**: problem podlogi próżni z poprzedniego audytu
   (α_eff ≈ 0.0227) jest niezależny, ale oba wymagają *tej samej* ewaluacji
   sprzężenia na skali GUT–Planck w module RGE — naturalny następny krok.
3. **Obserwować α_s**: atraktor przewiduje α_s ≈ −5×10⁻⁴ (<0), napiwne ACT
   wskazuje >0 na ~2σ (fit rozszerzony) — jeśli się umocni, vanilla α-attractor
   padnie też tą osią.

## 5. Reprodukcja

```bash
PYTHONPATH=src python3 scripts/konfrontuj_inflacje.py
PYTHONPATH=src python3 -m unittest tests.test_inflacja_konfrontacja     # 32 kontrakty
```
