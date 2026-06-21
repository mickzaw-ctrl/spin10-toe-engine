# SHZSpin10 Ultima Apex v14.5 — Windows Installation Guide

## Method 1: Simplest (wheel + pip)

**Requirements:** Python 3.9+ with pip (https://python.org/downloads/)

```cmd
:: Pobierz projekt (git clone lub zip)
:: Rozpakuj, otwórz CMD w katalogu projektu

pip install dist\shzspin10_ultima_apex-14.5.0-py3-none-any.whl

:: Gotowe! Teraz możesz używać komend:
shzspin10 -o raport.json
shzspin10-menu
shzspin10-dashboard
python -m shzspin10
```

## Method 2: Batch Installer (install_windows.bat)

1. Make sure Python 3.9+ is installed and in PATH.
2. Double-click `install_windows.bat`.
3. The installer will automatically:
   - Check Python version
   - Install the package from wheel (offline or online)
   - Create a desktop shortcut: "SHZSpin10 Dashboard"

## Method 3: PowerShell Installer (install_windows.ps1)

1. Open PowerShell (as administrator or user).
2. Set execution policy if needed:
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
   ```
3. Run:
   ```powershell
   .\install_windows.ps1
   ```

## Method 4: Inno Setup (.exe installer)

**Requires:** Inno Setup 6.x (https://jrsoftware.org/isinfo.php)

1. Install Inno Setup.
2. Open `setup_shzspin10.iss` in Inno Setup Compiler.
3. Click **Build → Compile** (Ctrl+F9).
4. Output: `SHZSpin10_UltimaApex_v145_Setup.exe` — run on any Windows machine.

Installer .exe features:
- Auto-detection of Python (redirects to python.org if missing)
- Offline wheel installation (no internet required)
- Start Menu and desktop shortcuts
- Uninstall via Control Panel

## Method 5: Standalone EXE (PyInstaller)

**Requires:** PyInstaller (pip install pyinstaller) na Windows

```cmd
pip install pyinstaller
python build_windows.py
:: Wynik: dist/SHZSpin10.exe (standalone, nie wymaga Pythona na docelowym PC!)
```

Uwaga: PyInstaller na Linux tworzy ELF, nie PE. Build .exe musi odbyć się na Windows.

## Komendy po instalacji

| Komenda | Opis |
|---------|------|
| `shzspin10` | Pełna symulacja + dashboard konsolowy |
| `shzspin10 -o raport.json` | Symulacja + zapis JSON |
| `shzspin10-menu` | Interaktywne menu (8 opcji) |
| `shzspin10-dashboard` | Otwórz HTML dashboard w przeglądarce |
| `python -m shzspin10 --no-dashboard` | Symulacja bez wypisywania raportu |

## API Python

```python
from shzspin10 import SHZSpin10UltimaApex

engine = SHZSpin10UltimaApex()
report = engine.run_ultima_simulation()
engine.display_ultima_dashboard(report)
```

## Pliki wynikowe

- `ultima_big_bang_simulation.png` — 4-panelowy wykres kosmologiczny
- `raport.json` (lub podana nazwa) — pełna synteza JSON z 16 sekcjami

## Troubleshooting

**"Python is not recognized"**
- Zainstaluj Python z https://python.org
- Podczas instalacji zaznacz ☑ **Add Python to PATH**

**"pip is not recognized"**
- W CMD/PowerShell: `python -m ensurepip --upgrade`
- Lub zainstaluj pip: https://pip.pypa.io/en/stable/installation/

**"No module named 'numpy'"**
- `pip install numpy scipy matplotlib`
- Lub po prostu: `pip install dist\shzspin10_ultima_apex-14.5.0-py3-none-any.whl` (zależności są w wheel)
