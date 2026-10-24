# Run Monte Carlo simulations for all technologies
n_simulations = 10000
simulation_results = {}

print(f"Running Monte Carlo simulations ({n_simulations:,} iterations per technology)...")

for tech_name, tech_specs in base_technologies.items():
    if tech_name == 'Diesel':
        # Diesel is baseline (NPV = 0)
        simulation_results[tech_name] = {
            'npv_distribution': np.zeros(n_simulations),
            'cash_flows': np.zeros((n_simulations, 6)),  # 6 years (0-5)
            'samples': None
        }
    else:
        print(f"  Simulating {tech_name}...")
        npv_dist, cash_flows, samples = calculate_npv_with_uncertainty(
            tech_specs, base_scenario, uncertainty_params, n_simulations
        )

        simulation_results[tech_name] = {
            'npv_distribution': npv_dist,
            'cash_flows': cash_flows,
            'samples': samples
        }

print("Monte Carlo simulations completed")

# Calculate summary statistics
summary_stats = {}
for tech_name, results in simulation_results.items():
    npv_dist = results['npv_distribution']

    summary_stats[tech_name] = {
        'mean': np.mean(npv_dist),
        'median': np.median(npv_dist),
        'std': np.std(npv_dist),
        'min': np.min(npv_dist),
        'max': np.max(npv_dist),
        'q5': np.percentile(npv_dist, 5),
        'q25': np.percentile(npv_dist, 25),
        'q75': np.percentile(npv_dist, 75),
        'q95': np.percentile(npv_dist, 95),
        'prob_positive': np.mean(npv_dist > 0) * 100,
        'prob_breakeven_3yr': np.mean(npv_dist > -50000) * 100  # Reasonable 3-year target
    }

print("\nNPV Distribution Summary Statistics:")
for tech_name, stats in summary_stats.items():
    if tech_name != 'Diesel':
        print(f"\n{tech_name}:")
        print(f"  Mean NPV: ${stats['mean']:,.0f}")
        print(f"  Median NPV: ${stats['median']:,.0f}")
        print(f"  Standard Deviation: ${stats['std']:,.0f}")
        print(f"  90% Confidence Interval: [${stats['q5']:,.0f}, ${stats['q95']:,.0f}]")
        print(f"  Probability of positive NPV: {stats['prob_positive']:.1f}%")

# Create NPV distribution visualization
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))

# 1. Histogram overlays
for tech_name in ['BEV', 'FCET', 'Hybrid']:
    npv_dist = simulation_results[tech_name]['npv_distribution']
    ax1.hist(npv_dist/1000, bins=50, alpha=0.6, label=tech_name,
             color=colors[tech_name], density=True)

ax1.axvline(x=0, color='red', linestyle='--', alpha=0.7, label='Break-even')
ax1.set_title('NPV Distribution Density', fontsize=14, fontweight='bold')
ax1.set_xlabel('NPV ($K)', fontsize=12)
ax1.set_ylabel('Probability Density', fontsize=12)
ax1.legend()
ax1.grid(True, alpha=0.3)

# 2. Box plots
box_data = []
box_labels = []
for tech_name in ['BEV', 'FCET', 'Hybrid']:
    box_data.append(simulation_results[tech_name]['npv_distribution']/1000)
    box_labels.append(tech_name)

bp = ax2.boxplot(box_data, labels=box_labels, patch_artist=True)
for i, (patch, tech) in enumerate(zip(bp['boxes'], box_labels)):
    patch.set_facecolor(colors[tech])
    patch.set_alpha(0.7)

ax2.axhline(y=0, color='red', linestyle='--', alpha=0.7)
ax2.set_title('NPV Distribution Quartiles', fontsize=14, fontweight='bold')
ax2.set_ylabel('NPV ($K)', fontsize=12)
ax2.grid(True, alpha=0.3)

# 3. Cumulative probability
for tech_name in ['BEV', 'FCET', 'Hybrid']:
    npv_dist = simulation_results[tech_name]['npv_distribution']
    sorted_npv = np.sort(npv_dist)
    cumulative_prob = np.arange(1, len(sorted_npv) + 1) / len(sorted_npv) * 100

    ax3.plot(sorted_npv/1000, cumulative_prob, linewidth=2,
             label=tech_name, color=colors[tech_name])

ax3.axvline(x=0, color='red', linestyle='--', alpha=0.7, label='Break-even')
ax3.axhline(y=50, color='gray', linestyle=':', alpha=0.5, label='50th percentile')
ax3.set_title('Cumulative Probability Distribution', fontsize=14, fontweight='bold')
ax3.set_xlabel('NPV ($K)', fontsize=12)
ax3.set_ylabel('Cumulative Probability (%)', fontsize=12)
ax3.legend()
ax3.grid(True, alpha=0.3)

# 4. Risk metrics comparison
technologies = ['BEV', 'FCET', 'Hybrid']
risk_metrics = ['prob_positive', 'prob_breakeven_3yr']
risk_labels = ['Prob. Positive NPV', 'Prob. Break-even']

x = np.arange(len(technologies))
width = 0.35

prob_positive = [summary_stats[tech]['prob_positive'] for tech in technologies]
prob_breakeven = [summary_stats[tech]['prob_breakeven_3yr'] for tech in technologies]

bars1 = ax4.bar(x - width/2, prob_positive, width, label='Positive NPV',
                color=[colors[tech] for tech in technologies], alpha=0.8)
bars2 = ax4.bar(x + width/2, prob_breakeven, width, label='Near Break-even',
                color=[colors[tech] for tech in technologies], alpha=0.5)

# Add value labels
for i, (bar1, bar2) in enumerate(zip(bars1, bars2)):
    ax4.text(bar1.get_x() + bar1.get_width()/2., bar1.get_height() + 1,
             f'{prob_positive[i]:.0f}%', ha='center', va='bottom', fontweight='bold')
    ax4.text(bar2.get_x() + bar2.get_width()/2., bar2.get_height() + 1,
             f'{prob_breakeven[i]:.0f}%', ha='center', va='bottom', fontweight='bold')

ax4.set_title('Probability of Success', fontsize=14, fontweight='bold')
ax4.set_ylabel('Probability (%)', fontsize=12)
ax4.set_xlabel('Technology', fontsize=12)
ax4.set_xticks(x)
ax4.set_xticklabels(technologies)
ax4.legend()
ax4.grid(axis='y', alpha=0.3)
ax4.set_ylim(0, 110)

plt.suptitle('Monte Carlo NPV Risk Analysis', fontsize=16, fontweight='bold')
plt.tight_layout()
plt.show()

print("NPV distribution analysis completed")

def calculate_sensitivity_correlations(tech_name):
    """Calculate correlations between input parameters and NPV"""
    if tech_name == 'Diesel':
        return {}

    results = simulation_results[tech_name]
    npv_dist = results['npv_distribution']
    samples = results['samples']

    correlations = {}

    for param_name, param_values in samples.items():
        # Calculate Pearson correlation
        correlation = np.corrcoef(param_values, npv_dist)[0, 1]
        correlations[param_name] = correlation

    return correlations

def create_tornado_chart(correlations, tech_name, ax):
    """Create tornado chart showing parameter sensitivities"""
    # Sort by absolute correlation
    sorted_params = sorted(correlations.items(), key=lambda x: abs(x[1]), reverse=True)

    params = [param.replace('_', ' ').title() for param, _ in sorted_params]
    corr_values = [corr for _, corr in sorted_params]

    # Create horizontal bar chart
    y_pos = np.arange(len(params))
    bars = ax.barh(y_pos, corr_values, color=[colors[tech_name]] * len(params), alpha=0.7)

    # Color bars based on positive/negative correlation
    for i, (bar, corr) in enumerate(zip(bars, corr_values)):
        if corr < 0:
            bar.set_color('red')
            bar.set_alpha(0.7)
        else:
            bar.set_color('green')
            bar.set_alpha(0.7)

    # Add value labels
    for i, corr in enumerate(corr_values):
        ax.text(corr + (0.02 if corr > 0 else -0.02), i, f'{corr:.2f}',
                ha='left' if corr > 0 else 'right', va='center', fontweight='bold')

    ax.set_yticks(y_pos)
    ax.set_yticklabels(params)
    ax.set_xlabel('Correlation with NPV')
    ax.set_title(f'{tech_name} - Parameter Sensitivity')
    ax.axvline(x=0, color='black', linestyle='-', alpha=0.3)
    ax.grid(axis='x', alpha=0.3)

    return sorted_params

# Calculate sensitivity for all technologies
sensitivity_results = {}
for tech_name in ['BEV', 'FCET', 'Hybrid']:
    sensitivity_results[tech_name] = calculate_sensitivity_correlations(tech_name)

# Create tornado charts
fig, axes = plt.subplots(1, 3, figsize=(18, 8))

tornado_data = {}
for i, tech_name in enumerate(['BEV', 'FCET', 'Hybrid']):
    tornado_data[tech_name] = create_tornado_chart(
        sensitivity_results[tech_name], tech_name, axes[i]
    )

plt.suptitle('Parameter Sensitivity Analysis - Tornado Charts', fontsize=16, fontweight='bold')
plt.tight_layout()
plt.show()

# Print sensitivity summary
print("Parameter Sensitivity Analysis Results:")
print("(Correlation with NPV: +1 = perfect positive, -1 = perfect negative, 0 = no correlation)")

for tech_name, correlations in sensitivity_results.items():
    print(f"\n{tech_name}:")
    sorted_corr = sorted(correlations.items(), key=lambda x: abs(x[1]), reverse=True)
    for param, corr in sorted_corr[:5]:  # Top 5 most sensitive
        impact = "Strong" if abs(corr) > 0.5 else "Moderate" if abs(corr) > 0.3 else "Weak"
        direction = "Positive" if corr > 0 else "Negative"
        print(f"  {param.replace('_', ' ').title()}: {corr:+.3f} ({impact} {direction})")
