# 🚀 Google Cloud Deployment Guide

This guide will help you deploy the Equity Signal Analyzer to Google Cloud App Engine for public access.

## 📋 Prerequisites

1. **Google Cloud Account**: Sign up at [Google Cloud Console](https://console.cloud.google.com/)
2. **Google Cloud CLI**: Install from [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)
3. **Billing Enabled**: Ensure billing is enabled on your Google Cloud project

## 🛠️ Setup Steps

### Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" → "New Project"
3. Enter project name: `equity-signal-analyzer`
4. Click "Create"
5. Note your **Project ID** (you'll need this later)

### Step 2: Configure Google Cloud CLI

```bash
# Authenticate with Google Cloud
gcloud auth login

# Set your project ID (replace with your actual project ID)
gcloud config set project YOUR_PROJECT_ID_HERE

# Enable required APIs
gcloud services enable appengine.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

### Step 3: Update Configuration

1. **Edit `deploy.sh`**:
   ```bash
   # Change this line in deploy.sh:
   PROJECT_ID="your-project-id-here"
   # To your actual project ID:
   PROJECT_ID="equity-signal-analyzer-123456"
   ```

2. **Edit `app.yaml`** (optional - customize if needed):
   - Adjust `min_instances` and `max_instances` for scaling
   - Modify `memory_gb` and `cpu` for performance
   - Change region if needed

### Step 4: Deploy to Google Cloud

```bash
# Make deployment script executable (Linux/Mac)
chmod +x deploy.sh

# Run deployment
./deploy.sh
```

**For Windows users:**
```cmd
# Run the deployment commands manually
gcloud app deploy app.yaml --quiet
gcloud app browse
```

## 🌐 Access Your Application

After successful deployment, your application will be available at:
- **URL**: `https://YOUR_PROJECT_ID.appspot.com`
- **Example**: `https://equity-signal-analyzer-123456.appspot.com`

## 📊 Features Available

Once deployed, users can:
- ✅ Analyze any equity ticker (TSX, NYSE, NASDAQ)
- ✅ Generate trading signals with RSI, MACD, Bollinger Bands
- ✅ View volatility regime analysis
- ✅ Access market quality metrics
- ✅ Download analysis results as JSON
- ✅ Export interactive charts

## 💰 Cost Estimation

**Google Cloud App Engine Pricing** (approximate):
- **Free Tier**: 28 instance hours/day
- **Paid Tier**: ~$0.05-0.10 per hour for F1 instance
- **Monthly Cost**: $15-30 for moderate usage

## 🔧 Customization Options

### Scaling Configuration
Edit `app.yaml` to adjust scaling:
```yaml
automatic_scaling:
  min_instances: 1      # Always keep 1 instance running
  max_instances: 10     # Scale up to 10 instances max
  target_cpu_utilization: 0.6
```

### Performance Tuning
```yaml
resources:
  cpu: 1                # Increase for better performance
  memory_gb: 2          # Increase for larger datasets
  disk_size_gb: 10      # Increase for more storage
```

### Custom Domain (Optional)
1. Go to Google Cloud Console → App Engine → Settings
2. Click "Custom Domains"
3. Add your domain and follow DNS setup instructions

## 🚨 Troubleshooting

### Common Issues:

1. **"Project not found"**
   - Verify project ID in `deploy.sh`
   - Run `gcloud config set project YOUR_PROJECT_ID`

2. **"Billing not enabled"**
   - Enable billing in Google Cloud Console
   - Link a payment method

3. **"API not enabled"**
   - Run: `gcloud services enable appengine.googleapis.com`

4. **"Deployment timeout"**
   - Check internet connection
   - Try deploying again with `--quiet` flag

### Logs and Monitoring:
```bash
# View application logs
gcloud app logs tail

# View specific service logs
gcloud app logs tail --service=default
```

## 🔄 Updates and Maintenance

### Deploy Updates:
```bash
# After making code changes
./deploy.sh
```

### Monitor Usage:
- Google Cloud Console → App Engine → Instances
- Monitor CPU, memory, and request metrics

### Scale Down (Cost Saving):
```yaml
# In app.yaml, set:
automatic_scaling:
  min_instances: 0  # Scale to zero when not in use
```

## 🎯 Next Steps

1. **Test your deployment** with various tickers
2. **Monitor performance** in Google Cloud Console
3. **Set up alerts** for errors or high usage
4. **Consider custom domain** for professional appearance
5. **Implement authentication** if needed for private access

## 📞 Support

If you encounter issues:
1. Check Google Cloud Console logs
2. Verify all prerequisites are met
3. Ensure billing is enabled
4. Contact Google Cloud support if needed

---

**🎉 Congratulations!** Your Equity Signal Analyzer is now publicly accessible and ready for users worldwide!
