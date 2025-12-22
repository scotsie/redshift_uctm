#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2025 tribe29 GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

"""
WATO rulesets for Redshift Networks UCTM monitoring
"""

from cmk.rulesets.v1 import Help, Title
from cmk.rulesets.v1.form_specs import (
    DefaultValue,
    DictElement,
    Dictionary,
    Integer,
    SingleChoice,
    SingleChoiceElement,
    String,
    validators,
)
from cmk.rulesets.v1.rule_specs import SpecialAgent, Topic


def _parameter_form() -> Dictionary:
    """Form specification for Redshift UCTM parameters"""
    return Dictionary(
        title=Title("Redshift Networks UCTM"),
        help_text=Help(
            "This rule configures the special agent for monitoring "
            "Redshift Networks UCTM devices via REST API."
        ),
        elements={
            "host": DictElement(
                parameter_form=String(
                    title=Title("Custom hostname or IP address"),
                    help_text=Help(
                        "If specified, use this hostname or IP address instead of the host's "
                        "configured IP address. Leave empty to use the host's IP address."
                    ),
                    custom_validate=(validators.LengthInRange(min_value=1),),
                ),
                required=False,
            ),
            "port": DictElement(
                parameter_form=Integer(
                    title=Title("TCP Port"),
                    help_text=Help("Port number for HTTPS connection to the Redshift UCTM device."),
                    prefill=DefaultValue(443),
                    custom_validate=(validators.NetworkPort(),),
                ),
                required=True,
            ),
            "verify_ssl": DictElement(
                parameter_form=SingleChoice(
                    title=Title("SSL certificate verification"),
                    help_text=Help(
                        "Whether to verify SSL certificates. "
                        "Disable for self-signed certificates."
                    ),
                    elements=[
                        SingleChoiceElement(
                            name=False,
                            title=Title("Do not verify SSL certificate (default)"),
                        ),
                        SingleChoiceElement(
                            name=True,
                            title=Title("Verify SSL certificate"),
                        ),
                    ],
                    prefill=DefaultValue(False),
                ),
                required=True,
            ),
            "timeout": DictElement(
                parameter_form=Integer(
                    title=Title("Timeout"),
                    help_text=Help("Timeout for API requests in seconds."),
                    prefill=DefaultValue(10),
                    custom_validate=(validators.NumberInRange(min_value=1, max_value=300),),
                ),
                required=True,
            ),
        },
    )


rule_spec_special_agent_redshift = SpecialAgent(
    name="redshift",
    title=Title("Redshift Networks UCTM"),
    topic=Topic.CLOUD,
    parameter_form=_parameter_form,
)
