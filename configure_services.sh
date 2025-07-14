#!/bin/bash

# Configure services for Pet Pocket on Compute Engine

set -e

echo "Configuring Nginx and Supervisor for Pet Pocket..."

# Create Gunicorn configuration
sudo tee /var/www/petpocket/gunicorn_config.py > /dev/null << 'EOF'
# Gunicorn configuration file
import multiprocessing

# Server socket
bind = "127.0.0.1:8000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 100

# Logging
accesslog = "/var/log/petpocket/access.log"
errorlog = "/var/log/petpocket/error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = 'petpocket'

# Server mechanics
preload_app = True
daemon = False
pidfile = '/var/run/petpocket.pid'
user = 'www-data'
group = 'www-data'
tmp_upload_dir = None

# SSL (if needed)
# keyfile = '/path/to/keyfile'
# certfile = '/path/to/certfile'
EOF

# Create log directory
sudo mkdir -p /var/log/petpocket
sudo chown www-data:www-data /var/log/petpocket

# Create Supervisor configuration
sudo tee /etc/supervisor/conf.d/petpocket.conf > /dev/null << 'EOF'
[program:petpocket]
command=/var/www/petpocket/venv/bin/gunicorn --config /var/www/petpocket/gunicorn_config.py run:app
directory=/var/www/petpocket
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/petpocket/supervisor.log
environment=
    FLASK_ENV=production,
    SECRET_KEY="your-super-secret-key-change-this-in-production",
    DATABASE_URL="sqlite:////var/www/petpocket/petpocket.db",
    RAZORPAY_KEY_ID="rzp_test_QTmdq1PBiByYN9",
    RAZORPAY_KEY_SECRET="TNgY0GTvtMjHsl5pSm9Stlsy",
    GOOGLE_CLIENT_ID="780308680733-150vt09u8286otguf6krlq5um3nsbrf7.apps.googleusercontent.com",
    GOOGLE_CLIENT_SECRET="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",
    MAIL_USERNAME="manavdodani2005@gmail.com",
    MAIL_PASSWORD="efpd snbt djxw wesj"
EOF

# Create Nginx configuration
sudo tee /etc/nginx/sites-available/petpocket > /dev/null << 'EOF'
server {
    listen 80;
    server_name _;  # Replace with your domain or IP

    # Security headers
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options SAMEORIGIN;
    add_header X-XSS-Protection "1; mode=block";

    # Static files
    location /static {
        alias /var/www/petpocket/PetPocket/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Main application
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types
        application/atom+xml
        application/javascript
        application/json
        application/rss+xml
        application/vnd.ms-fontobject
        application/x-font-ttf
        application/x-web-app-manifest+json
        application/xhtml+xml
        application/xml
        font/opentype
        image/svg+xml
        image/x-icon
        text/css
        text/plain
        text/x-component;

    # File upload size limit
    client_max_body_size 16M;
}
EOF

# Enable the site
sudo ln -sf /etc/nginx/sites-available/petpocket /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test nginx configuration
sudo nginx -t

# Create systemd service for easier management
sudo tee /etc/systemd/system/petpocket.service > /dev/null << 'EOF'
[Unit]
Description=Pet Pocket Flask Application
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/var/www/petpocket
Environment=FLASK_ENV=production
Environment=SECRET_KEY=your-super-secret-key-change-this-in-production
Environment=DATABASE_URL=sqlite:////var/www/petpocket/petpocket.db
Environment=RAZORPAY_KEY_ID=rzp_test_QTmdq1PBiByYN9
Environment=RAZORPAY_KEY_SECRET=TNgY0GTvtMjHsl5pSm9Stlsy
Environment=GOOGLE_CLIENT_ID=780308680733-150vt09u8286otguf6krlq5um3nsbrf7.apps.googleusercontent.com
Environment=GOOGLE_CLIENT_SECRET=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
Environment=MAIL_USERNAME=manavdodani2005@gmail.com
Environment=MAIL_PASSWORD=efpd snbt djxw wesj
ExecStart=/var/www/petpocket/venv/bin/gunicorn --config /var/www/petpocket/gunicorn_config.py run:app
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# Set proper permissions
sudo chown -R www-data:www-data /var/www/petpocket
sudo chmod -R 755 /var/www/petpocket

# Reload and start services
sudo systemctl daemon-reload
sudo systemctl enable petpocket
sudo systemctl enable nginx
sudo systemctl enable supervisor

# Start services
sudo systemctl restart supervisor
sudo systemctl restart nginx

echo "Configuration completed!"
echo "Services configured:"
echo "- Nginx (reverse proxy)"
echo "- Supervisor (process manager)"
echo "- Systemd service (petpocket)"
echo ""
echo "To start the application:"
echo "sudo systemctl start petpocket"
echo ""
echo "To check status:"
echo "sudo systemctl status petpocket"
echo "sudo systemctl status nginx"
echo ""
echo "To view logs:"
echo "sudo journalctl -u petpocket -f"
echo "sudo tail -f /var/log/petpocket/error.log"
