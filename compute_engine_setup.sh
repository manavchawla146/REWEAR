#!/bin/bash

# Google Compute Engine Deployment Script for Pet Pocket
# This script sets up the Pet Pocket Flask application on Ubuntu

set -e

echo "========================================="
echo "  Pet Pocket - Compute Engine Setup"
echo "========================================="

# Update system packages
echo "Updating system packages..."
sudo apt-get update -y
sudo apt-get upgrade -y

# Install Python 3.9 and pip
echo "Installing Python 3.9 and dependencies..."
sudo apt-get install -y python3.9 python3.9-venv python3.9-dev python3-pip
sudo apt-get install -y nginx supervisor git

# Create application directory
echo "Setting up application directory..."
sudo mkdir -p /var/www/petpocket
sudo chown $USER:$USER /var/www/petpocket
cd /var/www/petpocket

# Clone or copy your application (you'll need to upload your code first)
echo "Setting up application files..."
# Note: You'll need to upload your application files to the server
# For now, we'll create the directory structure

# Create Python virtual environment
echo "Creating Python virtual environment..."
python3.9 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip

# Create requirements.txt for production
cat > requirements.txt << 'EOF'
alembic==1.15.2
blinker==1.9.0
cachelib==0.13.0
cachetools==5.5.2
certifi==2025.1.31
charset-normalizer==3.4.1
click==8.1.8
colorama==0.4.6
Flask==3.1.0
Flask-Admin==1.6.1
Flask-Login==0.6.3
Flask-Mail==0.10.0
Flask-Migrate==4.1.0
Flask-OAuthlib==0.9.6
Flask-SQLAlchemy==3.1.1
Flask-WTF==1.2.2
google-api-core==2.24.2
google-api-python-client==2.170.0
google-auth==2.40.2
google-auth-httplib2==0.2.0
googleapis-common-protos==1.70.0
greenlet==3.1.1
httplib2==0.22.0
idna==3.10
itsdangerous==2.2.0
Jinja2==3.1.6
Mako==1.3.10
MarkupSafe==3.0.2
oauthlib==2.1.0
proto-plus==1.26.1
protobuf==6.31.1
pyasn1==0.6.1
pyasn1_modules==0.4.2
pyparsing==3.2.3
razorpay==1.4.2
requests==2.32.3
requests-oauthlib==1.1.0
rsa==4.9.1
SQLAlchemy==2.0.40
typing_extensions==4.13.1
uritemplate==4.1.1
urllib3==2.4.0
Werkzeug==3.1.3
WTForms==3.1.2
gunicorn==21.2.0
setuptools==75.8.0
pandas==2.1.4
EOF

pip install -r requirements.txt

echo "Setup completed! Next steps:"
echo "1. Upload your Pet Pocket application files to /var/www/petpocket/"
echo "2. Run the configuration script: sudo bash configure_services.sh"
echo "3. Start the application: sudo systemctl start petpocket"
