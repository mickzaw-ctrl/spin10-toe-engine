# Data Manifest — Final (2026-09-17)

## 1. Pantheon+SH0ES Data Release
- Źródło: https://github.com/PantheonPlusSH0ES/DataRelease
- Pliki: Pantheon+SH0ES.dat (579283 bytes, sha256[:16]=1cb0fc379ef066af), Pantheon+SH0ES_STAT+SYS.cov (33284960 bytes, 1701x1701), Pantheon+SH0ES_STATONLY.cov
- Data pobrania: 2026-09-17 via `gh repo clone PantheonPlusSH0ES/DataRelease /tmp/PantheonData -- --depth 1`
- Liczba: 1701 light curves, 1550 unique SNe, z∈[0.001,2.26]
- Licencja: public/MIT (repo)
- Status: użyty w pipeline, sanity-check 1701 rows, RA/Dec coverage, north_frac 54.4%
- Lokalnie: local_structure_test/data/Pantheon+SH0ES.dat (gitignored), results/local_tomography/pantheon_processed.csv

## 2. DES-SN5YR
- Źródło: https://github.com/des-science/DES-SN5YR + Zenodo 10.5281/zenodo.12720778
- Data pobrania: 2026-09-17 via gh clone
- Pliki: 4_DISTANCES_COVMAT/DES-Dovekie_HD.csv, STAT+SYS.npz, etc.
- Liczba: 1829 SNe photometrically classified
- Licencja: DES Collaboration
- Status: struktura zweryfikowana, użyty do krzyżowej walidacji, nie pełny fit (wymaga PIPPIN)
- Lokalnie: local_structure_test/data/DES5YR_DISTANCES/

## 3. Carrick et al. 2015 (2M++) rekonstrukcja
- Źródło: https://cosmicflows.iap.fr/download/ (twompp_density.npy, twompp_velocity.npy, twompp_README.txt, twompp.txt.gz)
- Próba pobrania: urllib z unverified SSL -> TLS/SSL connection closed (EOF), curl -k -> Empty reply, fetch_page działa dla HTML ale nie dla binarnych npy
- Status: niedostępne w sandbox z powodu blokady TLS, użyto syntetycznego substytutu o parametrach: 128³ grid, box 400 Mpc/h, smoothing 4 Mpc/h, V_ext=[89,-131,17] km/s, v_LG constraint 627 km/s, b=1.1, f=0.516
- Publikacja: MNRAS 450, 317 (2015)
- Licencja: academic use
- Uwaga: wymaga weryfikacji z realnymi danymi gdy dostępne

## 4. Lilow & Nusser 2021 CORAS (2MRS)
- Źródło: https://github.com/rlilow/CORAS + Dropbox https://www.dropbox.com/sh/3nebvt1lskxshtu/AAByegavgA_-l1x118tZkaSAa?dl=0 (cartesian_grid_density_zCMB.dat 56.82 MB, velocity 141 MB)
- Data pobrania kodu: 2026-09-17 via gh clone, data/2MRS_group_member_catalog.dat etc. skopiowane
- Próba pobrania gridów: Dropbox via urllib unverified SSL -> TLS closed, fetch_page zwraca HTML listę plików ale nie binaria
- Status: grid niedostępny, użyto syntetycznego substytutu: GRF P(k)∝k^-1.5 exp(-k²R²), struktury Shapley/Coma/Hydra/Virgo/P-P, void R=70 Mpc δ=-0.2, bulk decaying Gaussian R=70 Mpc
- Publikacja: MNRAS 507, 1557-1581 (2021)
- Licencja: MIT (code)

## 5. Lilow et al. 2024 NeuralNet (2MRS)
- Źródło: https://github.com/rlilow/2MRS-NeuralNet + Dropbox https://www.dropbox.com/scl/fo/wb8iyg113hyin4ni7srkg/h?rlkey=bfry3x0s612qtnmgb6n82rnny&dl=0 (density.npy, velocity, error)
- Data pobrania kodu: 2026-09-17 via gh clone
- Grid: 128³, 400 h⁻¹ Mpc, 3.125 Mpc/h, smoothing 3 h⁻¹ Mpc, valid within 200 h⁻¹ Mpc sphere, NaN outside
- Próba pobrania: TLS blocked, użyto syntetycznego substytutu z innym seed i R_bulk=50 Mpc, b=1.3
- Publikacja: arXiv:2404.02278
- Status: syntetyczny substytut, wymaga realnych danych

## 6. CosmicFlows-4
- Źródło: https://edd.ifa.hawaii.edu, catalogs All CF4 Individual Distances, Groups, Velocities
- Publikacja: Tully et al. 2023 ApJ 944,94, 55877 galaxies, 38065 groups
- Status: nie pobrano bezpośrednio (EDD wymaga interaktywnego dostępu), użyto do dyskusji skali via Boubel et al. 2025 (arXiv:2506.10518) który używa CF4 TFR catalog i znajduje preferencję void ≤70 Mpc
- Licencja: public domain EDD

## 7. Mocki / GRF
- Źródło własne: generowane w scripts/local_tomography/01_velocity_field.py i 06_null_systematics.py
- P(k) = k^-1.5 exp(-(k R_smooth)²), R_smooth 4 / 3.1 Mpc/h, rms 0.3, FFT 128³
- Użyte do testów null: isotropic mocks 200 realizacji, known dipole recovery test
- Status: wygenerowane lokalnie, 58 MB npz per method (gitignored)

## 8. Weryfikacja linków (web access)
- Pantheon+ DataRelease: https://github.com/PantheonPlusSH0ES/DataRelease — OK, 83 stars, 36 forks, ostatni commit 2022-12-21, pliki Pantheon+SH0ES.dat etc. istnieją (gh api list)
- DES-SN5YR: https://github.com/des-science/DES-SN5YR — OK, 0_DATA..7_PIPPIN_FILES, Zenodo badge 12720778
- CORAS: https://github.com/rlilow/CORAS — OK, Dropbox folder z gridami istnieje (fetch_page potwierdza 4 pliki 56-141 MB)
- 2MRS-NeuralNet: https://github.com/rlilow/2MRS-NeuralNet — OK, Dropbox folder istnieje
- CosmicFlows: https://cosmicflows.iap.fr/ — OK, download page z linkami do npy i txt.gz, wymaga rejestracji, dane oparte na 2M++ (2MRS+6dF+SDSS)
- EDD: http://edd.ifa.hawaii.edu/ — OK, CosmicFlows-4 catalogs
- Velocity Field Olympics: https://github.com/Richard-Sti/csiborgtools — lista rekonstrukcji C15, L24, CSiBORG1/2, S18, C23

## 9. Hashes i wersje użyte w raporcie
- Pantheon+SH0ES.dat: 579283 bytes, sha256 1cb0fc379ef066af...
- DES-SN5YR: commit depth 1 z 2026-09-17, pliki npz w SingleSYS_CovMatrix
- CORAS params: calibrated_parameters_CR1-50.dat etc. z repo
- Syntetyczne velocity fields: velocity_field_C15.npz 58 MB, velocity_field_L24.npz 58 MB, meta json z v_origin ~626 km/s, V_ext [89,-131,17], b 1.1/1.3, R_bulk 70/50
- Wyniki: delta_per_sn_C15.csv 1701 rows, healpix maps nside16/32, dipole_pred json, fit_observed_dipole.json (A=0.113, RA=211.89, DEC=-47.93, S=0.491, l=315.89,b=13.01), comparison.json, null_tests.json, sensitivity.json

## 10. Licencje
- Pantheon+: public/MIT (sprawdź README w repo)
- DES-SN5YR: DES Collaboration, dozwolone użycie akademickie
- Carrick+15: academic use, cite MNRAS 450,317
- CORAS: MIT, cite MNRAS 507,1557
- L24: MIT, cite arXiv:2404.02278
- CF4: public domain EDD
- Własne skrypty: MIT (zgodnie z repo)

## 11. Uwagi o network restrictions
- Sandbox blokuje TLS do raw.githubusercontent.com i cosmicflows.iap.fr (SSL_ERROR_SYSCALL, Empty reply), ale gh CLI działa (używa tokena i proxy)
- Dropbox TLS również blokowany
- Dlatego realne gridy zastąpiono syntetycznymi substytutami, co jest dozwolone w instrukcji jako tańszy substytut do testów pipeline'u
- Wymaga weryfikacji z realnymi danymi na maszynie z pełnym dostępem do internetu przed human review publikacji
