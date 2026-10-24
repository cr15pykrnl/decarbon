"""
Utility functions for fleet decarbonization analysis.

This module contains helper functions for creating base configurations,
scenarios, and data structures used throughout the analysis.
"""

from typing import Dict, Any


def create_base_technologies() -> Dict[str, Dict[str, Any]]:
    """
    Create base technology specifications based on Queensland trial parameters.

    Returns
    -------
    dict
        Dictionary containing specifications for each technology:
        - Diesel (baseline)
        - BEV (Battery Electric Vehicle)
        - FCET (Fuel Cell Electric Truck)
        - Hybrid

    Examples
    --------
    >>> technologies = create_base_technologies()
    >>> technologies['BEV']['initial_cost']
    300000
    """
    return {
        'Diesel': {
            'initial_cost': 150000,
            'annual_operating_cost': 85000,
            'energy_efficiency': 0.35,  # Tank-to-wheel efficiency
            'co2_emission_factor': 2.68,  # kg CO2 per liter diesel
            'range_km': 1200,
            'fuel_cost_per_unit': 1.50,  # AUD per liter
        },
        'BEV': {
            'initial_cost': 300000,
            'annual_operating_cost': 51000,
            'energy_efficiency': 0.85,  # Battery-to-wheel efficiency
            'co2_emission_factor': 0.75,  # kg CO2 per kWh (grid average)
            'range_km': 400,
            'fuel_cost_per_unit': 0.25,  # AUD per kWh
            'battery_degradation_rate': 0.106,  # ~10% per year
        },
        'FCET': {
            'initial_cost': 450000,
            'annual_operating_cost': 68000,
            'energy_efficiency': 0.50,  # Hydrogen-to-wheel efficiency
            'co2_emission_factor': 0.48,  # kg CO2 per kg H2 (green hydrogen)
            'range_km': 600,
            'fuel_cost_per_unit': 8.00,  # AUD per kg H2
        },
        'Hybrid': {
            'initial_cost': 600000,
            'annual_operating_cost': 59500,
            'energy_efficiency': 0.60,  # Combined efficiency
            'co2_emission_factor': 1.07,  # kg CO2 (blended)
            'range_km': 800,
            'fuel_cost_per_unit': 1.20,  # AUD per unit (blended)
        },
    }


def create_base_scenario() -> Dict[str, Any]:
    """
    Create base operational scenario for fleet analysis.

    Returns
    -------
    dict
        Dictionary containing base scenario parameters:
        - Annual kilometers
        - Operating days
        - Vehicle specifications
        - Financial parameters

    Examples
    --------
    >>> scenario = create_base_scenario()
    >>> scenario['annual_km']
    100000
    """
    return {
        'annual_km': 100000,
        'operating_days': 250,
        'vehicle_mass_kg': 18000,
        'average_velocity_kmh': 80,
        'road_grade': 0.0,  # radians (0 = flat)
        'discount_rate': 0.08,  # 8% discount rate
        'analysis_period_years': 5,
        'fuel_price_escalation': 0.03,  # 3% annual increase
        'electricity_price_escalation': 0.02,  # 2% annual increase
    }


def create_uncertainty_params() -> Dict[str, Dict[str, Any]]:
    """
    Create uncertainty parameter specifications for Monte Carlo analysis.

    Returns
    -------
    dict
        Dictionary specifying uncertainty distributions for key parameters

    Examples
    --------
    >>> uncertainty = create_uncertainty_params()
    >>> uncertainty['fuel_price_variation']['std']
    0.20
    """
    return {
        'fuel_price_variation': {
            'type': 'normal',
            'std': 0.20,  # 20% standard deviation
        },
        'electricity_price_variation': {
            'type': 'normal',
            'std': 0.15,  # 15% standard deviation
        },
        'utilization_rate': {
            'type': 'uniform',
            'min': 0.70,  # 70% minimum utilization
            'max': 0.95,  # 95% maximum utilization
        },
        'degradation_uncertainty': {
            'type': 'normal',
            'std': 0.25,  # 25% uncertainty in degradation rate
        },
        'maintenance_cost_variation': {
            'type': 'normal',
            'std': 0.10,  # 10% standard deviation
        },
    }


def calculate_break_even_years(
    initial_cost_new: float,
    initial_cost_baseline: float,
    annual_savings: float,
) -> float:
    """
    Calculate payback period (break-even years) for a technology.

    Parameters
    ----------
    initial_cost_new : float
        Initial cost of new technology
    initial_cost_baseline : float
        Initial cost of baseline technology
    annual_savings : float
        Annual cost savings vs baseline

    Returns
    -------
    float
        Break-even period in years

    Examples
    --------
    >>> calculate_break_even_years(300000, 150000, 34000)
    4.41
    """
    if annual_savings <= 0:
        return float('inf')  # Never breaks even

    additional_investment = initial_cost_new - initial_cost_baseline
    break_even_years = additional_investment / annual_savings

    return break_even_years


def format_currency(amount: float) -> str:
    """
    Format a number as AUD currency string.

    Parameters
    ----------
    amount : float
        Amount to format

    Returns
    -------
    str
        Formatted AUD currency string

    Examples
    --------
    >>> format_currency(150000)
    '$150,000'
    """
    if amount >= 0:
        return f"${amount:,.0f}"
    else:
        return f"-${abs(amount):,.0f}"


def calculate_co2_reduction_percentage(
    baseline_emissions: float,
    new_emissions: float,
) -> float:
    """
    Calculate percentage CO2 reduction vs baseline.

    Parameters
    ----------
    baseline_emissions : float
        Baseline CO2 emissions
    new_emissions : float
        New technology CO2 emissions

    Returns
    -------
    float
        Percentage reduction (positive = reduction, negative = increase)

    Examples
    --------
    >>> calculate_co2_reduction_percentage(100, 28)
    72.0
    """
    if baseline_emissions == 0:
        return 0.0

    reduction = (
        (baseline_emissions - new_emissions) / baseline_emissions
    ) * 100
    return reduction
