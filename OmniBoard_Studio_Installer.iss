[Setup]
AppId={{2A6A9E8F-4B1C-4D3E-8F9A-1B2C3D4E5F6A}
AppName=OmniBoard Studio
AppVersion=Latest
DefaultDirName={localappdata}\OmniBoard Studio
DefaultGroupName=OmniBoard Studio
PrivilegesRequired=lowest
OutputDir=.
OutputBaseFilename=OmniBoard_Online_Installer
SolidCompression=yes
DisableDirPage=no
UninstallDisplayIcon={app}\OmniBoard Studio.exe
SetupIconFile=resources\images\Appicon.ico

[Tasks]
Name: "desctopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Icons]
Name: "{group}\Omniboard Studio"; Filename: "{app}\Omniboard Studio.exe"; WorkingDir: "{app}"
Name: "{group}\Uninstall OmniBoard Studio"; Filename: "{uninstallexe}"
Name: "{autodesktop}\OmniBoard Studio"; Filename: "{app}\Omniboard Studio.exe"; WorkingDir: "{app}"; Tasks: desctopicon

[Run]
; 1. Normal Installation (Interactive)
Filename: "{app}\OmniBoard Studio.exe"; Description: "Launch OmniBoard Studio"; Flags: nowait postinstall skipifsilent

; 2. Update Installation (Silent)
Filename: "{app}\OmniBoard Studio.exe"; Flags: nowait skipifnotsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}"

[Code]
var
  DownloadPage: TDownloadWizardPage;
  InstallSuccessful: Boolean;

procedure InitializeWizard;
begin
  DownloadPage := CreateDownloadPage('Downloading OmniBoard Studio Update', 'Please wait...', nil);
end;

function PrepareToInstall(var NeedsRestart: Boolean): String;
var
  ResultCode: Integer;
begin
  Result := ''; // An empty string tells the installer to proceed

  // 1. Force kill the app before any files are locked
  Exec(ExpandConstant('{sys}\taskkill.exe'), '/F /IM "OmniBoard Studio.exe"', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  // Optional: Kill python if running from source during development
  Exec(ExpandConstant('{sys}\taskkill.exe'), '/F /IM "python.exe" /FI "WINDOWTITLE eq OmniBoard Studio*"', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  Sleep(2000); 

  // 2. Setup download
  DownloadPage.Clear;
  DownloadPage.Add('https://github.com/Kotoad/APP_PyQt/releases/latest/download/OmniBoard_Studio_Windows.zip', 'OmniBoard.zip', '');

  // 3. Execute download safely
  if not WizardSilent then DownloadPage.Show;
  try
    try
      DownloadPage.Download;
    except
      // Catches network errors so the silent installer doesn't crash violently
      Result := 'Download failed. Please check your connection or firewall.';
      Exit;
    end;
  finally
    if not WizardSilent then DownloadPage.Hide;
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  ResultCode: Integer;
begin
  // 4. Extract only when the installer engine is actually ready to write files
  if CurStep = ssInstall then begin
    ForceDirectories(ExpandConstant('{app}'));
    
    Exec(ExpandConstant('{sys}\tar.exe'), 
         '-xf "' + ExpandConstant('{tmp}\OmniBoard.zip') + '" -C "' + ExpandConstant('{app}') + '"', 
         '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
         
    if ResultCode = 0 then 
      InstallSuccessful := True
    else
      Log('Extraction failed with tar exit code: ' + IntToStr(ResultCode));
  end;
end;

procedure DeinitializeSetup();
var
  ErrorCode: Integer;
begin
  if InstallSuccessful then begin
    Exec('cmd.exe', '/c ping 127.0.0.1 -n 3 > nul & del "' + ExpandConstant('{srcexe}') + '"', '', SW_HIDE, ewNoWait, ErrorCode);
  end;
end;