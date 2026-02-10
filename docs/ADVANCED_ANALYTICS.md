# Advanced Analytics & ML-Powered Optimization

This document describes the advanced analytics and machine learning features added to the Facebook Ads Manager.

## Table of Contents

1. [Advanced Analytics](#advanced-analytics)
2. [ML-Powered Optimization](#ml-powered-optimization)
3. [Usage Examples](#usage-examples)
4. [API Reference](#api-reference)

## Advanced Analytics

The `AdvancedAnalytics` class provides sophisticated statistical analysis and trend detection for campaign performance.

### Features

#### 1. Trend Detection

Automatically detect trends in campaign metrics using linear regression and statistical significance testing.

- **Metrics analyzed**: spend, conversions, ROAS, CTR, CPC, CPA
- **Statistical measures**: R², p-values, percent change
- **Seasonality detection**: Weekly patterns
- **Change point detection**: Significant spikes or drops

```python
from src.analytics import AdvancedAnalytics

analytics = AdvancedAnalytics(api_client)
trends = analytics.detect_trends(campaign_id='12345', days=90)

# Output includes:
# - trend: 'increasing', 'decreasing', or 'stable'
# - significance: 'significant' or 'not_significant'
# - r_squared: Model fit quality (0-1)
# - p_value: Statistical significance
# - percent_change: Overall change percentage
# - seasonality: Weekly pattern detection
# - change_points: Anomalous dates
```

#### 2. Time Series Forecasting

Predict future performance with confidence intervals using linear extrapolation.

```python
forecast = analytics.forecast_metric(
    campaign_id='12345',
    metric='conversions',
    days_ahead=7,
    days_history=30
)

# Output includes:
# - forecast: Predicted values
# - upper_bound: 95% confidence upper bound
# - lower_bound: 95% confidence lower bound
# - dates: Forecast dates
# - model_r_squared: Model quality
```

#### 3. Correlation Analysis

Discover relationships between different metrics.

```python
correlations = analytics.correlation_analysis(campaign_id='12345', days=90)

# Output includes:
# - correlation_matrix: Full correlation matrix
# - strong_correlations: Pairs with |r| > 0.5
```

#### 4. Confidence Intervals

Calculate statistical confidence intervals for key metrics.

```python
confidence = analytics.performance_confidence_intervals(
    campaign_id='12345',
    days=30,
    confidence=0.95
)

# Output includes for each metric:
# - mean: Average value
# - std: Standard deviation
# - lower_bound: 95% CI lower bound
# - upper_bound: 95% CI upper bound
```

#### 5. A/B Test Significance

Test statistical significance between campaign variants.

```python
result = analytics.ab_test_significance(
    variant_a_data={'conversions': [10, 12, 11, ...]},
    variant_b_data={'conversions': [15, 17, 16, ...]},
    metric='conversions'
)

# Output includes:
# - significant: Boolean
# - p_value: Statistical p-value
# - cohens_d: Effect size
# - winner: 'A', 'B', or 'inconclusive'
```

#### 6. Visualizations

Generate publication-quality charts and graphs.

```python
# Trend visualization with regression lines and moving averages
trend_path = analytics.visualize_trends(
    campaign_id='12345',
    days=90,
    metrics=['spend', 'conversions', 'roas']
)

# Correlation heatmap
corr_path = analytics.visualize_correlations(
    campaign_id='12345',
    days=90
)
```

#### 7. Comprehensive Insights Report

Generate a complete analysis report with all metrics and visualizations.

```python
report = analytics.generate_insights_report(
    campaign_id='12345',
    days=90
)

# Output includes:
# - trends: Full trend analysis
# - correlations: Correlation analysis
# - confidence_intervals: Statistical bounds
# - forecasts: Predictions for key metrics
# - visualizations: Paths to saved charts
# - report_file: Path to JSON report
```

### Caching

Expensive computations are automatically cached to improve performance on repeated analyses.

---

## ML-Powered Optimization

The `MLOptimizer` class uses machine learning models to predict performance and generate optimization recommendations.

### Features

#### 1. Performance Prediction Model

Train a Random Forest regression model to predict future campaign performance.

```python
from src.optimization import MLOptimizer

ml_optimizer = MLOptimizer(api_client)

# Train the model
results = ml_optimizer.train_performance_predictor(
    campaign_id='12345',
    days=90,
    target_metric='conversions'
)

# Results include:
# - r2_score: Model accuracy (0-1)
# - rmse: Root mean squared error
# - feature_importance: Most influential features
```

**Features used:**
- Impressions, clicks, spend, reach, frequency
- CTR, CPC, CPA
- Day of week, weekend indicator
- Lag features (previous day, week ago)
- Rolling averages (7-day, 14-day)

#### 2. Success Classification Model

Train a Gradient Boosting classifier to predict campaign success (ROAS >= threshold).

```python
results = ml_optimizer.train_success_classifier(
    campaign_id='12345',
    days=90
)

# Results include:
# - train_accuracy: Training accuracy
# - test_accuracy: Test accuracy
# - feature_importance: Key success factors
```

#### 3. Automated Recommendations

Generate actionable optimization recommendations based on ML analysis.

```python
recommendations = ml_optimizer.recommend_optimizations(
    campaign_id='12345',
    days=30
)

# Recommendations include:
# - Budget adjustments
# - Timing/scheduling optimization
# - Bid strategy changes
# - Creative refresh suggestions
# - Audience expansion/refinement
```

**Recommendation Types:**

1. **Budget Recommendations**
   - Increase budget for high ROAS campaigns
   - Decrease budget for underperformers
   - Based on historical performance patterns

2. **Timing Recommendations**
   - Identify best-performing days of week
   - Adjust ad scheduling
   - Optimize for time-of-day patterns

3. **Bid Strategy Recommendations**
   - Detect rising CPC trends
   - Suggest bid cap adjustments
   - Optimize for cost efficiency

4. **Creative Refresh Recommendations**
   - Detect creative fatigue (declining CTR)
   - Suggest refresh timing
   - Based on performance decay analysis

5. **Audience Recommendations**
   - Detect audience saturation (high frequency)
   - Suggest expansion opportunities
   - Optimize frequency caps

Each recommendation includes:
- **Priority** (0-100): Urgency/importance
- **Action**: Specific action to take
- **Reason**: Data-driven explanation
- **Expected Impact**: Predicted outcome

#### 4. What-If Scenario Analysis

Predict outcomes for hypothetical campaign configurations.

```python
scenarios = [
    {'spend': 150, 'clicks': 3000, 'day_of_week': 5},  # Weekend
    {'spend': 200, 'clicks': 4000, 'day_of_week': 2},  # Weekday, higher budget
]

results = ml_optimizer.generate_what_if_scenarios(
    campaign_id='12345',
    scenarios=scenarios
)

# Compare predicted performance across scenarios
```

#### 5. Feature Importance

Understand which factors most influence campaign success.

Models automatically calculate and report:
- Feature importance scores
- Top contributing factors
- Relative impact on performance

Common top features:
- **Clicks**: Strong predictor of conversions
- **CTR**: Indicator of ad relevance
- **CPC**: Cost efficiency signal
- **Day of week**: Timing patterns
- **Spend lag features**: Historical momentum

---

## Usage Examples

### Example 1: Complete Campaign Analysis

```python
from src.analytics import AdvancedAnalytics
from src.optimization import MLOptimizer

# Initialize
analytics = AdvancedAnalytics(api_client)
ml_optimizer = MLOptimizer(api_client)

# 1. Analyze trends
trends = analytics.detect_trends(campaign_id='12345', days=90)
print(f"Conversions trend: {trends['conversions']['trend']}")
print(f"R²: {trends['conversions']['r_squared']:.3f}")

# 2. Generate forecast
forecast = analytics.forecast_metric(
    campaign_id='12345',
    metric='conversions',
    days_ahead=7
)
print(f"Predicted conversions for next week: {forecast['forecast']}")

# 3. Create visualizations
analytics.visualize_trends(campaign_id='12345', days=90)
analytics.visualize_correlations(campaign_id='12345', days=90)

# 4. Train ML models
ml_optimizer.train_performance_predictor(campaign_id='12345', days=90)
ml_optimizer.train_success_classifier(campaign_id='12345', days=90)

# 5. Get recommendations
recs = ml_optimizer.recommend_optimizations(campaign_id='12345', days=30)
for rec in recs['recommendations']:
    print(f"{rec['type']}: {rec['recommendation']}")
    print(f"Priority: {rec['priority']}, Impact: {rec['expected_impact']}")
```

### Example 2: Cross-Campaign Optimization

```python
# Analyze all campaigns and prioritize optimizations
campaigns = api_client.get_campaigns()

all_recommendations = []

for campaign in campaigns:
    recs = ml_optimizer.recommend_optimizations(
        campaign_id=campaign['id'],
        days=30
    )

    for rec in recs['recommendations']:
        rec['campaign_id'] = campaign['id']
        rec['campaign_name'] = campaign['name']
        all_recommendations.append(rec)

# Sort by priority
all_recommendations.sort(key=lambda x: x['priority'], reverse=True)

# Execute top 5 recommendations
for rec in all_recommendations[:5]:
    print(f"Campaign: {rec['campaign_name']}")
    print(f"Action: {rec['recommendation']}")
    print()
```

### Example 3: A/B Test Analysis

```python
# Compare two campaign variants
variant_a = analytics.detect_trends(campaign_id='variant_a', days=30)
variant_b = analytics.detect_trends(campaign_id='variant_b', days=30)

# Statistical significance test
significance = analytics.ab_test_significance(
    variant_a_data={'conversions': [...]},
    variant_b_data={'conversions': [...]},
    metric='conversions'
)

if significance['significant']:
    print(f"Winner: Variant {significance['winner']}")
    print(f"Improvement: {significance['percent_difference']:.1f}%")
    print(f"P-value: {significance['p_value']:.4f}")
else:
    print("No statistically significant difference detected")
```

---

## API Reference

### AdvancedAnalytics Class

#### `detect_trends(campaign_id, days, metrics)`
Detect statistical trends in performance metrics.

**Parameters:**
- `campaign_id` (str, optional): Campaign ID (None for account-level)
- `days` (int): Historical days to analyze
- `metrics` (List[str], optional): Metrics to analyze

**Returns:** Dict with trend analysis for each metric

#### `forecast_metric(campaign_id, metric, days_ahead, days_history)`
Forecast future metric values.

**Parameters:**
- `campaign_id` (str, optional): Campaign ID
- `metric` (str): Metric to forecast
- `days_ahead` (int): Number of days to forecast
- `days_history` (int): Historical days for training

**Returns:** Dict with forecast values and confidence intervals

#### `correlation_analysis(campaign_id, days)`
Analyze correlations between metrics.

**Parameters:**
- `campaign_id` (str, optional): Campaign ID
- `days` (int): Historical days to analyze

**Returns:** Dict with correlation matrix and strong correlations

#### `visualize_trends(campaign_id, days, metrics, filename)`
Create trend visualization charts.

**Parameters:**
- `campaign_id` (str, optional): Campaign ID
- `days` (int): Historical days to visualize
- `metrics` (List[str], optional): Metrics to plot
- `filename` (str, optional): Output filename

**Returns:** str - Path to saved visualization

### MLOptimizer Class

#### `train_performance_predictor(campaign_id, days, target_metric)`
Train Random Forest model to predict performance.

**Parameters:**
- `campaign_id` (str, optional): Campaign ID
- `days` (int): Training data period
- `target_metric` (str): Metric to predict (e.g., 'conversions', 'roas')

**Returns:** Dict with training results and feature importance

#### `train_success_classifier(campaign_id, days)`
Train classifier to predict campaign success.

**Parameters:**
- `campaign_id` (str, optional): Campaign ID
- `days` (int): Training data period

**Returns:** Dict with accuracy and feature importance

#### `recommend_optimizations(campaign_id, days)`
Generate optimization recommendations.

**Parameters:**
- `campaign_id` (str): Campaign ID
- `days` (int): Historical data period

**Returns:** Dict with prioritized recommendations

---

## Requirements

### Python Packages

```
numpy>=1.26.3
pandas>=2.2.0
scipy>=1.11.4
scikit-learn>=1.4.0
matplotlib>=3.8.2
seaborn>=0.13.1
```

### Configuration

Add to your config.yaml:

```yaml
analytics:
  avg_order_value: 50  # Used for ROAS calculations

optimization:
  min_roas: 1.5  # Minimum acceptable ROAS
  min_ctr: 0.5   # Minimum CTR threshold
  max_cpa: 50    # Maximum cost per acquisition
```

---

## Output Files

All generated files are saved to the `exports/` directory:

- **Visualizations**: `trend_analysis_*.png`, `correlation_heatmap_*.png`
- **Reports**: `insights_report_*.json`, `ml_optimization_report.json`
- **Models**: Saved to `models/` directory as `.pkl` files

---

## Performance Considerations

1. **Caching**: Results are cached automatically to avoid redundant API calls
2. **Model Training**: Train models periodically (weekly) with fresh data
3. **Data Requirements**: Minimum 30 days of data recommended for reliable analysis
4. **Computational Cost**: ML training is CPU-intensive; use background tasks for large datasets

---

## Best Practices

1. **Regular Updates**: Retrain ML models weekly with new data
2. **Data Quality**: Ensure sufficient historical data (90+ days ideal)
3. **Multiple Metrics**: Analyze multiple metrics to get complete picture
4. **Act on Insights**: Implement high-priority recommendations promptly
5. **A/B Testing**: Validate ML recommendations with controlled experiments
6. **Monitor Results**: Track impact of implemented optimizations

---

## Troubleshooting

### "Insufficient training data" error
- Ensure campaign has at least 30 days of data
- Check that campaign had active ad delivery during period

### Low model accuracy
- Increase training data period (try 90 days)
- Ensure data quality (no gaps, consistent delivery)
- Consider external factors (seasonality, market changes)

### Missing visualizations
- Check that `exports/` directory exists and is writable
- Verify matplotlib/seaborn are installed
- Check for errors in console output

---

## Future Enhancements

Planned features:
- Deep learning models (LSTM for time series)
- Multi-campaign portfolio optimization
- Automated recommendation execution
- Real-time anomaly detection
- Budget allocation optimization across campaigns
- Integration with external data sources (weather, events, etc.)
