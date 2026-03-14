; KIF — Kio Image Format Installer
; Copyright (c) 2026 KibaOfficial
; https://opensource.org/licenses/MIT

#define MyAppName "KIF"
#define MyAppVersion "2.1.0"
#define MyAppPublisher "KibaOfficial"
#define MyAppURL "https://github.com/kibaofficial/kio-image-format"
#define MyAppExeName "kif.exe"

[Setup]
AppId={{B4F2A1C3-7E8D-4F2A-9B1E-3C5D6E7F8A9B}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\KIF
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=..\LICENSE
OutputDir=..\dist
OutputBaseFilename=kif-{#MyAppVersion}-setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64compatible
UninstallDisplayName=KIF - Kio Image Format
UninstallDisplayIcon={app}\kif.exe

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "addtopath"; Description: "Add KIF to PATH (recommended)"; GroupDescription: "System Integration"

[Files]
Source: "..\dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\KIF CLI"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Uninstall KIF"; Filename: "{uninstallexe}"

[Registry]
; Add to PATH
Root: HKLM; Subkey: "SYSTEM\CurrentControlSet\Control\Session Manager\Environment"; \
    ValueType: expandsz; ValueName: "Path"; \
    ValueData: "{olddata};{app}"; \
    Tasks: addtopath; \
    Check: NeedsAddPath(ExpandConstant('{app}'))

[Code]
function NeedsAddPath(Param: string): boolean;
var
  OrigPath: string;
begin
  if not RegQueryStringValue(
    HKEY_LOCAL_MACHINE,
    'SYSTEM\CurrentControlSet\Control\Session Manager\Environment',
    'Path', OrigPath)
  then begin
    Result := True;
    exit;
  end;
  Result := Pos(';' + Param + ';', ';' + OrigPath + ';') = 0;
end;

[Run]
Filename: "{cmd}"; Parameters: "/C refreshenv"; \
    Flags: runhidden; \
    StatusMsg: "Updating PATH...";