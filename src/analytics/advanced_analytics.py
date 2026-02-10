"""Advanced analytics module with trend detection and statistical analysis."""

from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import json
from functools import lru_cache
import hashlib

import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.signal import find_peaks
from loguru import logger

# Set style for visualizations
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)


class AdvancedAnalytics:
    """Advanced analytics with trend detection, forecasting, and statistical analysis."""

    def __init__(self, api_client, cache_dir: Optional[str] = None):
        """Initialize advanced analytics.

        Args:
            api_client: FacebookAdsClient instance
            cache_dir: Directory for caching expensive computations
        """
        self.client = api_client
        self.config = api_client.config
        self.cache_dir = Path(cache_dir or "cache")
        self.cache_dir.mkdir(exist_ok=True)
        self.exports_dir = Path("exports")
        self.exports_dir.mkdir(exist_ok=True)

    def _get_time_series_data(
        self,
        campaign_id: Optional[str] = None,
        days: int = 90,
        level: str = 'campaign'
    ) -> pd.DataFrame:
        """Fetch and prepare time-series data.

        Args:
            campaign_id: Campaign ID (None for account-level)
            days: Number of days of historical data
            level: Data level (campaign, adset, ad)

        Returns:
            DataFrame with time-series data
        """
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        # Fetch insights with daily breakdown
        if campaign_id:
            insights = self.client.get_campaign_insights(
                campaign_id,
                time_range={
                    'since': start_date.strftime('%Y-%m-%d'),
                    'until': end_date.strftime('%Y-%m-%d')
                },
                time_increment=1  # Daily
            )
        else:
            insights = self.client.get_account_insights(
                time_range={
                    'since': start_date.strftime('%Y-%m-%d'),
                    'until': end_date.strftime('%Y-%m-%d')
                },
                time_increment=1,
                level=level
            )

        if not insights:
            return pd.DataFrame()

        # Convert to DataFrame
        df = pd.DataFrame(insights)

        # Parse dates
        if 'date_start' in df.columns:
            df['date'] = pd.to_datetime(df['date_start'])
        else:
            df['date'] = pd.date_range(start=start_date, periods=len(df), freq='D')

        # Convert numeric columns
        numeric_cols = ['impressions', 'clicks', 'spend', 'reach', 'frequency']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        # Calculate derived metrics
        df['ctr'] = np.where(df['impressions'] > 0, df['clicks'] / df['impressions'] * 100, 0)
        df['cpc'] = np.where(df['clicks'] > 0, df['spend'] / df['clicks'], 0)

        # Extract conversions
        if 'actions' in df.columns:
            df['conversions'] = df['actions'].apply(self._extract_conversions)
        else:
            df['conversions'] = 0

        df['cpa'] = np.where(df['conversions'] > 0, df['spend'] / df['conversions'], 0)

        # Calculate ROAS
        avg_order_value = self.config.get('analytics', {}).get('avg_order_value', 50)
        df['revenue'] = df['conversions'] * avg_order_value
        df['roas'] = np.where(df['spend'] > 0, df['revenue'] / df['spend'], 0)

        return df.sort_values('date')

    @staticmethod
    def _extract_conversions(actions) -> int:
        """Extract conversion count from actions data."""
        if not actions or not isinstance(actions, list):
            return 0

        for action in actions:
            if 'purchase' in action.get('action_type', '').lower():
                return int(action.get('value', 0))
        return 0

    def detect_trends(
        self,
        campaign_id: Optional[str] = None,
        days: int = 90,
        metrics: Optional[List[str]] = None
    ) -> Dict:
        """Detect trends in campaign performance.

        Args:
            campaign_id: Campaign ID (None for account-level)
            days: Days of historical data
            metrics: List of metrics to analyze

        Returns:
            Dictionary with trend analysis results
        """
        df = self._get_time_series_data(campaign_id, days)

        if df.empty:
            return {'error': 'No data available'}

        if metrics is None:
            metrics = ['spend', 'conversions', 'roas', 'ctr', 'cpc']

        results = {}

        for metric in metrics:
            if metric not in df.columns:
                continue

            series = df[metric].values
            dates = df['date'].values

            # Calculate trend using linear regression
            x = np.arange(len(series))
            valid_idx = ~np.isnan(series)

            if valid_idx.sum() < 2:
                continue

            slope, intercept, r_value, p_value, std_err = stats.linregress(
                x[valid_idx], series[valid_idx]
            )

            # Determine trend direction
            if p_value < 0.05:  # Statistically significant
                if slope > 0:
                    trend = 'increasing'
                    significance = 'significant'
                else:
                    trend = 'decreasing'
                    significance = 'significant'
            else:
                trend = 'stable'
                significance = 'not_significant'

            # Calculate percent change
            first_valid = series[valid_idx][0]
            last_valid = series[valid_idx][-1]
            pct_change = ((last_valid - first_valid) / first_valid * 100) if first_valid != 0 else 0

            # Detect seasonality (weekly patterns)
            seasonality = self._detect_seasonality(series)

            # Find change points
            change_points = self._detect_change_points(series, dates)

            results[metric] = {
                'trend': trend,
                'significance': significance,
                'slope': float(slope),
                'r_squared': float(r_value ** 2),
                'p_value': float(p_value),
                'percent_change': float(pct_change),
                'seasonality': seasonality,
                'change_points': change_points,
                'current_value': float(last_valid),
                'mean': float(np.nanmean(series)),
                'std': float(np.nanstd(series))
            }

        return results

    @staticmethod
    def _detect_seasonality(series: np.ndarray, period: int = 7) -> Dict:
        """Detect weekly seasonality patterns.

        Args:
            series: Time series data
            period: Period to check (default 7 for weekly)

        Returns:
            Seasonality analysis results
        """
        if len(series) < period * 2:
            return {'detected': False}

        # Calculate autocorrelation at the period
        valid_data = series[~np.isnan(series)]
        if len(valid_data) < period * 2:
            return {'detected': False}

        # Simple autocorrelation check
        mean = np.mean(valid_data)
        std = np.std(valid_data)

        if std == 0:
            return {'detected': False}

        n = len(valid_data)
        acf = np.correlate(valid_data - mean, valid_data - mean, mode='full')[n-1:] / (std**2 * n)

        if len(acf) > period:
            period_corr = acf[period]
            detected = period_corr > 0.3  # Threshold for seasonality
            return {
                'detected': bool(detected),
                'period': period,
                'correlation': float(period_corr)
            }

        return {'detected': False}

    @staticmethod
    def _detect_change_points(series: np.ndarray, dates: np.ndarray) -> List[Dict]:
        """Detect significant change points in time series.

        Args:
            series: Time series data
            dates: Corresponding dates

        Returns:
            List of detected change points
        """
        valid_idx = ~np.isnan(series)
        valid_series = series[valid_idx]
        valid_dates = dates[valid_idx]

        if len(valid_series) < 10:
            return []

        # Calculate rolling mean and std
        window = min(7, len(valid_series) // 3)
        rolling_mean = pd.Series(valid_series).rolling(window=window, center=True).mean()
        rolling_std = pd.Series(valid_series).rolling(window=window, center=True).std()

        # Z-score for anomaly detection
        z_scores = np.abs((valid_series - rolling_mean) / rolling_std)

        # Find significant changes (z-score > 2)
        change_points = []
        for idx in np.where(z_scores > 2)[0]:
            if window <= idx < len(valid_series) - window:
                change_points.append({
                    'date': str(valid_dates[idx]),
                    'value': float(valid_series[idx]),
                    'z_score': float(z_scores[idx]),
                    'type': 'spike' if valid_series[idx] > rolling_mean[idx] else 'drop'
                })

        return change_points[:10]  # Limit to top 10

    def forecast_metric(
        self,
        campaign_id: Optional[str] = None,
        metric: str = 'conversions',
        days_ahead: int = 7,
        days_history: int = 30
    ) -> Dict:
        """Forecast future metric values using time series analysis.

        Args:
            campaign_id: Campaign ID
            metric: Metric to forecast
            days_ahead: Days to forecast
            days_history: Historical days to use

        Returns:
            Forecast results with confidence intervals
        """
        df = self._get_time_series_data(campaign_id, days_history)

        if df.empty or metric not in df.columns:
            return {'error': 'Insufficient data'}

        series = df[metric].values
        dates = df['date'].values

        # Remove NaN values
        valid_idx = ~np.isnan(series)
        if valid_idx.sum() < 7:
            return {'error': 'Insufficient valid data points'}

        series = series[valid_idx]
        x = np.arange(len(series))

        # Fit linear trend
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, series)

        # Generate forecast
        future_x = np.arange(len(series), len(series) + days_ahead)
        forecast = slope * future_x + intercept

        # Calculate confidence intervals (95%)
        residuals = series - (slope * x + intercept)
        residual_std = np.std(residuals)
        confidence_interval = 1.96 * residual_std

        forecast_upper = forecast + confidence_interval
        forecast_lower = forecast - confidence_interval
        forecast_lower = np.maximum(forecast_lower, 0)  # Don't allow negative values

        # Generate future dates
        last_date = pd.to_datetime(dates[-1])
        future_dates = [last_date + timedelta(days=i+1) for i in range(days_ahead)]

        return {
            'metric': metric,
            'forecast': [float(v) for v in forecast],
            'upper_bound': [float(v) for v in forecast_upper],
            'lower_bound': [float(v) for v in forecast_lower],
            'dates': [d.strftime('%Y-%m-%d') for d in future_dates],
            'confidence_level': 0.95,
            'model_r_squared': float(r_value ** 2),
            'historical_mean': float(np.mean(series)),
            'historical_std': float(np.std(series))
        }

    def correlation_analysis(
        self,
        campaign_id: Optional[str] = None,
        days: int = 90
    ) -> Dict:
        """Analyze correlations between different metrics.

        Args:
            campaign_id: Campaign ID
            days: Days of historical data

        Returns:
            Correlation analysis results
        """
        df = self._get_time_series_data(campaign_id, days)

        if df.empty:
            return {'error': 'No data available'}

        # Select numeric metrics
        metric_cols = ['impressions', 'clicks', 'spend', 'conversions', 'ctr', 'cpc', 'cpa', 'roas']
        available_cols = [col for col in metric_cols if col in df.columns]

        if len(available_cols) < 2:
            return {'error': 'Insufficient metrics'}

        # Calculate correlation matrix
        corr_matrix = df[available_cols].corr()

        # Find strongest correlations (excluding diagonal)
        strong_correlations = []
        for i, metric1 in enumerate(available_cols):
            for j, metric2 in enumerate(available_cols):
                if i < j:  # Upper triangle only
                    corr_value = corr_matrix.iloc[i, j]
                    if abs(corr_value) > 0.5:  # Strong correlation threshold
                        strong_correlations.append({
                            'metric1': metric1,
                            'metric2': metric2,
                            'correlation': float(corr_value),
                            'strength': 'strong' if abs(corr_value) > 0.7 else 'moderate'
                        })

        return {
            'correlation_matrix': corr_matrix.to_dict(),
            'strong_correlations': sorted(
                strong_correlations,
                key=lambda x: abs(x['correlation']),
                reverse=True
            )
        }

    def performance_confidence_intervals(
        self,
        campaign_id: Optional[str] = None,
        days: int = 30,
        confidence: float = 0.95
    ) -> Dict:
        """Calculate confidence intervals for key metrics.

        Args:
            campaign_id: Campaign ID
            days: Days of historical data
            confidence: Confidence level (default 0.95)

        Returns:
            Confidence intervals for metrics
        """
        df = self._get_time_series_data(campaign_id, days)

        if df.empty:
            return {'error': 'No data available'}

        metrics = ['spend', 'conversions', 'roas', 'ctr', 'cpc']
        results = {}

        z_score = stats.norm.ppf((1 + confidence) / 2)

        for metric in metrics:
            if metric not in df.columns:
                continue

            values = df[metric].dropna()
            if len(values) < 2:
                continue

            mean = values.mean()
            std = values.std()
            se = std / np.sqrt(len(values))  # Standard error
            margin = z_score * se

            results[metric] = {
                'mean': float(mean),
                'std': float(std),
                'confidence_level': confidence,
                'lower_bound': float(mean - margin),
                'upper_bound': float(mean + margin),
                'sample_size': int(len(values))
            }

        return results

    def ab_test_significance(
        self,
        variant_a_data: Dict,
        variant_b_data: Dict,
        metric: str = 'conversions'
    ) -> Dict:
        """Test statistical significance between two variants.

        Args:
            variant_a_data: Data for variant A (dict with metric values)
            variant_b_data: Data for variant B
            metric: Metric to compare

        Returns:
            Statistical test results
        """
        values_a = variant_a_data.get(metric, [])
        values_b = variant_b_data.get(metric, [])

        if not values_a or not values_b:
            return {'error': 'Insufficient data'}

        # Perform two-sample t-test
        t_stat, p_value = stats.ttest_ind(values_a, values_b)

        # Calculate effect size (Cohen's d)
        mean_a = np.mean(values_a)
        mean_b = np.mean(values_b)
        pooled_std = np.sqrt((np.var(values_a) + np.var(values_b)) / 2)
        cohens_d = (mean_b - mean_a) / pooled_std if pooled_std > 0 else 0

        # Determine winner
        significant = p_value < 0.05
        if significant:
            winner = 'B' if mean_b > mean_a else 'A'
        else:
            winner = 'inconclusive'

        return {
            'metric': metric,
            'variant_a_mean': float(mean_a),
            'variant_b_mean': float(mean_b),
            'difference': float(mean_b - mean_a),
            'percent_difference': float((mean_b - mean_a) / mean_a * 100) if mean_a != 0 else 0,
            't_statistic': float(t_stat),
            'p_value': float(p_value),
            'significant': significant,
            'cohens_d': float(cohens_d),
            'winner': winner,
            'confidence_level': 0.95
        }

    def visualize_trends(
        self,
        campaign_id: Optional[str] = None,
        days: int = 90,
        metrics: Optional[List[str]] = None,
        filename: Optional[str] = None
    ) -> str:
        """Create trend visualization charts.

        Args:
            campaign_id: Campaign ID
            days: Days of historical data
            metrics: Metrics to visualize
            filename: Output filename

        Returns:
            Path to saved visualization
        """
        df = self._get_time_series_data(campaign_id, days)

        if df.empty:
            logger.warning("No data available for visualization")
            return ""

        if metrics is None:
            metrics = ['spend', 'conversions', 'roas', 'ctr']

        # Filter available metrics
        metrics = [m for m in metrics if m in df.columns]

        if not metrics:
            logger.warning("No valid metrics for visualization")
            return ""

        # Create subplots
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
            valid_idx = ~df[metric].isna()
            if valid_idx.sum() > 1:
                slope, intercept, r_value, _, _ = stats.linregress(
                    x[valid_idx], df[metric][valid_idx]
                )
                trend_line = slope * x + intercept
                ax.plot(df['date'], trend_line, '--', linewidth=2, alpha=0.7, label=f'Trend (R²={r_value**2:.3f})')

            # Add rolling average
            rolling_mean = df[metric].rolling(window=7, center=True).mean()
            ax.plot(df['date'], rolling_mean, linewidth=2, alpha=0.7, label='7-day MA')

            ax.set_title(f'{metric.upper()} Trend Analysis', fontsize=14, fontweight='bold')
            ax.set_xlabel('Date')
            ax.set_ylabel(metric.upper())
            ax.legend()
            ax.grid(True, alpha=0.3)

            # Rotate x-axis labels
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')

        plt.tight_layout()

        # Save figure
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"trend_analysis_{timestamp}.png"

        filepath = self.exports_dir / filename
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()

        logger.info(f"Trend visualization saved to {filepath}")
        return str(filepath)

    def visualize_correlations(
        self,
        campaign_id: Optional[str] = None,
        days: int = 90,
        filename: Optional[str] = None
    ) -> str:
        """Create correlation heatmap.

        Args:
            campaign_id: Campaign ID
            days: Days of historical data
            filename: Output filename

        Returns:
            Path to saved visualization
        """
        df = self._get_time_series_data(campaign_id, days)

        if df.empty:
            logger.warning("No data available for visualization")
            return ""

        # Select numeric metrics
        metric_cols = ['impressions', 'clicks', 'spend', 'conversions', 'ctr', 'cpc', 'cpa', 'roas']
        available_cols = [col for col in metric_cols if col in df.columns]

        if len(available_cols) < 2:
            logger.warning("Insufficient metrics for correlation analysis")
            return ""

        # Calculate correlation matrix
        corr_matrix = df[available_cols].corr()

        # Create heatmap
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

        # Save figure
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"correlation_heatmap_{timestamp}.png"

        filepath = self.exports_dir / filename
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()

        logger.info(f"Correlation heatmap saved to {filepath}")
        return str(filepath)

    def generate_insights_report(
        self,
        campaign_id: Optional[str] = None,
        days: int = 90
    ) -> Dict:
        """Generate comprehensive insights report.

        Args:
            campaign_id: Campaign ID
            days: Days of historical data

        Returns:
            Complete insights report
        """
        logger.info(f"Generating insights report for {days} days")

        report = {
            'generated_at': datetime.now().isoformat(),
            'period_days': days,
            'campaign_id': campaign_id
        }

        # Trend analysis
        report['trends'] = self.detect_trends(campaign_id, days)

        # Correlation analysis
        report['correlations'] = self.correlation_analysis(campaign_id, days)

        # Confidence intervals
        report['confidence_intervals'] = self.performance_confidence_intervals(campaign_id, days)

        # Forecasts for key metrics
        report['forecasts'] = {}
        for metric in ['conversions', 'spend', 'roas']:
            forecast = self.forecast_metric(campaign_id, metric, days_ahead=7, days_history=days)
            if 'error' not in forecast:
                report['forecasts'][metric] = forecast

        # Generate visualizations
        trend_viz = self.visualize_trends(campaign_id, days)
        corr_viz = self.visualize_correlations(campaign_id, days)

        report['visualizations'] = {
            'trends': trend_viz,
            'correlations': corr_viz
        }

        # Save report to JSON
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.exports_dir / f"insights_report_{timestamp}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        logger.info(f"Insights report saved to {report_file}")
        report['report_file'] = str(report_file)

        return report

    @lru_cache(maxsize=128)
    def _cached_computation(self, cache_key: str) -> Optional[Dict]:
        """Load cached computation result.

        Args:
            cache_key: Cache key

        Returns:
            Cached data or None
        """
        cache_file = self.cache_dir / f"{cache_key}.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load cache: {e}")
        return None

    def _save_to_cache(self, cache_key: str, data: Dict):
        """Save computation result to cache.

        Args:
            cache_key: Cache key
            data: Data to cache
        """
        cache_file = self.cache_dir / f"{cache_key}.json"
        try:
            with open(cache_file, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            logger.warning(f"Failed to save cache: {e}")

    @staticmethod
    def _generate_cache_key(*args) -> str:
        """Generate cache key from arguments.

        Args:
            *args: Arguments to hash

        Returns:
            Cache key string
        """
        key_string = "_".join(str(arg) for arg in args)
        return hashlib.md5(key_string.encode()).hexdigest()
