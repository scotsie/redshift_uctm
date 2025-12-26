#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2024 tribe29 GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

"""
Common utilities for Redshift UCTM monitoring plugin
"""

import json
from typing import Any


def parse_json_section(string_table: list) -> Any | None:
    """
    Generic JSON parser for Redshift agent sections.

    This handles the standard case where the special agent has already
    cleaned up any malformed JSON from the Redshift API.

    Args:
        string_table: CheckMK string table from agent section

    Returns:
        Parsed JSON data structure, or None if parsing fails
    """
    if not string_table:
        return None
    try:
        return json.loads(string_table[0][0])
    except (json.JSONDecodeError, IndexError):
        return None
