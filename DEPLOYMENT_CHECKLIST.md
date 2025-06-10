# ✅ **Cloud Run Deployment Checklist**

## **🚀 Quick Checklist - GitHub Method (Recommended)**

### **Prerequisites**
- [ ] Google account 
- [ ] GitHub account ✅ (you have this)
- [ ] Task dashboard files ✅ (ready!)

### **Step 1: Google Cloud Setup**
- [ ] Visit [console.cloud.google.com](https://console.cloud.google.com)
- [ ] Create new project: "task-dashboard"
- [ ] Enable APIs: Cloud Run, Cloud Build, Container Registry

### **Step 2: GitHub Repository**
- [ ] Run `setup-github.bat` in your project folder
- [ ] Create new GitHub repository: "task-dashboard" 
- [ ] Make repository **PUBLIC** (required for free tier)
- [ ] Connect local folder to GitHub:
  ```bash
  git remote add origin https://github.com/YOUR_USERNAME/task-dashboard.git
  git branch -M main  
  git push -u origin main
  ```

### **Step 3: Deploy to Cloud Run**
- [ ] Google Cloud Console → "Cloud Run" → "Create Service"
- [ ] Select "Continuously deploy from repository" 
- [ ] Connect your GitHub repository
- [ ] Service name: "task-dashboard"
- [ ] Region: Select closest to you
- [ ] Authentication: "Allow unauthenticated invocations"
- [ ] Click "Create"

### **Step 4: Test & Share**
- [ ] Visit your Cloud Run URL
- [ ] Test dashboard rotation
- [ ] Test admin interface (click "Admin" button)
- [ ] Share URL with household members

---

## **⚡ Alternative: Quick CLI Method**

If you prefer command line:

```bash
# Install Google Cloud CLI first
# Then run these commands:

gcloud auth login
gcloud config set project YOUR_PROJECT_ID
gcloud run deploy task-dashboard --source . --platform managed --region us-central1 --allow-unauthenticated
```

---

## **🎯 What You Get**

After deployment:
- ✅ **Free hosting** (perfect for household use)
- ✅ **Global URL** like: `https://task-dashboard-xxxxx-uc.a.run.app`
- ✅ **Automatic scaling** (handles traffic spikes)
- ✅ **Auto-updates** when you push to GitHub
- ✅ **Mobile-friendly** dashboard for all devices

---

## **💡 Pro Tips**

- **Updates**: Just push to GitHub and Cloud Run auto-deploys
- **Monitoring**: View logs in Google Cloud Console
- **Cost**: Completely free for typical household usage
- **Access**: Share the URL - no app installation needed

---

**Ready to deploy?** Start with **Step 1** above! 🚀 