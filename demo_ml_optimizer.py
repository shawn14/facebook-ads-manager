"""Demo script for ML-powered optimization recommendations.

This script demonstrates:
- Training ML models on campaign data
- Performance prediction
- Success classification
- Automated optimization recommendations
- What-if scenario analysis
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import json


def generate_training_data(days=90):
    """Generate synthetic campaign data for ML training."""
    dates = [datetime.now() - timedelta(days=i) for i in range(days, 0, -1)]

    data = []
    for i, date in enumerate(dates):
        # Simulate different campaign scenarios

        # Base metrics
        base_spend = np.random.uniform(80, 150)

        # Add trends
        trend_factor = 1 + (i / days) * 0.3

        # Seasonality (weekends better)
        weekday = date.weekday()
        seasonal_factor = 1.4 if weekday in [5, 6] else 1.0

        # Time of month (beginning and end are better)
        day_of_month = date.day
        monthly_factor = 1.2 if day_of_month <= 5 or day_of_month >= 25 else 1.0

        # Random variation
        noise = np.random.normal(1, 0.2)

        spend = base_spend * trend_factor * seasonal_factor * monthly_factor * noise

        # Performance varies by spend level (diminishing returns)
        efficiency = 1.0 - (spend / 500) * 0.3  # Lower efficiency at higher spend

        impressions = int(spend * 120 * efficiency)
        clicks = int(impressions * np.random.uniform(0.015, 0.025))
        reach = int(impressions * np.random.uniform(0.6, 0.8))
        frequency = impressions / reach if reach > 0 else 1.0

        # Conversions depend on CTR, day of week, and randomness
        # Add more variation - some days perform poorly
        base_cvr = 0.05  # 5% conversion rate from clicks
        cvr_factor = seasonal_factor * monthly_factor * np.random.normal(1, 0.4)

        # Occasionally have very poor performance days
        if np.random.random() < 0.2:  # 20% of days are poor performers
            cvr_factor *= 0.3

        conversions = max(0, int(clicks * base_cvr * cvr_factor))

        data.append({
            'date': date,
            'date_start': date.strftime('%Y-%m-%d'),
            'impressions': impressions,
            'clicks': clicks,
            'spend': spend,
            'reach': reach,
            'frequency': frequency,
            'conversions': conversions,
            'day_of_week': weekday,
            'is_weekend': 1 if weekday >= 5 else 0,
            'day_of_month': day_of_month,
            'month': date.month
        })

    return data


def prepare_ml_features(data):
    """Prepare features for ML model."""
    df = pd.DataFrame(data)

    # Calculate derived metrics
    df['ctr'] = np.where(df['impressions'] > 0, df['clicks'] / df['impressions'] * 100, 0)
    df['cpc'] = np.where(df['clicks'] > 0, df['spend'] / df['clicks'], 0)
    df['cpa'] = np.where(df['conversions'] > 0, df['spend'] / df['conversions'], 0)
    df['revenue'] = df['conversions'] * 50  # $50 AOV
    df['roas'] = np.where(df['spend'] > 0, df['revenue'] / df['spend'], 0)

    # Add lag features
    for col in ['spend', 'conversions', 'ctr', 'roas']:
        df[f'{col}_lag1'] = df[col].shift(1)
        df[f'{col}_lag7'] = df[col].shift(7)

    # Add rolling averages
    for col in ['spend', 'conversions', 'roas']:
        df[f'{col}_ma7'] = df[col].rolling(window=7, min_periods=1).mean()
        df[f'{col}_ma14'] = df[col].rolling(window=14, min_periods=1).mean()

    # Success classification (ROAS >= 1.5)
    df['is_successful'] = (df['roas'] >= 1.5).astype(int)

    df = df.fillna(0)

    return df


def train_performance_model(df, target='conversions'):
    """Train a simple performance prediction model."""
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import r2_score, mean_squared_error

    # Select features
    feature_cols = [
        'impressions', 'clicks', 'spend', 'reach', 'frequency',
        'ctr', 'cpc', 'day_of_week', 'is_weekend', 'day_of_month', 'month',
        'spend_lag1', 'conversions_lag1', 'ctr_lag1', 'roas_lag1',
        'spend_ma7', 'conversions_ma7', 'roas_ma7'
    ]

    X = df[feature_cols].values
    y = df[target].values

    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Train model
    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        n_jobs=-1
    )

    model.fit(X_train_scaled, y_train)

    # Evaluate
    y_pred = model.predict(X_test_scaled)
    r2 = r2_score(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))

    # Feature importance
    feature_importance = sorted(
        zip(feature_cols, model.feature_importances_),
        key=lambda x: x[1],
        reverse=True
    )

    return {
        'model': model,
        'scaler': scaler,
        'feature_cols': feature_cols,
        'r2_score': r2,
        'rmse': rmse,
        'feature_importance': feature_importance
    }


def train_success_classifier(df):
    """Train a model to classify successful campaigns."""
    from sklearn.ensemble import GradientBoostingClassifier
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler

    feature_cols = [
        'impressions', 'clicks', 'spend', 'reach', 'frequency',
        'ctr', 'cpc', 'day_of_week', 'is_weekend'
    ]

    X = df[feature_cols].values
    y = df['is_successful'].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    model = GradientBoostingClassifier(
        n_estimators=100,
        max_depth=5,
        learning_rate=0.1,
        random_state=42
    )

    model.fit(X_train_scaled, y_train)

    train_acc = model.score(X_train_scaled, y_train)
    test_acc = model.score(X_test_scaled, y_test)

    feature_importance = sorted(
        zip(feature_cols, model.feature_importances_),
        key=lambda x: x[1],
        reverse=True
    )

    return {
        'model': model,
        'scaler': scaler,
        'feature_cols': feature_cols,
        'train_accuracy': train_acc,
        'test_accuracy': test_acc,
        'feature_importance': feature_importance
    }


def generate_recommendations(df):
    """Generate optimization recommendations based on data analysis."""
    recommendations = []

    # Analyze recent performance
    recent = df.tail(7)
    older = df.iloc[-14:-7]

    avg_roas_recent = recent['roas'].mean()
    avg_roas_older = older['roas'].mean()
    avg_ctr_recent = recent['ctr'].mean()
    avg_ctr_older = older['ctr'].mean()
    avg_frequency = recent['frequency'].mean()

    # Budget recommendation
    if avg_roas_recent >= 2.5:
        recommendations.append({
            'type': 'budget',
            'action': 'increase',
            'priority': 90,
            'recommendation': 'Increase daily budget by 20-30%',
            'reason': f'Excellent ROAS ({avg_roas_recent:.2f}x) - scale winning campaign',
            'expected_impact': 'Higher conversions while maintaining efficiency'
        })
    elif avg_roas_recent < 1.2:
        recommendations.append({
            'type': 'budget',
            'action': 'decrease',
            'priority': 95,
            'recommendation': 'Decrease daily budget by 30-50%',
            'reason': f'Low ROAS ({avg_roas_recent:.2f}x) - reduce spend',
            'expected_impact': 'Lower losses, focus on optimization'
        })

    # Creative refresh
    if avg_ctr_recent < avg_ctr_older * 0.8:
        recommendations.append({
            'type': 'creative',
            'action': 'refresh',
            'priority': 85,
            'recommendation': 'Refresh ad creative - CTR declining',
            'reason': f'CTR dropped from {avg_ctr_older:.2f}% to {avg_ctr_recent:.2f}%',
            'expected_impact': 'Improved engagement and click-through rate'
        })

    # Audience saturation
    if avg_frequency > 3.0:
        recommendations.append({
            'type': 'audience',
            'action': 'expand',
            'priority': 80,
            'recommendation': 'Expand audience targeting',
            'reason': f'High frequency ({avg_frequency:.2f}) indicates saturation',
            'expected_impact': 'Reach new prospects, lower frequency'
        })

    # Day of week optimization
    day_perf = df.groupby('day_of_week')['conversions'].sum().sort_values(ascending=False)
    best_days = day_perf.head(3).index.tolist()
    day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

    if day_perf.std() > day_perf.mean() * 0.3:
        best_day_names = [day_names[d] for d in best_days]
        recommendations.append({
            'type': 'timing',
            'action': 'adjust_schedule',
            'priority': 70,
            'recommendation': f'Increase budget on {", ".join(best_day_names[:2])}',
            'reason': f'Best performance on {", ".join(best_day_names)}',
            'expected_impact': 'Better budget allocation to high-performing days'
        })

    # Sort by priority
    recommendations.sort(key=lambda x: x['priority'], reverse=True)

    return recommendations


def main():
    """Run ML optimizer demo."""
    print("=" * 80)
    print("Facebook Ads Manager - ML-Powered Optimization Demo")
    print("=" * 80)
    print()

    # Generate training data
    print("1. GENERATING TRAINING DATA")
    print("-" * 80)
    print("Creating 90 days of synthetic campaign data...")
    training_data = generate_training_data(days=90)
    df = prepare_ml_features(training_data)
    print(f"✓ Generated {len(df)} days of training data")
    print(f"  - Success rate: {df['is_successful'].mean() * 100:.1f}%")
    print(f"  - Avg ROAS: {df['roas'].mean():.2f}x")
    print(f"  - Avg conversions/day: {df['conversions'].mean():.1f}")
    print()

    # Train performance predictor
    print("2. TRAINING PERFORMANCE PREDICTION MODEL")
    print("-" * 80)
    print("Training Random Forest model to predict conversions...")
    perf_model = train_performance_model(df, target='conversions')
    print(f"✓ Model trained successfully")
    print(f"  - R² Score: {perf_model['r2_score']:.3f}")
    print(f"  - RMSE: {perf_model['rmse']:.2f}")
    print(f"\n  Top 5 features by importance:")
    for feat, imp in perf_model['feature_importance'][:5]:
        print(f"    {feat}: {imp:.3f}")
    print()

    # Train success classifier
    print("3. TRAINING SUCCESS CLASSIFICATION MODEL")
    print("-" * 80)
    print("Training Gradient Boosting classifier...")
    class_model = train_success_classifier(df)
    print(f"✓ Classifier trained successfully")
    print(f"  - Train Accuracy: {class_model['train_accuracy']:.3f}")
    print(f"  - Test Accuracy: {class_model['test_accuracy']:.3f}")
    print(f"\n  Top 5 features by importance:")
    for feat, imp in class_model['feature_importance'][:5]:
        print(f"    {feat}: {imp:.3f}")
    print()

    # Make predictions
    print("4. PERFORMANCE PREDICTIONS")
    print("-" * 80)
    print("Predicting next day's conversions...")

    # Get latest data point
    latest = df.iloc[-1]
    features = [latest[col] for col in perf_model['feature_cols']]
    features_scaled = perf_model['scaler'].transform([features])

    predicted_conversions = perf_model['model'].predict(features_scaled)[0]
    actual_conversions = df.iloc[-1]['conversions']

    print(f"  Predicted conversions: {predicted_conversions:.1f}")
    print(f"  Actual conversions: {actual_conversions:.0f}")
    print(f"  Prediction error: {abs(predicted_conversions - actual_conversions):.1f}")
    print()

    # Success probability
    class_features = [latest[col] for col in class_model['feature_cols']]
    class_features_scaled = class_model['scaler'].transform([class_features])
    success_prob = class_model['model'].predict_proba(class_features_scaled)[0][1]

    print(f"  Probability of success (ROAS >= 1.5): {success_prob * 100:.1f}%")
    print()

    # Generate recommendations
    print("5. OPTIMIZATION RECOMMENDATIONS")
    print("-" * 80)
    recommendations = generate_recommendations(df)

    print(f"Generated {len(recommendations)} recommendations:\n")
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec['type'].upper()} - Priority: {rec['priority']}")
        print(f"   Action: {rec['recommendation']}")
        print(f"   Reason: {rec['reason']}")
        print(f"   Impact: {rec['expected_impact']}")
        print()

    # What-if scenarios
    print("6. WHAT-IF SCENARIO ANALYSIS")
    print("-" * 80)

    scenarios = [
        {
            'name': 'Increase budget by 30%',
            'spend_multiplier': 1.3
        },
        {
            'name': 'Decrease budget by 20%',
            'spend_multiplier': 0.8
        },
        {
            'name': 'Weekend campaign only',
            'is_weekend': 1
        }
    ]

    base_features = [latest[col] for col in perf_model['feature_cols']]

    for scenario in scenarios:
        scenario_features = base_features.copy()

        # Adjust features based on scenario
        if 'spend_multiplier' in scenario:
            spend_idx = perf_model['feature_cols'].index('spend')
            scenario_features[spend_idx] *= scenario['spend_multiplier']

        if 'is_weekend' in scenario:
            weekend_idx = perf_model['feature_cols'].index('is_weekend')
            scenario_features[weekend_idx] = scenario['is_weekend']

        # Predict
        scenario_scaled = perf_model['scaler'].transform([scenario_features])
        predicted = perf_model['model'].predict(scenario_scaled)[0]

        change = ((predicted - actual_conversions) / actual_conversions * 100) if actual_conversions > 0 else 0

        print(f"{scenario['name']}:")
        print(f"  Predicted conversions: {predicted:.1f} ({change:+.1f}% change)")
        print()

    # Save summary report
    print("7. SAVING RESULTS")
    print("-" * 80)

    report = {
        'generated_at': datetime.now().isoformat(),
        'model_performance': {
            'predictor_r2': perf_model['r2_score'],
            'predictor_rmse': perf_model['rmse'],
            'classifier_accuracy': class_model['test_accuracy']
        },
        'current_metrics': {
            'avg_spend': float(df.tail(7)['spend'].mean()),
            'avg_conversions': float(df.tail(7)['conversions'].mean()),
            'avg_roas': float(df.tail(7)['roas'].mean()),
            'success_probability': float(success_prob)
        },
        'recommendations': recommendations
    }

    Path('exports').mkdir(exist_ok=True)
    report_path = 'exports/ml_optimization_report.json'
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"✓ ML optimization report saved to {report_path}")
    print()

    print("=" * 80)
    print("Demo complete! ML models trained and recommendations generated.")
    print("=" * 80)


if __name__ == '__main__':
    main()
