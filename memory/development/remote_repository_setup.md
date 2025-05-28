# Remote Repository Setup Guide

## Prerequisites
- GitHub/GitLab/Bitbucket account
- Git configured locally

## Steps to Create Remote Repository

### 1. Create Repository on GitHub
1. Go to https://github.com/new
2. Repository name: `facemesh-visualization`
3. Description: "3D visualization tool for facial microexpression analysis"
4. Set to Private (initially)
5. **Don't** initialize with README, .gitignore, or license (we have them)

### 2. Add Remote Origin
```bash
git remote add origin https://github.com/YOUR_USERNAME/facemesh-visualization.git
```

### 3. Push Both Branches
```bash
# Push main branch
git checkout main
git push -u origin main

# Push dev branch
git checkout dev
git push -u origin dev

# Set dev as default branch on GitHub (optional)
```

### 4. Verify Remote
```bash
git remote -v
git branch -r
```

## Repository Settings

### Recommended GitHub Settings
1. **Default branch**: Consider setting `dev` as default
2. **Branch protection**: Protect `main` branch
3. **Issues**: Enable for bug tracking
4. **Wiki**: Disable (we use memory/ for docs)

### .gitignore Check
Our .gitignore already excludes:
- `__pycache__/`
- `*.pyc`
- Test outputs
- Large animation files
- User preferences

## After Setup

1. **Update README** with repository URL
2. **Add collaborators** if needed
3. **Set up branch rules**:
   - `main`: Stable releases only
   - `dev`: Active development
   - Feature branches: `feature/description`

## Security Notes
- Don't commit sensitive data
- Use environment variables for API keys
- Review conversation histories before committing 