#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2025 tribe29 GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

"""
CheckMK agent based checks for Redshift Networks UCTM - Additional sections with parameters
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
# Processor Statistics Section
# ============================================================================

def parse_redshift_processor(string_table):
    """Parse processor statistics section"""
    if not string_table:
        return None
    try:
        return json.loads(string_table[0][0])
    except (json.JSONDecodeError, IndexError):
        return None


agent_section_redshift_processor = AgentSection(
    name="redshift_processor",
    parse_function=parse_redshift_processor,
)


def discover_redshift_processor(params: Mapping[str, Any], section) -> DiscoveryResult:
    """Discover processor services based on discovery parameters"""
    if not section or not isinstance(section, list):
        return

    # Get discovery parameters with defaults
    discover_aggregate = params.get("aggregate", True)
    discover_individual = params.get("individual", False)

    # Check if we have the required data
    has_aggregate = False
    cpu_cores = []

    for item in section:
        if item.get("type") == "mpstat":
            if item.get("cpu") == "all":
                has_aggregate = True
            elif item.get("cpu") not in ["all", None]:
                cpu_cores.append(item.get("cpu"))

    # Discover aggregate service
    if discover_aggregate and has_aggregate:
        yield Service()

    # Discover individual CPU core services
    if discover_individual:
        for cpu_id in cpu_cores:
            yield Service(item=str(cpu_id))


def check_redshift_processor(params: Mapping[str, Any], section) -> CheckResult:
    """Check aggregate processor statistics with configurable thresholds"""
    if not section or not isinstance(section, list):
        yield Result(state=State.UNKNOWN, summary="No processor data")
        return

    # Find the 'all' CPU entry
    cpu_all = None
    for item in section:
        if item.get("type") == "mpstat" and item.get("cpu") == "all":
            cpu_all = item
            break

    if not cpu_all:
        yield Result(state=State.UNKNOWN, summary="No aggregate CPU data")
        return

    try:
        usr = float(cpu_all.get("usr", 0))
        sys = float(cpu_all.get("sys", 0))
        iowait = float(cpu_all.get("iowait", 0))
        idle = float(cpu_all.get("idle", 0))
        nice = float(cpu_all.get("nice", 0))
        irq = float(cpu_all.get("irq", 0))
        soft = float(cpu_all.get("soft", 0))
        steal = float(cpu_all.get("steal", 0))
        total_usage = 100.0 - idle

        # Use standard CPU metric names that integrate with existing graphs
        yield Metric("user", usr)
        yield Metric("system", sys)
        yield Metric("wait", iowait)  # Standard name for iowait
        yield Metric("util", total_usage)

        # Additional detailed metrics
        if nice > 0:
            yield Metric("nice", nice)
        if irq > 0:
            yield Metric("interrupt", irq)
        if soft > 0:
            yield Metric("softirq", soft)
        if steal > 0:
            yield Metric("steal", steal)

        # Check against configurable thresholds
        util_levels = params.get("util", (80, 90))
        if isinstance(util_levels, tuple) and len(util_levels) == 2:
            warn, crit = util_levels
            if total_usage >= crit:
                state = State.CRIT
            elif total_usage >= warn:
                state = State.WARN
            else:
                state = State.OK
        else:
            state = State.OK

        # Check I/O wait separately if configured
        iowait_levels = params.get("iowait")
        iowait_state = State.OK
        if iowait_levels and isinstance(iowait_levels, tuple) and len(iowait_levels) == 2:
            warn_io, crit_io = iowait_levels
            if iowait >= crit_io:
                iowait_state = State.CRIT
            elif iowait >= warn_io:
                iowait_state = State.WARN

        # Use the worst state
        final_state = State.worst(state, iowait_state)

        yield Result(
            state=final_state,
            summary=f"Total: {total_usage:.1f}%, User: {usr:.1f}%, System: {sys:.1f}%, Wait: {iowait:.1f}%"
        )
    except (ValueError, TypeError):
        yield Result(state=State.UNKNOWN, summary="Unable to parse CPU data")


def check_redshift_processor_core(item: str, params: Mapping[str, Any], section) -> CheckResult:
    """Check individual CPU core statistics with configurable thresholds"""
    if not section or not isinstance(section, list):
        return

    # Find the specific CPU core entry
    cpu_core = None
    for entry in section:
        if entry.get("type") == "mpstat" and str(entry.get("cpu")) == str(item):
            cpu_core = entry
            break

    if not cpu_core:
        return

    try:
        usr = float(cpu_core.get("usr", 0))
        sys = float(cpu_core.get("sys", 0))
        iowait = float(cpu_core.get("iowait", 0))
        idle = float(cpu_core.get("idle", 0))
        nice = float(cpu_core.get("nice", 0))
        irq = float(cpu_core.get("irq", 0))
        soft = float(cpu_core.get("soft", 0))
        steal = float(cpu_core.get("steal", 0))
        total_usage = 100.0 - idle

        # Use per-core metric naming pattern following CheckMK conventions
        # Format: cpu_core_util_<num> for compatibility with standard graphs
        core_num = str(item)
        yield Metric(f"cpu_core_util_{core_num}", total_usage)
        yield Metric(f"cpu_core_util_user_{core_num}", usr)
        yield Metric(f"cpu_core_util_system_{core_num}", sys)
        yield Metric(f"cpu_core_util_wait_{core_num}", iowait)

        # Check against configurable thresholds
        util_levels = params.get("util", (80, 90))
        if isinstance(util_levels, tuple) and len(util_levels) == 2:
            warn, crit = util_levels
            if total_usage >= crit:
                state = State.CRIT
            elif total_usage >= warn:
                state = State.WARN
            else:
                state = State.OK
        else:
            state = State.OK

        # Check I/O wait separately if configured
        iowait_levels = params.get("iowait")
        iowait_state = State.OK
        if iowait_levels and isinstance(iowait_levels, tuple) and len(iowait_levels) == 2:
            warn_io, crit_io = iowait_levels
            if iowait >= crit_io:
                iowait_state = State.CRIT
            elif iowait >= warn_io:
                iowait_state = State.WARN

        # Use the worst state
        final_state = State.worst(state, iowait_state)

        # Build summary with key metrics
        summary_parts = [f"Total: {total_usage:.1f}%"]
        if usr > 1.0:
            summary_parts.append(f"User: {usr:.1f}%")
        if sys > 1.0:
            summary_parts.append(f"System: {sys:.1f}%")
        if iowait > 1.0:
            summary_parts.append(f"Wait: {iowait:.1f}%")

        yield Result(
            state=final_state,
            summary=", ".join(summary_parts)
        )
    except (ValueError, TypeError):
        yield Result(state=State.UNKNOWN, summary="Unable to parse CPU core data")


check_plugin_redshift_processor = CheckPlugin(
    name="redshift_processor",
    service_name="CPU utilization",
    discovery_function=discover_redshift_processor,
    discovery_ruleset_name="redshift_processor_discovery",
    discovery_default_parameters={"aggregate": True, "individual": False},
    check_function=check_redshift_processor,
    check_default_parameters={"util": (80, 90)},
    check_ruleset_name="redshift_cpu",
)


check_plugin_redshift_processor_core = CheckPlugin(
    name="redshift_processor_core",
    service_name="CPU Core %s",
    discovery_function=discover_redshift_processor,
    discovery_ruleset_name="redshift_processor_discovery",
    discovery_default_parameters={"aggregate": True, "individual": False},
    check_function=check_redshift_processor_core,
    check_default_parameters={"util": (80, 90)},
    check_ruleset_name="redshift_cpu",
)


# ============================================================================
# Memory Section
# ============================================================================

def parse_redshift_memory(string_table):
    """Parse memory section"""
    if not string_table:
        return None
    try:
        return json.loads(string_table[0][0])
    except (json.JSONDecodeError, IndexError):
        return None


agent_section_redshift_memory = AgentSection(
    name="redshift_memory",
    parse_function=parse_redshift_memory,
)


def discover_redshift_memory(section) -> DiscoveryResult:
    """Discover memory service"""
    if section and isinstance(section, list):
        for item in section:
            if item.get("type") == "Mem:":
                yield Service()
                break


def check_redshift_memory(params: Mapping[str, Any], section) -> CheckResult:
    """Check memory usage with configurable thresholds"""
    if not section or not isinstance(section, list):
        yield Result(state=State.UNKNOWN, summary="No memory data")
        return

    mem_data = None
    for item in section:
        if item.get("type") == "Mem:":
            mem_data = item
            break

    if not mem_data:
        yield Result(state=State.UNKNOWN, summary="No memory data")
        return

    try:
        total_bytes = int(mem_data.get("total", 0)) * 1024  # Convert KB to bytes
        free_bytes = int(mem_data.get("free", 0)) * 1024

        if total_bytes == 0:
            yield Result(state=State.UNKNOWN, summary="Invalid memory data")
            return

        used_bytes = total_bytes - free_bytes
        used_percent = (used_bytes / total_bytes * 100) if total_bytes > 0 else 0

        # Use standard memory metric names
        yield Metric("mem_used", used_bytes)
        yield Metric("mem_total", total_bytes)
        yield Metric("mem_used_percent", used_percent)

        # Check against configurable thresholds
        levels = params.get("levels", (80, 90))
        if isinstance(levels, tuple) and len(levels) == 2:
            warn, crit = levels
            if used_percent >= crit:
                state = State.CRIT
            elif used_percent >= warn:
                state = State.WARN
            else:
                state = State.OK
        else:
            state = State.OK

        yield Result(
            state=state,
            summary=f"Usage: {used_percent:.1f}% - {render.bytes(used_bytes)} of {render.bytes(total_bytes)}"
        )
    except (ValueError, TypeError, KeyError):
        yield Result(state=State.UNKNOWN, summary="Unable to parse memory data")


check_plugin_redshift_memory = CheckPlugin(
    name="redshift_memory",
    service_name="Memory",
    discovery_function=discover_redshift_memory,
    check_function=check_redshift_memory,
    check_default_parameters={"levels": (80, 90)},
    check_ruleset_name="redshift_memory",
)


# ============================================================================
# Disk Space Section
# ============================================================================

def parse_redshift_disk(string_table):
    """Parse disk space section"""
    if not string_table:
        return None
    try:
        return json.loads(string_table[0][0])
    except (json.JSONDecodeError, IndexError):
        return None


agent_section_redshift_disk = AgentSection(
    name="redshift_disk",
    parse_function=parse_redshift_disk,
)


def discover_redshift_disk(section) -> DiscoveryResult:
    """Discover disk services"""
    if not section or not isinstance(section, list):
        return

    for item in section:
        if "filesystem" in item and "mountedOn" in item:
            # Use mountpoint as item name
            yield Service(item=item["mountedOn"])


def check_redshift_disk(item: str, params: Mapping[str, Any], section) -> CheckResult:
    """Check disk space with configurable thresholds"""
    if not section or not isinstance(section, list):
        return

    disk_data = None
    for disk in section:
        if disk.get("mountedOn") == item:
            disk_data = disk
            break

    if not disk_data:
        return

    try:
        blocks_1k = int(disk_data.get("blocks_1k", 0))
        used = int(disk_data.get("used", 0))
        available = int(disk_data.get("available", 0))

        # Convert to bytes
        size_bytes = blocks_1k * 1024
        used_bytes = used * 1024
        avail_bytes = available * 1024

        used_percent = (used_bytes / size_bytes * 100) if size_bytes > 0 else 0

        # Use standard filesystem metric names
        yield Metric("fs_used", used_bytes)
        yield Metric("fs_free", avail_bytes)
        yield Metric("fs_size", size_bytes)
        yield Metric("fs_used_percent", used_percent)

        # Check against configurable thresholds
        levels = params.get("levels", (80, 90))
        if isinstance(levels, tuple) and len(levels) == 2:
            warn, crit = levels
            if used_percent >= crit:
                state = State.CRIT
            elif used_percent >= warn:
                state = State.WARN
            else:
                state = State.OK
        else:
            state = State.OK

        yield Result(
            state=state,
            summary=f"{used_percent:.1f}% used ({render.bytes(used_bytes)} of {render.bytes(size_bytes)})"
        )
    except (ValueError, TypeError, KeyError):
        yield Result(state=State.UNKNOWN, summary="Unable to parse disk data")


check_plugin_redshift_disk = CheckPlugin(
    name="redshift_disk",
    service_name="Filesystem %s",
    discovery_function=discover_redshift_disk,
    check_function=check_redshift_disk,
    check_default_parameters={"levels": (80, 90)},
    check_ruleset_name="redshift_disk",
)
