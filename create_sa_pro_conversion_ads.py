#!/usr/bin/env python3
"""
Create SA Pro conversion ads with tight active-trader targeting.

Strategy: Start with one highly-targeted ad set (Feed only, 28–55, trading interests)
inside the existing active campaign. Ad created PAUSED for review before activating.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.api_client import FacebookAdsClient
from src.creative.image_generator import create_image_generator_from_config
from facebook_business.adobjects.targetingsearch import TargetingSearch
from rich.console import Console
from rich.table import Table

console = Console()

CAMPAIGN_ID = "52509592895634"   # SA Pro - Active Traders - Conversions v2
PIXEL_ID    = "758105866947534"
DEST_URL    = "https://pro.stockalarm.io"


def search_interest(query: str):
    """Return the top Facebook interest match for a search query."""
    try:
        results = TargetingSearch.search(params={
            'q': query,
            'type': 'adinterest',
            'limit': 3,
        })
        if results:
            return {'id': results[0]['id'], 'name': results[0]['name']}
    except Exception as e:
        console.print(f"  [red]✗ Search error for '{query}': {e}[/red]")
    return None


def main():
    console.print("\n[bold cyan]SA Pro — Creating Tight Conversion Ad[/bold cyan]\n")

    client = FacebookAdsClient()

    # ── Step 1: Validate interest IDs via live search ─────────────────────────
    console.print("[yellow]Step 1: Searching for trading interest IDs...[/yellow]")

    interest_queries = [
        "Day trading",
        "Options trading",
        "Stock market",
        "Technical analysis",
        "Webull",
        "thinkorswim",
        "Swing trading",
        "Stock screening",
    ]

    validated_interests = []
    for q in interest_queries:
        result = search_interest(q)
        if result:
            validated_interests.append(result)
            console.print(f"  ✓  {result['name']}  (ID: {result['id']})")
        else:
            console.print(f"  ✗  No match for '{q}'")

    if not validated_interests:
        console.print("[red]No interests found — aborting.[/red]")
        sys.exit(1)

    # ── Step 2: Build targeting spec ──────────────────────────────────────────
    console.print("\n[yellow]Step 2: Building targeting spec...[/yellow]")

    targeting_spec = {
        'geo_locations': {
            'countries': ['US'],
            'location_types': ['home', 'recent'],
        },
        'age_min': 28,
        'age_max': 55,
        # Feeds only — no Audience Network, no Stories
        'publisher_platforms': ['facebook', 'instagram'],
        'facebook_positions': ['feed'],
        'instagram_positions': ['stream'],
        'device_platforms': ['desktop', 'mobile'],
        # OR logic: match anyone interested in any of these trading topics
        'flexible_spec': [
            {
                'interests': [
                    {'id': i['id'], 'name': i['name']}
                    for i in validated_interests
                ]
            }
        ],
    }

    # Disable Advantage+ audience expansion — keep our tight manual targeting
    targeting_spec['targeting_automation'] = {'advantage_audience': 0}

    console.print(f"  ✓  Ages 28–55 · US · Feed only · {len(validated_interests)} interests · Advantage+ OFF")

    # ── Step 3: Create ad set ─────────────────────────────────────────────────
    console.print("\n[yellow]Step 3: Creating ad set...[/yellow]")

    # Campaign uses CBO — omit daily_budget at ad set level, call API directly
    adset_params = {
        'name': "SA Pro — Active Traders · Feed Only · US · 28-55 · v1",
        'campaign_id': CAMPAIGN_ID,
        'targeting': targeting_spec,
        'optimization_goal': 'OFFSITE_CONVERSIONS',
        'billing_event': 'IMPRESSIONS',
        'bid_strategy': 'LOWEST_COST_WITHOUT_CAP',
        'status': 'PAUSED',
        'promoted_object': {
            'pixel_id': PIXEL_ID,
            'custom_event_type': 'PURCHASE',
        },
    }
    adset = client.ad_account.create_ad_set(params=adset_params)

    adset_id = adset['id']
    console.print(f"  ✓  Ad set: {adset_id}")

    # ── Step 4: Generate ad image via AI ─────────────────────────────────────
    console.print("\n[yellow]Step 4: Generating ad image (Google Gemini)...[/yellow]")

    image_prompt = (
        "Professional dark-themed financial trading dashboard on a laptop and phone, "
        "showing real-time stock price alerts with green upward-trending charts, "
        "AI analyst panel with stock insights, clean modern fintech UI, "
        "no text or logos, dark navy background with blue accent colors, "
        "premium professional look for a stock market subscription platform"
    )

    try:
        image_gen = create_image_generator_from_config(client.config)
        image_bytes = image_gen.generate_ad_image(
            prompt=image_prompt,
            product_name="Stock Alarm Pro",
            style="professional",
            size="1024x1024",
        )

        os.makedirs("generated_images", exist_ok=True)
        image_path = "generated_images/sa_pro_active_traders_v1.png"
        with open(image_path, 'wb') as f:
            f.write(image_bytes)
        console.print(f"  ✓  Image saved: {image_path}")

    except Exception as e:
        console.print(f"  [yellow]⚠  AI image failed ({e}), falling back to existing image[/yellow]")
        image_path = "generated_images/stock_alarm_never_miss_a_breakout.png"
        if not os.path.exists(image_path):
            console.print("[red]No fallback image found — aborting.[/red]")
            sys.exit(1)
        console.print(f"  ✓  Using fallback: {image_path}")

    # ── Step 5: Upload image ──────────────────────────────────────────────────
    console.print("\n[yellow]Step 5: Uploading image to Facebook...[/yellow]")
    image = client.upload_image(image_path=image_path)
    image_hash = image['hash']
    console.print(f"  ✓  Hash: {image_hash}")

    # ── Step 6: Create creative ───────────────────────────────────────────────
    console.print("\n[yellow]Step 6: Creating ad creative...[/yellow]")

    primary_text = (
        "Most traders miss the move because they're watching the wrong stocks.\n\n"
        "Stock Alarm Pro sends real-time alerts the moment your setups trigger — "
        "price breaks, RSI signals, moving average crosses, earnings surprises — "
        "so you act fast, not catch up.\n\n"
        "✓ Alerts on 3,600+ stocks\n"
        "✓ AI analyst that explains every signal\n"
        "✓ Professional screener to find setups before they run\n\n"
        "Start free. No credit card required."
    )

    creative = client.create_image_creative(
        name="SA Pro — Active Traders — Never Miss a Setup v1",
        image_hash=image_hash,
        message=primary_text,
        link=DEST_URL,
        headline="Never Miss a Trade Setup Again",
        description="Real-time alerts + AI analyst for active traders",
        call_to_action_type="SIGN_UP",
    )

    creative_id = creative['id']
    console.print(f"  ✓  Creative: {creative_id}")

    # ── Step 7: Create ad (PAUSED) ────────────────────────────────────────────
    console.print("\n[yellow]Step 7: Creating ad (PAUSED for review)...[/yellow]")

    ad = client.create_ad(
        name="SA Pro — Active Traders — Never Miss a Setup v1",
        adset_id=adset_id,
        creative_id=creative_id,
        status="PAUSED",
    )

    ad_id = ad['id']
    console.print(f"  ✓  Ad: {ad_id}")

    # ── Summary ───────────────────────────────────────────────────────────────
    console.print("\n[bold green]✅ Done! Review in Meta Ads Manager before activating.[/bold green]\n")

    table = Table(title="New Ad — Summary")
    table.add_column("", style="cyan", no_wrap=True)
    table.add_column("", style="yellow")

    table.add_row("Campaign",    f"SA Pro - Active Traders - Conversions v2")
    table.add_row("Campaign ID", CAMPAIGN_ID)
    table.add_row("Ad Set ID",   adset_id)
    table.add_row("Creative ID", creative_id)
    table.add_row("Ad ID",       ad_id)
    table.add_row("Status",      "PAUSED — activate after review")
    table.add_row("Budget",      "$25/day (controlled by CBO campaign)")
    table.add_row("Optimize",    "OFFSITE_CONVERSIONS → Purchase (pixel)")
    table.add_row("Placements",  "Facebook Feed + Instagram Feed only")
    table.add_row("Audience",    "US · Ages 28–55 · Active trading interests")
    table.add_row("Interests",   " · ".join(i['name'] for i in validated_interests))

    console.print(table)
    console.print(
        "\n[dim]Next step: open Meta Ads Manager, verify the ad preview and "
        "conversion event, then activate the ad set.[/dim]\n"
    )


if __name__ == "__main__":
    main()
