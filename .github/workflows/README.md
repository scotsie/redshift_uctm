# GitHub Actions Workflows

This directory contains CI/CD workflows that automatically test, lint, and validate the codebase.

## Workflows

### 1. pytest.yml - Test Suite

**Triggers**: Push to main/develop, Pull Requests

**What it does**:
- Runs the full test suite (95 tests)
- Tests on Python 3.11 and 3.12
- Generates coverage reports (targets 88%+)
- Uploads results to Codecov
- Creates test result artifacts

**Badge**: ![pytest](https://github.com/YOUR-USERNAME/redshift_uctm/workflows/pytest/badge.svg)

**Local equivalent**:
```bash
pytest --cov=agent_based --cov=server_side_calls --cov-report=term-missing
```

### 2. lint.yml - Code Quality

**Triggers**: Push to main/develop, Pull Requests

**What it does**:
- Runs flake8 linter
- Checks for syntax errors
- Validates code style (PEP 8)
- Uploads results as SARIF for code annotations

**Badge**: ![Lint](https://github.com/YOUR-USERNAME/redshift_uctm/workflows/Lint/badge.svg)

**Local equivalent**:
```bash
flake8 agent_based/ server_side_calls/ libexec/ tests/
```

### 3. build.yml - Package Build

**Triggers**: Push to main/develop, Pull Requests, Tags (v*)

**What it does**:
- Validates package structure
- Checks Python syntax
- Extracts package version
- Creates build artifacts
- Creates GitHub releases for tagged versions

**Badge**: ![build](https://github.com/YOUR-USERNAME/redshift_uctm/workflows/build/badge.svg)

**Local equivalent**:
```bash
.devcontainer/build.sh
```

### 4. security.yml - Security Scanning

**Triggers**: Push to main/develop, Pull Requests, Weekly schedule

**What it does**:
- Scans dependencies for vulnerabilities (Safety)
- Runs security linter (Bandit)
- Checks for exposed secrets (TruffleHog)
- Generates security reports

**Badge**: ![Security](https://github.com/YOUR-USERNAME/redshift_uctm/workflows/Security/badge.svg)

**Local equivalent**:
```bash
bandit -r agent_based/ server_side_calls/ libexec/
safety check
```

## Workflow Features

### Matrix Testing
The pytest workflow runs tests on multiple Python versions:
- Python 3.11
- Python 3.12

This ensures compatibility across supported versions.

### Caching
Dependencies are cached to speed up workflow runs:
- pip packages cached by requirements.txt hash
- Significant speedup on subsequent runs

### Artifacts
Workflows upload various artifacts:
- Test results (JUnit XML)
- Coverage reports (XML)
- Build packages (tar.gz)
- Security scan results (JSON)

Artifacts are retained for 30 days.

### Status Badges
All workflows provide status badges for the README:
```markdown
![build](https://github.com/YOUR-USERNAME/redshift_uctm/workflows/build/badge.svg)
![pytest](https://github.com/YOUR-USERNAME/redshift_uctm/workflows/pytest/badge.svg)
![Lint](https://github.com/YOUR-USERNAME/redshift_uctm/workflows/Lint/badge.svg)
![Security](https://github.com/YOUR-USERNAME/redshift_uctm/workflows/Security/badge.svg)
```

## Setting Up

### 1. Push to GitHub
```bash
git add .github/workflows/
git commit -m "ci: add GitHub Actions workflows"
git push origin main
```

### 2. Enable GitHub Actions
- Go to your repository settings
- Navigate to Actions
- Ensure Actions are enabled

### 3. Set Up Codecov (Optional)
1. Sign up at [codecov.io](https://codecov.io)
2. Add your repository
3. Get the upload token
4. Add as repository secret: `CODECOV_TOKEN`

### 4. Update Badge URLs
Replace `YOUR-USERNAME` in README.md with your GitHub username.

## Workflow Status

View workflow runs:
- Go to the **Actions** tab in your GitHub repository
- Click on any workflow to see run history
- Click on a specific run to see detailed logs

## Troubleshooting

### Workflow Not Running
- Check if Actions are enabled in repository settings
- Verify the trigger conditions (branch names, etc.)
- Check workflow YAML syntax

### Tests Failing in CI but Passing Locally
- Check Python version (use same version locally)
- Verify dependencies match requirements.txt
- Check for environment-specific issues

### Coverage Upload Failing
- Verify Codecov token is set correctly
- Check if coverage.xml was generated
- Review Codecov action logs

### Security Scan False Positives
- Review Bandit configuration in workflow
- Add exclusions for known safe patterns
- Document any ignored warnings

## Customization

### Changing Python Versions
Edit `pytest.yml`:
```yaml
strategy:
  matrix:
    python-version: ['3.11', '3.12', '3.13']
```

### Adjusting Triggers
Edit any workflow file:
```yaml
on:
  push:
    branches: [ main, develop, feature/* ]
  pull_request:
    branches: [ main ]
```

### Adding New Workflows
1. Create new `.yml` file in `.github/workflows/`
2. Define name, triggers, and jobs
3. Add badge to README if desired

## Best Practices

1. **Keep workflows fast**: Use caching, parallel jobs
2. **Fail fast**: Run quick checks first (linting before tests)
3. **Clear names**: Use descriptive job and step names
4. **Version pins**: Pin action versions (e.g., `@v4` not `@main`)
5. **Secrets management**: Use GitHub Secrets for sensitive data
6. **Status checks**: Require workflows to pass before merging

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Workflow Syntax Reference](https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions)
- [Available Actions](https://github.com/marketplace?type=actions)
