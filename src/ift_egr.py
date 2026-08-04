"""IFT-EGR v0.2: numerically stabilized research prototype.

This module preserves the main public interfaces of the original prototype while
correcting deterministic zero dynamics, Bures-speed normalization, density-matrix
stability, graph-edge counting, and coordinate/proper-time Hubble relations.

Scientific status
-----------------
This is a project hypothesis and a numerical research prototype. It does not
constitute a derivation of general relativity. All quantities are expressed in
Planck units unless an explicit calibration is supplied.
"""

from __future__ import annotations

from functools import partial
from typing import NamedTuple

import equinox as eqx
import jax
import jax.numpy as jnp

jax.config.update("jax_enable_x64", True)

N_NODES = 32
N_EDGE_MODES = 6
BETA_RG = 0.05
GRAPH_COUPLING = 0.30
GEOMETRIC_COUPLING = 0.05
ETA_VERLINDE = 0.25
CUTOFF_IR = 1.0e-12
ENTROPY_FLOOR = 1.0e-12
OMEGA_MIN = 1.0e-12  # Used only in divisions, never as a physical clock tick.
CLOCK_CALIBRATION = 1.0  # One Planck time per unit Bures length: project hypothesis.
PLANCK_DENSITY = 1.0


def _dagger(matrix: jax.Array) -> jax.Array:
    return jnp.swapaxes(matrix.conj(), -1, -2)


@jax.jit
def project_density_matrix(rho: jax.Array) -> jax.Array:
    """Project a matrix onto Hermitian, positive-semidefinite, unit-trace states."""
    rho_h = 0.5 * (rho + _dagger(rho))
    evals, evecs = jnp.linalg.eigh(rho_h)
    evals = jnp.maximum(evals, 0.0)
    total = jnp.sum(evals)
    dim = rho.shape[-1]
    normalized = jnp.where(
        total > CUTOFF_IR,
        evals / total,
        jnp.ones_like(evals) / jnp.float64(dim),
    )
    return (evecs * normalized[None, :]) @ _dagger(evecs)


@jax.jit
def symmetric_log_derivative(rho: jax.Array, drho: jax.Array) -> jax.Array:
    """Solve rho L + L rho = 2 drho on the support of rho."""
    rho_h = project_density_matrix(rho)
    drho_h = 0.5 * (drho + _dagger(drho))
    drho_h = drho_h - jnp.trace(drho_h).real * jnp.eye(
        drho_h.shape[-1], dtype=drho_h.dtype
    ) / jnp.float64(drho_h.shape[-1])

    evals, evecs = jnp.linalg.eigh(rho_h)
    drho_basis = _dagger(evecs) @ drho_h @ evecs
    denominator = evals[:, None] + evals[None, :]
    support = denominator > CUTOFF_IR
    safe_denominator = jnp.where(support, denominator, 1.0)
    l_basis = jnp.where(support, 2.0 * drho_basis / safe_denominator, 0.0)
    return evecs @ l_basis @ _dagger(evecs)


@jax.jit
def quantum_fisher_information(rho: jax.Array, drho: jax.Array) -> jax.Array:
    """Return tangent-space quantum Fisher information Tr(drho L_drho)."""
    l_sld = symmetric_log_derivative(rho, drho)
    value = jnp.real(jnp.trace(drho @ l_sld))
    return jnp.maximum(value, 0.0)


class InformationClock(eqx.Module):
    tau_proper: jax.Array
    t_coord: jax.Array
    omega_global: jax.Array
    omega_local: jax.Array
    dtau_dt: jax.Array

    @staticmethod
    def init(n_nodes: int = N_NODES) -> "InformationClock":
        return InformationClock(
            tau_proper=jnp.float64(0.0),
            t_coord=jnp.float64(0.0),
            omega_global=jnp.float64(0.0),
            omega_local=jnp.zeros(n_nodes, dtype=jnp.float64),
            dtau_dt=jnp.float64(0.0),
        )


@partial(jax.jit, static_argnames=("dt_coord",))
def information_frequency_matrix(
    rho_t0: jax.Array,
    rho_t1: jax.Array,
    dt_coord: float = 0.01,
) -> jax.Array:
    """Return the symmetric Bures-speed matrix, omega = 0.5 sqrt(F_Q)."""
    if dt_coord <= 0.0:
        raise ValueError("dt_coord must be positive")

    drho_dt = (rho_t1 - rho_t0) / dt_coord
    rho_mid = 0.5 * (rho_t0 + rho_t1)

    def edge_speed(rho: jax.Array, tangent: jax.Array) -> jax.Array:
        fq = quantum_fisher_information(rho, tangent)
        return 0.5 * jnp.sqrt(jnp.maximum(fq, 0.0))

    omega = jax.vmap(jax.vmap(edge_speed))(rho_mid, drho_dt)
    return 0.5 * (omega + omega.T)


@partial(jax.jit, static_argnames=("dt_coord",))
def compute_information_clock(
    rho_t0: jax.Array,
    rho_t1: jax.Array,
    adj: jax.Array,
    clock_old: InformationClock,
    dt_coord: float = 0.01,
) -> InformationClock:
    """Advance the clock using undirected active edges exactly once."""
    omega_mat = information_frequency_matrix(rho_t0, rho_t1, dt_coord)
    active = jnp.where(adj > 0.0, 1.0, 0.0)
    upper_mask = jnp.triu(active, k=1)
    edge_count = jnp.sum(upper_mask)
    omega_global_raw = jnp.where(
        edge_count > 0.0,
        jnp.sum(omega_mat * upper_mask) / edge_count,
        0.0,
    )
    omega_global = CLOCK_CALIBRATION * jnp.maximum(omega_global_raw, 0.0)

    degree = jnp.sum(active, axis=1)
    local_sum = jnp.sum(omega_mat * active, axis=1)
    omega_local = CLOCK_CALIBRATION * jnp.where(
        degree > 0.0, local_sum / jnp.maximum(degree, 1.0), 0.0
    )

    dtau = omega_global * dt_coord
    return InformationClock(
        tau_proper=clock_old.tau_proper + dtau,
        t_coord=clock_old.t_coord + dt_coord,
        omega_global=omega_global,
        omega_local=omega_local,
        dtau_dt=omega_global,
    )


@jax.jit
def local_time_dilation(clock: InformationClock) -> jax.Array:
    """Return local/global clock ratios; use unity when the global clock is static."""
    return jnp.where(
        clock.omega_global > OMEGA_MIN,
        clock.omega_local / clock.omega_global,
        jnp.ones_like(clock.omega_local),
    )


@jax.jit
def effective_gravitational_potential(clock: InformationClock) -> jax.Array:
    """Return the project-hypothesis lapse potential Phi/c^2 = log(Omega_i/Omega)."""
    gamma = jnp.maximum(local_time_dilation(clock), OMEGA_MIN)
    return jnp.log(gamma)


@jax.jit
def temporal_entropy_weight(
    omega_mat: jax.Array, omega_planck: float = 1.0
) -> jax.Array:
    """Return a bounded temporal activity ansatz in consistent Planck units."""
    scale = jnp.maximum(jnp.asarray(omega_planck, dtype=jnp.float64), OMEGA_MIN)
    return -jnp.expm1(-jnp.maximum(omega_mat, 0.0) / scale)


@jax.jit
def von_neumann_entropy_single(rho: jax.Array) -> jax.Array:
    rho_psd = project_density_matrix(rho)
    evals = jnp.linalg.eigvalsh(rho_psd)
    return -jnp.sum(jnp.where(evals > CUTOFF_IR, evals * jnp.log(evals), 0.0))


@jax.jit
def effective_entropy_matrix(
    graph_rho: jax.Array, omega_mat: jax.Array, adj: jax.Array
) -> jax.Array:
    entropy = jax.vmap(jax.vmap(von_neumann_entropy_single))(graph_rho)
    return entropy * temporal_entropy_weight(omega_mat) * jnp.where(adj > 0.0, 1.0, 0.0)


@jax.jit
def emergent_G_ift(
    graph_rho: jax.Array, omega_mat: jax.Array, adj: jax.Array
) -> jax.Array:
    """Return the dimensionless entropy-response ansatz in Planck units."""
    s_eff = effective_entropy_matrix(graph_rho, omega_mat, adj)
    upper_mask = jnp.triu(jnp.where(adj > 0.0, 1.0, 0.0), k=1)
    s_total = jnp.sum(s_eff * upper_mask)
    area_horizon = jnp.float64(adj.shape[0]) ** (2.0 / 3.0)
    return ETA_VERLINDE * area_horizon / (s_total + ENTROPY_FLOOR)


def _modular_hamiltonian(rho: jax.Array) -> jax.Array:
    rho_psd = project_density_matrix(rho)
    evals, evecs = jnp.linalg.eigh(rho_psd)
    log_evals = -jnp.log(jnp.maximum(evals, CUTOFF_IR))
    return (evecs * log_evals[None, :]) @ _dagger(evecs)


@jax.jit
def corner_anomaly_ift(
    rho_t0: jax.Array,
    rho_t1: jax.Array,
    omega_mat: jax.Array,
    adj: jax.Array,
) -> jax.Array:
    """Return a non-negative, temporally weighted modular-variance ansatz."""

    def edge_variance(rho0: jax.Array, rho1: jax.Array) -> jax.Array:
        delta_k = _modular_hamiltonian(rho1) - _modular_hamiltonian(rho0)
        delta_k = 0.5 * (delta_k + _dagger(delta_k))
        rho_ref = project_density_matrix(rho1)
        mean = jnp.real(jnp.trace(rho_ref @ delta_k))
        second = jnp.real(jnp.trace(rho_ref @ delta_k @ delta_k))
        return jnp.maximum(second - mean * mean, 0.0)

    variances = jax.vmap(jax.vmap(edge_variance))(rho_t0, rho_t1)
    theta = temporal_entropy_weight(omega_mat)
    upper_mask = jnp.triu(jnp.where(adj > 0.0, 1.0, 0.0), k=1)
    normalization = jnp.sum(theta * upper_mask)
    return jnp.where(
        normalization > CUTOFF_IR,
        jnp.sum(variances * theta * upper_mask) / normalization,
        0.0,
    )


class RelationalGraph(eqx.Module):
    edge_rho: jax.Array
    node_pos: jax.Array
    adj: jax.Array
    rg_scale: jax.Array

    @staticmethod
    def init_thermal(
        n_nodes: int = N_NODES,
        dim: int = N_EDGE_MODES,
        beta: float = 1.0,
        *,
        key: jax.Array,
    ) -> "RelationalGraph":
        k1, k2, k3 = jax.random.split(key, 3)
        h_re = jax.random.normal(k1, (n_nodes, n_nodes, dim, dim))
        h_im = jax.random.normal(k2, (n_nodes, n_nodes, dim, dim))
        hamiltonian = 0.5 * (h_re + jnp.swapaxes(h_re, -1, -2))
        hamiltonian = hamiltonian + 0.5j * (
            h_im - jnp.swapaxes(h_im, -1, -2)
        )

        def gibbs_state(h_edge: jax.Array) -> jax.Array:
            evals, evecs = jnp.linalg.eigh(h_edge)
            shifted = evals - jnp.min(evals)
            weights = jnp.exp(-beta * shifted)
            weights = weights / jnp.sum(weights)
            return (evecs * weights[None, :]) @ _dagger(evecs)

        edge_rho = jax.vmap(jax.vmap(gibbs_state))(hamiltonian)
        edge_rho = 0.5 * (edge_rho + jnp.swapaxes(edge_rho, 0, 1))
        edge_rho = jax.vmap(jax.vmap(project_density_matrix))(edge_rho)
        node_pos = jax.random.normal(k3, (n_nodes, 3))
        adj = jnp.ones((n_nodes, n_nodes), dtype=jnp.float64) - jnp.eye(
            n_nodes, dtype=jnp.float64
        )
        return RelationalGraph(edge_rho, node_pos, adj, jnp.float64(0.0))


def _base_generator(dim: int, dtype: jnp.dtype) -> jax.Array:
    diagonal = jnp.diag(jnp.linspace(-1.0, 1.0, dim, dtype=jnp.float64))
    nearest = jnp.eye(dim, k=1, dtype=jnp.float64) + jnp.eye(
        dim, k=-1, dtype=jnp.float64
    )
    return (diagonal + 0.35 * nearest).astype(dtype)


@partial(jax.jit, static_argnames=("dt",))
def rg_flow_step(graph: RelationalGraph, dt: float = 0.01) -> RelationalGraph:
    """Apply a graph-coupled, noncommuting, positivity-preserving unitary step."""
    if dt <= 0.0:
        raise ValueError("dt must be positive")

    active = jnp.where(graph.adj > 0.0, 1.0, 0.0)
    degree = jnp.sum(active, axis=1)
    node_mean = jnp.einsum("ij,ijab->iab", active, graph.edge_rho)
    node_mean = node_mean / jnp.maximum(degree[:, None, None], 1.0)
    pair_feedback = 0.5 * (node_mean[:, None, :, :] + node_mean[None, :, :, :])

    delta_pos = graph.node_pos[:, None, :] - graph.node_pos[None, :, :]
    distance = jnp.linalg.norm(delta_pos, axis=-1)
    dim = graph.edge_rho.shape[-1]
    base = _base_generator(dim, graph.edge_rho.dtype)
    geometric = jnp.diag(jnp.linspace(-1.0, 1.0, dim)).astype(
        graph.edge_rho.dtype
    )
    h_edge = (
        base[None, None, :, :]
        + GRAPH_COUPLING * pair_feedback
        + GEOMETRIC_COUPLING * distance[:, :, None, None] * geometric
    )
    h_edge = 0.5 * (h_edge + _dagger(h_edge))

    evals, evecs = jnp.linalg.eigh(h_edge)
    phases = jnp.exp(-1j * BETA_RG * dt * evals)
    unitary = (evecs * phases[..., None, :]) @ _dagger(evecs)
    evolved = unitary @ graph.edge_rho @ _dagger(unitary)
    evolved = jax.vmap(jax.vmap(project_density_matrix))(evolved)
    evolved = jnp.where(active[:, :, None, None] > 0.0, evolved, graph.edge_rho)
    evolved = 0.5 * (evolved + jnp.swapaxes(evolved, 0, 1))
    evolved = jax.vmap(jax.vmap(project_density_matrix))(evolved)

    return RelationalGraph(
        edge_rho=evolved,
        node_pos=graph.node_pos,
        adj=graph.adj,
        rg_scale=graph.rg_scale + dt,
    )


class CosmologicalState(NamedTuple):
    a: jax.Array
    H_coord: jax.Array
    H_proper: jax.Array
    rho_matter: jax.Array
    rho_rad: jax.Array
    G_eff: jax.Array
    Lambda_eff: jax.Array
    Xi: jax.Array
    tau_proper: jax.Array
    omega: jax.Array


@jax.jit
def friedmann_bracket(state: CosmologicalState, k: float = 0.0) -> jax.Array:
    rho_total = state.rho_matter + state.rho_rad
    return (
        (8.0 * jnp.pi * state.G_eff / 3.0) * rho_total
        - k / jnp.maximum(state.a * state.a, CUTOFF_IR)
        + state.Lambda_eff / 3.0
        + state.Xi
    )


@jax.jit
def friedmann_ift(
    state: CosmologicalState,
    omega: jax.Array,
    k: float = 0.0,
) -> jax.Array:
    """Return physical H=(1/a) da/dtau; omega is a lapse, not a new source."""
    del omega  # The homogeneous lapse belongs to H_coord, not physical H.
    bracket = friedmann_bracket(state, k)
    return jnp.where(bracket >= 0.0, jnp.sqrt(jnp.maximum(bracket, 0.0)), jnp.nan)


@partial(jax.jit, static_argnames=("dt_coord",))
def cosmological_step(
    state: CosmologicalState,
    graph_old: RelationalGraph,
    graph_new: RelationalGraph,
    clock: InformationClock,
    dt_coord: float = 0.001,
    lambda_0: float = 1.0e-3,
    k: float = 0.0,
) -> tuple[CosmologicalState, InformationClock]:
    """Advance the graph clock and FLRW background with correct lapse relations."""
    omega_mat = information_frequency_matrix(
        graph_old.edge_rho, graph_new.edge_rho, dt_coord
    )
    new_clock = compute_information_clock(
        graph_old.edge_rho,
        graph_new.edge_rho,
        graph_new.adj,
        clock,
        dt_coord,
    )
    omega = new_clock.omega_global
    g_new = emergent_G_ift(graph_new.edge_rho, omega_mat, graph_new.adj)
    xi_new = corner_anomaly_ift(
        graph_old.edge_rho, graph_new.edge_rho, omega_mat, graph_new.adj
    )
    lambda_new = jnp.float64(lambda_0) + 8.0 * jnp.pi * xi_new

    dtau = omega * dt_coord
    a_new = state.a * jnp.exp(state.H_proper * dtau)
    scale_ratio = state.a / jnp.maximum(a_new, CUTOFF_IR)
    rho_m_new = state.rho_matter * scale_ratio**3
    rho_r_new = state.rho_rad * scale_ratio**4

    partial_state = CosmologicalState(
        a=a_new,
        H_coord=state.H_coord,
        H_proper=state.H_proper,
        rho_matter=rho_m_new,
        rho_rad=rho_r_new,
        G_eff=g_new,
        Lambda_eff=lambda_new,
        Xi=xi_new,
        tau_proper=new_clock.tau_proper,
        omega=omega,
    )
    h_proper = friedmann_ift(partial_state, omega, k)
    h_coord = omega * h_proper
    return partial_state._replace(H_proper=h_proper, H_coord=h_coord), new_clock


@jax.jit
def hubble_tension_correction(
    H_proper: jax.Array,
    omega_early: jax.Array,
    omega_late: jax.Array,
) -> jax.Array:
    """Coordinate-frame diagnostic only; a homogeneous lapse is not observable."""
    ratio = omega_early / jnp.maximum(omega_late, OMEGA_MIN)
    return H_proper * ratio


@jax.jit
def information_age_of_universe(clock: InformationClock) -> dict[str, jax.Array]:
    """Return coordinate and hypothesized information-clock durations."""
    return {
        "T_coord": clock.t_coord,
        "T_info": clock.tau_proper,
        "delta_T": clock.tau_proper - clock.t_coord,
        "ratio": clock.tau_proper / jnp.maximum(clock.t_coord, OMEGA_MIN),
    }


def evolve_ift_universe(
    n_steps: int = 600,
    dt_coord: float = 0.001,
    dt_rg: float = 0.01,
    beta_thermal: float = 1.2,
    lambda_0: float = 1.0e-3,
    k: float = 0.0,
    seed: int = 2024,
    n_nodes: int = N_NODES,
    dim: int = N_EDGE_MODES,
):
    """Run the stabilized prototype and fail closed on non-finite cosmology."""
    graph = RelationalGraph.init_thermal(
        n_nodes=n_nodes,
        dim=dim,
        beta=beta_thermal,
        key=jax.random.PRNGKey(seed),
    )
    clock = InformationClock.init(n_nodes=n_nodes)
    graph_old = graph
    graph = rg_flow_step(graph, dt=dt_rg)
    omega_mat = information_frequency_matrix(
        graph_old.edge_rho, graph.edge_rho, dt_coord
    )
    g0 = emergent_G_ift(graph.edge_rho, omega_mat, graph.adj)

    initial_partial = CosmologicalState(
        a=jnp.float64(1.0e-4),
        H_coord=jnp.float64(0.0),
        H_proper=jnp.float64(0.0),
        rho_matter=jnp.float64(PLANCK_DENSITY),
        rho_rad=jnp.float64(PLANCK_DENSITY),
        G_eff=g0,
        Lambda_eff=jnp.float64(lambda_0),
        Xi=jnp.float64(0.0),
        tau_proper=jnp.float64(0.0),
        omega=jnp.float64(0.0),
    )
    h0 = friedmann_ift(initial_partial, jnp.float64(0.0), k)
    state = initial_partial._replace(H_proper=h0, H_coord=jnp.float64(0.0))

    fields = (
        "t_coord",
        "tau_proper",
        "omega_global",
        "a",
        "H_coord",
        "H_proper",
        "G_eff",
        "Lambda_eff",
        "Xi",
        "dtau_dt",
        "phi_grav_mean",
        "phi_grav_std",
    )
    history = {name: [] for name in fields}

    for _ in range(n_steps):
        graph_old = graph
        graph = rg_flow_step(graph, dt=dt_rg)
        state, clock = cosmological_step(
            state,
            graph_old,
            graph,
            clock,
            dt_coord=dt_coord,
            lambda_0=lambda_0,
            k=k,
        )
        finite = all(
            bool(jnp.isfinite(value))
            for value in (
                state.a,
                state.H_coord,
                state.H_proper,
                state.G_eff,
                state.Lambda_eff,
                state.Xi,
            )
        )
        if not finite:
            raise FloatingPointError(
                "IFT-EGR evolution left the physical finite branch; inspect the "
                "Friedmann constraint and input scales."
            )

        phi = effective_gravitational_potential(clock)
        values = {
            "t_coord": clock.t_coord,
            "tau_proper": clock.tau_proper,
            "omega_global": clock.omega_global,
            "a": state.a,
            "H_coord": state.H_coord,
            "H_proper": state.H_proper,
            "G_eff": state.G_eff,
            "Lambda_eff": state.Lambda_eff,
            "Xi": state.Xi,
            "dtau_dt": clock.dtau_dt,
            "phi_grav_mean": jnp.mean(phi),
            "phi_grav_std": jnp.std(phi),
        }
        for name, value in values.items():
            history[name].append(float(value))

    return history, graph, state, clock


if __name__ == "__main__":
    run_history, _, final_state, final_clock = evolve_ift_universe(
        n_steps=100, n_nodes=8, dim=4
    )
    ages = information_age_of_universe(final_clock)
    print("IFT-EGR v0.2 stabilized research run")
    print(f"steps={len(run_history['a'])}")
    print(f"a_final={float(final_state.a):.8e}")
    print(f"H_proper_final={float(final_state.H_proper):.8e}")
    print(f"H_coord_final={float(final_state.H_coord):.8e}")
    print(f"omega_final={float(final_clock.omega_global):.8e}")
    print(f"tau_over_t={float(ages['ratio']):.8e}")
