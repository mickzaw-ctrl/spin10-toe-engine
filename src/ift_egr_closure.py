"""IFT-EGR v0.3 cosmology closure and falsifiability gates.

This module is deliberately isolated from :mod:`ift_egr`. It implements exact
algebraic checks that can be tested without claiming that a causal GFT
condensate, a cosmological constant, or an observational likelihood has been
derived.

Units
-----
Unless stated otherwise, c = hbar = G = l_Pl = 1. Areas are expressed in
Planck-area units and densities in Planck-density units.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable

import numpy as np
from numpy.typing import ArrayLike, NDArray


class ClosureInputError(ValueError):
    """Raised when a scientific closure calculation receives invalid inputs."""


@dataclass(frozen=True)
class PartialOrderAudit:
    """Machine-readable audit of a finite candidate causal partial order."""

    is_reflexive: bool
    is_antisymmetric: bool
    is_transitive: bool

    @property
    def is_partial_order(self) -> bool:
        return self.is_reflexive and self.is_antisymmetric and self.is_transitive


def _positive_finite(value: float, name: str) -> float:
    result = float(value)
    if not math.isfinite(result) or result <= 0.0:
        raise ClosureInputError(f"{name} must be positive and finite")
    return result


def lqc_area_gap_planck(gamma: float) -> float:
    """Return Delta/l_Pl^2 = 4 sqrt(3) pi gamma in standard LQC convention."""

    gamma_value = _positive_finite(gamma, "gamma")
    return 4.0 * math.sqrt(3.0) * math.pi * gamma_value


def lqc_critical_density_ratio(gamma: float, area_gap_planck: float | None = None) -> float:
    """Return rho_c/rho_Pl = 3/(8 pi gamma^2 Delta) in Planck units.

    ``area_gap_planck`` is Delta/l_Pl^2. If omitted, the standard LQC area gap
    is used. This reproduces approximately 0.41 for gamma = 0.2375; it is an
    LQC result, not a new IFT-EGR prediction.
    """

    gamma_value = _positive_finite(gamma, "gamma")
    delta = (
        lqc_area_gap_planck(gamma_value)
        if area_gap_planck is None
        else _positive_finite(area_gap_planck, "area_gap_planck")
    )
    return 3.0 / (8.0 * math.pi * gamma_value**2 * delta)


def lqc_hubble_squared(rho: float, rho_c: float, newton_g: float = 1.0) -> float:
    """Return the effective flat-LQC H^2 on its physical density branch."""

    density = float(rho)
    critical = _positive_finite(rho_c, "rho_c")
    gravity = _positive_finite(newton_g, "newton_g")
    if not math.isfinite(density) or density < 0.0 or density > critical:
        raise ClosureInputError("rho must lie on the physical branch 0 <= rho <= rho_c")
    return (8.0 * math.pi * gravity / 3.0) * density * (1.0 - density / critical)


def puncture_area_planck(spin: float, gamma: float) -> float:
    """Return A_j/l_Pl^2 = 8 pi gamma sqrt(j(j+1))."""

    j = _positive_finite(spin, "spin")
    if 2.0 * j != round(2.0 * j):
        raise ClosureInputError("spin must be a positive half-integer")
    gamma_value = _positive_finite(gamma, "gamma")
    return 8.0 * math.pi * gamma_value * math.sqrt(j * (j + 1.0))


def isolated_horizon_entropy_upper_bound(spins: Iterable[float]) -> float:
    """Return sum_i log(2 j_i + 1), before projection/topology constraints.

    This is a degeneracy upper bound, not the complete ABCK/DL microcanonical
    entropy. Gauge projection, finite Chern-Simons level, and topology can
    reduce the state count and generate subleading corrections.
    """

    spin_values = tuple(float(spin) for spin in spins)
    if not spin_values:
        raise ClosureInputError("spins must contain at least one puncture")
    for spin in spin_values:
        puncture_area_planck(spin, gamma=1.0)
    return float(sum(math.log(2.0 * spin + 1.0) for spin in spin_values))


def entropy_per_area_ratio(spin: float) -> float:
    """Return the gamma-independent ratio log(2j+1)/sqrt(j(j+1))."""

    j = _positive_finite(spin, "spin")
    if 2.0 * j != round(2.0 * j):
        raise ClosureInputError("spin must be a positive half-integer")
    return math.log(2.0 * j + 1.0) / math.sqrt(j * (j + 1.0))


def dominant_spin(candidates: Iterable[float]) -> float:
    """Return the candidate maximizing the independent-puncture entropy/area ratio."""

    values = tuple(float(spin) for spin in candidates)
    if not values:
        raise ClosureInputError("candidates must not be empty")
    return max(values, key=entropy_per_area_ratio)


def spherical_horizon_radius_planck(
    puncture_count: int,
    spin: float,
    gamma: float,
) -> float:
    """Return L/l_Pl from 4 pi L^2 = N_p A_j.

    The factor 4 pi is the area of a spherical horizon. Replacing it by
    pi L^2 would overestimate the radius by exactly a factor of two.
    """

    if isinstance(puncture_count, bool) or int(puncture_count) != puncture_count:
        raise ClosureInputError("puncture_count must be a positive integer")
    count = int(puncture_count)
    if count <= 0:
        raise ClosureInputError("puncture_count must be a positive integer")
    area = count * puncture_area_planck(spin, gamma)
    return math.sqrt(area / (4.0 * math.pi))


def holographic_lambda_planck(entropy: float, coefficient: float) -> float:
    """Return Lambda l_Pl^2 = coefficient / S for a declared HDE-like ansatz.

    Entropy is dimensionless and ``coefficient`` must be supplied explicitly.
    Dimensional consistency and inverse-area scaling do not derive the
    coefficient or select the infrared horizon.
    """

    entropy_value = _positive_finite(entropy, "entropy")
    coefficient_value = _positive_finite(coefficient, "coefficient")
    return coefficient_value / entropy_value


def classical_padmanabhan_constant(
    hubble_squared: float,
    rho: float,
    newton_g: float = 1.0,
    *,
    regime: str = "classical",
) -> float:
    """Return C = H^2 - 8 pi G rho/3 only in the classical FLRW regime.

    The classical integrated equation is not valid at an LQC/GFT bounce, where
    the rho^2/rho_c correction is order unity. The explicit regime guard
    prevents an invalid bounce substitution from being presented as a
    derivation of the late-time cosmological constant.
    """

    if regime != "classical":
        raise ClosureInputError(
            "the classical Padmanabhan integration constant cannot be inferred "
            "at a quantum bounce; derive a modified emergence law first"
        )
    h2 = float(hubble_squared)
    density = float(rho)
    gravity = _positive_finite(newton_g, "newton_g")
    if not math.isfinite(h2) or h2 < 0.0:
        raise ClosureInputError("hubble_squared must be non-negative and finite")
    if not math.isfinite(density) or density < 0.0:
        raise ClosureInputError("rho must be non-negative and finite")
    return h2 - (8.0 * math.pi * gravity / 3.0) * density


def efold_intersection(
    model_lower: float,
    model_upper: float,
    required_lower: float,
    required_upper: float,
) -> tuple[float, float] | None:
    """Return the overlap of two closed e-fold intervals, or ``None``."""

    values = tuple(float(value) for value in (model_lower, model_upper, required_lower, required_upper))
    if not all(math.isfinite(value) for value in values):
        raise ClosureInputError("e-fold bounds must be finite")
    if model_lower > model_upper or required_lower > required_upper:
        raise ClosureInputError("e-fold interval lower bounds must not exceed upper bounds")
    lower = max(model_lower, required_lower)
    upper = min(model_upper, required_upper)
    return (lower, upper) if lower <= upper else None


def audit_partial_order(relation: ArrayLike) -> PartialOrderAudit:
    """Audit reflexivity, antisymmetry, and transitivity of a finite relation."""

    matrix = np.asarray(relation, dtype=bool)
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1] or matrix.shape[0] == 0:
        raise ClosureInputError("relation must be a non-empty square matrix")
    identity = np.eye(matrix.shape[0], dtype=bool)
    reflexive = bool(np.all(np.diag(matrix)))
    antisymmetric = bool(not np.any(matrix & matrix.T & ~identity))
    composed = (matrix.astype(np.int64) @ matrix.astype(np.int64)) > 0
    transitive = bool(np.all(~composed | matrix))
    return PartialOrderAudit(reflexive, antisymmetric, transitive)


def causal_order_violation_fraction(transition_weight: ArrayLike, relation: ArrayLike) -> float:
    """Return weighted support outside strict future-directed causal relations.

    This is a project diagnostic for candidate causal-GFT kernels. A value of
    zero is necessary but not sufficient for a consistent causal quantum theory.
    """

    weights = np.asarray(transition_weight, dtype=float)
    matrix = np.asarray(relation, dtype=bool)
    audit = audit_partial_order(matrix)
    if not audit.is_partial_order:
        raise ClosureInputError("relation must be a valid partial order")
    if weights.shape != matrix.shape or not np.all(np.isfinite(weights)) or np.any(weights < 0.0):
        raise ClosureInputError("transition_weight must be finite, non-negative, and match relation")
    strict_future = matrix & ~np.eye(matrix.shape[0], dtype=bool)
    total = float(np.sum(weights))
    if total == 0.0:
        return 0.0
    forbidden = float(np.sum(np.where(strict_future, 0.0, weights)))
    return forbidden / total


def gft_condensate_number_profile(
    relational_scalar: ArrayLike,
    minimum_number: float,
    newton_g: float = 1.0,
    bounce_scalar: float = 0.0,
) -> NDArray[np.float64]:
    """Return the symmetric single-mode free-GFT number-profile ansatz.

    N(phi) = N_min cosh(sqrt(12 pi G) (phi - phi_b)). This imported GFT
    condensate profile does not identify GFT quanta with horizon punctures and
    does not encode a causal partial order by itself.
    """

    minimum = _positive_finite(minimum_number, "minimum_number")
    gravity = _positive_finite(newton_g, "newton_g")
    phi = np.asarray(relational_scalar, dtype=float)
    if not np.all(np.isfinite(phi)) or not math.isfinite(float(bounce_scalar)):
        raise ClosureInputError("relational scalar values must be finite")
    argument = math.sqrt(12.0 * math.pi * gravity) * (phi - float(bounce_scalar))
    return np.asarray(minimum * np.cosh(argument), dtype=np.float64)
