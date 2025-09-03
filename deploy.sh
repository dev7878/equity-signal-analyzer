#!/bin/bash

# Google Cloud Deployment Script for Equity Signal Analyzer
# This script deploys the application to Google Cloud App Engine

set -e  # Exit on any error

echo "🚀 Deploying Equity Signal Analyzer to Google Cloud..."
echo "=================================================="

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ Google Cloud CLI is not installed."
    echo "Please install it from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if user is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "❌ Not authenticated with Google Cloud."
    echo "Please run: gcloud auth login"
    exit 1
fi

# Set project ID (you'll need to change this to your project ID)
PROJECT_ID="your-project-id-here"

echo "📋 Current configuration:"
echo "  Project ID: $PROJECT_ID"
echo "  Region: us-central1 (default)"
echo ""

# Set the project
echo "🔧 Setting Google Cloud project..."
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "🔧 Enabling required APIs..."
gcloud services enable appengine.googleapis.com
gcloud services enable cloudbuild.googleapis.com

# Deploy to App Engine
echo "🚀 Deploying to Google Cloud App Engine..."
gcloud app deploy app.yaml --quiet

# Get the URL
echo "✅ Deployment complete!"
echo ""
echo "🌐 Your application is now live at:"
gcloud app browse --no-launch-browser

echo ""
echo "📊 Dashboard URL: https://$PROJECT_ID.appspot.com"
echo ""
echo "🎉 Deployment successful! Your Equity Signal Analyzer is now publicly accessible."
