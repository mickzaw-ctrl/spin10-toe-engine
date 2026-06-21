"""
shzspin10/streamlit_dashboard.py
================================
Interactive web dashboard for SHZSpin10 Ultima Apex v14.5.

Requires: pip install streamlit
Run: streamlit run shzspin10/streamlit_dashboard.py
Or: shzspin10-streamlit (if entry point installed)

Author: SHZ Quantum Technologies
Version: 14.5.0
"""

import json
import io
import base64
import numpy as np
import matplotlib.pyplot as plt

from .engine import (
    SHZSpin10UltimaApex,
    CosmicEvolutionEngine,
    SpinFoamLQGBridge,
    StandardModelLowEnergyDerivation,
    BlackHoleQuantumGraphity,
    cloud_gauge_relaxation,
    cloud_holographic_random_walk,
    cloud_rge_unification,
    cloud_mukhanov_sasaki,
    cloud_mera_entropy,
)


def _check_streamlit():
    try:
        import streamlit as st
        return st
    except ImportError:
        return None


def run_dashboard():
    st = _check_streamlit()
    if st is None:
        print("[ERROR] Streamlit is not installed.")
        print("  pip install streamlit")
        print("  streamlit run shzspin10/streamlit_dashboard.py")
        return

    st.set_page_config(
        page_title="SHZSpin10 Ultima Apex v14.5",
        page_icon="⚛️",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # --- CSS Custom ---
    st.markdown("""
    <style>
    .main-title { font-size: 2.2rem; font-weight: 800; color: #00d4ff; }
    .sub-title { font-size: 1.0rem; color: #8892b0; margin-top: -0.5rem; }
    .metric-card { background: #111122; border-radius: 8px; padding: 1rem; }
    .stButton>button { background: #0f3460; color: #64ffda; border: 1px solid #64ffda; }
    .stButton>button:hover { background: #64ffda; color: #0a0a12; }
    </style>
    """, unsafe_allow_html=True)

    # --- Sidebar ---
    with st.sidebar:
        st.markdown("## ⚙️ Konfiguracja Symulacji")
        st.markdown("---")

        run_base = st.checkbox("🔧 Base Engine v13.6", value=True)
        run_bh = st.checkbox("🕳️ Black Hole Quantum Graphity", value=True)
        run_lqg = st.checkbox("🌀 LQG Spin Foam (EPRL)", value=True)
        run_sm = st.checkbox("⚛️ Standard Model RGE", value=True)
        run_cloud = st.checkbox("☁️ Cloud Microservices (6x)", value=True)
        run_cosmo = st.checkbox("🌌 Cosmology (Big Bang + FRW + CMB)", value=True)

        st.markdown("---")
        st.markdown("### 📊 Parametry Kosmologii")
        phi_init = st.slider("φ_init (M_Pl)", 1.0, 20.0, 5.5, 0.1)
        n_points = st.slider("Punkty FRW", 1000, 50000, 10000, 1000)
        l_max_cmb = st.slider("l_max CMB", 50, 2500, 200, 50)

        st.markdown("---")
        st.markdown("### 🧪 Parametry LQG")
        spin_j = st.slider("spin_j", 0.5, 10.0, 2.5, 0.5)
        immirzi = st.slider("Immirzi γ", 0.1, 1.0, 0.274, 0.001)

        st.markdown("---")
        st.markdown("### ☁️ Parametry Cloud")
        nodes = st.number_input("Gauge nodes", 1000, 500000, 50000, 1000)
        m_susy = st.number_input("M_SUSY (GeV)", 1000.0, 20000.0, 5000.0, 100.0)

        st.markdown("---")
        run_btn = st.button("🚀 URUCHOM PEŁNĄ SYNTĘZĘ", use_container_width=True)

    # --- Main Header ---
    st.markdown('<p class="main-title">⚡ SHZSpin10 Ultima Apex v14.5</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Unified Quantum Theory of Everything — Interactive Dashboard</p>', unsafe_allow_html=True)
    st.markdown("---")

    if not run_btn:
        st.info("👈 Wybierz horyzonty w panelu bocznym i kliknij **URUCHOM PEŁNĄ SYNTĘZĘ**")

        # Pre-render: show dashboard structure preview
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Horyzonty fizyki", "6", "Base + LQG + SM + BH + E8 + TQEC")
        with col2:
            st.metric("Cloud microservices", "6", "Gauge + Walk + RGE + Mukhanov + MERA + AI")
        with col3:
            st.metric("Kosmologia", "4 panele", "Inflation + FRW + CMB + P(k)")
        with col4:
            st.metric("Wiek Wszechświata", "13.798 Gyr", "Planck 2018")
        return

    # --- RUN SIMULATION ---
    progress = st.progress(0, text="Inicjalizacja silnika...")
    engine = SHZSpin10UltimaApex()
    report = {}
    figures = []

    # Base
    if run_base:
        progress.progress(5, text="Base Engine v13.6...")
        report["Base Engine"] = engine.run_all()

    # Black Hole
    if run_bh:
        progress.progress(15, text="Black Hole Quantum Graphity...")
        bh = BlackHoleQuantumGraphity(internal_qubits=128)
        report["Grawitacja Kwantowa"] = bh.simulate_evaporation_page_curve(time_steps=50)

    # LQG
    if run_lqg:
        progress.progress(25, text="LQG Spin Foam EPRL...")
        lqg = SpinFoamLQGBridge()
        report["LQG Spin Foam"] = lqg.calculate_eprl_vertex_amplitude(spin_j=spin_j, immirzi_gamma=immirzi)

    # SM RGE
    if run_sm:
        progress.progress(35, text="Standard Model RGE Derivation...")
        sm = StandardModelLowEnergyDerivation()
        report["Standard Model RGE"] = sm.integrate_rge_downwards_to_modern_constants()

    # Cloud
    if run_cloud:
        progress.progress(50, text="Cloud Microservices...")
        report["Cloud Gauge"] = cloud_gauge_relaxation(nodes=nodes)
        report["Cloud Holographic Walk"] = cloud_holographic_random_walk()
        report["Cloud RGE"] = cloud_rge_unification(m_susy_gev=m_susy)
        report["Cloud Mukhanov"] = cloud_mukhanov_sasaki()
        report["Cloud MERA"] = cloud_mera_entropy()

    # Cosmology
    if run_cosmo:
        progress.progress(70, text="Cosmology: Inflation & FRW...")
        cosmo = CosmicEvolutionEngine()
        inf = cosmo.simulate_inflation_reheating(phi_init=phi_init)
        frw = cosmo.simulate_frw_evolution(n_points=n_points)
        cmb = cosmo.compute_cmb_power_spectrum(l_max=l_max_cmb)
        matter = cosmo.compute_matter_power_spectrum()

        report["Cosmology Inflation"] = inf
        report["Cosmology FRW"] = frw
        report["Cosmology CMB"] = cmb
        report["Cosmology Matter"] = matter

        # Generate plots
        progress.progress(85, text="Generowanie wykresów...")
        fig, axes = plt.subplots(2, 2, figsize=(12, 8))
        a = np.array(frw['scale_factor_a'])
        t = np.array(frw['time_Gyr'])
        T = np.array(frw['temperature_K'])
        z = np.array(frw['redshift_z'])

        ax = axes[0, 0]
        ax.semilogy(t, a, 'b-', lw=1.5)
        ax.set_xlabel('Czas [Gyr]'); ax.set_ylabel('Skala a(t)')
        ax.set_title('Ewolucja skali Wszechświata'); ax.grid(True, alpha=0.3)

        ax = axes[0, 1]
        ax.loglog(1 + z, T, 'r-', lw=1.5)
        ax.set_xlabel('1 + z'); ax.set_ylabel('Temperatura [K]')
        ax.set_title('Temperatura vs redshift'); ax.grid(True, alpha=0.3)

        ax = axes[1, 0]
        l = np.array(cmb['multipole_l']); cl = np.array(cmb['C_l_TT_uK2'])
        ax.plot(l, cl, 'k-', lw=1.2)
        ax.axvline(220, color='b', ls='--', alpha=0.7)
        ax.set_xlabel('Multipole l'); ax.set_ylabel(r'$C_l^{TT}$ [uK$^2$]')
        ax.set_title('Widmo mocy CMB'); ax.grid(True, alpha=0.3)

        ax = axes[1, 1]
        k = np.array(matter['wavenumber_k_h_Mpc']); pk = np.array(matter['power_spectrum_P_k'])
        ax.loglog(k, pk, 'g-', lw=1.5)
        ax.set_xlabel('k [h/Mpc]'); ax.set_ylabel('P(k)')
        ax.set_title('Widmo mocy materii P(k)'); ax.grid(True, alpha=0.3)

        fig.tight_layout()
        figures.append(("Kosmologia — 4 panele", fig))

        # Inflation plot
        fig2, ax2 = plt.subplots(figsize=(10, 4))
        phi_arr = np.array(inf['phi_array'])
        N_arr = np.array(inf['N_e_array'])
        ax2.plot(N_arr, phi_arr, 'c-', lw=2)
        ax2.axvline(60, color='m', ls='--', label='Horizon exit N=60')
        ax2.set_xlabel('N (e-folds)'); ax2.set_ylabel(r'$\phi / M_{Pl}$')
        ax2.set_title('Inflacja Starobinsky R² — pole skalarne vs e-folds')
        ax2.legend(); ax2.grid(True, alpha=0.3)
        fig2.tight_layout()
        figures.append(("Inflacja — pole skalarne", fig2))

    progress.progress(100, text="Synteza zakończona!")

    # --- DISPLAY RESULTS ---
    st.success("✅ Synteza ULTIMA zakończona pomyślnie!")

    # Metrics row
    st.markdown("### 📈 Kluczowe Metryki")
    mcol1, mcol2, mcol3, mcol4, mcol5 = st.columns(5)
    with mcol1:
        if run_cosmo:
            st.metric("Wiek Wszechświata", f"{report['Cosmology FRW']['age_universe_Gyr']} Gyr")
    with mcol2:
        if run_cosmo:
            st.metric("n_s (N=60)", f"{report['Cosmology Inflation']['spectral_index_n_s_60']}", "Planck: 0.9649")
    with mcol3:
        if run_cosmo:
            st.metric("r (N=60)", f"{report['Cosmology Inflation']['tensor_ratio_r_60']}", "< 0.036")
    with mcol4:
        if run_sm:
            st.metric("1/αₑₘ", f"{report['Standard Model RGE']['fine_structure_constant_0_inv']}")
    with mcol5:
        if run_sm:
            st.metric("αₛ(Mz)", f"{report['Standard Model RGE']['strong_force_coupling_MZ']}")

    st.markdown("---")

    # Tabs for each section
    tabs = st.tabs(["🌌 Kosmologia", "🧪 Fizyka", "☁️ Cloud", "📊 Wykresy", "📄 JSON Raport"])

    with tabs[0]:
        if run_cosmo:
            c1, c2 = st.columns(2)
            with c1:
                st.subheader("Inflacja Starobinsky R²")
                st.json({k: v for k, v in report["Cosmology Inflation"].items() if not isinstance(v, list)})
            with c2:
                st.subheader("Ewolucja FRW")
                st.json(report["Cosmology FRW"]["key_epochs"])
            st.subheader("Widmo CMB")
            st.json({k: v for k, v in report["Cosmology CMB"].items() if not isinstance(v, list)})
        else:
            st.info("Kosmologia nie została uruchomiona.")

    with tabs[1]:
        if run_lqg:
            st.subheader("LQG Spin Foam EPRL")
            st.json({k: v for k, v in report["LQG Spin Foam"].items() if not isinstance(v, list)})
        if run_sm:
            st.subheader("Standard Model RGE Derivation")
            st.json({k: v for k, v in report["Standard Model RGE"].items() if not isinstance(v, list)})
        if run_bh:
            st.subheader("Black Hole Quantum Graphity")
            st.json(report["Grawitacja Kwantowa"]["manifest_czarnej_dziury"])

    with tabs[2]:
        if run_cloud:
            for name in ["Cloud Gauge", "Cloud Holographic Walk", "Cloud RGE", "Cloud Mukhanov", "Cloud MERA"]:
                if name in report:
                    with st.expander(name):
                        st.json(report[name])
        else:
            st.info("Cloud nie został uruchomiony.")

    with tabs[3]:
        if figures:
            for title, fig in figures:
                st.subheader(title)
                st.pyplot(fig)
                # Download PNG
                buf = io.BytesIO()
                fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
                buf.seek(0)
                st.download_button(
                    label=f"📥 Pobierz {title}.png",
                    data=buf,
                    file_name=f"{title.replace(' ', '_').lower()}.png",
                    mime="image/png",
                )
        else:
            st.info("Brak wykresów — włącz Kosmologię.")

    with tabs[4]:
        json_str = json.dumps(report, indent=2, ensure_ascii=False)
        st.json(report)
        st.download_button(
            label="📥 Pobierz raport.json",
            data=json_str,
            file_name="shzspin10_ultima_report.json",
            mime="application/json",
        )

    st.markdown("---")
    st.markdown(
        "<p style='text-align:center; color:#64ffda;'>"
        "WSZECHŚWIAT JEST SAMOKORYGUJĄCYM SIĘ KOMPUTEREM KWANTOWYM E8.<br>"
        "CIĄGI → WYKRESY → CZĄSTKI → KUBITY → CHMURA → KOSMOS"
        "</p>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    run_dashboard()
