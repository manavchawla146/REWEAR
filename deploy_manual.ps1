# Pet Pocket - Manual Deployment Commands
# Copy and paste these commands one by one in PowerShell

# Set the gcloud path (adjust if your installation is different)
$GCLOUD = "C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd"

Write-Host "==========================================" -ForegroundColor Green
Write-Host "  Pet Pocket - Compute Engine Deployment" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""

# Step 1: Check authentication
Write-Host "[1/6] Checking authentication..." -ForegroundColor Yellow
& $GCLOUD auth list

# Step 2: Create project
Write-Host ""
Write-Host "[2/6] Creating project..." -ForegroundColor Yellow
$PROJECT_ID = Read-Host "Enter your project ID (e.g., pet-pocket-compute-123)"
& $GCLOUD projects create $PROJECT_ID --name="Pet Pocket"
& $GCLOUD config set project $PROJECT_ID

# Step 3: Enable APIs
Write-Host ""
Write-Host "[3/6] Enabling APIs..." -ForegroundColor Yellow
& $GCLOUD services enable compute.googleapis.com

# Step 4: Create VM instance
Write-Host ""
Write-Host "[4/6] Creating VM instance (e2-micro - Free Tier)..." -ForegroundColor Yellow
& $GCLOUD compute instances create pet-pocket-vm `
    --zone=us-west1-b `
    --machine-type=e2-micro `
    --network-tier=STANDARD `
    --maintenance-policy=MIGRATE `
    --service-account=default `
    --scopes=https://www.googleapis.com/auth/cloud-platform `
    --image-family=ubuntu-2004-lts `
    --image-project=ubuntu-os-cloud `
    --boot-disk-size=30GB `
    --boot-disk-type=pd-standard `
    --boot-disk-device-name=pet-pocket-vm `
    --no-shielded-secure-boot `
    --shielded-vtpm `
    --shielded-integrity-monitoring `
    --reservation-affinity=any

# Step 5: Create firewall rules
Write-Host ""
Write-Host "[5/6] Creating firewall rules..." -ForegroundColor Yellow
& $GCLOUD compute firewall-rules create allow-http-pet-pocket `
    --allow tcp:80 `
    --source-ranges 0.0.0.0/0 `
    --description "Allow HTTP traffic for Pet Pocket"

& $GCLOUD compute firewall-rules create allow-https-pet-pocket `
    --allow tcp:443 `
    --source-ranges 0.0.0.0/0 `
    --description "Allow HTTPS traffic for Pet Pocket"

# Step 6: Get VM information
Write-Host ""
Write-Host "[6/6] Getting VM information..." -ForegroundColor Yellow
$EXTERNAL_IP = & $GCLOUD compute instances describe pet-pocket-vm --zone=us-west1-b --format="get(networkInterfaces[0].accessConfigs[0].natIP)"

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "   Deployment Completed Successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "VM Instance: pet-pocket-vm" -ForegroundColor Cyan
Write-Host "Zone: us-west1-b" -ForegroundColor Cyan
Write-Host "Machine Type: e2-micro (Free Tier)" -ForegroundColor Cyan
Write-Host "External IP: $EXTERNAL_IP" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Connect to your VM:" -ForegroundColor White
Write-Host "   & `"$GCLOUD`" compute ssh pet-pocket-vm --zone=us-west1-b" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Upload your application files to the VM" -ForegroundColor White
Write-Host ""
Write-Host "3. Access your app at: http://$EXTERNAL_IP" -ForegroundColor Green
