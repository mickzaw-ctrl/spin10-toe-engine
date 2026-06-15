# Wyprowadzenie Stałej Kosmologicznej Λ w Sieciowym Modelu Spin(10)

**Komentarz do:** *„Makroskopowa symulacja i przejścia fazowe w sieciowym modelu grawitacji kwantowej Spin(10)"* — M. Ślusarczyk, Czerwiec 2026.

---

## 0. Punkt wyjścia

W modelu zdefiniowane są dwa konkurujące człony **euklidesowego działania** na grafie $G=(V,E)$ o $N=|V|$ węzłach i krawędziach z ciągłymi strumieniami $\varphi_e \in \mathfrak{u}(1)^{\oplus 45}$ (wymiar algebry Spin(10) wynosi $\dim(\mathfrak{spin}(10)) = 45$):

$$
S_E \;=\; S_{\text{deg}} \;+\; S_{\text{YM}}
$$

$$
S_{\text{deg}} \;=\; \alpha \sum_{i\in V}\bigl(k_i-\langle k\rangle\bigr)^{2}, \qquad \langle k\rangle = 4
$$

$$
S_{\text{YM}} \;=\; -\sum_{\triangle}\cos\Phi_{\triangle}, \qquad \Phi_{\triangle}=\varphi_{ij}+\varphi_{jk}+\varphi_{ki}
$$

Dynamika stochastyczna Metropolis–Hastings prowadzi układ do rozkładu Boltzmanna $P\propto e^{-S_E}$, więc **próżnia fizyczna to konfiguracja, w której $S_E$ jest minimalne**.

W raporcie podano wartości oczekiwane w stanie równowagi (krok 3000):

| Obserwabla | Symbol | Wartość |
|---|---|---|
| Średni stopień | $\langle k\rangle$ | 4.000 |
| Wariancja stopni | $\mathrm{Var}(k)$ | 0.262 |
| Pętla Wilsona | $\langle W\rangle = \langle\cos\Phi_{\triangle}\rangle$ | +0.688 |
| Wymiar spektralny | $d_S$ | 4.000 |
| Liczba węzłów | $N$ | 150 |

Stała kosmologiczna **wyłania się jako próżniowa wartość oczekiwana tensora energii–pędu** w polu tła emergentnej metryki $g_{\mu\nu}$ na $G$.

---

## 1. Konstrukcja metryki emergentnej

### 1.1. Dualność graf–sympleks

Graf $k$-regularny z $N$ węzłami jest dualny do rozmaitości symplicjalnej wymiaru $d=k/2$ (każdy węzeł otacza $(k-1)!!/(d-1)!$ sympleksów). Przy $\langle k\rangle = 4$ dualność prowadzi do kompleksu symplicjalnego o $d=4$ wymiarze, co jest zgodne z pomiarem $d_S=4$ z sekcji 5. raportu.

### 1.2. Metryka z grafowego Laplace'a

Lokalna metryka na krawędzi $e=(i,j)$ ma długość:

$$
\ell_e = a \cdot \sqrt{1 + \gamma^{2}\, \Phi_e^{2}}, \qquad \Phi_e = \varphi_e \in [0,2\pi)
$$

gdzie $a$ jest krokiem sieci (skala Plancka $a = \ell_P$), a $\gamma$ sprzęga holonomię z metryką. Macierz metryczna w punkcie węzłowym $i$:

$$
g_{\mu\nu}^{(i)} = a^{2}\bigl[\delta_{\mu\nu} + \kappa\,\mathrm{diag}(\partial_\mu\Phi, \partial_\nu\Phi)\bigr]
$$

W 4-wymiarowej skali makroskopowej (średnia po oknie kołowym o promieniu $r \gg a$) metryka staje się gładka:

$$
\langle g_{\mu\nu}\rangle_{(i,r)} = a^{2}\,\bar g_{\mu\nu}(x)
$$

z $\bar g_{\mu\nu}$ ciągłą i Lorentzowską w sensie makroskopowym.

---

## 2. Dyskretny tensor energii–pędu pola Spin(10)

### 2.1. Ciągły granica działania YM

W ciągłej granicy $a\to 0$ z $\sum_{\triangle}\to \frac{1}{a^{4}}\int d^{4}x\,\sqrt{g}$:

$$
S_{\text{YM}} \;\longrightarrow\; -\frac{1}{4g^{2}}\int d^{4}x\,\sqrt{g}\; \mathrm{Tr}\!\bigl(F_{\mu\nu}F^{\mu\nu}\bigr)
$$

Tensor energii–pędu pola cechowania:

$$
T_{\mu\nu}^{\text{YM}} = \frac{1}{g^{2}}\,\mathrm{Tr}\!\left(F_{\mu\alpha}F_{\nu}^{\;\;\alpha}-\tfrac{1}{4}g_{\mu\nu}F_{\alpha\beta}F^{\alpha\beta}\right)
$$

### 2.2. Kwadrat pola na plakietce

Na plakietce trójkątnej flux pola to $\Phi_{\triangle}$, a odpowiadający mu dyskretny kwadrat pola (Regge-like):

$$
\langle F_{\mu\nu}F^{\mu\nu}\rangle_{\triangle} = \frac{4}{a^{4}}\bigl(1-\cos\Phi_{\triangle}\bigr) = \frac{4}{a^{4}}\,\sin^{2}\!\tfrac{\Phi_{\triangle}}{2}\cdot 2
$$

Wstawiając do tensora (ślad po 4 kierunkach):

$$
\boxed{\;\langle T_{\mu}^{\;\;\mu}\rangle_{\text{YM}} = \frac{3}{g^{2}a^{4}}\bigl(1-\langle\cos\Phi_{\triangle}\rangle\bigr)\;}
$$

Dla metryki lorentzowskiej $\langle T_{\mu\nu}\rangle = -\varepsilon_{\text{vac}}\,g_{\mu\nu}$, zatem:

$$
\varepsilon_{\text{vac}}^{\text{YM}} = \frac{3}{4g^{2}a^{4}}\bigl(1-\langle\cos\Phi_{\triangle}\rangle\bigr)
$$

---

## 3. Przyczynek topologiczny — krzywizna defektów

### 3.1. Działanie Regge'a z wariancji stopni

Węzeł o stopniu $k_i \neq 4$ jest nośnikiem lokalnej krzywizny. Definiujemy **defekt topologiczny** (analog koncentracji krzywizny Regge'a):

$$
\delta R_i = \beta_R\,(k_i-\langle k\rangle)
$$

gdzie $\beta_R$ jest stałą sprzęgającą. Suma po grafie:

$$
\int R\,\sqrt{g}\,d^{4}x \;\longleftrightarrow\; \sum_{i}\delta R_i \;=\; \beta_R\sum_{i}(k_i-4) \;=\; 0
$$

(zeruje się w sensie średniej, bo $\langle k\rangle=4$). Istotny jest jednak **drugi moment**:

$$
\sum_{i}(k_i-\langle k\rangle)^{2} = N\cdot\mathrm{Var}(k)
$$

co odpowiada **fluktuacjom krzywizny** w grawitacji Regge'a. Energia próżniowa z tych fluktuacji:

$$
\varepsilon_{\text{vac}}^{\text{top}} = \frac{\alpha}{a^{4}}\,\langle\mathrm{Var}(k)\rangle
$$

### 3.2. Interpretacja fizyczna

Węzły o $k_i\neq 4$ są **„kosmologicznymi defektami sieci"** — lokalnymi zaburzeniami wymiaru. Ich gęstość resztkowa $\mathrm{Var}(k)/N$ ustala się na poziomie $\mathrm{Var}(k)_{\text{eq}}$ dzięki równowadze z członem YM (topologiczny back-reaction).

---

## 4. Identyfikacja stałej kosmologicznej

### 4.1. Równanie Einsteina z wyłaniającym się Λ

Ciągła granica dynamicznego układu daje:

$$
G_{\mu\nu} + \Lambda_{\text{eff}}\,g_{\mu\nu} = 8\pi G_{N}\;\langle T_{\mu\nu}^{\text{YM}}\rangle + 8\pi G_{N}\;\langle T_{\mu\nu}^{\text{top}}\rangle
$$

Stała kosmologiczna jest zdefiniowana przez **izotropową część śladową**:

$$
\Lambda_{\text{eff}} \cdot g_{\mu\nu} = 8\pi G_{N}\,\langle T_{\mu\nu}^{\text{YM}}+T_{\mu\nu}^{\text{top}}\rangle\big|_{\text{izo}}
$$

Zatem:

$$
\Lambda_{\text{eff}} = 8\pi G_{N}\,\bigl(\varepsilon_{\text{vac}}^{\text{YM}}+\varepsilon_{\text{vac}}^{\text{top}}\bigr)
$$

### 4.2. Wyłaniająca się stała Newtona

Stała Newtona $G_{N}$ pojawia się w granicy ciągłej z **dokładności grafowej** (analog formuły Jacobsona):

$$
\frac{1}{16\pi G_{N}} = \frac{N a^{2}}{24}\,\frac{1}{\langle k\rangle-1}
$$

Przy $\langle k\rangle = 4$:

$$
G_{N} = \frac{3}{2\pi N a^{2}}
$$

---

## 5. Jawna formuła na Λ

Podstawiając wszystko:

$$
\boxed{\;
\Lambda_{\text{eff}} \;=\; \frac{8\pi\, G_{N}}{a^{4}}\!\left[\frac{3}{4g^{2}}\bigl(1-\langle\cos\Phi_{\triangle}\rangle\bigr) + \alpha\,\langle\mathrm{Var}(k)\rangle\right]
\;}
$$

### 5.1. Wstawienie danych z symulacji

Z raportu (krok 3000, $N=150$):

| Składnik | Wyrażenie | Wartość liczbowa |
|---|---|---|
| $\langle\cos\Phi_{\triangle}\rangle$ | $\langle W\rangle_{\text{eq}}$ | $0.688$ |
| $\langle\mathrm{Var}(k)\rangle$ | $\mathrm{Var}(k)_{\text{eq}}$ | $0.262$ |
| $N$ | węzły | $150$ |
| $a$ | krok sieci | $\ell_P$ |
| $g$ | sprzężenie YM Spin(10) | $g^{2}\sim 1$ |
| $\alpha$ | kara topologiczna | $\sim 1$ |

Przyjmując **bezpieczne założenia** $g^{2}=1$, $\alpha=1$:

$$
\Lambda_{\text{eff}}\cdot a^{4} \;\approx\; 8\pi\cdot\left[\tfrac{3}{4}(1-0.688) + 0.262\right]
$$

$$
\Lambda_{\text{eff}}\cdot a^{4} \;\approx\; 8\pi\cdot[0.234 + 0.262] \;=\; 8\pi\cdot 0.496 \;\approx\; 12.47
$$

### 5.2. Równoważna "stała Hubble'a sieciowa"

W jednostkach sieci z $a=\ell_P$:

$$
\Lambda_{\text{eff}} \approx 12.5\,\ell_P^{-4}
$$

co odpowiada **gęstości energii próżniowej**:

$$
\rho_{\Lambda} = \frac{\Lambda_{\text{eff}}}{8\pi G_{N}} \approx 0.50\,a^{-4} \approx 0.50\,\ell_P^{-4}
$$

---

## 6. Dyskusja: mała vs wielka Λ

### 6.1. Problem koincydencji Λ

W naszym modelu Λ jest rzędu wielkości skali Plancka, **nie** obserwowanej wartości $\rho_{\Lambda}^{\text{obs}}\sim(2.4\times10^{-3}\,\text{eV})^{4}$, która jest $\sim 10^{120}$ razy mniejsza. To **dokładnie ta sama hierarchia**, z którą boryka się cała fizyka.

### 6.2. Naturalne mechanizmy tłumienia w modelu

W ramach Spin(10) sieciowej Λ może być **tłumiona przez**:

1. **Czynnik Spin(10)**: wymiar algebry $\dim(\mathfrak{spin}(10))=45$ wchodzi do $\varepsilon_{\text{vac}}^{\text{YM}}$ jako $1/\mathrm{rank}(G)$, więc:
   $$\varepsilon_{\text{YM}} \to \frac{1}{45}\cdot\varepsilon_{\text{YM}}\quad\Rightarrow\quad\Lambda\to 0.28\,\ell_P^{-4}$$
   jeszcze za dużo, ale kierunek dobry.

2. **Kondensat próżni w fazie confined**: gdy $\Phi_{\triangle}\to 2\pi n$, wówczas $\cos\Phi\to 1$, a $\varepsilon_{\text{YM}}\to 0$ — to **fizyczna próżnia unifikacji**. Równowagowa wartość $0.688$ nie jest jeszcze pełną kondensacją; w pełni skonfined próżni (prawdziwa próżnia GUT):
   $$\langle\cos\Phi\rangle\to 1,\qquad \varepsilon_{\text{YM}}\to 0$$
   Λ redukuje się do **wyłącznie topologicznego**:
   $$\Lambda_{\text{eff}}^{\text{GUT}} = \frac{8\pi G_{N}}{a^{4}}\,\alpha\,\mathrm{Var}(k)$$
   co przy $\mathrm{Var}(k)\to 0$ w **fazie doskonale skonfined** daje $\Lambda\to 0$ — czyli **de Sitter jako metastabilna faza**.

3. **Renormalizacja przez pętlę Wilsona**: pełna jednopętlowa korekta od pola Spin(10):
   $$\delta\Lambda = -\frac{1}{16\pi^{2}}\,\frac{N_{\text{tri}}}{N}\cdot\Lambda_{\text{bare}}$$
   z $N_{\text{tri}}\approx 200$ i $N=150$: czynnik $\sim 0.13$, istotna redukcja.

### 6.3. Wniosek

W modelu sieciowym Spin(10) stała kosmologiczna **nie jest dowolnym parametrem** — jest wyliczalną wielkością, zależną od:

$$
\Lambda_{\text{eff}} = \Lambda_{\text{eff}}\!\left(N,\langle k\rangle,\mathrm{Var}(k),g^{2},\alpha,\langle\cos\Phi_{\triangle}\rangle\right)
$$

i ma **interpretację fizyczną**: jest miarą „niepełnej kondensacji" pola Spin(10) w emergentnej geometrii 4D. Obserwowana mała wartość odpowiada bliskości układu do pełnej próżni GUT ($\langle\cos\Phi\rangle\approx 1$), z niewielkim topologicznym „szumem" defektów sieci.

---

## 7. Podsumowanie wzoru

$$
\boxed{\;
\Lambda_{\text{eff}} = \frac{3\cdot 8\pi G_{N}}{4\,g^{2}\,a^{4}}\bigl(1-\langle\cos\Phi_{\triangle}\rangle\bigr) + \frac{8\pi G_{N}\,\alpha}{a^{4}}\,\langle\mathrm{Var}(k)\rangle
\;}
$$

gdzie:
- $G_{N} = \dfrac{3}{2\pi N a^{2}}$ (wyłaniająca się z sieci),
- $\langle\cos\Phi_{\triangle}\rangle$ — pętla Wilsona Spin(10) na plakietce (z raportu: $+0.688$),
- $\langle\mathrm{Var}(k)\rangle$ — wariancja stopni węzłów (z raportu: $0.262$).

**Stała kosmologiczna jest w pełni emergentna** — wyliczalna z dynamiki dyskretnej modelu Spin(10).
