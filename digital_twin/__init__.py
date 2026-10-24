"""
Digital Twin - Fleet Decarbonization Analysis

A Python package for analyzing heavy transport fleet decarbonization using
mathematical models and risk analysis.
"""

__version__ = "0.1.0"
__author__ = "Digital Twin Team"
__description__ = "Fleet Decarbonization Analysis - Digital Twin"

from digital_twin.models import (
    calculate_energy_consumption,
    calculate_battery_degradation,
    calculate_npv,
    GRAVITY_ACCELERATION,
    ROLLING_RESISTANCE_COEFF,
    DEFAULT_DRAG_COEFFICIENT,
)

from digital_twin.utils import (
    create_base_technologies,
    create_base_scenario,
)

__all__ = [
    "calculate_energy_consumption",
    "calculate_battery_degradation",
    "calculate_npv",
    "create_base_technologies",
    "create_base_scenario",
    "GRAVITY_ACCELERATION",
    "ROLLING_RESISTANCE_COEFF",
    "DEFAULT_DRAG_COEFFICIENT",
]
