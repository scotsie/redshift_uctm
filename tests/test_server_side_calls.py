#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for server_side_calls/redshift.py
"""

import pytest
from pydantic import ValidationError

from server_side_calls.redshift import (
    RedshiftParams,
    generate_redshift_command,
)


class MockHostConfig:
    """Mock HostConfig for testing"""

    class MockIPConfig:
        def __init__(self, address):
            self.address = address

    def __init__(self, address="192.168.1.100"):
        self.primary_ip_config = self.MockIPConfig(address)


class TestRedshiftParams:
    """Tests for RedshiftParams model"""

    def test_params_defaults(self):
        """Test default parameter values"""
        params = RedshiftParams()

        assert params.host is None
        assert params.port == 443
        assert params.verify_ssl == "no_verify"
        assert params.timeout == 10
        assert params.sections is None

    def test_params_custom_values(self):
        """Test custom parameter values"""
        params = RedshiftParams(
            host="redshift.example.com",
            port=8443,
            verify_ssl="verify",
            timeout=30,
            sections=["system_stats", "processor"]
        )

        assert params.host == "redshift.example.com"
        assert params.port == 8443
        assert params.verify_ssl == "verify"
        assert params.timeout == 30
        assert params.sections == ["system_stats", "processor"]

    def test_params_from_dict(self):
        """Test creating params from dictionary"""
        data = {
            "host": "10.0.0.1",
            "port": 443,
            "verify_ssl": "no_verify",
            "timeout": 15
        }
        params = RedshiftParams.model_validate(data)

        assert params.host == "10.0.0.1"
        assert params.port == 443
        assert params.timeout == 15


class TestGenerateRedshiftCommand:
    """Tests for generate_redshift_command function"""

    def test_generate_command_minimal(self):
        """Test command generation with minimal parameters"""
        params = RedshiftParams()
        host_config = MockHostConfig("192.168.1.100")

        commands = list(generate_redshift_command(params, host_config))

        assert len(commands) == 1
        cmd = commands[0]

        # Check arguments
        args = cmd.command_arguments
        assert "-H" in args
        assert "192.168.1.100" in args
        assert "-p" in args
        assert "443" in args
        assert "-t" in args
        assert "10" in args
        assert "--verify-ssl" not in args

    def test_generate_command_with_custom_host(self):
        """Test command generation with custom host"""
        params = RedshiftParams(host="custom.example.com")
        host_config = MockHostConfig("192.168.1.100")

        commands = list(generate_redshift_command(params, host_config))

        args = commands[0].command_arguments
        assert "custom.example.com" in args
        assert "192.168.1.100" not in args

    def test_generate_command_with_custom_port(self):
        """Test command generation with custom port"""
        params = RedshiftParams(port=8443)
        host_config = MockHostConfig()

        commands = list(generate_redshift_command(params, host_config))

        args = commands[0].command_arguments
        assert "8443" in args

    def test_generate_command_with_verify_ssl(self):
        """Test command generation with SSL verification enabled"""
        params = RedshiftParams(verify_ssl="verify")
        host_config = MockHostConfig()

        commands = list(generate_redshift_command(params, host_config))

        args = commands[0].command_arguments
        assert "--verify-ssl" in args

    def test_generate_command_without_verify_ssl(self):
        """Test command generation with SSL verification disabled"""
        params = RedshiftParams(verify_ssl="no_verify")
        host_config = MockHostConfig()

        commands = list(generate_redshift_command(params, host_config))

        args = commands[0].command_arguments
        assert "--verify-ssl" not in args

    def test_generate_command_with_timeout(self):
        """Test command generation with custom timeout"""
        params = RedshiftParams(timeout=30)
        host_config = MockHostConfig()

        commands = list(generate_redshift_command(params, host_config))

        args = commands[0].command_arguments
        assert "-t" in args
        assert "30" in args

    def test_generate_command_with_sections(self):
        """Test command generation with specific sections"""
        params = RedshiftParams(sections=["system_stats", "processor", "memory"])
        host_config = MockHostConfig()

        commands = list(generate_redshift_command(params, host_config))

        args = commands[0].command_arguments
        assert "--sections" in args
        assert "system_stats,processor,memory" in args

    def test_generate_command_without_sections(self):
        """Test command generation without sections parameter"""
        params = RedshiftParams()
        host_config = MockHostConfig()

        commands = list(generate_redshift_command(params, host_config))

        args = commands[0].command_arguments
        assert "--sections" not in args

    def test_generate_command_all_parameters(self):
        """Test command generation with all parameters set"""
        params = RedshiftParams(
            host="redshift.example.com",
            port=8443,
            verify_ssl="verify",
            timeout=30,
            sections=["system_stats", "chassis"]
        )
        host_config = MockHostConfig()

        commands = list(generate_redshift_command(params, host_config))

        args = commands[0].command_arguments

        # Verify all parameters are present
        assert "-H" in args
        assert "redshift.example.com" in args
        assert "-p" in args
        assert "8443" in args
        assert "-t" in args
        assert "30" in args
        assert "--verify-ssl" in args
        assert "--sections" in args
        assert "system_stats,chassis" in args
