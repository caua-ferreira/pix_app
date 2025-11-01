#define MyAppName "PixApp"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "CauTech"
#define MyAppExeName "PixApp.exe"

[Setup]
AppId={{52A3C89E-5F4E-4C84-A0B5-3C6C0C6EA246}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
OutputDir=installer
OutputBaseFilename=PixApp_Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "{%USERPROFILE}\Desktop\PixApp.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "perfis.json"; DestDir: "{app}"; Flags: ignoreversion
Source: "pix_config.json"; DestDir: "{app}"; Flags: ignoreversion
Source: "pix_gerados.json"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent