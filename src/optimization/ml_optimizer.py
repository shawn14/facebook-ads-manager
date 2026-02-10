"""ML-powered optimization recommendations using scikit-learn."""

from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import json
import pickle
from functools import lru_cache

from sklearn.ensemble import RandomForestRegressor, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, r2_score, classification_report
from loguru import logger


class MLOptimizer:
    """ML-powered optimization for Facebook Ads campaigns."""

    def __init__(self, api_client, model_dir: Optional[str] = None):
        """Initialize ML optimizer.

        Args:
            api_client: FacebookAdsClient instance
            model_dir: Directory for saving/loading models
        """
        self.client = api_client
        self.config = api_client.config
        self.model_dir = Path(model_dir or "models")
        self.model_dir.mkdir(exist_ok=True)

        # Models
        self.performance_predictor = None
        self.success_classifier = None
        self.scaler = StandardScaler()

    def prepare_training_data(
        self,
        campaign_id: Optional[str] = None,
        days: int = 90
    ) -> pd.DataFrame:
        """Prepare training data from historical campaign performance.

        Args:
            campaign_id: Campaign ID (None for all campaigns)
            days: Days of historical data

        Returns:
            DataFrame with features and targets
        """
        # Fetch time-series data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        if campaign_id:
            insights = self.client.get_campaign_insights(
                campaign_id,
                time_range={
                    'since': start_date.strftime('%Y-%m-%d'),
                    'until': end_date.strftime('%Y-%m-%d')
                },
                time_increment=1
            )
        else:
            insights = self.client.get_account_insights(
                time_range={
                    'since': start_date.strftime('%Y-%m-%d'),
                    'until': end_date.strftime('%Y-%m-%d')
                },
                time_increment=1,
                level='campaign'
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

        # Extract conversions
        if 'actions' in df.columns:
            df['conversions'] = df['actions'].apply(self._extract_conversions)
        else:
            df['conversions'] = 0

        # Calculate derived metrics
        df['ctr'] = np.where(df['impressions'] > 0, df['clicks'] / df['impressions'] * 100, 0)
        df['cpc'] = np.where(df['clicks'] > 0, df['spend'] / df['clicks'], 0)
        df['cpa'] = np.where(df['conversions'] > 0, df['spend'] / df['conversions'], 0)

        avg_order_value = self.config.get('analytics', {}).get('avg_order_value', 50)
        df['revenue'] = df['conversions'] * avg_order_value
        df['roas'] = np.where(df['spend'] > 0, df['revenue'] / df['spend'], 0)

        # Add time-based features
        df['day_of_week'] = df['date'].dt.dayofweek
        df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
        df['day_of_month'] = df['date'].dt.day
        df['month'] = df['date'].dt.month

        # Add lag features (previous day's performance)
        for col in ['spend', 'conversions', 'ctr', 'roas']:
            if col in df.columns:
                df[f'{col}_lag1'] = df[col].shift(1)
                df[f'{col}_lag7'] = df[col].shift(7)  # Week ago

        # Add rolling averages
        for col in ['spend', 'conversions', 'roas']:
            if col in df.columns:
                df[f'{col}_ma7'] = df[col].rolling(window=7, min_periods=1).mean()
                df[f'{col}_ma14'] = df[col].rolling(window=14, min_periods=1).mean()

        # Success target (high ROAS)
        min_roas = self.config.get('optimization', {}).get('min_roas', 1.5)
        df['is_successful'] = (df['roas'] >= min_roas).astype(int)

        # Fill NaN values
        df = df.fillna(0)

        return df

    def _extract_conversions(self, actions) -> int:
        """Extract conversion count from actions."""
        if not actions or not isinstance(actions, list):
            return 0

        for action in actions:
            if 'purchase' in action.get('action_type', '').lower():
                return int(action.get('value', 0))
        return 0

    def train_performance_predictor(
        self,
        campaign_id: Optional[str] = None,
        days: int = 90,
        target_metric: str = 'conversions'
    ) -> Dict:
        """Train a model to predict campaign performance.

        Args:
            campaign_id: Campaign ID (None for all campaigns)
            days: Days of training data
            target_metric: Metric to predict (conversions, roas, etc.)

        Returns:
            Training results and metrics
        """
        logger.info(f"Training performance predictor for {target_metric}")

        # Prepare data
        df = self.prepare_training_data(campaign_id, days)

        if df.empty or len(df) < 30:
            return {'error': 'Insufficient training data'}

        # Select features
        feature_cols = [
            'impressions', 'clicks', 'spend', 'reach', 'frequency',
            'ctr', 'cpc', 'day_of_week', 'is_weekend', 'day_of_month', 'month'
        ]

        # Add lag features if available
        for col in ['spend', 'conversions', 'ctr', 'roas']:
            if f'{col}_lag1' in df.columns:
                feature_cols.extend([f'{col}_lag1', f'{col}_lag7'])
            if f'{col}_ma7' in df.columns:
                feature_cols.extend([f'{col}_ma7', f'{col}_ma14'])

        # Filter available features
        feature_cols = [col for col in feature_cols if col in df.columns]

        if not feature_cols:
            return {'error': 'No valid features'}

        X = df[feature_cols].values
        y = df[target_metric].values

        # Remove rows with invalid targets
        valid_idx = ~np.isnan(y)
        X = X[valid_idx]
        y = y[valid_idx]

        if len(X) < 30:
            return {'error': 'Insufficient valid data'}

        # Train/test split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        # Scale features
        self.scaler.fit(X_train)
        X_train_scaled = self.scaler.transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        # Train Random Forest
        self.performance_predictor = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            random_state=42,
            n_jobs=-1
        )

        self.performance_predictor.fit(X_train_scaled, y_train)

        # Evaluate
        train_score = self.performance_predictor.score(X_train_scaled, y_train)
        test_score = self.performance_predictor.score(X_test_scaled, y_test)

        y_pred = self.performance_predictor.predict(X_test_scaled)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)

        # Feature importance
        feature_importance = list(zip(
            feature_cols,
            self.performance_predictor.feature_importances_
        ))
        feature_importance.sort(key=lambda x: x[1], reverse=True)

        results = {
            'target_metric': target_metric,
            'training_samples': len(X_train),
            'test_samples': len(X_test),
            'train_r2': float(train_score),
            'test_r2': float(test_score),
            'rmse': float(rmse),
            'r2_score': float(r2),
            'feature_importance': [
                {'feature': f, 'importance': float(imp)}
                for f, imp in feature_importance[:10]
            ]
        }

        # Save model
        self._save_model('performance_predictor', {
            'model': self.performance_predictor,
            'scaler': self.scaler,
            'feature_cols': feature_cols,
            'target_metric': target_metric
        })

        logger.info(f"Model trained: R²={r2:.3f}, RMSE={rmse:.2f}")
        return results

    def train_success_classifier(
        self,
        campaign_id: Optional[str] = None,
        days: int = 90
    ) -> Dict:
        """Train a model to classify campaigns as successful or not.

        Args:
            campaign_id: Campaign ID (None for all campaigns)
            days: Days of training data

        Returns:
            Training results
        """
        logger.info("Training success classifier")

        # Prepare data
        df = self.prepare_training_data(campaign_id, days)

        if df.empty or len(df) < 30:
            return {'error': 'Insufficient training data'}

        # Select features
        feature_cols = [
            'impressions', 'clicks', 'spend', 'reach', 'frequency',
            'ctr', 'cpc', 'day_of_week', 'is_weekend'
        ]

        feature_cols = [col for col in feature_cols if col in df.columns]

        X = df[feature_cols].values
        y = df['is_successful'].values

        # Train/test split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        # Train Gradient Boosting Classifier
        self.success_classifier = GradientBoostingClassifier(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            random_state=42
        )

        self.success_classifier.fit(X_train_scaled, y_train)

        # Evaluate
        train_acc = self.success_classifier.score(X_train_scaled, y_train)
        test_acc = self.success_classifier.score(X_test_scaled, y_test)

        # Get predictions
        y_pred = self.success_classifier.predict(X_test_scaled)

        # Feature importance
        feature_importance = list(zip(
            feature_cols,
            self.success_classifier.feature_importances_
        ))
        feature_importance.sort(key=lambda x: x[1], reverse=True)

        results = {
            'training_samples': len(X_train),
            'test_samples': len(X_test),
            'train_accuracy': float(train_acc),
            'test_accuracy': float(test_acc),
            'feature_importance': [
                {'feature': f, 'importance': float(imp)}
                for f, imp in feature_importance[:10]
            ]
        }

        # Save model
        self._save_model('success_classifier', {
            'model': self.success_classifier,
            'scaler': scaler,
            'feature_cols': feature_cols
        })

        logger.info(f"Classifier trained: Accuracy={test_acc:.3f}")
        return results

    def predict_performance(
        self,
        campaign_config: Dict
    ) -> Dict:
        """Predict campaign performance using trained model.

        Args:
            campaign_config: Campaign configuration with features

        Returns:
            Predicted performance
        """
        if self.performance_predictor is None:
            return {'error': 'Model not trained'}

        # Load model if needed
        model_data = self._load_model('performance_predictor')
        if not model_data:
            return {'error': 'Model not found'}

        model = model_data['model']
        scaler = model_data['scaler']
        feature_cols = model_data['feature_cols']

        # Extract features
        features = []
        for col in feature_cols:
            features.append(campaign_config.get(col, 0))

        X = np.array([features])
        X_scaled = scaler.transform(X)

        # Predict
        prediction = model.predict(X_scaled)[0]

        return {
            'predicted_value': float(prediction),
            'target_metric': model_data['target_metric'],
            'features_used': feature_cols
        }

    def recommend_optimizations(
        self,
        campaign_id: str,
        days: int = 30
    ) -> Dict:
        """Generate optimization recommendations for a campaign.

        Args:
            campaign_id: Campaign ID
            days: Days of historical data

        Returns:
            Optimization recommendations
        """
        logger.info(f"Generating recommendations for campaign {campaign_id}")

        # Get historical data
        df = self.prepare_training_data(campaign_id, days)

        if df.empty:
            return {'error': 'No data available'}

        # Calculate current performance
        recent_data = df.tail(7)  # Last 7 days

        current_metrics = {
            'avg_spend': float(recent_data['spend'].mean()),
            'avg_conversions': float(recent_data['conversions'].mean()),
            'avg_roas': float(recent_data['roas'].mean()),
            'avg_ctr': float(recent_data['ctr'].mean()),
            'avg_cpc': float(recent_data['cpc'].mean())
        }

        recommendations = []

        # Budget recommendations
        budget_rec = self._recommend_budget(df, current_metrics)
        if budget_rec:
            recommendations.append(budget_rec)

        # Timing recommendations
        timing_rec = self._recommend_timing(df)
        if timing_rec:
            recommendations.append(timing_rec)

        # Bid strategy recommendations
        bid_rec = self._recommend_bid_strategy(df, current_metrics)
        if bid_rec:
            recommendations.append(bid_rec)

        # Creative refresh recommendations
        creative_rec = self._recommend_creative_refresh(df)
        if creative_rec:
            recommendations.append(creative_rec)

        # Audience recommendations
        audience_rec = self._recommend_audience(df, current_metrics)
        if audience_rec:
            recommendations.append(audience_rec)

        # Rank by priority
        recommendations.sort(key=lambda x: x['priority'], reverse=True)

        return {
            'campaign_id': campaign_id,
            'current_performance': current_metrics,
            'recommendations': recommendations,
            'generated_at': datetime.now().isoformat()
        }

    def _recommend_budget(self, df: pd.DataFrame, current_metrics: Dict) -> Optional[Dict]:
        """Recommend budget adjustments."""
        avg_roas = current_metrics['avg_roas']
        min_roas = self.config.get('optimization', {}).get('min_roas', 1.5)

        # Find optimal budget from historical data
        spend_roas = df.groupby(pd.cut(df['spend'], bins=5)).agg({
            'roas': 'mean',
            'conversions': 'sum'
        }).reset_index()

        if avg_roas >= min_roas * 1.5:
            return {
                'type': 'budget',
                'action': 'increase',
                'priority': 90,
                'recommendation': 'Increase daily budget by 20-30%',
                'reason': f'Campaign performing well (ROAS: {avg_roas:.2f}x)',
                'expected_impact': 'Higher reach and conversions while maintaining ROAS'
            }
        elif avg_roas < min_roas * 0.8:
            return {
                'type': 'budget',
                'action': 'decrease',
                'priority': 95,
                'recommendation': 'Decrease daily budget by 30-50%',
                'reason': f'Low ROAS ({avg_roas:.2f}x) - reduce spend until performance improves',
                'expected_impact': 'Lower spend, focus on optimization'
            }

        return None

    def _recommend_timing(self, df: pd.DataFrame) -> Optional[Dict]:
        """Recommend optimal timing based on performance patterns."""
        # Analyze performance by day of week
        day_performance = df.groupby('day_of_week').agg({
            'conversions': 'sum',
            'roas': 'mean',
            'ctr': 'mean'
        }).reset_index()

        best_days = day_performance.nlargest(3, 'conversions')['day_of_week'].tolist()
        worst_days = day_performance.nsmallest(2, 'conversions')['day_of_week'].tolist()

        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

        if len(best_days) > 0 and day_performance['conversions'].std() > day_performance['conversions'].mean() * 0.3:
            best_day_names = [day_names[d] for d in best_days]
            worst_day_names = [day_names[d] for d in worst_days]

            return {
                'type': 'timing',
                'action': 'adjust_schedule',
                'priority': 70,
                'recommendation': f'Increase budget on {", ".join(best_day_names[:2])}',
                'reason': f'Best performance on {", ".join(best_day_names)}; weakest on {", ".join(worst_day_names)}',
                'expected_impact': 'Better allocation of budget to high-performing days'
            }

        return None

    def _recommend_bid_strategy(self, df: pd.DataFrame, current_metrics: Dict) -> Optional[Dict]:
        """Recommend bid strategy adjustments."""
        avg_cpc = current_metrics['avg_cpc']
        cpc_trend = df['cpc'].tail(14).values

        # Check if CPC is increasing
        if len(cpc_trend) > 7:
            recent_cpc = cpc_trend[-7:].mean()
            older_cpc = cpc_trend[:7].mean()

            if recent_cpc > older_cpc * 1.2:  # 20% increase
                return {
                    'type': 'bid_strategy',
                    'action': 'optimize',
                    'priority': 75,
                    'recommendation': 'Review bid strategy - CPC increasing',
                    'reason': f'CPC increased from ${older_cpc:.2f} to ${recent_cpc:.2f}',
                    'expected_impact': 'Lower cost per click, improved efficiency'
                }

        return None

    def _recommend_creative_refresh(self, df: pd.DataFrame) -> Optional[Dict]:
        """Recommend creative refresh based on performance decay."""
        if len(df) < 14:
            return None

        # Check CTR trend
        recent_ctr = df['ctr'].tail(7).mean()
        older_ctr = df['ctr'].head(7).mean()

        if recent_ctr < older_ctr * 0.8:  # 20% decline
            return {
                'type': 'creative',
                'action': 'refresh',
                'priority': 85,
                'recommendation': 'Refresh ad creative - performance declining',
                'reason': f'CTR declined from {older_ctr:.2f}% to {recent_ctr:.2f}%',
                'expected_impact': 'Improved engagement and click-through rates'
            }

        return None

    def _recommend_audience(self, df: pd.DataFrame, current_metrics: Dict) -> Optional[Dict]:
        """Recommend audience adjustments."""
        avg_frequency = df['frequency'].tail(7).mean()

        if avg_frequency > 3.0:
            return {
                'type': 'audience',
                'action': 'expand',
                'priority': 80,
                'recommendation': 'Expand audience targeting',
                'reason': f'High frequency ({avg_frequency:.2f}) indicates audience saturation',
                'expected_impact': 'Lower frequency, reach new potential customers'
            }
        elif avg_frequency < 1.2 and current_metrics['avg_roas'] >= 2.0:
            return {
                'type': 'audience',
                'action': 'increase_frequency',
                'priority': 60,
                'recommendation': 'Consider increasing frequency cap',
                'reason': 'Low frequency with good ROAS - room for more impressions',
                'expected_impact': 'Increased conversions from existing audience'
            }

        return None

    def generate_what_if_scenarios(
        self,
        campaign_id: str,
        scenarios: List[Dict]
    ) -> List[Dict]:
        """Generate predictions for what-if scenarios.

        Args:
            campaign_id: Campaign ID
            scenarios: List of scenario configurations

        Returns:
            Predictions for each scenario
        """
        results = []

        for i, scenario in enumerate(scenarios):
            prediction = self.predict_performance(scenario)

            if 'error' not in prediction:
                results.append({
                    'scenario_id': i + 1,
                    'scenario_config': scenario,
                    'prediction': prediction
                })

        return results

    def _save_model(self, model_name: str, model_data: Dict):
        """Save trained model to disk.

        Args:
            model_name: Name of the model
            model_data: Model data to save
        """
        filepath = self.model_dir / f"{model_name}.pkl"
        try:
            with open(filepath, 'wb') as f:
                pickle.dump(model_data, f)
            logger.info(f"Model saved to {filepath}")
        except Exception as e:
            logger.error(f"Failed to save model: {e}")

    def _load_model(self, model_name: str) -> Optional[Dict]:
        """Load trained model from disk.

        Args:
            model_name: Name of the model

        Returns:
            Loaded model data or None
        """
        filepath = self.model_dir / f"{model_name}.pkl"
        if not filepath.exists():
            return None

        try:
            with open(filepath, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return None
