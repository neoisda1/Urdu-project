# 🚀 GitHub Publishing Guide

## Step 1: Initialize Git Repository

```bash
cd "/home/dan/Urdu project"
git init
git add .
git commit -m "Initial commit: Urdu Stories for Children - 33 stories with interactive reader"
```

## Step 2: Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `urdu-stories-for-children`
3. Description: "Interactive Urdu short stories for children (Ages 3-13) with adjustable fonts and dark/light themes"
4. Choose: **Public**
5. Do NOT initialize with README (we already have one)
6. Click "Create repository"

## Step 3: Connect and Push

Replace `YOUR_USERNAME` with your GitHub username:

```bash
git remote add origin https://github.com/YOUR_USERNAME/urdu-stories-for-children.git
git branch -M main
git push -u origin main
```

## Step 4: Enable GitHub Pages

1. Go to your repository on GitHub
2. Click **Settings** → **Pages**
3. Under "Source", select **main** branch
4. Select **/ (root)** folder
5. Click **Save**
6. Your site will be live at: `https://YOUR_USERNAME.github.io/urdu-stories-for-children/`

## Step 5: Update Links (Optional)

After publishing, update the GitHub links in:
- `index.html` - Line with GitHub button
- `story-viewer.html` - GitHub link in header

Replace `https://github.com` with your actual repository URL.

## ✨ Features of Your Site

- 📚 **33 Urdu Stories** across 5 categories
- 🎨 **Dark & Light Themes** with smooth transitions
- 🔤 **Adjustable Font Sizes** (12px - 36px)
- 📱 **Responsive Design** for all devices
- 🌐 **Bilingual Content** (Urdu + English)
- 💾 **Auto-saves** font size and theme preferences

## 📊 Project Stats

- Total Stories: 33
- Total Vocabulary: 300+ words
- Age Range: 3-13 years
- Categories: Regular, Simple, Funny, Mystery

## 🎯 Categories Breakdown

1. **Reading Lesson** (1) - Complete Urdu basics
2. **Regular Stories** (16) - Ages 5-8
3. **Simple Stories** (6) - Ages 3-5
4. **Funny Stories** (6) - Ages 3-5
5. **Mystery Stories** (5) - Ages 10-13

## 🌟 After Publishing

Your project will be accessible at:
- **GitHub Repo**: github.com/YOUR_USERNAME/urdu-stories-for-children
- **Live Site**: YOUR_USERNAME.github.io/urdu-stories-for-children

Share the live site link with:
- Parents and educators
- Urdu learning communities
- Social media platforms

---

**Made with ❤️ for Urdu learners**
