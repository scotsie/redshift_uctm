#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for redshift.py main plugin
"""

import json
from cmk.agent_based.v2 import Result, Metric, State, Service

from agent_based.redshift import (
    parse_redshift_system_stats,
    discover_redshift_system_stats,
    check_redshift_system_stats,
    parse_redshift_hdd_ethernet,
    discover_redshift_hdd,
    check_redshift_hdd,
    discover_redshift_interfaces,
    check_redshift_interfaces,
    parse_redshift_chassis,
    discover_redshift_chassis,
    check_redshift_chassis,
    parse_redshift_uptime,
    discover_redshift_uptime,
    check_redshift_uptime,
)


# ============================================================================
# System Statistics Tests
# ============================================================================

class TestSystemStats:
    """Tests for system statistics functions"""

    def test_parse_valid_system_stats(self, sample_system_stats_string_table):
        """Test parsing valid system statistics"""
        result = parse_redshift_system_stats(sample_system_stats_string_table)

        assert result is not None
        assert result["Total Memory"] == "16173828 kB"
        assert result["Used Memory"] == "3747460 kB (23.0%)"
        assert result["CPU Usage"] == "15.2%"

    def test_parse_empty_system_stats(self):
        """Test parsing empty system statistics"""
        result = parse_redshift_system_stats([])

        assert result is None

    def test_parse_invalid_json_system_stats(self):
        """Test parsing invalid JSON"""
        result = parse_redshift_system_stats([["not valid json"]])

        assert result is None

    def test_discover_system_stats_with_data(self):
        """Test discovery with valid data"""
        section = {"Total Memory": "16173828 kB"}
        services = list(discover_redshift_system_stats(section))

        assert len(services) == 1
        assert isinstance(services[0], Service)

    def test_discover_system_stats_no_data(self):
        """Test discovery with no data"""
        services = list(discover_redshift_system_stats(None))

        assert len(services) == 0

    def test_check_system_stats_no_data(self):
        """Test check with no data"""
        results = list(check_redshift_system_stats(None))

        assert len(results) == 1
        assert isinstance(results[0], Result)
        assert results[0].state == State.UNKNOWN

    def test_check_system_stats_memory_ok(self):
        """Test check with normal memory usage"""
        section = {
            "Total Memory": "16173828 kB",
            "Used Memory": "3747460 kB (23.0%)",
        }
        results = list(check_redshift_system_stats(section))

        # Find metrics and results
        metrics = [r for r in results if isinstance(r, Metric)]
        result_objs = [r for r in results if isinstance(r, Result)]

        # Check we have memory metrics
        assert any(m.name == "memory_used" for m in metrics)
        assert any(m.name == "memory_total" for m in metrics)
        assert any(m.name == "memory_used_percent" for m in metrics)

        # Check state is OK for low usage
        memory_result = [r for r in result_objs if "Memory:" in r.summary][0]
        assert memory_result.state == State.OK

    def test_check_system_stats_memory_warn(self):
        """Test check with high memory usage (warning)"""
        section = {
            "Total Memory": "16173828 kB",
            "Used Memory": "14556446 kB (90.0%)",  # Slightly over 90% usage
        }
        results = list(check_redshift_system_stats(section))

        result_objs = [r for r in results if isinstance(r, Result)]
        memory_result = [r for r in result_objs if "Memory:" in r.summary][0]

        assert memory_result.state == State.WARN

    def test_check_system_stats_memory_crit(self):
        """Test check with critical memory usage"""
        section = {
            "Total Memory": "16173828 kB",
            "Used Memory": "15365239 kB (95.0%)",  # 95% usage
        }
        results = list(check_redshift_system_stats(section))

        result_objs = [r for r in results if isinstance(r, Result)]
        memory_result = [r for r in result_objs if "Memory:" in r.summary][0]

        assert memory_result.state == State.CRIT

    def test_check_system_stats_cpu_ok(self):
        """Test check with normal CPU usage"""
        section = {
            "CPU Usage": "45.5%",
        }
        results = list(check_redshift_system_stats(section))

        metrics = [r for r in results if isinstance(r, Metric)]
        result_objs = [r for r in results if isinstance(r, Result)]

        # Check CPU metric
        cpu_metric = [m for m in metrics if m.name == "cpu_percent"][0]
        assert cpu_metric.value == 45.5

        # Check state
        cpu_result = [r for r in result_objs if "CPU:" in r.summary][0]
        assert cpu_result.state == State.OK

    def test_check_system_stats_cpu_warn(self):
        """Test check with high CPU usage"""
        section = {
            "CPU Usage": "85.0%",
        }
        results = list(check_redshift_system_stats(section))

        result_objs = [r for r in results if isinstance(r, Result)]
        cpu_result = [r for r in result_objs if "CPU:" in r.summary][0]

        assert cpu_result.state == State.WARN

    def test_check_system_stats_cpu_crit(self):
        """Test check with critical CPU usage"""
        section = {
            "CPU Usage": "95.0%",
        }
        results = list(check_redshift_system_stats(section))

        result_objs = [r for r in results if isinstance(r, Result)]
        cpu_result = [r for r in result_objs if "CPU:" in r.summary][0]

        assert cpu_result.state == State.CRIT

    def test_check_system_stats_license_info(self):
        """Test check includes license information"""
        section = {
            "Days To Expire": "365 days",
        }
        results = list(check_redshift_system_stats(section))

        result_objs = [r for r in results if isinstance(r, Result)]
        license_result = [r for r in result_objs if "License:" in r.summary][0]

        assert "365 days" in license_result.summary


# ============================================================================
# HDD and Ethernet Tests
# ============================================================================

class TestHDDEthernet:
    """Tests for HDD and Ethernet functions"""

    def test_parse_hdd_ethernet(self, sample_hdd_ethernet_json):
        """Test parsing HDD and Ethernet data"""
        string_table = [[json.dumps(sample_hdd_ethernet_json)]]
        result = parse_redshift_hdd_ethernet(string_table)

        assert result is not None
        assert "HDD Usage Details" in result
        assert "Ethernet usage" in result

    def test_discover_hdd_with_data(self, sample_hdd_ethernet_json):
        """Test HDD discovery with valid data"""
        services = list(discover_redshift_hdd(sample_hdd_ethernet_json))

        assert len(services) == 1

    def test_discover_hdd_no_data(self):
        """Test HDD discovery with no data"""
        services = list(discover_redshift_hdd(None))

        assert len(services) == 0

    def test_check_hdd_ok(self, sample_hdd_ethernet_json):
        """Test HDD check with normal usage"""
        params = {"levels": (80, 90)}
        results = list(check_redshift_hdd(params, sample_hdd_ethernet_json))

        metrics = [r for r in results if isinstance(r, Metric)]
        result_objs = [r for r in results if isinstance(r, Result)]

        # Check metrics
        assert any(m.name == "fs_used" for m in metrics)
        assert any(m.name == "fs_size" for m in metrics)
        assert any(m.name == "fs_used_percent" for m in metrics)

        # Check state (42.3% should be OK)
        assert result_objs[0].state == State.OK
        assert "42.3%" in result_objs[0].summary

    def test_check_hdd_warn(self):
        """Test HDD check with warning level"""
        section = {
            "HDD Usage Details": {
                "Total Space": "1000000 MB",
                "Used Space": "850000 MB",
                "Used Percentage": "85.0%"
            }
        }
        params = {"levels": (80, 90)}
        results = list(check_redshift_hdd(params, section))

        result_objs = [r for r in results if isinstance(r, Result)]
        assert result_objs[0].state == State.WARN

    def test_check_hdd_crit(self):
        """Test HDD check with critical level"""
        section = {
            "HDD Usage Details": {
                "Total Space": "1000000 MB",
                "Used Space": "950000 MB",
                "Used Percentage": "95.0%"
            }
        }
        params = {"levels": (80, 90)}
        results = list(check_redshift_hdd(params, section))

        result_objs = [r for r in results if isinstance(r, Result)]
        assert result_objs[0].state == State.CRIT

    def test_discover_interfaces(self, sample_hdd_ethernet_json):
        """Test interface discovery"""
        services = list(discover_redshift_interfaces(sample_hdd_ethernet_json))

        assert len(services) == 2
        items = [s.item for s in services]
        assert "eth0" in items
        assert "eth1" in items

    def test_check_interface_eth0(self, sample_hdd_ethernet_json):
        """Test checking eth0 interface"""
        results = list(check_redshift_interfaces("eth0", sample_hdd_ethernet_json))

        metrics = [r for r in results if isinstance(r, Metric)]
        result_objs = [r for r in results if isinstance(r, Result)]

        # Check we have metrics
        assert any(m.name == "if_in_pkts" for m in metrics)
        assert any(m.name == "if_out_pkts" for m in metrics)

        # Check summary includes IP address
        assert "192.168.1.100" in result_objs[0].summary

    def test_check_interface_not_found(self, sample_hdd_ethernet_json):
        """Test checking non-existent interface"""
        results = list(check_redshift_interfaces("eth99", sample_hdd_ethernet_json))

        assert len(results) == 0


# ============================================================================
# Chassis Information Tests
# ============================================================================

class TestChassis:
    """Tests for chassis information functions"""

    def test_parse_chassis(self, sample_chassis_json):
        """Test parsing chassis data"""
        string_table = [[json.dumps(sample_chassis_json)]]
        result = parse_redshift_chassis(string_table)

        assert result is not None
        assert result["manufacturer"] == "Dell Inc."

    def test_discover_chassis(self, sample_chassis_json):
        """Test chassis discovery"""
        services = list(discover_redshift_chassis(sample_chassis_json))

        assert len(services) == 1

    def test_check_chassis_ok(self, sample_chassis_json):
        """Test chassis check with all OK states"""
        results = list(check_redshift_chassis(sample_chassis_json))

        result_objs = [r for r in results if isinstance(r, Result)]
        assert len(result_objs) == 1
        assert result_objs[0].state == State.OK
        assert "Dell Inc." in result_objs[0].summary

    def test_check_chassis_critical_state(self):
        """Test chassis check with critical state"""
        section = {
            "manufacturer": "Dell Inc.",
            "type": "Rack Mount",
            "serialNumber": "ABC123",
            "boot_upState": "Safe",
            "powerSupplyState": "Critical",  # Not safe!
            "thermalState": "Safe",
            "securityStatus": "None"
        }
        results = list(check_redshift_chassis(section))

        result_objs = [r for r in results if isinstance(r, Result)]
        assert result_objs[0].state == State.CRIT
        assert "powerSupplyState" in result_objs[0].summary


# ============================================================================
# Uptime Tests
# ============================================================================

class TestUptime:
    """Tests for uptime functions"""

    def test_parse_uptime(self, sample_uptime_json):
        """Test parsing uptime data"""
        string_table = [[json.dumps(sample_uptime_json)]]
        result = parse_redshift_uptime(string_table)

        assert result is not None
        assert "value" in result

    def test_discover_uptime(self, sample_uptime_json):
        """Test uptime discovery"""
        services = list(discover_redshift_uptime(sample_uptime_json))

        assert len(services) == 1

    def test_check_uptime(self, sample_uptime_json):
        """Test uptime check"""
        results = list(check_redshift_uptime(sample_uptime_json))

        result_objs = [r for r in results if isinstance(r, Result)]
        assert len(result_objs) == 1
        assert result_objs[0].state == State.OK
        assert "45 days" in result_objs[0].summary

    def test_check_uptime_no_data(self):
        """Test uptime check with no data"""
        results = list(check_redshift_uptime(None))

        result_objs = [r for r in results if isinstance(r, Result)]
        assert result_objs[0].state == State.UNKNOWN

    def test_check_uptime_capital_value(self):
        """Test uptime with capital 'Value' key"""
        section = {"Value": "up 10 days, 5:30:00"}
        results = list(check_redshift_uptime(section))

        result_objs = [r for r in results if isinstance(r, Result)]
        assert result_objs[0].state == State.OK
        assert "10 days" in result_objs[0].summary
