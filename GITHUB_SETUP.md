# GitHub Setup Guide

This guide walks you through setting up GitHub Actions CI/CD for your Redshift UCTM CheckMK extension.

## Prerequisites

- GitHub account
- Git installed locally
- Repository created on GitHub

## Quick Setup (5 Minutes)

### 1. Update Badge URLs

Replace `YOUR-USERNAME` in [README.md](README.md) with your GitHub username:

```markdown
![build](https://github.com/YOUR-USERNAME/redshift_uctm/workflows/build/badge.svg)
![pytest](https://github.com/YOUR-USERNAME/redshift_uctm/workflows/pytest/badge.svg)
![Lint](https://github.com/YOUR-USERNAME/redshift_uctm/workflows/Lint/badge.svg)
![Security](https://github.com/YOUR-USERNAME/redshift_uctm/workflows/Security/badge.svg)
```

Example for user `johndoe`:
```markdown
![build](https://github.com/johndoe/redshift_uctm/workflows/build/badge.svg)
```

### 2. Push to GitHub

```bash
# Add all files
git add .

# Commit
git commit -m "ci: add GitHub Actions workflows and test suite"

# Push to main branch
git push origin main
```

### 3. Verify Workflows

1. Go to your GitHub repository
2. Click the **Actions** tab
3. You should see 4 workflows running:
   - build
   - pytest
   - Lint
   - Security

4. Wait for workflows to complete (usually < 2 minutes)
5. Check that all workflows pass ✅

### 4. View Badges

Go to your repository's main page. The badges should now appear at the top of the README showing:
- 🟢 Green "passing" badges if all checks succeeded
- 🔴 Red "failing" badges if any checks failed

## Optional Enhancements

### Enable Codecov (Recommended)

Get detailed coverage reports and a coverage badge.

1. **Sign up at Codecov**:
   - Go to [codecov.io](https://codecov.io)
   - Sign in with GitHub
   - Add your repository

2. **Get Upload Token** (if repository is private):
   - In Codecov, go to repository settings
   - Copy the upload token

3. **Add Token to GitHub** (private repos only):
   - Go to your GitHub repository
   - Settings > Secrets and variables > Actions
   - Click "New repository secret"
   - Name: `CODECOV_TOKEN`
   - Value: [paste token]
   - Click "Add secret"

4. **Update README** (optional):
   The codecov badge is already in the README:
   ```markdown
   [![codecov](https://codecov.io/gh/YOUR-USERNAME/redshift_uctm/branch/main/graph/badge.svg)](https://codecov.io/gh/YOUR-USERNAME/redshift_uctm)
   ```

5. **Verify**:
   - Push a commit
   - Check the pytest workflow
   - Coverage should upload to Codecov
   - View detailed reports at codecov.io

### Enable Branch Protection

Require all checks to pass before merging.

1. Go to repository Settings > Branches
2. Click "Add rule" under Branch protection rules
3. Configure:
   - **Branch name pattern**: `main`
   - ☑️ **Require a pull request before merging**
   - ☑️ **Require status checks to pass before merging**
     - Select: pytest, Lint, build, Security
   - ☑️ **Require conversation resolution before merging**

4. Click "Create" or "Save changes"

### Add Dependabot

Automatically update dependencies.

1. Create `.github/dependabot.yml`:
   ```yaml
   version: 2
   updates:
     - package-ecosystem: "pip"
       directory: "/.devcontainer"
       schedule:
         interval: "weekly"
       open-pull-requests-limit: 10

     - package-ecosystem: "github-actions"
       directory: "/"
       schedule:
         interval: "weekly"
   ```

2. Commit and push:
   ```bash
   git add .github/dependabot.yml
   git commit -m "ci: add dependabot configuration"
   git push
   ```

### Set Up GitHub Pages (Optional)

Host coverage reports and documentation.

1. Create `.github/workflows/pages.yml`:
   ```yaml
   name: Deploy Coverage to Pages

   on:
     push:
       branches: [ main ]

   jobs:
     deploy:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v4
         - uses: actions/setup-python@v5
           with:
             python-version: '3.12'
         - run: |
             pip install -r .devcontainer/requirements.txt
             pytest --cov=agent_based --cov=server_side_calls --cov-report=html
         - uses: peaceiris/actions-gh-pages@v3
           with:
             github_token: ${{ secrets.GITHUB_TOKEN }}
             publish_dir: ./htmlcov
   ```

2. Enable Pages:
   - Settings > Pages
   - Source: Deploy from a branch
   - Branch: gh-pages / (root)
   - Save

## Workflow Details

### What Runs on Every Push/PR

1. **pytest** (2-3 minutes):
   - Installs dependencies
   - Runs 95 tests on Python 3.11 and 3.12
   - Generates coverage report (88%)
   - Uploads to Codecov

2. **Lint** (< 1 minute):
   - Runs flake8 code quality checks
   - Checks for syntax errors
   - Validates PEP 8 compliance

3. **build** (< 1 minute):
   - Validates package structure
   - Checks Python syntax
   - Creates build artifacts

4. **Security** (1-2 minutes):
   - Scans dependencies for vulnerabilities
   - Runs Bandit security linter
   - Checks for exposed secrets

### What Runs on Tagged Releases

When you create a git tag starting with `v` (e.g., `v2.4.0`):

```bash
git tag v2.4.0
git push origin v2.4.0
```

The build workflow will:
- Run all standard checks
- Create a GitHub Release
- Upload build artifacts
- Generate release notes

## Troubleshooting

### Workflows Not Running

**Problem**: Actions tab shows no workflows

**Solution**:
1. Check Settings > Actions > General
2. Ensure "Allow all actions and reusable workflows" is selected
3. Check that workflow files are in `.github/workflows/`
4. Verify YAML syntax is correct

### Tests Failing in CI

**Problem**: Tests pass locally but fail in CI

**Solution**:
1. Check Python version matches (3.11 or 3.12)
2. Review workflow logs for errors
3. Ensure all dependencies in requirements.txt
4. Check for environment-specific issues

### Badge Not Showing

**Problem**: Badge shows "unknown" or doesn't appear

**Solution**:
1. Verify GitHub username in badge URL is correct
2. Ensure workflow has run at least once
3. Check workflow name matches badge URL exactly
4. Wait a few minutes for GitHub's cache to update

### Codecov Upload Failing

**Problem**: Coverage upload fails

**Solution**:
1. For private repos, ensure `CODECOV_TOKEN` secret is set
2. Check coverage.xml was generated
3. Review pytest workflow logs
4. Verify Codecov action version is current

## Best Practices

### Before Committing

```bash
# Run tests locally
pytest -v

# Check code quality
flake8 agent_based/ server_side_calls/ libexec/ tests/

# Verify coverage
pytest --cov=agent_based --cov=server_side_calls --cov-report=term-missing
```

### Commit Messages

Use [Conventional Commits](https://www.conventionalcommits.org/):
- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation changes
- `test:` - Test changes
- `ci:` - CI/CD changes

### Pull Request Workflow

1. Create feature branch:
   ```bash
   git checkout -b feature/my-feature
   ```

2. Make changes and commit

3. Push branch:
   ```bash
   git push origin feature/my-feature
   ```

4. Create PR on GitHub

5. Wait for all checks to pass

6. Request review

7. Merge when approved

## Monitoring

### Check Workflow Status

**Via GitHub**:
- Actions tab > Select workflow > View runs

**Via Badges**:
- Green = Passing
- Red = Failing
- Gray = Not run yet

**Via Email**:
- You'll receive emails for workflow failures

### View Coverage Reports

**Terminal** (local):
```bash
pytest --cov=agent_based --cov=server_side_calls --cov-report=term-missing
```

**HTML** (local):
```bash
pytest --cov=agent_based --cov=server_side_calls --cov-report=html
open htmlcov/index.html
```

**Codecov** (online):
- Go to codecov.io
- View your repository
- Detailed line-by-line coverage

## Next Steps

1. ✅ **Push to GitHub** - Get workflows running
2. ✅ **Fix any failing tests** - All should pass
3. ⭐ **Set up branch protection** - Require checks before merge
4. 📊 **Enable Codecov** - Get detailed coverage
5. 🔄 **Add Dependabot** - Keep dependencies updated
6. 📚 **Star the repo** - Help others discover it!

## Support

- **Issues**: Report bugs or request features via GitHub Issues
- **Discussions**: Ask questions in GitHub Discussions
- **Documentation**: See [TESTING.md](TESTING.md) and [CONTRIBUTING.md](.github/CONTRIBUTING.md)

---

**Your repository is now production-ready with automated testing, linting, and security scanning!** 🎉
