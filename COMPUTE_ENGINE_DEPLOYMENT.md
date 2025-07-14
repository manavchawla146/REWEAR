# Pet Pocket - Google Compute Engine Deployment Guide

## Free Tier Specifications
- **VM Instance**: e2-micro (1 vCPU, 1 GB RAM)
- **Region**: us-west1 (Oregon), us-central1 (Iowa), or us-east1 (South Carolina)
- **Disk**: 30 GB standard persistent disk
- **Network**: 1 GB outbound data transfer per month
- **Cost**: FREE (within limits)

## Prerequisites

1. **Google Cloud Account**: Create a free account at [Google Cloud Platform](https://cloud.google.com/)
2. **Google Cloud SDK**: Install the [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)
3. **SSH Key**: Generate SSH key for secure access

## Step 1: Create and Configure VM Instance

### 1.1 Login and Setup Project

```bash
# Login to Google Cloud
gcloud auth login

# Create a new project
gcloud projects create pet-pocket-compute --name="Pet Pocket"

# Set the project as default
gcloud config set project pet-pocket-compute

# Enable required APIs
gcloud services enable compute.googleapis.com
```

### 1.2 Create VM Instance (Free Tier)

```bash
# Create e2-micro instance in us-west1 (Oregon) - Free tier eligible
gcloud compute instances create pet-pocket-vm \
    --zone=us-west1-b \
    --machine-type=e2-micro \
    --network-tier=STANDARD \
    --maintenance-policy=MIGRATE \
    --service-account=default \
    --scopes=https://www.googleapis.com/auth/cloud-platform \
    --image-family=ubuntu-2004-lts \
    --image-project=ubuntu-os-cloud \
    --boot-disk-size=30GB \
    --boot-disk-type=pd-standard \
    --boot-disk-device-name=pet-pocket-vm \
    --no-shielded-secure-boot \
    --shielded-vtpm \
    --shielded-integrity-monitoring \
    --reservation-affinity=any

# Create firewall rule for HTTP traffic
gcloud compute firewall-rules create allow-http-pet-pocket \
    --allow tcp:80 \
    --source-ranges 0.0.0.0/0 \
    --description "Allow HTTP traffic for Pet Pocket"

# Create firewall rule for HTTPS traffic (optional)
gcloud compute firewall-rules create allow-https-pet-pocket \
    --allow tcp:443 \
    --source-ranges 0.0.0.0/0 \
    --description "Allow HTTPS traffic for Pet Pocket"
```

### 1.3 Connect to VM

```bash
# SSH into the instance
gcloud compute ssh pet-pocket-vm --zone=us-west1-b

# Or get external IP and use regular SSH
gcloud compute instances describe pet-pocket-vm \
    --zone=us-west1-b \
    --format='get(networkInterfaces[0].accessConfigs[0].natIP)'
```

## Step 2: Setup Application on VM

### 2.1 Initial Server Setup

Once connected to your VM via SSH:

```bash
# Download setup script
wget https://raw.githubusercontent.com/your-repo/pet-pocket/main/compute_engine_setup.sh

# Make it executable
chmod +x compute_engine_setup.sh

# Run setup script
bash compute_engine_setup.sh
```

### 2.2 Upload Application Files

**Option A: Using Git (Recommended)**
```bash
# On your VM
cd /var/www/petpocket
git clone https://github.com/your-username/pet-pocket.git .
```

**Option B: Using SCP from your local machine**
```bash
# From your local machine
gcloud compute scp --recurse "c:\Users\kotwa\Downloads\pet pocket\*" \
    pet-pocket-vm:/var/www/petpocket/ \
    --zone=us-west1-b
```

**Option C: Using rsync**
```bash
# From your local machine (if you have rsync)
gcloud compute ssh pet-pocket-vm --zone=us-west1-b \
    --command="rsync -av /path/to/local/petpocket/ /var/www/petpocket/"
```

### 2.3 Configure Services

```bash
# On your VM
sudo bash configure_services.sh

# Start the application
sudo systemctl start petpocket
sudo systemctl status petpocket

# Check if everything is running
sudo systemctl status nginx
sudo systemctl status petpocket
```

## Step 3: Access Your Application

### 3.1 Get VM External IP

```bash
# Get external IP
gcloud compute instances describe pet-pocket-vm \
    --zone=us-west1-b \
    --format='get(networkInterfaces[0].accessConfigs[0].natIP)'
```

### 3.2 Test Application

Visit `http://YOUR_EXTERNAL_IP` in your browser.

## Step 4: Domain Setup (Optional)

### 4.1 Point Domain to VM

If you have a domain, update your DNS records:
- **A Record**: `your-domain.com` → `YOUR_VM_EXTERNAL_IP`
- **CNAME Record**: `www.your-domain.com` → `your-domain.com`

### 4.2 Setup SSL Certificate (Optional)

```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Get SSL certificate (replace with your domain)
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Test auto-renewal
sudo certbot renew --dry-run
```

## Management Commands

### Application Management

```bash
# Start/Stop/Restart application
sudo systemctl start petpocket
sudo systemctl stop petpocket
sudo systemctl restart petpocket

# View logs
sudo journalctl -u petpocket -f
sudo tail -f /var/log/petpocket/error.log

# Check status
sudo systemctl status petpocket
sudo systemctl status nginx
```

### VM Management

```bash
# Start/Stop VM (to save costs)
gcloud compute instances start pet-pocket-vm --zone=us-west1-b
gcloud compute instances stop pet-pocket-vm --zone=us-west1-b

# SSH into VM
gcloud compute ssh pet-pocket-vm --zone=us-west1-b

# Get VM info
gcloud compute instances describe pet-pocket-vm --zone=us-west1-b
```

## Monitoring and Maintenance

### Resource Monitoring

```bash
# Check disk usage
df -h

# Check memory usage
free -h

# Check CPU usage
top

# Check running processes
ps aux | grep gunicorn
```

### Application Updates

```bash
# Pull latest changes (if using Git)
cd /var/www/petpocket
git pull origin main

# Restart application
sudo systemctl restart petpocket
```

## Cost Optimization

### Free Tier Limits
- Keep VM running ≤ 744 hours/month (always-free)
- Monitor disk usage (30 GB limit)
- Monitor outbound traffic (1 GB/month limit)
- Use us-west1, us-central1, or us-east1 regions only

### Cost Saving Tips

```bash
# Stop VM when not needed (saves compute costs)
gcloud compute instances stop pet-pocket-vm --zone=us-west1-b

# Start VM when needed
gcloud compute instances start pet-pocket-vm --zone=us-west1-b

# Schedule automatic shutdown (optional)
# Add to crontab: 0 2 * * * /usr/bin/sudo /usr/bin/systemctl poweroff
```

## Troubleshooting

### Common Issues

1. **Application won't start**
   ```bash
   sudo journalctl -u petpocket -f
   sudo systemctl status petpocket
   ```

2. **502 Bad Gateway**
   ```bash
   sudo systemctl status nginx
   sudo nginx -t
   sudo systemctl restart nginx
   ```

3. **Database issues**
   ```bash
   # Check database file permissions
   ls -la /var/www/petpocket/petpocket.db
   sudo chown www-data:www-data /var/www/petpocket/petpocket.db
   ```

4. **High memory usage**
   ```bash
   # Check memory usage
   free -h
   # Restart application to free memory
   sudo systemctl restart petpocket
   ```

### Useful Commands

```bash
# View all logs
sudo journalctl -xe

# Check disk space
df -h

# Check network connectivity
ping google.com

# Check open ports
sudo netstat -tlnp

# Check firewall status
sudo ufw status
```

## Security Best Practices

1. **Update system regularly**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. **Setup firewall**
   ```bash
   sudo ufw enable
   sudo ufw allow 22  # SSH
   sudo ufw allow 80  # HTTP
   sudo ufw allow 443 # HTTPS
   ```

3. **Monitor logs**
   ```bash
   sudo tail -f /var/log/auth.log
   sudo journalctl -u petpocket -f
   ```

4. **Backup database**
   ```bash
   # Create backup
   cp /var/www/petpocket/petpocket.db /var/www/petpocket/backup_$(date +%Y%m%d).db
   
   # Download backup to local machine
   gcloud compute scp pet-pocket-vm:/var/www/petpocket/backup_*.db ./backups/ --zone=us-west1-b
   ```

## Support

- [Google Cloud Documentation](https://cloud.google.com/docs)
- [Compute Engine Documentation](https://cloud.google.com/compute/docs)
- [Flask Deployment Guide](https://flask.palletsprojects.com/en/2.3.x/deploying/)
- [Nginx Documentation](https://nginx.org/en/docs/)

Your Pet Pocket application will be running on Google Compute Engine with the free tier limits!
