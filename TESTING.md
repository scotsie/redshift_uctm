# Testing Guide for Redshift UCTM CheckMK Extension

## Overview

This project includes a comprehensive test suite with **95 tests** achieving **88% code coverage** across all components.

## Quick Start

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=agent_based --cov=server_side_calls --cov-report=html

# Run specific test file
pytest tests/test_redshift.py

# Run with verbose output
pytest -v
```

## Test Suite Statistics

- **Total Tests**: 95
- **Overall Coverage**: 88%
- **Test Files**: 5
- **Components Tested**: 6

### Coverage Breakdown

| Component | Coverage | Notes |
|-----------|----------|-------|
| `agent_based/redshift_common.py` | 100% | All utility functions tested |
| `server_side_calls/redshift.py` | 100% | Complete parameter validation |
| `agent_based/redshift.py` | 90% | Main plugin functions |
| `libexec/agent_redshift` | 88% | Special agent script |
| `agent_based/redshift_additional.py` | 84% | Additional monitoring plugins |

## Test Files

### 1. `tests/test_redshift_common.py` (7 tests)
Tests common utility functions:
- JSON parsing (valid, invalid, nested, unicode)
- Error handling for malformed data
- Edge cases (empty data, invalid structures)

### 2. `tests/test_redshift.py` (38 tests)
Tests main monitoring plugins:
- **System Statistics**: Parse, discover, check with OK/WARN/CRIT states
- **HDD Monitoring**: Disk usage with configurable thresholds
- **Network Interfaces**: Interface discovery and monitoring
- **Chassis Information**: Hardware status monitoring
- **Uptime**: System uptime tracking

### 3. `tests/test_redshift_additional.py` (32 tests)
Tests additional monitoring features:
- **Processor Stats**: Aggregate and per-core CPU monitoring
- **Memory Usage**: Memory consumption with thresholds
- **Disk Space**: Per-filesystem disk monitoring
- **Discovery Parameters**: Configurable service discovery

### 4. `tests/test_server_side_calls.py` (11 tests)
Tests configuration and command generation:
- Parameter validation with Pydantic models
- Command-line argument generation
- SSL verification options
- Section filtering
- Default values and custom configurations

### 5. `tests/test_agent_redshift.py` (7 tests)
Tests the special agent script:
- API client initialization and configuration
- HTTP request handling with retries
- Malformed JSON cleanup (Redshift API quirks)
- Error handling (timeouts, connection errors, HTTP errors)
- Section output formatting
- Command-line argument parsing

## Key Testing Features

### Fixtures and Test Data
- Shared fixtures in `conftest.py` provide realistic sample data
- Reusable test data for system stats, processor info, memory, disk, etc.
- Easy to maintain and extend

### Mocked API Calls
- Uses `requests_mock` to simulate Redshift API responses
- No external dependencies required
- Fast test execution (< 3 seconds for full suite)

### Comprehensive Coverage
- **Parse functions**: Valid/invalid JSON, edge cases
- **Discovery functions**: With/without data, configurable parameters
- **Check functions**: All state transitions (OK → WARN → CRIT)
- **Metrics**: Proper metric names and values
- **Error handling**: Missing data, malformed responses

### State Testing
All check functions test the three monitoring states:
- **OK**: Normal operation within thresholds
- **WARN**: Warning level threshold exceeded
- **CRIT**: Critical level threshold exceeded

## Running Tests in Different Ways

### Basic Usage
```bash
# All tests with emoji output
pytest

# Quiet mode (only failures)
pytest -q

# Stop on first failure
pytest -x

# Show local variables on failure
pytest -l
```

### Filtering Tests
```bash
# Run tests matching pattern
pytest -k "memory"

# Run specific test class
pytest tests/test_redshift.py::TestSystemStats

# Run specific test
pytest tests/test_redshift.py::TestSystemStats::test_check_system_stats_memory_ok
```

### Coverage Options
```bash
# Terminal coverage report
pytest --cov=agent_based --cov=server_side_calls

# HTML coverage report (opens in browser)
pytest --cov=agent_based --cov=server_side_calls --cov-report=html
open htmlcov/index.html

# Coverage with missing lines
pytest --cov=agent_based --cov-report=term-missing

# Fail if coverage below threshold
pytest --cov=agent_based --cov-fail-under=80
```

### Output Formats
```bash
# JUnit XML (for CI/CD)
pytest --junitxml=test-results.xml

# Markdown report
pytest --md=test-report.md

# JSON report
pytest --json-report --json-report-file=report.json
```

## Continuous Integration

The test suite is CI-ready:
- Fast execution (< 3 seconds)
- No external dependencies
- Deterministic results
- Exit code indicates pass/fail
- Multiple output formats

### Example GitHub Actions
```yaml
- name: Run tests
  run: |
    pip install -r .devcontainer/requirements.txt
    pytest --cov=agent_based --cov=server_side_calls --junitxml=test-results.xml
```

## Test Configuration

Configuration in [`pytest.ini`](pytest.ini):
- Test discovery patterns
- Coverage settings
- Output options
- Custom markers
- Logging configuration

## Adding New Tests

When adding new functionality:

1. **Write the test first** (TDD approach):
   ```python
   def test_new_feature(self):
       result = new_feature(test_data)
       assert result == expected_value
   ```

2. **Use existing fixtures** from `conftest.py`

3. **Test edge cases**:
   - Empty data
   - Invalid data
   - Missing fields
   - Boundary conditions

4. **Test all states** for check functions:
   - OK state
   - WARN state
   - CRIT state

5. **Add to appropriate test file** based on component

## Troubleshooting

### Import Errors
If you encounter import errors:
```bash
export PYTHONPATH=/workspaces/redshift_uctm:$PYTHONPATH
pytest
```

### Coverage Not Working
Install pytest-cov:
```bash
pip install pytest-cov
```

### Slow Tests
Run with timing report:
```bash
pytest --durations=10
```

## Best Practices

1. **Keep tests fast**: All tests complete in < 3 seconds
2. **Test one thing**: Each test should verify one specific behavior
3. **Use descriptive names**: `test_memory_check_returns_critical_when_usage_above_95_percent`
4. **Mock external calls**: Always mock API calls and file I/O
5. **Don't test implementation**: Test behavior, not internal structure
6. **Keep fixtures simple**: Easy to understand test data
7. **Assert specific values**: Don't just check for non-None

## Coverage Goals

Current coverage: **88%**

Goals:
- ✅ Common utilities: 100%
- ✅ Server-side calls: 100%
- ✅ Main plugin: 90%+
- ✅ Special agent: 88%+
- 🎯 Additional plugins: Target 90%+

## Resources

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)
- [CheckMK Plugin Development](https://docs.checkmk.com/latest/en/devel_check_plugins.html)
- [Test README](tests/README.md)

## Summary

This test suite provides:
- ✅ Comprehensive coverage of all components
- ✅ Fast, reliable tests
- ✅ Easy to run and maintain
- ✅ CI/CD ready
- ✅ Clear documentation
- ✅ Good practices demonstrated

Run `pytest` to verify everything works!
