@echo off
cls
echo.
echo ==========================================
echo    📚 Setting up GitHub Repository
echo ==========================================
echo.

echo 🔍 Checking for Git installation...
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Git is not installed or not in PATH
    echo 📥 Please install Git from: https://git-scm.com/download/win
    echo.
    pause
    exit /b 1
)

echo ✅ Git is installed
echo.

echo 📁 Initializing Git repository...
git init

echo 📝 Creating .gitignore file...
echo __pycache__/ > .gitignore
echo *.pyc >> .gitignore
echo .env >> .gitignore
echo .vscode/ >> .gitignore
echo .idea/ >> .gitignore

echo 📦 Adding all files to Git...
git add .

echo 💬 Making initial commit...
git commit -m "Initial commit: Task Dashboard with Admin Interface"

echo.
echo ✅ Local repository setup complete!
echo.
echo 🚀 Next steps:
echo 1. Go to GitHub.com and create a new repository
echo 2. Copy the repository URL
echo 3. Run these commands:
echo.
echo    git remote add origin YOUR_GITHUB_URL
echo    git branch -M main
echo    git push -u origin main
echo.
pause 