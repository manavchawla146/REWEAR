#!/bin/bash

# Upload Pet Pocket application to Compute Engine VM
# Run this script from your local machine

set -e

echo "========================================="
echo "  Pet Pocket - Upload to Compute Engine"
echo "========================================="

# Configuration
PROJECT_ID="pet-pocket-compute"  # Change this to your project ID
VM_NAME="pet-pocket-vm"
ZONE="us-west1-b"
LOCAL_PATH="."  # Current directory
REMOTE_PATH="/tmp/petpocket-upload"

echo "Uploading Pet Pocket application to VM..."

# Create remote directory
gcloud compute ssh ${VM_NAME} --zone=${ZONE} --command="mkdir -p ${REMOTE_PATH}"

# Upload application files
echo "Uploading files..."
gcloud compute scp --recurse \
    --exclude="*.pyc" \
    --exclude="__pycache__" \
    --exclude=".git" \
    --exclude="instance" \
    --exclude="migrations" \
    --exclude="*.db" \
    ${LOCAL_PATH}/* \
    ${VM_NAME}:${REMOTE_PATH}/ \
    --zone=${ZONE}

# Move files to proper location and set permissions
echo "Setting up application..."
gcloud compute ssh ${VM_NAME} --zone=${ZONE} --command="
    sudo mkdir -p /var/www/petpocket
    sudo cp -r ${REMOTE_PATH}/* /var/www/petpocket/
    sudo chown -R www-data:www-data /var/www/petpocket
    sudo chmod -R 755 /var/www/petpocket
    rm -rf ${REMOTE_PATH}
"

echo "Upload completed!"
echo ""
echo "Next steps:"
echo "1. SSH into your VM:"
echo "   gcloud compute ssh ${VM_NAME} --zone=${ZONE}"
echo ""
echo "2. Run setup script:"
echo "   cd /var/www/petpocket"
echo "   sudo bash compute_engine_setup.sh"
echo ""
echo "3. Configure services:"
echo "   sudo bash configure_services.sh"
echo ""
echo "4. Start application:"
echo "   sudo systemctl start petpocket"
