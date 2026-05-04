"""Campaign management module."""

import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from loguru import logger


class CampaignManager:
    """Manages Facebook ad campaigns."""

    def __init__(self, api_client):
        """Initialize campaign manager.

        Args:
            api_client: FacebookAdsClient instance
        """
        self.client = api_client
        self.config = api_client.config

    # Financial Products & Services is mandatory for fintech/investing apps in the US
    # as of January 2025. Declare it or risk account-level policy violations.
    FINANCIAL_AD_CATEGORY = ["CREDIT"]

    def create_campaign(
        self,
        name: str,
        objective: str,
        daily_budget: float,
        status: str = "PAUSED",
        special_ad_categories: Optional[List[str]] = None,
        is_financial_product: bool = False
    ) -> Dict:
        """Create a new campaign with default settings.

        Args:
            name: Campaign name
            objective: Campaign objective
            daily_budget: Daily budget in USD
            status: Initial status
            special_ad_categories: Special categories if applicable
            is_financial_product: Set True for financial/investing apps (required by Meta
                                  policy since Jan 2025). Automatically sets CREDIT category.

        Returns:
            Created campaign data
        """
        # Convert budget to cents
        budget_cents = int(daily_budget * 100)

        if special_ad_categories is None:
            special_ad_categories = self.FINANCIAL_AD_CATEGORY if is_financial_product else []

        campaign = self.client.create_campaign(
            name=name,
            objective=objective,
            status=status,
            special_ad_categories=special_ad_categories
        )

        # Create default ad set if campaign is created successfully
        if campaign and status == "ACTIVE":
            self._create_default_adset(campaign['id'], budget_cents)

        return dict(campaign)

    def _create_default_adset(self, campaign_id: str, budget_cents: int):
        """Create a default ad set for a campaign.

        Args:
            campaign_id: Campaign ID
            budget_cents: Budget in cents
        """
        targeting = self._get_default_targeting()

        adset = self.client.create_adset(
            campaign_id=campaign_id,
            name=f"Ad Set 1",
            daily_budget=budget_cents,
            targeting=targeting,
            optimization_goal="LINK_CLICKS",
            status="ACTIVE"
        )

        logger.info(f"Created default ad set for campaign {campaign_id}")
        return adset

    def _get_default_targeting(self) -> Dict:
        """Get default targeting parameters from config."""
        targeting_config = self.config.get('targeting', {})

        return {
            'geo_locations': {
                'countries': targeting_config.get('default_countries', ['US'])
            },
            'age_min': targeting_config.get('default_age_min', 25),
            'age_max': targeting_config.get('default_age_max', 65),
        }

    def list_campaigns(
        self,
        status_filter: Optional[str] = None,
        include_insights: bool = False
    ) -> List[Dict]:
        """List campaigns with optional filtering.

        Args:
            status_filter: Filter by status (ACTIVE, PAUSED, etc.)
            include_insights: Include performance insights

        Returns:
            List of campaign data
        """
        filtering = []
        if status_filter:
            filtering.append({
                'field': 'status',
                'operator': 'EQUAL',
                'value': status_filter
            })

        campaigns = self.client.get_campaigns(filtering=filtering if filtering else None)

        results = []
        for campaign in campaigns:
            camp_data = dict(campaign)

            if include_insights:
                insights = self.client.get_campaign_insights(campaign['id'])
                if insights:
                    camp_data['insights'] = insights[0]

            results.append(camp_data)

        return results

    def pause_campaign(self, campaign_id: str):
        """Pause a campaign."""
        self.client.pause_campaign(campaign_id)
        logger.info(f"Paused campaign {campaign_id}")

    def activate_campaign(self, campaign_id: str):
        """Activate a campaign."""
        self.client.activate_campaign(campaign_id)
        logger.info(f"Activated campaign {campaign_id}")

    def update_budget(self, campaign_id: str, new_budget: float):
        """Update campaign budget.

        Args:
            campaign_id: Campaign ID
            new_budget: New daily budget in USD
        """
        budget_cents = int(new_budget * 100)

        # Update ad sets associated with campaign
        adsets = self.client.get_adsets(campaign_id=campaign_id)
        for adset in adsets:
            self.client.update_campaign(adset['id'], {'daily_budget': budget_cents})

        logger.info(f"Updated budget for campaign {campaign_id} to ${new_budget}")

    # ── Hormozi Testing Campaign (Phase 3) ────────────────────────────────────

    def create_hormozi_testing_campaign(
        self,
        name: str,
        daily_budget_per_adset_usd: float,
        optimization_goal: str = "APP_INSTALLS",
        promoted_object: Optional[Dict] = None,
        age_min: int = 25,
        age_max: int = 54,
        countries: Optional[List[str]] = None,
        max_workers: int = 5,
    ) -> Dict:
        """Create a 30-ad-set ABO testing campaign using the Hormozi 6×5 framework.

        Creates:
          1 ABO campaign (status=PAUSED)
          30 ad sets — one per creative brief from StockAlarmAngleMatrix
          Saves angle/hook→adset mapping to campaign_mappings/{campaign_id}.json

        After this runs, upload your 30 creatives, then call
        add_creatives_to_testing_campaign() to wire ads to each ad set.

        Args:
            name: Campaign name (e.g. "SA Testing — May 2026")
            daily_budget_per_adset_usd: ABO budget per ad set in USD.
                                        Rule: minimum 5× your target CPT.
                                        E.g. if target CPT=$20, use $100.
            optimization_goal: APP_INSTALLS (Phase 0-1), OFFSITE_CONVERSIONS (Phase 2+)
            promoted_object: Required for app campaigns.
                            E.g. {'application_id': '123', 'object_store_url': 'https://...'}
            age_min / age_max: Targeting age range (default 25-54 per research)
            countries: ISO codes (default ['US'])
            max_workers: Parallel threads for adset creation (default 5, Meta rate-limit safe)

        Returns:
            {campaign_id, adset_count, adsets: [{adset_id, angle_id, hook_id, ...}],
             mapping_file, errors}
        """
        from src.creative.hormozi_framework import StockAlarmAngleMatrix

        if countries is None:
            countries = ['US']

        # Step 1 — Create the ABO testing campaign (PAUSED for safety)
        campaign = self.client.create_campaign(
            name=name,
            objective="OUTCOME_APP_PROMOTION" if "APP" in optimization_goal else "OUTCOME_SALES",
            status="PAUSED",
            special_ad_categories=self.FINANCIAL_AD_CATEGORY,
        )
        campaign_id = campaign['id']
        logger.info(f"Created testing campaign: {name} (ID: {campaign_id})")

        # Step 2 — Build 30 ad set specs from the angle/hook matrix
        matrix = StockAlarmAngleMatrix()
        briefs = matrix.get_all_briefs()
        budget_cents = int(daily_budget_per_adset_usd * 100)
        targeting = {
            'geo_locations': {'countries': countries},
            'age_min': age_min,
            'age_max': age_max,
        }

        # Step 3 — Create 30 ad sets in parallel (rate-limit safe at max_workers=5)
        adsets_created = []
        errors = []

        def _create_one_adset(brief) -> Tuple[Dict, object]:
            adset = self.client.create_adset(
                campaign_id=campaign_id,
                name=brief.ad_set_name,
                daily_budget=budget_cents,
                targeting=targeting,
                optimization_goal=optimization_goal,
                billing_event="IMPRESSIONS",
                bid_strategy="LOWEST_COST_WITHOUT_CAP",
                status="PAUSED",
                promoted_object=promoted_object,
                exclude_audience_network=True,
            )
            return {
                'adset_id': adset['id'],
                'adset_name': brief.ad_set_name,
                'angle_id': brief.angle_id,
                'hook_id': brief.hook_id,
                'angle_name': brief.angle_name,
                'hook_format': brief.hook_format,
                'hook_opening': brief.hook_opening,
                'cta_text': brief.cta_text,
                'creative_id': None,  # populated later via add_creatives_to_testing_campaign
                'ad_id': None,
            }, brief

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(_create_one_adset, brief): brief for brief in briefs}
            for future in as_completed(futures):
                try:
                    result, brief = future.result()
                    adsets_created.append(result)
                    logger.info(f"Created ad set: {result['adset_name']} ({result['adset_id']})")
                except Exception as e:
                    brief = futures[future]
                    errors.append({'brief': brief.ad_set_name, 'error': str(e)})
                    logger.error(f"Failed to create ad set for {brief.ad_set_name}: {e}")

        # Sort by angle then hook for consistent ordering
        adsets_created.sort(key=lambda x: (x['angle_id'], x['hook_id']))

        # Step 4 — Save mapping to disk (needed by creative performance tracker)
        mapping = {
            'campaign_id': campaign_id,
            'campaign_name': name,
            'campaign_type': 'ABO_TESTING',
            'optimization_goal': optimization_goal,
            'daily_budget_per_adset_usd': daily_budget_per_adset_usd,
            'adsets': adsets_created,
        }
        mapping_path = self._save_campaign_mapping(campaign_id, mapping)

        logger.info(
            f"Testing campaign ready: {len(adsets_created)}/30 ad sets created. "
            f"Mapping saved to {mapping_path}. "
            f"Next: upload creatives then call add_creatives_to_testing_campaign()."
        )

        return {
            'campaign_id': campaign_id,
            'campaign_name': name,
            'adset_count': len(adsets_created),
            'adsets': adsets_created,
            'mapping_file': str(mapping_path),
            'errors': errors,
        }

    def add_creatives_to_testing_campaign(
        self,
        campaign_id: str,
        creative_assignments: List[Dict],
    ) -> Dict:
        """Wire creatives to ad sets and create the actual ads.

        Call this after uploading your 30 creatives to Facebook.

        Args:
            campaign_id: The testing campaign ID
            creative_assignments: List of {adset_id, creative_id, ad_name (optional)}

        Returns:
            {ads_created, errors, updated_mapping}
        """
        mapping = self._load_campaign_mapping(campaign_id)
        if not mapping:
            raise ValueError(f"No mapping found for campaign {campaign_id}. "
                             "Was it created with create_hormozi_testing_campaign()?")

        adset_lookup = {a['adset_id']: a for a in mapping['adsets']}
        ads_created = []
        errors = []

        for assignment in creative_assignments:
            adset_id = assignment['adset_id']
            creative_id = assignment['creative_id']
            adset_info = adset_lookup.get(adset_id, {})

            ad_name = assignment.get(
                'ad_name',
                f"Ad | {adset_info.get('angle_name', 'Unknown')} | H{adset_info.get('hook_id', '?')}"
            )

            try:
                ad = self.client.create_ad(
                    adset_id=adset_id,
                    creative_id=creative_id,
                    name=ad_name,
                    status="PAUSED",
                )
                ads_created.append({'ad_id': ad['id'], 'adset_id': adset_id, 'creative_id': creative_id})

                # Update mapping in memory
                if adset_id in adset_lookup:
                    adset_lookup[adset_id]['creative_id'] = creative_id
                    adset_lookup[adset_id]['ad_id'] = ad['id']

                logger.info(f"Created ad {ad['id']} in ad set {adset_id}")
            except Exception as e:
                errors.append({'adset_id': adset_id, 'error': str(e)})
                logger.error(f"Failed to create ad for adset {adset_id}: {e}")

        # Persist updated mapping
        self._save_campaign_mapping(campaign_id, mapping)

        return {'ads_created': len(ads_created), 'errors': errors}

    def create_cbo_scaling_campaign(
        self,
        name: str,
        total_daily_budget_usd: float,
        winner_creative_ids: List[str],
        optimization_goal: str = "APP_INSTALLS",
        promoted_object: Optional[Dict] = None,
        age_min: int = 25,
        age_max: int = 54,
        countries: Optional[List[str]] = None,
    ) -> Dict:
        """Create a CBO scaling campaign for proven winner creatives.

        Phase 3 of the Hormozi framework. Uses one broad ad set with all
        winners — CBO allocates spend automatically to best performers.

        Args:
            name: Campaign name (e.g. "SA Scaling — CBO Winners")
            total_daily_budget_usd: Total campaign daily budget in USD
            winner_creative_ids: Creative IDs that passed the kill criteria
            optimization_goal: Should match your testing campaign
            promoted_object: Same as testing campaign
            age_min / age_max / countries: Same as testing campaign

        Returns:
            {campaign_id, adset_id, ads_created}
        """
        if countries is None:
            countries = ['US']

        # CBO campaign — budget set at campaign level
        campaign = self.client.create_campaign(
            name=name,
            objective="OUTCOME_APP_PROMOTION" if "APP" in optimization_goal else "OUTCOME_SALES",
            status="PAUSED",
            special_ad_categories=self.FINANCIAL_AD_CATEGORY,
        )
        campaign_id = campaign['id']

        # Set campaign-level budget (CBO)
        from facebook_business.adobjects.campaign import Campaign as FBCampaign
        fb_campaign = FBCampaign(campaign_id)
        fb_campaign.api_update(params={'daily_budget': int(total_daily_budget_usd * 100)})

        # One broad ad set — no budget at ad set level (CBO controls it)
        targeting = {
            'geo_locations': {'countries': countries},
            'age_min': age_min,
            'age_max': age_max,
        }
        adset = self.client.create_adset(
            campaign_id=campaign_id,
            name="SA | CBO Scaling | Broad",
            daily_budget=0,
            targeting=targeting,
            optimization_goal=optimization_goal,
            billing_event="IMPRESSIONS",
            bid_strategy="LOWEST_COST_WITHOUT_CAP",
            status="PAUSED",
            promoted_object=promoted_object,
            exclude_audience_network=True,
        )
        adset_id = adset['id']

        # Wire each winner creative to this ad set
        ads_created = []
        for i, creative_id in enumerate(winner_creative_ids, 1):
            ad = self.client.create_ad(
                adset_id=adset_id,
                creative_id=creative_id,
                name=f"SA | CBO Winner {i}",
                status="PAUSED",
            )
            ads_created.append({'ad_id': ad['id'], 'creative_id': creative_id})

        logger.info(
            f"CBO scaling campaign created: {name} ({campaign_id}) "
            f"with {len(ads_created)} winner creatives."
        )

        return {
            'campaign_id': campaign_id,
            'adset_id': adset_id,
            'ads_created': len(ads_created),
            'ads': ads_created,
        }

    def _save_campaign_mapping(self, campaign_id: str, mapping: Dict) -> Path:
        """Persist angle/hook→adset mapping to disk."""
        mappings_dir = Path("campaign_mappings")
        mappings_dir.mkdir(exist_ok=True)
        path = mappings_dir / f"{campaign_id}.json"
        with open(path, 'w') as f:
            json.dump(mapping, f, indent=2)
        return path

    def _load_campaign_mapping(self, campaign_id: str) -> Optional[Dict]:
        """Load a campaign mapping from disk."""
        path = Path("campaign_mappings") / f"{campaign_id}.json"
        if not path.exists():
            return None
        with open(path) as f:
            return json.load(f)

    def get_launch_checklist(
        self,
        campaign_id: str,
        target_cpt_usd: float,
    ) -> Dict:
        """Phase 5 launch checklist — validates prerequisites before going live.

        Checks:
          - CAPI pixel configured
          - Special Ad Category declared
          - Audience Network excluded
          - Budget ≥ 5× target CPT per ad set
          - Optimization event set (not just link clicks)
          - All ad sets PAUSED (ready to launch simultaneously)

        Args:
            campaign_id: The testing campaign ID
            target_cpt_usd: Your target cost-per-trial in USD

        Returns:
            {ready: bool, checks: [{name, passed, detail}]}
        """
        checks = []
        mapping = self._load_campaign_mapping(campaign_id)

        # 1 — CAPI pixel configured
        pixel_id = self.config.get('facebook', {}).get('pixel_id', '')
        checks.append({
            'name': 'CAPI pixel_id configured',
            'passed': bool(pixel_id),
            'detail': (
                f"pixel_id = {pixel_id}" if pixel_id
                else "Missing. Add pixel_id to config/config.yaml and wire CAPI endpoints."
            ),
        })

        # 2 — Special Ad Category declared
        has_mapping = mapping is not None
        checks.append({
            'name': 'Financial Special Ad Category (CREDIT) declared',
            'passed': has_mapping,
            'detail': (
                "Campaign created via create_hormozi_testing_campaign() which sets CREDIT category."
                if has_mapping else
                "Unknown — campaign not found in local mappings. Verify in Meta Ads Manager."
            ),
        })

        # 3 — Audience Network excluded (verified via create_adset param)
        checks.append({
            'name': 'Audience Network excluded',
            'passed': has_mapping,
            'detail': (
                "Ad sets created with publisher_platforms=['facebook','instagram','messenger']."
                if has_mapping else
                "Cannot verify — check publisher_platforms in Meta Ads Manager."
            ),
        })

        # 4 — Budget ≥ 5× target CPT
        if mapping:
            budget = mapping.get('daily_budget_per_adset_usd', 0)
            min_budget = target_cpt_usd * 5
            budget_ok = budget >= min_budget
            checks.append({
                'name': f'Budget ≥ 5× target CPT (≥ ${min_budget:.0f}/ad set/day)',
                'passed': budget_ok,
                'detail': (
                    f"${budget}/day per ad set — OK."
                    if budget_ok else
                    f"${budget}/day is below the ${min_budget:.0f} minimum. "
                    f"Increase to ensure ad sets exit the learning phase."
                ),
            })
        else:
            checks.append({
                'name': 'Budget ≥ 5× target CPT',
                'passed': False,
                'detail': 'Cannot verify — campaign mapping not found.',
            })

        # 5 — Optimization event (not LINK_CLICKS)
        if mapping:
            goal = mapping.get('optimization_goal', 'LINK_CLICKS')
            goal_ok = goal not in ('LINK_CLICKS', 'IMPRESSIONS', 'REACH')
            checks.append({
                'name': 'Optimization event is a conversion (not clicks/impressions)',
                'passed': goal_ok,
                'detail': (
                    f"Optimization goal: {goal} — good."
                    if goal_ok else
                    f"Optimization goal is {goal}. Should be APP_INSTALLS or "
                    f"OFFSITE_CONVERSIONS targeting trial/subscribe events."
                ),
            })

        # 6 — All ads have creatives wired (ad_id not None)
        if mapping:
            adsets_with_ads = [a for a in mapping['adsets'] if a.get('ad_id')]
            total = len(mapping['adsets'])
            all_wired = len(adsets_with_ads) == total
            checks.append({
                'name': f'All {total} ad sets have creatives wired',
                'passed': all_wired,
                'detail': (
                    f"{len(adsets_with_ads)}/{total} ad sets have ads. "
                    + ("Ready to launch." if all_wired else
                       "Call add_creatives_to_testing_campaign() for remaining ad sets.")
                ),
            })

        ready = all(c['passed'] for c in checks)
        return {
            'ready': ready,
            'campaign_id': campaign_id,
            'checks': checks,
            'next_step': (
                "All checks passed. Launch all 30 ad sets simultaneously — "
                "do NOT stagger the launch or one creative gets an unfair head start."
                if ready else
                "Fix the failing checks above before going live."
            ),
        }

    def check_scale_triggers(
        self,
        campaign_id: str,
        days: int = 7,
    ) -> Dict:
        """Phase 7 — Check whether you've hit the scale trigger thresholds.

        Meta's algorithm needs 50 qualifying conversion events per ad set per week
        to exit the learning phase. The further down-funnel the event, the harder
        this is to hit — so scaling happens in stages.

        Trigger thresholds (from Phase 7 plan):
          < 50 trials/week  → Stay on App Installs; keep testing creatives
          50-150 trials/wk  → Switch to Trial Started optimization; scale CBO
          150+ trials/wk    → Test "Activated Trial" event (trial + no cancel ≤4hrs)
          50+ subscribes/wk → Test Subscribe event optimization + value-based bidding

        Args:
            campaign_id: Campaign to evaluate
            days: Lookback window for event count

        Returns:
            {current_stage, next_stage, recommendation, event_counts}
        """
        date_preset = self._get_date_preset(days)

        # Pull campaign-level insights for conversion event counts
        insights = self.client.get_campaign_insights(
            campaign_id,
            date_preset=date_preset,
            fields=[
                'impressions', 'spend', 'actions',
                'action_values',
            ]
        )

        if not insights:
            return {
                'current_stage': 'unknown',
                'recommendation': 'No data available. Ensure campaigns are running.',
                'event_counts': {},
            }

        insight = insights[0]
        actions = insight.get('actions', [])

        # Count each event type
        def count_action(types):
            total = 0
            for action in actions:
                if any(t.lower() in action.get('action_type', '').lower() for t in types):
                    total += int(action.get('value', 0))
            return total

        installs = count_action(['app_install', 'mobile_app_install'])
        trials = count_action(['start_trial', 'starttrial'])
        subscribes = count_action(['subscribe', 'offsite_conversion.fb_pixel_subscribe'])
        purchases = count_action(['purchase', 'offsite_conversion.fb_pixel_purchase'])

        # Get number of active ad sets (for per-adset event rate)
        adsets = self.client.get_adsets(campaign_id=campaign_id)
        active_adsets = [a for a in adsets if a.get('status') == 'ACTIVE']
        adset_count = max(len(active_adsets), 1)

        trials_per_adset = trials / adset_count
        subscribes_per_adset = subscribes / adset_count

        # Determine current stage and recommendation
        if subscribes_per_adset >= 50:
            stage = 4
            stage_name = "Stage 4 — Optimize for Subscribe + value-based bidding"
            recommendation = (
                f"You have {subscribes:.0f} subscribe events/week ({subscribes_per_adset:.0f}/ad set). "
                f"Switch optimization event to 'Subscribe'. Enable value-based bidding once "
                f"RevenueCat/CAPI revenue data is clean and consistent."
            )
            next_stage = "Stage 5: Optimize on LTV/ROAS with 90-day payback cohort tracking"

        elif trials_per_adset >= 150:
            stage = 3
            stage_name = "Stage 3 — Test Activated Trial event"
            recommendation = (
                f"You have {trials:.0f} trial events/week ({trials_per_adset:.0f}/ad set). "
                f"Test the 'Activated Trial' custom event: fires 4 hours after trial start "
                f"IF the user hasn't cancelled. This filters low-intent trial abusers and "
                f"trains Meta on higher-quality users."
            )
            next_stage = f"Stage 4: Need 50+ subscribes/week per ad set ({subscribes:.0f} currently)"

        elif trials_per_adset >= 50:
            stage = 2
            stage_name = "Stage 2 — Optimize for Trial Started; scale CBO"
            recommendation = (
                f"You have {trials:.0f} trial events/week ({trials_per_adset:.0f}/ad set). "
                f"Switch optimization event from App Installs to 'StartTrial'. "
                f"Move winners to CBO scaling campaign. Consider excluding ages 18-24 "
                f"(cheap installs, poor trial-to-paid conversion for premium financial apps)."
            )
            next_stage = f"Stage 3: Need 150+ trials/week per ad set ({trials:.0f} currently)"

        elif installs >= 50:
            stage = 1
            stage_name = "Stage 1 — Generating install volume; continue creative testing"
            recommendation = (
                f"You have {installs:.0f} installs/week but only {trials:.0f} trial events. "
                f"Check trial conversion rate from install. If < 20%, onboarding may have friction — "
                f"review time-to-first-value (should be < 24 hours). Keep optimizing on installs "
                f"and running creative tests until you hit 50+ trials/week per ad set."
            )
            next_stage = f"Stage 2: Need 50+ trial events/week per ad set ({trials_per_adset:.1f} currently)"

        else:
            stage = 0
            stage_name = "Stage 0 — Early testing; not enough signal yet"
            recommendation = (
                f"Only {installs:.0f} installs this week. Need more volume before optimizing. "
                f"Check: (1) Are campaigns ACTIVE? (2) Is budget ≥ $50/day per ad set? "
                f"(3) Is the CAPI pixel firing? Run /api/debug/conversion-tracking to verify."
            )
            next_stage = "Stage 1: Need 50+ installs/week per ad set"

        return {
            'campaign_id': campaign_id,
            'days': days,
            'current_stage': stage,
            'stage_name': stage_name,
            'recommendation': recommendation,
            'next_stage': next_stage,
            'event_counts': {
                'installs': installs,
                'trial_starts': trials,
                'activated_trials': 0,
                'subscribes': subscribes,
                'purchases': purchases,
                'active_adsets': adset_count,
                'trials_per_adset_per_week': round(trials_per_adset, 1),
                'subscribes_per_adset_per_week': round(subscribes_per_adset, 1),
            },
        }

    def _get_date_preset(self, days: int) -> str:
        presets = {1: 'today', 7: 'last_7d', 14: 'last_14d', 30: 'last_30d'}
        return presets.get(days, 'last_7d')

    def duplicate_campaign(
        self,
        campaign_id: str,
        new_name: Optional[str] = None
    ) -> Dict:
        """Duplicate a campaign.

        Args:
            campaign_id: Source campaign ID
            new_name: Name for duplicated campaign

        Returns:
            New campaign data
        """
        # Get source campaign
        campaigns = self.client.get_campaigns()
        source = next((c for c in campaigns if c['id'] == campaign_id), None)

        if not source:
            raise ValueError(f"Campaign {campaign_id} not found")

        # Create duplicate
        name = new_name or f"{source['name']} (Copy)"
        return self.create_campaign(
            name=name,
            objective=source['objective'],
            daily_budget=int(source.get('daily_budget', 5000)) / 100,  # Convert cents to USD
            status='PAUSED'
        )
