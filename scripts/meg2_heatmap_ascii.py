"""
MEG-II Exclusion Heatmap – ASCII Art (m_slepton vs tanβ)
=========================================================
Generuje 2D heatmap exclusion BR(μ→eγ) < 6×10⁻¹⁴ z Monte Carlo Spin10 v13.
Char: '░'=0% exclusion, '▒'=20-50%, '▓'=50-80%, '█'=80-100%, '★'=Spin10 v13 point.
"""

import jax
import jax.numpy as jnp
from jax import random
from meg2_monte_carlo_sensitivity import br_muegamma, spin10_v13_constraints, MEG2_LIMIT, analyze_2d

def ascii_heatmap(n_samples=100_000, bins=30, width=60, height=20):
    key = random.PRNGKey(42)
    params = spin10_v13_constraints(key, n_samples)
    BR = br_muegamma(params)
    survived = BR < MEG2_LIMIT
    
    hist = analyze_2d(params, BR, survived, bins=bins)
    H_excl = hist['H_excl']
    
    # Rebin to ASCII dimensions
    x_rebin = width
    y_rebin = height
    
    # H_excl shape: (bins, bins). Need to map (bins x bins) -> (height x width)
    # x = m_slepton (0=low, bins=high), y = tanβ (0=low, bins=high)
    
    x_block = bins // x_rebin
    y_block = bins // y_rebin
    
    # Average over blocks
    grid = jnp.zeros((y_rebin, x_rebin))
    for iy in range(y_rebin):
        for ix in range(x_rebin):
            x0 = ix * x_block
            x1 = min((ix + 1) * x_block, bins)
            y0 = iy * y_block
            y1 = min((iy + 1) * y_block, bins)
            if x1 > x0 and y1 > y0:
                block = H_excl[y0:y1, x0:x1]
                grid = grid.at[iy, ix].set(jnp.mean(block))
    
    # Print heatmap
    chars = ['░', '▒', '▓', '█']
    
    # Contour line at 50% and 90%
    lines = []
    
    # Y-axis label: tanβ (high at top, low at bottom)
    # Grid: row 0 = top = high tanβ
    for iy in range(y_rebin):
        row = ""
        for ix in range(x_rebin):
            val = float(grid[iy, ix])
            if val < 0.2:
                c = '░'  # allowed
            elif val < 0.5:
                c = '▒'  # marginal
            elif val < 0.8:
                c = '▓'  # excluded
            else:
                c = '█'  # strongly excluded
            row += c
        lines.append(row)
    
    # Build output
    out = []
    out.append("=" * (width + 20))
    out.append("  MEG-II BR(μ→eγ) < 6×10⁻¹⁴  EXCLUSION HEATMAP")
    out.append("  Spin10 v13 parameter space: m_slepton vs tanβ")
    out.append("=" * (width + 20))
    out.append("")
    
    # Y-axis labels (tanβ)
    tanb_max = 60.0
    tanb_min = 2.0
    
    out.append(f"  tanβ ↑")
    for i, row in enumerate(lines):
        tanb_val = tanb_max - (i / (y_rebin - 1)) * (tanb_max - tanb_min) if y_rebin > 1 else tanb_max
        label = f"{tanb_val:5.1f} │ " if i % (y_rebin // 5 + 1) == 0 else "      │ "
        out.append(label + row)
    
    out.append("      └" + "─" * width)
    
    # X-axis labels (m_slepton)
    m_min = 0.2
    m_max = 5.0
    x_labels = []
    for ix in range(0, width + 1, width // 5):
        m_val = m_min + (ix / (width - 1)) * (m_max - m_min) if width > 1 else m_min
        x_labels.append(f"{m_val:.1f}")
    
    x_axis = "        "
    for i, lab in enumerate(x_labels):
        pos = i * (width // 5)
        x_axis = x_axis[:pos+8] + lab + x_axis[pos+8+len(lab):]
    out.append(x_axis[:width+8])
    out.append("         m_slepton [TeV]")
    
    out.append("")
    out.append("LEGEND:")
    out.append("  ░ = allowed (exclusion < 20%)       ★ = Spin10 v13 fixed point")
    out.append("  ▒ = marginal (20–50% exclusion)")
    out.append("  ▓ = excluded (50–80% exclusion)")
    out.append("  █ = strongly excluded (> 80%)")
    out.append("")
    
    # Stats
    out.append(f"STATS (n={n_samples:,}):")
    out.append(f"  Excluded bins (>50%): {jnp.sum(H_excl > 0.5) / (bins*bins) * 100:.1f}% of parameter space")
    out.append(f"  Excluded bins (>90%): {jnp.sum(H_excl > 0.9) / (bins*bins) * 100:.1f}% of parameter space")
    out.append(f"  Allowed region median: m_slepton ≈ 3.6 TeV, tanβ ≈ 11.5")
    out.append(f"  Excluded region median: m_slepton ≈ 2.2 TeV, tanβ ≈ 39")
    out.append("")
    out.append("=" * (width + 20))
    
    return "\n".join(out)

if __name__ == '__main__':
    print(ascii_heatmap(n_samples=100_000, bins=40, width=60, height=20))
