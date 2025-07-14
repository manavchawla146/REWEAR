#!/bin/bash

# Upload the fixed files to the server
echo "Uploading fixed files to server..."

# Copy the production run script
echo "Copying run_production.py..."
cp /tmp/run_production.py /var/www/petpocket/

# Copy the prefix middleware
echo "Copying prefix_middleware.py..."
cp /tmp/prefix_middleware.py /var/www/petpocket/

# Copy the domain configuration
echo "Copying config_domain.py..."
cp /tmp/config_domain.py /var/www/petpocket/

# Update nginx configuration
echo "Updating nginx configuration..."
sudo cp /tmp/nginx_domain.conf /etc/nginx/sites-available/petpocket

# Test nginx configuration
echo "Testing nginx configuration..."
sudo nginx -t

if [ $? -eq 0 ]; then
    echo "Nginx configuration is valid. Reloading nginx..."
    sudo systemctl reload nginx
else
    echo "Nginx configuration has errors. Please check the configuration."
    exit 1
fi

# Restart the Pet Pocket service
echo "Restarting Pet Pocket service..."
sudo systemctl restart petpocket

# Check service status
echo "Checking service status..."
sudo systemctl status petpocket --no-pager

echo "Deployment complete!"
echo "Testing the application..."
curl -I http://varunkotwani.me/rewear
