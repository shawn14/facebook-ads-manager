"""Database manager for handling database operations."""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path
from sqlalchemy import create_engine, desc, and_, or_, func
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import IntegrityError
from loguru import logger
import json

from .models import (
    Base, Campaign, AdSet, Ad, Creative, Insight,
    CacheEntry, CampaignHistory, AdSetHistory, PerformanceSnapshot
)


class DatabaseManager:
    """Manager for all database operations."""

    def __init__(self, db_path: Optional[str] = None):
        """Initialize database manager.

        Args:
            db_path: Path to SQLite database file (default: data/fbads.db)
        """
        if db_path is None:
            db_dir = Path.home() / "projects/facebook-ads-manager/data"
            db_dir.mkdir(parents=True, exist_ok=True)
            db_path = str(db_dir / "fbads.db")

        self.db_path = db_path
        self.engine = create_engine(f'sqlite:///{db_path}', echo=False)
        self.Session = sessionmaker(bind=self.engine)

        # Create tables if they don't exist
        Base.metadata.create_all(self.engine)
        logger.info(f"Database initialized at {db_path}")

    def get_session(self) -> Session:
        """Get a new database session."""
        return self.Session()

    # Campaign Operations

    def save_campaign(self, campaign_data: Dict[str, Any]) -> Campaign:
        """Save or update a campaign.

        Args:
            campaign_data: Campaign data from Facebook API

        Returns:
            Campaign object
        """
        session = self.get_session()
        try:
            campaign = session.query(Campaign).filter_by(id=campaign_data['id']).first()

            if campaign:
                # Update existing
                for key, value in campaign_data.items():
                    if hasattr(campaign, key):
                        setattr(campaign, key, value)
                campaign.last_synced = datetime.utcnow()

                # Record history
                self._record_campaign_history(session, campaign, 'updated')
            else:
                # Create new
                campaign = Campaign(**campaign_data)
                campaign.last_synced = datetime.utcnow()
                session.add(campaign)

                # Record history
                self._record_campaign_history(session, campaign, 'created')

            session.commit()
            logger.debug(f"Saved campaign {campaign.id}")
            return campaign
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to save campaign: {e}")
            raise
        finally:
            session.close()

    def get_campaign(self, campaign_id: str) -> Optional[Campaign]:
        """Get a campaign by ID.

        Args:
            campaign_id: Campaign ID

        Returns:
            Campaign object or None
        """
        session = self.get_session()
        try:
            return session.query(Campaign).filter_by(id=campaign_id).first()
        finally:
            session.close()

    def get_campaigns(
        self,
        status: Optional[str] = None,
        active_only: bool = True,
        limit: int = 100
    ) -> List[Campaign]:
        """Get campaigns with optional filtering.

        Args:
            status: Filter by status (ACTIVE, PAUSED, etc.)
            active_only: Only return active campaigns
            limit: Maximum number of campaigns

        Returns:
            List of Campaign objects
        """
        session = self.get_session()
        try:
            query = session.query(Campaign)

            if status:
                query = query.filter(Campaign.status == status)

            if active_only:
                query = query.filter(Campaign.is_active == True)

            query = query.order_by(desc(Campaign.created_time)).limit(limit)
            return query.all()
        finally:
            session.close()

    def _record_campaign_history(
        self,
        session: Session,
        campaign: Campaign,
        change_type: str
    ):
        """Record campaign history snapshot."""
        history = CampaignHistory(
            campaign_id=campaign.id,
            name=campaign.name,
            status=campaign.status,
            daily_budget=campaign.daily_budget,
            lifetime_budget=campaign.lifetime_budget,
            objective=campaign.objective,
            change_type=change_type
        )
        session.add(history)

    # Ad Set Operations

    def save_adset(self, adset_data: Dict[str, Any]) -> AdSet:
        """Save or update an ad set.

        Args:
            adset_data: Ad set data from Facebook API

        Returns:
            AdSet object
        """
        session = self.get_session()
        try:
            adset = session.query(AdSet).filter_by(id=adset_data['id']).first()

            if adset:
                for key, value in adset_data.items():
                    if hasattr(adset, key):
                        setattr(adset, key, value)
                adset.last_synced = datetime.utcnow()

                self._record_adset_history(session, adset, 'updated')
            else:
                adset = AdSet(**adset_data)
                adset.last_synced = datetime.utcnow()
                session.add(adset)

                self._record_adset_history(session, adset, 'created')

            session.commit()
            logger.debug(f"Saved ad set {adset.id}")
            return adset
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to save ad set: {e}")
            raise
        finally:
            session.close()

    def get_adsets_by_campaign(self, campaign_id: str) -> List[AdSet]:
        """Get all ad sets for a campaign.

        Args:
            campaign_id: Campaign ID

        Returns:
            List of AdSet objects
        """
        session = self.get_session()
        try:
            return session.query(AdSet).filter_by(
                campaign_id=campaign_id,
                is_active=True
            ).all()
        finally:
            session.close()

    def _record_adset_history(
        self,
        session: Session,
        adset: AdSet,
        change_type: str
    ):
        """Record ad set history snapshot."""
        history = AdSetHistory(
            adset_id=adset.id,
            campaign_id=adset.campaign_id,
            name=adset.name,
            status=adset.status,
            daily_budget=adset.daily_budget,
            targeting=adset.targeting,
            optimization_goal=adset.optimization_goal,
            change_type=change_type
        )
        session.add(history)

    # Ad Operations

    def save_ad(self, ad_data: Dict[str, Any]) -> Ad:
        """Save or update an ad.

        Args:
            ad_data: Ad data from Facebook API

        Returns:
            Ad object
        """
        session = self.get_session()
        try:
            ad = session.query(Ad).filter_by(id=ad_data['id']).first()

            if ad:
                for key, value in ad_data.items():
                    if hasattr(ad, key):
                        setattr(ad, key, value)
                ad.last_synced = datetime.utcnow()
            else:
                ad = Ad(**ad_data)
                ad.last_synced = datetime.utcnow()
                session.add(ad)

            session.commit()
            logger.debug(f"Saved ad {ad.id}")
            return ad
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to save ad: {e}")
            raise
        finally:
            session.close()

    def get_ads_by_adset(self, adset_id: str) -> List[Ad]:
        """Get all ads for an ad set.

        Args:
            adset_id: Ad set ID

        Returns:
            List of Ad objects
        """
        session = self.get_session()
        try:
            return session.query(Ad).filter_by(
                adset_id=adset_id,
                is_active=True
            ).all()
        finally:
            session.close()

    # Creative Operations

    def save_creative(self, creative_data: Dict[str, Any]) -> Creative:
        """Save or update a creative.

        Args:
            creative_data: Creative data from Facebook API

        Returns:
            Creative object
        """
        session = self.get_session()
        try:
            creative = session.query(Creative).filter_by(id=creative_data['id']).first()

            if creative:
                for key, value in creative_data.items():
                    if hasattr(creative, key):
                        setattr(creative, key, value)
                creative.last_synced = datetime.utcnow()
            else:
                creative = Creative(**creative_data)
                creative.last_synced = datetime.utcnow()
                session.add(creative)

            session.commit()
            logger.debug(f"Saved creative {creative.id}")
            return creative
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to save creative: {e}")
            raise
        finally:
            session.close()

    # Insights Operations

    def save_insights(self, insights_data: List[Dict[str, Any]]) -> int:
        """Batch save insights data.

        Args:
            insights_data: List of insight dictionaries

        Returns:
            Number of insights saved
        """
        session = self.get_session()
        count = 0
        try:
            for data in insights_data:
                insight = Insight(**data)
                session.add(insight)
                count += 1

            session.commit()
            logger.debug(f"Saved {count} insights")
            return count
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to save insights: {e}")
            raise
        finally:
            session.close()

    def get_insights(
        self,
        campaign_id: Optional[str] = None,
        adset_id: Optional[str] = None,
        ad_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 1000
    ) -> List[Insight]:
        """Get insights with filtering.

        Args:
            campaign_id: Filter by campaign ID
            adset_id: Filter by ad set ID
            ad_id: Filter by ad ID
            start_date: Filter by start date
            end_date: Filter by end date
            limit: Maximum number of results

        Returns:
            List of Insight objects
        """
        session = self.get_session()
        try:
            query = session.query(Insight)

            if campaign_id:
                query = query.filter(Insight.campaign_id == campaign_id)
            if adset_id:
                query = query.filter(Insight.adset_id == adset_id)
            if ad_id:
                query = query.filter(Insight.ad_id == ad_id)
            if start_date:
                query = query.filter(Insight.date_start >= start_date)
            if end_date:
                query = query.filter(Insight.date_stop <= end_date)

            query = query.order_by(desc(Insight.date_start)).limit(limit)
            return query.all()
        finally:
            session.close()

    def get_latest_insights(
        self,
        entity_id: str,
        days: int = 7
    ) -> List[Insight]:
        """Get latest insights for an entity.

        Args:
            entity_id: Campaign, ad set, or ad ID
            days: Number of days to look back

        Returns:
            List of Insight objects
        """
        session = self.get_session()
        try:
            cutoff = datetime.utcnow() - timedelta(days=days)
            query = session.query(Insight).filter(
                or_(
                    Insight.campaign_id == entity_id,
                    Insight.adset_id == entity_id,
                    Insight.ad_id == entity_id
                ),
                Insight.date_start >= cutoff
            ).order_by(desc(Insight.date_start))

            return query.all()
        finally:
            session.close()

    # Cache Operations

    def cache_set(
        self,
        key: str,
        value: Any,
        ttl_hours: int = 1
    ):
        """Set a cache entry.

        Args:
            key: Cache key
            value: Value to cache (will be JSON serialized)
            ttl_hours: Time to live in hours
        """
        session = self.get_session()
        try:
            expires_at = datetime.utcnow() + timedelta(hours=ttl_hours)

            entry = session.query(CacheEntry).filter_by(cache_key=key).first()

            if entry:
                entry.cache_value = value
                entry.expires_at = expires_at
                entry.updated_at = datetime.utcnow()
            else:
                entry = CacheEntry(
                    cache_key=key,
                    cache_value=value,
                    expires_at=expires_at
                )
                session.add(entry)

            session.commit()
            logger.debug(f"Cached {key} (expires in {ttl_hours}h)")
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to set cache: {e}")
            raise
        finally:
            session.close()

    def cache_get(self, key: str) -> Optional[Any]:
        """Get a cache entry.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found or expired
        """
        session = self.get_session()
        try:
            entry = session.query(CacheEntry).filter_by(cache_key=key).first()

            if not entry:
                return None

            if entry.is_expired():
                session.delete(entry)
                session.commit()
                return None

            return entry.cache_value
        finally:
            session.close()

    def cache_delete(self, key: str):
        """Delete a cache entry.

        Args:
            key: Cache key
        """
        session = self.get_session()
        try:
            session.query(CacheEntry).filter_by(cache_key=key).delete()
            session.commit()
        finally:
            session.close()

    def cache_clear_expired(self) -> int:
        """Clear all expired cache entries.

        Returns:
            Number of entries deleted
        """
        session = self.get_session()
        try:
            count = session.query(CacheEntry).filter(
                CacheEntry.expires_at < datetime.utcnow()
            ).delete()
            session.commit()
            logger.info(f"Cleared {count} expired cache entries")
            return count
        finally:
            session.close()

    # Performance Snapshots

    def save_performance_snapshot(
        self,
        entity_type: str,
        entity_id: str,
        metrics: Dict[str, Any]
    ) -> PerformanceSnapshot:
        """Save a daily performance snapshot.

        Args:
            entity_type: Type (campaign, adset, ad)
            entity_id: Entity ID
            metrics: Performance metrics

        Returns:
            PerformanceSnapshot object
        """
        session = self.get_session()
        try:
            snapshot = PerformanceSnapshot(
                entity_type=entity_type,
                entity_id=entity_id,
                snapshot_date=datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0),
                **metrics
            )
            session.add(snapshot)
            session.commit()
            logger.debug(f"Saved performance snapshot for {entity_type} {entity_id}")
            return snapshot
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to save performance snapshot: {e}")
            raise
        finally:
            session.close()

    def get_performance_trend(
        self,
        entity_id: str,
        days: int = 30
    ) -> List[PerformanceSnapshot]:
        """Get performance trend for an entity.

        Args:
            entity_id: Entity ID
            days: Number of days to look back

        Returns:
            List of PerformanceSnapshot objects
        """
        session = self.get_session()
        try:
            cutoff = datetime.utcnow() - timedelta(days=days)
            return session.query(PerformanceSnapshot).filter(
                PerformanceSnapshot.entity_id == entity_id,
                PerformanceSnapshot.snapshot_date >= cutoff
            ).order_by(PerformanceSnapshot.snapshot_date).all()
        finally:
            session.close()

    # Statistics and Analytics

    def get_campaign_stats(
        self,
        campaign_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get aggregated statistics for a campaign.

        Args:
            campaign_id: Campaign ID
            start_date: Start date for filtering
            end_date: End date for filtering

        Returns:
            Dictionary of aggregated metrics
        """
        session = self.get_session()
        try:
            query = session.query(
                func.sum(Insight.impressions).label('total_impressions'),
                func.sum(Insight.clicks).label('total_clicks'),
                func.sum(Insight.spend).label('total_spend'),
                func.sum(Insight.conversions).label('total_conversions'),
                func.avg(Insight.ctr).label('avg_ctr'),
                func.avg(Insight.cpc).label('avg_cpc'),
                func.avg(Insight.cpm).label('avg_cpm')
            ).filter(Insight.campaign_id == campaign_id)

            if start_date:
                query = query.filter(Insight.date_start >= start_date)
            if end_date:
                query = query.filter(Insight.date_stop <= end_date)

            result = query.first()

            return {
                'total_impressions': result.total_impressions or 0,
                'total_clicks': result.total_clicks or 0,
                'total_spend': result.total_spend or 0.0,
                'total_conversions': result.total_conversions or 0,
                'avg_ctr': result.avg_ctr or 0.0,
                'avg_cpc': result.avg_cpc or 0.0,
                'avg_cpm': result.avg_cpm or 0.0
            }
        finally:
            session.close()

    # Cleanup and Maintenance

    def cleanup_old_data(self, days: int = 90) -> Dict[str, int]:
        """Clean up old data.

        Args:
            days: Delete data older than this many days

        Returns:
            Dictionary with counts of deleted records
        """
        session = self.get_session()
        try:
            cutoff = datetime.utcnow() - timedelta(days=days)
            counts = {}

            # Clean old insights
            counts['insights'] = session.query(Insight).filter(
                Insight.fetched_at < cutoff
            ).delete()

            # Clean old snapshots
            counts['snapshots'] = session.query(PerformanceSnapshot).filter(
                PerformanceSnapshot.snapshot_date < cutoff
            ).delete()

            # Clean old history
            counts['campaign_history'] = session.query(CampaignHistory).filter(
                CampaignHistory.snapshot_time < cutoff
            ).delete()

            counts['adset_history'] = session.query(AdSetHistory).filter(
                AdSetHistory.snapshot_time < cutoff
            ).delete()

            session.commit()
            logger.info(f"Cleaned up old data: {counts}")
            return counts
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to cleanup old data: {e}")
            raise
        finally:
            session.close()

    def close(self):
        """Close database connections."""
        self.engine.dispose()
        logger.info("Database connections closed")
