def calculate_performance_metrics(tech_specs, route_data):
    """Calculate normalized performance metrics (0-10 scale) based on computed data"""

    # Range calculation (normalized to diesel range)
    base_range = 800  # km for diesel
    if 'energy_consumption' in tech_specs:  # BEV
        # Assume 100 kWh battery capacity
        battery_capacity = 100
        bev_range = (battery_capacity / tech_specs['energy_consumption']) * 0.8  # 80% usable capacity
        range_score = min(10, (bev_range / base_range) * 10)
    elif 'hydrogen_consumption' in tech_specs:  # FCET
        # Assume 30 kg hydrogen tank
        tank_capacity = 30
        fcet_range = tank_capacity / tech_specs['hydrogen_consumption']
        range_score = min(10, (fcet_range / base_range) * 10)
    else:  # Diesel/Hybrid
        range_score = 10

    # Refuel speed (diesel = 10, others scaled accordingly)
    if tech_specs.get('energy_consumption'):  # BEV
        refuel_speed = 3  # Slow charging
    elif tech_specs.get('hydrogen_consumption'):  # FCET
        refuel_speed = 8  # Fast refueling
    else:  # Diesel/Hybrid
        refuel_speed = 10

    # Daily utilization based on range and route requirements
    daily_km = route_data['daily_km']
    if 'energy_consumption' in tech_specs:
        bev_range = (100 / tech_specs['energy_consumption']) * 0.8
        utilization = min(10, (bev_range / daily_km) * 5)  # Can handle 5x daily requirement = 10
    elif 'hydrogen_consumption' in tech_specs:
        fcet_range = 30 / tech_specs['hydrogen_consumption']
        utilization = min(10, (fcet_range / daily_km) * 3)
    else:
        utilization = 10

    # Energy efficiency (higher efficiency = higher score)
    efficiency = tech_specs.get('efficiency', 0.35) * 10 / 0.85  # Normalized to BEV efficiency
    efficiency = min(10, efficiency)

    # Maintenance (lower maintenance factor = higher score)
    maintenance_score = (2 - tech_specs['maintenance_factor']) * 5
    maintenance_score = max(0, min(10, maintenance_score))

    # Environmental (lower emissions = higher score)
    trip_emissions = calculate_trip_emissions(tech_specs, route_data['distance'])
    diesel_emissions = calculate_trip_emissions(technology_matrix[route_data['name']]['Diesel'], route_data['distance'])
    if diesel_emissions > 0:
        environmental_score = (1 - trip_emissions / diesel_emissions) * 10
    else:
        environmental_score = 10
    environmental_score = max(0, environmental_score)

    return {
        'Range': range_score,
        'Refuel_Speed': refuel_speed,
        'Utilization': utilization,
        'Efficiency': efficiency,
        'Maintenance': maintenance_score,
        'Environmental': environmental_score
    }

# Calculate performance metrics for medium range scenario
route_scenario = 'Medium Range'
route_data = routes[route_scenario].copy()
route_data['name'] = route_scenario

performance_metrics = {}
for tech_name in ['Diesel', 'BEV', 'FCET', 'Hybrid']:
    tech_specs = technology_matrix[route_scenario][tech_name]
    performance_metrics[tech_name] = calculate_performance_metrics(tech_specs, route_data)

# Create radar chart using plotly
categories = list(performance_metrics['Diesel'].keys())
categories_display = ['Range', 'Refuel Speed', 'Daily Utilization', 'Energy Efficiency', 'Low Maintenance', 'Environmental']

fig = go.Figure()

for tech, metrics in performance_metrics.items():
    values = list(metrics.values())
    values += [values[0]]  # Close the polygon
    categories_plot = categories_display + [categories_display[0]]

    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories_plot,
        fill='toself',
        name=tech,
        line_color=colors[tech],
        fillcolor=colors[tech],
        opacity=0.6,
        line_width=3
    ))

fig.update_layout(
    polar=dict(
        radialaxis=dict(
            visible=True,
            range=[0, 10],
            tickvals=[2, 4, 6, 8, 10],
            ticktext=['2', '4', '6', '8', '10']
        )
    ),
    showlegend=True,
    title={
        'text': f'Operational Performance Comparison - {route_scenario}<br><sub>Computed metrics based on technology specifications</sub>',
        'x': 0.5,
        'font': {'size': 16}
    },
    font=dict(size=12),
    width=800,
    height=700
)

fig.show()

print(f"Operational performance analysis completed for {route_scenario}")
print("\nComputed performance scores (0-10 scale):")
for tech, metrics in performance_metrics.items():
    print(f"\n{tech}:")
    for category, score in metrics.items():
        print(f"  {category}: {score:.1f}")

def battery_degradation_model(initial_capacity, years, degradation_rate):
    """Model battery degradation using exponential decay"""
    return initial_capacity * np.exp(-degradation_rate * years)

def calculate_range_degradation(tech_specs, initial_range, years):
    """Calculate range degradation accounting for energy consumption changes"""
    degradation_rate = tech_specs.get('degradation_rate', 0.106)

    # Battery capacity degradation
    capacity_retention = np.exp(-degradation_rate * years)

    # Range calculation with degraded battery
    degraded_range = initial_range * capacity_retention

    return degraded_range, capacity_retention

def monte_carlo_degradation(tech_specs, initial_range, years, n_simulations=1000):
    """Monte Carlo simulation of battery degradation with uncertainty"""
    base_degradation_rate = tech_specs.get('degradation_rate', 0.106)

    # Add uncertainty to degradation rate (±20%)
    degradation_rates = np.random.normal(base_degradation_rate, base_degradation_rate * 0.2, n_simulations)
    degradation_rates = np.clip(degradation_rates, 0.05, 0.2)  # Reasonable bounds

    # Add uncertainty to initial conditions (±5%)
    initial_ranges = np.random.normal(initial_range, initial_range * 0.05, n_simulations)

    ranges = []
    for i in range(n_simulations):
        degraded_range, _ = calculate_range_degradation(
            {'degradation_rate': degradation_rates[i]},
            initial_ranges[i],
            years
        )
        ranges.append(degraded_range)

    return np.array(ranges)

# Calculate BEV range degradation
bev_specs = technology_matrix['Medium Range']['BEV']
initial_battery_capacity = 100  # kWh
energy_consumption = bev_specs['energy_consumption']
initial_range = (initial_battery_capacity / energy_consumption) * 0.8  # 80% usable capacity

print(f"Calculated initial BEV range: {initial_range:.0f} km")
print(f"Based on {initial_battery_capacity} kWh battery and {energy_consumption:.2f} kWh/km consumption")

# Model degradation over 8 years
years_array = np.linspace(0, 8, 50)
mean_ranges = []
capacity_retentions = []

for year in years_array:
    degraded_range, capacity = calculate_range_degradation(bev_specs, initial_range, year)
    mean_ranges.append(degraded_range)
    capacity_retentions.append(capacity * 100)  # Convert to percentage

# Monte Carlo simulation for uncertainty bounds
confidence_intervals = []
for year in [0, 1, 2, 3, 4, 5, 6, 7, 8]:
    if year == 0:
        ranges = [initial_range] * 1000
    else:
        ranges = monte_carlo_degradation(bev_specs, initial_range, year)

    confidence_intervals.append({
        'year': year,
        'mean': np.mean(ranges),
        'lower_95': np.percentile(ranges, 2.5),
        'upper_95': np.percentile(ranges, 97.5),
        'lower_68': np.percentile(ranges, 16),
        'upper_68': np.percentile(ranges, 84)
    })

confidence_df = pd.DataFrame(confidence_intervals)

# Create comprehensive degradation visualization
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))

# 1. Range degradation with confidence bands
ax1.fill_between(confidence_df['year'], confidence_df['lower_95'], confidence_df['upper_95'],
                alpha=0.2, color=colors['BEV'], label='95% Confidence Interval')
ax1.fill_between(confidence_df['year'], confidence_df['lower_68'], confidence_df['upper_68'],
                alpha=0.4, color=colors['BEV'], label='68% Confidence Interval')
ax1.plot(years_array, mean_ranges, linewidth=3, color=colors['BEV'], label='Expected Range')

# Add milestone markers
milestone_years = [1, 3, 5, 8]
for year in milestone_years:
    degraded_range, capacity = calculate_range_degradation(bev_specs, initial_range, year)
    degradation_pct = (1 - capacity) * 100
    ax1.plot(year, degraded_range, 'o', markersize=8, color='red', markeredgecolor='black')
    ax1.annotate(f'Y{year}: {degraded_range:.0f}km\n({degradation_pct:.0f}% loss)',
                xy=(year, degraded_range), xytext=(year + 0.3, degraded_range + 15),
                ha='left', va='bottom', fontsize=9,
                bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7))

# Warranty threshold
warranty_threshold = initial_range * 0.8
ax1.axhline(y=warranty_threshold, color='orange', linestyle='--', alpha=0.7,
           label=f'Warranty Threshold (80% = {warranty_threshold:.0f}km)')

ax1.set_title('BEV Range Degradation Over Time', fontsize=14, fontweight='bold')
ax1.set_xlabel('Years of Operation', fontsize=12)
ax1.set_ylabel('Available Range (km)', fontsize=12)
ax1.legend(loc='upper right', fontsize=10)
ax1.grid(True, alpha=0.3)

# 2. Battery capacity retention
ax2.plot(years_array, capacity_retentions, linewidth=3, color=colors['BEV'])
ax2.axhline(y=80, color='orange', linestyle='--', alpha=0.7, label='Warranty Threshold (80%)')
ax2.axhline(y=70, color='red', linestyle='--', alpha=0.7, label='Critical Threshold (70%)')

# Add markers
for year in milestone_years:
    _, capacity = calculate_range_degradation(bev_specs, initial_range, year)
    capacity_pct = capacity * 100
    ax2.plot(year, capacity_pct, 'o', markersize=8, color='red', markeredgecolor='black')

ax2.set_title('Battery Capacity Retention', fontsize=14, fontweight='bold')
ax2.set_xlabel('Years of Operation', fontsize=12)
ax2.set_ylabel('Battery Capacity (%)', fontsize=12)
ax2.legend(fontsize=10)
ax2.grid(True, alpha=0.3)
ax2.set_ylim(60, 105)

# 3. Impact on daily operations
route_data = routes['Medium Range']
daily_km = route_data['daily_km']

operational_impact = []
for year in range(9):
    degraded_range, _ = calculate_range_degradation(bev_specs, initial_range, year)

    # Can complete daily route?
    can_complete = degraded_range >= daily_km

    # Safety margin
    safety_margin = (degraded_range - daily_km) / daily_km * 100 if can_complete else 0

    operational_impact.append({
        'year': year,
        'range': degraded_range,
        'can_complete': can_complete,
        'safety_margin': max(0, safety_margin)
    })

impact_df = pd.DataFrame(operational_impact)

# Safety margin chart
colors_impact = ['green' if x else 'red' for x in impact_df['can_complete']]
bars = ax3.bar(impact_df['year'], impact_df['safety_margin'],
               color=colors_impact, alpha=0.7, edgecolor='black')

ax3.axhline(y=20, color='orange', linestyle='--', alpha=0.7, label='Recommended 20% margin')
ax3.set_title(f'Daily Route Safety Margin\n(Daily requirement: {daily_km}km)', fontsize=14, fontweight='bold')
ax3.set_xlabel('Years of Operation', fontsize=12)
ax3.set_ylabel('Safety Margin (%)', fontsize=12)
ax3.legend(fontsize=10)
ax3.grid(axis='y', alpha=0.3)

# 4. Economic impact of degradation
economic_impact = []
for year in range(6):
    degraded_range, capacity = calculate_range_degradation(bev_specs, initial_range, year)

    # Reduced productivity due to more frequent charging
    if degraded_range < daily_km * 1.2:  # Less than 20% safety margin
        productivity_loss = max(0, (daily_km * 1.2 - degraded_range) / (daily_km * 1.2) * 100)
    else:
        productivity_loss = 0

    # Potential replacement cost consideration
    if capacity < 0.7:  # Below 70% capacity
        replacement_cost = 50000  # Battery replacement cost
    else:
        replacement_cost = 0

    economic_impact.append({
        'year': year,
        'productivity_loss': productivity_loss,
        'replacement_cost': replacement_cost
    })

economic_df = pd.DataFrame(economic_impact)

ax4_twin = ax4.twinx()
line1 = ax4.plot(economic_df['year'], economic_df['productivity_loss'],
                 'o-', color='red', linewidth=2, label='Productivity Loss')
bars4 = ax4_twin.bar(economic_df['year'], economic_df['replacement_cost'],
                     alpha=0.3, color='orange', label='Replacement Cost')

ax4.set_title('Economic Impact of Battery Degradation', fontsize=14, fontweight='bold')
ax4.set_xlabel('Years of Operation', fontsize=12)
ax4.set_ylabel('Productivity Loss (%)', fontsize=12, color='red')
ax4_twin.set_ylabel('Replacement Cost (AUD)', fontsize=12, color='orange')
ax4.grid(True, alpha=0.3)

# Combine legends
lines1, labels1 = ax4.get_legend_handles_labels()
lines2, labels2 = ax4_twin.get_legend_handles_labels()
ax4.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=10)

plt.suptitle('BEV Battery Degradation Analysis - Computed from Physics Models', fontsize=16, fontweight='bold')
plt.tight_layout()
plt.show()

print("Battery degradation analysis completed")
print(f"\nDegradation summary (degradation rate: {bev_specs['degradation_rate']:.3f}/year):")
print(f"Initial calculated range: {initial_range:.0f} km")

for year in [1, 3, 5, 8]:
    degraded_range, capacity = calculate_range_degradation(bev_specs, initial_range, year)
    degradation_pct = (1 - capacity) * 100
    print(f"Year {year}: {degraded_range:.0f} km ({capacity*100:.1f}% capacity, {degradation_pct:.1f}% degradation)")

print(f"\nDaily route requirement: {daily_km} km")
for year in [1, 3, 5, 8]:
    degraded_range, _ = calculate_range_degradation(bev_specs, initial_range, year)
    margin = (degraded_range - daily_km) / daily_km * 100
    status = "✓ Adequate" if margin > 20 else "⚠ Marginal" if margin > 0 else "✗ Insufficient"
    print(f"Year {year}: {margin:+.0f}% safety margin - {status}")
