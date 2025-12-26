#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for the agent_redshift special agent
"""

import pytest
import json
import requests
import requests_mock
import sys
import importlib.util

# Import the agent module dynamically since it doesn't have .py extension
from pathlib import Path
from importlib.machinery import SourceFileLoader

agent_path = Path(__file__).parent.parent / "libexec" / "agent_redshift"
loader = SourceFileLoader("agent_redshift", str(agent_path))
agent_redshift = loader.load_module()
sys.modules['agent_redshift'] = agent_redshift

# Import the required functions and classes
RedshiftAPI = agent_redshift.RedshiftAPI
parse_arguments = agent_redshift.parse_arguments
output_section = agent_redshift.output_section
main = agent_redshift.main


class TestRedshiftAPI:
    """Tests for RedshiftAPI class"""

    def test_init_default_params(self):
        """Test API initialization with default parameters"""
        api = RedshiftAPI(host="redshift.example.com")

        assert api.base_url == "https://redshift.example.com:443/rs/rest"
        assert api.verify_ssl is False
        assert api.timeout == 10

    def test_init_custom_params(self):
        """Test API initialization with custom parameters"""
        api = RedshiftAPI(
            host="10.0.0.1",
            port=8443,
            verify_ssl=True,
            timeout=30
        )

        assert api.base_url == "https://10.0.0.1:8443/rs/rest"
        assert api.verify_ssl is True
        assert api.timeout == 30

    def test_make_request_success(self):
        """Test successful API request"""
        api = RedshiftAPI(host="redshift.example.com")

        with requests_mock.Mocker() as m:
            response_data = {"status": "ok", "value": "test"}
            m.post(
                "https://redshift.example.com:443/rs/rest/test/endpoint",
                json=response_data
            )

            result = api._make_request("test/endpoint")

            assert result == response_data

    def test_make_request_with_trailing_comma(self):
        """Test API request with malformed JSON (trailing comma)"""
        api = RedshiftAPI(host="redshift.example.com")

        with requests_mock.Mocker() as m:
            # Malformed JSON with trailing comma
            malformed_json = '{"status": "ok", "value": "test",}'
            m.post(
                "https://redshift.example.com:443/rs/rest/test/endpoint",
                text=malformed_json
            )

            result = api._make_request("test/endpoint")

            # Should clean and parse successfully
            assert result == {"status": "ok", "value": "test"}

    def test_make_request_with_leading_comma_in_array(self):
        """Test API request with malformed JSON (leading comma in array)"""
        api = RedshiftAPI(host="redshift.example.com")

        with requests_mock.Mocker() as m:
            # Malformed JSON with leading comma in array
            malformed_json = '[,{"type": "test"}]'
            m.post(
                "https://redshift.example.com:443/rs/rest/test/endpoint",
                text=malformed_json
            )

            result = api._make_request("test/endpoint")

            # Should clean and parse successfully
            assert result == [{"type": "test"}]

    def test_make_request_connection_error(self):
        """Test API request with connection error"""
        api = RedshiftAPI(host="nonexistent.example.com")

        with requests_mock.Mocker() as m:
            m.post(
                "https://nonexistent.example.com:443/rs/rest/test/endpoint",
                exc=requests.exceptions.ConnectionError
            )

            result = api._make_request("test/endpoint")

            assert result is None

    def test_make_request_timeout(self):
        """Test API request with timeout"""
        api = RedshiftAPI(host="redshift.example.com", timeout=1)

        with requests_mock.Mocker() as m:
            m.post(
                "https://redshift.example.com:443/rs/rest/test/endpoint",
                exc=requests.exceptions.Timeout
            )

            result = api._make_request("test/endpoint")

            assert result is None

    def test_make_request_http_error(self):
        """Test API request with HTTP error"""
        api = RedshiftAPI(host="redshift.example.com")

        with requests_mock.Mocker() as m:
            m.post(
                "https://redshift.example.com:443/rs/rest/test/endpoint",
                status_code=500
            )

            result = api._make_request("test/endpoint")

            assert result is None

    def test_get_system_stats(self):
        """Test get_system_stats endpoint"""
        api = RedshiftAPI(host="redshift.example.com")

        with requests_mock.Mocker() as m:
            response_data = [{"type": "CPU Usage", "value": "15.2%"}]
            m.post(
                "https://redshift.example.com:443/rs/rest/systemstatusandstatistics/statsandstatus",
                json=response_data
            )

            result = api.get_system_stats()

            assert result == response_data

    def test_get_hdd_ethernet_usage(self):
        """Test get_hdd_ethernet_usage endpoint"""
        api = RedshiftAPI(host="redshift.example.com")

        with requests_mock.Mocker() as m:
            response_data = {"HDD Usage Details": {}}
            m.post(
                "https://redshift.example.com:443/rs/rest/ethernet/ethernetUsage",
                json=response_data
            )

            result = api.get_hdd_ethernet_usage()

            assert result == response_data

    def test_get_chassis_info(self):
        """Test get_chassis_info endpoint"""
        api = RedshiftAPI(host="redshift.example.com")

        with requests_mock.Mocker() as m:
            response_data = {"manufacturer": "Test Inc."}
            m.post(
                "https://redshift.example.com:443/rs/rest/systemdevicestats/chassisInfo",
                json=response_data
            )

            result = api.get_chassis_info()

            assert result == response_data


class TestParseArguments:
    """Tests for command-line argument parsing"""

    def test_parse_minimal_args(self):
        """Test parsing minimal required arguments"""
        args = parse_arguments(["-H", "redshift.example.com"])

        assert args.host == "redshift.example.com"
        assert args.port == 443
        assert args.verify_ssl is False
        assert args.timeout == 10

    def test_parse_all_args(self):
        """Test parsing all arguments"""
        args = parse_arguments([
            "-H", "10.0.0.1",
            "-p", "8443",
            "--verify-ssl",
            "-t", "30",
            "--debug",
            "--sections", "system_stats,processor"
        ])

        assert args.host == "10.0.0.1"
        assert args.port == 8443
        assert args.verify_ssl is True
        assert args.timeout == 30
        assert args.debug is True
        assert args.sections == "system_stats,processor"

    def test_parse_missing_host(self):
        """Test parsing without required host argument"""
        with pytest.raises(SystemExit):
            parse_arguments([])

    def test_parse_custom_port(self):
        """Test parsing custom port"""
        args = parse_arguments(["-H", "test.com", "-p", "9443"])

        assert args.port == 9443

    def test_parse_custom_timeout(self):
        """Test parsing custom timeout"""
        args = parse_arguments(["-H", "test.com", "-t", "60"])

        assert args.timeout == 60


class TestOutputSection:
    """Tests for output_section function"""

    def test_output_section_dict(self, capsys):
        """Test outputting a section with dictionary data"""
        data = {"key": "value", "number": 123}
        output_section("test_section", data)

        captured = capsys.readouterr()
        lines = captured.out.strip().split('\n')

        assert lines[0] == "<<<redshift_test_section:sep(0)>>>"
        assert json.loads(lines[1]) == data

    def test_output_section_list(self, capsys):
        """Test outputting a section with list data"""
        data = [{"type": "A"}, {"type": "B"}]
        output_section("test_section", data)

        captured = capsys.readouterr()
        lines = captured.out.strip().split('\n')

        assert lines[0] == "<<<redshift_test_section:sep(0)>>>"
        assert json.loads(lines[1]) == data


class TestMain:
    """Tests for main function"""

    def test_main_success(self, capsys):
        """Test successful execution of main"""
        with requests_mock.Mocker() as m:
            # Mock all API endpoints
            m.post(
                "https://redshift.example.com:443/rs/rest/systemstatusandstatistics/statsandstatus",
                json=[{"type": "CPU Usage", "value": "15%"}]
            )
            m.post(
                "https://redshift.example.com:443/rs/rest/ethernet/ethernetUsage",
                json={"HDD Usage Details": {}}
            )
            m.post(
                "https://redshift.example.com:443/rs/rest/systemdevicestats/chassisInfo",
                json={"manufacturer": "Test"}
            )
            m.post(
                "https://redshift.example.com:443/rs/rest/systemdevicestats/mpstat",
                json=[{"cpu": "all"}]
            )
            m.post(
                "https://redshift.example.com:443/rs/rest/systemdevicestats/freespace",
                json=[{"type": "Mem:"}]
            )
            m.post(
                "https://redshift.example.com:443/rs/rest/systemdevicestats/diskspace",
                json=[{"mountedOn": "/"}]
            )
            m.post(
                "https://redshift.example.com:443/rs/rest/systemdevicestats/uptime",
                json={"value": "up 1 day"}
            )

            result = main(["-H", "redshift.example.com"])

            assert result == 0

            captured = capsys.readouterr()
            output = captured.out

            # Check that sections are output
            assert "<<<redshift_system_stats:sep(0)>>>" in output
            assert "<<<redshift_hdd_ethernet:sep(0)>>>" in output
            assert "<<<redshift_chassis:sep(0)>>>" in output

    def test_main_with_sections_filter(self, capsys):
        """Test main with sections filter"""
        with requests_mock.Mocker() as m:
            m.post(
                "https://redshift.example.com:443/rs/rest/systemstatusandstatistics/statsandstatus",
                json=[{"type": "CPU Usage"}]
            )

            result = main([
                "-H", "redshift.example.com",
                "--sections", "system_stats"
            ])

            assert result == 0

            captured = capsys.readouterr()
            output = captured.out

            # Only system_stats section should be output
            assert "<<<redshift_system_stats:sep(0)>>>" in output
            assert "<<<redshift_chassis:sep(0)>>>" not in output

    def test_main_with_failed_endpoint(self, capsys):
        """Test main with one failed endpoint"""
        with requests_mock.Mocker() as m:
            # Success
            m.post(
                "https://redshift.example.com:443/rs/rest/systemstatusandstatistics/statsandstatus",
                json=[{"type": "CPU Usage"}]
            )
            # Failure
            m.post(
                "https://redshift.example.com:443/rs/rest/ethernet/ethernetUsage",
                status_code=500
            )
            # Success
            m.post(
                "https://redshift.example.com:443/rs/rest/systemdevicestats/chassisInfo",
                json={"manufacturer": "Test"}
            )
            m.post(
                "https://redshift.example.com:443/rs/rest/systemdevicestats/mpstat",
                json=[{"cpu": "all"}]
            )
            m.post(
                "https://redshift.example.com:443/rs/rest/systemdevicestats/freespace",
                json=[{"type": "Mem:"}]
            )
            m.post(
                "https://redshift.example.com:443/rs/rest/systemdevicestats/diskspace",
                json=[{"mountedOn": "/"}]
            )
            m.post(
                "https://redshift.example.com:443/rs/rest/systemdevicestats/uptime",
                json={"value": "up 1 day"}
            )

            result = main(["-H", "redshift.example.com"])

            # Should still succeed even if one endpoint fails
            assert result == 0

            captured = capsys.readouterr()
            output = captured.out

            # Successful sections should be present
            assert "<<<redshift_system_stats:sep(0)>>>" in output
            # Failed section should not be present
            assert "<<<redshift_hdd_ethernet:sep(0)>>>" not in output
