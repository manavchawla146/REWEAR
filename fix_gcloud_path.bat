@echo off
echo ========================================
echo   Add Google Cloud CLI to System PATH
echo ========================================
echo.

REM Check if gcloud is already in PATH
gcloud version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ Google Cloud CLI is already in PATH
    gcloud version
    pause
    exit /b 0
)

REM Check if gcloud exists in default location
set GCLOUD_BIN="C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin"
if not exist %GCLOUD_BIN%\gcloud.cmd (
    echo ERROR: Google Cloud CLI not found at expected location: %GCLOUD_BIN%
    echo Please install Google Cloud CLI first from:
    echo https://cloud.google.com/sdk/docs/install
    pause
    exit /b 1
)

echo Found Google Cloud CLI at: %GCLOUD_BIN%
echo.
echo Adding to system PATH...

REM Add to current session PATH
set PATH=%PATH%;%GCLOUD_BIN%

REM Add to user PATH permanently (requires PowerShell)
powershell -Command "$env:PATH = [Environment]::GetEnvironmentVariable('PATH','User'); if ($env:PATH -notlike '*Google*Cloud*SDK*') { [Environment]::SetEnvironmentVariable('PATH', $env:PATH + ';C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin', 'User') }"

echo.
echo ✓ Google Cloud CLI added to PATH
echo.
echo Testing gcloud command...
gcloud version

if %errorlevel% equ 0 (
    echo.
    echo ✓ Success! Google Cloud CLI is now available.
    echo You may need to restart your PowerShell/Command Prompt for the PATH changes to take effect.
    echo.
    echo You can now run: .\deploy_compute_engine.bat
) else (
    echo.
    echo ⚠ Warning: PATH update may require a restart.
    echo Please restart your PowerShell/Command Prompt and try again.
    echo Or use: .\deploy_compute_engine_fixed.bat
)

echo.
pause
