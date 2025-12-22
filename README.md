# CheckMK Extension for Redshift Networks UCTM

## Description

This CheckMK 2.3 extension provides monitoring for Redshift Networks UCTM (Unified Communications Threat Management) systems via their REST API.

## Features

The extension monitors the following metrics from Redshift UCTM devices:

- **System Status & Statistics**: Memory usage, CPU utilization, network port status
- **HDD & Ethernet Usage**: Disk space, network interface statistics (RX/TX packets, errors)
- **Chassis Information**: BIOS, hardware details
- **Processor Statistics**: Per-processor CPU utilization
- **Free Memory**: Available memory (mem, swap, total)
- **System Uptime**: Device uptime information

## Installation

1. Build the MKP package: `Ctrl+Shift+B` in VSCode or run `.devcontainer/build.sh`
2. Upload the `.mkp` file to your CheckMK instance via Setup > Extension Packages
3. Install the package

## Configuration

1. Navigate to Setup > VM, Cloud, Container > Redshift UCTM
2. Add a new datasource rule
3. Configure:
   - Hostname or IP address of the Redshift UCTM device
   - Authentication credentials (if required)
   - Port (default: 443)

## Development

For development, use [VSCode](https://code.visualstudio.com/) with the [Remote Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) extension. This maps your workspace into a CheckMK docker container.

## API Reference

This extension uses the Redshift Networks UCTM REST API v0.6. See the API documentation in [reference/RSN-UCTM-REST-API-Document-v0.6.pdf](reference/RSN-UCTM-REST-API-Document-v0.6.pdf) for details.

## License

[Add your license here]
