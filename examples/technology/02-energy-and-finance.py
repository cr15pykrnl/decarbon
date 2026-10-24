def calculate_energy_consumption(tech_specs, route_data):
    """Calculate energy consumption per km based on technology and route"""
    distance = route_data['distance']

    if 'fuel_consumption' in tech_specs:
        return tech_specs['fuel_consumption'], 'L/km'
    elif 'energy_consumption' in tech_specs:
        return tech_specs['energy_consumption'], 'kWh/km'
    elif 'hydrogen_consumption' in tech_specs:
        return tech_specs['hydrogen_consumption'], 'kg H₂/km'
    else:
        return 0, 'N/A'

# Calculate energy consumption for medium range scenario
route_scenario = 'Medium Range'
energy_consumption_data = []

for tech_name in ['Diesel', 'BEV', 'FCET', 'Hybrid']:
    tech_specs = technology_matrix[route_scenario][tech_name]
    route_data = routes[route_scenario]

    consumption, unit = calculate_energy_consumption(tech_specs, route_data)

    energy_consumption_data.append({
        'Technology': tech_name,
        'Energy_Consumption': consumption,
        'Unit': unit
    })

energy_df = pd.DataFrame(energy_consumption_data)

# Create energy consumption comparison chart
fig, ax = plt.subplots(1, 1, figsize=(12, 8))

bars = ax.bar(energy_df['Technology'], energy_df['Energy_Consumption'],
              color=[colors[tech] for tech in energy_df['Technology']], alpha=0.8, edgecolor='black')

# Add value labels on bars
for i, (bar, unit) in enumerate(zip(bars, energy_df['Unit'])):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height + height*0.02,
            f'{height:.2f}\n{unit}', ha='center', va='bottom', fontweight='bold', fontsize=11)

ax.set_title(f'Energy Consumption Comparison - {route_scenario}', fontsize=16, fontweight='bold', pad=20)
ax.set_ylabel('Energy Consumption per km', fontsize=12)
ax.set_xlabel('Technology', fontsize=12)
ax.grid(axis='y', alpha=0.3)

# Add efficiency context
efficiency_text = "\n".join([f"{row['Technology']}: {row['Energy_Consumption']:.2f} {row['Unit']}"
                           for _, row in energy_df.iterrows()])
ax.text(0.02, 0.98, f"Terrain factor: {routes[route_scenario]['terrain_factor']}",
        transform=ax.transAxes, fontsize=10, verticalalignment='top',
        bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.7))

plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

print(f"Energy consumption analysis completed for {route_scenario}")
print("\nCalculated energy consumption:")
for _, row in energy_df.iterrows():
    print(f"  {row['Technology']}: {row['Energy_Consumption']:.3f} {row['Unit']}")

def calculate_annual_costs(tech_specs, route_data):
    """Calculate total annual costs including fuel/energy and maintenance"""
    annual_km = route_data['annual_km']

    # Base operating costs
    operating_cost = tech_specs['operating_cost_annual']

    # Maintenance costs (percentage of initial cost)
    maintenance_cost = tech_specs['initial_cost'] * 0.05 * tech_specs['maintenance_factor']

    # Energy costs
    energy_cost = 0
    if 'fuel_consumption' in tech_specs:
        fuel_price = 1.60  # AUD per liter
        energy_cost = tech_specs['fuel_consumption'] * annual_km * fuel_price
    elif 'energy_consumption' in tech_specs:
        electricity_price = 0.25  # AUD per kWh
        energy_cost = tech_specs['energy_consumption'] * annual_km * electricity_price
    elif 'hydrogen_consumption' in tech_specs:
        hydrogen_price = 12.0  # AUD per kg
        energy_cost = tech_specs['hydrogen_consumption'] * annual_km * hydrogen_price

    total_annual_cost = operating_cost + maintenance_cost + energy_cost

    return {
        'operating': operating_cost,
        'maintenance': maintenance_cost,
        'energy': energy_cost,
        'total': total_annual_cost
    }

def calculate_npv_timeline(tech_specs, route_data, baseline_costs, years=5, discount_rate=0.08):
    """Calculate NPV timeline comparing to diesel baseline"""
    # Initial investment difference from baseline
    initial_cost_diff = tech_specs['initial_cost'] - baseline_costs['initial_cost']

    # Annual cost difference from baseline
    tech_annual_costs = calculate_annual_costs(tech_specs, route_data)
    baseline_annual_costs = calculate_annual_costs(baseline_costs, route_data)
    annual_savings = baseline_annual_costs['total'] - tech_annual_costs['total']

    # Calculate cumulative NPV
    npv_timeline = [-initial_cost_diff]  # Year 0
    cumulative_npv = -initial_cost_diff

    for year in range(1, years + 1):
        discounted_savings = annual_savings / (1 + discount_rate) ** year
        cumulative_npv += discounted_savings
        npv_timeline.append(cumulative_npv)

    return npv_timeline, annual_savings

# Calculate NPV for medium range scenario
route_scenario = 'Medium Range'
baseline_tech = technology_matrix[route_scenario]['Diesel']
years = range(6)  # 0 to 5 years

npv_data = {}
annual_savings_data = {}

for tech_name in ['Diesel', 'BEV', 'FCET', 'Hybrid']:
    tech_specs = technology_matrix[route_scenario][tech_name]
    route_data = routes[route_scenario]

    if tech_name == 'Diesel':
        npv_data[tech_name] = [0] * 6  # Baseline reference
        annual_savings_data[tech_name] = 0
    else:
        npv_timeline, annual_savings = calculate_npv_timeline(tech_specs, route_data, baseline_tech)
        npv_data[tech_name] = npv_timeline
        annual_savings_data[tech_name] = annual_savings

# Create NPV timeline chart
fig, ax = plt.subplots(1, 1, figsize=(14, 8))

for tech_name, npv_values in npv_data.items():
    line_style = '--' if tech_name == 'Diesel' else '-'
    line_width = 2 if tech_name == 'Diesel' else 3
    ax.plot(years, npv_values, marker='o', linewidth=line_width, markersize=8,
            label=tech_name, color=colors[tech_name], linestyle=line_style)

# Add break-even line
ax.axhline(y=0, color='red', linestyle=':', alpha=0.7, linewidth=2, label='Break-even')

# Find and mark break-even points
for tech_name, npv_values in npv_data.items():
    if tech_name != 'Diesel':
        # Find break-even year (where NPV crosses zero)
        for i in range(1, len(npv_values)):
            if npv_values[i-1] < 0 and npv_values[i] >= 0:
                # Linear interpolation for more precise break-even point
                break_even_year = i - 1 + abs(npv_values[i-1]) / (npv_values[i] - npv_values[i-1])
                ax.plot(break_even_year, 0, 's', markersize=10, color=colors[tech_name],
                       markeredgecolor='black', markeredgewidth=2)
                ax.annotate(f'{tech_name}\nBreak-even: {break_even_year:.1f} years',
                           xy=(break_even_year, 0), xytext=(break_even_year, 50000),
                           ha='center', va='bottom', fontsize=10,
                           arrowprops=dict(arrowstyle='->', color=colors[tech_name]),
                           bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
                break

# Formatting
ax.set_title(f'Net Present Value Timeline - {route_scenario} Operations\n(Compared to Diesel Baseline)',
             fontsize=16, fontweight='bold', pad=20)
ax.set_xlabel('Years', fontsize=12)
ax.set_ylabel('Cumulative NPV (AUD)', fontsize=12)
ax.legend(loc='lower right', fontsize=11)
ax.grid(True, alpha=0.3)

# Format y-axis as currency
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1000:.0f}K'))

plt.tight_layout()
plt.show()

print(f"NPV timeline analysis completed for {route_scenario}")
print("\nAnnual savings compared to diesel:")
for tech, savings in annual_savings_data.items():
    if tech != 'Diesel':
        print(f"  {tech}: ${savings:,.0f}/year")

def calculate_payback_period(tech_specs, route_data, baseline_specs):
    """Calculate simple payback period in years"""
    # Initial investment difference
    initial_investment_diff = tech_specs['initial_cost'] - baseline_specs['initial_cost']

    # Annual cost calculations
    tech_annual = calculate_annual_costs(tech_specs, route_data)
    baseline_annual = calculate_annual_costs(baseline_specs, route_data)
    annual_savings = baseline_annual['total'] - tech_annual['total']

    if annual_savings <= 0:
        return float('inf'), tech_annual, baseline_annual  # Never pays back

    payback = initial_investment_diff / annual_savings
    return payback, tech_annual, baseline_annual

# Calculate payback periods for all route scenarios
payback_analysis = {}

for route_name, route_data in routes.items():
    baseline_specs = technology_matrix[route_name]['Diesel']
    payback_analysis[route_name] = []

    for tech_name in ['BEV', 'FCET', 'Hybrid']:
        tech_specs = technology_matrix[route_name][tech_name]
        payback, tech_costs, baseline_costs = calculate_payback_period(tech_specs, route_data, baseline_specs)

        payback_analysis[route_name].append({
            'Technology': tech_name,
            'Route': route_name,
            'Payback_Years': payback,
            'Initial_Cost_Diff': tech_specs['initial_cost'] - baseline_specs['initial_cost'],
            'Annual_Savings': baseline_costs['total'] - tech_costs['total'],
            'Tech_Annual_Cost': tech_costs['total'],
            'Baseline_Annual_Cost': baseline_costs['total']
        })

# Focus on medium range for detailed analysis
medium_payback = payback_analysis['Medium Range']
payback_df = pd.DataFrame(medium_payback)

# Create horizontal bar chart
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

# Payback period chart
bars1 = ax1.barh(payback_df['Technology'], payback_df['Payback_Years'],
                 color=[colors[tech] for tech in payback_df['Technology']], alpha=0.8, edgecolor='black')

# Add value labels
for i, bar in enumerate(bars1):
    width = bar.get_width()
    if width != float('inf'):
        ax1.text(width + 0.1, bar.get_y() + bar.get_height()/2,
                f'{width:.1f} years', ha='left', va='center', fontweight='bold')
    else:
        ax1.text(0.1, bar.get_y() + bar.get_height()/2,
                'No payback', ha='left', va='center', fontweight='bold')

ax1.set_title('Break-even Timeline by Technology', fontsize=14, fontweight='bold')
ax1.set_xlabel('Years to Break-even', fontsize=12)
ax1.set_ylabel('Technology', fontsize=12)
ax1.grid(axis='x', alpha=0.3)

# Annual savings breakdown
bars2 = ax2.bar(payback_df['Technology'], payback_df['Annual_Savings'],
                color=[colors[tech] for tech in payback_df['Technology']], alpha=0.8, edgecolor='black')

# Add value labels
for bar in bars2:
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height + height*0.02,
             f'${height/1000:.0f}K', ha='center', va='bottom', fontweight='bold')

ax2.set_title('Annual Cost Savings vs Diesel', fontsize=14, fontweight='bold')
ax2.set_ylabel('Annual Savings (AUD)', fontsize=12)
ax2.set_xlabel('Technology', fontsize=12)
ax2.grid(axis='y', alpha=0.3)
ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1000:.0f}K'))

plt.suptitle(f'Break-even Analysis - {route_scenario}', fontsize=16, fontweight='bold')
plt.tight_layout()
plt.show()

print(f"Break-even analysis completed for {route_scenario}")
print("\nDetailed payback analysis:")
for _, row in payback_df.iterrows():
    print(f"\n{row['Technology']}:")
    print(f"  Initial cost difference: ${row['Initial_Cost_Diff']:,.0f}")
    print(f"  Annual savings: ${row['Annual_Savings']:,.0f}")
    if row['Payback_Years'] != float('inf'):
        print(f"  Payback period: {row['Payback_Years']:.1f} years")
    else:
        print(f"  Payback period: No payback (higher operating costs)")
