# Quick Start Guide

## For Developers

### Setup (One-Time)

```bash
# 1. Clone and open in VSCode with Remote Containers
# 2. Container will build automatically
# 3. You're ready to develop!
```

### Daily Development

```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=agent_based --cov=server_side_calls --cov-report=html

# Check code quality
flake8 agent_based/ server_side_calls/ libexec/ tests/

# Build package
# Press Ctrl+Shift+B in VSCode
# OR run: .devcontainer/build.sh
```

### Making Changes

```bash
# 1. Create branch
git checkout -b feature/my-feature

# 2. Make changes

# 3. Add tests
# Edit files in tests/

# 4. Verify
pytest -v
flake8

# 5. Commit
git add .
git commit -m "feat: add new feature"

# 6. Push
git push origin feature/my-feature

# 7. Create PR on GitHub
```

## For GitHub Setup

### First Time (5 Minutes)

```bash
# 1. Update README.md badge URLs
# Replace YOUR-USERNAME with your GitHub username

# 2. Push to GitHub
git add .
git commit -m "ci: add GitHub Actions and tests"
git push origin main

# 3. Check GitHub Actions tab
# All workflows should pass ✅
```

See [GITHUB_SETUP.md](GITHUB_SETUP.md) for detailed instructions.

## For Users

### Installation

1. **Download** the `.mkp` file from Releases
2. **Upload** to CheckMK: Setup > Extension Packages
3. **Install** the package
4. **Configure**: Setup > VM, Cloud, Container > Redshift UCTM

### Configuration

- **Host**: IP or hostname of Redshift UCTM device
- **Port**: 443 (default)
- **SSL**: Disable verification if using self-signed cert
- **Timeout**: 10 seconds (increase if slow)
- **Sections**: Leave empty for all, or specify specific sections

### Troubleshooting

**No data received**:
- Check device is reachable
- Disable SSL verification
- Increase timeout

**Services not discovered**:
- Run service discovery manually
- Check special agent logs

See [README.md](README.md) for full documentation.

## Quick Reference

### File Structure

```
redshift_uctm/
├── agent_based/        - Check plugins
├── server_side_calls/  - Agent configuration
├── libexec/           - Special agent script
├── tests/             - 95 tests, 88% coverage
├── .github/           - CI/CD workflows
└── rulesets/          - Configuration UI
```

### Commands

| Task | Command |
|------|---------|
| Run all tests | `pytest` |
| Run with coverage | `pytest --cov` |
| Run specific test | `pytest tests/test_redshift.py` |
| Lint code | `flake8 agent_based/` |
| Build package | `Ctrl+Shift+B` |
| View coverage | `open htmlcov/index.html` |

### Test Statistics

- **95 tests** in 5 files
- **88% coverage** overall
- **< 3 seconds** execution time
- All tests passing ✅

### CI/CD Workflows

| Workflow | What It Does | When |
|----------|--------------|------|
| pytest | Runs 95 tests | Every push/PR |
| Lint | Code quality | Every push/PR |
| build | Package validation | Every push/PR |
| Security | Vulnerability scan | Push/PR/Weekly |

### Coverage by Component

| Component | Coverage |
|-----------|----------|
| `redshift_common.py` | 100% |
| `server_side_calls/redshift.py` | 100% |
| `redshift.py` | 90% |
| `agent_redshift` | 88% |
| `redshift_additional.py` | 84% |

## Links

- [README.md](README.md) - Full documentation
- [TESTING.md](TESTING.md) - Testing guide
- [GITHUB_SETUP.md](GITHUB_SETUP.md) - CI/CD setup
- [CONTRIBUTING.md](.github/CONTRIBUTING.md) - Contribution guide

## Support

- **Issues**: GitHub Issues
- **Questions**: GitHub Discussions
- **Security**: See SECURITY.md (if exists)
