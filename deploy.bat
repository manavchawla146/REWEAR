@echo off
echo ========================================
echo   Pet Pocket - App Engine Deployment
echo ========================================
echo.

echo [1/5] Checking Google Cloud CLI...
gcloud version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Google Cloud CLI not found. Please install it first.
    echo Visit: https://cloud.google.com/sdk/docs/install
    pause
    exit /b 1
)
echo ✓ Google Cloud CLI found

echo.
echo [2/5] Checking authentication...
gcloud auth list --filter=status:ACTIVE --format="value(account)" >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Not authenticated. Please run 'gcloud auth login'
    pause
    exit /b 1
)
echo ✓ Authenticated

echo.
echo [3/5] Copying production requirements...
copy requirements_appengine.txt requirements.txt >nul
echo ✓ Requirements updated

echo.
echo [4/5] Deploying to App Engine...
echo This may take several minutes...
gcloud app deploy --quiet
if %errorlevel% neq 0 (
    echo ERROR: Deployment failed. Check the logs above.
    pause
    exit /b 1
)

echo.
echo [5/5] Deployment completed successfully!
echo.
echo Your app is now available at:
gcloud app browse --no-launch-browser
echo.
echo To view logs: gcloud app logs tail -s default
echo.
pause
