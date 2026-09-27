# Konfrontacja Modelu Spin(10) z Danymi — Sektor Λ / Ciemnej Energii

**Moduł:** [`src/konfrontacja_kosmologiczna.py`](../src/konfrontacja_kosmologiczna.py) ·
**Runner:** [`scripts/konfrontuj_stala_kosmologiczna.py`](../scripts/konfrontuj_stala_kosmologiczna.py) ·
**Kontrakty:** [`tests/test_konfrontacja_kosmologiczna.py`](../tests/test_konfrontacja_kosmologiczna.py) ·
**Artefakty:** [`results/konfrontacja_stala_kosmologiczna.json`](../results/konfrontacja_stala_kosmologiczna.json),
[`results/konfrontacja_silnik_exp.json`](../results/konfrontacja_silnik_exp.json),
`results/stala_kosmologiczna/konfrontacja.png`

Data konfrontacji: 27 września 2026.

---

## 1. Konfrontacja globalna silnika (stan istniejący, odświeżona)

Istniejący runner [`run_experimental_confrontation.py`](../scripts/run_experimental_confrontation.py)
zestawia rzeczywiste wyjście silnika v9 (N=200, 400 kroków MC + solwery
Mukhanov–Sasaki/RGE/MCMC) z 18 wierszami zamrożonych danych:

| Oś | Wynik |
|---|---|
| DATA | **AGREE=12, EXCLUDED=1, NO-DATA=5** |
| DERIVATION | computed=9, hard-coded=5, measured input=1, tuned-to-data=3 |
| χ²/dof (wiersze mierzone) | 5.03/7 = 0.72 |
| Jedynie wykluczony | **ρ_Λ (silnik: 5.1×10¹¹⁴ J/m³ vs zmierzone 5.3×10⁻¹⁰ J/m³)** |

Sektor inflacyjno-cząsteczkowy (n_s, A_s, r, f_NL, axion-CDM, proton,
RGE-unifikacja) przechodzi — z zastrzeżeniami osi DERIVATION (η_B, Ω_a h²,
m_gluino są dopasowane do danych). **Jedynym odporowo wykluczonym obserwablem
pozostaje gęstość energii próżniowej** — co motywuje dedykowaną konfrontację
sektora Λ poniżej.

## 2. Zamrożone dane sektora Λ / ciemnej energii

| Wielkość | Wartość | Źródło |
|---|---|---|
| Λ/M_Pl² | 2.8485×10⁻¹²² | Planck 2018 VI ([arXiv:1807.06209](https://arxiv.org/abs/1807.06209)) |
| ρ_Λ/M_Pl⁴ | 1.135×10⁻¹²³ | Planck 2018 VI |
| Ω_Λ | 0.6847 ± 0.0073 | Planck 2018 VI |
| Ω_m | 0.295 ± 0.015 (BAO) · 0.307 ± 0.005 (+CMB) | DESI 2024 VI DR1 ([arXiv:2404.03002](https://arxiv.org/abs/2404.03002)) |
| H₀ | 67.36 ± 0.54 · 67.97 ± 0.38 | Planck18 · DESI+CMB |
| w (stałe) | −0.99 ⁺⁰·¹⁵₋₀.₁₃ | DESI DR1 BAO |
| w₀wₐ hint | w₀>−1, wₐ<0; 3.1σ (DESI+CMB), do 4.2σ (z SNe) | DESI DR2 ([arXiv:2503.14738](https://arxiv.org/abs/2503.14738)) |
| ρ_stiff/ρ_rad (BBN) | < 0.068 | ΔN_eff ≤ 0.3 (Planck+BBN) |
| t₀ | 13.797 ± 0.023 Gyr | Planck 2018 VI |

## 3. Wyniki: scenariusz × dane

Zmierzone w silniku (poprzedni audyt): q = 0.835, A = 0.170 (skan β, N=120,
3 ziarna). Pozostałe liczby z [`src/stala_kosmologiczna.py`](../src/stala_kosmologiczna.py).

| Scenariusz | Λ(t₀) vs Λ_obs | w₀ vs DESI −0.99⁺⁰·¹⁵₋₀.₁₃ | ρ_stiff/ρ_rad & BBN | Werdykt |
|---|---|---|---|---|
| **S1** goły model | 10⁺¹²⁰ EXCLUDED | −1 (0.08σ) AGREE | ×4.6×10⁸⁸ EXCLUDED | **EXCLUDED** |
| **S2** po kanałach (×0.10) | 10⁺¹¹⁹ EXCLUDED | −1 (0.08σ) AGREE | ×4.7×10⁸⁷ EXCLUDED | **EXCLUDED** |
| **S3** termiczna (q=0.84, mierzone) | 10⁺⁹³ EXCLUDED | −0.72 (1.8σ) AGREE | ×4.2×10⁶⁹ EXCLUDED | **EXCLUDED** |
| **S4** tracker t⁻² (C=C_req) | zgodna (z definicji) | 0 → **6.6σ EXCLUDED** | ×6.2×10³ EXCLUDED | **EXCLUDED** |
| **S4b** tracker t⁻² (C=1) | 10⁻⁰·⁹ (−0.89 dex) | 0 → **6.6σ EXCLUDED** | ×8.0×10² EXCLUDED | **EXCLUDED** |
| **S5** podłoga x_f=x_req przed BBN | zgodna (z definicji) | −1 (0.08σ) AGREE | ×3.3×10⁻³² AGREE | **AGREE*** |

\* **S5 jest dopasowany do danych z konstrukcji** (oś DERIVATION = tuned-to-data) —
jego zgodność NIE jest predykcją modelu.

Wiersze kontekstowe:

| Wiersz | Model | Dane | Werdykt |
|---|---|---|---|
| w₀wₐ (DESI DR2) | (w₀, wₐ) = (−1, 0) — każdy stały Λ (wspólne z ΛCDM) | w₀>−1, wₐ<0 na 2.5–4.2σ | TENSION-CONTEXT |
| α_eff podłogi | 0.0227 (z e^(−2π/α)=x_req) | α_GUT = 0.04 (2-pętlowy RGE silnika) | TENSION, stosunek 1.76 (pending) |

## 4. Wnioski

1. **Amplituda Λ**: żaden scenariusz nie-dopasowany nie trafia w zgodność —
   najbliżej jest tracker C=1 (10⁻⁰·⁹, czyli czynnik ~8 za mało dziś), ale
   zabija go skład (równanie stanu), nie amplituda.
2. **Równanie stanu**: wszystkie wersje „relaksującej" próżni (t⁻²) mają w
   erze materii w = 0 (pył), co jest **6.6σ od pomiaru DESI** — równanie stanu
   jest śmiertelnym ograniczeniem dla trackera, silniejszym niż amplituda.
3. **Trasa termiczna** ma intrygująco właściwy *znak* odchylenia w (w₀ = −0.72,
   1.8σ od DESI constant-w, blisko DESI-preferred thawing-quadrant), ale jej
   amplituda przekracza dane o ~93 rzędy, a historia narusza BBN katastrofalnie
   — nie jest wykładalna jako mechanizm.
4. **BBN** jest najboleśniejszą, niezależną śmiercią dla każdego „wolnego"
   scenariusza: ρ~t⁻² w próżni oznacza dominację próżni w epoce nukleosyntezy.
5. **DESI DR2 w₀wₐ hint**: punkt (−1, 0) dowolnej stałej Λ leży 2.5–4.2σ od
   preferowanego rejonu. To napięcie **wspólne z samym ΛCDM** — raportowane
   jako TENSION-CONTEXT, nie jako falsyfikacja modelu. Daje jednak konkretny
   cel: mechanizm generujący podłogę *z niedawnym przejściem* w kierunku
   w₀>−1, wₐ<0 byłby naturalnie sekwencyjnie testowalny.
6. **Warunek krzyżowy α_eff = 0.0227** (podłoga nieperturbacyjna) vs α_GUT = 0.04
   silnika — otwarty; następny krok to ewaluacja sprzężenia na skali ~M_Pl w
   [`src/numerical_rge_solver.py`](../src/numerical_rge_solver.py).

## 5. Reprodukcja

```bash
PYTHONPATH=src python3 scripts/run_experimental_confrontation.py --json results/konfrontacja_silnik_exp.json
PYTHONPATH=src python3 scripts/konfrontuj_stala_kosmologiczna.py            # konfrontacja sektora Λ
PYTHONPATH=src python3 -m unittest tests.test_konfrontacja_kosmologiczna    # 25 kontraktów
```
