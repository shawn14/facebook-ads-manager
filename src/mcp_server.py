"""MCP server — full Meta Ads account management for paid-marketing-cmo."""

import json
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp.server.fastmcp import FastMCP
from src.api_client import FacebookAdsClient
from src.campaign.manager import CampaignManager
from src.analytics.reporter import AnalyticsReporter
from src.optimization.optimizer import BudgetOptimizer

mcp = FastMCP("Paid Marketing CMO — Meta Ads")

_client = None
_campaign_mgr = None
_analytics = None
_optimizer = None

def _get_client() -> FacebookAdsClient:
    global _client
    if _client is None:
        config_path = os.environ.get("FB_CONFIG_PATH", "config/config.yaml")
        _client = FacebookAdsClient(config_path)
    return _client

def _get_managers():
    global _campaign_mgr, _analytics, _optimizer
    c = _get_client()
    if _campaign_mgr is None:
        _campaign_mgr = CampaignManager(c)
        _analytics = AnalyticsReporter(c)
        _optimizer = BudgetOptimizer(c)
    return _campaign_mgr, _analytics, _optimizer


# ── Account ───────────────────────────────────────────────────────────────────

@mcp.tool()
def get_account_info() -> str:
    """Get ad account name, currency, timezone, status, and total spend."""
    return json.dumps(_get_client().get_account_info(), indent=2, default=str)


@mcp.tool()
def get_pixels() -> str:
    """List all Facebook Pixels attached to this ad account."""
    return json.dumps(_get_client().get_pixels(), indent=2, default=str)


# ── Reporting ─────────────────────────────────────────────────────────────────

@mcp.tool()
def account_report(days: int = 7) -> str:
    """Overall account performance across all campaigns for the last N days."""
    _, analytics, _ = _get_managers()
    return json.dumps(analytics.account_report(days=days), indent=2, default=str)


@mcp.tool()
def campaign_report(campaign_id: str, days: int = 7) -> str:
    """Performance metrics (spend, CTR, CPC, ROAS, conversions) for a campaign."""
    _, analytics, _ = _get_managers()
    return json.dumps(analytics.campaign_report(campaign_id, days=days), indent=2, default=str)


@mcp.tool()
def detect_anomalies(campaign_id: str) -> str:
    """Detect spend spikes, CTR drops, or other anomalies for a campaign."""
    _, analytics, _ = _get_managers()
    return json.dumps(analytics.detect_anomalies(campaign_id), indent=2, default=str)


# ── Campaigns ─────────────────────────────────────────────────────────────────

@mcp.tool()
def list_campaigns(status: str = None, include_insights: bool = False) -> str:
    """List campaigns. status: ACTIVE, PAUSED, or omit for all."""
    mgr, _, _ = _get_managers()
    return json.dumps(mgr.list_campaigns(status_filter=status, include_insights=include_insights), indent=2, default=str)


@mcp.tool()
def create_campaign(
    name: str,
    objective: str = "OUTCOME_SALES",
    status: str = "PAUSED",
    daily_budget_usd: float = None,
) -> str:
    """Create a new campaign.

    objective options: OUTCOME_SALES, OUTCOME_LEADS, OUTCOME_TRAFFIC,
                       OUTCOME_ENGAGEMENT, OUTCOME_APP_PROMOTION, OUTCOME_AWARENESS
    status: ACTIVE or PAUSED (default PAUSED for safety)
    daily_budget_usd: optional daily budget in USD
    """
    client = _get_client()
    params = {
        'name': name,
        'objective': objective,
        'status': status,
        'special_ad_categories': [],
    }
    if daily_budget_usd is not None:
        params['daily_budget'] = int(daily_budget_usd * 100)
    campaign = client.ad_account.create_campaign(params=params)
    return json.dumps({'id': campaign['id'], 'name': name, 'status': status}, indent=2)


@mcp.tool()
def update_campaign(campaign_id: str, name: str = None, status: str = None, daily_budget_usd: float = None) -> str:
    """Update a campaign's name, status, or daily budget."""
    updates = {}
    if name:
        updates['name'] = name
    if status:
        updates['status'] = status
    if daily_budget_usd is not None:
        updates['daily_budget'] = int(daily_budget_usd * 100)
    _get_client().update_campaign(campaign_id, updates)
    return f"Campaign {campaign_id} updated: {updates}"


@mcp.tool()
def pause_campaign(campaign_id: str) -> str:
    """Pause an active campaign."""
    _get_managers()[0].pause_campaign(campaign_id)
    return f"Campaign {campaign_id} paused."


@mcp.tool()
def activate_campaign(campaign_id: str) -> str:
    """Activate a paused campaign."""
    _get_managers()[0].activate_campaign(campaign_id)
    return f"Campaign {campaign_id} activated."


@mcp.tool()
def update_budget(campaign_id: str, new_daily_budget_usd: float) -> str:
    """Update a campaign's daily budget (in USD)."""
    _get_managers()[0].update_budget(campaign_id, new_daily_budget_usd)
    return f"Campaign {campaign_id} budget updated to ${new_daily_budget_usd}/day."


# ── Ad Sets ───────────────────────────────────────────────────────────────────

@mcp.tool()
def list_adsets(campaign_id: str = None) -> str:
    """List ad sets. Optionally filter by campaign_id.

    Returns id, name, status, daily_budget, bid_strategy, bid_amount,
    optimization_goal for each ad set.
    """
    fields = [
        'id', 'name', 'status', 'campaign_id',
        'daily_budget', 'bid_strategy', 'bid_amount',
        'optimization_goal', 'billing_event',
        'targeting', 'created_time', 'updated_time'
    ]
    adsets = _get_client().get_adsets(campaign_id=campaign_id, fields=fields)
    return json.dumps([dict(a) for a in adsets], indent=2, default=str)


@mcp.tool()
def create_adset(
    campaign_id: str,
    name: str,
    daily_budget_usd: float,
    optimization_goal: str = "OFFSITE_CONVERSIONS",
    bid_strategy: str = "LOWEST_COST_WITHOUT_CAP",
    bid_cap_usd: float = None,
    age_min: int = 25,
    age_max: int = 65,
    countries: str = "US",
    status: str = "PAUSED",
) -> str:
    """Create an ad set under a campaign.

    bid_strategy options:
      LOWEST_COST_WITHOUT_CAP  — Meta optimizes freely (no cap)
      LOWEST_COST_WITH_BID_CAP — set bid_cap_usd to cap the max bid
      COST_CAP                 — set bid_cap_usd as target cost per result

    optimization_goal options: OFFSITE_CONVERSIONS, LINK_CLICKS, REACH,
                                IMPRESSIONS, LANDING_PAGE_VIEWS, LEAD_GENERATION

    countries: comma-separated ISO codes, e.g. "US" or "US,CA,GB"
    """
    targeting = {
        'geo_locations': {'countries': [c.strip() for c in countries.split(',')]},
        'age_min': age_min,
        'age_max': age_max,
    }
    params = {
        'name': name,
        'campaign_id': campaign_id,
        'daily_budget': int(daily_budget_usd * 100),
        'targeting': targeting,
        'optimization_goal': optimization_goal,
        'billing_event': 'IMPRESSIONS',
        'bid_strategy': bid_strategy,
        'status': status,
    }
    if bid_cap_usd is not None:
        params['bid_amount'] = int(bid_cap_usd * 100)

    adset = _get_client().ad_account.create_ad_set(params=params)
    return json.dumps({'id': adset['id'], 'name': name, 'bid_strategy': bid_strategy}, indent=2)


@mcp.tool()
def update_adset(
    adset_id: str,
    name: str = None,
    status: str = None,
    daily_budget_usd: float = None,
    bid_strategy: str = None,
    bid_cap_usd: float = None,
) -> str:
    """Update an ad set. Use this to set, change, or remove bid caps.

    To set a bid cap:
      bid_strategy="LOWEST_COST_WITH_BID_CAP", bid_cap_usd=2.00

    To remove a bid cap:
      bid_strategy="LOWEST_COST_WITHOUT_CAP"

    To use cost cap:
      bid_strategy="COST_CAP", bid_cap_usd=15.00
    """
    updates = {}
    if name:
        updates['name'] = name
    if status:
        updates['status'] = status
    if daily_budget_usd is not None:
        updates['daily_budget'] = int(daily_budget_usd * 100)
    if bid_strategy:
        updates['bid_strategy'] = bid_strategy
    if bid_cap_usd is not None:
        updates['bid_amount'] = int(bid_cap_usd * 100)

    _get_client().update_adset(adset_id, updates)
    return f"Ad set {adset_id} updated: {updates}"


@mcp.tool()
def pause_adset(adset_id: str) -> str:
    """Pause an ad set."""
    _get_client().pause_adset(adset_id)
    return f"Ad set {adset_id} paused."


@mcp.tool()
def activate_adset(adset_id: str) -> str:
    """Activate a paused ad set."""
    _get_client().activate_adset(adset_id)
    return f"Ad set {adset_id} activated."


# ── Ads ───────────────────────────────────────────────────────────────────────

@mcp.tool()
def list_ads(adset_id: str = None) -> str:
    """List ads. Optionally filter by adset_id."""
    fields = ['id', 'name', 'status', 'adset_id', 'creative', 'created_time', 'updated_time']
    ads = _get_client().get_ads(adset_id=adset_id, fields=fields)
    return json.dumps([dict(a) for a in ads], indent=2, default=str)


@mcp.tool()
def create_ad(adset_id: str, creative_id: str, name: str, status: str = "PAUSED") -> str:
    """Create an ad linking an ad set to a creative."""
    ad = _get_client().create_ad(adset_id=adset_id, creative_id=creative_id, name=name, status=status)
    return json.dumps({'id': ad['id'], 'name': name, 'status': status}, indent=2)


@mcp.tool()
def update_ad(ad_id: str, name: str = None, status: str = None) -> str:
    """Update an ad's name or status."""
    updates = {}
    if name:
        updates['name'] = name
    if status:
        updates['status'] = status
    _get_client().update_ad(ad_id, updates)
    return f"Ad {ad_id} updated: {updates}"


@mcp.tool()
def pause_ad(ad_id: str) -> str:
    """Pause an ad."""
    _get_client().pause_ad(ad_id)
    return f"Ad {ad_id} paused."


@mcp.tool()
def activate_ad(ad_id: str) -> str:
    """Activate an ad."""
    _get_client().activate_ad(ad_id)
    return f"Ad {ad_id} activated."


# ── Creatives ─────────────────────────────────────────────────────────────────

@mcp.tool()
def list_creatives() -> str:
    """List all ad creatives in the account."""
    fields = ['id', 'name', 'status', 'image_url', 'thumbnail_url', 'effective_object_story_id']
    creatives = _get_client().get_creatives(fields=fields)
    return json.dumps([dict(c) for c in creatives], indent=2, default=str)


@mcp.tool()
def create_image_creative(
    name: str,
    image_hash: str,
    message: str,
    link: str,
    headline: str = None,
    description: str = None,
    call_to_action: str = "LEARN_MORE",
) -> str:
    """Create an image ad creative.

    call_to_action options: LEARN_MORE, SHOP_NOW, SIGN_UP, GET_QUOTE,
                             SUBSCRIBE, DOWNLOAD, BOOK_TRAVEL, CONTACT_US
    image_hash: hash returned from upload_image
    """
    creative = _get_client().create_image_creative(
        name=name,
        image_hash=image_hash,
        message=message,
        link=link,
        headline=headline,
        description=description,
        call_to_action_type=call_to_action,
    )
    return json.dumps({'id': creative['id'], 'name': name}, indent=2)


@mcp.tool()
def get_ad_preview(creative_id: str, ad_format: str = "MOBILE_FEED_STANDARD") -> str:
    """Get an HTML preview of an ad creative.

    ad_format options: MOBILE_FEED_STANDARD, DESKTOP_FEED_STANDARD,
                       INSTAGRAM_STANDARD, RIGHT_COLUMN_STANDARD
    """
    html = _get_client().get_ad_preview(creative_id, ad_format=ad_format)
    return html or "No preview available."


# ── Optimization ──────────────────────────────────────────────────────────────

@mcp.tool()
def optimize_budgets(min_roas: float = None, dry_run: bool = True) -> str:
    """Review and rebalance budget allocation based on ROAS.
    Set dry_run=False to apply changes.
    """
    _, _, optimizer = _get_managers()
    changes = optimizer.optimize_budgets(min_roas=min_roas, dry_run=dry_run)
    prefix = "[DRY RUN] " if dry_run else "[APPLIED] "
    return prefix + json.dumps(changes, indent=2, default=str)


@mcp.tool()
def pause_underperformers(min_ctr: float = 0.5, min_spend: float = 100, dry_run: bool = True) -> str:
    """Find campaigns with CTR below min_ctr after spending min_spend USD.
    Set dry_run=False to pause them.
    """
    _, _, optimizer = _get_managers()
    result = optimizer.pause_underperformers(min_ctr=min_ctr, min_spend=min_spend, dry_run=dry_run)
    prefix = "[DRY RUN] " if dry_run else "[APPLIED] "
    return prefix + json.dumps(result, indent=2, default=str)


@mcp.tool()
def rebalance_portfolio(total_budget_usd: float, dry_run: bool = True) -> str:
    """Rebalance total daily budget across campaigns by performance.
    Set dry_run=False to apply.
    """
    _, _, optimizer = _get_managers()
    result = optimizer.rebalance_portfolio(total_budget=total_budget_usd, dry_run=dry_run)
    prefix = "[DRY RUN] " if dry_run else "[APPLIED] "
    return prefix + json.dumps(result, indent=2, default=str)


# ── Hormozi Framework Tools ───────────────────────────────────────────────────

@mcp.tool()
def get_angle_matrix() -> str:
    """Get the full 6-angle × 5-hook = 30 creative brief matrix for Stock Alarm.

    Returns all 30 creative briefs with angle arguments, hook formats,
    opening lines, body points, and pre-formatted ad set names for Meta
    Ads Manager. Use this to brief your creative team before filming.
    """
    from src.creative.hormozi_framework import StockAlarmAngleMatrix
    matrix = StockAlarmAngleMatrix()
    return json.dumps(matrix.to_dict(), indent=2)


@mcp.tool()
def get_angle_matrix_summary() -> str:
    """Print a human-readable summary of the 30-creative matrix.

    Shows each angle's core argument and the 5 hook formats under it.
    Easier to read than the full JSON — use for quick orientation.
    """
    from src.creative.hormozi_framework import StockAlarmAngleMatrix
    matrix = StockAlarmAngleMatrix()
    return matrix.summary()


@mcp.tool()
def get_gso_offer() -> str:
    """Get the Grand Slam Offer stack and Value Equation for Stock Alarm.

    Returns the full offer construction: offer components, Value Equation
    analysis, compliance notes for Meta financial ad policy, headline
    variants (40-char limit), and primary text variants (125-char limit).
    """
    from src.creative.hormozi_framework import GSOBuilder
    builder = GSOBuilder()
    return json.dumps({
        'summary': builder.summary(),
        'offer_stack': builder.get_offer_stack(),
        'headline_variants': builder.get_headline_variants(),
        'primary_text_variants': builder.get_primary_text_variants(),
        'cta_options': builder.get_cta_options(),
    }, indent=2)


@mcp.tool()
def create_testing_campaign(
    name: str,
    daily_budget_per_adset_usd: float,
    optimization_goal: str = "APP_INSTALLS",
    app_id: str = None,
    app_store_url: str = None,
    age_min: int = 25,
    age_max: int = 54,
) -> str:
    """Create a 30-ad-set ABO testing campaign (Phase 3 — Hormozi framework).

    Creates 1 campaign + 30 ad sets (one per creative brief) in parallel.
    All ad sets start PAUSED. Saves angle/hook mapping for performance tracking.

    After running this:
    1. Upload your 30 creative videos/images to Facebook
    2. Call add_creatives_to_testing_campaign() to wire them
    3. Run get_launch_checklist() before going live

    daily_budget_per_adset_usd: minimum = 5 × your target CPT
      (e.g. target CPT=$20 → use $100/day per ad set)
    optimization_goal: APP_INSTALLS (Phase 0-1) or OFFSITE_CONVERSIONS (Phase 2+)
    app_id / app_store_url: required for APP_INSTALLS campaigns
    """
    mgr, _, _ = _get_managers()
    promoted_object = None
    if app_id and app_store_url:
        promoted_object = {
            'application_id': app_id,
            'object_store_url': app_store_url,
        }
    result = mgr.create_hormozi_testing_campaign(
        name=name,
        daily_budget_per_adset_usd=daily_budget_per_adset_usd,
        optimization_goal=optimization_goal,
        promoted_object=promoted_object,
        age_min=age_min,
        age_max=age_max,
    )
    return json.dumps(result, indent=2, default=str)


@mcp.tool()
def add_creatives_to_campaign(
    campaign_id: str,
    creative_assignments_json: str,
) -> str:
    """Wire creative IDs to their ad sets and create the actual ads.

    Call after uploading your 30 creatives to Facebook.

    creative_assignments_json: JSON array of objects:
      [{"adset_id": "123", "creative_id": "456"}, ...]

    Get adset_ids from the result of create_testing_campaign().
    Get creative_ids from create_image_creative() or list_creatives().
    """
    mgr, _, _ = _get_managers()
    assignments = json.loads(creative_assignments_json)
    result = mgr.add_creatives_to_testing_campaign(campaign_id, assignments)
    return json.dumps(result, indent=2, default=str)


@mcp.tool()
def create_scaling_campaign(
    name: str,
    total_daily_budget_usd: float,
    winner_creative_ids_json: str,
    optimization_goal: str = "APP_INSTALLS",
    app_id: str = None,
    app_store_url: str = None,
) -> str:
    """Create a CBO scaling campaign for proven winner creatives (Phase 3).

    Uses one broad ad set — CBO allocates budget to best performers automatically.
    Run after identifying winners via get_creative_performance().

    winner_creative_ids_json: JSON array of creative IDs, e.g. ["111", "222", "333"]
    total_daily_budget_usd: Full campaign budget (CBO manages distribution)
    """
    mgr, _, _ = _get_managers()
    promoted_object = None
    if app_id and app_store_url:
        promoted_object = {'application_id': app_id, 'object_store_url': app_store_url}
    creative_ids = json.loads(winner_creative_ids_json)
    result = mgr.create_cbo_scaling_campaign(
        name=name,
        total_daily_budget_usd=total_daily_budget_usd,
        winner_creative_ids=creative_ids,
        optimization_goal=optimization_goal,
        promoted_object=promoted_object,
    )
    return json.dumps(result, indent=2, default=str)


@mcp.tool()
def get_launch_checklist(campaign_id: str, target_cpt_usd: float) -> str:
    """Phase 5 — Run the pre-launch checklist before activating 30 ad sets.

    Validates:
    - CAPI pixel configured
    - Financial Special Ad Category declared
    - Audience Network excluded
    - Budget ≥ 5× target CPT per ad set
    - Optimization event is a conversion (not clicks)
    - All ad sets have creatives wired

    Returns ready: true/false with specific actions needed.

    target_cpt_usd: your target cost-per-trial in USD
    """
    mgr, _, _ = _get_managers()
    result = mgr.get_launch_checklist(campaign_id, target_cpt_usd)
    return json.dumps(result, indent=2)


@mcp.tool()
def get_creative_performance(
    campaign_id: str,
    days: int = 7,
    target_cpt_usd: float = None,
) -> str:
    """Phase 4.3/6 — Pull ad-level creative performance with kill/winner verdicts.

    Metrics per creative: Hook Rate (stop-scroll %), Hold Rate (retention %),
    CTR, CPT (cost per trial), frequency, and verdict classification.

    Verdicts applied:
    - winner: CPT ≤ target AND Hook Rate ≥ 30%
    - kill: Hook Rate < 25%, OR 3× CPT spent with 0 conversions, OR CPT > 2× target by day 10
    - fatigued: frequency > 3.0 AND CTR degrading (needs creative refresh not replacement)
    - gray_zone: CPT within 30% of target — give 3 more days

    target_cpt_usd: your target cost-per-trial (required for kill/winner verdicts)
    """
    _, analytics, _ = _get_managers()
    result = analytics.get_creative_performance(
        campaign_id=campaign_id,
        days=days,
        target_cpt_usd=target_cpt_usd,
    )
    return json.dumps(result, indent=2, default=str)


@mcp.tool()
def weekly_creative_review(
    campaign_id: str,
    target_cpt_usd: float,
    dry_run: bool = True,
) -> str:
    """Phase 6 — Run the full Monday weekly review (60-minute process automated).

    Pulls creative performance, applies kill rules, pauses losers (if dry_run=False),
    identifies winners for CBO promotion, and generates next week's 70/20/10 brief.

    Always run with dry_run=True first to preview decisions before applying.

    Kill rules:
    - Hook Rate < 25% → kill
    - 3× target CPT spent with 0 conversions → kill
    - CPT > 2× target by day 10 → kill
    - Frequency > 3.0 + CTR < 0.5% → fatigued (refresh, not kill)
    """
    _, _, optimizer = _get_managers()
    result = optimizer.weekly_creative_review(
        campaign_id=campaign_id,
        target_cpt_usd=target_cpt_usd,
        dry_run=dry_run,
    )
    return json.dumps(result, indent=2, default=str)


@mcp.tool()
def check_scale_triggers(campaign_id: str, days: int = 7) -> str:
    """Phase 7 — Check whether you've hit the thresholds to deepen optimization.

    Returns your current stage and exact next action:

    Stage 0: < 50 installs/week — not enough volume
    Stage 1: 50+ installs but < 50 trials/week — keep on installs, test creatives
    Stage 2: 50-150 trials/week — switch to StartTrial optimization, scale CBO
    Stage 3: 150+ trials/week — test Activated Trial custom event
    Stage 4: 50+ subscribes/week — switch to Subscribe event + value-based bidding

    Meta needs 50 qualifying events/ad set/week to exit learning phase.
    """
    mgr, _, _ = _get_managers()
    result = mgr.check_scale_triggers(campaign_id=campaign_id, days=days)
    return json.dumps(result, indent=2, default=str)


if __name__ == "__main__":
    mcp.run()
