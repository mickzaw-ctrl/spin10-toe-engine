# UMOWA KONSORCJUM EUROPEJSKIEJ INFRASTRUKTURY OBLICZENIOWEJ (EuroHPC Synergy)
**Umowa o Wspolpracy Strategicznej R&D, Shardowaniu Sieci i Wdrozeniach ToE v12.0**

**ZAWARTA W DNIU 2026-06-16 W WARSZAWIE / KRAKOWIE / BRUKSELI POMIEDZY:**

**SHZ Quantum Technologies Sp. z o.o.** z siedziba w Warszawie/Krakowie, (Podmiot Spin-Off DeepTech), zwanym dalej **„Liderem Konsorcjum / Tworca ToE”**,  
a  
**Akademickim Centrum Komputerowym Cyfronet AGH (PLGrid)** z siedziba w Krakowie,  
**Interdyscyplinarnym Centrum Modelowania Matematycznego i Komputerowego (ICM UW)** z siedziba w Warszawie,  
**Jülich Supercomputing Centre (JSC)** w Forschungszentrum Jülich GmbH z siedziba w Jülich (Niemcy),  
**CINECA Consorzio Interuniversitario** z siedziba w Bolonii (Wlochy),  
oraz  
**CSC — IT Center for Science (LUMI Supercomputer)** z siedziba w Espoo/Kajaani (Finlandia),  
zwanymi wspolnie **„Wezlami Klastrowymi EuroHPC”**.

---

## § 1. PRZEDMIOT UMOWY I MANIFEST STRATEGICZNY
Przedmiotem niniejszej Umowy jest powolanie miedzynarodowego konsorcjum badawczo-wdrozeniowego pod nazwa **„European Spin(10) Quantum Modeling & SciML Cloud Network”** na potrzeby uruchamiania, zrownoleglania i testowania na akceleratorach GPU ogolnoswiatowego jadra computeeniowego **`SHZSpin10QuantumEngine v12.0-ULTIMA`**. Lider dostarcza authorskie oprogramowanie i algorytmy w frameworku Python / C++ / Ray, a Nodes Klastrowe udostepniaja moc computeeniowa i partycje akcelerowane w najwiekszych superkomputerach kontynentu.

---

## § 2. ROLAE I ZOBOWIAZANIA PARTNEROW KONSORCJUM

### [1] Lider Konsorcjum (SHZ Quantum Technologies Sp. z o.o.)
*   Udostepnia zoptymalizowane hybrydowe jadro w czystym C++ (`libspin10_hpc.so`) oraz scripts orkiestratora w `Ray` ze wsparciem dla dynamicznego, bezpiecznego ladowania bibliotek (Pickle-Safe Architecture).
*   Koordynuje prace badawcze w zakresie wyznaczania przeplywow Dimensionu Spektralnego ($d_S: 2 \to 4$), ewolucji ewolucyjnej RGE Modelu Standardowego oraz estymacji Bayesowskiej MCMC.
*   Zglasza project do finansowania z programu **EIC Accelerator (€15m)** w roli koordynatora rynkowego.

### [2] Cyfronet AGH / PLGrid & ICM UW (Polskie Nodes Jadrowe HPC)
*   Instaluja engine zrodlowy w zasobach klastrow **Prometheus, Athena, Ares oraz Okeanos** jako referencyjna biblioteke udostepniana panstwowemu srodowisku badawczemu w ramach grantow KDM.
*   Dokonuja shardowania wielomilionowych graphow relacyjnych w oparciu o szybkie interkonekty InfiniBand.

### [3] Jülich Supercomputing Centre (JSC) & CINECA
*   Biora na siebie weryfikacje quantumch Lorentzkich amplitud przejscia $A_v$ wierzcholka Petlowej Grawitacji (LQG w modelu EPRL / Barretta-Crane'a) w Bulku hiper-network ToE.
*   Weryfikuja niezmienniczosc Immirziego ($\gamma \approx 0.274$) w swietle Von Neumannowskiej entropy Bekensteina-Hawkinga na zderzaczach numerycznych JUPITER i Leonardo.

### [4] LUMI Supercomputer / CSC Finlandia (The Pre-Exascale Engine)
*   Przejmuja orkiestracje chmurowa klastrow `Ray` dla errorzenia losowego Lazy Random Walk w scale holographic ($N=10^6$ oraz $10^7$ nodes).
*   Zapewniaja Klientom komercyjnym Lidera absolutne SLA na wywolywane w chmurze uslugi mikrouslugowe `FastAPI Cloud Engine` (POST /cloud/service/*) ze stawka miliarda operacji tensorowych na sekunde.

---

## § 3. PRAWA WLASNOSCI INTELEKTUALNEJ (IP)
1.  Authorskie prawa majatkowe do wyjsciowych kodow engine **Spin10 v12.0** pozostaja niepodzielna wlasnoscia Lidera Konsorcjum.
2.  Nodes Klastrowe otrzymuja wolna, nieograniczona timeowo ani terytorialnie licencje akademicka w standardzie **GNU AGPLv3** na pelne running kodu do celow czysto naukowych, publikacyjnych i badawczych.
3.  Zyski z **Licencji Komercyjnych Enterprise** (SaaS Cloud/API, Blizniaki Cyfrowe w Tokamak Plasma, QAOA combinatoric optimization) sprzedawanych korporacjom w pelni przypadaja Liderowi --- z wylaczeniem ustalonej prowizji za zuzyte kilowatogodziny i nodes (Core-Hours) placonej poszczegolnym klastrom EuroHPC.

---

## § 4. CZAS TRWANIA UMOWY
Niniejsza Umowa zostala zawarta na time okreslony od dnia **2026-06-16 do dnia 2036-12-31** --- pokrywajacy sie w stu procentach z ustalonym w Heptalogii horyzontem weryfikacji i ostatecznych celow falsyfikacyjnych w nadchodzacych eksperymentach (misji LiteBIRD, CMB-S4, Hyper-K, CASPEr).

*Podpisy Oficjalnych Przedstawicieli ze strony Lidera oraz Dyrektorow Wezlow EuroHPC osadzone w protokole kryptographicznym.*
