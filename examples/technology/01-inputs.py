import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

# Set consistent styling
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")
colors = {'Diesel': '#8B4513', 'BEV': '#2E8B57', 'FCET': '#4169E1', 'Hybrid': '#FF8C00'}

# Set random seed for reproducible synthetic data
np.random.seed(42)

print("Libraries loaded successfully")

# Base technology specifications with realistic parameters
base_technologies = {
    'Diesel': {
        'initial_cost_base': 150000,
        'operating_cost_base': 85000,
        'fuel_consumption_base': 0.35,  # L/km
        'emission_factor': 2.68,  # kg CO2/L
        'maintenance_factor': 1.0,
        'efficiency': 0.35  # 35% thermal efficiency
    },
    'BEV': {
        'cost_multiplier': 2.0,  # 2x diesel cost
        'operating_cost_base': 50000,
        'energy_consumption_base': 1.2,  # kWh/km
        'emission_factor': 0.35,  # kg CO2/kWh (grid mix)
        'maintenance_factor': 0.7,
        'degradation_rate': 0.106,  # per year
        'efficiency': 0.85  # 85% motor efficiency
    },
    'FCET': {
        'cost_multiplier': 3.0,  # 3x diesel cost
        'operating_cost_base': 82500,
        'hydrogen_consumption_base': 0.08,  # kg H2/km
        'emission_factor': 0.0,  # kg CO2/kg H2 (green hydrogen)
        'maintenance_factor': 0.8,
        'efficiency': 0.60  # 60% fuel cell efficiency
    },
    'Hybrid': {
        'cost_multiplier': 4.0,  # 4x diesel cost
        'operating_cost_base': 85000,
        'fuel_consumption_reduction': 0.3,  # 30% reduction vs diesel
        'emission_reduction': 0.25,  # 25% emission reduction
        'maintenance_factor': 1.1,
        'efficiency': 0.45  # 45% combined efficiency
    }
}

# Route scenarios with operational parameters
routes = {
    'Short Range': {
        'distance': 120,
        'trips_per_day': 1,
        'terrain_factor': 1.0,  # Flat urban
        'utilization_hours': 8
    },
    'Medium Range': {
        'distance': 200,
        'trips_per_day': 2,
        'terrain_factor': 1.1,  # Mixed terrain
        'utilization_hours': 12
    },
    'Long Range': {
        'distance': 300,
        'trips_per_day': 1,
        'terrain_factor': 1.2,  # Hilly highways
        'utilization_hours': 10
    }
}

# Calculate operational parameters
working_days_per_year = 250
for route_name, route_data in routes.items():
    route_data['annual_km'] = route_data['distance'] * route_data['trips_per_day'] * working_days_per_year
    route_data['daily_km'] = route_data['distance'] * route_data['trips_per_day']

print("Base technology and route parameters initialized")
print("\nAnnual distance by route:")
for route, data in routes.items():
    print(f"  {route}: {data['annual_km']:,} km/year ({data['daily_km']} km/day)")

# Generate technology specifications with route-dependent adjustments
def generate_technology_specs(base_tech, route_data):
    """Generate technology specifications adjusted for route characteristics"""
    specs = {}

    if 'cost_multiplier' in base_tech:
        specs['initial_cost'] = base_technologies['Diesel']['initial_cost_base'] * base_tech['cost_multiplier']
    else:
        specs['initial_cost'] = base_tech['initial_cost_base']

    # Adjust operating costs based on utilization
    utilization_factor = route_data['utilization_hours'] / 8  # 8 hours baseline
    specs['operating_cost_annual'] = base_tech['operating_cost_base'] * utilization_factor

    # Apply terrain factor to energy consumption
    terrain_factor = route_data['terrain_factor']

    if 'fuel_consumption_base' in base_tech:
        specs['fuel_consumption'] = base_tech['fuel_consumption_base'] * terrain_factor
    elif 'energy_consumption_base' in base_tech:
        specs['energy_consumption'] = base_tech['energy_consumption_base'] * terrain_factor
    elif 'hydrogen_consumption_base' in base_tech:
        specs['hydrogen_consumption'] = base_tech['hydrogen_consumption_base'] * terrain_factor
    elif 'fuel_consumption_reduction' in base_tech:
        diesel_consumption = base_technologies['Diesel']['fuel_consumption_base'] * terrain_factor
        specs['fuel_consumption'] = diesel_consumption * (1 - base_tech['fuel_consumption_reduction'])

    # Copy other parameters
    for key in ['emission_factor', 'maintenance_factor', 'degradation_rate', 'efficiency']:
        if key in base_tech:
            specs[key] = base_tech[key]

    # Special handling for hybrid emissions
    if 'emission_reduction' in base_tech:
        specs['emission_factor'] = base_technologies['Diesel']['emission_factor'] * (1 - base_tech['emission_reduction'])

    return specs

# Generate complete technology matrix
technology_matrix = {}
for route_name, route_data in routes.items():
    technology_matrix[route_name] = {}
    for tech_name, base_tech in base_technologies.items():
        technology_matrix[route_name][tech_name] = generate_technology_specs(base_tech, route_data)

print("Technology specifications generated for all route scenarios")
print("\nExample - Medium Range Diesel specs:")
for key, value in technology_matrix['Medium Range']['Diesel'].items():
    print(f"  {key}: {value}")
