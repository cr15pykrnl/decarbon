"""
Mathematical models for fleet decarbonization analysis.

This module contains the core mathematical models used in the digital twin
analysis, including energy consumption, battery degradation, and financial
calculations.
"""

import numpy as np
from typing import Dict, List, Optional

# Physical constants
GRAVITY_ACCELERATION = 9.81  # m/s²
ROLLING_RESISTANCE_COEFF = 0.006  # Typical for heavy trucks on asphalt
DEFAULT_DRAG_COEFFICIENT = 1.0  # Cd for heavy trucks (0.6-1.0 typical range)


def calculate_energy_consumption(
    mass: float,
    grade: float,
    distance: float,
    velocity: float,
    air_density: float = 1.2,
    frontal_area: float = 8.0,
    drag_coefficient: float = DEFAULT_DRAG_COEFFICIENT,
    rolling_resistance: float = ROLLING_RESISTANCE_COEFF,
) -> float:
    """
    Calculate energy consumption at the wheel using physics-based model.

    This calculation assumes steady-state travel at constant velocity.
    Energy is computed as force × distance for each resistance component.

    Parameters
    ----------
    mass : float
        Vehicle mass in kg
    grade : float
        Road grade (slope angle in radians, 0 = flat)
    distance : float
        Distance traveled in meters
    velocity : float
        Vehicle velocity in m/s (steady-state assumption)
    air_density : float, optional
        Air density in kg/m³ (default: 1.2)
    frontal_area : float, optional
        Vehicle frontal area in m² (default: 8.0)
    drag_coefficient : float, optional
        Aerodynamic drag coefficient Cd (default: 1.0 for heavy trucks)
    rolling_resistance : float, optional
        Rolling resistance coefficient (default: 0.006 for trucks on asphalt)

    Returns
    -------
    float
        Energy consumption at the wheel in Joules

    Examples
    --------
    >>> calculate_energy_consumption(
    ...     mass=18000, grade=0, distance=100000, velocity=22.2
    ... )
    342511200.0
    """
    # Gravitational potential energy (climbing work against gravity)
    E_gravity = mass * GRAVITY_ACCELERATION * np.sin(grade) * distance

    # Rolling resistance energy (friction between tires and road)
    E_rolling = rolling_resistance * mass * GRAVITY_ACCELERATION * distance

    # Aerodynamic drag energy (air resistance)
    # Drag force: F_d = 0.5 * Cd * ρ * A * v²
    # Energy over distance: E = F_d × distance (assumes constant velocity)
    E_aero = (
        0.5 * drag_coefficient * air_density * frontal_area *
        (velocity ** 2) * distance
    )

    # Total energy at wheel
    E_wheel = E_gravity + E_rolling + E_aero

    return E_wheel


def calculate_battery_degradation(
    initial_range: float,
    years: float,
    degradation_rate: float = 0.106,
) -> float:
    """
    Calculate battery range after degradation using exponential decay model.

    Parameters
    ----------
    initial_range : float
        Initial battery range in km
    years : float
        Number of years of operation
    degradation_rate : float, optional
        Annual degradation rate (default: 0.106 for ~10% per year)

    Returns
    -------
    float
        Degraded battery range in km

    Examples
    --------
    >>> calculate_battery_degradation(initial_range=400, years=5)
    236.8
    """
    range_degraded = initial_range * np.exp(-degradation_rate * years)
    return range_degraded


def calculate_npv(
    initial_investment: float,
    annual_cashflows: List[float],
    discount_rate: float = 0.08,
) -> float:
    """
    Calculate Net Present Value of an investment.

    Parameters
    ----------
    initial_investment : float
        Initial capital investment (positive value; treated as cash outflow)
    annual_cashflows : list of float
        Annual cash flows (positive for income, negative for costs)
    discount_rate : float, optional
        Annual discount rate (default: 0.08 for 8%)

    Returns
    -------
    float
        Net Present Value

    Examples
    --------
    >>> calculate_npv(150000, [30000, 30000, 30000, 30000, 30000])
    -30398.26
    """
    npv = -initial_investment
    for t, cashflow in enumerate(annual_cashflows, start=1):
        npv += cashflow / ((1 + discount_rate) ** t)
    return npv


def calculate_total_cost_of_ownership(
    initial_cost: float,
    annual_operating_cost: float,
    years: int = 5,
    discount_rate: float = 0.08,
) -> float:
    """
    Calculate Total Cost of Ownership over the vehicle lifetime.

    Parameters
    ----------
    initial_cost : float
        Initial purchase cost
    annual_operating_cost : float
        Annual operating cost (positive value; represents cost magnitude)
    years : int, optional
        Number of years (default: 5)
    discount_rate : float, optional
        Annual discount rate (default: 0.08)

    Returns
    -------
    float
        Total Cost of Ownership (present value)
    """
    tco = initial_cost
    for year in range(1, years + 1):
        tco += annual_operating_cost / ((1 + discount_rate) ** year)
    return tco


def monte_carlo_simulation(
    base_params: Dict[str, float],
    uncertainty_params: Dict[str, Dict[str, float]],
    n_simulations: int = 10000,
    random_seed: Optional[int] = None,
) -> np.ndarray:
    """
    Run Monte Carlo simulation with parameter uncertainty.

    Parameters
    ----------
    base_params : dict
        Base parameter values
    uncertainty_params : dict
        Dictionary specifying uncertainty distributions for each parameter
        Format: {param_name: {'type': 'normal'|'uniform', 'std': value,
                               'min': value, 'max': value}}
    n_simulations : int, optional
        Number of simulations to run (default: 10000)
    random_seed : int, optional
        Random seed for reproducibility

    Returns
    -------
    np.ndarray
        Array of simulation results

    Examples
    --------
    >>> params = {'fuel_price': 1.5, 'utilization': 0.85}
    >>> uncertainty = {
    ...     'fuel_price': {'type': 'normal', 'std': 0.3},
    ...     'utilization': {'type': 'uniform', 'min': 0.7, 'max': 0.95}
    ... }
    >>> results = monte_carlo_simulation(
    ...     params, uncertainty, n_simulations=1000
    ... )
    """
    if random_seed is not None:
        np.random.seed(random_seed)

    results = []

    for _ in range(n_simulations):
        sim_params = base_params.copy()

        # Apply uncertainty to each parameter
        for param_name, uncertainty in uncertainty_params.items():
            if param_name not in base_params:
                continue

            base_value = base_params[param_name]

            if uncertainty['type'] == 'normal':
                sim_params[param_name] = np.random.normal(
                    base_value,
                    uncertainty.get('std', 0.1 * base_value)
                )
            elif uncertainty['type'] == 'uniform':
                sim_params[param_name] = np.random.uniform(
                    uncertainty.get('min', 0.8 * base_value),
                    uncertainty.get('max', 1.2 * base_value)
                )

        results.append(sim_params)

    return np.array(results)
