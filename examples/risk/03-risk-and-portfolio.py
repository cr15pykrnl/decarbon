def calculate_risk_return_metrics():
    """Calculate risk and return metrics for each technology"""
    risk_return_data = []

    for tech_name, results in simulation_results.items():
        if tech_name == 'Diesel':
            continue

        npv_dist = results['npv_distribution']

        # Return metrics
        expected_npv = np.mean(npv_dist)
        median_npv = np.median(npv_dist)

        # Risk metrics
        npv_std = np.std(npv_dist)
        value_at_risk_95 = np.percentile(npv_dist, 5)  # 95% VaR
        downside_deviation = np.std(npv_dist[npv_dist < 0])  # Downside risk

        # Risk-adjusted returns
        sharpe_ratio = expected_npv / npv_std if npv_std > 0 else 0
        sortino_ratio = expected_npv / downside_deviation if downside_deviation > 0 else np.inf

        # Probability metrics
        prob_loss = np.mean(npv_dist < 0) * 100
        prob_large_loss = np.mean(npv_dist < -100000) * 100  # Prob of losing >$100K

        risk_return_data.append({
            'Technology': tech_name,
            'Expected_NPV': expected_npv,
            'Median_NPV': median_npv,
            'NPV_Std': npv_std,
            'VaR_95': value_at_risk_95,
            'Downside_Deviation': downside_deviation,
            'Sharpe_Ratio': sharpe_ratio,
            'Sortino_Ratio': sortino_ratio,
            'Prob_Loss': prob_loss,
            'Prob_Large_Loss': prob_large_loss
        })

    return pd.DataFrame(risk_return_data)

# Calculate risk-return metrics
risk_return_df = calculate_risk_return_metrics()

# Create comprehensive risk-return visualization
fig = make_subplots(
    rows=2, cols=2,
    subplot_titles=['Risk-Return Scatter', 'Value at Risk Comparison',
                    'Risk-Adjusted Returns', 'Probability of Loss'],
    specs=[[{'type': 'scatter'}, {'type': 'bar'}],
           [{'type': 'bar'}, {'type': 'bar'}]]
)

# 1. Risk-Return Scatter Plot
for _, row in risk_return_df.iterrows():
    fig.add_trace(
        go.Scatter(
            x=[row['NPV_Std']/1000],
            y=[row['Expected_NPV']/1000],
            mode='markers+text',
            marker=dict(size=20, color=colors[row['Technology']], opacity=0.8),
            text=[row['Technology']],
            textposition='top center',
            name=row['Technology'],
            showlegend=False
        ),
        row=1, col=1
    )

fig.update_xaxes(title_text='Risk (NPV Std Dev, $K)', row=1, col=1)
fig.update_yaxes(title_text='Expected Return (NPV, $K)', row=1, col=1)

# Add quadrant lines
fig.add_hline(y=0, line_dash="dash", line_color="red", opacity=0.5, row=1, col=1)

# 2. Value at Risk Comparison
fig.add_trace(
    go.Bar(
        x=risk_return_df['Technology'],
        y=risk_return_df['VaR_95']/1000,
        marker_color=[colors[tech] for tech in risk_return_df['Technology']],
        name='95% VaR',
        showlegend=False
    ),
    row=1, col=2
)

fig.update_yaxes(title_text='95% Value at Risk ($K)', row=1, col=2)

# 3. Risk-Adjusted Returns
fig.add_trace(
    go.Bar(
        x=risk_return_df['Technology'],
        y=risk_return_df['Sharpe_Ratio'],
        marker_color=[colors[tech] for tech in risk_return_df['Technology']],
        name='Sharpe Ratio',
        showlegend=False
    ),
    row=2, col=1
)

fig.update_yaxes(title_text='Sharpe Ratio (Return/Risk)', row=2, col=1)

# 4. Probability of Loss
fig.add_trace(
    go.Bar(
        x=risk_return_df['Technology'],
        y=risk_return_df['Prob_Loss'],
        marker_color=[colors[tech] for tech in risk_return_df['Technology']],
        name='Prob of Loss',
        showlegend=False
    ),
    row=2, col=2
)

fig.update_yaxes(title_text='Probability of Loss (%)', row=2, col=2)

fig.update_layout(
    title_text='Risk-Return Analysis Dashboard',
    height=800,
    showlegend=False
)

fig.show()

# Print risk-return summary
print("Risk-Return Analysis Summary:")
print("=" * 50)

for _, row in risk_return_df.iterrows():
    print(f"\n{row['Technology']}:")
    print(f"  Expected NPV: ${row['Expected_NPV']:,.0f}")
    print(f"  Risk (Std Dev): ${row['NPV_Std']:,.0f}")
    print(f"  95% Value at Risk: ${row['VaR_95']:,.0f}")
    print(f"  Sharpe Ratio: {row['Sharpe_Ratio']:.3f}")
    print(f"  Probability of Loss: {row['Prob_Loss']:.1f}%")
    print(f"  Probability of Large Loss (>$100K): {row['Prob_Large_Loss']:.1f}%")

# Rank technologies by risk-adjusted return
risk_return_df_sorted = risk_return_df.sort_values('Sharpe_Ratio', ascending=False)
print("\nTechnology Ranking by Risk-Adjusted Return (Sharpe Ratio):")
for i, (_, row) in enumerate(risk_return_df_sorted.iterrows(), 1):
    print(f"  {i}. {row['Technology']} (Sharpe: {row['Sharpe_Ratio']:.3f})")

def calculate_portfolio_metrics(weights, returns_matrix):
    """Calculate portfolio return and risk for given weights"""
    # Portfolio returns for each simulation
    portfolio_returns = np.dot(returns_matrix, weights)

    # Portfolio metrics
    expected_return = np.mean(portfolio_returns)
    portfolio_risk = np.std(portfolio_returns)
    sharpe_ratio = expected_return / portfolio_risk if portfolio_risk > 0 else 0

    return expected_return, portfolio_risk, sharpe_ratio, portfolio_returns

def optimize_portfolio(returns_matrix, risk_tolerance=1.0):
    """Optimize portfolio weights to maximize risk-adjusted return"""
    n_assets = returns_matrix.shape[1]

    # Objective function: minimize negative Sharpe ratio
    def objective(weights):
        expected_return, portfolio_risk, sharpe_ratio, _ = calculate_portfolio_metrics(weights, returns_matrix)
        return -sharpe_ratio  # Minimize negative = maximize positive

    # Constraints
    constraints = [
        {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},  # Weights sum to 1
    ]

    # Bounds (0 to 1 for each weight)
    bounds = [(0, 1) for _ in range(n_assets)]

    # Initial guess (equal weights)
    x0 = np.array([1/n_assets] * n_assets)

    # Optimize
    result = minimize(objective, x0, method='SLSQP', bounds=bounds, constraints=constraints)

    return result.x

def generate_efficient_frontier(returns_matrix, n_points=50):
    """Generate efficient frontier by varying target returns"""
    n_assets = returns_matrix.shape[1]

    # Calculate individual asset metrics
    individual_returns = [np.mean(returns_matrix[:, i]) for i in range(n_assets)]
    individual_risks = [np.std(returns_matrix[:, i]) for i in range(n_assets)]

    min_return = min(individual_returns)
    max_return = max(individual_returns)

    target_returns = np.linspace(min_return, max_return, n_points)
    efficient_portfolios = []

    for target_return in target_returns:
        # Objective: minimize portfolio variance
        def objective(weights):
            _, portfolio_risk, _, _ = calculate_portfolio_metrics(weights, returns_matrix)
            return portfolio_risk ** 2  # Minimize variance

        # Constraints
        constraints = [
            {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},  # Weights sum to 1
            {'type': 'eq', 'fun': lambda x: np.dot(x, individual_returns) - target_return}  # Target return
        ]

        bounds = [(0, 1) for _ in range(n_assets)]
        x0 = np.array([1/n_assets] * n_assets)

        result = minimize(objective, x0, method='SLSQP', bounds=bounds, constraints=constraints)

        if result.success:
            weights = result.x
            expected_return, portfolio_risk, sharpe_ratio, _ = calculate_portfolio_metrics(weights, returns_matrix)
            efficient_portfolios.append({
                'weights': weights,
                'return': expected_return,
                'risk': portfolio_risk,
                'sharpe': sharpe_ratio
            })

    return efficient_portfolios

# Prepare returns matrix (exclude Diesel baseline)
technologies = ['BEV', 'FCET', 'Hybrid']
returns_matrix = np.column_stack([
    simulation_results[tech]['npv_distribution'] for tech in technologies
])

print(f"Portfolio optimization setup: {len(technologies)} technologies, {len(returns_matrix)} simulations")

# Find optimal portfolio
optimal_weights = optimize_portfolio(returns_matrix)
optimal_return, optimal_risk, optimal_sharpe, optimal_returns = calculate_portfolio_metrics(optimal_weights, returns_matrix)

print("\nOptimal Portfolio Composition (Max Sharpe Ratio):")
for i, (tech, weight) in enumerate(zip(technologies, optimal_weights)):
    print(f"  {tech}: {weight*100:.1f}%")

print(f"\nOptimal Portfolio Metrics:")
print(f"  Expected NPV: ${optimal_return:,.0f}")
print(f"  Risk (Std Dev): ${optimal_risk:,.0f}")
print(f"  Sharpe Ratio: {optimal_sharpe:.3f}")

# Generate efficient frontier
print("\nGenerating efficient frontier...")
efficient_portfolios = generate_efficient_frontier(returns_matrix, n_points=30)

# Create portfolio optimization visualization
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))

# 1. Efficient Frontier
if efficient_portfolios:
    frontier_returns = [p['return']/1000 for p in efficient_portfolios]
    frontier_risks = [p['risk']/1000 for p in efficient_portfolios]

    ax1.plot(frontier_risks, frontier_returns, 'b-', linewidth=2, label='Efficient Frontier')

# Plot individual technologies
for i, tech in enumerate(technologies):
    tech_return = np.mean(returns_matrix[:, i]) / 1000
    tech_risk = np.std(returns_matrix[:, i]) / 1000
    ax1.scatter(tech_risk, tech_return, s=100, color=colors[tech],
                label=tech, alpha=0.8, edgecolors='black')

# Plot optimal portfolio
ax1.scatter(optimal_risk/1000, optimal_return/1000, s=200, color='red',
           marker='*', label='Optimal Portfolio', edgecolors='black')

ax1.set_xlabel('Risk (NPV Std Dev, $K)')
ax1.set_ylabel('Expected Return (NPV, $K)')
ax1.set_title('Efficient Frontier & Optimal Portfolio')
ax1.legend()
ax1.grid(True, alpha=0.3)

# 2. Optimal Portfolio Composition (Pie Chart)
colors_pie = [colors[tech] for tech in technologies]
wedges, texts, autotexts = ax2.pie(optimal_weights, labels=technologies, colors=colors_pie,
                                   autopct='%1.1f%%', startangle=90)
ax2.set_title('Optimal Portfolio Composition\n(Maximum Sharpe Ratio)')

# 3. Portfolio Return Distribution
ax3.hist(optimal_returns/1000, bins=50, alpha=0.7, color='red', density=True)
ax3.axvline(x=optimal_return/1000, color='black', linestyle='--',
           label=f'Expected: ${optimal_return/1000:.0f}K')
ax3.axvline(x=0, color='red', linestyle=':', alpha=0.7, label='Break-even')
ax3.set_xlabel('Portfolio NPV ($K)')
ax3.set_ylabel('Probability Density')
ax3.set_title('Optimal Portfolio Return Distribution')
ax3.legend()
ax3.grid(True, alpha=0.3)

# 4. Comparison of Portfolio Strategies
strategies = ['Equal Weight', 'Optimal (Max Sharpe)', 'Conservative', 'Aggressive']

# Equal weight portfolio
equal_weights = np.array([1/3, 1/3, 1/3])
eq_return, eq_risk, eq_sharpe, _ = calculate_portfolio_metrics(equal_weights, returns_matrix)

# Conservative portfolio (favor lower risk)
conservative_weights = np.array([0.6, 0.2, 0.2])  # Heavy BEV
cons_return, cons_risk, cons_sharpe, _ = calculate_portfolio_metrics(conservative_weights, returns_matrix)

# Aggressive portfolio (favor higher return potential)
aggressive_weights = np.array([0.2, 0.6, 0.2])  # Heavy FCET
agg_return, agg_risk, agg_sharpe, _ = calculate_portfolio_metrics(aggressive_weights, returns_matrix)

strategy_returns = [eq_return/1000, optimal_return/1000, cons_return/1000, agg_return/1000]
strategy_risks = [eq_risk/1000, optimal_risk/1000, cons_risk/1000, agg_risk/1000]
strategy_sharpes = [eq_sharpe, optimal_sharpe, cons_sharpe, agg_sharpe]

colors_strategies = ['blue', 'red', 'green', 'orange']

for i, (strategy, ret, risk, color) in enumerate(zip(strategies, strategy_returns, strategy_risks, colors_strategies)):
    ax4.scatter(risk, ret, s=150, color=color, label=strategy, alpha=0.8, edgecolors='black')

ax4.set_xlabel('Risk (NPV Std Dev, $K)')
ax4.set_ylabel('Expected Return (NPV, $K)')
ax4.set_title('Portfolio Strategy Comparison')
ax4.legend()
ax4.grid(True, alpha=0.3)

plt.suptitle('Portfolio Optimization & Fleet Composition Analysis', fontsize=16, fontweight='bold')
plt.tight_layout()
plt.show()

print("\nPortfolio Strategy Comparison:")
strategy_data = [
    ('Equal Weight', equal_weights, eq_return, eq_risk, eq_sharpe),
    ('Optimal (Max Sharpe)', optimal_weights, optimal_return, optimal_risk, optimal_sharpe),
    ('Conservative', conservative_weights, cons_return, cons_risk, cons_sharpe),
    ('Aggressive', aggressive_weights, agg_return, agg_risk, agg_sharpe)
]

for strategy_name, weights, ret, risk, sharpe in strategy_data:
    print(f"\n{strategy_name}:")
    print(f"  Allocation: {' / '.join([f'{w*100:.0f}%' for w in weights])} ({' / '.join(technologies)})")
    print(f"  Expected Return: ${ret:,.0f}")
    print(f"  Risk: ${risk:,.0f}")
    print(f"  Sharpe Ratio: {sharpe:.3f}")
