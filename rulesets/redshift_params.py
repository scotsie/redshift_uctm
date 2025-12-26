#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2025 tribe29 GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

"""
WATO check parameters for Redshift Networks UCTM monitoring
"""

from cmk.rulesets.v1 import Help, Label, Title
from cmk.rulesets.v1.form_specs import (
    BooleanChoice,
    DefaultValue,
    DictElement,
    Dictionary,
    Integer,
    LevelDirection,
    migrate_to_integer_simple_levels,
    SimpleLevels,
)
from cmk.rulesets.v1.rule_specs import CheckParameters, DiscoveryParameters, HostAndItemCondition, Topic


# Processor Discovery Parameters
def _parameter_form_processor_discovery() -> Dictionary:
    return Dictionary(
        title=Title("Processor monitoring discovery"),
        help_text=Help(
            "This rule controls which services will be created for monitoring CPU/processor utilization. "
            "You can choose to monitor the aggregate (all CPUs combined), individual CPU cores, or both."
        ),
        elements={
            "aggregate": DictElement(
                parameter_form=BooleanChoice(
                    title=Title("Discover aggregate CPU utilization service"),
                    help_text=Help(
                        "Create a single service that shows the average utilization across all CPU cores."
                    ),
                    prefill=DefaultValue(True),
                    label=Label("Discover aggregate service"),
                ),
                required=True,
            ),
            "individual": DictElement(
                parameter_form=BooleanChoice(
                    title=Title("Discover individual services for each CPU core"),
                    help_text=Help(
                        "Create separate services for each CPU core, allowing you to monitor per-core "
                        "utilization, identify hotspots, and detect CPU core imbalances."
                    ),
                    prefill=DefaultValue(False),
                    label=Label("Discover individual CPU core services"),
                ),
                required=True,
            ),
        },
    )


rule_spec_redshift_processor_discovery = DiscoveryParameters(
    name="redshift_processor_discovery",
    title=Title("Redshift Processor Discovery"),
    topic=Topic.OPERATING_SYSTEM,
    parameter_form=_parameter_form_processor_discovery,
)


# CPU Utilization Parameters
def _parameter_form_cpu() -> Dictionary:
    return Dictionary(
        title=Title("CPU utilization thresholds"),
        elements={
            "util": DictElement(
                parameter_form=SimpleLevels(
                    title=Title("Total CPU utilization"),
                    level_direction=LevelDirection.UPPER,
                    form_spec_template=Integer(unit_symbol="%"),
                    prefill_fixed_levels=DefaultValue((80, 90)),
                    migrate=migrate_to_integer_simple_levels,
                ),
                required=True,
            ),
            "iowait": DictElement(
                parameter_form=SimpleLevels(
                    title=Title("I/O wait percentage"),
                    level_direction=LevelDirection.UPPER,
                    form_spec_template=Integer(unit_symbol="%"),
                    prefill_fixed_levels=DefaultValue((30, 50)),
                    migrate=migrate_to_integer_simple_levels,
                ),
                required=False,
            ),
        },
    )


rule_spec_redshift_cpu = CheckParameters(
    name="redshift_cpu",
    title=Title("Redshift CPU utilization"),
    topic=Topic.OPERATING_SYSTEM,
    parameter_form=_parameter_form_cpu,
    condition=HostAndItemCondition(item_title=Title("CPU")),
)


# Memory Parameters
def _parameter_form_memory() -> Dictionary:
    return Dictionary(
        title=Title("Memory usage thresholds"),
        elements={
            "levels": DictElement(
                parameter_form=SimpleLevels(
                    title=Title("Memory usage"),
                    level_direction=LevelDirection.UPPER,
                    form_spec_template=Integer(unit_symbol="%"),
                    prefill_fixed_levels=DefaultValue((80, 90)),
                    migrate=migrate_to_integer_simple_levels,
                ),
                required=True,
            ),
        },
    )


rule_spec_redshift_memory = CheckParameters(
    name="redshift_memory",
    title=Title("Redshift Memory usage"),
    topic=Topic.OPERATING_SYSTEM,
    parameter_form=_parameter_form_memory,
    condition=HostAndItemCondition(item_title=Title("Memory")),
)


# Filesystem Parameters
def _parameter_form_filesystem() -> Dictionary:
    return Dictionary(
        title=Title("Filesystem usage thresholds"),
        elements={
            "levels": DictElement(
                parameter_form=SimpleLevels(
                    title=Title("Filesystem usage"),
                    level_direction=LevelDirection.UPPER,
                    form_spec_template=Integer(unit_symbol="%"),
                    prefill_fixed_levels=DefaultValue((80, 90)),
                    migrate=migrate_to_integer_simple_levels,
                ),
                required=True,
            ),
        },
    )


rule_spec_redshift_disk = CheckParameters(
    name="redshift_disk",
    title=Title("Redshift Disk/Filesystem usage"),
    topic=Topic.STORAGE,
    parameter_form=_parameter_form_filesystem,
    condition=HostAndItemCondition(item_title=Title("Mount point")),
)


rule_spec_redshift_hdd = CheckParameters(
    name="redshift_hdd",
    title=Title("Redshift HDD aggregate usage"),
    topic=Topic.STORAGE,
    parameter_form=_parameter_form_filesystem,
    condition=HostAndItemCondition(item_title=Title("HDD")),
)
