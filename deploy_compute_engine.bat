@echo off
echo =========================================
echo   Pet Pocket - Compute Engine Deployment
echo =========================================
echo.

echo [1/6] Checking Google Cloud CLI...
gcloud version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Google Cloud CLI not found. Please install it first.
    echo Visit: https://cloud.google.com/sdk/docs/install
    pause
    exit /b 1
)
echo ✓ Google Cloud CLI found

echo.
echo [2/6] Checking authentication...
gcloud auth list --filter=status:ACTIVE --format="value(account)" >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Not authenticated. Please run 'gcloud auth login'
    pause
    exit /b 1
)
echo ✓ Authenticated

echo.
echo [3/6] Creating project and enabling APIs...
set /p PROJECT_ID="Enter your project ID (e.g., pet-pocket-compute): "
gcloud projects create %PROJECT_ID% --name="Pet Pocket"
gcloud config set project %PROJECT_ID%
gcloud services enable compute.googleapis.com

echo.
echo [4/6] Creating VM instance (e2-micro - Free Tier)...
echo This will create an e2-micro instance in us-west1-b...
gcloud compute instances create pet-pocket-vm ^
    --zone=us-west1-b ^
    --machine-type=e2-micro ^
    --network-tier=STANDARD ^
    --maintenance-policy=MIGRATE ^
    --service-account=default ^
    --scopes=https://www.googleapis.com/auth/cloud-platform ^
    --image-family=ubuntu-2004-lts ^
    --image-project=ubuntu-os-cloud ^
    --boot-disk-size=30GB ^
    --boot-disk-type=pd-standard ^
    --boot-disk-device-name=pet-pocket-vm ^
    --no-shielded-secure-boot ^
    --shielded-vtpm ^
    --shielded-integrity-monitoring ^
    --reservation-affinity=any

if %errorlevel% neq 0 (
    echo ERROR: Failed to create VM instance
    pause
    exit /b 1
)

echo.
echo [5/6] Creating firewall rules...
gcloud compute firewall-rules create allow-http-pet-pocket ^
    --allow tcp:80 ^
    --source-ranges 0.0.0.0/0 ^
    --description "Allow HTTP traffic for Pet Pocket"

gcloud compute firewall-rules create allow-https-pet-pocket ^
    --allow tcp:443 ^
    --source-ranges 0.0.0.0/0 ^
    --description "Allow HTTPS traffic for Pet Pocket"

echo.
echo [6/6] Getting VM information...
echo Getting external IP address...
for /f %%i in ('gcloud compute instances describe pet-pocket-vm --zone=us-west1-b --format="get(networkInterfaces[0].accessConfigs[0].natIP)"') do set EXTERNAL_IP=%%i

echo.
echo ========================================
echo   Deployment Completed Successfully!
echo ========================================
echo.
echo VM Instance: pet-pocket-vm
echo Zone: us-west1-b
echo Machine Type: e2-micro (Free Tier)
echo External IP: %EXTERNAL_IP%
echo.
echo Next Steps:
echo 1. Connect to your VM:
echo    gcloud compute ssh pet-pocket-vm --zone=us-west1-b
echo.
echo 2. Upload your application files to the VM
echo.
echo 3. Run the setup script on the VM:
echo    bash compute_engine_setup.sh
echo.
echo 4. Configure services:
echo    sudo bash configure_services.sh
echo.
echo 5. Start the application:
echo    sudo systemctl start petpocket
echo.
echo 6. Access your app at: http://%EXTERNAL_IP%
echo.
echo For detailed instructions, see: COMPUTE_ENGINE_DEPLOYMENT.md
echo.
pause
