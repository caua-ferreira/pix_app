; Inno Setup script template for PixApp
; Adjust AppName, AppVersion, DefaultDirName and files as needed

[Setup]
AppName=PixApp
AppVersion=1.0
DefaultDirName={pf}\PixApp
DefaultGroupName=PixApp
OutputBaseFilename=PixApp_Installer
Compression=lzma
SolidCompression=yes
; Use the generated application icon as setup icon (optional)
SetupIconFile=pixapp.ico

[Files]
; Include all files from dist\PixApp and the application icon
Source: "{#SourcePath}\dist\PixApp\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "{#SourcePath}\pixapp.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\PixApp"; Filename: "{app}\PixApp.exe"; IconFilename: "{app}\pixapp.ico"

[Run]
Filename: "{app}\PixApp.exe"; Description: "Iniciar PixApp"; Flags: nowait postinstall skipifsilent
