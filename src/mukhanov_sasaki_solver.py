"""
mukhanov_sasaki_solver.py
=========================
Zaawansowany module do numerycznego wyznaczania pierwotnego widma mocy
fluktuacji curvature P_R(k) poprzez rozwiazywanie quantum rownania Mukanova-Sasakiego.

Modeluje inflacje w ramach modelu alpha-Attractor (zwiazanego z algebra Spin(10) ToE).
Wyznacza numerycznie scalerna amplitude fluktuacji A_s oraz indeks spektralny n_s,
w pelni uwzgledniajac odchylenia od czystej space de Sittera (slow-roll).

Author: SHZSpin10QuantumEngine Team
Version: 9.5 (Quantum Primordial Perturbations)
"""

import numpy as np
from scipy.integrate import solve_ivp
from scipy.special import gamma
from typing import Tuple, Dict, Any, List
import warnings


class MukhanovSasakiSolver:
    """
    Solwer rownania Mukanova-Sasakiego dla ewolucji fluktuacji w ToE.
    """

    @staticmethod
    def generate_inflationary_background(
        alpha: float = 3.75, 
        N_efolds: int = 60,
        n_points: int = 1000,
        A_s_target: float = None
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Generuje fizyczne tlo ewolucyjne a(eta) i z(eta) w timeie konforemnym eta
        dla modelu inflation alpha-Attractor ToE.
        
        W quasi-de Sitter mamy eta in [eta_start, eta_end] < 0,
        a(eta) ~ -1 / (H*eta) oraz z(eta) = a * sqrt(2*epsilon).

        ``A_s_target``
            Hubble scale is NOT a prediction of this model.  The Mukhanov-Sasaki
            equation is linear and ``z`` enters only through ``z''/z``, so
            ``|v_k|^2`` is independent of the overall normalisation of ``z`` and
            ``P_R`` scales exactly as ``H^2``.  A measured amplitude therefore
            *fixes* H; n_s and r are unaffected by the rescaling.

            The previous code hard-set ``H = 1e-5`` with a comment claiming it
            was normalised to ``P_R ~ 2.1e-9``.  It was not: that value of H
            together with the epsilon computed in this same function gives
            A_s = 1.86e-9, 6.3% below Planck, which showed up downstream as a
            spurious -7.9 sigma "tension" with the data.  Pass the measured
            A_s instead and H is derived from it.
        """
        # Parameters slow-roll w modelu alpha-Attractor
        # Dla potencjalu T-model/E-model V(phi) ~ (1 - e^{-...})^2
        # Mamy epsilon ~ 3*alpha / (4*N^2) oraz eta_SR ~ -2 / N
        epsilon = 3.0 * alpha / (4.0 * N_efolds**2)
        eta_SR = -2.0 / N_efolds
        
        # Wykladnik ewolucji potencjalu U(eta) = z'' / z ~ (nu^2 - 1/4) / eta^2
        # W quasi-de Sitter nu = 3/2 + epsilon - eta_SR/2
        nu = 1.5 + epsilon - 0.5 * eta_SR
        
        # Time konforemny eta: od dalekiej przeszlosci do momentu po zamrozeniu fluktuacji
        eta_start = -1000.0
        eta_end = -0.01
        
        # Uzywamy siatki logarytmicznej by uzyskac wysoka precyzje blisko eta -> 0
        eta_vals = -np.geomspace(-eta_start, -eta_end, n_points)

        # Stala Hubble'a.  Jednostki: M_Pl = 1.
        H_reference = 1.0e-5
        if A_s_target is None:
            H = H_reference
        else:
            # Dokladne rozwiazanie Hankela dla stalego nu przy prozni Buncha-Daviesa:
            #   P_R(k) = Gamma(nu)^2 H^2 2^(2 nu) / (16 pi^3 epsilon) * k^(3 - 2 nu)
            A_reference = MukhanovSasakiSolver.analytic_amplitude(
                H_reference, epsilon, nu, k_pivot=0.05)
            H = H_reference * float(np.sqrt(A_s_target / A_reference))

        # Scale a(eta) w przyblizeniu quasi-de Sitter
        a_eta = -1.0 / (H * eta_vals) * ( (-eta_vals)**(-epsilon) )
        
        # Scale z(eta) = a(eta) * sqrt(2*epsilon) z uwzglednieniem ewolucji epsilon
        z_0 = np.sqrt(2.0 * epsilon)
        z_eta = a_eta * z_0 * ( (-eta_vals)**(1.5 - nu) )
        
        return eta_vals, a_eta, z_eta

    @staticmethod
    def analytic_amplitude(
        H: float,
        epsilon: float,
        nu: float,
        k_pivot: float = 0.05
    ) -> float:
        """Exact constant-nu amplitude at ``k_pivot`` for the Bunch-Davies vacuum.

        Used as the reference against which the numerical solver is checked and
        to convert a measured A_s into a Hubble scale.
        """
        return float(
            (gamma(nu) ** 2 * H ** 2 / (16.0 * np.pi ** 3 * epsilon))
            * 2.0 ** (2.0 * nu)
            * k_pivot ** (3.0 - 2.0 * nu)
        )

    @staticmethod
    def inflationary_energy_scale(
        alpha: float = 3.75,
        N_efolds: int = 60,
        A_s_target: float = None
    ) -> Dict[str, Any]:
        """Inflationary energy scale implied by a measured A_s.

        With H fixed by the amplitude, the slow-roll potential energy
        ``V = 3 H^2 M_Pl^2`` becomes a derived quantity and can be compared with
        the unification scale obtained independently from the gauge-coupling RGE.
        """
        epsilon = 3.0 * alpha / (4.0 * N_efolds ** 2)
        eta_SR = -2.0 / N_efolds
        nu = 1.5 + epsilon - 0.5 * eta_SR
        H_reference = 1.0e-5
        A_ref = MukhanovSasakiSolver.analytic_amplitude(H_reference, epsilon, nu)
        A_s = A_ref if A_s_target is None else float(A_s_target)
        H = H_reference * float(np.sqrt(A_s / A_ref))
        V_quarter_M_Pl = (3.0 * H ** 2) ** 0.25
        M_PLANCK_GEV = 1.22e19 / np.sqrt(8.0 * np.pi)  # reduced Planck mass
        return {
            'epsilon': epsilon,
            'nu': nu,
            'H_over_M_Pl': H,
            'A_s_input': A_s,
            'r_consistency_16_epsilon': 16.0 * epsilon,
            'n_s_consistency_4_minus_2nu': 4.0 - 2.0 * nu,
            'V_quarter_M_Pl': V_quarter_M_Pl,
            'V_quarter_GeV': V_quarter_M_Pl * M_PLANCK_GEV,
        }

    @staticmethod
    def solve_mukhanov_sasaki(
        k_modes: np.ndarray, 
        eta_vals: np.ndarray, 
        a_eta: np.ndarray, 
        z_eta: np.ndarray
    ) -> np.ndarray:
        """
        Rozwiazuje uklad quantumch rownan Mukanova-Sasakiego:
            v_k'' + (k^2 - z'' / z) v_k = 0
        Gdzie v_k(eta) = z(eta) * R_k(eta).
        
        Parameters:
            k_modes: wektor falowy modow fluktuacji
            eta_vals: siatka time konforemnego
            a_eta: czynnik scale tla
            z_eta: function z = a * dphi/dN
            
        Zwraca:
            Wektor pierwotnego widma fluktuacji P_R(k) = (k^3 / 2pi^2) |R_k|^2.
        """
        spectra = []
        
        # Computeenie potencjalu efemerycznego U(eta) = z'' / z
        # Wyznaczamy numerycznie za pomoca gradientu w siatce nierownomiernej
        dz = np.gradient(z_eta, eta_vals)
        ddz = np.gradient(dz, eta_vals)
        U_eta = ddz / z_eta

        for k in k_modes:
            def ode_system(eta, y):
                # y = [v_real, v_real', v_imag, v_imag']
                vr, p_vr, vi, p_vi = y
                # Interfieldcja U_eta
                U = np.interp(eta, eta_vals, U_eta)
                omega_sq = k**2 - U
                return [p_vr, -omega_sq * vr, p_vi, -omega_sq * vi]
            
            # Warunki poczatkowe Buncha-Daviesa (asymptotyczna proznia Minkowskiego dla k|eta| >> 1)
            # v_k(eta) ~ e^{-i k eta} / sqrt(2k)
            eta_start = eta_vals[0]
            y0 = [
                np.cos(k * eta_start) / np.sqrt(2.0 * k),  k * np.sin(k * eta_start) / np.sqrt(2.0 * k),
                -np.sin(k * eta_start) / np.sqrt(2.0 * k), k * np.cos(k * eta_start) / np.sqrt(2.0 * k)
            ]
            
            # Calkowanie w dziedzinie eta
            sol = solve_ivp(
                ode_system, 
                [eta_vals[0], eta_vals[-1]], 
                y0, 
                method='RK45',
                rtol=1e-8,
                atol=1e-11
            )
            
            # Stan koncowy po przejsciu przez horyzont quantum
            vr_end, _, vi_end, _ = sol.y[:, -1]
            
            # Widmo mocy P_R(k) = (k^3 / 2pi^2) * |v_k|^2 / z^2
            v_k_sq = vr_end**2 + vi_end**2
            P_R = (k**3 / (2.0 * np.pi**2)) * (v_k_sq / (z_eta[-1]**2))
            spectra.append(P_R)
            
        return np.array(spectra, dtype=np.float64)

    @staticmethod
    def analyze_power_spectrum(
        k_modes: np.ndarray, 
        power_spectrum: np.ndarray,
        alpha: float = 3.75,
        N_efolds: int = 60
    ) -> Dict[str, Any]:
        """
        Dopasowuje parameters obserwacyjne A_s oraz n_s do wyznaczonego numerycznie widma.
        Formula dopasowania: P_R(k) = A_s * (k / k_*)^{n_s - 1}.
        """
        # Scale referencyjna k_* (tzw. pivot scale w analysisch Plancka, np. 0.05 Mpc^-1)
        k_pivot = 0.05
        idx_pivot = np.argmin(abs(k_modes - k_pivot))
        
        if abs(k_modes[idx_pivot] - k_pivot) > k_pivot * 0.5:
            # Fallback jesli siatka nie zawiera k_pivot
            idx_pivot = len(k_modes) // 2
            k_pivot = k_modes[idx_pivot]
            
        A_s_actual = float(power_spectrum[idx_pivot])
        
        # Wyznaczenie indeksu spektralnego n_s metoda regresji log-log
        # ln(P_R) = ln(A_s) + (n_s - 1) ln(k / k_*)
        # Pomijamy pierwsze, najnizsze mody (k < 0.02) by uniknac przejsciowych efektow brzegowych
        valid_k = k_modes >= 0.02
        if np.sum(valid_k) < 3:
            valid_k = np.ones_like(k_modes, dtype=bool)
            
        log_k = np.log(k_modes[valid_k] / k_pivot)
        log_P = np.log(power_spectrum[valid_k])
        
        slope, intercept = np.polyfit(log_k, log_P, 1)
        n_s_numeric = float(1.0 + slope)
        
        # Teoretyczna wartosc ToE z analityki: n_s = 1 - 2/N
        n_s_theo = 1.0 - 2.0 / N_efolds

        # Stosunek tensorowo-scalerny r w modelu ToE
        r_theo = 12.0 * alpha / (N_efolds**2)

        # Amplituda zmierzona przez Planck: ln(10^10 A_s) = 3.044 +- 0.014
        # (Planck 2018 VI).  P_R = k^3 |v_k|^2 / (2 pi^2 z^2) przy k_* = 0.05
        # Mpc^-1 jest dokladnie konwencja Plancka, wiec porownanie jest bezposrednie.
        A_s_Planck = float(np.exp(3.044) * 1e-10)
        A_s_Planck_sigma = A_s_Planck * 0.014
        A_s_sigma_deviation = abs(A_s_actual - A_s_Planck) / A_s_Planck_sigma

        return {
            'A_s': A_s_actual,
            'k_pivot': k_pivot,
            'n_s_numeric': n_s_numeric,
            'n_s_theoretical': n_s_theo,
            'n_s_error_sigma': abs(n_s_numeric - 0.9649) / 0.0042, # w porownaniu z danymi Planck PR4
            'A_s_Planck': A_s_Planck,
            'A_s_Planck_sigma': A_s_Planck_sigma,
            'A_s_error_sigma': A_s_sigma_deviation,
            'A_s_agrees_with_Planck': bool(A_s_sigma_deviation < 2.0),
            'r_theoretical': r_theo,
            'excellent_agreement': abs(n_s_numeric - n_s_theo) < 0.005
        }
