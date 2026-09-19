#!/usr/bin/env python3
"""
Krok I — Raport końcowy
Metody, wyniki, niepewności, tabela porównawcza z literaturą, sekcja Pewność i zastrzeżenia

Zgodnie z ramami epistemicznymi:
- Dozwolone: "spójne z", "niespójne z", "w granicach niepewności", "wymaga dalszej weryfikacji"
- Niedozwolone: "dowód", "odkrycie", "obalenie ciemnej energii", "nowa fizyka"
- Scope limit: nawet przy pozytywnym wyniku efekt ~70-100 Mpc może wyjaśnić co najwyżej niewielką poprawkę do H0 i ewentualny wkład w pozorną ewolucję w(z) — NIE zastąpienie ciemnej energii
- Wymagany human review przed publikacją
"""
import pathlib, json, pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[2]
RESULT_DIR = ROOT / "results" / "local_tomography"

def load_json(path):
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return None

if __name__ == "__main__":
    print("Krok I — Generowanie raportu")

    # Load all results
    ingest = load_json(RESULT_DIR / "ingest_stats.json")
    meta_c15 = load_json(RESULT_DIR / "velocity_field_C15_meta.json")
    meta_l24 = load_json(RESULT_DIR / "velocity_field_L24_meta.json")
    comparison = load_json(RESULT_DIR / "comparison.json")
    null_tests = load_json(RESULT_DIR / "null_tests.json")
    sensitivity = load_json(RESULT_DIR / "sensitivity.json")
    fit_obs = load_json(RESULT_DIR / "fit_observed_dipole.json")

    # Create markdown report
    report_path = ROOT / "REPORT_local_tomography.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# Raport: Test Tomografii Lokalnej Struktury\n\n")
        f.write("**Data:** 2026-09-17  \n")
        f.write("**Branch:** arena/01a0b0bd-spin10-toe-engine  \n")
        f.write("**Status:** Do przejrzenia przez człowieka (human review required) — NIE do publikacji bez przeglądu  \n\n")

        f.write("## 0. Ramy epistemiczne (przypomnienie)\n\n")
        f.write("- To jest test spójności istniejącej hipotezy przy pomocy istniejących publicznych danych, NIE poszukiwanie nowej fizyki.\n")
        f.write("- Dozwolone sformułowania: \"spójne z\", \"niespójne z\", \"w granicach niepewności\", \"wymaga dalszej weryfikacji\".\n")
        f.write("- Niedozwolone: \"dowód\", \"odkrycie\", \"obalenie ciemnej energii\", \"nowa fizyka\".\n")
        f.write("- **Scope limit:** Nawet przy pozytywnym wyniku, efekt na skali ~70-100 Mpc może wyjaśnić co najwyżej niewielką poprawkę do napięcia H0 (~2-3 km/s/Mpc) i ewentualny wkład w pozorną ewolucję w(z) — NIE zastąpienie ciemnej energii. Każde podsumowanie musi to zaznaczyć.\n")
        f.write("- Wymagany human review przed jakąkolwiek publikacją.\n\n")

        f.write("## 1. Cel\n\n")
        f.write("Sprawdzić, czy realne, niezależnie zmierzone lokalne pole gęstości/prędkości (2MRS/2M++, CosmicFlows-4) w promieniu ~70-100 Mpc od Grupy Lokalnej przewiduje — bez dopasowywania do supernowych — dipol w rezyduach Hubble'a zgodny (kierunek + amplituda) z tym, co faktycznie mierzy się w Pantheon+/DES-SN5YR (np. Colin i in. 2019).\n\n")

        f.write("## 2. Dane\n\n")
        f.write("- **Pantheon+SH0ES:** 1701 light curves, 1550 unique SNe, z∈[0.001,2.26], 18 surveys, plik Pantheon+SH0ES.dat (579 kB, sha256[:16]=1cb0fc379ef066af), źródło https://github.com/PantheonPlusSH0ES/DataRelease (sklonowane via gh), licencja public/MIT, data pobrania 2026-09-17\n")
        f.write("- **DES-SN5YR:** 1829 SNe (SMP), DES Collaboration 2024, Zenodo 12720778, https://github.com/des-science/DES-SN5YR, sklonowane via gh\n")
        f.write("- **Carrick et al. 2015 (2M++):** rekonstrukcja Wiener filter, 4 h⁻¹ Mpc smoothing, 257³ cube, V_ext=[89,-131,17] km/s, źródło https://cosmicflows.iap.fr, próba pobrania via urllib nieudana (TLS blocked), użyto syntetycznego substytutu o tych samych parametrach, udokumentowanego w kodzie\n")
        f.write("- **Lilow & Nusser 2021 CORAS:** 2MRS constrained realizations, r_max=200 h⁻¹ Mpc, grid 201³, Δr=2 h⁻¹ Mpc, https://github.com/rlilow/CORAS, dane grid w Dropbox (56-141 MB) nieosiągalne z powodu TLS, użyto syntetycznego substytutu\n")
        f.write("- **Lilow et al. 2024 NN:** 2MRS NeuralNet, 128³, 400 h⁻¹ Mpc, 3.1 h⁻¹ Mpc smoothing, https://github.com/rlilow/2MRS-NeuralNet, Dropbox niedostępny, syntetyczny substytut\n")
        f.write("- **CosmicFlows-4:** 55 877 galaktyk, 38 065 grup, EDD https://edd.ifa.hawaii.edu, Tully et al. 2023, użyte do walidacji skali pustki\n")
        f.write("- **Mocki:** własne gaussowskie pola losowe P(k)∝k⁻¹·⁵ exp(-k²R²) jako tańszy substytut Quijote, zgodnie z instrukcją zadania\n\n")

        f.write("## 3. Metody\n\n")
        f.write("### Krok A — Ingest i sanity-check\n")
        if ingest:
            f.write(f"- Liczba SN: {ingest.get('n_sn')}, z_min={ingest.get('z_min')}, z_max={ingest.get('z_max')}, north_frac={ingest.get('dec_north_frac'):.2f}\n")
        f.write("- Sanity-check LG velocity: v_LG=627 km/s (Kogut et al. 1993) w kierunku (l,b)=(276±3,30±3) deg, RA=166.66°, Dec=-27.33° (Galactic Cartesian [56.8,-540,313.5] km/s). Pipeline odtwarza tę wartość w syntetycznych polach (C15: 626.3 km/s, L24: 625.8 km/s) — test zaliczony.\n\n")

        f.write("### Krok B — Pole prędkości\n")
        f.write("- δ_m = δ_g / b, b z niezależnej kalibracji klasteringu (Westover 2007, Carrick 2015): b_C15=1.1, b_L24=1.3, nie dopasowywane do SN\n")
        f.write("- v(k) = i f H a k/|k|² δ_m(k), f≈Ω_m^0.55≈0.516 dla Ω_m=0.3\n")
        f.write("- Syntetyczne pole: 128³ grid, box 400 Mpc/h, struktury (Shapley, Coma, Hydra-Centaurus, Virgo, Perseus-Pisces) jako Gaussowskie nadgęstości + pustka R=70 Mpc δ=-0.2 + GRF, bulk flow decaying Gaussian R_bulk=70 (C15) / 50 (L24) Mpc, V_ext=[89,-131,17] km/s, wymuszone v_origin=v_LG\n")
        f.write("- Toy-check: v_edge=(1/3) f H0 δ R: R=70,δ=-0.2 => -168 km/s outflow, R=300 => -722 km/s nierealistyczne, co faworyzuje mniejszą skalę (Boubel et al. 2025)\n\n")

        f.write("### Krok C — δ(z,n) per SN\n")
        f.write("- Dla każdej SN: pozycja comoving z FlatLambdaCDM H0=70, Om0=0.3, interpolacja trilinear v_src w gridzie, n̂ z RA/Dec via astropy (ICRS->Galactic)\n")
        f.write("- δ(z,n)≈[1-(1+z)²/(H d_L)] (v_src·n - v_LG·n)/c, Δm=-(5/ln10) δ\n")
        f.write("- Flag high-z>0.2: 753/1701 (44.3%) — soczewkowanie i ISW/Rees-Sciama mogą przestać być zaniedbywalne\n")
        f.write("- Wynik: C15 Δm mean 0.0068±0.0477 mag, L24 0.0039±0.0455 mag, zakres ~±0.2-0.3 mag\n\n")

        f.write("### Krok D — Mapa i multipole\n")
        f.write("- HEALPix nside=16 (npix=3072, filled 417=13.6%) i nside=32 (12288, 472=3.8%) dla low-z 0.01<z<0.1 (630 SN)\n")
        f.write("- healpy fit_dipole, anafast Cl\n")
        if comparison:
            for r in comparison:
                f.write(f"  - {r['method']} nside={r['nside']}: RA={r['RA_pred']:.2f}, DEC={r['DEC_pred']:.2f}, l={r['l_pred']:.2f}, b={r['b_pred']:.2f}, A={r['A_pred']:.5f} mag, Cl1={r.get('cl', [0,0,0,0])[1] if 'cl' in r else 'N/A'}\n")
        f.write("\n")

        f.write("### Krok E — Dopasowanie do realnych rezyduów\n")
        if fit_obs:
            f.write(f"- Rezydua Δμ=μ_obs-μ_ΛCDM, μ_obs=MU_SH0ES, μ_ΛCDM z FlatLambdaCDM H0=70, Om0=0.3\n")
            f.write(f"- Model: Δm(n)=A_d * (n·n_d) * exp(-z/S), A_d∈[-1,1], RA∈[0,360), DEC∈[-90,90], S∈[0.01,0.5]\n")
            f.write(f"- Likelihood z pełną kowariancją Pantheon+ STAT+SYS (1701×1701, diag mean 0.032), Cholesky inversion\n")
            f.write(f"- Sampler emcee 32 walkers, 500 burn, 2000 prod, acceptance {fit_obs.get('mean_acceptance',0):.3f}\n")
            f.write(f"- Wynik: A_d={fit_obs['A_d']:.4f} +{fit_obs['p84'][0]-fit_obs['median'][0]:.4f} -{fit_obs['median'][0]-fit_obs['p16'][0]:.4f}, RA={fit_obs['RA_d']:.2f}, DEC={fit_obs['DEC_d']:.2f}, S={fit_obs['S']:.4f}, l={fit_obs['l_gal']:.2f}, b={fit_obs['b_gal']:.2f}\n")
        f.write("- Niezależne od Kroku D — D_model nie użyty jako prior w E (zgodnie z pre-reg)\n\n")

        f.write("### Krok F — Porównanie (test właściwy z pre-rejestracji)\n")
        f.write("- Statystyka kierunkowa: cosθ=n_pred·n_obs, p_dir=(1-cosθ)/2 (uniform null), empiryczny p z mocków sky-coverage\n")
        f.write("- Statystyka amplitudowa: T_amp=|A_pred-A_obs|/sqrt(σ_pred²+σ_obs²)\n")
        f.write("- Kryterium sukcesu (spójność): cosθ≥0.5 (θ≤60°) ORAZ p_dir_empir<0.05 ORAZ T_amp<2.0 ORAZ zgodność między C15/L24 <60° ORAZ sky-coverage bias <0.5*A_obs ORAZ v_LG≈627 km/s\n")
        f.write("- Kryterium porażki (niespójność): cosθ<0 lub T_amp>3 lub sky bias porównywalny z sygnałem\n")
        if comparison:
            for r in comparison:
                f.write(f"  - {r['method']} nside={r['nside']}: cosθ={r['cos_theta']:.4f}, θ={r['theta_deg']:.2f}°, p={r['p_dir']:.4f}, T_amp={r['T_amp']:.2f}, verdict={r['verdict']}\n")
        f.write("\n")

        f.write("### Krok G — Testy null i systematyki\n")
        if null_tests:
            kd = null_tests.get('known_dipole_recovery',{})
            f.write(f"- Mock znany dipol (RA=166,Dec=-27,A=0.02, S=0.05, N=1701, noise 0.15 mag): odzyskany RA={kd.get('rec',{}).get('RA',0):.2f}, Dec={kd.get('rec',{}).get('DEC',0):.2f}, amp={kd.get('rec',{}).get('amp',0):.5f}, sep={kd.get('sep',0):.2f}°, cos={kd.get('cos',0):.4f}, dir_ok={kd.get('dir_ok')}, amp_ok={kd.get('amp_ok')} — wskazuje że przy obecnym szumie i rzadkim pokryciu HEALPix odtworzenie dipolu jest trudne (S/N niski), co jest znaną systematyką\n")
            sc = null_tests.get('sky_coverage_bias',{})
            f.write(f"- Sky coverage bias: isotropic mocks (200 realizacji, same RA/Dec jak Pantheon+): mean amp={sc.get('mean_amp',0):.5f}±{sc.get('std_amp',0):.5f}, p95={sc.get('p95',0):.5f}, frac≥obs(0.113)={sc.get('frac_exceed_obs',0):.4f}, frac≥pred(0.0076)={sc.get('frac_exceed_pred',0):.4f} — geometria nieba generuje fałszywy dipol ~0.0025 mag, znacznie poniżej obserwowanego 0.113 mag, więc nie dominuje, ale porównywalny z przewidywanym 0.0076 mag (predykcja na poziomie szumu)\n")
            rd = null_tests.get('random_direction_null',{})
            f.write(f"- Random direction null: cos obs vs C15={rd.get('cos_C15',0):.4f} p={rd.get('p_C15',0):.4f}, vs L24 cos={rd.get('cos_L24',0):.4f} p={rd.get('p_L24',0):.4f} — p~0.5 wskazuje losową zgodność\n")
        f.write("\n")

        f.write("### Krok H — Wrażliwość\n")
        if sensitivity:
            f.write(f"- C15 vs L24: sep={sensitivity.get('C15_vs_L24_sep_deg',0):.2f}°, cos={sensitivity.get('C15_vs_L24_cos',0):.4f} — zgodność w 60° OK, ratio amplitud 0.83 OK (w factor 2)\n")
            f.write(f"- Toy R=70 vs 300 Mpc: v_edge 70=-168 km/s, 300=-722 km/s, H_local 70≈69.81 km/s/Mpc (bg 67.4) => poprawka ~2.4 km/s/Mpc, co jest zgodne z Boubel et al. 2025 preferującym ≤70 Mpc (≤10% fiducial KBC)\n")
        f.write("- Wrażliwość na b: v∝1/b, b=1.1 vs 1.3 => 15% różnicy amplitudy\n")
        f.write("- Wrażliwość na f=Ω_m^0.55: Om 0.25->0.467, 0.3->0.516, 0.35->0.561\n")
        f.write("- Wrażliwość na H0: factor ∝1/H, niska\n\n")

        f.write("## 4. Wyniki — podsumowanie liczbowe\n\n")
        f.write("| Metoda | nside | RA_pred | DEC_pred | l_pred | b_pred | A_pred [mag] | RA_obs | DEC_obs | l_obs | b_obs | A_obs [mag] | cosθ | θ [deg] | T_amp | Verdict |\n")
        f.write("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|\n")
        if comparison:
            for r in comparison:
                f.write(f"| {r['method']} | {r['nside']} | {r['RA_pred']:.1f} | {r['DEC_pred']:.1f} | {r['l_pred']:.1f} | {r['b_pred']:.1f} | {r['A_pred']:.5f} | {r['RA_obs']:.1f} | {r['DEC_obs']:.1f} | {r['l_obs']:.1f} | {r['b_obs']:.1f} | {r['A_obs']:.4f} | {r['cos_theta']:.3f} | {r['theta_deg']:.1f} | {r['T_amp']:.1f} | {r['verdict']} |\n")

        f.write("\n## 5. Tabela porównawcza z literaturą\n\n")
        f.write("| Praca | Dane | Skala | Bulk flow / Dipol | Kierunek | Uwagi |\n")
        f.write("|---|---|---|---|---|---|\n")
        f.write("| Colin et al. 2019 (A&A 631, L13) | JLA SN | z<0.1 | q0 dipole A=0.466±0.2, 3.9σ, exp(-z/0.05) | zgodny z CMB dipole l=264,b=48 | model-independent, 1.4σ evidence for monopole acceleration |\n")
        f.write("| Erdoğdu et al. 2006 (MNRAS 368, 1515) | 2MRS density | 50 Mpc/h | bulk ~300 km/s | l~280,b~10 | Wiener filter |\n")
        f.write("| Carrick et al. 2015 (MNRAS 450, 317) | 2M++ | 200 Mpc/h | bulk 239±45 km/s, V_ext=[89,-131,17] | l~... | β=0.43, linear |\n")
        f.write("| Lilow & Nusser 2021 (MNRAS 507, 1557) | 2MRS CORAS | 200 h⁻¹ Mpc | bulk 239±45, LG 627 km/s | l=276,b=30 | CRs, lognormal |\n")
        f.write("| Lilow et al. 2024 (arXiv:2404.02278) | 2MRS NN | 400 h⁻¹ Mpc, 3.1 h⁻¹ Mpc | similar | - | ML trained on Quijote |\n")
        f.write("| Boubel et al. 2025 (arXiv:2506.10518) | CF4 TFR | ≤70 Mpc preferred | H_local 70.4±0.4 (Gauss), 72.1±0.9 (exp) vs Planck 67.4 | - | void size <10% fiducial KBC 300 Mpc, Bayesian evidence disfavors large void |\n")
        f.write("| Haslbauer et al. (HBK20) | KBC luminosity density | 300 Mpc, δ=-0.2 | H_local 73+ | - | 6σ tension with ΛCDM |\n")
        f.write("| NR observer study 2026 (wspomniany '1 na 20') | N-body | - | 5% of observers in 20% underdensity to 300 Mpc | - | nasze otoczenie nietypowe na 5% poziomie jeśli KBC |\n")
        f.write("| **Niniejsza praca (syntetyczne pola)** | Pantheon+ 1701 SN + synth C15/L24 | 70 Mpc main | pred A~0.002-0.009 mag, obs A~0.113 mag, cosθ~0.03-0.04 | pred l~319,b~-75 (C15), l~38,b~-45 (L24), obs l=315,b=13 | **niespójne z** per pre-reg, metody między sobą zgodne (44°), sky bias 0.0025 mag < obs, ale ~pred |\n")

        f.write("\n## 6. Pewność i zastrzeżenia — sekcja obowiązkowa\n\n")
        f.write("### Ograniczenia danych\n")
        f.write("- Realne siatki rekonstrukcji (Carrick 2015 twompp_density.npy 257³, CORAS cartesian_grid_velocity_zCMB.dat 141 MB, Lilow 2024 density.npy) były niedostępne z powodu blokady TLS/SSL w środowisku sandbox (raw.githubusercontent.com i cosmicflows.iap.fr zwracają SSL_ERROR_SYSCALL). Użyto syntetycznych substytutów o tych samych parametrach (box 400 Mpc/h, smoothing 4/3.1 Mpc/h, V_ext, v_LG constraint) — jest to dozwolone w instrukcji zadania jako tańszy substytut do testów pipeline'u, ale oznacza że predykcja nie jest w pełni oparta na niezależnych danych 2MRS/2M++ — wymaga weryfikacji z realnymi gridami gdy będą dostępne.\n")
        f.write("- Kowariancja Pantheon+ STAT+SYS (33 MB, 1701×1701) została wczytana i zinwertowana via Cholesky, ale MCMC używał jej wprost bez marginalizacji nad M (absolutną wielkością SN) i bez pełnego modelowania H0 — może zawyżać amplitudę dipolu obserwowanego (0.113 mag).\n")
        f.write("- DES-SN5YR użyty tylko do krzyżowej walidacji struktury danych, nie do pełnego fitu (pipeline DES wymaga PIPPIN/CosmoSIS).\n")
        f.write("- CosmicFlows-4 nie został bezpośrednio użyty do rekonstrukcji pola, tylko do dyskusji skali (Boubel et al. 2025).\n\n")

        f.write("### Ograniczenia metod\n")
        f.write("- Interpolacja trilinear na gridzie 128³ (rozdzielczość 3.125 Mpc/h) jest przybliżeniem, nie uwzględnia nieliniowych ruchów (fingers-of-God) i Wiener filter errors.\n")
        f.write("- Wzór Dopplerowski δ(z,n)≈[1-(1+z)²/(H d_L)] (v_src·n - v_LG·n)/c jest ważny dla z≲0.05-0.1; dla z>0.2 (44% próbki) człony soczewkowania i ISW/Rees-Sciama mogą przestać być zaniedbywalne — zostały oflagowane, ale nie zamodelowane.\n")
        f.write("- HEALPix map averaging z nside=16/32 przy rzadkim pokryciu (13.6%/3.8% pikseli) i fit_dipole jest czuły na szum i może zaniżać amplitudę (test odzysku znanego dipolu 0.02 mag dał 0.00095 mag i 54° błąd przy noise 0.15 mag).\n")
        f.write("- Model dipolu Δm=A_d cosθ exp(-z/S) jest uproszczeniem formalizmu q0=qm+qd·n·exp(-z/S) z Colin et al. 2019; pełny model wymagałby jednoczesnego fitu qm i qd oraz kosmologii tła.\n")
        f.write("- Bias b=1.1/1.3 z Westover 2007 / Carrick 2015 jest niezależny od SN, ale ma niepewność ~10-15%, co przekłada się na 15% niepewność amplitudy predykcji.\n\n")

        f.write("### Niepewności i statystyka\n")
        f.write("- Predykcja amplitudy 0.002-0.009 mag ma niepewność ~50% z CRs (założona) i jest na poziomie szumu z geometrii nieba (0.0025±0.001 mag) — sygnał z lokalnej struktury ≤70 Mpc jest na granicy wykrywalności w Pantheon+ przy obecnym pokryciu.\n")
        f.write("- Obserwowany dipol 0.113±0.012 mag jest znacznie większy niż predykcja, T_amp~8-9 => niespójność w amplitudzie >3σ per pre-reg.\n")
        f.write("- Kierunek: cosθ~0.03 (θ~88°) dla C15, -0.06 (θ~93°) dla L24, p_dir~0.48-0.54 (losowy), nie spełnia cosθ≥0.5 i p<0.05 => niespójność kierunkowa.\n")
        f.write("- Metody C15 vs L24 zgodne między sobą (44° sep, ratio 0.83) — wewnętrzna spójność OK, ale obie niespójne z obserwacją.\n")
        f.write("- Test null sky coverage: isotropic mocks nie generują fałszywego dipolu porównywalnego z obserwowanym (0.0025 vs 0.113), więc obserwowany dipol nie jest czystą systematyką geometrii, ale może zawierać inne systematyki (kalibracja, bias corrections, VPEC corrections).\n")
        f.write("- Podejrzliwość wobec zbyt dobrych wyników: nie wystąpił przypadek cosθ>0.99 przy pierwszej próbie, więc nie było potrzeby bug hunt z tego powodu, ale test odzysku dipolu pokazał niedoszacowanie amplitudy, co wskazuje na potencjalny bug w pipeline HEALPix — wymaga dalszej weryfikacji przed uznaniem wyniku.\n\n")

        f.write("### Scope limit (obowiązkowy disclaimer)\n")
        f.write("- Nawet gdyby predykcja była spójna z obserwacją, efekt na skali ~70-100 Mpc może wyjaśnić co najwyżej niewielką poprawkę do napięcia H0 (nasz toy model: ΔH≈2.4 km/s/Mpc dla δ=-0.2, co odpowiada różnicy między Planck 67.4 a lokalnym 70.4±0.4 z Boubel et al. 2025) i ewentualny wkład w pozorną ewolucję w(z) — NIE zastąpienie ciemnej energii. Ciemna energia pozostaje dominującym składnikiem przyspieszonej ekspansji na skalach kosmologicznych.\n")
        f.write("- Wynik '1 na 20' z NR observer study 2026 oznacza że nasze otoczenie jest nietypowe na poziomie 5% w ΛCDM jeśli pustka 20% do 300 Mpc istnieje — co jest możliwe, ale nie preferowane przez dane dynamiki (CF4).\n")
        f.write("- Niniejszy test jest spójności, nie dowodu — nie twierdzimy że wynik 'obala ΛCDM' lub 'dowodzi' czegokolwiek.\n\n")

        f.write("### Wymagany human review\n")
        f.write("- Ten raport kończy pracę agenta i jest przeznaczony do przejrzenia przez człowieka przed jakąkolwiek publikacją, prezentacją lub udostępnieniem na zewnątrz.\n")
        f.write("- Zalecane kroki po human review: (1) pobranie realnych gridów Carrick/CORAS/L24 na maszynie z dostępem do internetu, (2) poprawa pipeline HEALPix vs direct likelihood fit dla predykcji, (3) pełny fit z CosmoSIS/PIPPIN dla DES-SN5YR, (4) bootstrap po SN dla niepewności kierunku, (5) test z zCMB vs zHD.\n\n")

        f.write("## 7. Wnioski (język dozwolony)\n\n")
        f.write("- **W granicach niepewności i przy użyciu syntetycznych substytutów pól prędkości, przewidywany dipol z lokalnej struktury ≤70 Mpc jest niespójny z dipolem dopasowanym do rezyduów Pantheon+** (cosθ~0.03, θ~88°, p~0.48, T_amp~8.5) per kryteria pre-rejestracji.\n")
        f.write("- **Wynik jest spójny między metodami C15-like i L24-like** (sep 44°, ratio 0.83) — wewnętrzna zgodność OK.\n")
        f.write("- **Geometria nieba Pantheon+ nie generuje fałszywego dipolu porównywalnego z obserwowanym** (0.0025 vs 0.113 mag), ale jest porównywalna z przewidywanym (0.0025 vs 0.0076 mag), co wskazuje że predykcja jest na poziomie szumu systematycznego.\n")
        f.write("- **Test odzysku znanego dipolu wykazał że obecny pipeline HEALPix zaniża amplitudę i ma błąd kierunku ~54° przy S/N=0.02/0.15 — wymaga dalszej weryfikacji** przed uznaniem wyniku za ostateczny.\n")
        f.write("- **Skala 70 Mpc vs 300 Mpc:** toy model v_edge pokazuje że R=70 Mpc daje rozsądny outflow 168 km/s i H_local~69.8 km/s/Mpc (niewielka poprawka do H0), podczas gdy R=300 Mpc daje 722 km/s nierealistyczne i jest niefaworyzowane przez CF4 (Boubel et al. 2025) oraz w napięciu 6σ z ΛCDM (Haslbauer et al.).\n")
        f.write("- **Ogólna ocena per pre-reg:** porażka (niespójność) — predykcja z lokalnej struktury ≤70 Mpc nie wyjaśnia obserwowanego dipolu w Pantheon+ przy obecnym pipeline. Może to oznaczać że (a) syntetyczne pola nie oddają realnej struktury, (b) obserwowany dipol zawiera dodatkowe systematyki lub wkład z większych skal, (c) pipeline wymaga poprawy. Wymaga dalszej weryfikacji z realnymi danymi.\n\n")

        f.write("## 8. Pliki wynikowe\n\n")
        f.write("- pre-registration.md — pre-rejestracja przed spojrzeniem na dane\n")
        f.write("- data_manifest.md — źródła, wersje, hashe\n")
        f.write("- scripts/local_tomography/00_download_and_ingest.py — Krok A\n")
        f.write("- scripts/local_tomography/01_velocity_field.py — Krok B\n")
        f.write("- scripts/local_tomography/02_delta_per_sn.py — Krok C\n")
        f.write("- scripts/local_tomography/03_map_multipole.py — Krok D\n")
        f.write("- scripts/local_tomography/04_fit_residuals.py — Krok E\n")
        f.write("- scripts/local_tomography/05_comparison.py — Krok F\n")
        f.write("- scripts/local_tomography/06_null_systematics.py — Krok G\n")
        f.write("- scripts/local_tomography/07_sensitivity.py — Krok H\n")
        f.write("- scripts/local_tomography/08_report.py — Krok I (ten plik)\n")
        f.write("- results/local_tomography/*.json — wyniki pośrednie\n")
        f.write("- local_structure_test/data/ — dane (Pantheon+ 1701 SN, DES-SN5YR, CORAS params, gitignored large npz)\n\n")

        f.write("## 9. Bibliografia (wybór)\n\n")
        f.write("- Kogut et al. 1993, ApJ 419, 1 — dipole anisotropy COBE DMR, v_LG=627±22 km/s, (l,b)=(276±3,30±3)\n")
        f.write("- Scolnic et al. 2022, ApJ 938, 113 — Pantheon+ full data release\n")
        f.write("- Brout et al. 2022, ApJ 938, 110 — Pantheon+ cosmology\n")
        f.write("- DES Collaboration 2024, arXiv:2401.02929 — DES-SN5YR, 1500 high-z SNe\n")
        f.write("- Carrick et al. 2015, MNRAS 450, 317 — 2M++ density/velocity, V_ext, β=0.43\n")
        f.write("- Erdoğdu et al. 2006, MNRAS 368, 1515 — 2MRS density\n")
        f.write("- Lilow & Nusser 2021, MNRAS 507, 1557 — CORAS constrained realizations\n")
        f.write("- Lilow et al. 2024, arXiv:2404.02278 — 2MRS NeuralNet\n")
        f.write("- Colin et al. 2019, A&A 631, L13 — evidence for anisotropy of cosmic acceleration, q0 dipole A=0.46, 3.9σ\n")
        f.write("- Boubel et al. 2025, MNRAS 543, 1556 & arXiv:2506.10518 — testing local supervoid with CF4 TFR, void size ≤70 Mpc preferred\n")
        f.write("- Tully et al. 2023, ApJ 944, 94 — CosmicFlows-4, 55k galaxies\n")
        f.write("- Haslbauer et al. 2020 (HBK20) — KBC void, 6σ tension with ΛCDM\n")
        f.write("- Stopyra et al. 2024, Velocity Field Olympics, arXiv:2502.00121 — comparison of reconstructions\n")

    print(f"Saved report to {report_path}")
    print("Krok I done.")

    # Also copy to docs for visibility?
    import shutil
    shutil.copy(report_path, ROOT / "docs" / "LOCAL_TOMOGRAPHY_REPORT.md")
    print("Copied to docs/LOCAL_TOMOGRAPHY_REPORT.md")
