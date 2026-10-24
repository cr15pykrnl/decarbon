def calculate_trip_emissions(tech_specs, route_distance):
    """Calculate CO2 emissions per trip based on energy consumption and emission factors"""
    if 'fuel_consumption' in tech_specs:
        fuel_per_trip = tech_specs['fuel_consumption'] * route_distance
        co2_per_trip = fuel_per_trip * tech_specs['emission_factor']
    elif 'energy_consumption' in tech_specs:
        energy_per_trip = tech_specs['energy_consumption'] * route_distance
        co2_per_trip = energy_per_trip * tech_specs['emission_factor']
    elif 'hydrogen_consumption' in tech_specs:
        hydrogen_per_trip = tech_specs['hydrogen_consumption'] * route_distance
        co2_per_trip = hydrogen_per_trip * tech_specs['emission_factor']
    else:
        co2_per_trip = 0

    return co2_per_trip

def calculate_annual_emissions(tech_specs, route_data):
    """Calculate annual CO2 emissions"""
    trip_emissions = calculate_trip_emissions(tech_specs, route_data['distance'])
    annual_trips = route_data['trips_per_day'] * working_days_per_year
    return trip_emissions * annual_trips

# Calculate emissions for all scenarios
emissions_data = []

for route_name, route_data in routes.items():
    diesel_emissions = calculate_trip_emissions(technology_matrix[route_name]['Diesel'], route_data['distance'])

    for tech_name in ['Diesel', 'BEV', 'FCET', 'Hybrid']:
        tech_specs = technology_matrix[route_name][tech_name]

        trip_emissions = calculate_trip_emissions(tech_specs, route_data['distance'])
        annual_emissions = calculate_annual_emissions(tech_specs, route_data)

        # Calculate reduction percentage
        if tech_name == 'Diesel':
            reduction_pct = 0
        else:
            reduction_pct = (diesel_emissions - trip_emissions) / diesel_emissions * 100

        emissions_data.append({
            'Route': route_name,
            'Technology': tech_name,
            'CO2_per_trip': trip_emissions,
            'Annual_CO2': annual_emissions,
            'Reduction_pct': reduction_pct
        })

emissions_df = pd.DataFrame(emissions_data)

# Create comprehensive emissions visualization
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))

# 1. Emissions per trip - Medium Range
medium_emissions = emissions_df[emissions_df['Route'] == 'Medium Range']
bars1 = ax1.bar(medium_emissions['Technology'], medium_emissions['CO2_per_trip'],
                color=[colors[tech] for tech in medium_emissions['Technology']],
                alpha=0.8, edgecolor='black')

for bar in bars1:
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height + height*0.02,
             f'{height:.0f} kg', ha='center', va='bottom', fontweight='bold')

ax1.set_title('CO₂ Emissions per Trip - Medium Range', fontsize=12, fontweight='bold')
ax1.set_ylabel('CO₂ Emissions (kg)', fontsize=10)
ax1.grid(axis='y', alpha=0.3)

# 2. Reduction percentages
reduction_data = medium_emissions[medium_emissions['Technology'] != 'Diesel']
bars2 = ax2.bar(reduction_data['Technology'], reduction_data['Reduction_pct'],
                color=[colors[tech] for tech in reduction_data['Technology']],
                alpha=0.8, edgecolor='black')

for bar in bars2:
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height + 1,
             f'{height:.0f}%', ha='center', va='bottom', fontweight='bold')

ax2.set_title('CO₂ Reduction vs Diesel', fontsize=12, fontweight='bold')
ax2.set_ylabel('Emission Reduction (%)', fontsize=10)
ax2.grid(axis='y', alpha=0.3)

# 3. Annual emissions by route
route_comparison = emissions_df.pivot(index='Technology', columns='Route', values='Annual_CO2')
route_comparison.plot(kind='bar', ax=ax3, color=['lightcoral', 'lightblue', 'lightgreen'], alpha=0.8)
ax3.set_title('Annual CO₂ Emissions by Route Scenario', fontsize=12, fontweight='bold')
ax3.set_ylabel('Annual CO₂ (tonnes)', fontsize=10)
ax3.set_xlabel('Technology', fontsize=10)
ax3.legend(title='Route Scenario', bbox_to_anchor=(1.05, 1), loc='upper left')
ax3.grid(axis='y', alpha=0.3)
ax3.tick_params(axis='x', rotation=45)

# Convert to tonnes for readability
ax3.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x/1000:.0f}'))

# 4. Cumulative emissions over 5 years
technologies_list = ['Diesel', 'BEV', 'FCET', 'Hybrid']
years_range = range(1, 6)
medium_route_data = routes['Medium Range']

for tech in technologies_list:
    tech_specs = technology_matrix['Medium Range'][tech]
    annual_emissions = calculate_annual_emissions(tech_specs, medium_route_data)
    cumulative_emissions = [annual_emissions * year for year in years_range]

    ax4.plot(years_range, [x/1000 for x in cumulative_emissions],
             marker='o', linewidth=2, label=tech, color=colors[tech])

ax4.set_title('Cumulative CO₂ Emissions - 5 Years', fontsize=12, fontweight='bold')
ax4.set_xlabel('Years', fontsize=10)
ax4.set_ylabel('Cumulative CO₂ (tonnes)', fontsize=10)
ax4.legend(fontsize=9)
ax4.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

print("Environmental impact analysis completed")
print("\nEmission reductions for Medium Range operations:")
for _, row in reduction_data.iterrows():
    annual_reduction = (medium_emissions[medium_emissions['Technology'] == 'Diesel']['Annual_CO2'].iloc[0] -
                       row['Annual_CO2']) / 1000  # Convert to tonnes
    print(f"  {row['Technology']}: {row['Reduction_pct']:.0f}% reduction ({annual_reduction:.1f} tonnes CO₂/year saved)")

def calculate_detailed_tco(tech_specs, route_data, years=5):
    """Calculate detailed 5-year total cost of ownership breakdown"""
    # Initial investment
    initial_cost = tech_specs['initial_cost']

    # Annual cost components
    annual_costs = calculate_annual_costs(tech_specs, route_data)

    # 5-year totals
    total_operating = annual_costs['operating'] * years
    total_maintenance = annual_costs['maintenance'] * years
    total_energy = annual_costs['energy'] * years

    # Depreciation (straight line over 10 years)
    annual_depreciation = initial_cost * 0.1
    total_depreciation = annual_depreciation * years

    # Residual value after 5 years
    residual_value = initial_cost * 0.5  # 50% residual value

    total_tco = initial_cost + total_operating + total_maintenance + total_energy - residual_value

    return {
        'Initial_Investment': initial_cost,
        'Operating_Costs': total_operating,
        'Maintenance_Costs': total_maintenance,
        'Energy_Costs': total_energy,
        'Residual_Value': -residual_value,  # Negative because it reduces TCO
        'Net_TCO': total_tco,
        'Annual_Costs': annual_costs
    }

# Calculate TCO for medium range scenario
route_scenario = 'Medium Range'
tco_data = []

for tech_name in ['Diesel', 'BEV', 'FCET', 'Hybrid']:
    tech_specs = technology_matrix[route_scenario][tech_name]
    route_data = routes[route_scenario]

    tco = calculate_detailed_tco(tech_specs, route_data)
    tco['Technology'] = tech_name
    tco_data.append(tco)

tco_df = pd.DataFrame(tco_data)

# Create comprehensive TCO visualization
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(18, 12))

# 1. Stacked TCO breakdown
technologies_list = tco_df['Technology']
initial = tco_df['Initial_Investment']
operating = tco_df['Operating_Costs']
maintenance = tco_df['Maintenance_Costs']
energy = tco_df['Energy_Costs']
residual = tco_df['Residual_Value']

# Positive costs
ax1.bar(technologies_list, initial, label='Initial Investment', alpha=0.8, color='red')
ax1.bar(technologies_list, operating, bottom=initial, label='Operating Costs', alpha=0.8, color='blue')
ax1.bar(technologies_list, maintenance, bottom=initial+operating, label='Maintenance', alpha=0.8, color='green')
ax1.bar(technologies_list, energy, bottom=initial+operating+maintenance, label='Energy Costs', alpha=0.8, color='orange')

# Residual value (negative)
total_positive = initial + operating + maintenance + energy
ax1.bar(technologies_list, residual, bottom=total_positive, label='Residual Value', alpha=0.8, color='purple')

# Add net TCO labels
for i, tech in enumerate(technologies_list):
    net_tco = tco_df.iloc[i]['Net_TCO']
    ax1.text(i, net_tco + net_tco*0.05, f'Net: ${net_tco/1000:.0f}K',
            ha='center', va='bottom', fontweight='bold', fontsize=11,
            bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7))

ax1.set_title('5-Year Total Cost of Ownership Breakdown', fontsize=14, fontweight='bold')
ax1.set_ylabel('Cost (AUD)', fontsize=12)
ax1.legend(loc='upper left', fontsize=10)
ax1.grid(axis='y', alpha=0.3)
ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1000:.0f}K'))
ax1.tick_params(axis='x', rotation=45)

# 2. Annual cost breakdown
annual_cost_data = []
for _, row in tco_df.iterrows():
    annual_costs = row['Annual_Costs']
    annual_cost_data.append({
        'Technology': row['Technology'],
        'Operating': annual_costs['operating'],
        'Maintenance': annual_costs['maintenance'],
        'Energy': annual_costs['energy']
    })

annual_df = pd.DataFrame(annual_cost_data)
annual_df.set_index('Technology')[['Operating', 'Maintenance', 'Energy']].plot(
    kind='bar', stacked=True, ax=ax2, alpha=0.8)

ax2.set_title('Annual Operating Cost Breakdown', fontsize=14, fontweight='bold')
ax2.set_ylabel('Annual Cost (AUD)', fontsize=12)
ax2.legend(title='Cost Component')
ax2.grid(axis='y', alpha=0.3)
ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1000:.0f}K'))
ax2.tick_params(axis='x', rotation=45)

# 3. TCO comparison vs Diesel
diesel_tco = tco_df[tco_df['Technology'] == 'Diesel']['Net_TCO'].iloc[0]
tco_diff = tco_df['Net_TCO'] - diesel_tco
tco_diff_pct = (tco_diff / diesel_tco) * 100

bars3 = ax3.bar(tco_df['Technology'], tco_diff_pct,
                color=[colors[tech] for tech in tco_df['Technology']], alpha=0.8, edgecolor='black')

# Add value labels
for i, bar in enumerate(bars3):
    height = bar.get_height()
    label_text = f'{height:+.0f}%\n${tco_diff.iloc[i]/1000:+.0f}K'
    ax3.text(bar.get_x() + bar.get_width()/2., height + (2 if height > 0 else -5),
             label_text, ha='center', va='bottom' if height > 0 else 'top',
             fontweight='bold', fontsize=10)

ax3.axhline(y=0, color='red', linestyle='--', alpha=0.7)
ax3.set_title('TCO Difference vs Diesel Baseline', fontsize=14, fontweight='bold')
ax3.set_ylabel('TCO Difference (%)', fontsize=12)
ax3.grid(axis='y', alpha=0.3)
ax3.tick_params(axis='x', rotation=45)

# 4. Cost per km analysis
annual_km = routes[route_scenario]['annual_km']
cost_per_km = tco_df['Net_TCO'] / (annual_km * 5)  # 5 years

bars4 = ax4.bar(tco_df['Technology'], cost_per_km,
                color=[colors[tech] for tech in tco_df['Technology']], alpha=0.8, edgecolor='black')

# Add value labels
for bar in bars4:
    height = bar.get_height()
    ax4.text(bar.get_x() + bar.get_width()/2., height + height*0.02,
             f'${height:.2f}', ha='center', va='bottom', fontweight='bold')

ax4.set_title('Total Cost per Kilometer (5-year average)', fontsize=14, fontweight='bold')
ax4.set_ylabel('Cost per km (AUD)', fontsize=12)
ax4.grid(axis='y', alpha=0.3)
ax4.tick_params(axis='x', rotation=45)

plt.suptitle(f'Total Cost of Ownership Analysis - {route_scenario}', fontsize=16, fontweight='bold')
plt.tight_layout()
plt.show()

print(f"Total Cost of Ownership analysis completed for {route_scenario}")
print("\n5-Year Net TCO Summary:")
for _, row in tco_df.iterrows():
    print(f"  {row['Technology']}: ${row['Net_TCO']:,.0f}")

print("\nCost per kilometer (5-year average):")
for i, tech in enumerate(tco_df['Technology']):
    print(f"  {tech}: ${cost_per_km.iloc[i]:.2f}/km")
