[Setup]
AppName=Odoo 18
AppVersion=1.0
DefaultDirName={pf}\Odoo18
DefaultGroupName=Odoo18
OutputDir=.
OutputBaseFilename=Odoo_And_Requirement_installer
Compression=lzma
SolidCompression=yes
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

[Files]
; Include your odoo18.exe
; Source: "odoo.exe"; DestDir: "{app}"; Flags: ignoreversion
; Source: "pgsql\*"; DestDir: "{app}\pgsql"; Flags: recursesubdirs
; Source: "data\*"; DestDir: "{app}\data"; Flags: recursesubdirs

; Include Python installer
; Source: "python-3.10.11-amd64.exe"; DestDir: "{tmp}"; Flags: deleteafterinstall
Source: "visualstudio.exe"; DestDir: "{tmp}"; Flags: deleteafterinstall

Source: "requirements.txt"; DestDir: "{app}"; Flags: ignoreversion

[Run]
; Filename: "{tmp}\python-3.10.11-amd64.exe"; Parameters: "/quiet InstallAllUsers=1 PrependPath=1"; StatusMsg: "Installing Python 3.10.11..."; Flags: waituntilterminated; Check: NeedsPythonInstall
; Filename: "{tmp}\vs_BuildTools.exe"; Parameters: "--quiet --wait --norestart --add Microsoft.VisualStudio.Workload.MSBuildTools"; StatusMsg: "Installing Microsoft Build Tools..."; Flags: waituntilterminated; Check: InstallBuildTools
Filename: "{tmp}\visualstudio.exe"; Parameters: "--quiet --wait --norestart --add Microsoft.VisualStudio.Workload.MSBuildTools"; StatusMsg: "Installing Microsoft Build Tools..."; Flags: waituntilterminated
; Install Python dependencies using Python from PATH
Filename: "{cmd}";  Parameters: "/c python -m pip install -r ""{app}\requirements.txt""";StatusMsg: "Installing Python dependencies (visible)..."; Flags: waituntilterminated
; Run odoo18.exe after installation
; Filename: "{app}\odoo.exe"; Description: "Launch Odoo"; Flags: nowait postinstall skipifsilent

[Code]
procedure InitializeWizard();
begin
  // Check if Python is already installed
  if not RegKeyExists(HKEY_LOCAL_MACHINE, 'SOFTWARE\Python\PythonCore\3.10\InstallPath') then
  begin
    // Python is not installed, proceed with installation
  end
  else
  begin
    // Python is already installed, skip Python installation
    WizardForm.StatusLabel.Caption := 'Python 3.10.11 is already installed. Skipping installation.';
  end;
end;
// Check if Python is installed
function NeedsPythonInstall(): Boolean;
begin
  Result := not RegKeyExists(HKEY_LOCAL_MACHINE, 'SOFTWARE\Python\PythonCore\3.10\InstallPath');
end;

// Get Python Executable Path
function GetPythonExe(Param: String): String;
var
  PythonPath: String;
begin
  if RegQueryStringValue(HKEY_LOCAL_MACHINE, 'SOFTWARE\Python\PythonCore\3.10\InstallPath', '', PythonPath) then
    Result := PythonPath + 'python.exe'
  else
    Result := 'python';
end;

// Check if Microsoft Build Tools is already installed
function InstallBuildTools(): Boolean;
begin
  Result := not RegKeyExists(HKEY_LOCAL_MACHINE, 'SOFTWARE\Microsoft\VisualStudio\BuildTools');
end;

// Check if Restart is Required After Installing Build Tools
function NeedsRestart(): Boolean;
begin
  Result := (InstallBuildTools());
end;

// Check if Installation Continues After Restart
function AfterRestart(): Boolean;
begin
  Result := not NeedsRestart();
end;