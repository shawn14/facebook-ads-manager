"""Demo script for advanced analytics features.

This script demonstrates the advanced analytics capabilities including:
- Trend detection with statistical significance
- Time series forecasting
- Correlation analysis
- Confidence intervals
- A/B test significance testing
- Visualization generation
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import json


# Generate synthetic campaign data
def generate_sample_data(days=90):
    """Generate realistic synthetic campaign data."""
    dates = [datetime.now() - timedelta(days=i) for i in range(days, 0, -1)]

    data = []
    base_spend = 100
    base_conversions = 10

    for i, date in enumerate(dates):
        # Add upward trend
        trend_factor = 1 + (i / days) * 0.5

        # Add weekly seasonality (weekends perform better)
        weekday = date.weekday()
        seasonal_factor = 1.3 if weekday in [5, 6] else 1.0

        # Add random noise
        noise = np.random.normal(1, 0.15)

        spend = base_spend * trend_factor * seasonal_factor * noise
        conversions = base_conversions * trend_factor * seasonal_factor * noise
        impressions = int(spend * 100)
        clicks = int(impressions * 0.02)

        data.append({
            'date': date,
            'spend': spend,
            'conversions': conversions,
            'impressions': impressions,
            'clicks': clicks,
            'ctr': (clicks / impressions * 100) if impressions > 0 else 0,
            'cpc': (spend / clicks) if clicks > 0 else 0,
            'cpa': (spend / conversions) if conversions > 0 else 0,
            'revenue': conversions * 50,  # $50 avg order value
            'roas': (conversions * 50 / spend) if spend > 0 else 0
        })

    return pd.DataFrame(data)


# Simple trend detection
def detect_trends(df, metric='spend'):
    """Detect trends using linear regression."""
    from scipy import stats

    series = df[metric].values
    x = np.arange(len(series))

    slope, intercept, r_value, p_value, std_err = stats.linregress(x, series)

    # Determine trend
    if p_value < 0.05:
        trend = 'increasing' if slope > 0 else 'decreasing'
        significance = 'significant'
    else:
        trend = 'stable'
        significance = 'not_significant'

    # Calculate percent change
    pct_change = (series[-1] - series[0]) / series[0] * 100 if series[0] != 0 else 0

    return {
        'metric': metric,
        'trend': trend,
        'significance': significance,
        'slope': slope,
        'r_squared': r_value ** 2,
        'p_value': p_value,
        'percent_change': pct_change,
        'current_value': series[-1],
        'mean': np.mean(series),
        'std': np.std(series)
    }


# Forecast future values
def forecast_metric(df, metric='conversions', days_ahead=7):
    """Forecast future metric values."""
    from scipy import stats

    series = df[metric].values
    x = np.arange(len(series))

    # Fit linear trend
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, series)

    # Generate forecast
    future_x = np.arange(len(series), len(series) + days_ahead)
    forecast = slope * future_x + intercept

    # Calculate confidence intervals
    residuals = series - (slope * x + intercept)
    residual_std = np.std(residuals)
    confidence_interval = 1.96 * residual_std

    forecast_upper = forecast + confidence_interval
    forecast_lower = np.maximum(forecast - confidence_interval, 0)

    # Generate future dates
    last_date = df['date'].iloc[-1]
    future_dates = [last_date + timedelta(days=i+1) for i in range(days_ahead)]

    return {
        'metric': metric,
        'forecast': forecast.tolist(),
        'upper_bound': forecast_upper.tolist(),
        'lower_bound': forecast_lower.tolist(),
        'dates': [d.strftime('%Y-%m-%d') for d in future_dates],
        'confidence_level': 0.95,
        'model_r_squared': r_value ** 2
    }


# Visualize trends
def visualize_trends(df, metrics=['spend', 'conversions', 'roas'], output_path='exports/trends.png'):
    """Create trend visualization."""
    import matplotlib.pyplot as plt
    from scipy import stats

    n_metrics = len(metrics)
    fig, axes = plt.subplots(n_metrics, 1, figsize=(14, 4 * n_metrics))

    if n_metrics == 1:
        axes = [axes]

    for idx, metric in enumerate(metrics):
        ax = axes[idx]

        # Plot actual data
        ax.plot(df['date'], df[metric], marker='o', linewidth=2, markersize=4, label='Actual')

        # Add trend line
        x = np.arange(len(df))
        slope, intercept, r_value, _, _ = stats.linregress(x, df[metric])
        trend_line = slope * x + intercept
        ax.plot(df['date'], trend_line, '--', linewidth=2, alpha=0.7,
                label=f'Trend (R²={r_value**2:.3f})')

        # Add rolling average
        rolling_mean = df[metric].rolling(window=7, center=True).mean()
        ax.plot(df['date'], rolling_mean, linewidth=2, alpha=0.7, label='7-day MA')

        ax.set_title(f'{metric.upper()} Trend Analysis', fontsize=14, fontweight='bold')
        ax.set_xlabel('Date')
        ax.set_ylabel(metric.upper())
        ax.legend()
        ax.grid(True, alpha=0.3)
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')

    plt.tight_layout()

    # Save
    Path(output_path).parent.mkdir(exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

    print(f"✓ Trend visualization saved to {output_path}")
    return output_path


# Correlation heatmap
def visualize_correlations(df, output_path='exports/correlations.png'):
    """Create correlation heatmap."""
    import matplotlib.pyplot as plt
    import seaborn as sns

    metric_cols = ['impressions', 'clicks', 'spend', 'conversions', 'ctr', 'cpc', 'cpa', 'roas']
    available_cols = [col for col in metric_cols if col in df.columns]

    corr_matrix = df[available_cols].corr()

    plt.figure(figsize=(10, 8))
    sns.heatmap(
        corr_matrix,
        annot=True,
        fmt='.2f',
        cmap='coolwarm',
        center=0,
        square=True,
        linewidths=1,
        cbar_kws={"shrink": 0.8}
    )
    plt.title('Metric Correlation Heatmap', fontsize=16, fontweight='bold', pad=20)
    plt.tight_layout()

    Path(output_path).parent.mkdir(exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

    print(f"✓ Correlation heatmap saved to {output_path}")
    return output_path


def main():
    """Run advanced analytics demo."""
    print("=" * 80)
    print("Facebook Ads Manager - Advanced Analytics Demo")
    print("=" * 80)
    print()

    # Generate sample data
    print("Generating 90 days of synthetic campaign data...")
    df = generate_sample_data(days=90)
    print(f"✓ Generated {len(df)} days of data")
    print()

    # Trend detection
    print("1. TREND DETECTION")
    print("-" * 80)
    for metric in ['spend', 'conversions', 'roas', 'ctr']:
        trend_result = detect_trends(df, metric)
        print(f"\n{metric.upper()}:")
        print(f"  Trend: {trend_result['trend']} ({trend_result['significance']})")
        print(f"  R²: {trend_result['r_squared']:.3f}")
        print(f"  P-value: {trend_result['p_value']:.4f}")
        print(f"  Change: {trend_result['percent_change']:+.1f}%")
        print(f"  Current: {trend_result['current_value']:.2f}")
    print()

    # Forecasting
    print("2. FORECASTING (Next 7 Days)")
    print("-" * 80)
    for metric in ['conversions', 'spend', 'roas']:
        forecast = forecast_metric(df, metric, days_ahead=7)
        print(f"\n{metric.upper()} Forecast:")
        print(f"  Model R²: {forecast['model_r_squared']:.3f}")
        print(f"  Predicted values:")
        for i, (date, val, lower, upper) in enumerate(zip(
            forecast['dates'], forecast['forecast'],
            forecast['lower_bound'], forecast['upper_bound']
        )):
            print(f"    {date}: {val:.2f} (95% CI: {lower:.2f} - {upper:.2f})")
    print()

    # Correlation analysis
    print("3. CORRELATION ANALYSIS")
    print("-" * 80)
    metric_cols = ['impressions', 'clicks', 'spend', 'conversions', 'ctr', 'cpc', 'cpa', 'roas']
    corr_matrix = df[metric_cols].corr()

    # Find strongest correlations
    strong_corr = []
    for i, metric1 in enumerate(metric_cols):
        for j, metric2 in enumerate(metric_cols):
            if i < j:
                corr_value = corr_matrix.iloc[i, j]
                if abs(corr_value) > 0.5:
                    strong_corr.append((metric1, metric2, corr_value))

    print("\nStrong correlations (|r| > 0.5):")
    for m1, m2, corr in sorted(strong_corr, key=lambda x: abs(x[2]), reverse=True):
        print(f"  {m1} ↔ {m2}: {corr:+.3f}")
    print()

    # Confidence intervals
    print("4. CONFIDENCE INTERVALS (95%)")
    print("-" * 80)
    from scipy import stats

    for metric in ['spend', 'conversions', 'roas']:
        values = df[metric]
        mean = values.mean()
        std = values.std()
        se = std / np.sqrt(len(values))
        margin = 1.96 * se

        print(f"\n{metric.upper()}:")
        print(f"  Mean: {mean:.2f} ± {margin:.2f}")
        print(f"  95% CI: [{mean - margin:.2f}, {mean + margin:.2f}]")
        print(f"  Std Dev: {std:.2f}")
    print()

    # A/B Test Example
    print("5. A/B TEST SIGNIFICANCE")
    print("-" * 80)

    # Simulate A/B test
    variant_a = df.iloc[:45]['conversions'].values
    variant_b = df.iloc[45:]['conversions'].values * 1.15  # B is 15% better

    from scipy import stats as scipy_stats
    t_stat, p_value = scipy_stats.ttest_ind(variant_a, variant_b)

    mean_a = np.mean(variant_a)
    mean_b = np.mean(variant_b)

    print(f"\nVariant A mean: {mean_a:.2f}")
    print(f"Variant B mean: {mean_b:.2f}")
    print(f"Difference: {mean_b - mean_a:+.2f} ({(mean_b - mean_a) / mean_a * 100:+.1f}%)")
    print(f"P-value: {p_value:.4f}")
    print(f"Statistically significant: {'Yes' if p_value < 0.05 else 'No'}")
    print(f"Winner: {'Variant B' if p_value < 0.05 and mean_b > mean_a else 'Inconclusive'}")
    print()

    # Generate visualizations
    print("6. VISUALIZATIONS")
    print("-" * 80)
    viz1 = visualize_trends(df, metrics=['spend', 'conversions', 'roas'])
    viz2 = visualize_correlations(df)
    print()

    # Save summary report
    report = {
        'generated_at': datetime.now().isoformat(),
        'period_days': 90,
        'summary': {
            'total_spend': float(df['spend'].sum()),
            'total_conversions': float(df['conversions'].sum()),
            'avg_roas': float(df['roas'].mean()),
            'avg_ctr': float(df['ctr'].mean()),
        },
        'trends': {
            metric: detect_trends(df, metric)
            for metric in ['spend', 'conversions', 'roas', 'ctr']
        },
        'forecasts': {
            metric: forecast_metric(df, metric, days_ahead=7)
            for metric in ['conversions', 'spend', 'roas']
        }
    }

    report_path = 'exports/analytics_report.json'
    Path(report_path).parent.mkdir(exist_ok=True)
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2, default=str)

    print(f"✓ Summary report saved to {report_path}")
    print()

    print("=" * 80)
    print("Demo complete! Check the exports/ directory for visualizations and reports.")
    print("=" * 80)


if __name__ == '__main__':
    main()
