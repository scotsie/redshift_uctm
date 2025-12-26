#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for redshift_additional.py
"""

import pytest
import json
from cmk.agent_based.v2 import Result, Metric, State, Service

from agent_based.redshift_additional import (
    parse_redshift_processor,
    discover_redshift_processor,
    check_redshift_processor,
    check_redshift_processor_core,
    parse_redshift_memory,
    discover_redshift_memory,
    check_redshift_memory,
    parse_redshift_disk,
    discover_redshift_disk,
    check_redshift_disk,
)


# ============================================================================
# Processor Tests
# ============================================================================

class TestProcessor:
    """Tests for processor statistics functions"""

    def test_parse_processor(self, sample_processor_json):
        """Test parsing processor data"""
        string_table = [[json.dumps(sample_processor_json)]]
        result = parse_redshift_processor(string_table)

        assert result is not None
        assert isinstance(result, list)
        assert len(result) == 3

    def test_discover_processor_aggregate_only(self, sample_processor_json):
        """Test processor discovery - aggregate only"""
        params = {"aggregate": True, "individual": False}
        services = list(discover_redshift_processor(params, sample_processor_json))

        assert len(services) == 1
        # Aggregate service has no item
        assert services[0].item is None

    def test_discover_processor_individual_only(self, sample_processor_json):
        """Test processor discovery - individual cores only"""
        params = {"aggregate": False, "individual": True}
        services = list(discover_redshift_processor(params, sample_processor_json))

        assert len(services) == 2
        items = [s.item for s in services]
        assert "0" in items
        assert "1" in items

    def test_discover_processor_both(self, sample_processor_json):
        """Test processor discovery - both aggregate and individual"""
        params = {"aggregate": True, "individual": True}
        services = list(discover_redshift_processor(params, sample_processor_json))

        assert len(services) == 3  # 1 aggregate + 2 cores

    def test_discover_processor_no_data(self):
        """Test processor discovery with no data"""
        params = {"aggregate": True, "individual": False}
        services = list(discover_redshift_processor(params, None))

        assert len(services) == 0

    def test_check_processor_ok(self, sample_processor_json):
        """Test processor check with normal usage"""
        params = {"util": (80, 90)}
        results = list(check_redshift_processor(params, sample_processor_json))

        metrics = [r for r in results if isinstance(r, Metric)]
        result_objs = [r for r in results if isinstance(r, Result)]

        # Check metrics
        assert any(m.name == "user" for m in metrics)
        assert any(m.name == "system" for m in metrics)
        assert any(m.name == "wait" for m in metrics)
        assert any(m.name == "util" for m in metrics)

        # CPU usage is 100 - 77.4 = 22.6%, should be OK
        assert result_objs[0].state == State.OK
        assert "Total:" in result_objs[0].summary

    def test_check_processor_warn(self):
        """Test processor check with warning level"""
        section = [
            {
                "type": "mpstat",
                "cpu": "all",
                "usr": "70.0",
                "sys": "15.0",
                "iowait": "0.0",
                "idle": "15.0",  # 85% usage
                "nice": "0.0",
                "irq": "0.0",
                "soft": "0.0",
                "steal": "0.0"
            }
        ]
        params = {"util": (80, 90)}
        results = list(check_redshift_processor(params, section))

        result_objs = [r for r in results if isinstance(r, Result)]
        assert result_objs[0].state == State.WARN

    def test_check_processor_crit(self):
        """Test processor check with critical level"""
        section = [
            {
                "type": "mpstat",
                "cpu": "all",
                "usr": "80.0",
                "sys": "15.0",
                "iowait": "0.0",
                "idle": "5.0",  # 95% usage
                "nice": "0.0",
                "irq": "0.0",
                "soft": "0.0",
                "steal": "0.0"
            }
        ]
        params = {"util": (80, 90)}
        results = list(check_redshift_processor(params, section))

        result_objs = [r for r in results if isinstance(r, Result)]
        assert result_objs[0].state == State.CRIT

    def test_check_processor_iowait_warn(self):
        """Test processor check with high I/O wait"""
        section = [
            {
                "type": "mpstat",
                "cpu": "all",
                "usr": "10.0",
                "sys": "5.0",
                "iowait": "25.0",  # High I/O wait
                "idle": "60.0",
                "nice": "0.0",
                "irq": "0.0",
                "soft": "0.0",
                "steal": "0.0"
            }
        ]
        params = {"util": (80, 90), "iowait": (20, 30)}
        results = list(check_redshift_processor(params, section))

        result_objs = [r for r in results if isinstance(r, Result)]
        assert result_objs[0].state == State.WARN

    def test_check_processor_core_ok(self, sample_processor_json):
        """Test individual core check"""
        params = {"util": (80, 90)}
        results = list(check_redshift_processor_core("0", params, sample_processor_json))

        metrics = [r for r in results if isinstance(r, Metric)]
        result_objs = [r for r in results if isinstance(r, Result)]

        # Check core-specific metrics
        assert any(m.name == "cpu_core_util_0" for m in metrics)
        assert any(m.name == "cpu_core_util_user_0" for m in metrics)

        # CPU 0 usage is 100 - 70.2 = 29.8%, should be OK
        assert result_objs[0].state == State.OK

    def test_check_processor_core_not_found(self, sample_processor_json):
        """Test checking non-existent core"""
        params = {"util": (80, 90)}
        results = list(check_redshift_processor_core("99", params, sample_processor_json))

        assert len(results) == 0


# ============================================================================
# Memory Tests
# ============================================================================

class TestMemory:
    """Tests for memory functions"""

    def test_parse_memory(self, sample_memory_json):
        """Test parsing memory data"""
        string_table = [[json.dumps(sample_memory_json)]]
        result = parse_redshift_memory(string_table)

        assert result is not None
        assert isinstance(result, list)

    def test_discover_memory(self, sample_memory_json):
        """Test memory discovery"""
        services = list(discover_redshift_memory(sample_memory_json))

        assert len(services) == 1

    def test_discover_memory_no_data(self):
        """Test memory discovery with no data"""
        services = list(discover_redshift_memory(None))

        assert len(services) == 0

    def test_check_memory_ok(self, sample_memory_json):
        """Test memory check with normal usage"""
        params = {"levels": (80, 90)}
        results = list(check_redshift_memory(params, sample_memory_json))

        metrics = [r for r in results if isinstance(r, Metric)]
        result_objs = [r for r in results if isinstance(r, Result)]

        # Check metrics
        assert any(m.name == "mem_used" for m in metrics)
        assert any(m.name == "mem_total" for m in metrics)
        assert any(m.name == "mem_used_percent" for m in metrics)

        # 3747460 / 16173828 = ~23%, should be OK
        assert result_objs[0].state == State.OK

    def test_check_memory_warn(self):
        """Test memory check with warning level"""
        section = [
            {
                "type": "Mem:",
                "total": "16173828",
                "used": "13747460",  # ~85%
                "free": "2426368",
                "shared": "0",
                "buffers": "0",
                "cached": "0"
            }
        ]
        params = {"levels": (80, 90)}
        results = list(check_redshift_memory(params, section))

        result_objs = [r for r in results if isinstance(r, Result)]
        assert result_objs[0].state == State.WARN

    def test_check_memory_crit(self):
        """Test memory check with critical level"""
        section = [
            {
                "type": "Mem:",
                "total": "16173828",
                "used": "15000000",  # ~93%
                "free": "1173828",
                "shared": "0",
                "buffers": "0",
                "cached": "0"
            }
        ]
        params = {"levels": (80, 90)}
        results = list(check_redshift_memory(params, section))

        result_objs = [r for r in results if isinstance(r, Result)]
        assert result_objs[0].state == State.CRIT


# ============================================================================
# Disk Space Tests
# ============================================================================

class TestDisk:
    """Tests for disk space functions"""

    def test_parse_disk(self, sample_disk_json):
        """Test parsing disk data"""
        string_table = [[json.dumps(sample_disk_json)]]
        result = parse_redshift_disk(string_table)

        assert result is not None
        assert isinstance(result, list)
        assert len(result) == 2

    def test_discover_disk(self, sample_disk_json):
        """Test disk discovery"""
        services = list(discover_redshift_disk(sample_disk_json))

        assert len(services) == 2
        items = [s.item for s in services]
        assert "/" in items
        assert "/var" in items

    def test_discover_disk_no_data(self):
        """Test disk discovery with no data"""
        services = list(discover_redshift_disk(None))

        assert len(services) == 0

    def test_check_disk_ok(self, sample_disk_json):
        """Test disk check with normal usage"""
        params = {"levels": (80, 90)}
        results = list(check_redshift_disk("/", params, sample_disk_json))

        metrics = [r for r in results if isinstance(r, Metric)]
        result_objs = [r for r in results if isinstance(r, Result)]

        # Check metrics
        assert any(m.name == "fs_used" for m in metrics)
        assert any(m.name == "fs_free" for m in metrics)
        assert any(m.name == "fs_size" for m in metrics)
        assert any(m.name == "fs_used_percent" for m in metrics)

        # Usage should be OK
        assert result_objs[0].state == State.OK

    def test_check_disk_warn(self):
        """Test disk check with warning level"""
        section = [
            {
                "filesystem": "/dev/sda1",
                "blocks_1k": "100000000",
                "used": "85000000",  # 85%
                "available": "15000000",
                "use_percent": "85%",
                "mountedOn": "/"
            }
        ]
        params = {"levels": (80, 90)}
        results = list(check_redshift_disk("/", params, section))

        result_objs = [r for r in results if isinstance(r, Result)]
        assert result_objs[0].state == State.WARN

    def test_check_disk_crit(self):
        """Test disk check with critical level"""
        section = [
            {
                "filesystem": "/dev/sda1",
                "blocks_1k": "100000000",
                "used": "95000000",  # 95%
                "available": "5000000",
                "use_percent": "95%",
                "mountedOn": "/"
            }
        ]
        params = {"levels": (80, 90)}
        results = list(check_redshift_disk("/", params, section))

        result_objs = [r for r in results if isinstance(r, Result)]
        assert result_objs[0].state == State.CRIT

    def test_check_disk_not_found(self, sample_disk_json):
        """Test checking non-existent mount point"""
        params = {"levels": (80, 90)}
        results = list(check_redshift_disk("/nonexistent", params, sample_disk_json))

        assert len(results) == 0
