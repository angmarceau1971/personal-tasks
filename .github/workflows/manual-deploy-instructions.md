# GitHub Actions Deployment Setup

## Quick Fix for Immediate Update

If you need to update your GCP app right now, run this command locally:

```bash
gcloud run deploy task-dashboard --source . --platform managed --region us-central1 --allow-unauthenticated
```

## Setting Up Automatic Deployment

To make your GitHub pushes automatically deploy to GCP, you need to set up secrets:

### Step 1: Create Service Account
1. Go to Google Cloud Console → IAM & Admin → Service Accounts
2. Click "Create Service Account"
3. Name: `github-actions-deploy`
4. Grant these roles:
   - Cloud Run Admin
   - Cloud Build Service Account
   - Service Account User

### Step 2: Create Service Account Key
1. Click on the service account you created
2. Go to "Keys" tab → "Add Key" → "Create new key"
3. Choose JSON format and download the file

### Step 3: Add GitHub Secrets
1. Go to your GitHub repository → Settings → Secrets and variables → Actions
2. Add these secrets:
   - `GCP_PROJECT_ID`: Your Google Cloud project ID
   - `GCP_SA_KEY`: The entire contents of the JSON key file you downloaded

### Step 4: Test the Workflow
1. Make any small change to your code
2. Commit and push: `git add . && git commit -m "Test auto-deploy" && git push`
3. Check GitHub Actions tab to see the deployment in progress

## Alternative: Manual Deployment Only

If you prefer to keep manual deployment, just delete the `.github/workflows/deploy.yml` file and use the gcloud command above whenever you want to update. 