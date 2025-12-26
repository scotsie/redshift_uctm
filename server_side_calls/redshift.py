#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2025 tribe29 GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

"""
Server-side calls configuration for Redshift Networks UCTM special agent
"""

from collections.abc import Iterator
from pydantic import BaseModel

from cmk.server_side_calls.v1 import (
    HostConfig,
    SpecialAgentCommand,
    SpecialAgentConfig,
)


class RedshiftParams(BaseModel):
    """Parameters for Redshift UCTM special agent"""
    host: str | None = None
    port: int = 443
    verify_ssl: str = "no_verify"
    timeout: int = 10


def generate_redshift_command(
    params: RedshiftParams,
    host_config: HostConfig,
) -> Iterator[SpecialAgentCommand]:
    """Generate command line for Redshift special agent"""

    # Use configured host or fall back to host_config
    target_host = params.host if params.host else host_config.primary_ip_config.address

    args = [
        "-H",
        target_host,
        "-p",
        str(params.port),
        "-t",
        str(params.timeout),
    ]

    if params.verify_ssl == "verify":
        args.append("--verify-ssl")

    yield SpecialAgentCommand(command_arguments=args)


special_agent_redshift = SpecialAgentConfig(
    name="redshift",
    parameter_parser=RedshiftParams.model_validate,
    commands_function=generate_redshift_command,
)
