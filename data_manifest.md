# Data Manifest — Tomografia Lokalnej Struktury

**Data utworzenia:** 2026-09-17
**Status:** wstępna wersja przed pobraniem — aktualizowana po ingest.

## Zasady
Każdy zbiór: źródło, data pobrania, wersja/hash, licencja, lokalna ścieżka.

## Zbiory

### 1. Pantheon+SH0ES Data Release
- Źródło: https://github.com/PantheonPlusSH0ES/DataRelease
- Alternatywny URL: https://pantheonplussh0es.github.io/
- Pliki oczekiwane: Pantheon+SH0ES.dat, Pantheon+SH0ES_STAT+SYS.cov, etc.
- Licencja: MIT / public (sprawdź w repo)
- Status: do pobrania
- Data pobrania: -
- Hash: -
- Weryfikacja: 1701 light curves, 1550 unique SNe, z ∈ [0.001,2.26], 18 surveys (Scolnic et al. 2022, Brout et al. 2022)

### 2. DES-SN5YR
- Źródło: https://github.com/des-science/DES-SN5YR + Zenodo https://doi.org/10.5281/zenodo.12720778 (DES-SN5YR-1.2.zip)
- Pliki: light curves, distances, covmat
- Licencja: DES Collaboration
- Status: do pobrania

### 3. Carrick et al. 2015 (2M++) rekonstrukcja
- Źródło: https://cosmicflows.iap.fr + https://cosmicflows.iap.fr (density/velocity grids)
- Alternatywnie: https://github.com/Richard-Sti/csiborgtools (lista rekonstrukcji)
- Opis: linear inverse modelling, luminosity-weighted, resolution 4 h^-1 Mpc
- Licencja: academic use
- Status: do pobrania
- Sanity-check: ma odtwarzać bulk flow, LG velocity

### 4. Lilow & Nusser 2021 CORAS (2MRS)
- Źródło: https://github.com/rlilow/CORAS + grid data alongside code
- Opis: Wiener filter in spherical Fourier-Bessel, constrained realizations, r_max=200 h^-1 Mpc
- Rozdzielczość: Δr=2 h^-1 Mpc, Δθ=Δφ=π/50
- Status: do pobrania
- Publikacja: MNRAS 507, 1557-1581 (2021), arXiv:2102.07291

### 5. Lilow et al. 2024 NeuralNet (2MRS)
- Źródło: https://github.com/rlilow/2MRS-NeuralNet
- Opis: ML inverse method trained on Quijote, resolution 3.1 h^-1 Mpc
- Status: do pobrania

### 6. CosmicFlows-4
- Źródło: https://edd.ifa.hawaii.edu (EDD), catalogs: All CF4 Individual Distances, CF4 All Groups, CF4 All Group Velocities
- Publikacja: Tully et al. 2023 ApJ 944,94
- Liczba: 55877 galaxies, 38065 groups
- Licencja: public domain EDD
- Status: do pobrania

### 7. Mocki / Quijote (jeśli dostępne) + własne GRF
- Źródło własne: generowane gaussowskie pola losowe o P(k) ΛCDM (CAMB/Eisenstein&Hu)
- Alternatywa: Quijote simulations https://quijote-simulations.readthedocs.io/ (jeśli dostęp)
- Status: generowane lokalnie w pipeline

## Procedura pobrania
- Skrypt: scripts/local_tomography/download_data.py (do napisania)
- Weryfikacja hashy SHA256 po pobraniu
- Zapis do data/ (gitignored) lub data_manifest update

## Wersje użyte w raporcie końcowym
(TBD po ingest)


## Update 2026-09-17 19:04:32.893618
- Pantheon+SH0ES.dat exists: True
  - size: 579283 bytes, sha256[:16]=1cb0fc379ef066af
  - source: https://github.com/PantheonPlusSH0ES/DataRelease (cloned via gh)
  - date: 2026-09-17 19:04:32.893700
  - license: public/MIT (check repo)
