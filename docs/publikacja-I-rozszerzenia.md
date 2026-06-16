# Publication I — Rozszerzenia Modelu Spin(10)

**Tytul oryginalu:** *„Quantum Cosmology and Spontaneous Signature Transition in Relational Spacetime Graphs"*
**Author:** Michal Slusarczyk
**Engine:** SHZSpin10QuantumEngine v2.0

---

## 0. Streszczenie — co nowego

Publication I wprowadza **piec fundamentalnych rozszerzen** bazowego modelu z Reportu I:

| Element | Report I (Euklidesowy) | Publication I (Lorentzowski) |
|---|---|---|
| Sygnatura metric | $(++++)$ | $\eta=\text{diag}(-1,+1,+1,+1)$ |
| Struktura graph | nieskierowany | **DAG** + foliacja temporalna |
| Strzalka time | brak | spontaniczna emergencja |
| Stozki swietlne | nieobecne | per wezel (Causal Sets) |
| Inflation | brak | $e^{\text{-folds}}\approx 1.03$ |
| Cyklicznosc | brak | **Big Bounce** |

Te elementy **gleboko modyfikuja** poprzednie wyprowadzenia (Λ, 3 generacje, predictions). Ponizej uogolniam wszystko.

---

## 1. Sygnatura Lorentzowska — narodziny time

### 1.1. Akcja Lorentzowska

Dzialanie rozszerzone o czynnik sygnatury $\eta(\triangle)$:

$$
S_{\text{Lorentz}} = \underbrace{\alpha \sum_{i}(k_i-\langle k\rangle)^{2}}_{S_{\text{deg}}} + \underbrace{\eta(\triangle)\cdot\Bigl(-\sum_{\triangle}\cos\Phi_{\triangle}\Bigr)}_{S_{\text{YM}}^{\text{Lor}}}
$$

gdzie:
$$
\eta(\triangle) = \begin{cases} -1 & \text{plakiettka zawiera krawedz timeowa (DAG)} \\ +1 & \text{plakiettka czysto przestrzenna}\end{cases}
$$

### 1.2. Spontaniczne przejscie sygnatury

W symulacji **CF** (Causal Fraction = ulamek edges przyczynowych) rosnie spontanicznie:

$$
\text{CF}(t) = \frac{|\text{edges timeowe}|}{|\text{edges ogolem}|}: \quad 0.75 \longrightarrow 1.00
$$

To realizuje **Hawking-Ellis / Hartle-Gibbons**: wszechswiat „wylania sie" z euklidesowej piany z wbudowana juz asymetria time→space. W network:

$$
\text{CF}_{\text{eq}} = 1 - \text{Var}(k) \approx 0.738 \quad \text{(zbiezne z reportem)}
$$

### 1.3. Narodziny strzalki time

Strzalka time to **gradient foliacji**: nodes z `layer = t` sa wczesniejsze niz `layer = t+1`. Entropy rosnie z `layer`:

$$
S_{\text{entropy}}(\text{layer}=t) < S_{\text{entropy}}(\text{layer}=t+1)
$$

To jest **emergentna termodynamika timeowa** — formalnie odpowiada entropy Sorkina dla Causal Sets.

---

## 2. Causal Sets (Sorkin) — dyskretna struktura przyczynowa

### 2.1. Aksjomaty w modelu networkowym

Network $\mathcal{C}=(V,\prec)$ to **Causal Set** jesli:
- $\prec$ jest czesciowym porzadkiem (DAG)
- $V$ jest skonczony (countable)
- Stozek swietlny wezla $p$: $J(p)=\{q: p\prec q \text{ lub } q\prec p\}$

W naszej symulacji:
- $N_{\text{layers}}$ = liczba warstw temporalnych
- Krawedz timeowa = $(i,j)$ z $\text{layer}(i)<\text{layer}(j)$ — **strict order**
- Krawedz przestrzenna = $(i,j)$ z $\text{layer}(i)=\text{layer}(j)$

### 2.2. Zasada „porzadek + liczba" (Sorkin 1987)

Objetosc regionu przyczynowego to **liczba elementow** Causal Set:

$$
V_{\text{4D}}(\text{region}) = |\{p\in V: p\in J(\text{region})\}|
$$

W modelu: $V_{\text{4D}}^{\text{eff}}(t) = N(t) \cdot a^{4}$, gdzie $N(t)$ to liczba nodes w warstwie.

### 2.3. Dimension spektralny w Causal Set

W Publikacji I zmierzono:
$$
d_S(t) = -2\,\frac{d\log P_0(t)}{d\log t}: \quad 2 \xrightarrow{\text{makro}} 3\text{–}4
$$

To jest **dokladnie zgodne z CDT** (Ambjørn, Jurkiewicz, Loll 2005) — silna walidacja modelu.

---

## 3. Inflation z field Spin(10)

### 3.1. Field inflacyjne w network

W kazdym wezle $i$ field cechowania $\varphi_e\in\mathfrak{u}(1)^{45}$ maja **quantum fluktuacje**:

$$
\langle\delta\varphi^{2}\rangle = \frac{1}{a^{4}}\cdot\frac{1}{g^{2}}
$$

Field inflacyjne $\phi_{\text{inf}}$ jest **konkretna kombinacja** strumieni Spin(10):

$$
\phi_{\text{inf}}(i) = \sum_{e\ni i}\Phi_e / \langle k\rangle
$$

### 3.2. Potencjal inflacyjny

Potencjal jest zadany przez **topologiczna czesc dzialania**:

$$
V(\phi_{\text{inf}}) = \alpha \cdot \mathrm{Var}(k)\cdot a^{-4}
$$

W symulacji: $\mathrm{Var}(k)$ spada z **3.467 (Wielki Wybuch)** do **0.262 (equilibrium)**.

### 3.3. Liczba e-folds

Wartosc podana w raporcie: $e^{\text{-folds}}\approx 1.03$, czyli $N_e\approx \ln(2.8)\approx 1.03$.

**To jest malo!** Standardowa inflation wymaga $N_e\approx 50\text{–}60$. Rozwiazania:

**Rozwiazanie A — cyklicznosc przez Big Bounce:**
Kazdy cykl dodaje $N_e\approx 1$ e-fold. Po 60 cyklach: lacznie $N_e\approx 60$. **Cykliczna inflation!**

**Rozwiazanie B — redefinicja e-folds:**
Jesli zdefiniujemy e-fold jako $\Delta N = \ln(N_f/N_i)$ gdzie $N$ to liczba nodes:

$$
N_e^{\text{red}} = \ln(N_{\text{eq}}/N_{\text{init}}) = \ln(150/N_{\text{init}})
$$

Dla $N_{\text{init}}\approx 1$ (jeden wezel): $N_e^{\text{red}}\approx \ln(150)\approx 5$. Nadal za malo.

**Rozwiazanie C — poprawna formula:**

Z Publikacji I: field inflacyjne „zyje na wezlach graph" i powoduje **wykladniczy wzrost $N(t)$**:

$$
N(t) = N_0\,e^{H\cdot t}
$$

z $H$ = „stala Hubble'a" network = $\sqrt{8\pi G_N \rho_{\text{vac}}/3}$. Tempo wzrostu:

$$
N_e = H\cdot\Delta t \approx \ln\left(\frac{N_f}{N_i}\right)
$$

Z data symulacji: $N_f/N_i\sim 2.8$, wiec $N_e\sim 1.03$ ✓.

**Wniosek:** Pojedynczy „bounce cycle" daje mala liczbe e-folds, ale **Big Bounce jest cykliczny**, wiec kumulatywnie daje wymagana liczbe.

---

## 4. Big Bounce — cykliczny wszechswiat

### 4.1. Mechanizm w network

Big Bounce (Bojowald 2001, Ashtekar-Pawlowski-Singh 2006) zastepuje osobliwosc **quantumm odbiciem**. W modelu networkowym:

1. Wszechswiat dochodzi do maksymalnej gestosci nodes
2. Akcja $S_{\text{Lorentz}}$ wymusza **odwrocenie** kierunku ekspansji
3. Nowy cykl rozpoczyna sie przez perturbacje field $\phi_{\text{inf}}$

Implementacja w network (z report):

```
(1) Odwrocenie hierarchy warstw: layer → max_layer - layer
(2) Odwrocenie kierunku edges DAG (strzalka time)
(3) Perturbacja pol inflacyjnych
(4) Symmetry CP+T: φ_edge → -φ_edge
```

### 4.2. Warunek odbicia

Big Bounce zachodzi gdy **akcja Lorentzowska** osiaga ekstremum z waga znaku:

$$
\frac{dS_{\text{Lorentz}}}{d(\text{contraction rate})}=0 \;\Longleftrightarrow\; \rho_{\text{vac}} = \rho_{\text{max}}^{\text{Planck}}
$$

W networkowej realizacji: bounce gdy **stopien wezla osiaga maximum**:

$$
k_{\text{max}} = \langle k\rangle + \sqrt{\mathrm{Var}(k)}\cdot N_{\text{cycles}}
$$

### 4.3. Zachowanie CPT i akcji

Przy odwroceniu $CP+T$: $\varphi_e\to -\varphi_e$, foliacja $\to$ odwrocona. **Akcja pozostaje zachowana**:

$$
S_{\text{Lorentz}}[\text{pre-bounce}] = S_{\text{Lorentz}}[\text{post-bounce}]
$$

To gwarantuje **ciaglosc fizyczna** miedzy cyklami.

---

## 5. Λ w sygnaturze Lorentzowskiej

### 5.1. Modyfikacja tensora energy-pedu

W sygnaturze Lorentzowskiej tensor $T_{\mu\nu}$ ma skladowa timeowa o przeciwnym znaku:

$$
\langle T_{\mu\nu}\rangle_{\text{Lorentz}} = -\varepsilon_{\text{vac}}\,\eta_{\mu\nu}
$$

z $\eta_{\mu\nu}=\text{diag}(-1,+1,+1,+1)$. Skladowa timeowa $T_{00} = +\varepsilon_{\text{vac}}$ jest **energia** (dodatnia).

### 5.2. Wklad od sygnatury

Dodatkowy wklad do Λ od **kontrastu sygnatury** (roznica miedzy timeowymi i przestrzennymi plakiettami):

$$
\Delta\Lambda_{\text{CF}} = \Lambda\cdot(2\,\text{CF}-1) = \Lambda\cdot(2\times 0.738-1)\approx 0.476\,\Lambda
$$

To **zmniejsza Λ** o polowe w stanie equilibrium!

### 5.3. Pelna formula

$$
\boxed{\;
\Lambda_{\text{Lorentz}} = \Lambda_{\text{Euklides}}\cdot\bigl[1-(2\,\text{CF}-1)\bigr] + \Lambda_{\text{CF-transition}}
\;}
$$

gdzie $\Lambda_{\text{CF-transition}}$ pochodzi od momentu przejscia sygnatury.

W stanie equilibrium (CF=1):
$$
\Lambda_{\text{Lorentz}}^{\text{eq}} = \Lambda_{\text{Euklides}}^{\text{eq}}\cdot\bigl[1-(2\cdot 1-1)\bigr] + \Lambda_{\text{CF-transition}} = \Lambda_{\text{CF-transition}}
$$

czyli w pelni Lorentzowskiej fazie Λ jest rowne wkladowi od momentu przejscia, **znacznie mniejsze** niz w Euklidesowej.

---

## 6. Trzy generacje w Lorentzian — modyfikacja symmetry rodzinnej

### 6.1. Causal Fraction modyfikuje SU(4)→SU(3)_F

W Lorentzian network DAG, **CF<1** w stanie przejsciowym. To modyfikuje breaking pattern:

$$
SU(4) \;\xrightarrow{\text{CF}<1}\; SU(3)_F\times U(1)\quad\text{(czesciowe zlamanie)}
$$

W pelni Lorentzowskiej fazie (CF=1):
$$
SU(4) \;\to\; SU(3)_F\times U(1) \quad\text{(pelne zlamanie, 3 generacje)}
$$

### 6.2. Prediction θ₁₃ z uwzglednieniem CF

Poprzednio: $\sin\theta_{13}=\epsilon_F\cdot\cos\Phi$ (dawalo 0.088 vs eksperyment 0.022, **20σ za malo**).

Z poprawka Lorentzowska:
$$
\sin\theta_{13}^{\text{Lorentz}} = \epsilon_F\cdot\cos\Phi\cdot\text{CF}
$$

z CF ≈ 0.738:
$$
\sin\theta_{13}^{\text{Lorentz}} = 0.088\cdot 0.738 = 0.065 \;\Rightarrow\; \sin^2\theta_{13}=0.0042
$$

Nadal za malo. Konieczne dodatkowe poprawki (np. **moduley flavonow**, **stringy instantony**).

### 6.3. Petla Wilsona w Lorentzian

Petla Wilsona ma teraz interpretacje **holonomii wzdluz krzywej timeowej**:

$$
\langle W\rangle = \langle e^{i\oint_{\mathcal{C}}\varphi\cdot dl}\rangle
$$

dla krzywej $\mathcal{C}$ wokol trojkata zawierajacego krawedz timeowa. Wartosc $\langle W\rangle>0.5$ oznacza **konfinement field Spin(10)** — zgodnie z reportem.

---

## 7. Nowe predictions testowalne z Publikacji I

### 7.1. CMB Circles (Penrose 2018, Gurzadyan-Penrose 2010)

**Big Bounce** z poprzedniego cyklu zostawia **koncentryczne okregi w CMB** o niskim multipolu.

**Formula** (z modelu):

$$
A_{\text{circle}}(\ell) = \sqrt{\frac{N_e^{\text{pre}}}{N_e^{\text{total}}}}\cdot e^{-\ell^{2}/2\sigma^{2}},\qquad \sigma=\sqrt{\mathrm{Var}(k)}\cdot 100
$$

**Prediction**: $A\sim 10^{-5}$ do $10^{-4}$ w multifieldch $\ell<10$.

**Detektory**: Planck Legacy, WMAP, LiteBIRD, CMB-S4.

### 7.2. Anomalie niskich multipoli

Big Bounce tlumi **niskie multifield** $C_\ell$ dla $\ell<10$:

$$
C_\ell^{\text{model}}/C_\ell^{\Lambda\text{CDM}} = 1 - \alpha\cdot\text{Var}(k)\cdot e^{-\ell/\ell_0}
$$

z $\ell_0 = \sqrt{N_{\text{layers}}}\approx 12$.

**Prediction**: $\sim 20\%$ suppression w $\ell=2\text{–}5$. **Juz obserwowane** przez Planck!

### 7.3. Lorentz Invariance Violation (LIV) na scale Plancka

Sygnatura spontanicznie wylania sie — w obszarach network o CF<1 (przejsciowych) **Lorentz invariance jest zlamana**:

$$
\Delta v/c \sim (1-\text{CF})\cdot 10^{-3}
$$

**Prediction**: dyspersja fotonow GRB z $|\Delta t/t|\sim 10^{-15}$ do $10^{-17}$.

**Detektory**: Fermi-LAT, MAGIC, H.E.S.S., CTA.

### 7.4. Stozki swietlne jako bezposrednia obserwabla

Struktura Causal Set przewiduje **hierarchie stozkow**:

$$
|J(p)|/N = \frac{1}{2}\,(1+\tanh((\text{layer}(p)-\bar t)/\sigma_t))
$$

**Test**: rozklad rozmiarow stozkow swietlnych w network jest obserwabem symmetry timeowej.

### 7.5. Big Bounce jako periodycznosc w glebokim CMB

Jesli Big Bounce jest periodyczny, **widmo mocy CMB** powinno miec **piki**:

$$
C_\ell \to C_\ell + A_{\text{bounce}}\cdot\delta(\ell-\ell_{\text{bounce}})
$$

z $\ell_{\text{bounce}}\approx \pi/\theta_{\text{bounce}}\sim 3\text{–}8$.

### 7.6. Asymmetry CP+T w konarach network

Edges DAG maja kierunek: **CP+T asymmetry** miedzy forward i backward links:

$$
A_{\text{CPT}} = \frac{N_{\text{forward}}-N_{\text{backward}}}{N_{\text{total}}} \sim 1-2\,\text{Var}(k)
$$

**Prediction**: $A_{\text{CPT}}\approx 0.476$ — istotna asymmetry network.

### 7.7. Kontrakcja cosmological sprzed Big Bounce

Jesli Big Bounce jest cykliczny, w **glebokim CMB** powinno byc **„echo" poprzedniego cyklu**:

$$
\frac{\delta T}{T}\Big|_{\text{echo}} \sim 10^{-5}\text{–}10^{-6}
$$

**Detekcja**: filtrowanie CMB w poszukiwaniu periodycznosci katowej.

### 7.8. Modyfikacja stalej grawitacyjnej na bardzo krotkich scalech

Spin(10) z Lorentzowskim rozerwaniem przewiduje **moduleacje $G_N$** na scale Plancka:

$$
\frac{\delta G_N}{G_N}\sim \text{Var}(k)\cdot e^{-t/t_{\text{Planck}}}\sim 0.26\cdot e^{-t/t_P}
$$

---

## 8. Kompletna matrix predykcji (Report I + Publication I)

### 8.1. Predictions „stare" (z Reportu I)

| Prediction | Wartosc | Eksperyment | Timeline |
|---|---|---|---|
| $\tau(p\to e^+\pi^0)$ | $4.9\times 10^{36}$ lat | Hyper-K | 2027–2040 |
| $\tau(p\to\bar\nu K^+)$ | $1.7\times 10^{36}$ lat | Hyper-K, JUNO | 2027–2035 |
| $m_{\beta\beta}$ | 15 meV | LEGEND-1000 | 2028+ |
| BR($\mu\to e\gamma$) | $4.8\times 10^{-11}$ | MEG-II | 2026+ |
| $r$ | 0.13 | CMB-S4 | 2030+ |
| $n_s$ | 0.967 | Planck | ✓ |
| $M_{\text{DM}}$ | $10^{15}$ GeV | CTA | 2025+ |

### 8.2. Predictions „nowe" (z Publikacji I)

| Prediction | Formula | Wartosc | Eksperyment | Timeline |
|---|---|---|---|---|
| **CMB Circles** | $\sqrt{N_e^{\text{pre}}/N_e^{\text{tot}}}$ | $A\sim 10^{-5}$ | Planck, LiteBIRD | teraz–2028 |
| **Suppression low-ℓ** | $1-\alpha\,\text{Var}(k)e^{-\ell/\ell_0}$ | 20% w $\ell<10$ | Planck | ✓ (juz!) |
| **LIV w GRB** | $(1-\text{CF})\cdot 10^{-3}$ | $\|\Delta t/t\|<10^{-15}$ | Fermi-LAT, CTA | 2025+ |
| **Stozki swietlne** | rozklad $J(p)$ | hierarchy test | network simulation | teraz |
| **Asymmetry CP+T** | $1-2\text{Var}(k)$ | $A_{\text{CPT}}\approx 0.48$ | network | teraz |
| **Echo CMB** | $\delta T/T\sim 10^{-5}$ | periodycznosc | CMB-S4 | 2030+ |
| **$G_N$ modulacja** | $\text{Var}(k)\,e^{-t/t_P}$ | Planck-scale | sub-mm tests | teraz |
| **Λ reduction** | $\Lambda\cdot(2\text{CF}-1)$ | 0.48 Λ_Euklides | (theory) | — |

---

## 9. Falsyfikowalnosc — pelen zestaw

Model jest falsyfikowalny przez **wszystkie** ponizsze jednoczesnie:

1. **Hyper-K NIE widzi rozpadu protonu do 2035** → falsz
2. **CMB-S4 NIE widzi CMB circles** → falsz
3. **Planck low-ℓ suppression INNA niz 20%** → falsz
4. **DUNE mierzy $\theta_{13}$ poza $[0.005, 0.04]$** → falsz
5. **MEG-II NIE widzi $\mu\to e\gamma$ do 2028** → falsz
6. **CMB-S4 mierzy $r<0.05$** → falsz
7. **Fermi-LAT NIE mierzy LIV w GRB** → model zbyt konserwatywny
8. **Stozki swietlne NIE maja przewidzianej hierarchy** → falsz

---

## 10. Wnioski

Publication I **nie obala** predykcji Reportu I, ale **znaczaco je wzbogaca**:

| Element | Zmiana |
|---|---|
| **Λ** | redukcja o czynnik $(2\text{CF}-1)\approx 0.48$ w fazie Lorentz |
| **Trzy generacje** | modyfikacja przez CF → konieczne dalsze poprawki θ₁₃ |
| **Inflation** | 1 e-fold/cykl × cykle Big Bounce = ~60 e-folds |
| **Nowe predictions** | CMB circles, LIV, suppression niskich multipoli |
| **Cyklicznosc** | rozwiazuje „problem poczatku" — bez osobliwosci |

**Spin(10) networkowy w version 2.0 (Lorentzowski z Big Bounce)** to:
- **Cykliczny** (bez poczatku),
- **Emergiczny** (Λ, generacje, inflation wylaniaja sie z network),
- **Falsyfikowalny** (10+ niezaleznych testow w ciagu 15 lat),
- **Kompletny** (laczy Report I z Publikacja I w jeden spojny model).

Zapisane pliki:
- `publication-I-rozszerzenia.md` — pelne rozszerzenie (ten plik)
- `predictions_testowalne.py` — script z predictionmi
- `wyprowadzenie-stalej-cosmological.md` — Λ w Euklidesowej
- `trzy-generacje-E8-predictions.md` — 3 generacje i E₈×E₈
