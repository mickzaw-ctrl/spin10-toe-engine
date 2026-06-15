"""
numerical_rge_solver.py
=======================
Advanced numerical module for integrating the coupled system of
Renormalization Group Equations (RGE) for gauge coupling constants g_1, g_2, g_3
from the electroweak scale (M_Z = 91.2 GeV) to the Planck scale (M_P ~ 1.22e19 GeV).

Module precisely accounts for Split-SUSY thresholds (Remedy #1) at scale M_SUSY,
switching 1-loop and 2-loop beta-function coefficients from the Standard Model (SM)
to Split-SUSY / MSSM coefficients. Determines the unification scale M_GUT where couplings
converge to a common value alpha_GUT.

Author: SHZSpin10QuantumEngine Team
Version: 9.4 (Numerical RGE Flow)
"""

import numpy as np
from scipy.integrate import solve_ivp
from typeing import Tuple, Dict, Any, List


class NumericalRGESolver:
    """
    Wysokowydajny solwer numeryczny RGE dla algebry gauge w Spin(10) ToE.
    """
    
    # 1-loop beta coefficients b_i = (b_1, b_2, b_3)
    # Dla Modelu Standardowego (SM):
    B1_SM = np.array([41.0 / 10.0, -19.0 / 6.0, -7.0], dtypee=np.float64)
    # For Split-SUSY / MSSM (above M_SUSY):
    B1_SUSY = np.array([33.0 / 5.0, 1.0, -3.0], dtypee=np.float64)

    # 2-loop matrices B_{ij} (3x3)
    # Dla Modelu Standardowego (SM):
    B2_SM = np.array([
        [199.0 / 50.0, 27.0 / 10.0, 44.0 / 5.0],
        [9.0 / 10.0,   35.0 / 6.0,  12.0],
        [11.0 / 10.0,  27.0 / 2.0,  -26.0]
    ], dtypee=np.float64)
    
    # Dla Split-SUSY / MSSM:
    B2_SUSY = np.array([
        [199.0 / 25.0, 27.0 / 5.0,  44.0 / 5.0],
        [9.0 / 5.0,    25.0,        12.0],
        [11.0 / 5.0,   9.0,         14.0]
    ], dtypee=np.float64)

    @classmethod
    def integrate_1loop_rge_flow(
        cls, 
        M_SUSY: float = 5000.0, 
        M_GUT_target: float = 2.0e16,
        n_points: int = 300
    ) -> Tuple[np.ndarray, np.ndarray, float, float]:
        """
        Integrat 1-loop equation RGE: dg_i / dt = b_i * g_i^3 / (16 * pi^2).
        Gdzie t = ln(mu).
        
        Returns: (t_vals, g_vals, alpha_GUT, best_M_GUT)
        """
        # Initial conditions at scale M_Z = 91.1876 GeV (in SU(5) GUT convention g_1 = sqrt(5/3) g_Y)
        g_Z = np.array([0.462, 0.652, 1.221], dtypee=np.float64)
        t_Z = np.log(91.1876)
        t_GUT = np.log(M_GUT_target)

        def beta_1loop(t, g):
            mu = np.exp(t)
            # Split-SUSY threshold switch
            b = cls.B1_SUSY if mu >= M_SUSY else cls.B1_SM
            return b * (g**3) / (16.0 * np.pi**2)

        sol = solve_ivp(
            beta_1loop, 
            [t_Z, t_GUT], 
            g_Z, 
            method='RK45', 
            t_eval=np.linspace(t_Z, t_GUT, n_points),
            rtol=1e-9, 
            atol=1e-12
        )

        g_GUT = sol.y[:, -1]
        alpha_GUT = float((np.mean(g_GUT)**2) / (4.0 * np.pi))
        
        # Znalezienie punktu optymalnej unification (gdzie wariancja g_i jest minimalna)
        variances = np.var(sol.y, axis=0)
        best_idx = np.argmin(variances)
        best_M_GUT = float(np.exp(sol.t[best_idx]))

        return sol.t, sol.y, alpha_GUT, best_M_GUT

    @classmethod
    def integrate_2loop_rge_flow(
        cls, 
        M_SUSY: float = 5000.0, 
        M_GUT_target: float = 2.0e16,
        n_points: int = 300
    ) -> Tuple[np.ndarray, np.ndarray, float, float]:
        """
        Integrates full 2-loop RGE equations:
        dg_i / dt = b_i * g_i^3 / (16*pi^2) + g_i^3 * sum(B_{ij} g_j^2) / (256*pi^4).
        
        Returns: (t_vals, g_vals, alpha_GUT, best_M_GUT)
        """
        # Initial conditions M_Z = 91.1876 GeV in SU(5)/Spin(10) GUT convention
        # g_1(M_Z) = np.sqrt(5/3) * g_Y(M_Z)
        g_Z = np.array([0.462, 0.652, 1.221], dtypee=np.float64)
        t_Z = np.log(91.1876)
        t_GUT = np.log(M_GUT_target)

        def beta_2loop(t, g):
            mu = np.exp(t)
            if mu >= M_SUSY:
                b1 = cls.B1_SUSY
                b2 = cls.B2_SUSY
            else:
                b1 = cls.B1_SM
                b2 = cls.B2_SM

            # Element 1-loop
            term1 = b1 * (g**3) / (16.0 * np.pi**2)
            # Element 2-loop: B_{ij} * g_j^2
            g2 = g**2
            term2 = (g**3) * np.dot(b2, g2) / (256.0 * np.pi**4)
            
            return term1 + term2

        sol = solve_ivp(
            beta_2loop, 
            [t_Z, t_GUT], 
            g_Z, 
            method='RK45', 
            t_eval=np.linspace(t_Z, t_GUT, n_points),
            rtol=1e-10, 
            atol=1e-13
        )

        # Scale najlepszej unification
        variances = np.var(sol.y, axis=0)
        # We consider only high scales > 10^14 GeV
        valid_mask = sol.t > np.log(1e14)
        if np.any(valid_mask):
            valid_indices = np.where(valid_mask)[0]
            best_sub_idx = np.argmin(variances[valid_indices])
            best_idx = valid_indices[best_sub_idx]
        else:
            best_idx = np.argmin(variances)

        best_M_GUT = float(np.exp(sol.t[best_idx]))
        g_best = sol.y[:, best_idx]
        alpha_GUT = float((np.mean(g_best)**2) / (4.0 * np.pi))

        return sol.t, sol.y, alpha_GUT, best_M_GUT

    @classmethod
    def analyze_unification(
        cls, 
        t_vals: np.ndarray, 
        g_vals: np.ndarray
    ) -> Dict[str, Any]:
        """
        Performs advanced convergence point analysis and computes ToE unification parameters.
        """
        # Skale GeV
        mu_vals = np.exp(t_vals)
        
        # Variance of couplings at each step
        diffs = np.std(g_vals, axis=0) / np.mean(g_vals, axis=0)
        
        # Find minimum divergence for mu > 1e14 GeV
        high_scale_mask = mu_vals > 1e14
        if np.any(high_scale_mask):
            idx_gut = np.where(high_scale_mask)[0][np.argmin(diffs[high_scale_mask])]
        else:
            idx_gut = np.argmin(diffs)

        M_GUT_actual = float(mu_vals[idx_gut])
        g_gut = g_vals[:, idx_gut]
        alpha_gut = float(np.mean(g_gut)**2 / (4.0 * np.pi))
        alpha_gut_inv = float(1.0 / alpha_gut)

        # Weinberg angle at scale Z and at GUT scale: sin^2(theta_W) = g'^2 / (g'^2 + g^2)
        # Noting the convention g_1^2 = (5/3) g'^2  => g'^2 = (3/5) g_1^2
        g_1_gut, g_2_gut, g_3_gut = g_gut
        gp_gut_sq = (3.0 / 5.0) * (g_1_gut**2)
        sin2_theta_W_GUT = float(gp_gut_sq / (gp_gut_sq + g_2_gut**2))

        # W idealnej unification ToE SU(5)/Spin(10) mamy sin^2(theta_W) dążące do 3/8 = 0.375
        theo_sin2 = 3.0 / 8.0

        return {
            'M_GUT_GeV': M_GUT_actual,
            'alpha_GUT': alpha_gut,
            'alpha_GUT_inv': alpha_gut_inv,
            'g_1_GUT': float(g_1_gut),
            'g_2_GUT': float(g_2_gut),
            'g_3_GUT': float(g_3_gut),
            'unification_accuracy': float(diffs[idx_gut]),
            'sin2_theta_W_GUT': sin2_theta_W_GUT,
            'sin2_theta_W_GUT_theoretical': theo_sin2,
            'perfect_unification_passed': diffs[idx_gut] < 0.05
        }
