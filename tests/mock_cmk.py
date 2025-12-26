#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mock CheckMK modules for testing in CI environments without full CheckMK installation
"""

from enum import IntEnum
from typing import Any, NamedTuple
from collections.abc import Callable


# Mock cmk.agent_based.v2
class State(IntEnum):
    """Check states"""
    OK = 0
    WARN = 1
    CRIT = 2
    UNKNOWN = 3

    @staticmethod
    def worst(*states):
        """Return the worst state"""
        return max(states) if states else State.OK


class Metric(NamedTuple):
    """Metric data"""
    name: str
    value: float
    levels: tuple = ()
    boundaries: tuple = ()


class Result(NamedTuple):
    """Check result"""
    state: State = State.OK
    summary: str = ""
    notice: str = ""
    details: str = ""


class Service(NamedTuple):
    """Discovered service"""
    item: Any = None
    parameters: dict = {}
    labels: list = []


class AgentSection:
    """Agent section registration"""
    def __init__(self, name: str, parse_function: Callable, **kwargs):
        self.name = name
        self.parse_function = parse_function


class CheckPlugin:
    """Check plugin registration"""
    def __init__(self, name: str, **kwargs):
        self.name = name
        for key, value in kwargs.items():
            setattr(self, key, value)


class HostLabel(NamedTuple):
    """Host label"""
    name: str
    value: str


class render:
    """Rendering helpers"""
    @staticmethod
    def bytes(value):
        """Format bytes"""
        for unit in ['B', 'KiB', 'MiB', 'GiB', 'TiB']:
            if value < 1024.0:
                return f"{value:.1f} {unit}"
            value /= 1024.0
        return f"{value:.1f} PiB"

    @staticmethod
    def timespan(seconds):
        """Format timespan"""
        return f"{seconds}s"


# Mock cmk.server_side_calls.v1
class HostConfig:
    """Host configuration"""
    class IPConfig:
        def __init__(self, address: str):
            self.address = address

    def __init__(self, address: str = "127.0.0.1"):
        self.primary_ip_config = self.IPConfig(address)


class SpecialAgentCommand(NamedTuple):
    """Special agent command"""
    command_arguments: list


class SpecialAgentConfig:
    """Special agent configuration"""
    def __init__(self, name: str, parameter_parser: Callable, commands_function: Callable):
        self.name = name
        self.parameter_parser = parameter_parser
        self.commands_function = commands_function


# Mock cmk.agent_based.v1
class RuleSetType(IntEnum):
    """Ruleset type"""
    MERGED = 1
    ALL = 2
