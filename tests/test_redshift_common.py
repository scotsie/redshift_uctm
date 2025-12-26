#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for redshift_common.py
"""

import pytest
import json
from agent_based.redshift_common import parse_json_section


class TestParseJsonSection:
    """Tests for the parse_json_section function"""

    def test_parse_valid_json_dict(self):
        """Test parsing valid JSON dictionary"""
        data = {"key": "value", "number": 123}
        string_table = [[json.dumps(data)]]

        result = parse_json_section(string_table)

        assert result == data
        assert result["key"] == "value"
        assert result["number"] == 123

    def test_parse_valid_json_list(self):
        """Test parsing valid JSON list"""
        data = [{"type": "A", "value": "1"}, {"type": "B", "value": "2"}]
        string_table = [[json.dumps(data)]]

        result = parse_json_section(string_table)

        assert result == data
        assert len(result) == 2
        assert result[0]["type"] == "A"

    def test_parse_empty_string_table(self):
        """Test parsing empty string_table"""
        result = parse_json_section([])

        assert result is None

    def test_parse_invalid_json(self):
        """Test parsing invalid JSON returns None"""
        string_table = [["this is not valid JSON"]]

        result = parse_json_section(string_table)

        assert result is None

    def test_parse_malformed_string_table(self):
        """Test parsing malformed string_table structure"""
        # Missing inner list
        result = parse_json_section(["invalid"])

        assert result is None

    def test_parse_nested_json(self):
        """Test parsing nested JSON structures"""
        data = {
            "outer": {
                "inner": {
                    "value": 42
                }
            },
            "list": [1, 2, 3]
        }
        string_table = [[json.dumps(data)]]

        result = parse_json_section(string_table)

        assert result == data
        assert result["outer"]["inner"]["value"] == 42
        assert result["list"] == [1, 2, 3]

    def test_parse_unicode_content(self):
        """Test parsing JSON with unicode content"""
        data = {"message": "Hello 世界 🌍"}
        string_table = [[json.dumps(data)]]

        result = parse_json_section(string_table)

        assert result == data
        assert result["message"] == "Hello 世界 🌍"