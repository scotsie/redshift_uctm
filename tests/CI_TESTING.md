# CI Testing Setup

## Problem

The tests import CheckMK modules (`cmk.agent_based.v2`, `cmk.server_side_calls.v1`) which are only available in a full CheckMK installation. In CI environments (GitHub Actions), these modules don't exist, causing import errors.

## Solution

We use **mock modules** that simulate the CheckMK API for testing purposes.

### How It Works

1. **[tests/mock_cmk.py](mock_cmk.py)** - Contains mock implementations of all CheckMK classes:
   - `State` (OK, WARN, CRIT, UNKNOWN)
   - `Result`, `Metric`, `Service`
   - `AgentSection`, `CheckPlugin`
   - `HostConfig`, `SpecialAgentCommand`
   - `render` helpers

2. **[tests/conftest.py](conftest.py)** - Automatically loads mocks when CheckMK is not available:
   ```python
   try:
       import cmk.agent_based.v2
   except ImportError:
       # CheckMK not installed, use mocks
       from tests import mock_cmk
       # Install mocks into sys.modules
   ```

3. **Tests run unchanged** - No modifications needed to test files

### Mock Classes

All mock classes provide the same interface as real CheckMK classes:

```python
# State enum
State.OK == 0
State.WARN == 1
State.CRIT == 2
State.UNKNOWN == 3
State.worst(State.OK, State.WARN)  # Returns State.WARN

# Result namedtuple
Result(state=State.OK, summary="Test passed", details="...")

# Metric namedtuple
Metric(name="cpu_percent", value=45.5)

# Service namedtuple
Service(item="eth0", parameters={})

# Render helpers
render.bytes(1048576)  # "1.0 MiB"
render.timespan(3600)  # "3600s"
```

## Testing Locally vs CI

### Local Development (with CheckMK)
```bash
pytest  # Uses real CheckMK modules
```

### CI Environment (without CheckMK)
```bash
pytest  # Automatically uses mocks
```

Both produce identical results!

## Verifying Mocks Work

Test the mocks directly:

```bash
python3 -c "
from tests.mock_cmk import State, Result, Metric, render

# Test State
print(f'State.OK = {State.OK}')
print(f'State.worst = {State.worst(State.OK, State.WARN)}')

# Test Result
result = Result(state=State.OK, summary='Test')
print(f'Result: {result}')

# Test Metric
metric = Metric(name='test', value=42)
print(f'Metric: {metric}')

# Test render
print(f'Bytes: {render.bytes(1048576)}')
"
```

## CI Workflow

The GitHub Actions workflow ([.github/workflows/pytest.yml](../.github/workflows/pytest.yml)) automatically:

1. Installs only test dependencies (no CheckMK)
2. Runs pytest
3. Mock modules are loaded automatically
4. Tests pass using mocked CheckMK API

## Adding New CheckMK APIs

If you use new CheckMK classes/functions:

1. Add them to [tests/mock_cmk.py](mock_cmk.py)
2. Ensure they match the real API signature
3. Tests will work in both environments

## Benefits

✅ Tests run in CI without full CheckMK installation
✅ Faster test execution (no heavy dependencies)
✅ No changes needed to existing tests
✅ Same test code works locally and in CI
✅ Easy to maintain and extend
