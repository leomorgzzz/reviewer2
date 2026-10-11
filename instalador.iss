; Instalador para Windows (Inno Setup). Lo compila GitHub Actions:
;   iscc /DVersion=1.3 instalador.iss   (después de pyinstaller --onedir)
; Se instala solo para el usuario, sin pedir permisos de administrador. El
; acceso directo abre el juego en la consola clásica (conhost), donde el juego
; puede ajustar la fuente y los colores; Windows Terminal no lo permite.

#ifndef Version
  #define Version "0.0"
#endif

[Setup]
AppId={{536CD333-C142-50AC-BFB7-C55A9A24A1F1}
AppName=Reviewer 2
AppVersion={#Version}
AppPublisher=leomorgzzz
AppPublisherURL=https://github.com/leomorgzzz/reviewer2
DefaultDirName={autopf}\Reviewer 2
DefaultGroupName=Reviewer 2
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
OutputDir=.
OutputBaseFilename=Reviewer2-Windows-Setup
SetupIconFile=icono.ico
UninstallDisplayIcon={app}\Reviewer2.exe
WizardStyle=modern
Compression=lzma2
SolidCompression=yes

[Languages]
Name: "es"; MessagesFile: "compiler:Languages\Spanish.isl"
Name: "en"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "escritorio"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "dist\Reviewer2\*"; DestDir: "{app}"; Flags: recursesubdirs ignoreversion

[InstallDelete]
; versiones anteriores se llamaban Revisor 2: se quitan el ejecutable y los accesos viejos
Type: files; Name: "{app}\Revisor2.exe"
Type: files; Name: "{autoprograms}\Revisor 2.lnk"
Type: files; Name: "{autodesktop}\Revisor 2.lnk"

[Icons]
Name: "{autoprograms}\Reviewer 2"; Filename: "{sys}\conhost.exe"; Parameters: """{app}\Reviewer2.exe"""; WorkingDir: "{app}"; IconFilename: "{app}\Reviewer2.exe"
Name: "{autodesktop}\Reviewer 2"; Filename: "{sys}\conhost.exe"; Parameters: """{app}\Reviewer2.exe"""; WorkingDir: "{app}"; IconFilename: "{app}\Reviewer2.exe"; Tasks: escritorio

[Run]
Filename: "{sys}\conhost.exe"; Parameters: """{app}\Reviewer2.exe"""; WorkingDir: "{app}"; Description: "{cm:LaunchProgram,Reviewer 2}"; Flags: nowait postinstall skipifsilent
; al actualizar desde el juego (instalador en modo silencioso) se vuelve a abrir solo
Filename: "{sys}\conhost.exe"; Parameters: """{app}\Reviewer2.exe"""; WorkingDir: "{app}"; Flags: nowait; Check: WizardSilent
