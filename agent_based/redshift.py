#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2025 tribe29 GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

"""
CheckMK agent based checks for Redshift Networks UCTM
"""

import json
from typing import Any, Mapping
from cmk.agent_based.v2 import (
    AgentSection,
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    Metric,
    Result,
    Service,
    State,
    render,
)


# ============================================================================
# System Statistics Section
# ============================================================================

def parse_redshift_system_stats(string_table):
    """Parse system statistics section"""
    if not string_table:
        return None
    try:
        return json.loads(string_table[0][0])
    except (json.JSONDecodeError, IndexError):
        return None


agent_section_redshift_system_stats = AgentSection(
    name="redshift_system_stats",
    parse_function=parse_redshift_system_stats,
)


def discover_redshift_system_stats(section) -> DiscoveryResult:
    """Discover system stats service"""
    if section:
        yield Service()


def check_redshift_system_stats(section) -> CheckResult:
    """Check system statistics"""
    if not section:
        yield Result(state=State.UNKNOWN, summary="No data received")
        return

    # Memory metrics
    if "Total Memory" in section and "Used Memory" in section:
        total_mem_str = section["Total Memory"]
        used_mem_str = section["Used Memory"]

        # Parse memory values (e.g., "16173828 kB" or "3747460 kB (23.0%)")
        try:
            total_mem = int(total_mem_str.split()[0])
            used_mem_parts = used_mem_str.split()
            used_mem = int(used_mem_parts[0])

            used_percent = (used_mem / total_mem * 100) if total_mem > 0 else 0

            yield Metric("memory_used", used_mem * 1024)  # Convert kB to bytes
            yield Metric("memory_total", total_mem * 1024)
            yield Metric("memory_used_percent", used_percent)

            yield Result(
                state=State.OK if used_percent < 90 else State.WARN if used_percent < 95 else State.CRIT,
                summary=f"Memory: {render.bytes(used_mem * 1024)} of {render.bytes(total_mem * 1024)} ({used_percent:.1f}%)"
            )
        except (ValueError, IndexError):
            pass

    # CPU usage
    if "CPU Usage" in section:
        cpu_usage_str = section["CPU Usage"]
        try:
            cpu_usage = float(cpu_usage_str.rstrip('%'))
            yield Metric("cpu_percent", cpu_usage)
            yield Result(
                state=State.OK if cpu_usage < 80 else State.WARN if cpu_usage < 90 else State.CRIT,
                summary=f"CPU: {cpu_usage:.1f}%"
            )
        except ValueError:
            pass

    # License info
    if "Days To Expire" in section:
        license_info = section["Days To Expire"]
        yield Result(state=State.OK, summary=f"License: {license_info}")


check_plugin_redshift_system_stats = CheckPlugin(
    name="redshift_system_stats",
    service_name="Redshift System Stats",
    discovery_function=discover_redshift_system_stats,
    check_function=check_redshift_system_stats,
)


# ============================================================================
# HDD and Ethernet Section
# ============================================================================

def parse_redshift_hdd_ethernet(string_table):
    """Parse HDD and Ethernet usage section"""
    if not string_table:
        return None
    try:
        return json.loads(string_table[0][0])
    except (json.JSONDecodeError, IndexError):
        return None


agent_section_redshift_hdd_ethernet = AgentSection(
    name="redshift_hdd_ethernet",
    parse_function=parse_redshift_hdd_ethernet,
)


def discover_redshift_hdd(section) -> DiscoveryResult:
    """Discover HDD service"""
    if section and "HDD Usage Details" in section:
        yield Service()


def check_redshift_hdd(section) -> CheckResult:
    """Check HDD usage"""
    if not section or "HDD Usage Details" not in section:
        yield Result(state=State.UNKNOWN, summary="No HDD data")
        return

    hdd = section["HDD Usage Details"]

    # Parse disk usage
    if "Total Space" in hdd and "Used Space" in hdd and "Used Percentage" in hdd:
        total_space = hdd["Total Space"]
        used_space = hdd["Used Space"]
        used_percent_str = hdd["Used Percentage"]

        try:
            used_percent = float(used_percent_str.rstrip('%'))
            yield Metric("disk_used_percent", used_percent)

            yield Result(
                state=State.OK if used_percent < 80 else State.WARN if used_percent < 90 else State.CRIT,
                summary=f"Disk: {used_space} of {total_space} ({used_percent:.1f}%)"
            )
        except ValueError:
            yield Result(state=State.OK, summary=f"Disk: {used_space} of {total_space}")


check_plugin_redshift_hdd = CheckPlugin(
    name="redshift_hdd",
    service_name="Redshift HDD",
    discovery_function=discover_redshift_hdd,
    check_function=check_redshift_hdd,
)


def discover_redshift_interfaces(section) -> DiscoveryResult:
    """Discover network interfaces"""
    if not section or "Ethernet usage" not in section:
        return

    interfaces = section["Ethernet usage"]
    for interface in interfaces:
        if "Iface" in interface:
            yield Service(item=interface["Iface"])


def check_redshift_interfaces(item: str, section) -> CheckResult:
    """Check network interface"""
    if not section or "Ethernet usage" not in section:
        return

    interfaces = section["Ethernet usage"]
    iface_data = None

    for interface in interfaces:
        if interface.get("Iface") == item:
            iface_data = interface
            break

    if not iface_data:
        return

    # Interface status
    met = iface_data.get("Met", "unknown")
    ip_addr = iface_data.get("IPAddress", "n/a")

    yield Result(state=State.OK, summary=f"Status: {met}, IP: {ip_addr}")

    # Traffic counters
    for key, metric_name, label in [
        ("RX-OK", "if_in_pkts", "RX packets"),
        ("TX-OK", "if_out_pkts", "TX packets"),
        ("RX-ERR", "if_in_errors", "RX errors"),
        ("TX-ERR", "if_out_errors", "TX errors"),
        ("RX-DRP", "if_in_discards", "RX dropped"),
        ("TX-DRP", "if_out_discards", "TX dropped"),
    ]:
        if key in iface_data:
            try:
                value = int(iface_data[key])
                yield Metric(metric_name, value)
            except ValueError:
                pass


check_plugin_redshift_interfaces = CheckPlugin(
    name="redshift_interfaces",
    service_name="Redshift Interface %s",
    discovery_function=discover_redshift_interfaces,
    check_function=check_redshift_interfaces,
)


# ============================================================================
# Chassis Information Section
# ============================================================================

def parse_redshift_chassis(string_table):
    """Parse chassis information section"""
    if not string_table:
        return None
    try:
        return json.loads(string_table[0][0])
    except (json.JSONDecodeError, IndexError):
        return None


agent_section_redshift_chassis = AgentSection(
    name="redshift_chassis",
    parse_function=parse_redshift_chassis,
)


def discover_redshift_chassis(section) -> DiscoveryResult:
    """Discover chassis service"""
    if section:
        yield Service()


def check_redshift_chassis(section) -> CheckResult:
    """Check chassis information"""
    if not section:
        yield Result(state=State.UNKNOWN, summary="No chassis data")
        return

    info_parts = []

    for key in ["manufacturer", "type", "version", "serialNumber"]:
        if key in section:
            info_parts.append(f"{key.title()}: {section[key]}")

    if info_parts:
        yield Result(state=State.OK, summary=", ".join(info_parts))
    else:
        yield Result(state=State.OK, summary="Chassis info available")


check_plugin_redshift_chassis = CheckPlugin(
    name="redshift_chassis",
    service_name="Redshift Chassis Info",
    discovery_function=discover_redshift_chassis,
    check_function=check_redshift_chassis,
)


# ============================================================================
# Uptime Section
# ============================================================================

def parse_redshift_uptime(string_table):
    """Parse uptime section"""
    if not string_table:
        return None
    try:
        return json.loads(string_table[0][0])
    except (json.JSONDecodeError, IndexError):
        return None


agent_section_redshift_uptime = AgentSection(
    name="redshift_uptime",
    parse_function=parse_redshift_uptime,
)


def discover_redshift_uptime(section) -> DiscoveryResult:
    """Discover uptime service"""
    if section:
        yield Service()


def check_redshift_uptime(section) -> CheckResult:
    """Check system uptime"""
    if not section or "Value" not in section:
        yield Result(state=State.UNKNOWN, summary="No uptime data")
        return

    uptime_str = section["Value"]
    yield Result(state=State.OK, summary=f"Uptime: {uptime_str}")


check_plugin_redshift_uptime = CheckPlugin(
    name="redshift_uptime",
    service_name="Redshift Uptime",
    discovery_function=discover_redshift_uptime,
    check_function=check_redshift_uptime,
)
