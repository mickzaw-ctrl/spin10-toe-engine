"""Thermo-Chromo-Dynamics (TCD) v15.0 research module.

TCD is implemented here as a collection of explicit toy parametrizations and
scientific-integrity gates.  It is not a completed Theory of Everything and it
does not turn reference lattice/QCD values into independent predictions.

All quantities use natural units (c = hbar = k_B = 1) unless a field name
states otherwise.  Energy is measured in GeV.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any, Dict, Iterable, Optional


class TCDInputError(ValueError):
    """Raised when a TCD calculation receives an invalid scientific input."""


ESTABLISHED = "established_physics"
PROJECT_HYPOTHESIS = "project_hypothesis"
UNVERIFIED = "unverified_assumption"
REJECTED = "rejected_as_stated"
INCOMPLETE = "incomplete_prediction"


@dataclass(frozen=True)
class TCDConstants:
    """Declared reference inputs; none is inferred by this module."""

    lambda_qcd_gev: float = 0.217
    qcd_crossover_gev: float = 0.1565
    qcd_crossover_uncertainty_gev: float = 0.0015
    string_tension_zero_gev2: float = 0.18
    glueball_reference_gev: float = 1.71
    planck_mass_gev: float = 1.22e19
    reduced_planck_mass_gev: float = 2.435e18
    gut_scale_gev: float = 1.03e16
    alpha_gut: float = 0.0381
    susy_scale_gev: float = 5.0e3
    hidden_generators: int = 125
    spin10_dimension: int = 45
    default_graph_nodes: int = 10**6
    coherence_coefficient: float = 0.33
    causal_fraction_reference: float = 0.738
    spectral_kappa: float = 0.7
    spectral_transition_gev: float = 1.22e19
    newton_si: float = 6.67430e-11
    dark_energy_density_reference_gev4: float = 2.5e-47

    # Compatibility aliases retained for older callers.
    @property
    def Lambda_QCD_MeV(self) -> float:  # noqa: N802
        return 1.0e3 * self.lambda_qcd_gev

    @property
    def T_c_QCD_MeV(self) -> float:  # noqa: N802
        return 1.0e3 * self.qcd_crossover_gev

    @property
    def T_c_err_MeV(self) -> float:  # noqa: N802
        return 1.0e3 * self.qcd_crossover_uncertainty_gev

    @property
    def M_Planck_GeV(self) -> float:  # noqa: N802
        return self.planck_mass_gev

    @property
    def M_GUT_GeV(self) -> float:  # noqa: N802
        return self.gut_scale_gev

    @property
    def M_SUSY_GeV(self) -> float:  # noqa: N802
        return self.susy_scale_gev

    @property
    def N_graph(self) -> int:  # noqa: N802
        return self.default_graph_nodes

    @property
    def CF_eq(self) -> float:  # noqa: N802
        return self.causal_fraction_reference


CONST = TCDConstants()


def _positive_finite(value: float, name: str) -> float:
    if isinstance(value, bool):
        raise TCDInputError(f"{name} must be numeric, not boolean")
    result = float(value)
    if not math.isfinite(result) or result <= 0.0:
        raise TCDInputError(f"{name} must be positive and finite")
    return result


def _nonnegative_finite(value: float, name: str) -> float:
    if isinstance(value, bool):
        raise TCDInputError(f"{name} must be numeric, not boolean")
    result = float(value)
    if not math.isfinite(result) or result < 0.0:
        raise TCDInputError(f"{name} must be non-negative and finite")
    return result


def qcd_dark_energy_scale_audit(
    crossover_temperature_gev: float,
    planck_mass_gev: float,
    reduced_planck_mass_gev: float,
    alpha_gut: float,
    dark_energy_density_reference_gev4: float,
) -> Dict[str, Any]:
    """Audit, rather than fit, proposed QCD-to-dark-energy scale relations.

    ``T_c^4 / M_Pl^2`` has units GeV^2 and is a candidate cosmological
    constant, not an energy density.  ``T_c^4 exp(-1/alpha_GUT)`` has units
    GeV^4 but remains many orders of magnitude above the reference dark-energy
    density for the declared inputs.
    """

    tc = _positive_finite(crossover_temperature_gev, "crossover_temperature_gev")
    mp = _positive_finite(planck_mass_gev, "planck_mass_gev")
    mpr = _positive_finite(reduced_planck_mass_gev, "reduced_planck_mass_gev")
    alpha = _positive_finite(alpha_gut, "alpha_gut")
    rho_ref = _positive_finite(
        dark_energy_density_reference_gev4,
        "dark_energy_density_reference_gev4",
    )
    qcd_density = tc**4
    lambda_candidate = qcd_density / mp**2
    lambda_reference = rho_ref / mpr**2
    instanton_density = qcd_density * math.exp(-1.0 / alpha)
    return {
        "qcd_scale_density_GeV4": qcd_density,
        "lambda_candidate_Tc4_over_Mp2_GeV2": lambda_candidate,
        "lambda_reference_GeV2": lambda_reference,
        "lambda_ratio_candidate_to_reference": lambda_candidate / lambda_reference,
        "instanton_density_Tc4_exp_minus_inv_alpha_GeV4": instanton_density,
        "instanton_density_ratio_to_reference": instanton_density / rho_ref,
        "status": REJECTED,
        "reason": (
            "T_c^4/M_Pl^2 is not a GeV^4 density and misses the observed "
            "cosmological-constant scale by about 42 orders of magnitude; "
            "the declared instanton factor does not close the remaining gap"
        ),
    }


def qcd_crossover_formula_audit(
    lambda_qcd_gev: float,
    coherence: float,
    causal_fraction: float,
    lattice_reference_gev: float,
) -> Dict[str, Any]:
    """Audit T_c = Lambda_QCD sqrt(P)/CF against a declared reference."""

    scale = _positive_finite(lambda_qcd_gev, "lambda_qcd_gev")
    coherence_value = _positive_finite(coherence, "coherence")
    cf = _positive_finite(causal_fraction, "causal_fraction")
    reference = _positive_finite(lattice_reference_gev, "lattice_reference_gev")
    predicted = scale * math.sqrt(coherence_value) / cf
    return {
        "formula_value_GeV": predicted,
        "lattice_reference_GeV": reference,
        "relative_error": abs(predicted - reference) / reference,
        "status": REJECTED,
        "reason": "the supplied formula evaluates near 0.294 GeV, not 0.156 GeV",
    }


def lattice_beta_from_alpha(alpha: float, normalization: float = 1.0) -> float:
    """Return normalization/g^2 with g^2=4 pi alpha.

    Lattice Wilson-action conventions can use other group-dependent
    normalizations, so callers must declare the normalization explicitly.
    """

    alpha_value = _positive_finite(alpha, "alpha")
    norm = _positive_finite(normalization, "normalization")
    return norm / (4.0 * math.pi * alpha_value)


def thermal_delta_g_fraction(
    temperature_gev: float,
    gut_scale_gev: float,
    hidden_generators: int = 125,
    spin10_dimension: int = 45,
) -> float:
    """Evaluate the user's dimensionless Delta G/G ansatz without validating it."""

    temperature = _nonnegative_finite(temperature_gev, "temperature_gev")
    gut_scale = _positive_finite(gut_scale_gev, "gut_scale_gev")
    if isinstance(hidden_generators, bool) or int(hidden_generators) != hidden_generators:
        raise TCDInputError("hidden_generators must be a non-negative integer")
    if isinstance(spin10_dimension, bool) or int(spin10_dimension) != spin10_dimension:
        raise TCDInputError("spin10_dimension must be a positive integer")
    hidden = int(hidden_generators)
    dimension = int(spin10_dimension)
    if hidden < 0 or dimension <= 0:
        raise TCDInputError("invalid group dimensions")
    return (temperature / gut_scale) ** 2 * hidden / dimension


def thermal_beta_correction(
    gauge_coupling: float,
    temperature_gev: float,
    susy_scale_gev: float,
    coefficient: float,
) -> float:
    """Evaluate the proposed thermal beta-function term as a project ansatz."""

    coupling = _positive_finite(gauge_coupling, "gauge_coupling")
    temperature = _nonnegative_finite(temperature_gev, "temperature_gev")
    susy_scale = _positive_finite(susy_scale_gev, "susy_scale_gev")
    coeff = _nonnegative_finite(coefficient, "coefficient")
    return coupling**3 * coeff * (temperature / susy_scale) ** 2 / (4.0 * math.pi) ** 2


def carnot_efficiency(hot_temperature: float, cold_temperature: float) -> float:
    """Return the standard Carnot efficiency for declared reservoir temperatures."""

    hot = _positive_finite(hot_temperature, "hot_temperature")
    cold = _nonnegative_finite(cold_temperature, "cold_temperature")
    if cold > hot:
        raise TCDInputError("cold_temperature must not exceed hot_temperature")
    return 1.0 - cold / hot


class ThermoSector:
    """Thermal graph diagnostics; graph-to-gravity mappings remain hypotheses."""

    def __init__(self, N: Optional[int] = None):
        node_count = CONST.default_graph_nodes if N is None else N
        if isinstance(node_count, bool) or int(node_count) != node_count or int(node_count) <= 0:
            raise TCDInputError("N must be a positive integer")
        self.N = int(node_count)

    def holographic_coherence(
        self,
        N: Optional[int] = None,
        T_GeV: Optional[float] = None,
    ) -> float:
        """Return P=1-c/sqrt(N_eff), explicitly a project parametrization."""

        node_count = self.N if N is None else N
        if isinstance(node_count, bool) or int(node_count) != node_count or int(node_count) <= 0:
            raise TCDInputError("N must be a positive integer")
        n_eff = float(node_count)
        if T_GeV is not None:
            temperature = _nonnegative_finite(T_GeV, "T_GeV")
            n_eff /= 1.0 + (temperature / CONST.gut_scale_gev) ** 2
        value = 1.0 - CONST.coherence_coefficient / math.sqrt(n_eff)
        if value <= 0.0:
            raise TCDInputError("coherence ansatz is non-positive for the declared N_eff")
        return value

    def free_energy_density(self, T_GeV: float) -> Dict[str, Any]:
        """Return an ideal-gas high-temperature diagnostic, not a QCD EOS fit."""

        temperature = _nonnegative_finite(T_GeV, "T_GeV")
        if temperature == 0.0:
            return {
                "T_GeV": 0.0,
                "p_GeV4": 0.0,
                "epsilon_GeV4": 0.0,
                "s_density_GeV3": 0.0,
                "w": None,
                "regime": "zero-temperature limit",
                "status": PROJECT_HYPOTHESIS,
            }
        # Three-flavour ideal QCD gas: 16 gluonic + 7/8 * 36 fermionic dof.
        effective_degrees = 16.0 + 7.0 / 8.0 * 36.0
        pressure = math.pi**2 * effective_degrees * temperature**4 / 90.0
        energy = 3.0 * pressure
        entropy = (energy + pressure) / temperature
        return {
            "T_GeV": temperature,
            "p_GeV4": pressure,
            "epsilon_GeV4": energy,
            "s_density_GeV3": entropy,
            "w": 1.0 / 3.0,
            "regime": "ideal three-flavour QCD gas diagnostic",
            "status": ESTABLISHED if temperature >= 1.0 else PROJECT_HYPOTHESIS,
        }

    def emergent_newton_constant(self, T_GeV: float) -> float:
        """Return G0/P(N,T), a declared project hypothesis."""

        return CONST.newton_si / self.holographic_coherence(T_GeV=T_GeV)

    def jacobson_einstein_equation(self, T_GeV: float) -> Dict[str, Any]:
        """Return a Jacobson-inspired audit without claiming field-equation closure."""

        temperature = _nonnegative_finite(T_GeV, "T_GeV")
        coherence = self.holographic_coherence(T_GeV=temperature)
        scale_audit = qcd_dark_energy_scale_audit(
            CONST.qcd_crossover_gev,
            CONST.planck_mass_gev,
            CONST.reduced_planck_mass_gev,
            CONST.alpha_gut,
            CONST.dark_energy_density_reference_gev4,
        )
        return {
            "T_GeV": temperature,
            "P(N,T)": coherence,
            "G_eff/G0": 1.0 / coherence,
            "Lambda_thermal_GeV4": None,
            "Omega_Lambda_TCD_raw": None,
            "Omega_Lambda_TCD_calib": None,
            "scale_audit": scale_audit,
            "derivation": (
                "Jacobson's local Clausius derivation is established under its "
                "own assumptions; the P(N,T) modification is not derived"
            ),
            "status": PROJECT_HYPOTHESIS,
        }


class ChromoSector:
    """Finite-temperature chromodynamic toy diagnostics."""

    def polyakov_loop(self, T_MeV: float) -> float:
        """Return a logistic crossover diagnostic, not a lattice calculation."""

        temperature = _nonnegative_finite(T_MeV, "T_MeV")
        tc = CONST.T_c_QCD_MeV
        width = 15.0
        return 1.0 / (1.0 + math.exp(-(temperature - tc) / width))

    def causal_fraction_from_polyakov(self, T_MeV: float) -> float:
        """Map a toy Polyakov diagnostic to CF; this map is unverified."""

        loop = self.polyakov_loop(T_MeV)
        cf_deconfined = 0.30
        return cf_deconfined + (CONST.causal_fraction_reference - cf_deconfined) * (1.0 - loop) ** 0.8

    def string_tension(self, T_MeV: float) -> float:
        """Return a continuous toy string-tension parametrization."""

        temperature = _nonnegative_finite(T_MeV, "T_MeV")
        tc = CONST.T_c_QCD_MeV
        if temperature >= tc:
            return CONST.string_tension_zero_gev2 * math.exp(-2.0 * (temperature - tc) / tc)
        return CONST.string_tension_zero_gev2 * math.sqrt(max(0.0, 1.0 - (temperature / tc) ** 2))

    def alpha_s_running(
        self,
        Q_GeV: float,
        include_thermal: bool = False,
        T_GeV: float = 0.0,
    ) -> float:
        """Return one-loop alpha_s above the declared perturbative floor."""

        scale = _positive_finite(Q_GeV, "Q_GeV")
        temperature = _nonnegative_finite(T_GeV, "T_GeV")
        if scale <= CONST.lambda_qcd_gev:
            raise TCDInputError("one-loop alpha_s is invalid at or below Lambda_QCD")
        flavours = 3 if scale < 4.0 else 5
        b0 = 11.0 - 2.0 * flavours / 3.0
        logarithm = math.log(scale**2 / CONST.lambda_qcd_gev**2)
        alpha = 4.0 * math.pi / (b0 * logarithm)
        if include_thermal:
            # Explicitly a toy correction; disabled by default.
            alpha *= 1.0 + 0.5 * (temperature / scale) ** 2
        return alpha

    def wilson_loop_expectation(self, area_fm2: float, T_MeV: float) -> float:
        """Return a toy area-law diagnostic with explicit fm-to-GeV conversion."""

        area = _nonnegative_finite(area_fm2, "area_fm2")
        temperature = _nonnegative_finite(T_MeV, "T_MeV")
        fm_to_gev_inverse = 5.0677307
        if temperature < CONST.T_c_QCD_MeV:
            exponent = -self.string_tension(temperature) * area * fm_to_gev_inverse**2
        else:
            perimeter_fm = 4.0 * math.sqrt(area)
            screening_mass_gev = 0.05
            exponent = -screening_mass_gev * perimeter_fm * fm_to_gev_inverse
        return math.exp(exponent)

    def eta_over_s(self, T_MeV: float) -> float:
        """Return a transparent phenomenological interpolation, not a prediction."""

        temperature = _positive_finite(T_MeV, "T_MeV")
        tc = CONST.T_c_QCD_MeV
        kss = 1.0 / (4.0 * math.pi)
        return kss + 0.010 + 0.020 * ((temperature - tc) / tc) ** 2

    def glueball_spectrum(self) -> Dict[str, Any]:
        """Return a reference-calibrated scaling diagnostic."""

        coherence = 1.0 - CONST.coherence_coefficient / math.sqrt(CONST.default_graph_nodes)
        return {
            "0++_MeV": 1.0e3 * CONST.glueball_reference_gev / coherence,
            "target_lattice_0++_MeV": 1.0e3 * CONST.glueball_reference_gev,
            "P_factor": coherence,
            "status": PROJECT_HYPOTHESIS,
            "warning": "the lattice reference is an input, so agreement is not an independent prediction",
        }

    def fifth_force_alpha(self, distance_um: float = 1.0) -> Dict[str, Any]:
        """Audit the bare dimensional ansatz; no torsion resummation is supplied."""

        distance = _positive_finite(distance_um, "distance_um")
        bare = (CONST.lambda_qcd_gev / CONST.planck_mass_gev) ** 2
        with_cf = bare * math.exp(CONST.causal_fraction_reference)
        with_hidden = with_cf * CONST.hidden_generators
        return {
            "distance_um": distance,
            "alpha_5_bare": bare,
            "alpha_5_bare_times_exp_CF": with_cf,
            "alpha_5_bare_x_hidden": with_hidden,
            "alpha_5_with_torsion_resummed_phenom": None,
            "status": INCOMPLETE,
            "reason": "no sourced torsion-resummation map derives an effective 1e-6 coupling",
        }


class ThermoChromoCoupling:
    """Cross-sector project parametrizations and standard one-loop RGE baseline."""

    def __init__(self, thermo: ThermoSector, chromo: ChromoSector):
        self.thermo = thermo
        self.chromo = chromo

    def spectral_dimension_T(self, T_GeV: float) -> float:
        """Return d_S=2+2/[1+(T/T*)^kappa], a project ansatz."""

        temperature = _nonnegative_finite(T_GeV, "T_GeV")
        ratio = temperature / CONST.spectral_transition_gev
        return 2.0 + 2.0 / (1.0 + ratio**CONST.spectral_kappa)

    def equation_of_state_w_T(self, T_GeV: float) -> float:
        """Return the declared piecewise cosmological history as a toy schedule."""

        temperature = _nonnegative_finite(T_GeV, "T_GeV")
        if temperature > CONST.gut_scale_gev / 10.0:
            return -0.99
        # Radiation domination persists through QCD, BBN, and recombination
        # until the matter-radiation equality scale (order 0.8 eV).
        if temperature > 8.0e-10:
            return 1.0 / 3.0
        # Temperature alone is not a complete cosmic clock; these late-time
        # thresholds are an explicit toy schedule, not a derived EOS.
        if temperature > 3.0e-13:
            return 0.0
        return -1.0

    def integrate_thermo_chromo_rge(
        self,
        M_GUT: Optional[float] = None,
        alpha_GUT: Optional[float] = None,
        M_SUSY: Optional[float] = None,
        n_points: int = 600,
    ) -> Dict[str, Any]:
        """Run a one-loop SM/MSSM threshold baseline; thermal term stays disabled."""

        gut = _positive_finite(CONST.gut_scale_gev if M_GUT is None else M_GUT, "M_GUT")
        alpha = _positive_finite(CONST.alpha_gut if alpha_GUT is None else alpha_GUT, "alpha_GUT")
        susy = _positive_finite(CONST.susy_scale_gev if M_SUSY is None else M_SUSY, "M_SUSY")
        if not (91.1876 < susy < gut):
            raise TCDInputError("require M_Z < M_SUSY < M_GUT")
        if isinstance(n_points, bool) or int(n_points) != n_points or int(n_points) < 2:
            raise TCDInputError("n_points must be an integer >= 2")
        b_sm = (41.0 / 10.0, -19.0 / 6.0, -7.0)
        b_mssm = (33.0 / 5.0, 1.0, -3.0)
        log_high = math.log(gut / susy)
        log_low = math.log(susy / 91.1876)
        inverse = [
            1.0 / alpha + b_mssm[i] * log_high / (2.0 * math.pi) + b_sm[i] * log_low / (2.0 * math.pi)
            for i in range(3)
        ]
        if min(inverse) <= 0.0:
            raise TCDInputError("one-loop running reached a non-perturbative branch")
        alphas = [1.0 / value for value in inverse]
        couplings = [math.sqrt(4.0 * math.pi * value) for value in alphas]
        return {
            "M_GUT_GeV": gut,
            "M_SUSY_GeV": susy,
            "alpha_GUT": alpha,
            "alpha_GUT_inv": 1.0 / alpha,
            "g_Z": couplings,
            "alpha_1_MZ": alphas[0],
            "alpha_2_MZ": alphas[1],
            "alpha_s_MZ": alphas[2],
            "thermal_correction_enabled": False,
            "thermal_term_status": UNVERIFIED,
            "unification_method": "one-loop SM/MSSM threshold baseline",
            "success": True,
            "n_points_compatibility_argument": int(n_points),
        }


class ThermoChromoDynamicsEngine:
    """Compatibility facade for the scientifically gated TCD research module."""

    def __init__(self, N: int = 10**6, M_SUSY_GeV: float = 5000.0, seed: int = 42):
        if isinstance(seed, bool) or int(seed) != seed:
            raise TCDInputError("seed must be an integer")
        self.thermo = ThermoSector(N=N)
        self.N = self.thermo.N
        self.M_SUSY = _positive_finite(M_SUSY_GeV, "M_SUSY_GeV")
        self.seed = int(seed)
        self.chromo = ChromoSector()
        self.coupling = ThermoChromoCoupling(self.thermo, self.chromo)
        self.const = CONST

    def compute_critical_temperatures(self) -> Dict[str, Any]:
        tc_mev = CONST.T_c_QCD_MeV
        formula_audit = qcd_crossover_formula_audit(
            CONST.lambda_qcd_gev,
            self.thermo.holographic_coherence(),
            CONST.causal_fraction_reference,
            CONST.qcd_crossover_gev,
        )
        return {
            "T_c_QCD_MeV": tc_mev,
            "T_c_QCD_err_MeV": CONST.T_c_err_MeV,
            "T_c_status": "external lattice-QCD reference input",
            "T_c_source": "arXiv:1908.09552; DOI:10.1103/PhysRevD.100.094510",
            "T_GUT_GeV": CONST.gut_scale_gev,
            "T_planck_GeV": CONST.planck_mass_gev,
            "CF_T_c": self.chromo.causal_fraction_from_polyakov(tc_mev),
            "Polyakov_T_c": self.chromo.polyakov_loop(tc_mev),
            "CF_Polyakov_map_status": UNVERIFIED,
            "T_c_formula_audit": formula_audit,
            "relation_Tc_Lambda": REJECTED,
        }

    def compute_eos_history(self) -> Dict[str, Any]:
        temperatures = [1e20, 1e19, 1e16, 1e3, 1.0, 0.155, 1e-3, 1e-9, 2e-13]
        history = []
        for temperature in temperatures:
            free = self.thermo.free_energy_density(temperature)
            try:
                gravity_ratio = self.thermo.emergent_newton_constant(temperature) / CONST.newton_si
                gravity_status = PROJECT_HYPOTHESIS
            except TCDInputError as exc:
                gravity_ratio = None
                gravity_status = f"outside_ansatz_domain: {exc}"
            history.append(
                {
                    "T_GeV": temperature,
                    "w_toy": self.coupling.equation_of_state_w_T(temperature),
                    "d_S_ansatz": self.coupling.spectral_dimension_T(temperature),
                    "ideal_gas_diagnostic": free,
                    "G_eff/G0_ansatz": gravity_ratio,
                    "G_eff_status": gravity_status,
                    "status": PROJECT_HYPOTHESIS,
                }
            )
        return {"eos_history": history, "status": PROJECT_HYPOTHESIS}

    def run_tcd_predictions(self) -> Dict[str, Any]:
        tc = CONST.T_c_QCD_MeV
        fifth = self.chromo.fifth_force_alpha(1.0)
        glueball = self.chromo.glueball_spectrum()
        delta_g_today = thermal_delta_g_fraction(2.35e-13, CONST.gut_scale_gev)
        delta_g_bbn = thermal_delta_g_fraction(1.0e-3, CONST.gut_scale_gev)
        return {
            "TCD-1_Tc_QCD": {
                "observable": "QCD crossover temperature",
                "value_MeV": tc,
                "status": INCOMPLETE,
                "reason": "the value is an external lattice reference input, not a TCD output",
            },
            "TCD-2_eta_s": {
                "observable": "eta/s toy interpolation",
                "eta/s_Tc": self.chromo.eta_over_s(tc),
                "eta/s_2Tc": self.chromo.eta_over_s(2.0 * tc),
                "status": PROJECT_HYPOTHESIS,
                "reason": "no TCD stress-tensor correlator or uncertainty model is implemented",
            },
            "TCD-3_fifth_force": {"observable": "chromo-torsional fifth force", **fifth},
            "TCD-4_glueball": {"observable": "lightest scalar glueball scaling", **glueball},
            "TCD-5_DeltaG": {
                "observable": "thermal Delta G/G ansatz",
                "DeltaG_today": delta_g_today,
                "DeltaG_BBN_1MeV": delta_g_bbn,
                "status": PROJECT_HYPOTHESIS,
                "reason": "the formula yields neither 1e-32 today nor 1e-2 at BBN",
            },
            "reinterpreted_38": {
                name: {"status": UNVERIFIED, "reason": "no implementing derivation in the TCD module"}
                for name in (
                    "axion_28.5neV",
                    "m_gluino_10.6TeV",
                    "f_NL_eq_14.5",
                    "eta_B_6.1e-10",
                    "n_s_0.9667_r_0.0125",
                    "Lambda_0.685",
                    "N_gen_3",
                    "CF_0.738_Var_0.262",
                )
            },
        }

    def run_full_tcd_simulation(self) -> Dict[str, Any]:
        rge = self.coupling.integrate_thermo_chromo_rge(
            M_GUT=CONST.gut_scale_gev,
            alpha_GUT=CONST.alpha_gut,
            M_SUSY=self.M_SUSY,
        )
        return {
            "engine_version": "v15.0-TCD research prototype",
            "scientific_status": "PROJECT HYPOTHESIS — NOT A VALIDATED TOE",
            "N_graph": self.N,
            "M_SUSY_GeV": self.M_SUSY,
            "critical_temperatures": self.compute_critical_temperatures(),
            "eos_and_spectral_history": self.compute_eos_history(),
            "spectral_dimension_flow": {
                f"T_{temperature:.2e}_GeV": self.coupling.spectral_dimension_T(temperature)
                for temperature in (1e21, 1e20, 1e19, 1e16, 1e3, 0.155, 0.0)
            },
            "rge_thermo_chromo": rge,
            "emergent_gravity_Jacobson": self.thermo.jacobson_einstein_equation(2e-13),
            "tcd_predictions": self.run_tcd_predictions(),
            "w_today": self.coupling.equation_of_state_w_T(2e-13),
            "consistency_with_heptalogy": {
                "tests_executed_by_report": False,
                "total_40/40_TCD": False,
                "zero_new_parameters": False,
                "status": INCOMPLETE,
            },
            "falsification_criteria": {
                "status": INCOMPLETE,
                "reason": "no TCD item currently has a derived signal, covariance, and frozen external-data likelihood",
            },
            "equation_Z_TCD": (
                "formal project ansatz only; measure, gauge fixing, graph ensemble, "
                "and continuum limit are not specified"
            ),
            "assumption_ledger": "docs/TCD_ASSUMPTION_LEDGER.json",
        }


class TCDLabForApex:
    """Compatibility adapter retained for the Windows/Ultima facade."""

    def __init__(self, N: int = 10**6):
        self.engine = ThermoChromoDynamicsEngine(N=N)

    def run_termo_chromo_simulation(self) -> Dict[str, Any]:
        return self.engine.run_full_tcd_simulation()


def demo() -> None:
    """Print a concise scientific-status report."""

    report = ThermoChromoDynamicsEngine().run_full_tcd_simulation()
    print(report["engine_version"])
    print(report["scientific_status"])
    print("TCD contract outputs are diagnostics, not validated predictions.")


if __name__ == "__main__":
    demo()
