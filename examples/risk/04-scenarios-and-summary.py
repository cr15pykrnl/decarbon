def define_market_scenarios():
    """Define different market scenarios for stress testing"""
    scenarios = {
        'Base Case': {
            'fuel_price_mult': 1.0,
            'electricity_price_mult': 1.0,
            'hydrogen_price_mult': 1.0,
            'utilization_mult': 1.0,
            'degradation_mult': 1.0,
            'description': 'Current market conditions'
        },
        'High Energy Prices': {
            'fuel_price_mult': 1.5,
            'electricity_price_mult': 1.3,
            'hydrogen_price_mult': 1.4,
            'utilization_mult': 1.0,
            'degradation_mult': 1.0,
            'description': 'Energy crisis scenario'
        },
        'Technology Breakthrough': {
            'fuel_price_mult': 1.0,
            'electricity_price_mult': 0.7,
            'hydrogen_price_mult': 0.6,
            'utilization_mult': 1.0,
            'degradation_mult': 0.5,  # Better battery technology
            'description': 'Rapid technology advancement'
        },
        'Economic Downturn': {
            'fuel_price_mult': 0.8,
            'electricity_price_mult': 0.9,
            'hydrogen_price_mult': 0.9,
            'utilization_mult': 0.7,  # Reduced demand
            'degradation_mult': 1.2,  # Delayed maintenance
            'description': 'Recession with reduced utilization'
        },
        'Rapid Adoption': {
            'fuel_price_mult': 1.2,
            'electricity_price_mult': 0.8,
            'hydrogen_price_mult': 0.7,
            'utilization_mult': 1.1,
            'degradation_mult': 0.8,
            'description': 'Scale effects from widespread adoption'
        }
    }

    return scenarios

def calculate_scenario_npv(tech_specs, scenario_params, market_scenario):
    """Calculate NPV under specific market scenario"""
    # Apply scenario multipliers
    modified_tech_specs = tech_specs.copy()
    modified_scenario = scenario_params.copy()

    if 'fuel_price' in modified_tech_specs:
        modified_tech_specs['fuel_price'] *= market_scenario['fuel_price_mult']
    if 'electricity_price' in modified_tech_specs:
        modified_tech_specs['electricity_price'] *= market_scenario['electricity_price_mult']
    if 'hydrogen_price' in modified_tech_specs:
        modified_tech_specs['hydrogen_price'] *= market_scenario['hydrogen_price_mult']
    if 'degradation_rate' in modified_tech_specs:
        modified_tech_specs['degradation_rate'] *= market_scenario['degradation_mult']

    modified_scenario['utilization_rate'] *= market_scenario['utilization_mult']

    # Calculate NPV
    npv, _ = calculate_single_npv(modified_tech_specs, modified_scenario)
    return npv

# Define scenarios and calculate NPVs
market_scenarios = define_market_scenarios()
scenario_results = {}

for scenario_name, scenario_params in market_scenarios.items():
    scenario_results[scenario_name] = {}

    for tech_name, tech_specs in base_technologies.items():
        if tech_name == 'Diesel':
            scenario_results[scenario_name][tech_name] = 0  # Baseline
        else:
            npv = calculate_scenario_npv(tech_specs, base_scenario, scenario_params)
            scenario_results[scenario_name][tech_name] = npv

# Create scenario analysis visualization
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))

# 1. NPV by scenario (heatmap)
scenario_matrix = []
scenario_names = list(market_scenarios.keys())
tech_names = ['BEV', 'FCET', 'Hybrid']

for tech in tech_names:
    tech_npvs = [scenario_results[scenario][tech]/1000 for scenario in scenario_names]
    scenario_matrix.append(tech_npvs)

im1 = ax1.imshow(scenario_matrix, cmap='RdYlGn', aspect='auto')
ax1.set_xticks(range(len(scenario_names)))
ax1.set_yticks(range(len(tech_names)))
ax1.set_xticklabels(scenario_names, rotation=45, ha='right')
ax1.set_yticklabels(tech_names)

# Add text annotations
for i in range(len(tech_names)):
    for j in range(len(scenario_names)):
        text = ax1.text(j, i, f'{scenario_matrix[i][j]:.0f}',
                       ha="center", va="center", color="black", fontweight='bold')

ax1.set_title('NPV by Technology & Scenario ($K)')
plt.colorbar(im1, ax=ax1)

# 2. Scenario impact on optimal portfolio
portfolio_scenario_results = []
for scenario_name in scenario_names:
    scenario_npvs = [scenario_results[scenario_name][tech] for tech in tech_names]
    portfolio_npv = np.dot(optimal_weights, scenario_npvs)
    portfolio_scenario_results.append(portfolio_npv/1000)

bars2 = ax2.bar(range(len(scenario_names)), portfolio_scenario_results,
                color=['green' if x > 0 else 'red' for x in portfolio_scenario_results],
                alpha=0.7, edgecolor='black')

# Add value labels
for i, (bar, value) in enumerate(zip(bars2, portfolio_scenario_results)):
    ax2.text(bar.get_x() + bar.get_width()/2., value + (10 if value > 0 else -10),
             f'${value:.0f}K', ha='center', va='bottom' if value > 0 else 'top', fontweight='bold')

ax2.set_xticks(range(len(scenario_names)))
ax2.set_xticklabels(scenario_names, rotation=45, ha='right')
ax2.set_ylabel('Portfolio NPV ($K)')
ax2.set_title('Optimal Portfolio Performance by Scenario')
ax2.axhline(y=0, color='black', linestyle='--', alpha=0.5)
ax2.grid(axis='y', alpha=0.3)

# 3. Technology ranking by scenario
tech_rankings = []
for scenario_name in scenario_names:
    scenario_npvs = [(tech, scenario_results[scenario_name][tech]) for tech in tech_names]
    ranked_techs = sorted(scenario_npvs, key=lambda x: x[1], reverse=True)
    tech_rankings.append([tech for tech, _ in ranked_techs])

# Create ranking visualization
for i, scenario in enumerate(scenario_names):
    for j, tech in enumerate(tech_rankings[i]):
        ax3.text(i, 2-j, tech, ha='center', va='center',
                bbox=dict(boxstyle='round,pad=0.3', facecolor=colors[tech], alpha=0.7),
                fontweight='bold')

ax3.set_xlim(-0.5, len(scenario_names)-0.5)
ax3.set_ylim(-0.5, 2.5)
ax3.set_xticks(range(len(scenario_names)))
ax3.set_xticklabels(scenario_names, rotation=45, ha='right')
ax3.set_yticks([0, 1, 2])
ax3.set_yticklabels(['3rd Best', '2nd Best', 'Best'])
ax3.set_title('Technology Ranking by Scenario')
ax3.grid(True, alpha=0.3)

# 4. Stress test summary
stress_metrics = []
for tech in tech_names:
    tech_npvs = [scenario_results[scenario][tech] for scenario in scenario_names]
    stress_metrics.append({
        'Technology': tech,
        'Best_Case': max(tech_npvs)/1000,
        'Worst_Case': min(tech_npvs)/1000,
        'Range': (max(tech_npvs) - min(tech_npvs))/1000,
        'Scenarios_Positive': sum(1 for npv in tech_npvs if npv > 0)
    })

stress_df = pd.DataFrame(stress_metrics)

x = np.arange(len(tech_names))
width = 0.35

bars4a = ax4.bar(x - width/2, stress_df['Best_Case'], width,
                 label='Best Case', color='green', alpha=0.7)
bars4b = ax4.bar(x + width/2, stress_df['Worst_Case'], width,
                 label='Worst Case', color='red', alpha=0.7)

# Add value labels
for i, (best, worst) in enumerate(zip(stress_df['Best_Case'], stress_df['Worst_Case'])):
    ax4.text(i - width/2, best + 10, f'${best:.0f}K', ha='center', va='bottom', fontweight='bold')
    ax4.text(i + width/2, worst - 10, f'${worst:.0f}K', ha='center', va='top', fontweight='bold')

ax4.set_xlabel('Technology')
ax4.set_ylabel('NPV ($K)')
ax4.set_title('Stress Test Results')
ax4.set_xticks(x)
ax4.set_xticklabels(tech_names)
ax4.legend()
ax4.axhline(y=0, color='black', linestyle='--', alpha=0.5)
ax4.grid(axis='y', alpha=0.3)

plt.suptitle('Scenario Analysis & Stress Testing', fontsize=16, fontweight='bold')
plt.tight_layout()
plt.show()

# Print scenario analysis summary
print("Scenario Analysis Summary:")
print("=" * 50)

for scenario_name, scenario_data in market_scenarios.items():
    print(f"\n{scenario_name}: {scenario_data['description']}")
    portfolio_npv = np.dot(optimal_weights, [scenario_results[scenario_name][tech] for tech in tech_names])
    print(f"  Optimal Portfolio NPV: ${portfolio_npv:,.0f}")

    # Best performing technology in this scenario
    best_tech = max(tech_names, key=lambda t: scenario_results[scenario_name][t])
    best_npv = scenario_results[scenario_name][best_tech]
    print(f"  Best Technology: {best_tech} (${best_npv:,.0f})")

print("\nStress Test Summary:")
for _, row in stress_df.iterrows():
    print(f"\n{row['Technology']}:")
    print(f"  Best case NPV: ${row['Best_Case']:,.0f}K")
    print(f"  Worst case NPV: ${row['Worst_Case']:,.0f}K")
    print(f"  NPV range: ${row['Range']:,.0f}K")
    print(f"  Scenarios with positive NPV: {row['Scenarios_Positive']}/{len(scenario_names)}")

print(f"\nOptimal Portfolio Scenario Performance:")
print(f"  Best scenario: ${max(portfolio_scenario_results):,.0f}K")
print(f"  Worst scenario: ${min(portfolio_scenario_results):,.0f}K")
print(f"  Scenarios with positive NPV: {sum(1 for x in portfolio_scenario_results if x > 0)}/{len(scenario_names)}")

# Generate executive summary metrics
def generate_executive_summary():
    """Generate comprehensive executive summary from all analyses"""

    summary = {
        'simulation_parameters': {
            'n_simulations': n_simulations,
            'analysis_years': base_scenario['analysis_years'],
            'base_annual_km': base_scenario['annual_km']
        },
        'technology_rankings': {},
        'portfolio_optimization': {},
        'risk_assessment': {},
        'scenario_resilience': {},
        'key_insights': []
    }

    # Technology rankings
    for tech in ['BEV', 'FCET', 'Hybrid']:
        stats = summary_stats[tech]
        summary['technology_rankings'][tech] = {
            'expected_npv': stats['mean'],
            'probability_positive': stats['prob_positive'],
            'risk_std': stats['std'],
            'value_at_risk_95': stats['q5']
        }

    # Portfolio optimization results
    summary['portfolio_optimization'] = {
        'optimal_weights': dict(zip(technologies, optimal_weights)),
        'expected_return': optimal_return,
        'portfolio_risk': optimal_risk,
        'sharpe_ratio': optimal_sharpe
    }

    # Risk assessment
    portfolio_prob_positive = np.mean(optimal_returns > 0) * 100
    portfolio_var_95 = np.percentile(optimal_returns, 5)

    summary['risk_assessment'] = {
        'portfolio_prob_positive': portfolio_prob_positive,
        'portfolio_var_95': portfolio_var_95,
        'best_individual_tech': max(technologies, key=lambda t: summary_stats[t]['prob_positive']),
        'lowest_risk_tech': min(technologies, key=lambda t: summary_stats[t]['std'])
    }

    # Scenario resilience
    portfolio_scenarios = [np.dot(optimal_weights, [scenario_results[s][t] for t in technologies])
                          for s in market_scenarios.keys()]

    summary['scenario_resilience'] = {
        'scenarios_positive': sum(1 for x in portfolio_scenarios if x > 0),
        'total_scenarios': len(portfolio_scenarios),
        'best_scenario_npv': max(portfolio_scenarios),
        'worst_scenario_npv': min(portfolio_scenarios)
    }

    return summary

# Generate summary
executive_summary = generate_executive_summary()

# Create executive dashboard
fig = plt.figure(figsize=(20, 12))
gs = fig.add_gridspec(3, 4, hspace=0.3, wspace=0.3)

# 1. Technology Performance Overview (top left)
ax1 = fig.add_subplot(gs[0, :2])
tech_names = ['BEV', 'FCET', 'Hybrid']
expected_returns = [summary_stats[tech]['mean']/1000 for tech in tech_names]
prob_positive = [summary_stats[tech]['prob_positive'] for tech in tech_names]

# Bubble chart: return vs probability, bubble size = risk
risks = [summary_stats[tech]['std']/1000 for tech in tech_names]
bubble_sizes = [r*2 for r in risks]  # Scale for visibility

for i, tech in enumerate(tech_names):
    ax1.scatter(prob_positive[i], expected_returns[i], s=bubble_sizes[i],
               color=colors[tech], alpha=0.7, edgecolors='black', linewidth=2)
    ax1.annotate(tech, (prob_positive[i], expected_returns[i]),
                xytext=(5, 5), textcoords='offset points', fontweight='bold')

ax1.set_xlabel('Probability of Positive NPV (%)')
ax1.set_ylabel('Expected NPV ($K)')
ax1.set_title('Technology Performance Overview\n(Bubble size = Risk)', fontweight='bold')
ax1.grid(True, alpha=0.3)
ax1.axhline(y=0, color='red', linestyle='--', alpha=0.5)

# 2. Optimal Portfolio Composition (top right)
ax2 = fig.add_subplot(gs[0, 2:])
colors_pie = [colors[tech] for tech in technologies]
wedges, texts, autotexts = ax2.pie(optimal_weights, labels=technologies, colors=colors_pie,
                                   autopct='%1.1f%%', startangle=90)
for autotext in autotexts:
    autotext.set_fontweight('bold')
    autotext.set_fontsize(12)
ax2.set_title('Optimal Portfolio Allocation\n(Maximizes Risk-Adjusted Return)', fontweight='bold')

# 3. Risk Metrics Comparison (middle left)
ax3 = fig.add_subplot(gs[1, :2])
risk_metrics = ['Expected NPV', 'Prob. Positive', 'Value at Risk']
bev_metrics = [summary_stats['BEV']['mean']/1000, summary_stats['BEV']['prob_positive'],
               -summary_stats['BEV']['q5']/1000]
fcet_metrics = [summary_stats['FCET']['mean']/1000, summary_stats['FCET']['prob_positive'],
                -summary_stats['FCET']['q5']/1000]
hybrid_metrics = [summary_stats['Hybrid']['mean']/1000, summary_stats['Hybrid']['prob_positive'],
                  -summary_stats['Hybrid']['q5']/1000]

# Normalize metrics for radar chart
max_vals = [max(bev_metrics[i], fcet_metrics[i], hybrid_metrics[i]) for i in range(3)]
bev_norm = [bev_metrics[i]/max_vals[i] * 10 for i in range(3)]
fcet_norm = [fcet_metrics[i]/max_vals[i] * 10 for i in range(3)]
hybrid_norm = [hybrid_metrics[i]/max_vals[i] * 10 for i in range(3)]

angles = np.linspace(0, 2*np.pi, len(risk_metrics), endpoint=False)
angles = np.concatenate((angles, [angles[0]]))

bev_norm.append(bev_norm[0])
fcet_norm.append(fcet_norm[0])
hybrid_norm.append(hybrid_norm[0])

ax3 = plt.subplot(gs[1, :2], projection='polar')
ax3.plot(angles, bev_norm, 'o-', linewidth=2, label='BEV', color=colors['BEV'])
ax3.fill(angles, bev_norm, alpha=0.25, color=colors['BEV'])
ax3.plot(angles, fcet_norm, 'o-', linewidth=2, label='FCET', color=colors['FCET'])
ax3.fill(angles, fcet_norm, alpha=0.25, color=colors['FCET'])
ax3.plot(angles, hybrid_norm, 'o-', linewidth=2, label='Hybrid', color=colors['Hybrid'])
ax3.fill(angles, hybrid_norm, alpha=0.25, color=colors['Hybrid'])

ax3.set_xticks(angles[:-1])
ax3.set_xticklabels(risk_metrics)
ax3.set_ylim(0, 10)
ax3.set_title('Risk Metrics Comparison\n(Normalized to 0-10 scale)', fontweight='bold', pad=20)
ax3.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))

# 4. Scenario Stress Test (middle right)
ax4 = fig.add_subplot(gs[1, 2:])
scenario_names_short = ['Base', 'High Energy', 'Tech Boom', 'Downturn', 'Adoption']
portfolio_scenarios = [np.dot(optimal_weights, [scenario_results[s][t] for t in technologies])
                      for s in market_scenarios.keys()]
portfolio_scenarios_k = [x/1000 for x in portfolio_scenarios]

colors_scenarios = ['green' if x > 0 else 'red' for x in portfolio_scenarios_k]
bars4 = ax4.bar(scenario_names_short, portfolio_scenarios_k, color=colors_scenarios, alpha=0.7, edgecolor='black')

for bar, value in zip(bars4, portfolio_scenarios_k):
    ax4.text(bar.get_x() + bar.get_width()/2., value + (5 if value > 0 else -5),
             f'${value:.0f}K', ha='center', va='bottom' if value > 0 else 'top', fontweight='bold')

ax4.set_ylabel('Portfolio NPV ($K)')
ax4.set_title('Scenario Stress Test Results\n(Optimal Portfolio)', fontweight='bold')
ax4.axhline(y=0, color='black', linestyle='--', alpha=0.5)
ax4.grid(axis='y', alpha=0.3)
plt.setp(ax4.xaxis.get_majorticklabels(), rotation=45, ha='right')

# 5. Key Performance Indicators (bottom)
ax5 = fig.add_subplot(gs[2, :])
ax5.axis('off')

# Create KPI boxes
kpi_data = [
    ('Expected Portfolio Return', f"${optimal_return/1000:,.0f}K", 'green'),
    ('Portfolio Success Rate', f"{np.mean(optimal_returns > 0)*100:.0f}%", 'blue'),
    ('Risk (95% VaR)', f"${np.percentile(optimal_returns, 5)/1000:,.0f}K", 'orange'),
    ('Optimal Allocation', f"{optimal_weights[0]*100:.0f}% BEV", 'purple'),
    ('Scenarios Profitable', f"{sum(1 for x in portfolio_scenarios if x > 0)}/{len(portfolio_scenarios)}", 'teal'),
    ('Sharpe Ratio', f"{optimal_sharpe:.2f}", 'brown')
]

for i, (label, value, color) in enumerate(kpi_data):
    x = i / len(kpi_data) + 0.08

    # Create KPI box
    bbox = dict(boxstyle="round,pad=0.3", facecolor=color, alpha=0.3, edgecolor=color)
    ax5.text(x, 0.7, label, ha='center', va='center', fontsize=11, fontweight='bold')
    ax5.text(x, 0.3, value, ha='center', va='center', fontsize=14, fontweight='bold',
             bbox=bbox)

ax5.set_xlim(0, 1)
ax5.set_ylim(0, 1)
ax5.set_title('Key Performance Indicators', fontweight='bold', fontsize=14, y=0.95)

plt.suptitle('Monte Carlo Risk Analysis - Executive Dashboard', fontsize=18, fontweight='bold', y=0.98)
plt.show()

# Print executive summary
print("=" * 80)
print("MONTE CARLO RISK ANALYSIS - EXECUTIVE SUMMARY")
print("=" * 80)

print(f"\n📊 SIMULATION PARAMETERS:")
print(f"• Monte Carlo simulations: {n_simulations:,} iterations per technology")
print(f"• Analysis period: {base_scenario['analysis_years']} years")
print(f"• Base annual distance: {base_scenario['annual_km']:,} km")
print(f"• Uncertainty factors: Energy prices (±20%), utilization (70-95%), degradation (±25%)")

print(f"\n🎯 TECHNOLOGY PERFORMANCE RANKING:")
tech_ranking = sorted(technologies, key=lambda t: summary_stats[t]['prob_positive'], reverse=True)
for i, tech in enumerate(tech_ranking, 1):
    stats = summary_stats[tech]
    print(f"{i}. {tech}:")
    print(f"   Expected NPV: ${stats['mean']:,.0f}")
    print(f"   Success rate: {stats['prob_positive']:.0f}%")
    print(f"   Risk (Std Dev): ${stats['std']:,.0f}")
    print(f"   95% VaR: ${stats['q5']:,.0f}")

print(f"\n🎯 OPTIMAL PORTFOLIO STRATEGY:")
print(f"• Recommended allocation:")
for tech, weight in zip(technologies, optimal_weights):
    print(f"  - {tech}: {weight*100:.1f}%")
print(f"• Expected portfolio return: ${optimal_return:,.0f}")
print(f"• Portfolio risk: ${optimal_risk:,.0f}")
print(f"• Success rate: {np.mean(optimal_returns > 0)*100:.0f}%")
print(f"• Sharpe ratio: {optimal_sharpe:.3f}")

print(f"\n⚠️ RISK ASSESSMENT:")
print(f"• Probability of portfolio loss: {100 - np.mean(optimal_returns > 0)*100:.0f}%")
print(f"• Maximum expected loss (95% VaR): ${np.percentile(optimal_returns, 5):,.0f}")
print(f"• Best case scenario: ${max(portfolio_scenarios):,.0f}")
print(f"• Worst case scenario: ${min(portfolio_scenarios):,.0f}")
print(f"• Scenario resilience: {sum(1 for x in portfolio_scenarios if x > 0)}/{len(portfolio_scenarios)} scenarios profitable")

print(f"\n🔍 KEY SENSITIVITY FACTORS:")
print("• Most impactful parameters on NPV:")
for tech in technologies:
    top_factor = max(sensitivity_results[tech].items(), key=lambda x: abs(x[1]))
    print(f"  - {tech}: {top_factor[0].replace('_', ' ').title()} (correlation: {top_factor[1]:+.2f})")

print(f"\n💡 STRATEGIC RECOMMENDATIONS:")
print(f"• Diversified portfolio approach reduces risk while maintaining returns")
print(f"• BEV technology shows highest probability of success ({summary_stats['BEV']['prob_positive']:.0f}%)")
print(f"• Portfolio performs positively in {sum(1 for x in portfolio_scenarios if x > 0)} out of {len(portfolio_scenarios)} stress scenarios")
print(f"• Key risk factors to monitor: energy prices, utilization rates, technology degradation")
print(f"• Expected portfolio payback: {-optimal_weights @ np.array([base_technologies[t]['initial_cost'] for t in technologies]) / optimal_return:.1f} years")

print(f"\n📈 INVESTMENT CASE:")
print(f"• Strong economic case with {np.mean(optimal_returns > 0)*100:.0f}% probability of positive returns")
print(f"• Diversification reduces individual technology risks")
print(f"• Robust performance across multiple market scenarios")
print(f"• Risk-adjusted returns superior to individual technology investments")

print("\n" + "="*80)
print("Analysis based on {n_simulations:,} Monte Carlo simulations with realistic parameter uncertainty")
print("Synthetic data generated for demonstration purposes")
print("="*80)
