# Pet Pocket - Google App Engine Deployment Guide

## Prerequisites

1. **Google Cloud Account**: Create a free account at [Google Cloud Platform](https://cloud.google.com/)
2. **Google Cloud SDK**: Install the [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)
3. **Python 3.9**: Ensure you have Python 3.9 installed

## Setup Steps

### 1. Create a Google Cloud Project

```bash
# Login to Google Cloud
gcloud auth login

# Create a new project (replace 'pet-pocket-app' with your desired project ID)
gcloud projects create pet-pocket-app --name="Pet Pocket"

# Set the project as default
gcloud config set project pet-pocket-app

# Enable required APIs
gcloud services enable appengine.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

### 2. Initialize App Engine

```bash
# Initialize App Engine (choose your preferred region when prompted)
gcloud app create
```

### 3. Configure Environment Variables

Before deploying, update the `app.yaml` file with your actual credentials:

- Replace `SECRET_KEY` with a strong, random secret key
- Update Razorpay credentials if needed
- Update Google OAuth credentials
- Update email credentials

### 4. Deploy the Application

```bash
# Navigate to your project directory
cd "c:\Users\kotwa\Downloads\pet pocket"

# Copy the production requirements file
copy requirements_appengine.txt requirements.txt

# Deploy to App Engine
gcloud app deploy

# Deploy with specific version (optional)
gcloud app deploy --version=v1

# Open the deployed app in browser
gcloud app browse
```

### 5. View Logs (if needed)

```bash
# View application logs
gcloud app logs tail -s default

# View logs for specific version
gcloud app logs tail -s default --version=v1
```

## Important Notes

### Database Considerations

- The current setup uses SQLite, which works for development but has limitations on App Engine
- For production, consider migrating to Google Cloud SQL (PostgreSQL/MySQL)
- To use Cloud SQL, update the `DATABASE_URL` in `app.yaml`

### Static Files

- Static files are served directly by App Engine as configured in `app.yaml`
- No need for additional static file hosting

### Environment Variables

All sensitive data is stored in environment variables in `app.yaml`. For production:

1. **Never commit sensitive data to version control**
2. Consider using Google Secret Manager for production secrets
3. Use strong, unique passwords and API keys

### SSL/HTTPS

- App Engine automatically provides SSL certificates
- Your app will be available at: `https://your-project-id.appspot.com`

### Custom Domain (Optional)

To use a custom domain:

```bash
# Map custom domain
gcloud app domain-mappings create your-domain.com
```

## Troubleshooting

### Common Issues

1. **Build Errors**: Check `requirements.txt` for incompatible packages
2. **Database Errors**: Ensure database initialization runs correctly
3. **Static Files Not Loading**: Check the `handlers` section in `app.yaml`

### Useful Commands

```bash
# Check app status
gcloud app describe

# List versions
gcloud app versions list

# Delete old versions
gcloud app versions delete v1

# Set traffic allocation
gcloud app services set-traffic default --splits=v2=1
```

## Cost Optimization

- App Engine has a generous free tier
- Monitor usage in Google Cloud Console
- Consider setting up billing alerts
- Use automatic scaling settings in `app.yaml`

## Security Best Practices

1. Use environment variables for all secrets
2. Enable HTTPS-only access
3. Regularly update dependencies
4. Monitor application logs
5. Use Google Cloud Security Command Center

## Support

For issues:
1. Check Google Cloud documentation
2. Review App Engine logs
3. Consult Flask deployment guides
4. Contact Google Cloud Support (if needed)
