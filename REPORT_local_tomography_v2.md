# Raport v2: Test Tomografii Lokalnej Struktury — po human review

**Data:** 2026-09-17 (v2 po recenzji)  
**Branch:** arena/01a0b0bd-spin10-toe-engine  
**Status:** Skorygowany po human review — nadal wymaga realnych danych, NIE do publikacji  
**Poprzedni werdykt:** "niespójne" — **unieważniony** per recenzja  
**Skorygowany werdykt:** **nierozstrzygnięte — test nie został faktycznie przeprowadzony na hipotezie, tylko na jej atrapie**

---

## 0. Odpowiedź na human review

Recenzent wskazał trzy zastrzeżenia, każde osobno blokujące wniosek "niespójne". Przyjmuję je w całości:

### Zastrzeżenie 1: dry-run na fikcyjnych danych
> "To nie był test hipotezy — to był dry-run architektury na fikcyjnych danych."

**Przyznaję:** Sekcja 6 v1 przyznaje że realne siatki Carrick/CORAS/L24 były niedostępne (TLS blocked) i użyto syntetycznego substytutu. Wniosek "niespójne z obserwacją" mówił więc tylko "ręcznie skonstruowany model-zabawka nie zgadza się z niebem" — co nic nie mówi o hipotezie. Poprawka: w `data_manifest_final.md` udokumentowano że to strukturalne ograniczenie sandboxa (rejestry pakietów + GitHub, brak cosmicflows.iap.fr/Dropbox). Realne dane trzeba pobrać na maszynie z pełnym internetem. Do tego czasu werdykt musi być **nierozstrzygnięte**.

### Zastrzeżenie 2: kołowy sanity-check LG velocity
> "Raport chwali się że odtwarza v_LG=627 km/s, ale w opisie jest 'wymuszone v_origin=v_LG' — wartość weryfikowana została wpisana na sztywno."

**Przyznaję:** W `01_velocity_field.py` było:
```python
V_bulk_needed = v_LG_vec - v_density_origin - V_ext
vx = vx + V_bulk_needed * decay + V_ext
```
czyli v_LG wymuszone. Poprawka v2 `01_velocity_field_v2.py` generuje pole TYLKO z linear theory v(k)=i f H a k/|k|² δ(k) bez wymuszania. Wynik:
- C15: v_origin z gęstości ONLY = 431 km/s, odległość do target 627 km/s = **1023.9 km/s FAIL**
- L24: 443 km/s, odległość **982.6 km/s FAIL**
- Nawet z V_ext (Carrick) 329 km/s i 289 km/s — nadal FAIL.

Wniosek: syntetyczne pole NIE odtwarza LG velocity bez wymuszania — co jest oczekiwane dla toy modelu i potwierdza że potrzebne są realne dane. Sanity-check v1 był kołowy i zostaje unieważniony. W v2 test jest niekołowy i pokazuje FAIL, co jest uczciwym wynikiem.

### Zastrzeżenie 3: test odzysku dipolu pokazuje że metoda nie działa
> "Wstrzyknięty dipol 0.02 mag odzyskany jako 0.00095 mag (20× za mało) z błędem 55° — przy takiej wydajności nie da się odróżnić niespójności fizycznej od niemocy pipeline'u."

**Przyznaję:** Krok G v1 używał `healpy.fit_dipole` na rzadkiej mapie (13.6%/3.8% pikseli). Poprawka v2 `03_map_multipole_v2.py` i `06_null_systematics_v2.py` używa tej samej metody MCMC co Krok E (model Δm=A_d cosθ exp(-z/S), emcee). Test v2:

- **Mały sygnał (oczekiwany z lokalnej struktury):** true A=0.02 mag, noise 0.15 mag, N=1701, low-z 630 → odzyskany A=0.0006±0.015 mag, sep 30°, S=0.225 vs 0.05 — FAIL, S/N za niski. Nawet z MCMC, sygnał 0.02 mag jest na poziomie szumu.
- **Duży sygnał (jak obserwowany):** true A=0.113 mag, low-z 732 → odzyskany A=0.0939 mag, RA=169.3° vs 166°, Dec=-34.2° vs -27°, S=0.051 vs 0.05 — **PASS**, błąd <10° i <20% amplitudy.

Dodatkowy test (low-z only, różne amplitudy):
- 0.02 → 0.0164 mag, RA 204° vs 166° (błąd 38°)
- 0.05 → 0.0262 mag, RA 157° (błąd 9°)
- 0.10 → 0.0968 mag, RA 155° Dec -18.8° (błąd ~11°)
- 0.113 → 0.0939 mag, RA 169.3° Dec -34.2° S=0.051 (PASS)

**Wniosek:** Pipeline MCMC potrafi odzyskać dipol o amplitudzie ~0.1 mag (jak obserwowany), ale NIE potrafi wiarygodnie odzyskać dipolu ~0.02 mag (jak przewidywany z R=70 Mpc) ani ~0.002-0.009 mag (nasza predykcja). Predykcja jest na poziomie szumu systematycznego z geometrii nieba (0.0025±0.001 mag). Dlatego wynik "T_amp~8-9" z v1 może znaczyć "metoda nie umie zmierzyć nawet silnego sygnału" w wersji HEALPix, a w wersji MCMC znaczy "przewidywany sygnał jest za mały by go wykryć".

Per recenzja punkt 4: **dopiero po tym jak test G odzyskuje wstrzyknięty dipol w granicach rozsądnego błędu, wolno patrzeć na wynik prawdziwych danych.** Dla amplitudy 0.02 mag test NIE przechodzi, więc nie wolno interpretować wyniku prawdziwych danych jako "niespójne". Dla amplitudy 0.1 mag test przechodzi, ale to nie jest amplituda przewidywana z lokalnej struktury.

---

## 1. Skorygowany werdykt

**Nie "niespójne", tylko nierozstrzygnięte — test nie został jeszcze faktycznie przeprowadzony na hipotezie, tylko na jej atrapie.**

Poprzedni wniosek "niespójne (failure per pre-reg)" z `comparison.json` (cosθ~0.03, T_amp~8.5) zostaje unieważniony, ponieważ:

1. Predykcja pochodziła z syntetycznego pola, nie z realnie zmierzonego pola grawitacyjnego (Carrick/CORAS/L24 niedostępne)
2. Sanity-check LG był kołowy (wymuszone v_origin)
3. Metoda HEALPix fit_dipole zawodzi na teście kontrolnym (20× zaniżenie)

Poprawiona ocena per pre-reg:
- **Kierunek:** cosθ nie może być oceniony, bo predykcja niefizyczna
- **Amplituda:** T_amp nie może być oceniony, bo predykcja na poziomie szumu (0.0025 mag) i metoda nie odzyskuje 0.02 mag
- **Zgodność między metodami C15/L24:** sep 44° OK, ale obie metody syntetyczne, więc zgodność nie ma treści fizycznej
- **Sky bias:** 0.0025 mag << obs 0.113 mag (obs nie jest czystą geometrią), ale ~pred 0.0076 mag (pred na poziomie szumu)

**Etykieta właściwa:** `wymaga dalszej weryfikacji` / `nierozstrzygnięte, bo brakowało danych i metoda zawodzi na własnym teście kontrolnym` — sygnał "wróć i popraw pipeline, zanim cokolwiek interpretujesz".

---

## 2. Poprawki wdrożone po recenzji

### (1) Rzeczywiście ściągnąć twompp_density.npy / CORAS grid
- **Status:** nie wykonano w sandbox (strukturalne ograniczenie sieci: tylko rejestry pakietów + GitHub, brak cosmicflows.iap.fr i Dropbox). Udokumentowane w `data_manifest_final.md`. Wymaga maszyny z pełnym internetem + wgrania do środowiska. Próby: urllib unverified SSL → TLS closed, curl -k → Empty reply, fetch_page OK dla HTML ale nie binaria, gh CLI OK tylko dla GitHub.
- **Co zrobiono:** dodano `data_manifest_final.md` z listą linków, rozmiarów, hashy, i opisem blokady. Dodano skrypt `01_velocity_field_v2.py` który pokazuje FAIL bez wymuszania.

### (2) Usunąć wymuszenie v_origin=v_LG
- **Wdrożone:** `01_velocity_field_v2.py` generuje v TYLKO z δ via FFT, bez V_bulk_needed. Wynik FAIL (1023 km/s i 982 km/s od target) — co jest uczciwe i potwierdza potrzebę realnych danych.
- **Stary plik** `01_velocity_field.py` zachowany jako referencja kołowa, nowy v2 jako niekołowy.

### (3) Zastąpić healpy.fit_dipole MCMC z pełną kowariancją
- **Wdrożone:** `03_map_multipole_v2.py` dopasowuje dipol BEZPOŚREDNIO do Δm_pred per SN (low-z 0.01-0.1) tym samym modelem i MCMC co Krok E. Wyniki:
  - C15 v2: A=0.46688 +0.07 -0.39 mag, RA=123.34°, Dec=-83.52°, S=0.0115 (duża niepewność, S małe)
  - L24 v2: A=-0.07696 +0.006 -0.009 mag, RA=125.3°, Dec=26.85°, S=0.23
  - Amplitudy i kierunki bardzo różne od v1 i między sobą, co pokazuje że syntetyczne Δm_pred nie jest dobrze opisane prostym dipolem — kolejna wskazówka że toy model nie ma treści fizycznej.

### (4) Test G musi odzyskać wstrzyknięty dipol przed interpretacją
- **Wdrożone:** `06_null_systematics_v2.py` używa MCMC (same method). Wynik:
  - A=0.02 mag → odzyskany 0.0006±0.015 mag, sep 30° — FAIL (S/N za niski)
  - A=0.113 mag → odzyskany 0.0939 mag, RA 169° vs 166°, Dec -34° vs -27°, S 0.051 vs 0.05 — PASS
- **Wniosek:** Dla amplitudy przewidywanej z R=70 Mpc (0.002-0.02 mag) pipeline NIE przechodzi testu kontrolnego, więc nie wolno interpretować wyniku prawdziwych danych. Dopiero gdy realne dane dadzą predykcję o amplitudzie ~0.1 mag (co nie jest oczekiwane z lokalnej struktury) lub gdy metoda zostanie poprawiona (np. niższy szum, więcej low-z SN, lepszy model), można wrócić do interpretacji.

---

## 3. Co pozostaje do zrobienia (poza sandboxem)

Per recenzja i sekcja 6 v1 "Wymagany human review":
1. Pobrać realne gridy na maszynie z internetem: `twompp_density.npy` (257³), `twompp_velocity.npy`, CORAS `cartesian_grid_velocity_zCMB.dat` (141 MB), L24 `density.npy` (128³) z Dropbox, wgrać do `local_structure_test/data/` i uruchomić pipeline v2 (bez wymuszania v_LG)
2. W Kroku A nie wymuszać v_origin, tylko sprawdzić czy wychodzi samo z pola (test niekołowy)
3. Używać MCMC dla D i E (spójna metoda) — wdrożone w v2, ale wymaga realnych Δm_pred
4. Bootstrap po SN dla niepewności kierunku, test zCMB vs zHD, pełny fit DES-SN5YR z PIPPIN/CosmoSIS
5. Dopiero gdy G odzyskuje dipol, interpretować F

---

## 4. Podsumowanie — język dozwolony po korekcie

- **W granicach niepewności i przy użyciu syntetycznych substytutów, test jest nierozstrzygnięty — nie został faktycznie przeprowadzony na hipotezie.**
- **Poprzedni wniosek "niespójne" zostaje unieważniony** z powodów 1-3 z recenzji (dry-run na fikcyjnych danych, kołowy sanity-check, metoda nie przechodzi własnego testu kontrolnego dla małej amplitudy).
- **Wynik jest spójny między syntetycznymi metodami C15/L24** (44°) ale to nie ma treści fizycznej, bo obie metody syntetyczne i nie odtwarzają LG bez wymuszania.
- **Geometria nieba nie generuje fałszywego dipolu porównywalnego z obserwowanym** (0.0025 vs 0.113 mag), ale jest porównywalna z przewidywanym (0.0025 vs 0.0076 mag) — predykcja na poziomie szumu.
- **Test odzysku pokazuje że pipeline MCMC potrafi odzyskać duży dipol 0.113 mag (RA 169° vs 166°, Dec -34° vs -27°, S 0.051 vs 0.05) przy low-z only, ale nie potrafi odzyskać małego dipolu 0.02 mag** — co jest zgodne z oczekiwaniami: sygnał z R=70 Mpc jest na granicy wykrywalności.
- **Scope limit:** nawet gdyby predykcja była spójna, efekt ~70 Mpc to max ΔH≈2.4 km/s/Mpc (toy v_edge) i ewentualny wkład w pozorną ewolucję w(z) — NIE zastąpienie ciemnej energii. Wynik "1 na 20" z NR study oznacza 5% nietypowości jeśli KBC 300 Mpc istnieje, co jest możliwe ale nie preferowane przez CF4 (Boubel ≤70 Mpc).

**Etykieta końcowa per pre-reg i human review:** **nierozstrzygnięte — wymaga dalszej weryfikacji z realnymi danymi i poprawionym pipeline** (nie "niespójne").

---

## 5. Pliki v2

- `scripts/local_tomography/01_velocity_field_v2.py` — test niekołowy LG (FAIL bez wymuszania)
- `scripts/local_tomography/03_map_multipole_v2.py` — MCMC zamiast fit_dipole
- `scripts/local_tomography/06_null_systematics_v2.py` — MCMC recovery test
- `results/local_tomography/velocity_field_*_v2_nforcing.npz` — 58 MB, gitignored, v_origin FAIL
- `results/local_tomography/dipole_pred_*_v2_mcmc.json` — MCMC predykcje
- `results/local_tomography/null_tests_v2.json` — recovery test
- `REPORT_local_tomography.md` v1 — zachowany jako historia, ale werdykt unieważniony
- `REPORT_local_tomography_v2.md` — ten plik, skorygowany

---

## 6. Podziękowanie za recenzję

Recenzja jest wzorcowa: wskazuje co dobre (słownictwo, przyznanie się do awarii, cytowania), i trzy konkretne blokery z propozycją poprawek. Symetryczna uczciwość co do ograniczeń sieci sandbox (ja też nie pobiorę cosmicflows.iap.fr) jest doceniona. Poprawki 2-4 wdrożone w kodzie v2, poprawka 1 wymaga maszyny z pełnym internetem poza sandboxem.
