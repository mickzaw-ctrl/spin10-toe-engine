# Pre-rejestracja: Test Tomografii Lokalnej Struktury
**Data utworzenia:** 2026-09-17 (UTC) — przed spojrzeniem na dane SN i przed porównaniem predykcji z rezyduami.
**Branch:** arena/01a0b0bd-spin10-toe-engine
**Cel:** Zapisanie z góry statystyki testowej, progu istotności i kryterium sukcesu/porażki zgodnie z punktem 0.1 zadania.

---

## 0. Ramy epistemiczne (twarde ograniczenia)

- To jest test spójności hipotezy przy pomocy istniejących publicznych danych, NIE poszukiwanie nowej fizyki.
- Dozwolone sformułowania: "spójne z", "niespójne z", "w granicach niepewności", "wymaga dalszej weryfikacji".
- Niedozwolone: "dowód", "odkrycie", "obalenie ciemnej energii", "nowa fizyka".
- Scope limit: nawet przy pozytywnym wyniku efekt ~70-100 Mpc może wyjaśnić co najwyżej niewielką poprawkę do napięcia H0 i ewentualny wkład w pozorną ewolucję w(z) — NIE zastąpienie ciemnej energii. Każde podsumowanie musi to zaznaczyć.
- Wymagany human review przed publikacją.

## 1. Hipoteza testowana

H1_spójność: Realne, niezależnie zmierzone lokalne pole prędkości (2MRS/2M++/CF4, Carrick et al. 2015, Lilow & Nusser 2021, Lilow et al. 2024) w promieniu ~70-100 Mpc przewiduje — bez dopasowywania do SN — dipol w rezyduach Hubble'a zgodny kierunkiem i amplitudą z tym, co mierzy się w Pantheon+/DES-SN5YR.

H0_null: Kierunek dipolu przewidzianego z pola prędkości jest losowy względem kierunku dipolu obserwowanego w SN (cosθ uniform w [-1,1]), lub amplituda jest niezgodna >3σ, lub obserwowany dipol jest generowany przez geometrię nieba / szum.

## 2. Dane użyte (przed pobraniem)

- Pantheon+SH0ES DataRelease: https://github.com/PantheonPlusSH0ES/DataRelease (plik Pantheon+SH0ES.dat, kowariancja)
- DES-SN5YR: https://github.com/des-science/DES-SN5YR + Zenodo 12720778
- Rekonstrukcje:
  - Carrick et al. 2015 (C15) 2M++: https://cosmicflows.iap.fr + EDD
  - Lilow & Nusser 2021 CORAS: https://github.com/rlilow/CORAS (grid 200 h^-1 Mpc)
  - Lilow et al. 2024 2MRS-NeuralNet: https://github.com/rlilow/2MRS-NeuralNet
  - Courtois et al. 2023 CF4 HMC (opcjonalnie)
- CosmicFlows-4: EDD https://edd.ifa.hawaii.edu (All CF4 Individual Distances, Groups)
- Mocki: własne gaussowskie pola losowe P(k) jako substytut N-body, jeśli brak Quijote.

## 3. Pipeline (kolejność z zadania)

Krok A: Ingest + sanity-check, weryfikacja v_LG ≈ 627 km/s (Kogut 1993) w kierunku (l,b)=(276±3,30±3) deg.
Krok B: δ_m = δ_g / b, b z niezależnej kalibracji (nie z SN). v(k) = i f H a k/|k|^2 δ_m(k), f≈Ω_m^0.55.
Krok C: Dla każdej SN interpolacja v_src wzdłuż LOS do jej z, δ(z,n) ≈ [1 - (1+z)^2/(H d_L)] (v_src·n - v_LG·n)/c, Δm = -(5/ln10) δ.
Krok D: Mapa Δm HEALPix, rozkład na harmoniki, dipol ℓ=1: kierunek + amplituda z niepewnością (propagacja z CRs).
Krok E: Niezależne dopasowanie do rezyduów Δμ_i = μ_obs - μ_ΛCDM, postać q0 = qm + qd·n·exp(-z/S) (Colin et al. 2019) z pełną kowariancją Pantheon+.
Krok F: Porównanie.
Krok G: Testy null i systematyki.
Krok H: Wrażliwość (Wiener vs NN, R~70 vs 300 Mpc).
Krok I: Raport.

## 4. Statystyka testowa (pre-registration)

### 4.1 Definicje

- **n_pred**: jednostkowy wektor kierunku dipolu przewidzianego z pola prędkości (Krok D), w Galactic lub Equatorial (konwersja jawna, astropy).
- **n_obs**: jednostkowy wektor kierunku dipolu dopasowanego do rezyduów SN (Krok E).
- **cosθ = n_pred · n_obs**, θ ∈ [0,π].
- **A_pred**: amplituda dipolu przewidzianego (mag), średnia po HEALPix w z-bin 0.01<z<0.1 (główny), lub amplitude parametru q_d (Colin formalism) przeliczona na Δm.
- **A_obs**: amplituda dipolu obserwowanego z fit SN, z niepewnością σ_obs (z posterior MCMC).
- **σ_pred**: niepewność A_pred z rozrzutu constrained realizations (CRs) pola prędkości (np. 50 realizacji CORAS).

### 4.2 Główna statystyka kierunkowa

- **T_dir = cosθ**.
- Rozkład null: przy izotropii kierunków, cosθ ~ Uniform(-1,1). PDF = 0.5. CDF.
- p_dir = P(C ≥ T_dir | H0) = (1 - T_dir)/2 dla testu jednostronnego (szukamy zgodności, cosθ→1).
- Dla uwzględnienia geometrii nieba: empiryczny rozkład null z mocków (Krok G) — randomizacja RA/Dec SN lub izotropowe mocki pola prędkości, 1000 realizacji, budujemy rozkład cosθ_null_sky.

### 4.3 Główna statystyka amplitudowa

- **T_amp = |A_pred - A_obs| / sqrt(σ_pred^2 + σ_obs^2 + σ_sys^2)**, gdzie σ_sys z niepewności b, f, H0.
- Spójność amplitudowa jeśli T_amp < 2 (w granicach 2σ). Niespójność jeśli T_amp > 3.

### 4.4 Łączne kryterium

Definiujemy dwie metryki, obie muszą być spełnione dla "spójności":

- Kierunek: cosθ ≥ 0.5 (θ ≤ 60°) ORAZ p_dir_empiryczny < 0.05 po korekcji na geometrię nieba (tj. obserwowany cosθ jest w górnym 5% rozkładu null z mocków sky-coverage).
- Amplituda: T_amp < 2.0 (zgodność w 2σ).

### 4.5 Progi istotności

- **Próg istotności kierunkowej:** α_dir = 0.05 (jednostronny). Wymagamy p_dir < 0.05 lub empiryczny p z mocków <0.05.
- **Próg amplitudowy:** 2σ (95% CL) dla spójności, 3σ dla niespójności.
- **Korekcja Look-Elsewhere:** Testujemy dwie skale R=70 Mpc (główna) i R=300 Mpc (test odporności). Używamy Bonferroni: α_eff = α/2 =0.025 dla każdej skali w ocenie końcowej, ale raportujemy obie.
- **Korekcja metod rekonstrukcji:** Testujemy min. 2 metody (C15 i L24). Wymagamy zgodności między nimi: |cosθ_C15 - cosθ_L24| < 0.3 lub obie w tym samym kwadrancie nieba, inaczej wynik "wymaga dalszej weryfikacji".

### 4.6 Kryterium sukcesu / porażki (niezmienialne po fakcie)

**Sukces (spójność):**
- cosθ ≥ 0.5 oraz p_dir_empiryczny <0.05 (po uwzględnieniu geometrii nieba),
- T_amp <2.0,
- Wynik powtarzalny między C15 i L24 (różnica kierunków <60° i amplitud w 2σ),
- Test null G pokazuje że sky-coverage generuje fałszywy dipol o amplitudzie <0.5 * A_obs (tj. nie dominuje),
- Sanity-check v_LG = 620±100 km/s odtworzony z pola (Krok A).

**Porażka (niespójność):**
- cosθ <0 (kierunki przeciwne) lub p_dir_empiryczny >0.2,
- lub T_amp >3.0,
- lub sky-coverage mocki pokazują że dipol obserwowany może być w całości wyjaśniony geometrią (A_mock_sky ~ A_obs w 1σ).

**Nieokreślony / wymaga weryfikacji:**
- Pośrednie wartości (np. 0<cosθ<0.5, 2<T_amp<3, niezgodność metod), lub
- cosθ>0.99 przy pierwszej próbie (kryterium stopu — szukać buga),
- lub niezgodność między C15 a L24.

### 4.7 Szczegóły dopasowania (Krok E)

- Model ΛCDM tło: Ω_m=0.3, H0=70 km/s/Mpc (lub Planck 67.4 dla testu wrażliwości), d_L(z) z astropy FlatLambdaCDM.
- Rezydua: Δμ_i = μ_obs,i - μ_ΛCDM(z_HD,i).
- Model dipolu (Colin 2019): q0(z,n) = q_m + q_d * (n·n_d) * exp(-z/S), S=0.05 (fiducial) lub S jako parametr wolny z prior U[0.01,0.1]. Alternatywnie prostszy: Δm(n) = A_d * cosθ' * exp(-z/S).
- Likelihood: L ∝ exp(-0.5 * (Δμ - model)^T C^{-1} (Δμ - model)), C = stat+sys kowariancja Pantheon+.
- Sampler: emcee, 32 walkers, 5000 steps, burn 1000, lub numpyro. Priory: q_m ~ N(-0.55,0.2), q_d ~ N(0,1), S~U, kierunek izotropowy (uniform na sferze).
- Raportujemy medianę + 16/84 percentyle.

### 4.8 Predykcja (Krok D) — niezależność

- Predykcja D_model NIE używana jako prior w E. D i E niezależne.
- D używa tylko pól gęstości/prędkości + bias b z klasteringu (Westover 2007, Carrick 2015: b≈1.1-1.4), NIE z SN.
- Propagacja niepewności: 50 CRs → rozkład n_pred, A_pred.

### 4.9 Testy null (Krok G)

- Mock 1: Gaussowskie pole losowe P(k) ΛCDM, znany dipol włożony, sprawdź odtworzenie.
- Mock 2: Izotropowe SN mock (shuffle RA/Dec lub losowe pozycje) — ile fałszywego dipolu generuje geometria Pantheon+ (półkula północna).
- Mock 3: Randomizacja v_field (losowe kierunki CR) — rozkład cosθ_null.

### 4.10 Wrażliwość (Krok H)

- Metoda 1: C15 (Wiener filter, 2M++).
- Metoda 2: L24 (NN, 2MRS).
- Skala: R_main=70 Mpc (dynamicznie preferowana, Boubel et al. 2025, ≤70 Mpc), R_test=300 Mpc (KBC fotometryczna). Użyj toy v_edge=(1/3) f H0 δ R do sanity-check.
- Oczekiwanie: R=70 Mpc daje v_edge~ (1/3)*0.5*70*0.2*70 ≈ 160 km/s (dla δ~0.2), R=300 Mpc daje ~700 km/s — nierealistyczne, więc test odporności powinien pokazać niezgodność dla 300 Mpc.

## 5. Kryteria stopu (z zadania)

- Zatrzymaj i poproś o human review jeśli:
  - cosθ>0.99 przy pierwszej próbie → bug hunt,
  - niezgodność między metodami rekonstrukcji,
  - test null pokazuje geometria nieba generuje dipol porównywalny z sygnałem,
  - brak weryfikacji v_LG≈627 km/s w Kroku A.

## 6. Raport końcowy — wymagane sekcje

- Metody, wyniki, niepewności, tabela porównawcza (Colin 2019, Erdoğdu 2006, Boubel 2025, NR observer study 2026 "1 na 20").
- Sekcja "Pewność i zastrzeżenia" obowiązkowa.
- Scope limit disclaimer.
- Brak języka odkrycia.

## 7. Zobowiązanie

Nie zmienię kryterium sukcesu z tej pre-rejestracji po zobaczeniu danych. Jeśli pipeline pokaże zbyt dobre dopasowanie, domyślnym wnioskiem jest błąd, nie sukces.

---
Podpis agenta: pre-registration przed Krokem A, 2026-09-17.
