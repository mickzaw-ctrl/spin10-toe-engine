# Problem Stałej Kosmologicznej — Pełny Audyt Modelu Spin(10)

**Moduł:** [`src/stala_kosmologiczna.py`](../src/stala_kosmologiczna.py) ·
**Pipeline:** [`scripts/rozwiaz_stala_kosmologiczna.py`](../scripts/rozwiaz_stala_kosmologiczna.py) ·
**Kontrakty:** [`tests/test_stala_kosmologiczna.py`](../tests/test_stala_kosmologiczna.py) ·
**Rejestr założeń:** [`docs/LEDGER_STALA_KOSMOLOGICZNA.json`](LEDGER_STALA_KOSMOLOGICZNA.json) ·
**Artefakty:** [`results/stala_kosmologiczna_raport.json`](../results/stala_kosmologiczna_raport.json)

**Status: PROTOTYP BADAWCZY OTWARTY — werdykt `LOCALIZED_OPEN`.**
Problem stałej kosmologicznej **nie jest rozwiązany**. Niniejszy raport pokazuje,
co model Spin(10) już rozstrzyga, co obala (w tym cztery naturalne trasy
rozwiązania — używając własnej dynamiki silnika) oraz jaki pozostaje precyzyjny,
mierzalny cel dla przyszłych mechanizmów.

---

## 1. Problem w standardowej fizyce — odtworzenie

Suma energii punktu zerowego z fizycznym odcięciem κ daje na jeden bozonowy
stopień swobody

$$\rho_{\rm vac} \;=\; \pm\,\frac{\kappa^{4}}{16\pi^{2}} \qquad (\text{bozony }+\text{, fermiony }-)$$

Dane obserwacyjne (Planck 2018, H₀ = 67.4, Ω_Λ = 0.6847):

$$\rho_\Lambda = (2.24\ {\rm meV})^{4} = 2.52\times10^{-47}\ {\rm GeV}^{4},
\qquad \Lambda = 1.09\times10^{-52}\ {\rm m}^{-2} = 2.85\times10^{-122}\ M_{\rm Pl}^{2}$$

| Odcięcie κ | ρ_vac/ρ_obs |
|---|---|
| Λ_QCD = 0.2 GeV | 10^41.6 |
| m_H = 125 GeV | 10^52.8 |
| v_EW = 246 GeV | 10^54.0 |
| M_SUSY = 1 TeV | 10^56.4 |
| M_GUT = 2×10¹⁶ GeV | 10^109.6 |
| M_Pl | **10^120.7** |

Dokładna SUSY znosi sumę; po złamaniu w skali 1 TeV zostaje **10^56.4** —
supersymetria też nie rozwiązuje problemu.

## 2. Formuła grafowa — i jej uczciwy bilans

Model Spin(10) ([dokument](../cosmological-constant.md)) daje emergentną Λ:

$$\Lambda = \frac{8\pi G_{N}}{a^{4}}\Big[\tfrac{3}{4g^{2}}\big(1-\langle\cos\Phi_{\triangle}\rangle\big) + \alpha\,\langle{\rm Var}(k)\rangle\Big], \qquad G_{N}=\frac{3}{2\pi N a^{2}}$$

(korekta wymiarowa: Λ = 8πG_Nρ_vac ma wymiar L⁻² = ℓ_Pl⁻², patrz wpis CC‑U002
w rejestrze — dokument wyjściowy pisał Λ ∼ ℓ_P⁻⁴, co jest wymiarem ρ_vac).

Dla równowagi raportu (⟨cosΦ⟩ = 0.688, Var(k) = 0.262, N = 150, g² = α = 1):

$$\Lambda = 0.0397\ \ell_{\rm Pl}^{-2} \quad\Longrightarrow\quad
\log_{10}\frac{\Lambda_{\rm model}}{\Lambda_{\rm obs}} = 120.1$$

**Grafowa Λ odziedziczyła pełny problem ~10¹²⁰.** Model nie redukuje jej
rzędu wielkości; za to *mechanizmem* Λ czyni dwie mierzalne liczby:
frakcję dekondensacji x = 1−⟨cosΦ⟩ i wariancję stopni Var(k).

## 3. Audyt kanałów tłumienia zgłoszonych w projekcie

| Kanał | Czynnik | Źródło |
|---|---|---|
| 1/rank Spin(10) = 1/5 (wariant 1/45) | 0.200 (0.0222) | pkt 6.2 dokumentu |
| Renormalizacja 1‑pętlowa Wilsona | 0.9916 | pkt 6.2(3) |
| Redukcja lorentzowska 2(1−CF), CF=0.738 | 0.5240 | Publ. I |
| Korekta α‑attractor, α=45/12 | 0.9929 | Publ. III |
| **łącznie** | **0.103 (0.0115)** | |

Pozostała luka: **10^119.2 (wariant 1/rank) / 10^118.2 (wariant 1/45)**.
Kanały kinematyczne są o ~118 rzędów za słabe — obalone jako rozwiązanie
(falsified_route CC‑F005).

## 4. Problem odwrotny — co musiałaby zrobić próżnia

Warunek Λ = Λ_obs (przy Var(k)=0, N=150, g²=1):

$$x_{\rm req} = 1-\langle\cos\Phi\rangle \;\lesssim\; 4.7\times10^{-121},
\qquad {\rm Var}(k)\ \lesssim\ 3.6\times10^{-121}\ (\text{dualnie})$$

Fine-tuning względem równowagi: 10^119.8. Skala poniżej **ε_float64 ≈ 2.2×10⁻¹⁶**
— wymagana korekta nie ma reprezentacji w liczbach podwójnej precyzji
(kontrakt testowy to odzwierciedla).

## 5. Cztery trasy relaksacji próżni — zmierzone i obalone

### 5.1. Trasa termiczna — obalona pomiarem MC silnika

Gdyby kosmologiczne stygnięcie napędzało x ∝ (T/T_Pl)^p, warunek x(T_CMB)=x_req
wymaga

$$p_{\rm req} = \frac{\log_{10}(1/x_{\rm req})}{\log_{10}(M_{\rm Pl}/T_{\rm CMB})} = 3.79$$

Równowagowy pomiar `MonteCarloWakuum` (lokalny Metropolis dla sektora YM
S = −Σ cosΦ na topologii `Spin10Graph`, N=120, 3 ziarna, β = 1…64):

$$x_{\rm eq}(\beta) = A\,\beta^{-q}, \qquad A = 0.17,\quad q = 0.84 \pm 0.16$$

(zgodne z przewidywaniem harmonicznym q = 1 dla fluktuacji wokół
skonfiniowanej próżni; dla β ≳ 32 widoczna saturacja frustracyjna).

**Rozstrzygnięcie: q ≈ 1 ≪ 3.79** — równowagowy spadek daje dziś x ~ 10⁻²⁸,
luka ~10⁹³ do wymaganego. **WYKLUCZONA** (CC‑F001).

### 5.2. Trasa szklista — obalona pomiarem MC

Trajektoria ze startu gorącego przy β = 64 (4000 sweepów): x spada i zatrzymuje
się na **podłożu frustracyjnym x_f ≈ 2×10⁻³** (plakietki sfrustrowane + tryby
wolne). Luka do x_req: ~10¹¹⁸. Nawet nieskończona relaksacja nie zbliża się do
potrzebnej podłogi. **WYKLUCZONA** (CC‑F002).

### 5.3. Tracker krytyczny (typ Abbott) x(t) = C·(t_R/t)² — obalony przez BBN

W erze radiacji ρ_rad ∝ t⁻², składnik t⁻² „jedzie więc" ze stałym stosunkiem do
promieniowania. Wymuszenie Λ(t₀) = Λ_obs (N=150, g²=1, t_R = 2t_Pl):

$$C_{\rm req} = 7.7\ (>1,\ \text{niefizyczne}); \qquad
\left.\frac{\rho_{\rm vac}}{\rho_{\rm rad}}\right|_{\rm BBN} = 424
\ \gg\ 0.068\ (=r_{\rm BBN}^{\rm max},\ \Delta N_{\rm eff}\le0.3)$$

Przekroczenie o ~3.8 rzędu, niezależne od C i t_R (przy stałym prawie t⁻²).
**WYKLUCZONY przez BBN** (CC‑F003). Uwaga: dla C=1 tracker nie dochodzi do
Λ_obs: Λ(t₀) = 0.13Λ_obs.

### 5.4. Hybryda freeze — równoważna fine-tuningowi

Relaksacja t⁻² do podłogi x_f = x_req, potem Λ = const: podłoga osiągana przy

$$t_f = t_R/\sqrt{x_f} \approx 1.6\times10^{17}\ {\rm s} \gg t_{\rm BBN}\approx 0.1{-}1\ {\rm s}$$

— sztywna składowa rujnuje nukleosyntezę. Zamrożenie przed BBN wymaga
wejściowej x_f ≲ 10⁻¹²¹, tj. **jawnego fine-tuningu tej samej wielkości co
problem wyjściowy**. **SFALSZYFICOWANA jako mechanizm** (CC‑F004).

## 6. Pozostałe okno i warunek krzyżowy

Audyt zwęża rozwiązanie do jednej postaci:

> **Prawdziwa próżnia osiąga x ≲ 5×10⁻¹²¹ przed nukleosyntezą (t ≲ 0.1 s) i pozostaje tam do dziś** (wpis CC‑R001).

Jedyna parametryczna kandydatka mechanizmu — **podłoga nieperturbacyjna**
x_f ~ exp(−2π/α_eff) (typ instanton/gąsienica sieci):

$$x_f = x_{\rm req} \;\Rightarrow\; S_{\rm inst} = 277, \qquad \alpha_{\rm eff} = 0.0227$$

Silnik ma α_GUT = 0.04 (stosunek 1.76). To **PERSPEKTYWA, nie mechanizm**
(CC‑H004): wymaga (i) wykazania istnienia podłogi nieperturbacyjnej w modelu,
(ii) spójności sprzężenia na skali dopasowania z modułem RGE
(`src/numerical_rge_solver.py`) — pierwszy konkretny, **falsyfikowalny warunek
krzyżowy** między problemem Λ a unifikacją sprzężeń.

## 7. Werdykt

```
status: LOCALIZED_OPEN
```

1. Model podaje Λ wyliczalną z dwóch obserwabli grafu — ale odziedziczył pełne
   10¹²⁰ (žadnej darmowej redukcji).
2. Kanały kinematyczne: łącznie ≤ 10¹·⁹ — za słabe o ~118 rzędów.
3. Trasy: termiczna, szklista, tracker, freeze — **sfalsyfikowane wewnętrznie**
   (pomiarami MC silnika + granicą BBN).
4. Pozostały wymóg jest ścisły: x ≲ 5×10⁻¹²¹ przed t ≃ 0.1 s; kandydacki
   mechanizm podłogi wymaga α_eff ≈ 0.0227 zgodnego z biegiem sprzężenia.

Problem stałej kosmologicznej **nie jest rozwiązany** — jest natomiast w tym
modelu *zlokalizowany w dwóch liczbach i zredukowany do weryfikowalnego
warunku* (CC‑R001 + CC‑H004), co zamienia problem „poczuj się swobodnie w 120
rzędach" w dwie konkretne nierówności do sprawdzenia w przyszłych wersjach
silnika.

## 8. Reprodukcja

```bash
PYTHONPATH=src python3 scripts/rozwiaz_stala_kosmologiczna.py          # pełny audyt (~1 min)
PYTHONPATH=src python3 scripts/rozwiaz_stala_kosmologiczna.py --szybki # wersja szybka
PYTHONPATH=src python3 -m unittest tests.test_stala_kosmologiczna -v   # 39 kontraktów
```

Wykresy: `results/stala_kosmologiczna/rozbieznosci_qft.png`,
`xeq_beta.png`, `relaksacja_lambda.png`.

## 9. Ograniczenia

- Pomiary MC: sektor **euklidesowy** (jak w wyprowadzeniu Λ); pełny sektor
  mieszany z η(△) Publ. I może przesunąć równowagę (CC‑U001).
- Mapowanie β ↔ T kosmicznym jest ansatzem audytowym, ale werdykt trasy
  termicznej oparty jest na równowagowym pomiarze q i nie zależy od szczegółów
  mapowania (wymagane 3.79 vs zmierzone ≤ 1.2).
- Granica BBN przyjęta ΔN_eff ≤ 0.3 (Planck+BBN).
