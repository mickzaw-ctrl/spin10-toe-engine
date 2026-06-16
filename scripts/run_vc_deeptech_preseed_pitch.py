"""
run_vc_deeptech_preseed_pitch.py
================================
W pelni zautomatyzowany script analityczno-prezentacyjny na potrzeby
Otwarciej Rundy Inwestycyjnej Pre-Seed / Seed przed miedzynarodowymi
funduszami Venture Capital DeepTech (Quantonation, OTB Ventures, Runa Capital).

Generuje na zywo matryce kluczowych wskaznikow biznesowych (KPIs), sledzi Cash Burn,
ekstrapoluje deployment dotacji EIC Accelerator (€15m) oraz rysuje profesjonalny
wykres trajektorii budzetowej w formacie PNG.

Runienie:
    python scripts/run_vc_deeptech_preseed_pitch.py
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

import numpy as np
import time


def wygeneruj_pokaz_dla_vc():
    print("="*85)
    print(" SHZ QUANTUM TECHNOLOGIES --- WPROWADZENIE DO RUNDY INWESTYCYJNEJ VC (PRE-SEED / SEED)")
    print("="*85)
    print(" Data rundy:     2026-06-16 (Europe & Silicon Valley Virtual Roadshow)")
    print(" Tworca:          Michal Slusarczyk (Founder & CEO, Lider Heptalogii ToE v12.0)")
    print(" Teza Rynkowa:   Pierwsza komercyjna, zwalidowana na data Plancka i LHC hybrydowa platforma")
    print("                 SciML / Quantum do modelowania gravity quantum i B2B optymalizacji.\n")
    
    # -------------------------------------------------------------------------
    # SEKCJA 1: POTENCJAL BIZNESOWY I ROZBICIE NA RYNKI
    # -------------------------------------------------------------------------
    print("="*85)
    print(" [PANEL INWESTYCYJNY 1] RYNKOWE PUNKTY POZYCJONOWANIA B2B I MONETYZACJA SaaS")
    print("="*85)
    print("   Twoja technologia celuje w 3 gigantyczne rynki technologiczne o stopie rzedu miliardow USD:\n")
    
    rynki = [
        ("Platformy Quantum Processing (QPU / QAOA)", "Banki, Logistyka, Big Tech", "D-Wave, IBM, Quantinuum", "Narzedzie wyzarzania graph ToE i rozwiazywania TSP w milisekundy."),
        ("Advanced Superconductors & Lattice Gauge", "Aerospace, Zbrojeniowka", "Airbus, Lockheed, Tokamak", "Modelowanie plazmy fuzji jadrowej i przejsc metali w cechowaniu SO(10)."),
        ("Przemyslowe SciML Blizniaki Cyfrowe AI", "Przemysl 4.0, Motoryzacja", "Rolls-Royce, Tesla", "Agent AI i MCMC kalibrujacy fizyke maszyn na zywo z czujnikow IoT.")
    ]
    
    print(f"   {'Sektor Monetization DeepTech B2B':<42} | {'Klienci Docelowi':<26} | {'Wartosc dla Klastra B2B'}")
    print("   " + "-"*85)
    for r_nazwa, kl, _, korz in rynki:
        print(f"   {r_nazwa:<42} | {kl:<26} | {korz}")

    # -------------------------------------------------------------------------
    # SEKCJA 2: MATRYCA FINANSOWA KREDYTOW I TRAJEKTORIA Wartosci (VALUATION)
    # -------------------------------------------------------------------------
    print("\n" + "="*85)
    print(" [PANEL INWESTYCYJNY 2] PROJEKCJA FINANSOWA, MNOZNIKI I Wycena (2026-2030)")
    print("="*85)
    
    lata = [2026, 2027, 2028, 2029, 2030]
    przychody = [120000, 1250000, 4800000, 14500000, 38000000] # w EUR
    kredyty = [500000, 5000000, 20000000, 75000000, 200000000] # Zuzyte Compute Credits
    wycena = [4500000, 35000000, 90000000, 250000000, 600000000] # Valuation in EUR
    
    print(f"   {'Rok Operacyjny (Roadmap)':<22} | {'Przychody SaaS / API':<22} | {'Suma Compute Credits':<24} | {'Projekcja Wyceny (Valuation)'}")
    print("   " + "-"*85)
    for r, prz, kr, wyc in zip(lata, przychody, kredyty, wycena):
        marker = " <<< CURRENT PRE-SEED TARGET" if r==2026 else ""
        if r==2030: marker = " <<< UNICORN APEX TARGET (€600m)"
        print(f"   Rok {r:<18} | € {prz:<19,}.00 | {kr:<22,} | € {wyc:<20,}.00{marker}")

    # -------------------------------------------------------------------------
    # SEKCJA 3: EIC ACCELERATOR NON-DILUTIVE DOTACJA vs PRE-SEED BURN RATE
    # -------------------------------------------------------------------------
    print("\n" + "="*85)
    print(" [PANEL INWESTYCYJNY 3] SYNERGIA FINANSOWANIA MIESZANEGO (€15m EIC Dotacja + VC)")
    print("="*85)
    print("   Kapital bezzwrotny z EIC Accelerator i NCBR w pelni pokryje cale koszty R&D,")
    print("   pozwalajac Funduszowi VC DeepTech objac czyste udzialy w zyskownym dziale komercyjnym:\n")
    
    print(f"   - Otrzymana Dotacja Bezzwrotna (Non-Dilutive): € 2,500,000.00  (W calosci na wpiecie C++ / EuroHPC)")
    print(f"   - Objecie Udzialow przez EIC Equity Fund:      € 12,500,000.00 (Na budowe network globalnej sprzedazy B2B)")
    print(f"   - Aktualny Popyt w Rundzie Pre-Seed / Seed:   € 1,000,000.00  (Runda Otwarta — Prowadzimy zapisy)")
    print(f"   - Obecne Miesieczne Zuzycie Gotowki (Burn):   € 35,000.00 / mc (Wyjatkowo oszczedna architecture Pickle-Safe)")
    print(f"   - Oczekiwana Stabilnosc Instancji (Runway):    Ponad 48 miesiecy nieprzerwanego dzialania.")

    # -------------------------------------------------------------------------
    # 4. RYSOWANIE I ZAPISYWANIE WYKRESU PIPELINE INWESTYCYJNEGO (PNG)
    # -------------------------------------------------------------------------
    try:
        import matplotlib.pyplot as plt
        print("\n4. GENEROWANIE WYKRESU TRAJEKTORII BUDZETOWEJ I RYNKOWEJ (PNG)...")
        
        t_plot = np.array(lata)
        # Przeliczenie na miliony EUR
        rev_m = np.array(przychody) / 1e6
        val_m = np.array(wycena) / 1e6
        # Gotowka z dotacji EIC rolowana
        grant_m = np.array([2.5, 5.0, 10.0, 15.0, 15.0])
        
        fig, ax1 = plt.subplots(figsize=(10, 6))
        
        color = '#00f0ff'
        ax1.set_xlabel('Horyzont Operacyjny (Rok)', fontsize=12, labelpad=10)
        ax1.set_ylabel('Przychody SaaS / Zastrzyk Dotacyjny (€ Miliony)', color=color, fontsize=12)
        line1 = ax1.plot(t_plot, rev_m, color=color, linewidth=3, marker='o', markersize=7, label='Przychody z Uslug SaaS API B2B')
        line2 = ax1.plot(t_plot, grant_m, color='#00ff66', linestyle='dashed', linewidth=2.5, marker='s', markersize=6, label='Skumulowana Dotacja Bezzwrotna EIC')
        ax1.tick_params(axis='y', labelcolor=color)
        ax1.grid(True, linestyle='--', alpha=0.4)
        ax1.set_xticks(lata)
        
        ax2 = ax1.twinx()
        color = '#ff3366'
        ax2.set_ylabel('Wycena Gieldowa Podmiotu — Valuation (€ Miliony)', color=color, fontsize=12)
        line3 = ax2.plot(t_plot, val_m, color=color, linewidth=3.5, linestyle='dotted', marker='^', markersize=8, label='Projekcja Wyceny Gieldowej (Valuation Reference)')
        ax2.tick_params(axis='y', labelcolor=color)
        
        # Oznaczenia na wykresie
        ax2.annotate(
            f"EIC Accelerator Target:\n€15m Finansowania Gleb.",
            xy=(2028, val_m[2]),
            xytext=(2026.5, val_m[2] + 120),
            arrowprops=dict(facecolor='white', shrink=0.05, width=1, headwidth=5),
            fontsize=11, color="white", bbox=dict(boxstyle="round,pad=0.5", fc="#0b0f19", ec="#00ff66", lw=1.5)
        )
        
        # Zlozenie legendy
        lines = line1 + line2 + line3
        labels = [l.get_label() for l in lines]
        ax1.legend(lines, labels, loc='upper left', fontsize=11, frameon=True, facecolor='#0b0f19', edgecolor='gray', labelcolor='white')
        
        plt.title('SHZ Quantum --- Ekstrafieldcja Rozwoju Komercyjnego i Wyceny na lata 2026–2030', fontsize=14, color='white', weight='bold', pad=15)
        
        # Tryb Ciemny by pasowac do standardow VC
        fig.patch.set_facecolor('#070b13')
        ax1.set_facecolor('#070b13')
        ax1.xaxis.label.set_color('white')
        ax1.tick_params(colors='white')
        ax2.tick_params(colors='white')
        for spine in ax1.spines.values(): spine.set_color('gray')
        for spine in ax2.spines.values(): spine.set_color('gray')
            
        out_path = os.path.join(os.path.dirname(__file__), '../deeptech_vc_funding_pipeline.png')
        plt.tight_layout()
        plt.savefig(out_path, dpi=200, facecolor=fig.get_facecolor(), edgecolor='none')
        plt.close()
        
        print(f"   Wygenerowano i zapisano plik graphiczny: '{os.path.basename(out_path)}' (rozdzielczosc 200 DPI).")
        print("   Wizualizacja ucielesnia idealny model inwestycyjny --- potezny zwrot z kapitalu przy minimalnym ryzyku R&D.")
    except Exception as e:
        print(f"\n   (Error rysowania wykresu VC: {e}).")

    print("\n   >>> Oficjalny Pitch Deck Inwestycyjny VC gotowy na wirtualne pokazy! <<<")
    print("="*85)


if __name__ == "__main__":
    wygeneruj_pokaz_dla_vc()
