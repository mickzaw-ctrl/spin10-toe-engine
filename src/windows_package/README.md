# SHZSpin10 Ultima Apex v14.5 — Windows Distribution Package

**Version:** 14.5.0 — ULTIMA COSMOS UNIFIED  
**Engine:** SHZSpin10 v14.5-ULTIMA COSMOS UNIFIED  
**Author:** Michal Slusarczyk / SHZ Quantum Technologies  

---

## What's New in v14.5

This is the first full **distributable Windows package** of the SHZSpin10 engine — a unified monolithic Python package (`shzspin10`) that integrates all engine generations into a single installable wheel.

### Integrated laboratories

| # | Laboratory | Key capability |
|---|-----------|----------------|
| 1 | **Base Engine v13.6** | Relational graph, Monte Carlo |
| 2 | **Ultima Frontiers** | Black Hole Page Curve, Yukawa Flavour, E8×E8, TQEC |
| 3 | **Enterprise HPC** | GPU batch relaxation, Quantum Bridge (Qiskit), SciML Digital Twin |
| 4 | **Physics Apex** | LQG Spin Foam EPRL (γ=0.274), SM constants RGE top-down |
| 5 | **Cloud SaaS API** | 6 microservices: Gauge Relaxation, Holographic RW, RGE Unification, Mukhanov-Sasaki, MERA Entropy, AI Equation Discovery |
| 6 | **Cosmology** | Starobinsky R² inflation, FRW evolution, CMB TT power spectrum, matter P(k) BBKS |

---

## Installation

### Method 1: pip (recommended)

```cmd
pip install shzspin10_ultima_apex-14.5.0-py3-none-any.whl
```

### Method 2: Batch installer (Windows)

```
install_windows.bat
```

### Method 3: PowerShell

```powershell
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
.\install_windows.ps1
```

### Method 4: Inno Setup .exe installer

Open `setup_shzspin10.iss` in Inno Setup Compiler → Build → Compile  
Output: `SHZSpin10_UltimaApex_v145_Setup.exe`

---

## Usage

### Python API

```python
from shzspin10 import SHZSpin10UltimaApex

engine = SHZSpin10UltimaApex()
report = engine.run_ultima_simulation()
engine.display_ultima_dashboard(report)
```

### CLI

```bash
shzspin10 -o report.json
shzspin10 --no-dashboard -o report.json
python -m shzspin10
```

### Interactive console menu

```bash
shzspin10-menu
```

### HTML dashboard

```bash
shzspin10-dashboard
```

### Streamlit web dashboard

```bash
pip install streamlit
streamlit run shzspin10/streamlit_dashboard.py
```

---

## Output files

| File | Description |
|------|-------------|
| `ultima_big_bang_simulation.png` | 4-panel cosmology plot: a(t), T(z), CMB TT, P(k) |
| `shz_spin10_v14_ultima.json` | Full JSON synthesis report — all laboratory results |

---

## Requirements

```
numpy >= 1.21.0
scipy >= 1.7.0
matplotlib >= 3.4.0
streamlit >= 1.20.0  # optional, for web dashboard
```

Python 3.9+ required.

---

## Package structure

```
shzspin10/
├── __init__.py              # Package entry point, version 14.5.0
├── __main__.py              # python -m shzspin10 entry point
├── engine.py                # Unified monolithic engine (all laboratories)
├── cli.py                   # CLI: shzspin10, shzspin10-dashboard
├── menu.py                  # Interactive console menu: shzspin10-menu
├── streamlit_dashboard.py   # Streamlit web dashboard
└── dashboard.html           # Standalone HTML dashboard
```

---

## Version history (engine generations)

| Version | Codename | Key additions |
|---------|----------|---------------|
| **v14.5** ★ | **ULTIMA COSMOS UNIFIED** | First Windows distributable package, full cosmology (FRW+CMB), unified monolithic wheel |
| v13.0-PRO | Physics Apex | LQG Spin Foams (EPRL), SM constants top-down, Quantum Core JAX+gRPC+Ray |
| v12.0-ULTIMA | Ultimate Frontiers | MERA AdS/CFT, AI equation discovery, Black Hole Page Curve |
| v10.0-PRO | Enterprise | GPU/CUDA, Quantum Bridge QAOA/VQE, SciML Digital Twins |
| v8.0 | Core | 8 physics modules, 38 predictions, 35/35 tests |

---

## Repository

Main engine: [github.com/mickzaw-ctrl/spin10-toe-engine](https://github.com/mickzaw-ctrl/spin10-toe-engine)  
Live site: [mickzaw-ctrl.github.io/spin10-toe-engine](https://mickzaw-ctrl.github.io/spin10-toe-engine/)

---

*Last updated: 2026-06-21 · Package version: 14.5.0 · Engine: v14.5-ULTIMA COSMOS UNIFIED*
