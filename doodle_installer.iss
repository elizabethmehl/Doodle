[Setup]
AppName=Doodle
AppVersion=1.0
DefaultDirName={pf}\Doodle
DefaultGroupName=Doodle
OutputDir=installer
OutputBaseFilename=DoodleSetup
SetupIconFile=doodle_icon.ico
Compression=lzma
SolidCompression=yes
UninstallDisplayIcon={app}\doodle.exe

[Files]
Source: "dist\doodle.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "doodle_icon.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Doodle"; Filename: "{app}\doodle.exe"
Name: "{commondesktop}\Doodle"; Filename: "{app}\doodle.exe"

[Run]
Filename: "{app}\doodle.exe"; Description: "Launch Doodle"; Flags: nowait postinstall skipifsilent