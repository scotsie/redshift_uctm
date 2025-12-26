# Contributing to Redshift UCTM CheckMK Extension

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to this project.

## Getting Started

### Prerequisites

- VSCode with Remote Containers extension
- Docker
- Git
- Basic knowledge of Python and CheckMK

### Development Setup

1. **Fork and clone the repository**:
   ```bash
   git clone https://github.com/YOUR-USERNAME/redshift_uctm.git
   cd redshift_uctm
   ```

2. **Open in VSCode with Remote Containers**:
   - Open VSCode
   - Press `F1` and select "Remote-Containers: Open Folder in Container"
   - Select the `redshift_uctm` folder
   - Wait for the container to build and start

3. **Verify the setup**:
   ```bash
   # Run tests
   pytest

   # Check code style
   flake8 agent_based/ server_side_calls/ libexec/ tests/
   ```

## Development Workflow

### Branch Strategy

- `main` - Production-ready code
- `develop` - Integration branch for features
- `feature/xxx` - Feature branches
- `bugfix/xxx` - Bug fix branches
- `hotfix/xxx` - Urgent fixes for production

### Making Changes

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following our coding standards

3. **Add tests** for new functionality:
   - Add tests to appropriate file in `tests/`
   - Aim for 80%+ coverage on new code
   - Test all edge cases

4. **Run the test suite**:
   ```bash
   # Run all tests
   pytest -v

   # Run with coverage
   pytest --cov=agent_based --cov=server_side_calls --cov-report=term-missing
   ```

5. **Check code quality**:
   ```bash
   # Linting
   flake8 agent_based/ server_side_calls/ libexec/ tests/

   # Security checks
   bandit -r agent_based/ server_side_calls/ libexec/
   ```

6. **Commit your changes**:
   ```bash
   git add .
   git commit -m "feat: add support for new metric"
   ```

### Commit Message Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `test:` - Adding or updating tests
- `refactor:` - Code refactoring
- `style:` - Code style changes (formatting, etc.)
- `chore:` - Maintenance tasks

Examples:
```
feat: add disk I/O monitoring
fix: correct memory calculation in system stats
docs: update README with new configuration options
test: add tests for chassis monitoring
```

### Pull Request Process

1. **Update documentation**:
   - Update README.md if adding features
   - Add/update docstrings
   - Update TESTING.md if changing tests

2. **Ensure all checks pass**:
   - All tests passing (95+ tests)
   - Code coverage maintained (88%+)
   - Linting passes (flake8)
   - No security issues (bandit)

3. **Create a pull request**:
   - Push your branch to GitHub
   - Create a PR against `develop`
   - Fill out the PR template
   - Link any related issues

4. **Code review**:
   - Address reviewer feedback
   - Keep the PR updated with `develop`
   - Squash commits if requested

## Coding Standards

### Python Style

- Follow [PEP 8](https://pep8.org/)
- Maximum line length: 127 characters
- Use type hints where appropriate
- Write docstrings for all functions

### CheckMK Plugin Standards

```python
def check_my_feature(params: Mapping[str, Any], section) -> CheckResult:
    """
    Check function for my feature

    Args:
        params: Configuration parameters
        section: Parsed section data

    Yields:
        Result and Metric objects
    """
    if not section:
        yield Result(state=State.UNKNOWN, summary="No data")
        return

    # Your logic here
    yield Metric("metric_name", value)
    yield Result(state=State.OK, summary="Everything OK")
```

### Testing Standards

- Write tests for all new functions
- Test happy path and edge cases
- Use descriptive test names
- Keep tests isolated (no dependencies between tests)

Example test:
```python
def test_check_feature_returns_ok_when_value_within_threshold(self):
    """Test that check returns OK when value is within threshold"""
    section = {"value": 50}
    params = {"levels": (80, 90)}

    results = list(check_my_feature(params, section))

    result_objs = [r for r in results if isinstance(r, Result)]
    assert result_objs[0].state == State.OK
```

## Project Structure

```
redshift_uctm/
├── .github/
│   ├── workflows/          # CI/CD pipelines
│   └── CONTRIBUTING.md     # This file
├── agent_based/            # CheckMK agent-based plugins
│   ├── redshift.py
│   ├── redshift_additional.py
│   └── redshift_common.py
├── server_side_calls/      # Special agent configuration
├── libexec/               # Special agent executable
├── rulesets/             # WATO configuration
├── checkman/             # Manual pages
├── tests/                # Test suite (95 tests, 88% coverage)
└── reference/            # API documentation
```

## Adding New Monitoring Features

### 1. Add API Method to Special Agent

Edit `libexec/agent_redshift`:

```python
def get_new_metric(self) -> Optional[Dict[str, Any]]:
    """Get new metric from API"""
    return self._make_request("api/endpoint/path")
```

### 2. Add Parser Function

Edit appropriate file in `agent_based/`:

```python
def parse_redshift_new_metric(string_table):
    """Parse new metric section"""
    return parse_json_section(string_table)

agent_section_redshift_new_metric = AgentSection(
    name="redshift_new_metric",
    parse_function=parse_redshift_new_metric,
)
```

### 3. Add Check Function

```python
def check_redshift_new_metric(params: Mapping[str, Any], section) -> CheckResult:
    """Check new metric"""
    # Your logic here
    yield Metric("metric_name", value)
    yield Result(state=state, summary=f"Metric: {value}")

check_plugin_redshift_new_metric = CheckPlugin(
    name="redshift_new_metric",
    service_name="New Metric",
    discovery_function=discover_redshift_new_metric,
    check_function=check_redshift_new_metric,
    check_default_parameters={"levels": (80, 90)},
    check_ruleset_name="redshift_new_metric",
)
```

### 4. Add Tests

Create tests in `tests/test_redshift.py` or `tests/test_redshift_additional.py`:

```python
class TestNewMetric:
    def test_parse_new_metric(self):
        string_table = [[json.dumps({"value": 42})]]
        result = parse_redshift_new_metric(string_table)
        assert result["value"] == 42

    def test_check_new_metric_ok(self):
        section = {"value": 50}
        params = {"levels": (80, 90)}
        results = list(check_redshift_new_metric(params, section))
        # Assert results
```

### 5. Add Ruleset (Optional)

If your check has configurable parameters, add a ruleset in `rulesets/`.

## Testing Guidelines

### Running Tests

```bash
# All tests
pytest

# Specific file
pytest tests/test_redshift.py

# Specific test
pytest tests/test_redshift.py::TestSystemStats::test_check_system_stats_memory_ok

# With coverage
pytest --cov=agent_based --cov=server_side_calls --cov-report=html
```

### Writing Good Tests

✅ **DO**:
- Test one thing per test
- Use descriptive names
- Test edge cases
- Mock external dependencies
- Keep tests fast (< 1s each)

❌ **DON'T**:
- Test implementation details
- Create test dependencies
- Use real API calls
- Skip error cases

## Documentation

### Code Documentation

- All functions must have docstrings
- Document parameters and return values
- Include examples for complex functions

### User Documentation

- Update README.md for new features
- Add checkman pages for new checks
- Update API reference if adding endpoints

## Questions?

- Open an issue for bugs or feature requests
- Start a discussion for questions
- Check existing issues before creating new ones

## License

By contributing, you agree that your contributions will be licensed under the GNU General Public License v2.
