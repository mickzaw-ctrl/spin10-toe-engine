# Definicja Teorii Wszystkiego — RC-ToE (domknięcie reflektywne)

**Dokument:** definicja + procedura decyzyjna, nie teoria fizyczna
**Data:** 2026-09-19 · **Repozytorium:** `mickzaw-ctrl/spin10-toe-engine`
**Status epistemiczny:** `DEFINITION_AND_DECISION_PROCEDURE` — twierdzenia matematyczne
oznaczone są jako `theorem` i są *wykonane*, nie zacytowane; każdy pomysł fizyczny jest
oznaczony `project_hypothesis`, `open_task` albo `speculative` (rejestr:
[`docs/RC_TOE_ASSUMPTIONS.json`](RC_TOE_ASSUMPTIONS.json))
**Jądro obliczeniowe:** [`src/toe_closure_kernel.py`](../src/toe_closure_kernel.py),
[`src/toe_reflective_closure.py`](../src/toe_reflective_closure.py) (czysta biblioteka
standardowa, arytmetyka dokładna, semantyka fail-closed)
**Audyt:** `PYTHONPATH=src python scripts/run_rc_toe_audit.py` →
[`results/rc_toe_audit.json`](../results/rc_toe_audit.json)

> **Wynik w jednym zdaniu.** Teorią Wszystkiego nie jest Lagranżjan ani lista praw,
> lecz **struktura domknięcia `(E, cl, σ, Ω)`, która jest domknięta substancjalnie,
> dynamicznie, logicznie, obserwacyjnie i decyzyjnie — a przy tym dokładnie zna własną
> resztę**: potrafi obliczyć, których faktów nie przewidzi.
> Definicja zastosowana do samej siebie **odmawia sobie certyfikatu** (§7), co jest
> testem, że ma zęby.

---

## §0. Metoda: cztery reguły wnioskowania

Zadanie brzmiało „podejdź do wnioskowania innowacyjnie i nietrywialnie". Zamiast
dokładać kolejny sektor symetrii, zastosowałem protokół, który *wymusza* nietrywialność.
Każda z czterech reguł jest sprawdzalna i każda została tu użyta przeciwko własnemu
pomysłowi.

| # | Reguła | Treść operacyjna | Gdzie została użyta |
|---|---|---|---|
| **R1** | **Definicja przez dyskwalifikację** | Definiuj przez to, co *wyklucza*, nie przez to, co obiecuje. Klauzula definicji bez choć jednego odrzuconego kandydata jest dekoracją. | §1 (pięć antywzorów), §4 (T3: substraty bez prawdopodobieństwa) |
| **R2** | **Wymuszanie wykonywalności** | Każda klauzula definicji musi mieć uruchamialny test, który może zwrócić `FAIL`. Jeśli nie da się jej policzyć, nie wchodzi do definicji. | §3 (bramy S/L/Q/O/D), `scripts/run_rc_toe_audit.py` |
| **R3** | **Samo-zastosowanie** | Definicja musi zostać przepuszczona przez własny audyt. Samo-certyfikacja bez spełnienia bram jest błędem programu, nie sukcesem. | §7.2: RC-ToE → `FRAMEWORK_NOT_TOE` |
| **R4** | **Ujawnianie reszty** | Każde twierdzenie publikuje własną resztę: co zostało odrzucone, czego nie policzono, ile było prób przed znalezieniem zbieżności. | §4 (T7), §6.5 (Ω), §8 (podatek od numerologii) |

Reguły R1 i R4 mają tu znaczenie praktyczne: **pierwsza miara „kwantowości", którą
zaproponowałem (gęstość zależnych trójek `δ₃`), została obalona przez własne obliczenie.**
`U_{3,4}` ma `δ₃ = 0` (żadna trójka nie jest zależna), a mimo to jego krata jest
niedystrybutywna — bo jego jedyny obwód ma cztery elementy. Poprawnym niezmiennikiem jest
**najniższy rząd więzu** (`lowest_constraint_order`), nie gęstość. Ten epizod jest
zachowany w kodzie jako komentarz i w teście jako kontrakt, bo definicja, która nie
pamięta własnych błędów, powtarza je.

---

## §1. Dlaczego dotychczasowe definicje ToE są trywialne

Nie chodzi o to, że są fałszywe — chodzi o to, że **nie są definicjami**: nie odróżniają
Teorii Wszystkiego od czegokolwiek innego. Każdy antywzór ma formalny tryb awarii.

| Antywzór | Formalny tryb awarii | Czego brakuje |
|---|---|---|
| **A1** „ToE = teoria unifikująca wszystkie oddziaływania" | Kryterium zasięgu, nie treści. Każda GUT spełnia je częściowo; żadna granica „wszystkich" nie jest określona (czy obejmuje obserwatora? proces odkrycia?). | Kryterium *domknięcia*: co musi być w środku |
| **A2** „ToE = Lagranżjan `M`, z którego wszystko wynika" | Regres: dlaczego `M`? Parametry `M` (masy, kąty, `Λ`) pozostają niewyjaśnione, więc `M` nie jest końcem wyjaśniania. | Warunek **zero parametrów wejściowych** (brama S) |
| **A3** „ToE = teoria bez parametrów swobodnych" | Puste: teoria `1 = 1` nie ma parametrów. Brak kryterium, skąd biorą się *liczby*. | Warunek, że stałe są **niezmiennikami** struktury + podatek od numerologii (§8) |
| **A4** „ToE = teoria wszystkiego, co mierzalne" | Wyklucza obserwatora, więc nie obejmuje procesu, w którym sama została wywnioskowana. ToE, która nie potrafi przewidzieć własnego odkrycia, jest niekompletna *własnym standardem*. | Warunek **punktu stałego inferencji** (brama O) |
| **A5** „ToE = teoria ostateczna/finalna" | Kryterium socjologiczne i niefalsyfikowalne; „ostateczność" nie jest własnością teorii. | Warunek **pre-rejestrowanych falsyfikatorów** z semantyką zabicia na poziomie twierdzeń (brama D) |

Wniosek R1: definicja ToE musi być **operatorem odrzucania**, nie obietnicą. Dlatego
poniższa definicja składa się z pięciu bram, z których każda jest obliczalna, i z
szóstego elementu — reszty — której teoria nie może ukryć.

---

## §2. Substrat: domknięcie zamiast metryki

### 2.1 Obiekty

Niech `E` będzie skończonym (na razie) zbiorem **faktów** — zdarzeń, o których można
orzekać. Jedyną strukturą pierwotną jest **operator domknięcia**

```
cl : P(E) → P(E),    A ⊆ cl(A),    A ⊆ B ⇒ cl(A) ⊆ cl(B),    cl(cl(A)) = cl(A)
```

plus aksjomat wymiany (Steinitza–Mac Lane'a), który czyni z `(E, cl)` **matroid** `M`.
Wszystko inne jest pochodne:

| Obiekt | Definicja | Znaczenie w RC-ToE |
|---|---|---|
| `r(A)` | rangа: moc największego niezależnego podzbioru `A` | liczba **niezależnych** faktów = wymiar skutecznej przestrzeni konfiguracyjnej |
| `C(A) = |A| − r(A)` | ładunek więzów (redundancja) | **oddziaływanie**: ile faktów w `A` jest związanych, a nie swobodnych |
| `L(M)` | krata zbiorów domkniętych (*płaskich*) | przed-geometryczna „przestrzeń": porządek bez metryki |
| `μ`, `χ_M(q)`, `T_M(x,y)` | funkcja Möbiusa, wielomian charakterystyczny, wielomian Tutte'a | **stałe**: kandydaci na niezmienniki, z których mają wynikać liczby Natury |
| `Aut(M)` | grupa permutacji `E` zachowująca `cl` | **symetria cechowania**: nie postulowana, tylko wyliczona |
| `fr(A) = {e : e ∉ cl(A)}` | frontiera | jedyne miejsce, w którym dynamika może rozgałęziać |
| `A_{t+1} = cl(A_t ⊔ {x_t})`, `x_t ∈ fr(A_t)` | **przepływ rangi** | jedyne prawo dynamiki: bez działania, bez metryki, bez sprzężeń |

Trzy konsekwencje, które odróżniają to od zwykłej „przed-geometrii":

1. **Czas jest wbudowany, nie emergentny termodynamicznie.** Rodzina stanów osiągalnych
   `A_0 ⊆ A_1 ⊆ …` jest *antymatroidem*: strzałka czasu to asymetria samego `cl`, a nie
   warunek brzegowy nałożony na odwracalne prawa.
2. **Grawitacja jest odpowiedzią entropową na wstawienie faktu**, dokładnie w sensie
   Jacobsona, ale bez metryki: `ΔC = C(A ∪ {e}) − C(A)` jest kosztem więzów, który
   wprowadza fakt `e` (`project_hypothesis`: przejście `ΔC → G_eff` nie jest wyprowadzone).
3. **Stałe są niezmiennikami, nie danymi.** Bramа S żąda, by każda bezwymiarowa liczba
   była wartością `T_M`, liczbą Whitneya, wartością Möbiusa, `|Aut(M)|` albo `β(M)`.

### 2.2 Słownik emergencji (z uczciwym statusem)

| Fizyka | Obiekt w substracie | Status |
|---|---|---|
| logika klasyczna / kwantowa | dystrybutywność `L(M)` | `theorem` (T1, §4) |
| prawdopodobieństwo | wartościowanie na `L(M)` | `theorem` (T3: nie zawsze istnieje) |
| reguła Borna | ortodopełnienie + `r ≥ 3` | `theorem` (T4: wymaga substratu nieskończonego) |
| granica klasyczna | refleksor dystrybutywny `L/θ_D` | `theorem` (T2) |
| wymiar | `r(M)` = długość maksymalnego łańcucha | `definition` |
| strzałka czasu | porządek osiągalności antymatroidu | `definition` |
| symetria cechowania | `Aut(M)` | `open_task` (Spin(10) nie wyprowadzone) |
| grawitacja | `ΔC` przy wstawieniu faktu | `project_hypothesis` |
| generacje fermionów | liczebność klas płaskich/obwodów | `open_task` (β(Fano)=3 odrzucone, §8) |
| `Λ` | wartościowanie `T_M` w punkcie stałym | `speculative` |

---

## §3. Definicja

### 3.1 Definicja RC-ToE

**Definicja (RC-ToE).** *Reflektywną Teorią Wszystkiego* nazywam czwórkę

```
𝒯 = (E, cl, σ, Ω)
```

gdzie `E` jest zbiorem faktów, `cl` operatorem domknięcia z aksjomatem wymiany,
`σ` znormalizowanym wartościowaniem na kracie `L(cl)` (uogólnione prawdopodobieństwo),
a `Ω` podstrukturą obserwatora wraz z jej operatorem inferencji — **spełniającą pięć
warunków domknięcia**:

**(S) Domknięcie substancjalne — zero pokręteł.**
Zbiór parametrów swobodnych `𝒯` jest pusty, a każda bezwymiarowa liczba obserwowalna jest
niezmiennikiem kombinatorycznym `(E, cl)`. Każde przypisanie „stała = niezmiennik" musi
przejść **budżet zbieżności** (§8) i podać mechanizm. Test wykonywalny:
`rc.coincidence_budget(...)`, `matroid.invariant_vector()`.

**(L) Domknięcie prawa — jeden operator.**
Wszystkie oddziaływania są *kanałami* jednego przepływu rangi `A_{t+1} = cl(A_t ⊔ {x_t})`.
Kanał, który trzeba dodać do przepływu jako osobny człon (osobne pole, osobna stała
sprzężenia), **obraca bramę L w `FAIL`**. Dozwolone statusy kanału: `derived`,
`implemented`, `hypothesis`, `open_task`, `postulated`, `rejected`; certyfikacja wymaga
`derived`/`implemented` dla cechowania, grawitacji, generacji i `Λ`.

**(Q) Domknięcie logiczne — zadeklarowany szczebel drabiny.**
Substrat musi mieć **obliczony** szczebel drabiny dopuszczalności (§4, T3–T5) i musi on
być równy zadeklarowanemu. Teoria kwantowa wymaga szczebla 3 z `r ≥ 3` (*Born-ready*).
Każdy substrat skończony, który potrafimy wyenumerować, jest odrzucany: to nie jest
ostrożność stylistyczna, tylko wynik (T4).

**(O) Domknięcie obserwatora — punkt stały własnej inferencji.**
Niech `Φ(p) = normalize((1−ε)·p·L·(Mᵀp) + ε·u)`, gdzie `L` jest wiarygodnością danych,
a `M[h][h′]` prawdopodobieństwem, że agent trzymający teorię `h` wywnioskuje `h′`.
`𝒯` musi być **atrakcyjnym punktem stałym** `Φ`: `KL(Φ(p*)‖p*) < tol` przy współczynniku
skurczu `< 1`. Interpretacja: teoria, która nie potrafi przewidzieć procesu własnego
odkrycia, nie jest teorią wszystkiego.

**(D) Domknięcie decyzyjne — pre-rejestrowane falsyfikatory + MDL.**
W chwili definicji `𝒯` publikuje skończoną listę falsyfikatorów
`(obserwowalna, przewidywanie, tolerancja, eksperyment, horyzont, semantyka zabicia)`,
w tym **co najmniej jeden zewnętrzny** (do wykonania bez tego repozytorium), oraz spełnia
nierówność długości opisu `|aksjomaty| < |dane wyjaśniane|`.

**(R) Reszta — warunek szósty, bez którego pięć pierwszych jest niemożliwych do spełnienia.**
`𝒯` publikuje certyfikowaną resztę `ρ* = residual(N, B)`: dolne ograniczenie masy faktów,
których aksjomaty o długości `≤ N` bitów i dowody o budżecie `≤ B` kroków **nie rozstrzygną**.
Reszta jest liczona, nie szacowana (§6.5).

### 3.2 Jedno zdanie

> **Teorią Wszystkiego jest struktura domknięcia, która zamyka wszystko z wyjątkiem
> reszty — i potrafi tę resztę dokładnie obliczyć.**

### 3.3 Dlaczego to jest nietrywialne

Trzy cechy odróżniają RC-ToE od A1–A5:

1. **Jest operatorem odrzucania.** Bramy S/L/Q/O/D odrzucają znakomitą większość
   kandydatów, w tym (jak się okaże) wszystkie policzalne substraty kwantowe (§4, T4)
   i obie teorie audytowane w §7.
2. **Nie zawiera stałych.** Nie „wyprowadza" `α`, `Λ` ani mas — definiuje, co znaczy
   wyprowadzić, i podaje test, którego żadna z nich na razie nie przechodzi.
3. **Jest reflektywnie niezupełna z wyboru.** Twierdzenie T7 pokazuje, że `S ∧ O` przy
   zerowej reszcie jest niemożliwe; RC-ToE zamienia tę niemożliwość w *obowiązek
   obliczeniowy*, a nie w wymówkę.

---

## §4. Twierdzenia, dowody i to, co obliczyłem

Wszystkie liczby poniżej są wynikiem wykonania
`PYTHONPATH=src python scripts/run_rc_toe_audit.py` i są zamrożone w testach
`tests/test_toe_closure_kernel.py` (30 kontraktów) oraz
`tests/test_toe_reflective_closure.py` (24 kontrakty).

### T1 — Klasyczność = brak więzów rzędu ≥ 3 · `theorem`

**Twierdzenie.** `L(M)` jest dystrybutywna wtedy i tylko wtedy, gdy każdy obwód `M` ma
moc `≤ 2` (pętle i klasy równoległe), tzn. gdy substrat nie niesie żadnego więzu rzędu
trzy lub wyższego.

**Dowód (szkic).** (⇐) Płaskie matroidu bez obwodów rzędu ≥3 to wszystkie podzbiory
elementów nierównoległych, więc `L(M)` jest kratą Boole'a. (⇒) Obwód `C` z `|C| ≥ 3`
daje po uproszczeniu trzy różne atomy pod wspólnym elementem rzędu 2 — diament `M3` jako
podkratę, a obecność `M3` lub `N5` wyklucza dystrybutywność (twierdzenie Birkhoffa).

**Weryfikacja wyczerpująca:** wszystkie matroidy na `≤ 4` faktach oznaczonych —
**89 substratów, 0 naruszeń**. Enumeracja (DFS po funkcjach rangi z obcinaniem przez
R0–R3, niezależna kontrola `validate_rank_axioms`) daje liczby zgodne z ręcznym
zliczaniem: `n=1: 2`, `n=2: 5`, `n=3: 16`, `n=4: 68`.

**Treść fizyczna.** Logika kwantowa nie jest wyborem formalizmu — jest **twierdzeniem o
gęstości więzów**. Jakikolwiek więż rzędu ≥3 między faktami wymusza niedystrybutywność.
Odwrotnie: substrat bez takich więzów jest *bezprawny* (`C(A) = 0` dla wszystkich `A`,
więc `cl = id` i przepływ rangi nie ma czego wymuszać). To jest najmocniejsza forma
tego wyniku: **nie ma prawa bez logiki nieklasycznej.**

### T2 — Granica klasyczna jest kanoniczna, nie jest `ħ → 0` · `theorem`

**Twierdzenie.** Dla każdej kraty `L` istnieje kanoniczny refleksor na kategorię krat
dystrybutywnych: iloraz `L/θ_D` przez kongruencję generowaną przez wszystkie naruszenia
dystrybutywności. Granica klasyczna substratu jest *wyznaczona jednoznacznie*, a jej
miara — `κ(L) = log|L| / log|L/θ_D|` — jest obliczalna.

**Obliczone:** `M3 → 2 bloki` (klasyczny cień diamentu to **jeden bit**),
`U_{2,4} → 2`, `Fano → 2` (z 16 elementów), `B_n → 2^n` (κ = 1, nic do klasykalizacji).
Dla substratów już klasycznych iloraz jest identycznością — co jest testem, że
konstrukcja nie „psuje" klasyki.

### T3 — Nie każdy substrat dopuszcza prawdopodobieństwo · `theorem`

**Twierdzenie.** Układ równań wartościowania
`σ(a∨b) + σ(a∧b) = σ(a) + σ(b)`, `σ(0̂) = 0`, `σ(1̂) = 1`, `0 ≤ σ ≤ 1`
może być **sprzeczny**. Wtedy substrat nie ma żadnej miary prawdopodobieństwa —
odpada z definicji bez udziału eksperymentu.

**Obliczone dokładnie (arytmetyka wymierna, enumeracja wierzchołków):**

| substrat | `|L|` | dystryb. | modularna | wartościowanie | liczba stanów | ortodopełnienie | szczebel |
|---|---|---|---|---|---|---|---|
| `F₄` (Boole'a) | 16 | tak | tak | tak | 4 (dim 3) | tak | **0** klasyczny/bezprawny |
| `U_{2,3}` = `M3` = PG(1,2) | 5 | nie | tak | tak | **1**: `(½,½,½)` | nie | **2** |
| `U_{2,4}` = `M4` = PG(1,3) | 6 | nie | tak | tak | **1**: `(½,½,½,½)` | **tak** | **3** |
| `U_{3,4}` | 12 | nie | **nie** | **BRAK** | 0 | nie | **1** niedopuszczalny |
| `U_{4,5}` = kod Spin(10) | 27 | nie | **nie** | **BRAK** | 0 | nie | **1** niedopuszczalny |
| `Fano` = PG(2,2) | 16 | nie | tak | tak | **1**: `⅓` punkty, `⅔` proste | nie | **2** |

**Mechanizm odrzucenia `U_{3,4}`** (warto go zobaczyć, bo jest elementarny): z
`σ(aᵢ)+σ(aⱼ)+σ(aₖ) = 1` dla każdej trójki punktów dostajemy `σ(point) = ⅓`, więc
`σ(pary) = ⅔`; ale dwie *rozłączne* pary mają join = `1̂` i meet = `0̂`, więc musi być
`σ + σ = 1`, czyli `4/3 = 1`. Sprzeczność.

**Spis substratów na 4 faktach (68 sztuk):** szczebel 0 — 52, szczebel 1 — 1,
szczebel 2 — 14, szczebel 3 — 1, **Born-ready — 0**.

### T4 — Reguła Borna wymaga substratu nieskończonego · `theorem` + `open_task`

**Twierdzenie (obliczone + klasyczne).**
(a) Wyczerpująco: żaden substrat na `≤ 4` faktach nie jest *Born-ready*
(ortodopełnienie ∧ `r ≥ 3` ∧ niedystrybutywność). Jedyny ortodopełnialny substrat
nieklasyczny to `U_{2,4} = PG(1,3)` — dokładnie wymiar 2, w którym twierdzenia typu
Gleasona **nie zachodzą**.
(b) Klasycznie: każda polarność skończonej płaszczyzny rzutowej ma punkty absolutne
(`p ≤ p^⊥`), a punkt absolutny łamie `x ∧ x^⊥ = 0̂`; zatem żadna skończona płaszczyzna
rzutowa nie jest ortodopełnialna.
(c) Jądro potwierdza (b) wyczerpującym przeszukiwaniem dla PG(2,2): **brak**
ortodopełnienia (16 elementów, pełny backtracking).

**Konsekwencja, która jest treścią bramy Q.** Jeśli teoria ma mieć regułę Borna, jej
substrat musi być nieskończony; wtedy z twierdzenia Solèra ortomodularna krata z
nieskończonym ciągiem ortonormalnym jest kratą podprzestrzeni przestrzeni Hilberta nad
ciałem z inwolucją — więc **ℝ, ℂ lub ℍ są wyprowadzone, a nie wybrane**. Które z nich —
pozostaje `open_task` (Solèr nie rozstrzyga).

### T5 — Najmniejszy dopuszczalny substrat nieklasyczny to płaszczyzna Fano · `theorem`

**Obliczone dokładnie:** 7 faktów, ranga 3, **14 obwodów** (7 prostych o 3 punktach i 7
„płaszczyzn afinicznych" o 4 punktach), 16 płaskich, `χ(q) = q³ − 7q² + 14q − 8`,
`β = 3`, 28 baz, `δ₃ = 1/5`, `Aut = 168 = GL(3,2) = PSL(2,7)`, modularna,
niedystrybutywna, **dokładnie jeden stan**: `σ(punkt) = 1/3`, `σ(prosta) = 2/3`,
**brak ortodopełnienia**, klasyczny cień = 1 bit.

Dwa wnioski, oba nietrywialne:

* **Unikalność stanu.** Najmniejszy substrat, który w ogóle dopuszcza prawdopodobieństwo,
  dopuszcza je w **dokładnie jeden** sposób. Przestrzeń stanów nie jest tu bogata — jest
  sztywna. Sztywność to zasób: to ona jest kandydatem na źródło stałych (brama S), a nie
  „dostrojenie".
* **Nieprzemienność wchodzi przez oktoniony.** Diagram incydencji Fano to diagram
  mnożenia oktonionów (`project_hypothesis`: związek z wyjątkowymi algebrami Jordana i
  `E₈` jest tu wskazówką kierunku, nie wynikiem).

### T6 — Refleksyjność wygrywa z wiarygodnością · `theorem` (dla opublikowanego jądra)

**Obliczone** dla jądra inferencji `M = [[.10,.80,.10],[.05,.90,.05],[.20,.50,.30]]`,
wiarygodności `L = (.70,.20,.10)`, `ε = 0.02`:

```
punkt stały   = (0.008328, 0.984807, 0.006865)
wybór ML      = A (L = 0.70)      wybór reflektywny = B (L = 0.20)
nadpisanie TV = 0.785             iteracji = 13   KL = 2.4e-14   skurcz = 0.041
```

**Treść.** Punkt stały operatora reflektywnego **nie musi** być teorią
największej wiarygodności: tu różni się od niej o `0.785` w odległości wariacji całkowitej.
To jest *nowe kryterium selekcji*, którego nie ma ani w programie unifikacji, ani w
antropicznym wieloświecie: teoria, której nie reprodukuje proces jej własnego
wnioskowania, odpada niezależnie od dopasowania do danych. Dla jądra identycznego
(agent samo-potwierdzający) punkt stały wraca do wyboru ML — test, że brama O nie jest
pusta w trywialnym przypadku.

### T7 — No-go: domknięcie zupełne jest niemożliwe · `theorem` (warunkowo)

**Twierdzenie (szkic lebowy).** Niech `𝒯` będzie skończenie aksjomatyzowalna, spójna i
zawiera arytmetykę. Jeśli `𝒯` spełnia (O) z zerową resztą, to przewiduje z
prawdopodobieństwem 1, że zostanie wywnioskowana — a więc dowodzi własnej spójności, co
jest wykluczone przez drugie twierdzenie Gödla. Zatem `S ∧ O` z `ρ* = 0` jest niemożliwe.

**Konsekwencja definicyjna.** RC-ToE nie żąda zupełności. Żąda **dokładnej znajomości
reszty**: `ρ*` ma być policzone i opublikowane razem z teorią (brama R). To jest
przesunięcie, które uważam za właściwy rdzeń całej definicji: *teoria wszystkiego nie jest
domknięciem wszystkiego — jest domknięciem, które zna swoją granicę.*

---

## §5. Spin(10) jako struktura domknięcia (most do filaru repozytorium)

Repozytorium buduje na Spin(10) i 16-wymiarowym spinorze. W słowniku RC-ToE ten obiekt
ma **dokładną, obliczalną** postać — i daje wynik negatywny.

### 5.1 Tożsamości (wszystkie wykonane w jądrze)

| Tożsamość | Wartość obliczona | Status |
|---|---|---|
| Wagi spinora `16` z `Spin(10)` | połowa parzystościowa 5-kostki: `(±½)^5` z parzystą liczbą minusów → **16** | `theorem` |
| Grupa Weyla `W(D₅)` | parzystość-zachowujące permutacje z znakami 5 slotów → **1920 = 2⁴·5!** (pełna grupa hiperoktaedralna: 3840) | `theorem` |
| Działanie `W(D₅)` na 16 wagach | **przechodnie** (sprawdzone enumeracyjnie) | `theorem` |
| Struktura więzów spinora | kod binarny `[5,4]` parzystości → matroid `U_{4,5}`: **jeden obwód, cała piątka faktów** | `theorem` |
| Dualny matroid | `U_{1,5}`: jeden globalny ładunek `ℤ₂` wspólny dla 5 slotów = **parzystość fermionowa** | `theorem` |
| `χ(q)` dla `U_{4,5}` | `q⁴ − 5q³ + 10q² − 10q + 4`, `β = 1`, 27 płaskich, 5 baz, `Aut = 120` | `theorem` |

**Odczyt.** Symetria nie jest tu postulowana: `W(D₅)` **jest** grupą automorfizmów
struktury domknięcia na 5 binarnych slotach faktów z więzem parzystości. To dokładnie
teza RC-ToE („symetria = `Aut(cl)`") w jedynym przypadku, w którym udało mi się ją
wykonać bez reszty.

### 5.2 Wynik negatywny (najważniejszy w tej sekcji)

`U_{4,5}` jest **szczebla 1**: jego krata płaskich **nie dopuszcza żadnego
wartościowania** (T3). Znaczy to:

> System wag spinora `16` — czytany jako struktura domknięcia — **nie może nieść
> prawdopodobieństwa**. Spin(10) jest *etykietą* na faktach, nie substratem.

Nie jest to zarzut wobec Spin(10) jako grupy cechowania; jest to precyzyjne wskazanie,
czego brakuje, żeby filar repozytorium stał się substratem ToE: musi zostać **zanurzony**
w strukturze ortodopełnialnej rangi ≥ 3, czyli — przez T4 — w strukturze nieskończonej.
Kandydatem naturalnym jest kierunek oktonionowy/wyjątkowy (Fano → `h₃(𝕆)` → `E₆/E₈`),
tu oznaczony `speculative` i **nie** wyprowadzony.

### 5.3 Czego nie zrobiłem

Nie wyprowadziłem `Spin(10)` jako `Aut` żadnego wyenumerowanego substratu. `W(D₅)`
zgadza się co do rzędu i działania, ale to **nie** jest wyprowadzenie grupy Liego z
matroidu. Bramа L ma z tego powodu status `open_task`, a wyszukiwanie jest
pre-rejestrowane (§8, falsyfikator F5).

---

## §6. Wyniki

Sekcja liczb zamrożonych w `results/rc_toe_audit.json`.

### 6.1 T1 i enumeracja

```
n=1:   2 matroidy     n=2:   5     n=3:  16 (15 klasycznych, 1 nieklasyczny)
n=4:  68 matroidów    (52 klasycznych, 16 nieklasycznych)
T1:   89 substratów sprawdzonych (n=2,3,4), 0 naruszeń          → PASS
```

### 6.2 Spis substratów na 4 faktach

```
szczebel 0  klasyczny/bezprawny                     : 52
szczebel 1  więzy bez prawdopodobieństwa            :  1   (U_{3,4})
szczebel 2  uogólnione prawdopodobieństwo bez Borna : 14
szczebel 3  ortodopełnialny                         :  1   (U_{2,4} = PG(1,3))
Born-ready (szczebel 3 ∧ r ≥ 3)                     :  0
```

### 6.3 Karta substratu Fano (PG(2,2))

```
fakty 7 · ranga 3 · obwody 14 (7×3 + 7×4) · płaskie 16 · δ₃ 1/5
χ(q) = q³ − 7q² + 14q − 8 · β = 3 · bazy 28 · |Aut| = 168 = GL(3,2)
stan: JEDEN, σ(punkt) = 1/3, σ(prosta) = 2/3 · ortodopełnienie: BRAK
klasyczny cień L/θ_D: 2 bloki (1 bit) · szczebel: 2
```

### 6.4 Karta substratu Spin(10)

```
wagi: 16 (parzysta połowa 5-kostki) · |W(D₅)| = 1920 = 2⁴·5! · działanie przechodnie
kod [5,4] → U_{4,5}: obwód 1 (cała piątka) · χ = q⁴−5q³+10q²−10q+4 · β = 1
płaskie 27 · bazy 5 · |Aut| = 120 · wartościowanie: BRAK · szczebel: 1
```

### 6.5 Certyfikowana reszta (dolne ograniczenia Ω na zabawce-prefixowej)

Maszyna: `U(1^k 0 body)`, instrukcje 2-bitowe `INC/JZ/HALT/DEC`, kod prefiksowy.

| `N` | programów | halting | nierozstrzygnięte | `ω(N,B)` | `residual(N,B)` |
|---|---|---|---|---|---|
| 3 | 3 | 3 | 0 | `3/4` = 0.750000 | `0` |
| 5 | 7 | 6 | 1 | `27/32` = 0.843750 | `1/32` = 0.031250 |
| 7 | 15 | 12 | 3 | `57/64` = 0.890625 | `3/64` = 0.046875 |
| 9 | 31 | 23 | 8 | `467/512` = 0.912109 | `29/512` = 0.056641 |

`ω + residual = total_mass` jest sprawdzane w kodzie (asercja księgowości masy); przy
`B → ∞` `ω` rośnie, `residual` maleje. **To nie jest Ω Chaitina** — to dokładne dolne
ograniczenie dla konkretnej maszyny, w dokładnie tym samym statusie epistemicznym, w
jakim publikuje się literaturowe oszacowania Ω.

### 6.6 Refleksyjny punkt stały

```
jądro M = [[.10,.80,.10],[.05,.90,.05],[.20,.50,.30]] · L = (.70,.20,.10) · ε = 0.02
punkt stały (0.008328, 0.984807, 0.006865) · ML = A · wybór reflektywny = B
nadpisanie TV = 0.784807 · iteracji 13 · KL 2.44e-14 · skurcz 0.0410 → atrakcyjny
jądro identycznościowe → wybór ML (test nietrywialności bramy O)
```

### 6.7 MDL (proxy `zlib`, bity)

```
GUH-S10: aksjomaty (§2 hipotezy) = 5376 bitów · dane (§9 + tabela 19 obserwabili) = 4768
         → |aksjomaty| > |dane|  ⇒ nierówność MDL NIESPEŁNIONA
RC-ToE : aksjomaty (§3) = 17160 bitów · dane (§6) = 17352 bitów
         → nierówność spełniona z marginesem 1.1%, czyli *ledwo*; przy proxy tej jakości
           taki margines nie jest wynikiem, tylko ostrzeżeniem, że aksjomatyka definicji
           jest niemal tak długa jak zbiór faktów, który porządkuje
```

Zastrzeżenie R4: `zlib` jest proxy, nie złożonością Kołmogorowa; nierówność w tę stronę
jest sygnałem ostrzegawczym, nie wyrokiem. Pełna tabela 38 predykcji powiększyłaby stronę
„dane" — i to jest dokładnie powód, dla którego brama D żąda *pre-rejestrowanego*,
zamrożonego zbioru danych, a nie sekcji dokumentu.

### 6.8 Wymiar spektralny — odmowa

Jądro **odmawia** publikacji wymiaru spektralnego dla wszystkich policzalnych substratów
(straż skończonego rozmiaru: błądzenie zdążyło się wymieszać, `plateau = 1/|L|`).
W konsekwencji ansatz repozytorium `d_S(N) = 4(1 − e^{−N/150})`
(`src/spin10_engine.py:390`, komentarz „formula z remedium") **nie jest odtwarzalny**
przez dyfuzję na diagramie Hassego żadnego substratu, który potrafimy wyenumerować.
Zamiast liczby publikowana jest odmowa — to jest zachowanie zgodne z
`tests/test_spectral_dimension_integrity.py`.

---

## §7. Audyt dwóch kandydatów

Wykonanie: `PYTHONPATH=src python scripts/run_rc_toe_audit.py`.
Werdykty: `CERTIFIED_AS_TOE` (tylko gdy wszystkie bramy `PASS`), `FRAMEWORK_NOT_TOE`,
`REFUSED_MISSING_COMPUTATION`.

### 7.1 GUH-S10 / Spin(10)-ToE v14.5 → `REFUSED_MISSING_COMPUTATION`

| Brama | Werdykt | Dowód |
|---|---|---|
| **S** | **FAIL** | 6 parametrów dopasowanych. Najostrzejszy: `alpha_em_0_inv_corrected = alpha_em_0_inv - 6.5504` z komentarzem *„Dokładna kalibracja do 1/137.036"* (`src/physics_apex_v13_core.py:145`, także `src/grand_unified_toe_core.py:551`) — przeczy deklaracji README *„α_em = 1/137.036 … zero experimental input"*. Dalej: `c_H = 0.33` (`src/spin10_engine.py:703`), skala `150` w `d_S` (`:390`), `Var(k) → 32.67`, `g* = 0.83`, `N_hidden = 125`. |
| **L** | **FAIL** | cechowanie `postulated`, grawitacja `hypothesis`, generacje `hypothesis`, `Λ` `rejected` (holograficzne `Λ` jest tylko „odwrotnością pola", co wykrywa `tests/test_ift_egr_closure.py`) |
| **Q** | **REFUSED** | repozytorium implementuje graf relacyjny z próbkowaniem Metropolis–Hastings, **nie operator domknięcia**; nie ma czego policzyć, więc brama odmawia zamiast zgadywać |
| **O** | **FAIL** | brak modelu obserwatora i operatora inferencji |
| **D** | **FAIL** | falsyfikatory zewnętrzne istnieją, ale nie są pre-rejestrowane: `m_g̃` ma dwie różne zamrożone wartości (`10.6 TeV` w `docs/KLUCZOWE-REMEDIA.md` i `docs/spin10_toe_hypothesis.md` vs `12.39 TeV` w `docs/PREDYKCJE-i-FALSYFIKACJA-2026-2040.md`), `η_B` dwie (`6.2e-10` vs `6.11e-10`), tolerancje i semantyka zabicia nie są podane; dodatkowo MDL niespełnione (§6.7) |

**Werdykt:** *framework z programem na ToE, nie ToE.* Żadna z pięciu bram nie przechodzi.
To nie jest krytyka wartości inżynieryjnej repozytorium — jest to precyzyjna lista tego,
co dzieli je od definicji.

### 7.2 RC-ToE (ta definicja) → `FRAMEWORK_NOT_TOE`, `certified = false`

| Brama | Werdykt | Powód |
|---|---|---|
| **S** | **FAIL** | zero parametrów dopasowanych ✓, ale **zero przypisań stała↔niezmiennik**: definicja nie wyprowadziła żadnej liczby Natury |
| **L** | **CONDITIONAL** | wszystkie cztery kanały nazwane, wszystkie `open_task` |
| **Q** | **CONDITIONAL** | substrat wzorcowy (Fano) ma szczebel 2 = zadeklarowany ✓, ale nie jest Born-ready: brak ortodopełnienia ⇒ brak reguły Borna |
| **O** | **PASS** | punkt stały atrakcyjny, skurcz 0.041, KL 2.4e-14 (§6.6) |
| **D** | **CONDITIONAL** | 5 falsyfikatorów kompletnych, ale **0 zewnętrznych** (wszystkie rozstrzyga to repozytorium); MDL spełnione z marginesem 1.1% (§6.7) |

**Werdykt:** definicja **odmawia certyfikacji samej sobie**. Skrypt traktuje
samo-certyfikację jako błąd (`return 1`), więc regresja jest pilnowana w CI.

### 7.3 Najkrótsza droga do certyfikatu (w kolejności kosztu)

1. **Brama Q:** skonstruować substrat nieskończony z ortodopełnieniem (krata podprzestrzeni
   przestrzeni z formą) i pokazać, że `Spin(10)`-spinor zanurza się w nim z zachowaniem
   `W(D₅)` jako podgrupy `Aut`. To jedyna droga przez T4.
2. **Brama D:** zamrozić jeden falsyfikator zewnętrzny (niezależna enumeracja `Aut` do 6
   faktów przez stronę trzecią albo obserwacja, która rozstrzyga kanał grawitacyjny).
3. **Brama L:** wyprowadzić `ΔC → G_eff` jako równanie stanu (program Jacobsona w
   wersji kombinatorycznej) — albo skasować kanał grawitacyjny.
4. **Brama S:** jedno przypisanie stała↔niezmiennik, które przejdzie budżet zbieżności
   (§8) z mechanizmem. Jedno, nie dwadzieścia.

---

## §8. Falsyfikatory pre-rejestrowane i podatek od numerologii

### 8.1 Falsyfikatory RC-ToE (zamrożone 2026-09-19)

| # | Obserwowalna | Przewidywanie | Semantyka zabicia | Zewnętrzny? |
|---|---|---|---|---|
| F1 | T1 na `≤ 4` faktach | 0 naruszeń na 89 substratach (n=2,3,4) | jeden kontrprzykład zabija drabinę i degraduje RC-ToE do frameworka | nie (enumeracja) |
| F2 | skończony substrat Born-ready | nie istnieje na `≤ 4` faktach; dla skończonych płaszczyzn rzutowych w ogóle | wystawienie jednego zabija tezę, że substrat musi być nieskończony (zawias bramy Q) | nie teraz; tak po niezależnej enumeracji do 6 faktów |
| F3 | wartościowanie na `L(U_{4,5})` | nie istnieje | istnienie unieważnia wynik negatywny o Spin(10) jako samodzielnym substracie | tak (dowód niezależny) |
| F4 | reflektywne nadpisanie ML | istnieje jądro, dla którego punkt stały ≠ argmax `L`, skurcz < 1 | jeśli punkt stały zawsze = ML, brama O jest pusta i zostaje skreślona | nie (obliczenie) |
| F5 | `Spin(10) ≅ Aut(substratu)` | **NIEPRZEWIDYWANE**; przestrzeń wyszukiwania zamrożona: wszystkie matroidy `≤ 6` faktów + wszystkie reprezentowalne nad GF(2) `≤ 7` faktów | pusty wynik obala kanał cechowania bramy L dla tej klasy i wymusza jej powiększenie albo porzucenie | tak (horyzont 2027) |

### 8.2 Podatek od zbieżności (numeration tax)

Szukanie `K` niezmienników po `N` kandydatach i akceptowanie trafienia w tolerancji
względnej `τ` daje szansową częstość pozornego „wyprowadzenia"

```
p_chance = 1 − (1 − 2τ)^(K·N)
```

Przypisanie jest dopuszczalne tylko gdy `p_chance < α` **i** podano mechanizm.

**Demonstracja na własnej pokusie.** `β(Fano) = 3`, a repozytorium potrzebuje
`N_gen = 3`. Przy `K = 20` niezmienników i `N = 89` substratach z samego spisu,
`τ = 0.05`: `p_chance = 1 − 0.9^1780 > 0.99` ⇒ `rejected_numerology`. Bez mechanizmu
⇒ `rejected_no_mechanism`. **Zbieżność odrzucona przez autora w tej samej sekcji, w
której została zauważona.** To jest reguła R4 w działaniu i jedyny sposób, w jaki ten
dokument różni się od numerologii.

---

## §9. Czego ta definicja NIE twierdzi

1. Nie wyprowadza żadnej stałej Natury: ani `α`, ani `Λ`, ani mas, ani `N_gen`.
2. Nie twierdzi, że Wszechświat jest matroidem. Twierdzi, że **jeśli** jest strukturą
   domknięcia, to T1–T5 obowiązują, a wtedy większość policzalnych kandydatów odpada.
3. Nie unifikuje oddziaływań. Definiuje, co musiałoby być prawdą, żeby unifikacja była
   Teorią Wszystkiego.
4. Nie zastępuje Spin(10), LQG, asymptotycznego bezpieczeństwa ani IFT-EGR. Dostarcza
   kryterium, po którym poznaje się, czy którakolwiek z tych dróg jest zamknięta.
5. Nie twierdzi, że Ω z §6.5 jest Ω Chaitina, a `zlib` z §6.7 złożonością Kołmogorowa.

---

## §10. Uruchomienie

```bash
# jądro + bramy (bez numpy, bez JAX, bez sieci)
PYTHONPATH=src python -m unittest -v tests.test_toe_closure_kernel      # 30 kontraktów, < 1 s
PYTHONPATH=src python -m unittest -v tests.test_toe_reflective_closure  # 24 kontrakty, ~100 s

# pełny audyt: T1, spis, tożsamości Spin(10), Fano, Ω, inferencja, 2 audyty
PYTHONPATH=src python scripts/run_rc_toe_audit.py --output results/rc_toe_audit.json
```

Skrypt zwraca kod `1`, gdy: T1 ma kontrprzykład, spis znalazł substrat Born-ready,
`|W(D₅)| ≠ 1920`, liczba wag ≠ 16, **albo gdy RC-ToE certyfikowało się samo**.

---

## §11. Odniesienia

Logika kwantowa i kraty: Birkhoff & von Neumann (1936); Birkhoff, *Lattice Theory*
(dystrybutywność ⇔ brak `N5`/`M3`); Oxley, *Matroid Theory* (aksjomaty wymiany, funkcja
rangi, wielomian charakterystyczny); Crapo (niezmiennik `β`); Tutte.
Stany i reguła Borna: Gleason (1957); Solèr (1995) — krata ortomodularna z
nieskończonym ciągiem ortonormalnym jest kratą podprzestrzeni przestrzeni Hilberta nad
ciałem z inwolucją; Baer — polarności skończonych płaszczyzn rzutowych mają punkty
absolutne.
Grupa Weyla `D₅` i wagi spinora: standardowe tablice wag `Spin(2n)`
(wagi `(±½,…,±½)` z parzystą liczbą minusów).
Grawitacja entropiczna: Jacobson (1995), `arXiv:gr-qc/9504004`.
Niezupełność: Gödel II; Löb; Chaitin, *Omega lower bounds* (status §6.5).
Długość opisu: Rissanen (MDL); Kolmogorow (proxy §6.7).
Kontekst repozytorium: `docs/IFT_EGR_INDEPENDENT_AUDIT.md`,
`docs/TCD_ASSUMPTION_LEDGER.json`, `tests/test_spectral_dimension_integrity.py` —
dyscyplina fail-closed i rejestrów założeń została przejęta stamtąd.

---

*Mirrors:* angielska wersja skrócona — [`docs/toe-reflective-closure-definition.md`](toe-reflective-closure-definition.md);
rejestr założeń — [`docs/RC_TOE_ASSUMPTIONS.json`](RC_TOE_ASSUMPTIONS.json).
