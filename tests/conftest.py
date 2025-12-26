#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pytest configuration and shared fixtures for Redshift UCTM tests
"""

import pytest
import sys
from pathlib import Path

# Add the project root to the Python path so we can import modules
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def sample_system_stats_json():
    """Sample system statistics JSON response"""
    return [
        {"type": "Total Memory", "value": "16173828 kB"},
        {"type": "Used Memory", "value": "3747460 kB (23.0%)"},
        {"type": "CPU Usage", "value": "15.2%"},
        {"type": "Days To Expire", "value": "365 days"}
    ]


@pytest.fixture
def sample_system_stats_string_table(sample_system_stats_json):
    """Sample system statistics as CheckMK string_table format"""
    import json
    return [[json.dumps(sample_system_stats_json)]]


@pytest.fixture
def sample_hdd_ethernet_json():
    """Sample HDD and Ethernet usage JSON response"""
    return {
        "HDD Usage Details": {
            "Total Space": "1238542 MB",
            "Used Space": "523456 MB",
            "Used Percentage": "42.3%"
        },
        "Ethernet usage": [
            {
                "Iface": "eth0",
                "Met": "1500",
                "IPAddress": "192.168.1.100",
                "RX-OK": "1234567",
                "TX-OK": "9876543",
                "RX-ERR": "0",
                "TX-ERR": "0",
                "RX-DRP": "0",
                "TX-DRP": "0"
            },
            {
                "Iface": "eth1",
                "Met": "1500",
                "IPAddress": "10.0.0.1",
                "RX-OK": "987654",
                "TX-OK": "654321",
                "RX-ERR": "2",
                "TX-ERR": "1",
                "RX-DRP": "0",
                "TX-DRP": "0"
            }
        ]
    }


@pytest.fixture
def sample_chassis_json():
    """Sample chassis information JSON response"""
    return {
        "info": "Chassis Information",
        "manufacturer": "Dell Inc.",
        "type": "Rack Mount",
        "serialNumber": "ABC123XYZ",
        "boot_upState": "Safe",
        "powerSupplyState": "Safe",
        "thermalState": "Safe",
        "securityStatus": "None",
        "version": "1.0"
    }


@pytest.fixture
def sample_processor_json():
    """Sample processor statistics JSON response"""
    return [
        {
            "type": "mpstat",
            "cpu": "all",
            "usr": "15.2",
            "sys": "5.3",
            "iowait": "2.1",
            "idle": "77.4",
            "nice": "0.0",
            "irq": "0.0",
            "soft": "0.0",
            "steal": "0.0"
        },
        {
            "type": "mpstat",
            "cpu": "0",
            "usr": "20.5",
            "sys": "6.2",
            "iowait": "3.1",
            "idle": "70.2",
            "nice": "0.0",
            "irq": "0.0",
            "soft": "0.0",
            "steal": "0.0"
        },
        {
            "type": "mpstat",
            "cpu": "1",
            "usr": "10.1",
            "sys": "4.5",
            "iowait": "1.2",
            "idle": "84.2",
            "nice": "0.0",
            "irq": "0.0",
            "soft": "0.0",
            "steal": "0.0"
        }
    ]


@pytest.fixture
def sample_memory_json():
    """Sample memory information JSON response"""
    return [
        {
            "type": "Mem:",
            "total": "16173828",
            "used": "3747460",
            "free": "12426368",
            "shared": "123456",
            "buffers": "234567",
            "cached": "345678"
        }
    ]


@pytest.fixture
def sample_disk_json():
    """Sample disk space JSON response"""
    return [
        {
            "filesystem": "/dev/sda1",
            "blocks_1k": "51474912",
            "used": "21789456",
            "available": "29685456",
            "use_percent": "42%",
            "mountedOn": "/"
        },
        {
            "filesystem": "/dev/sda2",
            "blocks_1k": "102400000",
            "used": "51200000",
            "available": "51200000",
            "use_percent": "50%",
            "mountedOn": "/var"
        }
    ]


@pytest.fixture
def sample_uptime_json():
    """Sample uptime JSON response"""
    return {
        "value": "up 45 days, 12:34:56"
    }