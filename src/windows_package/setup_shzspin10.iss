; SHZSpin10 Ultima Apex v14.5 — Inno Setup Script
; Jednolity instalator .exe dla Windows (Python wheel + skróty + dashboard)
; Wymaga: Inno Setup 6.x (https://jrsoftware.org/isinfo.php)
; Instrukcja: Otwórz w Inno Setup Compiler → Build → Output: SHZSpin10_Setup.exe

#define MyAppName "SHZSpin10 Ultima Apex"
#define MyAppVersion "14.5.0"
#define MyAppPublisher "SHZ Quantum Technologies"
#define MyAppURL "https://shz-quantum.tech/shzspin10"
#define MyWheel "shzspin10_ultima_apex-14.5.0-py3-none-any.whl"

[Setup]
AppId={{SHZSPIN10-ULTIMA-APEX-14-5-0-2026}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\SHZSpin10
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=README.md
OutputDir=.
OutputBaseFilename=SHZSpin10_UltimaApex_v145_Setup
SetupIconFile=.
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequiredOverridesAllowed=dialog
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "polish"; MessagesFile: "compiler:Languages\\Polish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
; Plik wheel (główny pakiet)
Source: "dist\{#MyWheel}"; DestDir: "{app}"; Flags: ignoreversion
; Pliki HTML dashboard (inline)
Source: "shzspin10\dashboard.html"; DestDir: "{app}"; Flags: ignoreversion
; README
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Start Menu
Name: "{group}\SHZSpin10 Dashboard"; Filename: "{cmd}"; Parameters: "/c shzspin10-dashboard"; IconFilename: "{app}\dashboard.html"
Name: "{group}\SHZSpin10 Menu (Console)"; Filename: "{cmd}"; Parameters: "/c shzspin10-menu"
Name: "{group}\SHZSpin10 Full Simulation"; Filename: "{cmd}"; Parameters: "/c shzspin10 -o %USERPROFILE%\Documents\SHZSpin10_report.json"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
; Desktop
Name: "{autodesktop}\SHZSpin10 Dashboard"; Filename: "{cmd}"; Parameters: "/c shzspin10-dashboard"; Tasks: desktopicon; IconFilename: "{app}\dashboard.html"

[Run]
; Instalacja wheel przez pip (wymaga Pythona w PATH)
Filename: "{cmd}"; Parameters: "/c echo Checking Python... && python --version && pip install --no-index --find-links=""{app}"" shzspin10_ultima_apex-14.5.0-py3-none-any.whl || echo ERROR: Install failed. Ensure Python 3.9+ is installed and in PATH. && pause"; StatusMsg: "Installing SHZSpin10 Python package..."; Flags: runhidden
; Post-install info
Filename: "{cmd}"; Parameters: "/c echo. && echo === SHZSpin10 Ultima Apex v14.5 Installed === && echo Commands: shzspin10 ^| shzspin10-menu ^| shzspin10-dashboard && echo. && pause"; Flags: postinstall skipifsilent

[UninstallRun]
; Odinstalowanie pakietu pip
Filename: "{cmd}"; Parameters: "/c pip uninstall -y shzspin10-ultima-apex"; Flags: runhidden

[Code]
function InitializeSetup(): Boolean;
var
  ErrorCode: Integer;
begin
  Result := true;
  
  ; Sprawdzenie czy Python jest zainstalowany
  if not Exec('python', '--version', '', SW_HIDE, ewWaitUntilTerminated, ErrorCode) then
  begin
    MsgBox('Python 3.9+ is not detected in PATH.' + #13#10 + 
           'Please install Python from https://python.org/downloads/' + #13#10 +
           'and ensure "Add Python to PATH" is checked during installation.', 
           mbCriticalError, MB_OK);
    Result := false;
    ShellExec('open', 'https://python.org/downloads/', '', '', SW_SHOWNORMAL, ErrorCode);
  end;
end;
