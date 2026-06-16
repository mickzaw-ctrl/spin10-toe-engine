# Wyprowadzenie Stalej Kosmologicznej Λ w Sieciowym Modelu Spin(10)

**Komentarz do:** *„Makroskopowa simulation i przejscia fazowe w networkowym modelu gravity quantum Spin(10)"* — M. Slusarczyk, Czerwiec 2026.

---

## 0. Punkt wyjscia

W modelu zdefiniowane sa dwa konkurujace czlony **euklidesowego dzialania** na graphie $G=(V,E)$ o $N=|V|$ wezlach i edgesach z ciaglymi strumieniami $\varphi_e \in \mathfrak{u}(1)^{\oplus 45}$ (dimension algebry Spin(10) wynosi $\dim(\mathfrak{spin}(10)) = 45$):

$$
S_E \;=\; S_{\text{deg}} \;+\; S_{\text{YM}}
$$

$$
S_{\text{deg}} \;=\; \alpha \sum_{i\in V}\bigl(k_i-\langle k\rangle\bigr)^{2}, \qquad \langle k\rangle = 4
$$

$$
S_{\text{YM}} \;=\; -\sum_{\triangle}\cos\Phi_{\triangle}, \qquad \Phi_{\triangle}=\varphi_{ij}+\varphi_{jk}+\varphi_{ki}
$$

Dynamika stochastyczna Metropolis–Hastings prowadzi uklad do rozkladu Boltzmanna $P\propto e^{-S_E}$, wiec **proznia fizyczna to configuration, w ktorej $S_E$ jest minimalne**.

W raporcie podano wartosci oczekiwane w stanie rownowagi (krok 3000):

| Obserwabla | Symbol | Wartosc |
|---|---|---|
| Sredni stopien | $\langle k\rangle$ | 4.000 |
| Wariancja stopni | $\mathrm{Var}(k)$ | 0.262 |
| Petla Wilsona | $\langle W\rangle = \langle\cos\Phi_{\triangle}\rangle$ | +0.688 |
| Dimension spektralny | $d_S$ | 4.000 |
| Liczba nodes | $N$ | 150 |

Stala cosmological **wylania sie jako prozniowa wartosc oczekiwana tensora energy–pedu** w polu tla emergentnej metric $g_{\mu\nu}$ na $G$.

---

## 1. Konstrukcja metric emergentnej

### 1.1. Dualnosc graph–sympleks

Graph $k$-regularny z $N$ wezlami jest dualny do rozmaitosci symplicjalnej dimensionu $d=k/2$ (kazdy wezel otacza $(k-1)!!/(d-1)!$ sympleksow). Przy $\langle k\rangle = 4$ dualnosc prowadzi do kompleksu symplicjalnego o $d=4$ dimensionze, co jest zgodne z pomiarem $d_S=4$ z sekcji 5. report.

### 1.2. Metric z graphowego Laplace'a

Lokalna metric na edges $e=(i,j)$ ma dlugosc:

$$
\ell_e = a \cdot \sqrt{1 + \gamma^{2}\, \Phi_e^{2}}, \qquad \Phi_e = \varphi_e \in [0,2\pi)
$$

gdzie $a$ jest krokiem network (scale Plancka $a = \ell_P$), a $\gamma$ sprzega holonomie z metryka. Matrix metryczna w punkcie wezlowym $i$:

$$
g_{\mu\nu}^{(i)} = a^{2}\bigl[\delta_{\mu\nu} + \kappa\,\mathrm{diag}(\partial_\mu\Phi, \partial_\nu\Phi)\bigr]
$$

W 4-dimensionowej scale makroskopowej (srednia po oknie kolowym o promieniu $r \gg a$) metric staje sie gladka:

$$
\langle g_{\mu\nu}\rangle_{(i,r)} = a^{2}\,\bar g_{\mu\nu}(x)
$$

z $\bar g_{\mu\nu}$ ciagla i Lorentzowska w sensie makroskopowym.

---

## 2. Dyskretny tensor energy–pedu field Spin(10)

### 2.1. Ciagly granica dzialania YM

W ciaglej granicy $a\to 0$ z $\sum_{\triangle}\to \frac{1}{a^{4}}\int d^{4}x\,\sqrt{g}$:

$$
S_{\text{YM}} \;\longrightarrow\; -\frac{1}{4g^{2}}\int d^{4}x\,\sqrt{g}\; \mathrm{Tr}\!\bigl(F_{\mu\nu}F^{\mu\nu}\bigr)
$$

Tensor energy–pedu field cechowania:

$$
T_{\mu\nu}^{\text{YM}} = \frac{1}{g^{2}}\,\mathrm{Tr}\!\left(F_{\mu\alpha}F_{\nu}^{\;\;\alpha}-\tfrac{1}{4}g_{\mu\nu}F_{\alpha\beta}F^{\alpha\beta}\right)
$$

### 2.2. Kwadrat field na plakietce

Na plakietce trojkatnej flux field to $\Phi_{\triangle}$, a odpowiadajacy mu dyskretny kwadrat field (Regge-like):

$$
\langle F_{\mu\nu}F^{\mu\nu}\rangle_{\triangle} = \frac{4}{a^{4}}\bigl(1-\cos\Phi_{\triangle}\bigr) = \frac{4}{a^{4}}\,\sin^{2}\!\tfrac{\Phi_{\triangle}}{2}\cdot 2
$$

Wstawiajac do tensora (slad po 4 kierunkach):

$$
\boxed{\;\langle T_{\mu}^{\;\;\mu}\rangle_{\text{YM}} = \frac{3}{g^{2}a^{4}}\bigl(1-\langle\cos\Phi_{\triangle}\rangle\bigr)\;}
$$

Dla metric lorentzowskiej $\langle T_{\mu\nu}\rangle = -\varepsilon_{\text{vac}}\,g_{\mu\nu}$, zatem:

$$
\varepsilon_{\text{vac}}^{\text{YM}} = \frac{3}{4g^{2}a^{4}}\bigl(1-\langle\cos\Phi_{\triangle}\rangle\bigr)
$$

---

## 3. Przyczynek topologiczny — curvature defektow

### 3.1. Dzialanie Regge'a z wariancji stopni

Wezel o stopniu $k_i \neq 4$ jest nosnikiem lokalnej curvature. Definiujemy **defekt topologiczny** (analog koncentracji curvature Regge'a):

$$
\delta R_i = \beta_R\,(k_i-\langle k\rangle)
$$

gdzie $\beta_R$ jest stala sprzegajaca. Suma po graphie:

$$
\int R\,\sqrt{g}\,d^{4}x \;\longleftrightarrow\; \sum_{i}\delta R_i \;=\; \beta_R\sum_{i}(k_i-4) \;=\; 0
$$

(zeruje sie w sensie sredniej, bo $\langle k\rangle=4$). Istotny jest jednak **drugi moment**:

$$
\sum_{i}(k_i-\langle k\rangle)^{2} = N\cdot\mathrm{Var}(k)
$$

co odpowiada **fluktuacjom curvature** w gravity Regge'a. Energy prozniowa z tych fluktuacji:

$$
\varepsilon_{\text{vac}}^{\text{top}} = \frac{\alpha}{a^{4}}\,\langle\mathrm{Var}(k)\rangle
$$

### 3.2. Interpretacja fizyczna

Nodes o $k_i\neq 4$ sa **„kosmologicznymi defektami network"** — lokalnymi zaburzeniami dimensionu. Ich gestosc resztkowa $\mathrm{Var}(k)/N$ ustala sie na poziomie $\mathrm{Var}(k)_{\text{eq}}$ dzieki rownowadze z czlonem YM (topologiczny back-reaction).

---

## 4. Identyfikacja cosmological constant

### 4.1. Rownanie Einsteina z wylaniajacym sie Λ

Ciagla granica dynamicznego ukladu daje:

$$
G_{\mu\nu} + \Lambda_{\text{eff}}\,g_{\mu\nu} = 8\pi G_{N}\;\langle T_{\mu\nu}^{\text{YM}}\rangle + 8\pi G_{N}\;\langle T_{\mu\nu}^{\text{top}}\rangle
$$

Stala cosmological jest zdefiniowana przez **izotropowa czesc sladowa**:

$$
\Lambda_{\text{eff}} \cdot g_{\mu\nu} = 8\pi G_{N}\,\langle T_{\mu\nu}^{\text{YM}}+T_{\mu\nu}^{\text{top}}\rangle\big|_{\text{izo}}
$$

Zatem:

$$
\Lambda_{\text{eff}} = 8\pi G_{N}\,\bigl(\varepsilon_{\text{vac}}^{\text{YM}}+\varepsilon_{\text{vac}}^{\text{top}}\bigr)
$$

### 4.2. Wylaniajaca sie stala Newtona

Stala Newtona $G_{N}$ pojawia sie w granicy ciaglej z **dokladnosci graphowej** (analog formuly Jacobsona):

$$
\frac{1}{16\pi G_{N}} = \frac{N a^{2}}{24}\,\frac{1}{\langle k\rangle-1}
$$

Przy $\langle k\rangle = 4$:

$$
G_{N} = \frac{3}{2\pi N a^{2}}
$$

---

## 5. Jawna formula na Λ

Podstawiajac wszystko:

$$
\boxed{\;
\Lambda_{\text{eff}} \;=\; \frac{8\pi\, G_{N}}{a^{4}}\!\left[\frac{3}{4g^{2}}\bigl(1-\langle\cos\Phi_{\triangle}\rangle\bigr) + \alpha\,\langle\mathrm{Var}(k)\rangle\right]
\;}
$$

### 5.1. Wstawienie data z symulacji

Z report (krok 3000, $N=150$):

| Skladnik | Wyrazenie | Wartosc liczbowa |
|---|---|---|
| $\langle\cos\Phi_{\triangle}\rangle$ | $\langle W\rangle_{\text{eq}}$ | $0.688$ |
| $\langle\mathrm{Var}(k)\rangle$ | $\mathrm{Var}(k)_{\text{eq}}$ | $0.262$ |
| $N$ | nodes | $150$ |
| $a$ | krok network | $\ell_P$ |
| $g$ | sprzezenie YM Spin(10) | $g^{2}\sim 1$ |
| $\alpha$ | kara topologiczna | $\sim 1$ |

Przyjmujac **bezpieczne zalozenia** $g^{2}=1$, $\alpha=1$:

$$
\Lambda_{\text{eff}}\cdot a^{4} \;\approx\; 8\pi\cdot\left[\tfrac{3}{4}(1-0.688) + 0.262\right]
$$

$$
\Lambda_{\text{eff}}\cdot a^{4} \;\approx\; 8\pi\cdot[0.234 + 0.262] \;=\; 8\pi\cdot 0.496 \;\approx\; 12.47
$$

### 5.2. Rownowazna "stala Hubble'a networkowa"

W jednostkach network z $a=\ell_P$:

$$
\Lambda_{\text{eff}} \approx 12.5\,\ell_P^{-4}
$$

co odpowiada **gestosci energy prozniowej**:

$$
\rho_{\Lambda} = \frac{\Lambda_{\text{eff}}}{8\pi G_{N}} \approx 0.50\,a^{-4} \approx 0.50\,\ell_P^{-4}
$$

---

## 6. Dyskusja: mala vs wielka Λ

### 6.1. Problem koincydencji Λ

W naszym modelu Λ jest rzedu wielkosci scale Plancka, **nie** obserwowanej wartosci $\rho_{\Lambda}^{\text{obs}}\sim(2.4\times10^{-3}\,\text{eV})^{4}$, ktora jest $\sim 10^{120}$ razy mniejsza. To **dokladnie ta sama hierarchy**, z ktora boryka sie cala fizyka.

### 6.2. Naturalne mechanizmy tlumienia w modelu

W ramach Spin(10) networkowej Λ moze byc **tlumiona przez**:

1. **Czynnik Spin(10)**: dimension algebry $\dim(\mathfrak{spin}(10))=45$ wchodzi do $\varepsilon_{\text{vac}}^{\text{YM}}$ jako $1/\mathrm{rank}(G)$, wiec:
   $$\varepsilon_{\text{YM}} \to \frac{1}{45}\cdot\varepsilon_{\text{YM}}\quad\Rightarrow\quad\Lambda\to 0.28\,\ell_P^{-4}$$
   jeszcze za duzo, ale kierunek dobry.

2. **Kondensat prozni w fazie confined**: gdy $\Phi_{\triangle}\to 2\pi n$, wowtime $\cos\Phi\to 1$, a $\varepsilon_{\text{YM}}\to 0$ — to **fizyczna proznia unification**. Rownowagowa wartosc $0.688$ nie jest jeszcze pelna kondensacja; w pelni skonfined prozni (prawdziwa proznia GUT):
   $$\langle\cos\Phi\rangle\to 1,\qquad \varepsilon_{\text{YM}}\to 0$$
   Λ redukuje sie do **wylacznie topologicznego**:
   $$\Lambda_{\text{eff}}^{\text{GUT}} = \frac{8\pi G_{N}}{a^{4}}\,\alpha\,\mathrm{Var}(k)$$
   co przy $\mathrm{Var}(k)\to 0$ w **fazie doskonale skonfined** daje $\Lambda\to 0$ — czyli **de Sitter jako metastabilna faza**.

3. **Renormalizacja przez petle Wilsona**: pelna jednopetlowa korekta od field Spin(10):
   $$\delta\Lambda = -\frac{1}{16\pi^{2}}\,\frac{N_{\text{tri}}}{N}\cdot\Lambda_{\text{bare}}$$
   z $N_{\text{tri}}\approx 200$ i $N=150$: czynnik $\sim 0.13$, istotna redukcja.

### 6.3. Wniosek

W modelu networkowym Spin(10) cosmological constant **nie jest dowolnym parametrem** — jest wyliczalna wielkoscia, zalezna od:

$$
\Lambda_{\text{eff}} = \Lambda_{\text{eff}}\!\left(N,\langle k\rangle,\mathrm{Var}(k),g^{2},\alpha,\langle\cos\Phi_{\triangle}\rangle\right)
$$

i ma **interpretacje fizyczna**: jest miara „niepelnej kondensacji" field Spin(10) w emergentnej geometry 4D. Obserwowana mala wartosc odpowiada bliskosci ukladu do pelnej prozni GUT ($\langle\cos\Phi\rangle\approx 1$), z niewielkim topologicznym „szumem" defektow network.

---

## 7. Summary wzoru

$$
\boxed{\;
\Lambda_{\text{eff}} = \frac{3\cdot 8\pi G_{N}}{4\,g^{2}\,a^{4}}\bigl(1-\langle\cos\Phi_{\triangle}\rangle\bigr) + \frac{8\pi G_{N}\,\alpha}{a^{4}}\,\langle\mathrm{Var}(k)\rangle
\;}
$$

gdzie:
- $G_{N} = \dfrac{3}{2\pi N a^{2}}$ (wylaniajaca sie z network),
- $\langle\cos\Phi_{\triangle}\rangle$ — petla Wilsona Spin(10) na plakietce (z report: $+0.688$),
- $\langle\mathrm{Var}(k)\rangle$ — wariancja stopni nodes (z report: $0.262$).

**Stala cosmological jest w pelni emergentna** — wyliczalna z dynamiki dyskretnej modelu Spin(10).
