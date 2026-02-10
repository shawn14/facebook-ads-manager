#!/usr/bin/env python3
"""Setup first campaigns for the Facebook Ads Manager."""

from src.api_client import FacebookAdsClient
from src.campaign.manager import CampaignManager
from src.targeting.presets import TargetingPresets
from src.targeting.builder import TargetingBuilder
from rich.console import Console
from rich.table import Table

console = Console()

def main():
    """Create initial test campaigns."""
    console.print("\n[bold cyan]Setting up your first Facebook ad campaigns...[/bold cyan]\n")

    # Initialize client
    client = FacebookAdsClient()
    manager = CampaignManager(client)

    campaigns_created = []

    # Campaign 1: Broad US Audience (General targeting)
    console.print("[yellow]Creating Campaign 1: Broad US Audience...[/yellow]")
    try:
        campaign_name = "Test Campaign 1 - Broad US Audience"
        campaign1 = manager.create_campaign(
            name=campaign_name,
            objective="OUTCOME_TRAFFIC",
            daily_budget=20,
            status="PAUSED"
        )
        campaigns_created.append({
            'name': campaign_name,
            'id': campaign1.get('id', 'Unknown'),
            'objective': 'OUTCOME_TRAFFIC',
            'budget': '$20/day',
            'status': 'PAUSED',
            'targeting': 'Broad US, Ages 25-65'
        })
        console.print(f"[green]✓[/green] Created: {campaign_name} (ID: {campaign1.get('id', 'Unknown')})\n")
    except Exception as e:
        console.print(f"[red]✗ Error creating Campaign 1:[/red] {e}\n")

    # Campaign 2: E-commerce Shoppers
    console.print("[yellow]Creating Campaign 2: E-commerce Shoppers...[/yellow]")
    try:
        campaign_name = "Test Campaign 2 - E-commerce Shoppers"
        campaign2 = manager.create_campaign(
            name=campaign_name,
            objective="OUTCOME_TRAFFIC",
            daily_budget=20,
            status="PAUSED"
        )
        campaigns_created.append({
            'name': campaign_name,
            'id': campaign2.get('id', 'Unknown'),
            'objective': 'OUTCOME_TRAFFIC',
            'budget': '$20/day',
            'status': 'PAUSED',
            'targeting': 'Online shoppers, Ages 25-55'
        })
        console.print(f"[green]✓[/green] Created: {campaign_name} (ID: {campaign2.get('id', 'Unknown')})\n")
    except Exception as e:
        console.print(f"[red]✗ Error creating Campaign 2:[/red] {e}\n")

    # Campaign 3: Tech Enthusiasts
    console.print("[yellow]Creating Campaign 3: Tech Enthusiasts...[/yellow]")
    try:
        campaign_name = "Test Campaign 3 - Tech Enthusiasts"
        campaign3 = manager.create_campaign(
            name=campaign_name,
            objective="OUTCOME_TRAFFIC",
            daily_budget=20,
            status="PAUSED"
        )
        campaigns_created.append({
            'name': campaign_name,
            'id': campaign3.get('id', 'Unknown'),
            'objective': 'OUTCOME_TRAFFIC',
            'budget': '$20/day',
            'status': 'PAUSED',
            'targeting': 'Tech/gadget lovers, Ages 25-55'
        })
        console.print(f"[green]✓[/green] Created: {campaign_name} (ID: {campaign3.get('id', 'Unknown')})\n")
    except Exception as e:
        console.print(f"[red]✗ Error creating Campaign 3:[/red] {e}\n")

    # Display summary
    if campaigns_created:
        console.print("\n[bold green]✓ Successfully created campaigns![/bold green]\n")

        table = Table(title="Campaign Summary")
        table.add_column("Campaign Name", style="cyan")
        table.add_column("ID", style="yellow")
        table.add_column("Objective")
        table.add_column("Budget", justify="right", style="green")
        table.add_column("Status", style="magenta")
        table.add_column("Targeting")

        for camp in campaigns_created:
            table.add_row(
                camp['name'],
                camp['id'],
                camp['objective'],
                camp['budget'],
                camp['status'],
                camp['targeting']
            )

        console.print(table)

        # Next steps
        console.print("\n[bold cyan]Next Steps:[/bold cyan]")
        console.print("1. [yellow]Create ad sets[/yellow] with specific targeting for each campaign")
        console.print("2. [yellow]Create ad creatives[/yellow] (images, copy, etc.)")
        console.print("3. [yellow]Review and activate[/yellow] campaigns when ready")
        console.print("\n[dim]Note: Campaigns are PAUSED by default. Activate them after setup.[/dim]")
        console.print("\n[bold]View campaigns in the web dashboard:[/bold]")
        console.print("  python run_web.py")
        console.print("  Then visit: http://localhost:8000/campaigns")
    else:
        console.print("\n[bold red]No campaigns were created. Please check for errors above.[/bold red]")

if __name__ == "__main__":
    main()
