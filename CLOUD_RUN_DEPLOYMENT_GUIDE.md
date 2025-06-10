# 🚀 **Deploy Task Dashboard to Google Cloud Run**

## **📋 Overview**
Deploy your task dashboard to Google Cloud Run for **free hosting** with **automatic scaling** and **global access**.

---

## **⚡ Quick Start (2 Options)**

### **Option A: GitHub + Cloud Run (Recommended)**
✅ Easy updates via Git push  
✅ Automatic deployments  
✅ Version control  

### **Option B: Direct Cloud Run**
✅ Faster initial setup  
❌ Manual updates required  

---

## **🎯 STEP 1: Setup Google Cloud**

### 1.1 Create Google Cloud Account
1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Sign in with your Google account
3. Accept terms and create project

### 1.2 Create New Project
```
1. Click "Select a project" → "New Project"
2. Project name: "task-dashboard" (or your choice)
3. Click "Create"
4. Wait for project creation
```

### 1.3 Enable Required APIs
```
1. Go to "APIs & Services" → "Library"
2. Search and enable:
   - Cloud Run API
   - Cloud Build API
   - Container Registry API
```

---

## **🎯 STEP 2: Setup GitHub Repository**

### 2.1 Run Setup Script
```batch
# In your project folder:
setup-github.bat
```

### 2.2 Create GitHub Repository
1. Go to [github.com](https://github.com) → "New repository"
2. Repository name: `task-dashboard` (or your choice)
3. Make it **Public** (required for free Cloud Run)
4. **Don't** initialize with README (we have files already)
5. Click "Create repository"

### 2.3 Connect Local to GitHub
```bash
# Replace YOUR_USERNAME with your GitHub username
git remote add origin https://github.com/YOUR_USERNAME/task-dashboard.git
git branch -M main
git push -u origin main
```

---

## **🎯 STEP 3: Deploy to Cloud Run**

### 3.1 Option A: GitHub Integration (Recommended)

#### Step 3.1.1: Setup Cloud Build Connection
```
1. In Google Cloud Console → "Cloud Build" → "Triggers"
2. Click "Connect Repository"
3. Select "GitHub" → "Authenticate"
4. Select your repository: YOUR_USERNAME/task-dashboard
5. Click "Connect"
```

#### Step 3.1.2: Create Build Trigger
```
1. Click "Create Trigger"
2. Name: "deploy-task-dashboard"
3. Event: "Push to branch"
4. Branch: "^main$"
5. Configuration: "Dockerfile"
6. Dockerfile: "Dockerfile"
7. Click "Create"
```

#### Step 3.1.3: Deploy to Cloud Run
```
1. Go to "Cloud Run" → "Create Service"
2. Select "Continuously deploy new revisions from a source repository"
3. Click "Set up with Cloud Build"
4. Choose your repository and branch (main)
5. Build type: "Dockerfile"
6. Service name: "task-dashboard"
7. Region: Choose closest to you (e.g., us-central1)
8. Authentication: "Allow unauthenticated invocations"
9. Click "Create"
```

### 3.2 Option B: Direct Deployment

#### Step 3.2.1: Install Google Cloud CLI
```
1. Download from: https://cloud.google.com/sdk/docs/install
2. Run installer and follow prompts
3. Restart terminal/PowerShell
```

#### Step 3.2.2: Login and Deploy
```bash
# Login to Google Cloud
gcloud auth login

# Set your project
gcloud config set project YOUR_PROJECT_ID

# Deploy to Cloud Run
gcloud run deploy task-dashboard \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

---

## **🎯 STEP 4: Access Your Dashboard**

### 4.1 Get Your URL
After deployment, you'll get a URL like:
```
https://task-dashboard-XXXXX-uc.a.run.app
```

### 4.2 Test Your Dashboard
1. **Dashboard View**: Visit the URL
2. **Admin Interface**: Click "Admin" button
3. **Network Access**: Share URL with household members

---

## **🔧 Managing Your Deployment**

### Update Your App (GitHub Method)
```bash
# Make changes to your files
git add .
git commit -m "Updated task categories"
git push

# Cloud Run automatically redeploys!
```

### View Logs
```
1. Google Cloud Console → "Cloud Run"
2. Click your service → "Logs" tab
3. View real-time application logs
```

### Custom Domain (Optional)
```
1. Cloud Run → Your service → "Manage Custom Domains"
2. Add your domain and verify ownership
3. Update DNS records as instructed
```

---

## **💰 Cost Estimate**

### Free Tier Limits (per month)
- **2 million requests**
- **360,000 GB-seconds** of memory
- **180,000 vCPU-seconds**

### Typical Usage (Household Dashboard)
- **~1,000 requests/month** = **FREE**
- Perfect for family/household use!

---

## **🔒 Security Notes**

### Public Access
- Dashboard is publicly accessible (required for free tier)
- Consider this for sensitive household data
- For private access, upgrade to paid tier

### Environment Variables
```
# If you need to add secrets later:
gcloud run services update task-dashboard \
  --set-env-vars="SECRET_KEY=your-secret"
```

---

## **🆘 Troubleshooting**

### Common Issues

#### "Service not found"
```bash
# Make sure you're in the right project
gcloud config get-value project

# List all services
gcloud run services list
```

#### "Build failed"
```
1. Check logs in Cloud Build console
2. Verify Dockerfile syntax
3. Ensure requirements.txt exists
```

#### "Admin not working"
```
# Check server logs for API endpoint errors
# Verify all files uploaded to GitHub
```

### Getting Help
- **Cloud Console**: Built-in help and documentation
- **Community**: Stack Overflow with tag `google-cloud-run`
- **Official Docs**: [cloud.google.com/run](https://cloud.google.com/run)

---

## **🎉 Success!**

Your task dashboard is now:
✅ **Hosted in the cloud**  
✅ **Accessible worldwide**  
✅ **Automatically scaling**  
✅ **Running for FREE**  

**Next**: Share the URL with your household and enjoy your cloud-hosted task management! 🏠📱 