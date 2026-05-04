"""Budget optimization module."""

from datetime import datetime
from typing import Dict, List, Optional
from loguru import logger


class BudgetOptimizer:
    """Optimizes budget allocation across campaigns."""

    def __init__(self, api_client):
        """Initialize budget optimizer.

        Args:
            api_client: FacebookAdsClient instance
        """
        self.client = api_client
        self.config = api_client.config

    def optimize_budgets(
        self,
        min_roas: Optional[float] = None,
        dry_run: bool = True
    ) -> List[Dict]:
        """Optimize budget allocation based on performance.

        Args:
            min_roas: Minimum ROAS threshold
            dry_run: Preview changes without applying

        Returns:
            List of budget changes
        """
        min_roas = min_roas or self.config.get('optimization', {}).get('min_roas', 1.5)

        # Get all active campaigns with insights
        campaigns = self.client.get_campaigns(filtering=[{
            'field': 'status',
            'operator': 'EQUAL',
            'value': 'ACTIVE'
        }])

        changes = []

        for campaign in campaigns:
            # Get performance data
            insights = self.client.get_campaign_insights(
                campaign['id'],
                date_preset='last_7d'
            )

            if not insights or not insights[0]:
                continue

            insight = insights[0]
            current_budget = int(campaign.get('daily_budget', 0)) / 100  # Convert cents to USD

            # Calculate ROAS
            spend = float(insight.get('spend', 0))
            conversions = self._extract_conversions(insight)
            revenue = conversions * self.config.get('analytics', {}).get('avg_order_value', 50)
            roas = (revenue / spend) if spend > 0 else 0

            # Determine budget change
            new_budget = self._calculate_optimal_budget(
                current_budget,
                roas,
                min_roas,
                spend
            )

            if new_budget != current_budget:
                change_pct = ((new_budget - current_budget) / current_budget) * 100

                change = {
                    'campaign_id': campaign['id'],
                    'campaign_name': campaign['name'],
                    'old_budget': current_budget,
                    'new_budget': new_budget,
                    'change_pct': change_pct,
                    'roas': roas,
                    'reason': self._get_change_reason(roas, min_roas, change_pct)
                }

                changes.append(change)

                # Apply change if not dry run
                if not dry_run:
                    self._update_campaign_budget(campaign['id'], new_budget)
                    logger.info(f"Updated budget for {campaign['name']}: ${current_budget} → ${new_budget}")

        return changes

    def _calculate_optimal_budget(
        self,
        current_budget: float,
        roas: float,
        min_roas: float,
        spend: float
    ) -> float:
        """Calculate optimal budget based on performance.

        Args:
            current_budget: Current daily budget
            roas: Current ROAS
            min_roas: Minimum acceptable ROAS
            spend: Total spend in period

        Returns:
            Optimal budget
        """
        min_budget = self.config.get('campaigns', {}).get('min_daily_budget', 10)
        max_budget = self.config.get('campaigns', {}).get('max_daily_budget', 5000)

        # High performers - increase budget
        if roas >= min_roas * 1.5:
            new_budget = current_budget * 1.2  # Increase by 20%
        # Good performers - slight increase
        elif roas >= min_roas * 1.2:
            new_budget = current_budget * 1.1  # Increase by 10%
        # Meeting threshold - maintain
        elif roas >= min_roas:
            new_budget = current_budget
        # Below threshold but close - slight decrease
        elif roas >= min_roas * 0.8:
            new_budget = current_budget * 0.9  # Decrease by 10%
        # Poor performers - significant decrease
        else:
            new_budget = current_budget * 0.7  # Decrease by 30%

        # Enforce limits
        new_budget = max(min_budget, min(max_budget, new_budget))

        # Round to nearest $5
        new_budget = round(new_budget / 5) * 5

        return new_budget

    def _get_change_reason(self, roas: float, min_roas: float, change_pct: float) -> str:
        """Get human-readable reason for budget change.

        Args:
            roas: Current ROAS
            min_roas: Minimum ROAS threshold
            change_pct: Percentage change

        Returns:
            Reason string
        """
        if change_pct > 0:
            if roas >= min_roas * 1.5:
                return f"High ROAS ({roas:.2f}x) - scaling up"
            elif roas >= min_roas:
                return f"Good ROAS ({roas:.2f}x) - increasing budget"
        else:
            if roas < min_roas:
                return f"Low ROAS ({roas:.2f}x) - reducing budget"
            else:
                return f"Below threshold ({roas:.2f}x < {min_roas:.2f}x)"

        return "Budget optimization"

    def pause_underperformers(
        self,
        min_ctr: float = 0.5,
        min_spend: float = 100,
        dry_run: bool = True
    ) -> List[Dict]:
        """Pause campaigns that are underperforming.

        Args:
            min_ctr: Minimum CTR threshold (%)
            min_spend: Minimum spend to evaluate
            dry_run: Preview without pausing

        Returns:
            List of paused campaigns
        """
        campaigns = self.client.get_campaigns(filtering=[{
            'field': 'status',
            'operator': 'EQUAL',
            'value': 'ACTIVE'
        }])

        paused = []

        for campaign in campaigns:
            insights = self.client.get_campaign_insights(
                campaign['id'],
                date_preset='last_7d'
            )

            if not insights:
                continue

            insight = insights[0]
            spend = float(insight.get('spend', 0))

            # Skip if not enough spend
            if spend < min_spend:
                continue

            # Calculate CTR
            impressions = int(insight.get('impressions', 0))
            clicks = int(insight.get('clicks', 0))
            ctr = (clicks / impressions * 100) if impressions > 0 else 0

            # Check if underperforming
            if ctr < min_ctr:
                paused.append({
                    'campaign_id': campaign['id'],
                    'campaign_name': campaign['name'],
                    'ctr': ctr,
                    'spend': spend,
                    'reason': f"CTR ({ctr:.2f}%) below threshold ({min_ctr}%)"
                })

                if not dry_run:
                    self.client.pause_campaign(campaign['id'])
                    logger.warning(f"Paused underperforming campaign: {campaign['name']}")

        return paused

    def _update_campaign_budget(self, campaign_id: str, new_budget: float):
        """Update campaign budget through ad sets.

        Args:
            campaign_id: Campaign ID
            new_budget: New budget in USD
        """
        budget_cents = int(new_budget * 100)

        # Get ad sets for campaign
        adsets = self.client.get_adsets(campaign_id=campaign_id)

        # Update each ad set
        for adset in adsets:
            from facebook_business.adobjects.adset import AdSet
            ad_set = AdSet(adset['id'])
            ad_set.api_update(params={'daily_budget': budget_cents})

    def _extract_conversions(self, insight: Dict) -> int:
        """Extract conversion count from insights.

        Args:
            insight: Insights data

        Returns:
            Number of conversions
        """
        if 'actions' not in insight:
            return 0

        for action in insight['actions']:
            action_type = action.get('action_type', '').lower()
            if 'purchase' in action_type or 'conversion' in action_type:
                return int(action.get('value', 0))

        return 0

    # ── Hormozi Weekly Review System (Phase 4.4 + 4.5) ───────────────────────

    def weekly_creative_review(
        self,
        campaign_id: str,
        target_cpt_usd: float,
        days: int = 7,
        dry_run: bool = True,
    ) -> Dict:
        """Phase 6 weekly review: apply kill rules, classify, output decisions.

        Runs every Monday. Takes 60 minutes operationally:
          Step 1 (15 min) — Pull numbers via AnalyticsReporter.get_creative_performance()
          Step 2 (15 min) — Classify: winner / gray_zone / kill / fatigued
          Step 3 (15 min) — Make decisions: pause kills, flag winners for CBO
          Step 4 (15 min) — Output 70/20/10 creative brief for next week

        Kill rules applied:
          - Hook Rate < 25%: kill (scroll failure)
          - Spend ≥ 3× target_cpt with 0 conversions: kill (structural)
          - CPT > 2× target by day 10: kill (performance)
          - Frequency > 3.0 AND CTR < 0.5%: fatigued (refresh, not kill)
          - CPT ≤ target AND Hook Rate ≥ 30%: winner (promote to CBO)

        Budget rule: Never increase by more than 30% at once (larger jumps
        restart the Meta learning phase).

        Args:
            campaign_id: The ABO testing campaign
            target_cpt_usd: Your target cost-per-trial in USD
            days: Lookback window (7 for weekly review)
            dry_run: Preview decisions without pausing ads

        Returns:
            Full review dict with kill/keep/scale/brief lists and actions taken
        """
        from src.analytics.reporter import AnalyticsReporter

        reporter = AnalyticsReporter(self.client)
        perf = reporter.get_creative_performance(
            campaign_id=campaign_id,
            days=days,
            target_cpt_usd=target_cpt_usd,
        )

        winners = perf['winners']
        kills = perf['kills']
        gray_zone = perf['gray_zone']
        fatigued = perf['fatigued']
        all_ads = perf['ads']

        actions_taken = []

        # Execute kills
        for ad in kills:
            if not dry_run:
                try:
                    self.client.pause_adset(ad['adset_id'])
                    actions_taken.append({
                        'action': 'paused',
                        'adset_id': ad['adset_id'],
                        'reason': f"Kill rule: CPT ${ad['cpt']} | Hook {ad['hook_rate_pct']}%",
                    })
                    logger.warning(f"Killed ad set {ad['adset_id']} ({ad['angle_name']} H{ad['hook_id']})")
                except Exception as e:
                    logger.error(f"Failed to pause ad set {ad['adset_id']}: {e}")
            else:
                actions_taken.append({
                    'action': 'would_pause',
                    'adset_id': ad['adset_id'],
                    'reason': f"Kill rule: CPT ${ad['cpt']} | Hook {ad['hook_rate_pct']}%",
                })

        # Flag winners for CBO (don't touch budget on testing campaign — move to CBO instead)
        winner_creative_ids = [a.get('creative_id') for a in winners if a.get('creative_id')]

        # Generate next week's brief
        brief = self.generate_creative_brief(winners, fatigued)

        mode = "[DRY RUN]" if dry_run else "[APPLIED]"
        logger.info(
            f"{mode} Weekly review: {len(winners)} winners, {len(kills)} killed, "
            f"{len(gray_zone)} gray zone, {len(fatigued)} fatigued."
        )

        return {
            'campaign_id': campaign_id,
            'review_date': datetime.now().isoformat() if True else None,
            'dry_run': dry_run,
            'target_cpt_usd': target_cpt_usd,
            'summary': perf['summary'],
            'winners': winners,
            'kills': kills,
            'gray_zone': gray_zone,
            'fatigued': fatigued,
            'winner_creative_ids': winner_creative_ids,
            'actions_taken': actions_taken,
            'next_week_brief': brief,
            'next_steps': [
                f"Move {len(winners)} winner creative(s) to CBO scaling campaign",
                f"Pause {len(kills)} ad sets" if dry_run else f"Paused {len(kills)} ad sets",
                f"Give {len(gray_zone)} gray-zone ads 3 more days before re-evaluating",
                f"Queue {len(fatigued)} fatigued creatives for refresh (minor variations)",
                "Review the next_week_brief and brief your creative team",
            ],
        }

    def generate_creative_brief(
        self,
        winners: List[Dict],
        fatigued: Optional[List[Dict]] = None,
    ) -> Dict:
        """Phase 4.5 — Generate the 70/20/10 creative production brief.

        Takes this week's winners and outputs structured briefs for next week:
          70% — Minor variations of top 2 winners (safe scaling)
          20% — Substantial variations (new hook, different creator)
          10% — New angle discovery (3 new hooks on an untested angle)

        Minor variations (70% bucket):
          - Different presenter / creator (swap the face)
          - Color filter / grade change
          - Horizontal flip of video
          - Swap b-roll cutaways
          - Slight copy tweak (same argument, one different word in hook)
          Note: Andromeda penalizes cosmetic-only changes — need ≥2 elements different.

        Substantial variations (20% bucket):
          - New hook bolted onto the winning angle
          - Different creator presenting the SAME argument
          - New setting/environment for same concept
          - Different edit style (talking head → narrated b-roll)

        New discovery (10% bucket):
          - 1 untested angle
          - 3 hooks on that angle

        Args:
            winners: Winner list from weekly_creative_review()
            fatigued: Fatigued list (needs creative refresh, not new concepts)

        Returns:
            Structured brief with 70/20/10 buckets
        """
        fatigued = fatigued or []
        top_winners = sorted(winners, key=lambda x: x.get('cpt') or 999)[:2]

        # 70% bucket — minor variations of top 2
        bucket_70 = []
        for winner in top_winners:
            angle_name = winner.get('angle_name', 'Unknown')
            hook_format = winner.get('hook_format', 'Unknown')
            hook_opening = winner.get('hook_opening', '')
            bucket_70.append({
                'source_ad_id': winner['ad_id'],
                'source_angle': angle_name,
                'source_hook': hook_opening[:80],
                'cpt': winner.get('cpt'),
                'hook_rate_pct': winner.get('hook_rate_pct'),
                'variations_to_produce': [
                    {
                        'variation': 'Different presenter/creator',
                        'instruction': f"Same script and angle as '{angle_name}' but swap the on-camera talent",
                        'andromeda_signal_change': 'face/talent',
                    },
                    {
                        'variation': 'Color grade + b-roll swap',
                        'instruction': f"Re-edit the '{hook_format}' version with different b-roll cutaways and warm color grade",
                        'andromeda_signal_change': 'visual_style + b-roll',
                    },
                    {
                        'variation': 'Horizontal flip + copy micro-tweak',
                        'instruction': f"Mirror-flip the video, change first word of hook: '{hook_opening[:40]}...'",
                        'andromeda_signal_change': 'orientation + copy',
                    },
                ],
            })

        # 20% bucket — substantial variations of winners
        bucket_20 = []
        for winner in top_winners:
            angle_name = winner.get('angle_name', 'Unknown')
            hook_opening = winner.get('hook_opening', '')
            bucket_20.append({
                'source_ad_id': winner['ad_id'],
                'source_angle': angle_name,
                'variations_to_produce': [
                    {
                        'variation': 'New hook, same angle body',
                        'instruction': (
                            f"Keep the '{angle_name}' argument and CTA unchanged. "
                            f"Write a completely different opening hook (current: '{hook_opening[:50]}...'). "
                            f"Try opposite format — if current is talking head, try silent text overlay."
                        ),
                        'andromeda_signal_change': 'hook + format',
                    },
                    {
                        'variation': 'Different creator, same script',
                        'instruction': (
                            f"Different creator/presenter delivers the exact same '{angle_name}' "
                            f"script word-for-word. Different face = different audience signal to Andromeda."
                        ),
                        'andromeda_signal_change': 'talent',
                    },
                ],
            })

        # Add fatigued creatives to 20% bucket — they need refresh, not replacement
        for fatigued_ad in fatigued[:2]:
            bucket_20.append({
                'source_ad_id': fatigued_ad['ad_id'],
                'source_angle': fatigued_ad.get('angle_name', 'Unknown'),
                'type': 'fatigue_refresh',
                'variations_to_produce': [
                    {
                        'variation': 'Fatigue refresh — new hook only',
                        'instruction': (
                            f"The '{fatigued_ad.get('angle_name')}' angle worked (frequency "
                            f"{fatigued_ad.get('frequency')} shows saturation). "
                            f"Keep the body/CTA, write 2 completely new hooks for it."
                        ),
                        'andromeda_signal_change': 'hook',
                    },
                ],
            })

        # 10% bucket — new angle discovery
        from src.creative.hormozi_framework import StockAlarmAngleMatrix, ANGLES
        matrix = StockAlarmAngleMatrix()
        used_angles = {w.get('angle_id') for w in winners + fatigued if w.get('angle_id')}
        untested_angles = [a for a in ANGLES if a['id'] not in used_angles]

        bucket_10 = []
        if untested_angles:
            new_angle = untested_angles[0]
            bucket_10.append({
                'angle_to_test': new_angle['name'],
                'angle_argument': new_angle['core_argument'],
                'hooks_to_produce': [
                    f"Hook A [talking_head]: Direct delivery of '{new_angle['name']}' argument",
                    f"Hook B [text_overlay]: Bold text treatment of the core claim",
                    f"Hook C [ugc]: Authentic creator story from '{new_angle['name']}' angle",
                ],
                'instruction': (
                    f"Produce 3 hooks on the '{new_angle['name']}' angle. "
                    f"Core argument: {new_angle['core_argument'][:100]}..."
                ),
            })
        else:
            bucket_10.append({
                'instruction': (
                    "All 6 angles have been tested. For 10% bucket this week: "
                    "test a new creative format (carousel or 15-second cut-down) "
                    "using your best-performing angle."
                ),
            })

        total_new_ads = (
            sum(len(b['variations_to_produce']) for b in bucket_70) +
            sum(len(b['variations_to_produce']) for b in bucket_20) +
            3  # 10% bucket always produces ~3
        )

        return {
            'week': datetime.now().strftime('%Y-W%W'),
            'total_new_ads_to_produce': total_new_ads,
            'budget_allocation': {
                '70_pct': 'Proven winners — minor variations for safe scaling',
                '20_pct': 'Substantial variations + fatigue refreshes',
                '10_pct': 'New angle discovery — expect most to fail',
            },
            'bucket_70_minor_variations': bucket_70,
            'bucket_20_substantial_variations': bucket_20,
            'bucket_10_new_discovery': bucket_10,
            'production_reminder': (
                "Andromeda requires genuine creative diversity — each variation must differ "
                "on ≥2 elements (talent, hook, format, visual style). Pure cosmetic re-skins "
                "are treated as the same creative and compete for the same auction slot."
            ),
        }

    def rebalance_portfolio(self, total_budget: float, dry_run: bool = True) -> List[Dict]:
        """Rebalance budget across all campaigns to maximize ROI.

        Args:
            total_budget: Total budget to allocate
            dry_run: Preview without applying

        Returns:
            List of allocations
        """
        # Get all active campaigns with performance data
        campaigns = self.client.get_campaigns(filtering=[{
            'field': 'status',
            'operator': 'EQUAL',
            'value': 'ACTIVE'
        }])

        # Calculate performance scores
        scored_campaigns = []
        for campaign in campaigns:
            insights = self.client.get_campaign_insights(campaign['id'], date_preset='last_7d')
            if not insights:
                continue

            insight = insights[0]
            spend = float(insight.get('spend', 0))
            conversions = self._extract_conversions(insight)
            revenue = conversions * self.config.get('analytics', {}).get('avg_order_value', 50)
            roas = (revenue / spend) if spend > 0 else 0

            scored_campaigns.append({
                'campaign': campaign,
                'roas': roas,
                'current_budget': int(campaign.get('daily_budget', 0)) / 100
            })

        # Sort by ROAS
        scored_campaigns.sort(key=lambda x: x['roas'], reverse=True)

        # Allocate budget proportional to ROAS
        total_roas = sum(c['roas'] for c in scored_campaigns if c['roas'] > 0)

        allocations = []
        for item in scored_campaigns:
            if item['roas'] <= 0:
                new_budget = 0
            else:
                proportion = item['roas'] / total_roas
                new_budget = total_budget * proportion

            allocations.append({
                'campaign_id': item['campaign']['id'],
                'campaign_name': item['campaign']['name'],
                'old_budget': item['current_budget'],
                'new_budget': new_budget,
                'roas': item['roas']
            })

            if not dry_run:
                self._update_campaign_budget(item['campaign']['id'], new_budget)

        return allocations
