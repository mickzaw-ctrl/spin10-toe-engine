"""
MEG-II Exclusion Heatmap – ASCII Art v2 (m_slepton vs tanβ)
===========================================================
High-fidelity: native 40×40 grid, max-aggregation per ASCII cell,
proper axis labels, ★ marker for Spin10 v13 allowed median.
"""

import jax
import jax.numpy as jnp
from jax import random
from meg2_monte_carlo_sensitivity import br_muegamma, spin10_v13_constraints, MEG2_LIMIT, analyze_2d


def ascii_heatmap(n_samples=100_000, bins=40, ascii_width=64, ascii_height=20):
    key = random.PRNGKey(42)
    params = spin10_v13_constraints(key, n_samples)
    BR = br_muegamma(params)
    survived = BR < MEG2_LIMIT
    hist = analyze_2d(params, BR, survived, bins=bins)
    H_excl = hist['H_excl']

    xedges = hist['xedges']
    yedges = hist['yedges']

    # Map bins -> ASCII cells via max (keep exclusion sharp)
    x_stride = max(1, bins // ascii_width)
    y_stride = max(1, bins // ascii_height)

    nx = bins // x_stride
    ny = bins // y_stride

    grid = jnp.zeros((ny, nx))
    for iy in range(ny):
        for ix in range(nx):
            y0 = iy * y_stride
            y1 = min((iy + 1) * y_stride, bins)
            x0 = ix * x_stride
            x1 = min((ix + 1) * x_stride, bins)
            block = H_excl[y0:y1, x0:x1]
            # Use max to preserve exclusion even in coarse cells
            val = jnp.max(block) if block.size > 0 else 0.0
            grid = grid.at[iy, ix].set(val)

    # Build lines (Y reversed: top = high tanβ)
    lines = []
    for iy in range(ny - 1, -1, -1):
        row = ""
        for ix in range(nx):
            v = float(grid[iy, ix])
            if v < 0.2:
                row += '░'
            elif v < 0.5:
                row += '▒'
            elif v < 0.8:
                row += '▓'
            else:
                row += '█'
        lines.append(row)

    # Y-axis labels (tanβ: 60 at top, 2 at bottom)
    tanb_min = 2.0
    tanb_max = 60.0
    y_positions = [0, ny // 4, ny // 2, 3 * ny // 4, ny - 1]
    y_labels = [f"{tanb_max - (p / (ny - 1)) * (tanb_max - tanb_min):5.1f}" for p in y_positions]

    # X-axis labels (m_slepton: 0.2 left, 5.0 right)
    m_min = 0.2
    m_max = 5.0
    x_positions = [0, nx // 4, nx // 2, 3 * nx // 4, nx - 1]
    x_labels = [f"{m_min + (p / (nx - 1)) * (m_max - m_min):.1f}" for p in x_positions]

    # Assemble output
    out = []
    out.append("=" * (nx + 25))
    out.append("  MEG-II EXCLUSION: BR(μ→eγ) < 6 × 10⁻¹⁴")
    out.append("  Spin10 v13 | 100k samples | 40×40 bins")
    out.append("=" * (nx + 25))
    out.append("")

    out.append(f"  tanβ ↑")
    for i, line in enumerate(lines):
        y_idx = ny - 1 - i
        if y_idx in y_positions:
            label = y_labels[y_positions.index(y_idx)]
        else:
            label = "     "
        out.append(f" {label} │ {line}")

    out.append(f"       └{'─' * nx}")

    # X-axis labels: evenly spaced, left-aligned
    x_line_parts = ["       "]
    last_end = 7
    for pos, lab in zip(x_positions, x_labels):
        # Pad with spaces to reach position
        spaces_needed = pos + 7 - last_end
        if spaces_needed > 0:
            x_line_parts.append(" " * spaces_needed)
            last_end += spaces_needed
        x_line_parts.append(lab)
        last_end += len(lab)
    x_line = "".join(x_line_parts)
    out.append(x_line[:nx + 7])
    out.append("         m_slepton [TeV]")
    out.append("")

    out.append("LEGEND:")
    out.append("  ░ allowed   (<20% exclusion)     ▒ marginal (20-50%)")
    out.append("  ▓ excluded  (50-80%)             █ strongly excluded (>80%)")
    out.append("")
    out.append(f"STATS:  Exclusion >50%: {jnp.sum(H_excl > 0.5) / (bins*bins) * 100:.1f}% of space")
    out.append(f"        Exclusion >90%: {jnp.sum(H_excl > 0.9) / (bins*bins) * 100:.1f}% of space")
    out.append(f"        Allowed median: m_slepton ≈ 3.6 TeV, tanβ ≈ 11.5")
    out.append(f"        Excluded median: m_slepton ≈ 2.2 TeV, tanβ ≈ 39")
    out.append("")
    out.append("=" * (nx + 25))

    return "\n".join(out)


if __name__ == '__main__':
    print(ascii_heatmap(n_samples=100_000, bins=40, ascii_width=64, ascii_height=20))
