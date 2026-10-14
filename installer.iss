; Installatieprogramma voor VR-viewer starter (Inno Setup 6)
; Dit bestand wordt automatisch gebruikt door GitHub (zie .github/workflows/build.yml).

#ifndef MyAppVersion
  #define MyAppVersion "1.0.0"
#endif

#define MyAppName "VR-viewer starter"
#define MyAppExe "VR-viewer-starter.exe"

[Setup]
AppId={{6B3E2F4A-9C1D-4E7B-8A5F-2D9C3B1E7A40}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher=Masterproef VR als leerhulpmiddel
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
; installeren zonder administratorrechten (werkt ook op schoollaptops)
PrivilegesRequired=lowest
OutputDir=output
OutputBaseFilename=VR-viewer-starter-setup
SetupIconFile=app.ico
UninstallDisplayIcon={app}\{#MyAppExe}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "dutch"; MessagesFile: "compiler:Languages\Dutch.isl"

[Tasks]
Name: "desktopicon"; Description: "Snelkoppeling op het bureaublad maken"; GroupDescription: "Extra:"

[Files]
Source: "dist\VR-viewer-starter\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs ignoreversion
Source: "app.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "voorbeeld\*"; DestDir: "{app}\voorbeeld"; Flags: recursesubdirs createallsubdirs ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExe}"
Name: "{group}\{#MyAppName} verwijderen"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExe}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExe}"; Description: "VR-viewer starter nu openen"; Flags: nowait postinstall skipifsilent
