#define MyAppName "Xbox Audio Rumble Studio"
#define MyAppVersion "1.1.0"
#define MyAppPublisher "Huyenbk97"
#define MyAppExeName "XboxAudioRumbleStudio.exe"

[Setup]
AppId={{E68BC201-9F31-4A59-B87A-E5E3D8110DF2}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=.
OutputBaseFilename=XboxAudioRumbleStudio-Setup-v1.1.0
SetupIconFile=app.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesInstallIn64BitMode=x64compatible
UninstallDisplayIcon={app}\{#MyAppExeName}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "XboxAudioRumbleStudio.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "XboxAudioRumbleStudio.settings.json"; DestDir: "{app}"; Flags: ignoreversion onlyifdoesntexist
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "app.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\app.ico"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\app.ico"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
