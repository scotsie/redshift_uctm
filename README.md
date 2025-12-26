# CheckMK Extension for Redshift Networks UCTM

![build](https://github.com/scotsie/redshift_uctm/workflows/build/badge.svg)
![pytest](https://github.com/scotsie/redshift_uctm/workflows/pytest/badge.svg)
![Lint](https://github.com/scotsie/redshift_uctm/workflows/Lint/badge.svg)
![Security](https://github.com/scotsie/redshift_uctm/workflows/Security/badge.svg)
[![codecov](https://codecov.io/gh/scotsie/redshift_uctm/branch/main/graph/badge.svg)](https://codecov.io/gh/scotsie/redshift_uctm)

## Description

This CheckMK 2.3+ extension provides comprehensive monitoring for Redshift Networks UCTM (Unified Communications Threat Management) systems via their REST API.

## Features

The extension monitors the following metrics from Redshift UCTM devices:

- **System Status & Statistics**: Memory usage, CPU utilization, network port status
- **HDD & Ethernet Usage**: Disk space, network interface statistics (RX/TX packets, errors)
- **Chassis Information**: BIOS, hardware details, thermal/power status
- **Processor Statistics**: Aggregate and per-core CPU utilization
- **Memory Usage**: Available memory (RAM, swap, total)
- **Disk Space**: Per-filesystem disk usage
- **System Uptime**: Device uptime information

### Configurable Thresholds

All checks support configurable warning and critical thresholds:
- CPU utilization (aggregate and per-core)
- Memory usage
- Disk space (HDD total and per-filesystem)
- I/O wait times

## Installation

1. **Build the MKP package**:
   - In VSCode: Press `Ctrl+Shift+B`
   - Or run: `.devcontainer/build.sh`

2. **Upload to CheckMK**: Navigate to Setup > Extension Packages

3. **Install the package**: Click install on the uploaded `.mkp` file

## Configuration

1. Navigate to **Setup > VM, Cloud, Container > Redshift UCTM**
2. Add a new datasource rule
3. Configure:
   - Hostname or IP address of the Redshift UCTM device
   - Port (default: 443)
   - SSL verification (optional)
   - Timeout settings
   - Sections to monitor (optional - defaults to all)

### Discovery Options

- **Processor Monitoring**: Choose between aggregate CPU stats, per-core stats, or both
- **Automatic Service Discovery**: All available metrics are discovered automatically

## Development

For the best development experience use [VSCode](https://code.visualstudio.com/) with the [Remote Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) extension. This maps your workspace into a CheckMK docker container, giving you access to the Python environment and libraries the installed extension has.

### Project Structure

```
redshift_uctm/
├── agent_based/          # Agent-based check plugins
│   ├── redshift.py              # Main monitoring plugins
│   ├── redshift_additional.py   # Additional plugins with parameters
│   └── redshift_common.py       # Shared utilities
├── server_side_calls/    # Special agent configuration
│   └── redshift.py
├── libexec/             # Special agent script
│   └── agent_redshift
├── rulesets/            # WATO rulesets for configuration
├── checkman/            # Check manual pages
├── tests/               # Comprehensive test suite (95 tests, 88% coverage)
├── reference/           # API documentation
└── package              # Package metadata
```

### Running Tests

This project includes a comprehensive test suite with **95 tests** achieving **88% code coverage**.

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

See [TESTING.md](TESTING.md) for complete testing documentation.

### Code Quality

```bash
# Run linter
flake8 agent_based/ server_side_calls/ libexec/ tests/

# Run security checks
bandit -r agent_based/ server_side_calls/ libexec/
```

## Continuous Integration

This project uses GitHub Actions for automated testing and quality assurance:

- **pytest**: Runs full test suite on Python 3.11 and 3.12
- **Lint**: Validates code style with flake8
- **Build**: Validates package structure
- **Security**: Scans for vulnerabilities and secrets

All checks run automatically on:
- Every push to `main` or `develop` branches
- Every pull request
- Security scans run weekly

## API Reference

This extension uses the Redshift Networks UCTM REST API v0.6. See the API documentation in [reference/RSN-UCTM-REST-API-Document-v0.6.pdf](reference/RSN-UCTM-REST-API-Document-v0.6.pdf) for details.

### API Endpoints

The special agent collects data from the following endpoints:

- `/rs/rest/systemstatusandstatistics/statsandstatus` - System statistics
- `/rs/rest/ethernet/ethernetUsage` - HDD and Ethernet usage
- `/rs/rest/systemdevicestats/chassisInfo` - Chassis information
- `/rs/rest/systemdevicestats/mpstat` - Processor statistics
- `/rs/rest/systemdevicestats/freespace` - Memory information
- `/rs/rest/systemdevicestats/diskspace` - Disk space
- `/rs/rest/systemdevicestats/uptime` - System uptime

## Troubleshooting

### Common Issues

**No data received from device**
- Verify the device is reachable from the CheckMK server
- Check SSL certificate settings (try disabling SSL verification)
- Verify API is enabled on the Redshift UCTM device
- Check timeout settings (increase if device is slow to respond)

**Services not discovered**
- Run service discovery manually
- Check discovery parameters for processor monitoring
- Verify the special agent is running without errors (check `var/log/`)

**JSON parsing errors**
- The special agent includes automatic cleanup for malformed JSON from the Redshift API
- Check stderr output in CheckMK logs for details

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass: `pytest`
5. Ensure code passes linting: `flake8`
6. Submit a pull request

## Credits

Development setup based on the template by [jiuka](https://github.com/jiuka/checkmk_template).

Special thanks to [Yogibaer75](https://github.com/Yogibaer75) for publicly available CheckMK 2.3.0 plugins that helped fill documentation gaps.

## License

GNU General Public License v2

---

**Developed with**:
- CheckMK 2.3+
- Python 3.11/3.12
- Tested with pytest (95 tests, 88% coverage)
