"""SQLAlchemy database models for Facebook Ads data."""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column, String, Integer, Float, DateTime, Text, JSON, Boolean,
    ForeignKey, Index, BigInteger
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Campaign(Base):
    """Campaign data model."""

    __tablename__ = 'campaigns'

    id = Column(String(50), primary_key=True)
    name = Column(String(255), nullable=False, index=True)
    objective = Column(String(50))
    status = Column(String(20), index=True)
    daily_budget = Column(BigInteger)  # in cents
    lifetime_budget = Column(BigInteger)  # in cents
    special_ad_categories = Column(JSON)

    # Metadata
    created_time = Column(DateTime)
    updated_time = Column(DateTime)
    start_time = Column(DateTime)
    stop_time = Column(DateTime)

    # Internal tracking
    last_synced = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # Relationships
    adsets = relationship("AdSet", back_populates="campaign", cascade="all, delete-orphan")
    insights = relationship("Insight", back_populates="campaign", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_campaign_status_active', 'status', 'is_active'),
    )

    def __repr__(self):
        return f"<Campaign(id={self.id}, name={self.name}, status={self.status})>"


class AdSet(Base):
    """Ad Set data model."""

    __tablename__ = 'adsets'

    id = Column(String(50), primary_key=True)
    campaign_id = Column(String(50), ForeignKey('campaigns.id'), nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    status = Column(String(20), index=True)

    # Budget and bidding
    daily_budget = Column(BigInteger)
    lifetime_budget = Column(BigInteger)
    bid_strategy = Column(String(50))
    bid_amount = Column(Integer)

    # Optimization
    optimization_goal = Column(String(50))
    billing_event = Column(String(50))

    # Targeting
    targeting = Column(JSON)

    # Scheduling
    start_time = Column(DateTime)
    end_time = Column(DateTime)

    # Metadata
    created_time = Column(DateTime)
    updated_time = Column(DateTime)
    last_synced = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # Relationships
    campaign = relationship("Campaign", back_populates="adsets")
    ads = relationship("Ad", back_populates="adset", cascade="all, delete-orphan")
    insights = relationship("Insight", back_populates="adset", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_adset_campaign_status', 'campaign_id', 'status'),
    )

    def __repr__(self):
        return f"<AdSet(id={self.id}, name={self.name}, campaign_id={self.campaign_id})>"


class Ad(Base):
    """Ad data model."""

    __tablename__ = 'ads'

    id = Column(String(50), primary_key=True)
    adset_id = Column(String(50), ForeignKey('adsets.id'), nullable=False, index=True)
    creative_id = Column(String(50), ForeignKey('creatives.id'), index=True)
    name = Column(String(255), nullable=False, index=True)
    status = Column(String(20), index=True)

    # Metadata
    created_time = Column(DateTime)
    updated_time = Column(DateTime)
    last_synced = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # Relationships
    adset = relationship("AdSet", back_populates="ads")
    creative = relationship("Creative", back_populates="ads")
    insights = relationship("Insight", back_populates="ad", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_ad_adset_status', 'adset_id', 'status'),
    )

    def __repr__(self):
        return f"<Ad(id={self.id}, name={self.name}, adset_id={self.adset_id})>"


class Creative(Base):
    """Creative data model."""

    __tablename__ = 'creatives'

    id = Column(String(50), primary_key=True)
    name = Column(String(255), nullable=False, index=True)
    status = Column(String(20))

    # Creative content
    object_story_spec = Column(JSON)
    image_url = Column(Text)
    image_hash = Column(String(100))
    video_id = Column(String(50))
    thumbnail_url = Column(Text)

    # Creative details
    title = Column(String(255))
    body = Column(Text)
    link_url = Column(Text)
    call_to_action_type = Column(String(50))

    # Metadata
    created_time = Column(DateTime)
    updated_time = Column(DateTime)
    last_synced = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    ads = relationship("Ad", back_populates="creative")

    def __repr__(self):
        return f"<Creative(id={self.id}, name={self.name})>"


class Insight(Base):
    """Performance insights/metrics data model."""

    __tablename__ = 'insights'

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Foreign keys
    campaign_id = Column(String(50), ForeignKey('campaigns.id'), index=True)
    adset_id = Column(String(50), ForeignKey('adsets.id'), index=True)
    ad_id = Column(String(50), ForeignKey('ads.id'), index=True)

    # Time period
    date_start = Column(DateTime, nullable=False, index=True)
    date_stop = Column(DateTime, nullable=False, index=True)

    # Core metrics
    impressions = Column(BigInteger, default=0)
    clicks = Column(BigInteger, default=0)
    spend = Column(Float, default=0.0)
    reach = Column(BigInteger, default=0)
    frequency = Column(Float, default=0.0)

    # Engagement metrics
    ctr = Column(Float, default=0.0)  # Click-through rate
    cpc = Column(Float, default=0.0)  # Cost per click
    cpm = Column(Float, default=0.0)  # Cost per mille (1000 impressions)
    cpp = Column(Float, default=0.0)  # Cost per person reached

    # Conversion metrics
    actions = Column(JSON)  # All action types
    conversions = Column(Integer, default=0)
    cost_per_conversion = Column(Float, default=0.0)
    conversion_rate = Column(Float, default=0.0)

    # Revenue metrics
    purchase_roas = Column(JSON)  # Return on ad spend
    action_values = Column(JSON)  # Revenue data

    # Additional metrics
    inline_link_clicks = Column(BigInteger, default=0)
    inline_link_click_ctr = Column(Float, default=0.0)
    unique_clicks = Column(BigInteger, default=0)
    unique_ctr = Column(Float, default=0.0)
    outbound_clicks = Column(BigInteger, default=0)

    # Video metrics (if applicable)
    video_views = Column(BigInteger, default=0)
    video_avg_time_watched = Column(Float, default=0.0)
    video_p25_watched = Column(BigInteger, default=0)
    video_p50_watched = Column(BigInteger, default=0)
    video_p75_watched = Column(BigInteger, default=0)
    video_p100_watched = Column(BigInteger, default=0)

    # Metadata
    fetched_at = Column(DateTime, default=datetime.utcnow, index=True)
    level = Column(String(20))  # campaign, adset, ad

    # Relationships
    campaign = relationship("Campaign", back_populates="insights")
    adset = relationship("AdSet", back_populates="insights")
    ad = relationship("Ad", back_populates="insights")

    __table_args__ = (
        Index('idx_insight_dates', 'date_start', 'date_stop'),
        Index('idx_insight_campaign_dates', 'campaign_id', 'date_start', 'date_stop'),
        Index('idx_insight_adset_dates', 'adset_id', 'date_start', 'date_stop'),
        Index('idx_insight_ad_dates', 'ad_id', 'date_start', 'date_stop'),
    )

    def __repr__(self):
        return f"<Insight(id={self.id}, level={self.level}, date_start={self.date_start})>"


class CacheEntry(Base):
    """Generic cache for API responses."""

    __tablename__ = 'cache'

    id = Column(Integer, primary_key=True, autoincrement=True)
    cache_key = Column(String(255), unique=True, nullable=False, index=True)
    cache_value = Column(JSON, nullable=False)
    expires_at = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('idx_cache_expires', 'expires_at'),
    )

    def __repr__(self):
        return f"<CacheEntry(key={self.cache_key}, expires={self.expires_at})>"

    def is_expired(self) -> bool:
        """Check if cache entry is expired."""
        return datetime.utcnow() > self.expires_at


class CampaignHistory(Base):
    """Historical snapshot of campaign changes."""

    __tablename__ = 'campaign_history'

    id = Column(Integer, primary_key=True, autoincrement=True)
    campaign_id = Column(String(50), nullable=False, index=True)
    snapshot_time = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Historical data
    name = Column(String(255))
    status = Column(String(20))
    daily_budget = Column(BigInteger)
    lifetime_budget = Column(BigInteger)
    objective = Column(String(50))

    # What changed
    changed_fields = Column(JSON)
    change_type = Column(String(20))  # created, updated, deleted, status_change

    __table_args__ = (
        Index('idx_history_campaign_time', 'campaign_id', 'snapshot_time'),
    )

    def __repr__(self):
        return f"<CampaignHistory(campaign_id={self.campaign_id}, snapshot_time={self.snapshot_time})>"


class AdSetHistory(Base):
    """Historical snapshot of ad set changes."""

    __tablename__ = 'adset_history'

    id = Column(Integer, primary_key=True, autoincrement=True)
    adset_id = Column(String(50), nullable=False, index=True)
    campaign_id = Column(String(50), index=True)
    snapshot_time = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Historical data
    name = Column(String(255))
    status = Column(String(20))
    daily_budget = Column(BigInteger)
    targeting = Column(JSON)
    optimization_goal = Column(String(50))

    # What changed
    changed_fields = Column(JSON)
    change_type = Column(String(20))

    __table_args__ = (
        Index('idx_adset_history_time', 'adset_id', 'snapshot_time'),
    )

    def __repr__(self):
        return f"<AdSetHistory(adset_id={self.adset_id}, snapshot_time={self.snapshot_time})>"


class PerformanceSnapshot(Base):
    """Daily performance snapshots for trend analysis."""

    __tablename__ = 'performance_snapshots'

    id = Column(Integer, primary_key=True, autoincrement=True)
    entity_type = Column(String(20), nullable=False)  # campaign, adset, ad
    entity_id = Column(String(50), nullable=False, index=True)
    snapshot_date = Column(DateTime, nullable=False, index=True)

    # Aggregated metrics
    total_spend = Column(Float, default=0.0)
    total_impressions = Column(BigInteger, default=0)
    total_clicks = Column(BigInteger, default=0)
    total_conversions = Column(Integer, default=0)

    # Calculated KPIs
    avg_ctr = Column(Float, default=0.0)
    avg_cpc = Column(Float, default=0.0)
    avg_cpm = Column(Float, default=0.0)
    roas = Column(Float, default=0.0)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index('idx_snapshot_entity', 'entity_type', 'entity_id', 'snapshot_date'),
    )

    def __repr__(self):
        return f"<PerformanceSnapshot(entity_type={self.entity_type}, entity_id={self.entity_id}, date={self.snapshot_date})>"
