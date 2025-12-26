# Test Suite for Redshift UCTM CheckMK Extension

This directory contains comprehensive tests for the Redshift UCTM CheckMK monitoring extension.

## Test Structure

```
tests/
├── conftest.py                    # Shared fixtures and test configuration
├── test_redshift_common.py        # Tests for common utility functions
├── test_redshift.py               # Tests for main agent-based plugins
├── test_redshift_additional.py    # Tests for additional plugins (processor, memory, disk)
├── test_server_side_calls.py      # Tests for server-side call configuration
├── test_agent_redshift.py         # Tests for the special agent script
└── README.md                      # This file
```

## Running Tests

### Run All Tests
```bash
pytest
```

### Run Specific Test File
```bash
pytest tests/test_redshift.py
```

### Run Specific Test Class
```bash
pytest tests/test_redshift.py::TestSystemStats
```

### Run Specific Test Function
```bash
pytest tests/test_redshift.py::TestSystemStats::test_parse_valid_system_stats
```

### Run with Verbose Output
```bash
pytest -v
```

### Run with Coverage Report
```bash
pytest --cov=agent_based --cov=server_side_calls --cov=libexec --cov-report=html
```

### Run Tests Matching a Pattern
```bash
pytest -k "memory"  # Runs all tests with "memory" in the name
```

### Run Only Fast Tests (exclude slow tests)
```bash
pytest -m "not slow"
```

## Test Categories

Tests are organized by component:

### 1. Common Utilities (`test_redshift_common.py`)
- JSON parsing functions
- Error handling
- Data structure validation

### 2. Main Plugins (`test_redshift.py`)
- System statistics parsing and checking
- HDD and Ethernet monitoring
- Chassis information
- Uptime monitoring
- Service discovery
- Metric generation
- State evaluation (OK/WARN/CRIT)

### 3. Additional Plugins (`test_redshift_additional.py`)
- Processor statistics (aggregate and per-core)
- Memory usage monitoring
- Disk space monitoring
- Configurable thresholds
- Discovery parameters

### 4. Server-Side Calls (`test_server_side_calls.py`)
- Parameter validation
- Command generation
- Configuration options

### 5. Special Agent (`test_agent_redshift.py`)
- API client functionality
- HTTP request handling
- Malformed JSON cleanup
- Error handling
- Section output formatting
- Command-line argument parsing

## Writing New Tests

When adding new functionality, follow these patterns:

### 1. Use Fixtures
Define shared test data in `conftest.py`:
```python
@pytest.fixture
def sample_data():
    return {"key": "value"}
```

### 2. Organize into Classes
Group related tests:
```python
class TestMyFeature:
    def test_basic_functionality(self):
        # Test code here
        pass
```

### 3. Test Edge Cases
- Empty data
- Invalid data
- Missing fields
- Boundary conditions
- Error conditions

### 4. Use Descriptive Names
```python
def test_memory_check_returns_critical_when_usage_above_95_percent(self):
    # Clear what this test verifies
    pass
```

### 5. Mock External Dependencies
Use `requests_mock` for API calls:
```python
def test_api_call(self):
    with requests_mock.Mocker() as m:
        m.post('https://api.example.com/endpoint', json={'data': 'value'})
        # Test code here
```

## Coverage Goals

Aim for:
- **80%+ overall coverage**
- **90%+ for critical paths** (parse, check, discovery functions)
- **100% for error handling** code paths

## Continuous Integration

These tests are designed to run in CI/CD pipelines. They:
- Are fast (most complete in < 1 second)
- Don't require external dependencies
- Use mocking for network calls
- Produce JUnit XML reports for CI systems

## Troubleshooting

### Import Errors
If you get import errors, ensure the project root is in PYTHONPATH:
```bash
export PYTHONPATH=/workspaces/redshift_uctm:$PYTHONPATH
pytest
```

### Coverage Not Working
Install pytest-cov:
```bash
pip install pytest-cov
```

### Tests Not Found
Check that:
- Test files start with `test_`
- Test functions start with `test_`
- Test classes start with `Test`
- You're running pytest from the project root
