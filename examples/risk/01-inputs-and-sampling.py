import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from scipy import stats
from scipy.optimize import minimize
import warnings
warnings.filterwarnings('ignore')

# Set styling
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")
colors = {'Diesel': '#8B4513', 'BEV': '#2E8B57', 'FCET': '#4169E1', 'Hybrid': '#FF8C00'}

# Set random seed for reproducible results
np.random.seed(42)

print("Libraries loaded successfully")
print("Monte Carlo simulation parameters initialized")

# Base parameters from technology comparison analysis
base_technologies = {
    'Diesel': {
        'initial_cost': 150000,
        'operating_cost': 85000,
        'fuel_consumption': 0.35,  # L/km
        'fuel_price': 1.60,  # AUD/L
        'maintenance_factor': 1.0
    },
    'BEV': {
        'initial_cost': 300000,
        'operating_cost': 50000,
        'energy_consumption': 1.2,  # kWh/km
        'electricity_price': 0.25,  # AUD/kWh
        'maintenance_factor': 0.7,
        'degradation_rate': 0.106  # per year
    },
    'FCET': {
        'initial_cost': 450000,
        'operating_cost': 82500,
        'hydrogen_consumption': 0.08,  # kg/km
        'hydrogen_price': 12.0,  # AUD/kg
        'maintenance_factor': 0.8
    },
    'Hybrid': {
        'initial_cost': 600000,
        'operating_cost': 85000,
        'fuel_consumption': 0.25,  # L/km (reduced)
        'fuel_price': 1.60,  # AUD/L
        'maintenance_factor': 1.1
    }
}

# Operating scenario
base_scenario = {
    'annual_km': 100000,  # Medium range scenario
    'utilization_rate': 0.85,  # 85% utilization
    'discount_rate': 0.08,
    'analysis_years': 5
}

def define_uncertainty_parameters():
    """Define probability distributions for uncertain parameters"""
    uncertainty_params = {
        # Energy price variations (±25%)
        'fuel_price_variation': {
            'distribution': 'normal',
            'mean': 1.0,  # Multiplier
            'std': 0.15,  # 15% standard deviation
            'bounds': (0.7, 1.4)
        },
        'electricity_price_variation': {
            'distribution': 'normal',
            'mean': 1.0,
            'std': 0.12,
            'bounds': (0.75, 1.35)
        },
        'hydrogen_price_variation': {
            'distribution': 'normal',
            'mean': 1.0,
            'std': 0.20,  # Higher uncertainty for hydrogen
            'bounds': (0.6, 1.6)
        },

        # Battery degradation (10-20% over 5 years)
        'degradation_rate_variation': {
            'distribution': 'normal',
            'mean': 0.106,  # Base rate
            'std': 0.025,   # Uncertainty
            'bounds': (0.08, 0.15)
        },

        # Utilization rate (70-95%)
        'utilization_variation': {
            'distribution': 'beta',
            'alpha': 8,
            'beta': 2,
            'scale': 0.25,  # Range from 70% to 95%
            'offset': 0.70
        },

        # Initial cost variations (±10%)
        'initial_cost_variation': {
            'distribution': 'normal',
            'mean': 1.0,
            'std': 0.08,
            'bounds': (0.85, 1.15)
        },

        # Operating cost variations (±15%)
        'operating_cost_variation': {
            'distribution': 'normal',
            'mean': 1.0,
            'std': 0.10,
            'bounds': (0.8, 1.2)
        },

        # Discount rate variations (6-10%)
        'discount_rate_variation': {
            'distribution': 'uniform',
            'low': 0.06,
            'high': 0.10
        }
    }

    return uncertainty_params

def sample_parameter(param_config, n_samples):
    """Sample from parameter distribution"""
    if param_config['distribution'] == 'normal':
        samples = np.random.normal(param_config['mean'], param_config['std'], n_samples)
        if 'bounds' in param_config:
            samples = np.clip(samples, param_config['bounds'][0], param_config['bounds'][1])
    elif param_config['distribution'] == 'beta':
        samples = np.random.beta(param_config['alpha'], param_config['beta'], n_samples)
        samples = samples * param_config['scale'] + param_config['offset']
    elif param_config['distribution'] == 'uniform':
        samples = np.random.uniform(param_config['low'], param_config['high'], n_samples)
    else:
        raise ValueError(f"Unknown distribution: {param_config['distribution']}")

    return samples

# Initialize uncertainty parameters
uncertainty_params = define_uncertainty_parameters()

print("Uncertainty parameter distributions defined:")
for param, config in uncertainty_params.items():
    if config['distribution'] == 'normal':
        print(f"  {param}: Normal(μ={config['mean']}, σ={config['std']})")
    elif config['distribution'] == 'beta':
        print(f"  {param}: Beta(α={config['alpha']}, β={config['beta']}) scaled")
    elif config['distribution'] == 'uniform':
        print(f"  {param}: Uniform({config['low']}, {config['high']})")

def calculate_npv_with_uncertainty(tech_specs, scenario_params, uncertain_params, n_simulations=10000):
    """Calculate NPV distribution using Monte Carlo simulation"""

    # Sample uncertain parameters
    samples = {}
    for param_name, param_config in uncertain_params.items():
        samples[param_name] = sample_parameter(param_config, n_simulations)

    npv_results = []
    annual_cash_flows = []

    for i in range(n_simulations):
        # Apply parameter variations
        sim_tech_specs = tech_specs.copy()
        sim_scenario = scenario_params.copy()

        # Initial cost variation
        sim_tech_specs['initial_cost'] *= samples['initial_cost_variation'][i]

        # Operating cost variation
        sim_tech_specs['operating_cost'] *= samples['operating_cost_variation'][i]

        # Energy price variations
        if 'fuel_price' in sim_tech_specs:
            sim_tech_specs['fuel_price'] *= samples['fuel_price_variation'][i]
        if 'electricity_price' in sim_tech_specs:
            sim_tech_specs['electricity_price'] *= samples['electricity_price_variation'][i]
        if 'hydrogen_price' in sim_tech_specs:
            sim_tech_specs['hydrogen_price'] *= samples['hydrogen_price_variation'][i]

        # Utilization and discount rate
        sim_scenario['utilization_rate'] = samples['utilization_variation'][i]
        sim_scenario['discount_rate'] = samples['discount_rate_variation'][i]

        # BEV degradation rate
        if 'degradation_rate' in sim_tech_specs:
            sim_tech_specs['degradation_rate'] = samples['degradation_rate_variation'][i]

        # Calculate NPV for this simulation
        npv, cash_flows = calculate_single_npv(sim_tech_specs, sim_scenario)
        npv_results.append(npv)
        annual_cash_flows.append(cash_flows)

    return np.array(npv_results), np.array(annual_cash_flows), samples

def calculate_single_npv(tech_specs, scenario_params):
    """Calculate NPV for a single parameter set"""
    years = scenario_params['analysis_years']
    discount_rate = scenario_params['discount_rate']
    annual_km = scenario_params['annual_km'] * scenario_params['utilization_rate']

    # Initial investment (negative cash flow)
    initial_cost = -tech_specs['initial_cost']

    # Calculate annual cash flows
    cash_flows = [initial_cost]  # Year 0

    for year in range(1, years + 1):
        # Base operating savings vs diesel
        annual_savings = base_technologies['Diesel']['operating_cost'] - tech_specs['operating_cost']

        # Energy cost calculations
        if 'fuel_consumption' in tech_specs:
            tech_energy_cost = tech_specs['fuel_consumption'] * annual_km * tech_specs['fuel_price']
            diesel_energy_cost = base_technologies['Diesel']['fuel_consumption'] * annual_km * base_technologies['Diesel']['fuel_price']
        elif 'energy_consumption' in tech_specs:
            tech_energy_cost = tech_specs['energy_consumption'] * annual_km * tech_specs['electricity_price']
            diesel_energy_cost = base_technologies['Diesel']['fuel_consumption'] * annual_km * base_technologies['Diesel']['fuel_price']
            # Apply degradation for BEV
            if 'degradation_rate' in tech_specs:
                degradation_factor = np.exp(-tech_specs['degradation_rate'] * year)
                # Increased energy cost due to reduced efficiency
                tech_energy_cost *= (1 + (1 - degradation_factor) * 0.1)  # 10% efficiency loss impact
        elif 'hydrogen_consumption' in tech_specs:
            tech_energy_cost = tech_specs['hydrogen_consumption'] * annual_km * tech_specs['hydrogen_price']
            diesel_energy_cost = base_technologies['Diesel']['fuel_consumption'] * annual_km * base_technologies['Diesel']['fuel_price']
        else:
            tech_energy_cost = 0
            diesel_energy_cost = 0

        energy_savings = diesel_energy_cost - tech_energy_cost

        # Maintenance cost differences
        diesel_maintenance = base_technologies['Diesel']['initial_cost'] * 0.05 * base_technologies['Diesel']['maintenance_factor']
        tech_maintenance = tech_specs['initial_cost'] * 0.05 * tech_specs['maintenance_factor']
        maintenance_savings = diesel_maintenance - tech_maintenance

        # Total annual cash flow
        annual_cash_flow = annual_savings + energy_savings + maintenance_savings

        # Discount to present value
        discounted_cash_flow = annual_cash_flow / (1 + discount_rate) ** year
        cash_flows.append(discounted_cash_flow)

    # Calculate NPV
    npv = sum(cash_flows)

    return npv, cash_flows

print("Monte Carlo simulation engine initialized")
print("Ready to run probabilistic NPV analysis")
