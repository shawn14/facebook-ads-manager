"""FastAPI web application for Facebook Ads Manager."""

from fastapi import FastAPI, HTTPException, Request, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from pathlib import Path
from datetime import datetime
import logging
import io
import traceback
import requests as http_requests

from ..api_client import FacebookAdsClient
from ..campaign.manager import CampaignManager
from ..analytics.reporter import AnalyticsReporter
from ..optimization.optimizer import BudgetOptimizer
from ..creative.image_generator import AIImageGenerator, create_image_generator_from_config
from ..creative.ai_ad_generator import AIAdGenerator
from ..conversion.tracker import ConversionTracker

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Facebook Ads Manager",
    description="Modern web dashboard for Facebook advertising campaigns",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup templates and static files
BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# Initialize clients (lazy loading)
_fb_client = None
_campaign_manager = None
_analytics_reporter = None
_budget_optimizer = None
_image_generator = None
_ai_ad_generator = None


def get_clients():
    """Lazy load and return initialized clients."""
    global _fb_client, _campaign_manager, _analytics_reporter, _budget_optimizer, _image_generator

    if _fb_client is None:
        try:
            _fb_client = FacebookAdsClient()
            _campaign_manager = CampaignManager(_fb_client)
            _analytics_reporter = AnalyticsReporter(_fb_client)
            _budget_optimizer = BudgetOptimizer(_fb_client)

            # Initialize image generator from config
            _image_generator = create_image_generator_from_config(_fb_client.config)
            logger.info(f"Image generator initialized with provider: {_image_generator.provider}")
        except Exception as e:
            logger.error(f"Failed to initialize clients: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to initialize Facebook API client. Check configuration."
            )

    return _fb_client, _campaign_manager, _analytics_reporter, _budget_optimizer, _image_generator


# HTML Routes

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Dashboard home page."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/campaigns", response_class=HTMLResponse)
async def campaigns_page(request: Request):
    """Campaign management page."""
    return templates.TemplateResponse("campaigns.html", {"request": request})


@app.get("/analytics", response_class=HTMLResponse)
async def analytics_page(request: Request):
    """Analytics page."""
    return templates.TemplateResponse("analytics.html", {"request": request})


@app.get("/optimization", response_class=HTMLResponse)
async def optimization_page(request: Request):
    """Budget optimization page."""
    return templates.TemplateResponse("optimization.html", {"request": request})


@app.get("/creatives", response_class=HTMLResponse)
async def creatives_page(request: Request):
    """Creative library page."""
    return templates.TemplateResponse("creatives.html", {"request": request})


@app.get("/ai-creator", response_class=HTMLResponse)
async def ai_creator_page(request: Request):
    """AI Ad Creator page."""
    return templates.TemplateResponse("ai_creator.html", {"request": request})


@app.get("/ads", response_class=HTMLResponse)
async def ads_page(request: Request):
    """Ads management page."""
    return templates.TemplateResponse("ads.html", {"request": request})


# API Routes

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.get("/api/account")
async def get_account_info():
    """Get ad account information."""
    try:
        client, _, _, _, _ = get_clients()
        account_info = client.get_account_info()
        return account_info
    except Exception as e:
        logger.error(f"Error fetching account info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/campaigns")
async def list_campaigns(
    status: Optional[str] = None,
    include_insights: bool = False
):
    """List all campaigns."""
    try:
        _, campaign_manager, _, _, _ = get_clients()
        campaigns = campaign_manager.list_campaigns(
            status_filter=status,
            include_insights=include_insights
        )
        return {"campaigns": campaigns, "count": len(campaigns)}
    except Exception as e:
        logger.error(f"Error fetching campaigns: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/campaigns")
async def create_campaign(
    name: str,
    objective: str,
    daily_budget: float,
    status: str = "PAUSED"
):
    """Create a new campaign."""
    try:
        _, campaign_manager, _, _, _ = get_clients()
        campaign = campaign_manager.create_campaign(
            name=name,
            objective=objective,
            daily_budget=daily_budget,
            status=status
        )
        return campaign
    except Exception as e:
        logger.error(f"Error creating campaign: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/campaigns/{campaign_id}/status")
async def update_campaign_status(campaign_id: str, status: str):
    """Update campaign status (ACTIVE/PAUSED)."""
    try:
        _, campaign_manager, _, _, _ = get_clients()

        if status == "ACTIVE":
            campaign_manager.activate_campaign(campaign_id)
        elif status == "PAUSED":
            campaign_manager.pause_campaign(campaign_id)
        else:
            raise HTTPException(status_code=400, detail="Invalid status")

        return {"campaign_id": campaign_id, "status": status}
    except Exception as e:
        logger.error(f"Error updating campaign status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/campaigns/{campaign_id}/budget")
async def update_campaign_budget(campaign_id: str, budget: float):
    """Update campaign budget."""
    try:
        _, campaign_manager, _, _, _ = get_clients()
        campaign_manager.update_budget(campaign_id, budget)
        return {"campaign_id": campaign_id, "new_budget": budget}
    except Exception as e:
        logger.error(f"Error updating campaign budget: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/campaigns/{campaign_id}")
async def delete_campaign(campaign_id: str):
    """Delete a campaign."""
    try:
        client, _, _, _, _ = get_clients()
        client.delete_campaign(campaign_id)
        return {"message": "Campaign deleted successfully", "campaign_id": campaign_id}
    except Exception as e:
        logger.error(f"Error deleting campaign: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analytics/overview")
async def get_analytics_overview(days: int = 7):
    """Get account-level analytics overview."""
    try:
        _, _, analytics_reporter, _, _ = get_clients()
        report = analytics_reporter.account_report(days=days)

        # Calculate summary metrics
        total_spend = sum(r['spend'] for r in report)
        total_impressions = sum(r['impressions'] for r in report)
        total_clicks = sum(r['clicks'] for r in report)
        total_conversions = sum(r['conversions'] for r in report)
        avg_roas = sum(r['roas'] for r in report) / len(report) if report else 0

        return {
            "campaigns": report,
            "summary": {
                "total_spend": total_spend,
                "total_impressions": total_impressions,
                "total_clicks": total_clicks,
                "total_conversions": total_conversions,
                "average_roas": avg_roas,
                "campaign_count": len(report)
            }
        }
    except Exception as e:
        logger.error(f"Error fetching analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analytics/campaign/{campaign_id}")
async def get_campaign_analytics(campaign_id: str, days: int = 7):
    """Get analytics for a specific campaign."""
    try:
        _, _, analytics_reporter, _, _ = get_clients()
        report = analytics_reporter.campaign_report(campaign_id, days=days)

        if 'error' in report:
            raise HTTPException(status_code=404, detail=report['error'])

        return report
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching campaign analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analytics/anomalies/{campaign_id}")
async def detect_anomalies(campaign_id: str):
    """Detect performance anomalies for a campaign."""
    try:
        _, _, analytics_reporter, _, _ = get_clients()
        anomalies = analytics_reporter.detect_anomalies(campaign_id)
        return {"campaign_id": campaign_id, "anomalies": anomalies}
    except Exception as e:
        logger.error(f"Error detecting anomalies: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/optimization/budgets")
async def optimize_budgets(min_roas: Optional[float] = None, dry_run: bool = True):
    """Optimize budget allocation across campaigns."""
    try:
        _, _, _, budget_optimizer, _ = get_clients()
        changes = budget_optimizer.optimize_budgets(
            min_roas=min_roas,
            dry_run=dry_run
        )
        return {
            "changes": changes,
            "count": len(changes),
            "dry_run": dry_run
        }
    except Exception as e:
        logger.error(f"Error optimizing budgets: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/optimization/pause-underperformers")
async def pause_underperformers(
    min_ctr: float = 0.5,
    min_spend: float = 100,
    dry_run: bool = True
):
    """Pause underperforming campaigns."""
    try:
        _, _, _, budget_optimizer, _ = get_clients()
        paused = budget_optimizer.pause_underperformers(
            min_ctr=min_ctr,
            min_spend=min_spend,
            dry_run=dry_run
        )
        return {
            "paused_campaigns": paused,
            "count": len(paused),
            "dry_run": dry_run
        }
    except Exception as e:
        logger.error(f"Error pausing underperformers: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/optimization/rebalance")
async def rebalance_portfolio(total_budget: float, dry_run: bool = True):
    """Rebalance budget across all campaigns."""
    try:
        _, _, _, budget_optimizer, _ = get_clients()
        allocations = budget_optimizer.rebalance_portfolio(
            total_budget=total_budget,
            dry_run=dry_run
        )
        return {
            "allocations": allocations,
            "total_budget": total_budget,
            "dry_run": dry_run
        }
    except Exception as e:
        logger.error(f"Error rebalancing portfolio: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Creative Management Endpoints

@app.get("/api/creatives")
async def get_creatives(include_stats: bool = True):
    """Get all ad creatives from Facebook with performance stats."""
    try:
        client, _, _, _, _ = get_clients()
        creatives = client.get_creatives(limit=100)

        # Format creatives for frontend
        formatted_creatives = []
        for creative in creatives:
            formatted = {
                'id': creative.get('id'),
                'name': creative.get('name', 'Untitled'),
                'status': creative.get('status', 'ACTIVE'),
                'thumbnail_url': creative.get('image_url') or creative.get('thumbnail_url'),
                'object_story_spec': creative.get('object_story_spec', {}),
            }

            # Determine type
            if creative.get('video_id'):
                formatted['type'] = 'video'
            elif creative.get('object_story_spec', {}).get('link_data', {}).get('child_attachments'):
                formatted['type'] = 'carousel'
            else:
                formatted['type'] = 'image'

            # Extract copy elements
            story_spec = creative.get('object_story_spec', {})
            link_data = story_spec.get('link_data', {})
            formatted['headline'] = link_data.get('name', '')
            formatted['description'] = link_data.get('message', '')
            formatted['call_to_action'] = link_data.get('call_to_action', {}).get('type', 'LEARN_MORE')

            # Get performance stats if requested
            if include_stats:
                try:
                    # Get ads using this creative
                    from facebook_business.adobjects.ad import Ad

                    # Get all ads
                    ads = client.ad_account.get_ads(
                        params={'effective_status': ['ACTIVE', 'PAUSED']},
                        fields=['id', 'creative']
                    )

                    # Aggregate stats for this creative
                    total_impressions = 0
                    total_clicks = 0
                    total_spend = 0
                    total_conversions = 0

                    for ad in ads:
                        if ad.get('creative', {}).get('id') == creative.get('id'):
                            # Fetch insights for this ad
                            try:
                                fb_ad = Ad(ad.get('id'))
                                insights = fb_ad.get_insights(
                                    fields=['spend', 'impressions', 'clicks', 'actions'],
                                    params={'date_preset': 'maximum'}
                                )

                                if insights and len(insights) > 0:
                                    insight = insights[0]
                                    total_impressions += int(insight.get('impressions', 0))
                                    total_clicks += int(insight.get('clicks', 0))
                                    total_spend += float(insight.get('spend', 0))

                                    # Get conversions if available
                                    actions = insight.get('actions', [])
                                    for action in actions:
                                        if action.get('action_type') in ['purchase', 'lead', 'complete_registration', 'offsite_conversion.fb_pixel_purchase']:
                                            total_conversions += int(action.get('value', 0))
                            except Exception as ad_error:
                                logger.debug(f"No insights for ad {ad.get('id')}: {ad_error}")

                    # Calculate metrics
                    ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
                    cpc = (total_spend / total_clicks) if total_clicks > 0 else 0

                    formatted['stats'] = {
                        'impressions': total_impressions,
                        'clicks': total_clicks,
                        'spend': round(total_spend, 2),
                        'conversions': total_conversions,
                        'ctr': round(ctr, 2),
                        'cpc': round(cpc, 2)
                    }

                except Exception as stats_error:
                    logger.warning(f"Failed to get stats for creative {creative.get('id')}: {stats_error}")
                    # Default stats if fetch fails
                    formatted['stats'] = {
                        'impressions': 0,
                        'clicks': 0,
                        'spend': 0,
                        'conversions': 0,
                        'ctr': 0,
                        'cpc': 0
                    }
            else:
                formatted['stats'] = {
                    'impressions': 0,
                    'clicks': 0,
                    'spend': 0,
                    'conversions': 0,
                    'ctr': 0,
                    'cpc': 0
                }

            formatted_creatives.append(formatted)

        return {"creatives": formatted_creatives, "count": len(formatted_creatives)}
    except Exception as e:
        logger.error(f"Error fetching creatives: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/creatives/image")
async def create_image_creative(
    name: str,
    headline: str,
    description: str,
    image_hash: str,
    link_url: str,
    call_to_action: str = "LEARN_MORE"
):
    """Create a new image creative.

    Facebook Ad Specifications:
    - Headline: Max 40 characters
    - Description: Max 125 characters (primary text: max 255 characters)
    - Image: 1200x628px recommended (1.91:1 ratio)
    - File size: Max 30MB
    - Formats: JPG, PNG
    """
    try:
        # Validate character limits
        if len(headline) > 40:
            raise HTTPException(status_code=400, detail="Headline must be 40 characters or less")
        if len(description) > 125:
            raise HTTPException(status_code=400, detail="Description must be 125 characters or less")

        client, _, _, _, _ = get_clients()
        creative = client.create_image_creative(
            name=name,
            image_hash=image_hash,
            message=description,
            link=link_url,
            call_to_action_type=call_to_action,
            headline=headline
        )
        return creative
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating image creative: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/creatives/video")
async def create_video_creative(
    name: str,
    headline: str,
    description: str,
    video_id: str,
    link_url: str,
    call_to_action: str = "LEARN_MORE"
):
    """Create a new video creative.

    Facebook Video Ad Specifications:
    - Headline: Max 40 characters
    - Description: Max 125 characters
    - Video length: 1 second to 241 minutes
    - Video size: Max 4GB
    - Formats: MP4, MOV, GIF
    - Recommended: 1080x1080px (1:1) or 1920x1080px (16:9)
    """
    try:
        # Validate character limits
        if len(headline) > 40:
            raise HTTPException(status_code=400, detail="Headline must be 40 characters or less")
        if len(description) > 125:
            raise HTTPException(status_code=400, detail="Description must be 125 characters or less")

        client, _, _, _, _ = get_clients()
        creative = client.create_video_creative(
            name=name,
            video_id=video_id,
            message=description,
            link=link_url,
            call_to_action_type=call_to_action,
            headline=headline
        )
        return creative
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating video creative: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/creatives/specifications")
async def get_creative_specifications():
    """Get Facebook ad creative specifications and limits."""
    return {
        "text_limits": {
            "headline": {
                "max": 40,
                "description": "Headline appears in large text"
            },
            "primary_text": {
                "max": 125,
                "recommended": 125,
                "description": "Main ad copy (description)"
            },
            "link_description": {
                "max": 30,
                "description": "Appears below headline"
            }
        },
        "image_specs": {
            "recommended_resolution": "1200x628px",
            "aspect_ratio": "1.91:1 (landscape), 1:1 (square), 4:5 (vertical)",
            "min_resolution": "600x314px",
            "max_file_size": "30MB",
            "formats": ["JPG", "PNG"]
        },
        "video_specs": {
            "recommended_resolution": "1080x1080px (1:1) or 1920x1080px (16:9)",
            "length": "1 second to 241 minutes (recommended: 15 seconds or less)",
            "max_file_size": "4GB",
            "formats": ["MP4", "MOV", "GIF"],
            "aspect_ratios": ["1:1", "4:5", "9:16", "16:9"]
        },
        "call_to_action_types": [
            "LEARN_MORE",
            "SHOP_NOW",
            "SIGN_UP",
            "DOWNLOAD",
            "BOOK_NOW",
            "CONTACT_US",
            "GET_QUOTE",
            "APPLY_NOW",
            "SUBSCRIBE",
            "WATCH_MORE"
        ]
    }


# Image Upload & AI Generation Endpoints

@app.post("/api/images/upload")
async def upload_image(file: UploadFile = File(...)):
    """Upload an image to Facebook and get the image hash.

    Args:
        file: Image file (JPG, PNG)

    Returns:
        dict with image_hash and metadata
    """
    try:
        client, _, _, _, _ = get_clients()

        # Read image bytes
        image_bytes = await file.read()

        # Upload to Facebook - save to temp file first
        import tempfile
        import os
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
            tmp_file.write(image_bytes)
            tmp_path = tmp_file.name

        try:
            params = {'filename': tmp_path}
            uploaded_image = client.ad_account.create_ad_image(params=params)
            image_hash = uploaded_image['hash']
            logger.info(f"✅ Uploaded image: {file.filename} → {image_hash}")
        finally:
            os.unlink(tmp_path)

        return {
            "image_hash": image_hash,
            "filename": file.filename,
            "size": len(image_bytes),
            "status": "uploaded"
        }

    except Exception as e:
        logger.error(f"Failed to upload image: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/images/generate")
async def generate_ai_image(
    prompt: str = Form(...),
    product_name: str = Form(""),
    style: str = Form("professional"),
    format_type: str = Form("feed"),
    save_locally: bool = Form(True)
):
    """Generate an ad image using AI (Google Gemini).

    Args:
        prompt: Image description
        product_name: Product/service name
        style: Visual style (professional, modern, minimalist, bold, tech, finance)
        format_type: Facebook ad format (feed, square, story, carousel)
        save_locally: Save image to generated_images/ folder

    Returns:
        dict with image_hash, download_url, and metadata
    """
    try:
        client, _, _, _, image_gen = get_clients()

        # Generate image with AI
        logger.info(f"Generating AI image: {prompt}")
        image_bytes = image_gen.generate_ad_image(
            prompt=prompt,
            product_name=product_name,
            style=style,
            size="1024x1024"
        )

        if not image_bytes:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate image. Check AI API key is set."
            )

        # Resize for Facebook
        resized_bytes = image_gen.resize_for_facebook(image_bytes, format_type)

        # Save locally if requested
        local_filename = None
        if save_locally:
            output_dir = Path("generated_images")
            output_dir.mkdir(exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_prompt = "".join(c for c in prompt[:30] if c.isalnum() or c in (' ', '-', '_')).strip()
            local_filename = f"{timestamp}_{safe_prompt}.png"
            local_path = output_dir / local_filename

            with open(local_path, "wb") as f:
                f.write(image_bytes)
            logger.info(f"💾 Saved locally: {local_path}")

        # Upload to Facebook - save to temp file first
        import tempfile
        import os
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
            tmp_file.write(resized_bytes)
            tmp_path = tmp_file.name

        try:
            params = {'filename': tmp_path}
            uploaded_image = client.ad_account.create_ad_image(params=params)
            image_hash = uploaded_image['hash']
            logger.info(f"✅ Generated and uploaded AI image → {image_hash}")
        finally:
            os.unlink(tmp_path)

        return {
            "image_hash": image_hash,
            "prompt": prompt,
            "style": style,
            "format": format_type,
            "size": len(image_bytes),
            "local_filename": local_filename,
            "download_url": f"/api/images/download/{local_filename}" if local_filename else None,
            "status": "generated"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate AI image: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/creatives/create-with-image")
async def create_creative_with_image(
    name: str = Form(...),
    headline: str = Form(...),
    description: str = Form(...),
    link_url: str = Form(...),
    call_to_action: str = Form("LEARN_MORE"),
    image_hash: str = Form(None),
    generate_image: bool = Form(False),
    image_prompt: str = Form(""),
    product_name: str = Form(""),
    style: str = Form("professional")
):
    """Create a complete ad creative with image (uploaded or AI-generated).

    Args:
        name: Creative name
        headline: Ad headline (max 40 chars)
        description: Primary text (max 125 chars)
        link_url: Destination URL
        call_to_action: CTA type
        image_hash: Pre-uploaded image hash (if not generating)
        generate_image: Whether to generate image with AI
        image_prompt: Prompt for AI image generation
        product_name: Product name for AI generation
        style: Visual style for AI generation

    Returns:
        Created creative object
    """
    try:
        # Validate character limits
        if len(headline) > 40:
            raise HTTPException(status_code=400, detail="Headline must be 40 characters or less")
        if len(description) > 125:
            raise HTTPException(status_code=400, detail="Description must be 125 characters or less")

        client, _, _, _, image_gen = get_clients()

        # Get or generate image hash
        final_image_hash = image_hash

        if generate_image and image_prompt:
            # Generate AI image
            logger.info(f"Generating AI image for creative: {name}")
            image_bytes = image_gen.generate_ad_image(
                prompt=image_prompt,
                product_name=product_name,
                style=style
            )

            if not image_bytes:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to generate image. Check OpenAI API key."
                )

            # Resize and upload
            image_bytes = image_gen.resize_for_facebook(image_bytes, "feed")

            # Save to temp file and upload
            import tempfile
            import os
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
                tmp_file.write(image_bytes)
                tmp_path = tmp_file.name

            try:
                params = {'filename': tmp_path}
                uploaded_image = client.ad_account.create_ad_image(params=params)
                final_image_hash = uploaded_image['hash']
                logger.info(f"✅ Generated AI image → {final_image_hash}")
            finally:
                os.unlink(tmp_path)

        if not final_image_hash:
            raise HTTPException(status_code=400, detail="No image provided or generated")

        # Create the creative
        creative = client.create_image_creative(
            name=name,
            image_hash=final_image_hash,
            message=description,
            link=link_url,
            call_to_action_type=call_to_action,
            headline=headline
        )

        logger.info(f"✅ Created creative: {creative.get('id')}")

        return {
            "creative": creative,
            "image_hash": final_image_hash,
            "ai_generated": generate_image,
            "status": "created"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create creative: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/images/suggest-prompt")
async def suggest_image_prompt(
    product_name: str = Form(...),
    headline: str = Form(...),
    description: str = Form(...),
    industry: str = Form("tech")
):
    """Generate a suggested image prompt based on ad copy.

    Args:
        product_name: Product/service name
        headline: Ad headline
        description: Ad description
        industry: Industry category

    Returns:
        Suggested DALL-E prompt
    """
    try:
        _, _, _, _, image_gen = get_clients()

        suggested_prompt = image_gen.suggest_prompt(
            product_name=product_name,
            headline=headline,
            description=description,
            industry=industry
        )

        return {
            "suggested_prompt": suggested_prompt,
            "can_customize": True
        }

    except Exception as e:
        logger.error(f"Failed to suggest prompt: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Conversational AI Ad Creator

@app.post("/api/ai/create-ad-from-prompt")
async def create_ad_from_natural_language(
    prompt: str = Form(...),
    product_name: str = Form(""),
    link_url: str = Form(...),
    industry: str = Form("tech")
):
    """Create a complete ad from natural language description.

    Example: "I want to promote our free trial to day traders who missed NVDA's jump"

    Args:
        prompt: What you want the ad to do (natural language)
        product_name: Your product/service name
        link_url: Destination URL
        industry: Industry (tech, finance, ecommerce, saas, health, education)

    Returns:
        Complete ad creative with AI-generated copy and image
    """
    try:
        # Initialize AI generators
        ai_gen = AIAdGenerator()
        client, _, _, _, _, = get_clients()
        _, _, _, _, image_gen = get_clients()

        if not ai_gen.client:
            raise HTTPException(
                status_code=500,
                detail="OpenAI API key not set. Add to config.yaml or set OPENAI_API_KEY env var."
            )

        logger.info(f"Creating ad from prompt: {prompt}")

        # Step 1: Generate complete ad plan using AI
        ad_plan = ai_gen.generate_complete_ad_plan(
            user_input=prompt,
            product_name=product_name,
            industry=industry
        )

        if not ad_plan:
            raise HTTPException(status_code=500, detail="Failed to generate ad plan")

        # Step 2: Generate image using AI
        logger.info(f"Generating image: {ad_plan.get('image_prompt', '')}")
        image_bytes = image_gen.generate_ad_image(
            prompt=ad_plan.get('image_prompt', prompt),
            product_name=product_name,
            style=ad_plan.get('image_style', 'professional'),
            size="1024x1024"
        )

        if not image_bytes:
            raise HTTPException(status_code=500, detail="Failed to generate image")

        # Save locally
        output_dir = Path("generated_images")
        output_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = "".join(c for c in product_name[:20] if c.isalnum() or c in (' ', '-', '_')).strip()
        local_filename = f"{timestamp}_{safe_name}_ad.png"
        local_path = output_dir / local_filename

        with open(local_path, "wb") as f:
            f.write(image_bytes)
        logger.info(f"💾 Saved AI-generated image: {local_path}")

        # Resize for Facebook
        image_bytes = image_gen.resize_for_facebook(
            image_bytes,
            ad_plan.get('ad_format', 'feed')
        )

        # Step 3: Upload image to Facebook
        # Save to temp file first (Facebook API needs a file path)
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
            tmp_file.write(image_bytes)
            tmp_path = tmp_file.name

        try:
            # Upload using the proper method
            params = {'filename': tmp_path}
            uploaded_image = client.ad_account.create_ad_image(params=params)
            image_hash = uploaded_image['hash']
            logger.info(f"✅ Image uploaded: {image_hash}")
        finally:
            # Clean up temp file
            import os
            os.unlink(tmp_path)

        # Step 4: Create the ad creative
        creative = client.create_image_creative(
            name=f"{product_name} - {ad_plan.get('headline', 'AI Generated Ad')}",
            image_hash=image_hash,
            message=ad_plan.get('description', ''),
            link=link_url,
            call_to_action_type=ad_plan.get('call_to_action', 'LEARN_MORE'),
            headline=ad_plan.get('headline', '')
        )

        logger.info(f"✅ Created complete ad: {creative.get('id')}")

        return {
            "status": "success",
            "creative_id": creative.get('id'),
            "ad_plan": ad_plan,
            "image_hash": image_hash,
            "message": "Complete ad created with AI! ✨"
        }

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        logger.error(f"Failed to create ad from prompt: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/ai/generate-copy-variations")
async def generate_ad_copy_variations(
    prompt: str = Form(...),
    product_name: str = Form(""),
    target_audience: str = Form(""),
    goal: str = Form("conversions"),
    tone: str = Form("professional"),
    num_variations: int = Form(3)
):
    """Generate multiple ad copy variations.

    Args:
        prompt: What the ad should communicate
        product_name: Product/service name
        target_audience: Who the ad is for
        goal: Ad goal (conversions, awareness, traffic, engagement)
        tone: Writing tone (professional, casual, urgent, friendly)
        num_variations: Number of variations (1-5)

    Returns:
        List of ad copy variations
    """
    try:
        ai_gen = AIAdGenerator()

        if not ai_gen.client:
            raise HTTPException(
                status_code=500,
                detail="OpenAI API key not set"
            )

        variations = ai_gen.generate_ad_copy(
            prompt=prompt,
            product_name=product_name,
            target_audience=target_audience,
            goal=goal,
            tone=tone,
            num_variations=min(num_variations, 5)
        )

        return {
            "variations": variations,
            "count": len(variations)
        }

    except Exception as e:
        logger.error(f"Failed to generate variations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/ai/improve-copy")
async def improve_ad_copy(
    current_headline: str = Form(...),
    current_description: str = Form(...),
    feedback: str = Form("make it more compelling")
):
    """Improve existing ad copy based on feedback.

    Args:
        current_headline: Current headline
        current_description: Current description
        feedback: What to improve

    Returns:
        Improved ad copy
    """
    try:
        ai_gen = AIAdGenerator()

        if not ai_gen.client:
            raise HTTPException(status_code=500, detail="OpenAI API key not set")

        improved = ai_gen.improve_ad_copy(
            current_headline=current_headline,
            current_description=current_description,
            feedback=feedback
        )

        return {
            "original": {
                "headline": current_headline,
                "description": current_description
            },
            "improved": improved
        }

    except Exception as e:
        logger.error(f"Failed to improve copy: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Ad Set Management Endpoints

@app.get("/api/campaigns/{campaign_id}/adsets")
async def list_adsets(campaign_id: str):
    """List all ad sets in a campaign."""
    try:
        client, _, _, _, _ = get_clients()
        adsets = client.get_adsets(campaign_id=campaign_id)

        formatted_adsets = []
        for adset in adsets:
            formatted_adsets.append({
                'id': adset.get('id'),
                'name': adset.get('name'),
                'status': adset.get('status'),
                'daily_budget': adset.get('daily_budget'),
                'optimization_goal': adset.get('optimization_goal'),
                'billing_event': adset.get('billing_event'),
            })

        return {"adsets": formatted_adsets, "count": len(formatted_adsets)}
    except Exception as e:
        logger.error(f"Error fetching ad sets: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/campaigns/{campaign_id}/adsets")
async def create_adset(
    campaign_id: str,
    name: str = Form(...),
    daily_budget: float = Form(...),
    optimization_goal: str = Form("LINK_CLICKS"),
    billing_event: str = Form("IMPRESSIONS"),
    status: str = Form("PAUSED")
):
    """Create a new ad set in a campaign."""
    try:
        client, _, _, _, _ = get_clients()

        # Create ad set with default targeting (US, 25-65)
        adset = client.create_adset(
            campaign_id=campaign_id,
            name=name,
            daily_budget=daily_budget,
            optimization_goal=optimization_goal,
            billing_event=billing_event,
            targeting={
                'geo_locations': {'countries': ['US']},
                'age_min': 25,
                'age_max': 65
            },
            status=status
        )

        return adset
    except Exception as e:
        logger.error(f"Error creating ad set: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Ad Management Endpoints

@app.get("/api/adsets/{adset_id}/ads")
async def list_ads(adset_id: str):
    """List all ads in an ad set."""
    try:
        client, _, _, _, _ = get_clients()
        ads = client.get_ads(adset_id=adset_id)

        formatted_ads = []
        for ad in ads:
            formatted_ads.append({
                'id': ad.get('id'),
                'name': ad.get('name'),
                'status': ad.get('status'),
                'creative_id': ad.get('creative', {}).get('id'),
            })

        return {"ads": formatted_ads, "count": len(formatted_ads)}
    except Exception as e:
        logger.error(f"Error fetching ads: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/ads")
async def list_all_ads(limit: int = 100, include_stats: bool = True):
    """List all ads across all campaigns with performance stats."""
    try:
        client, _, _, _, _ = get_clients()

        # Get all ads from ad account
        fields = ['id', 'name', 'status', 'creative', 'adset_id', 'campaign_id']

        ads = client.ad_account.get_ads(
            fields=fields,
            params={'limit': limit}
        )

        formatted_ads = []
        for ad in ads:
            ad_data = {
                'id': ad.get('id'),
                'name': ad.get('name'),
                'status': ad.get('status'),
                'creative_id': ad.get('creative', {}).get('id') if ad.get('creative') else None,
                'adset_id': ad.get('adset_id'),
                'campaign_id': ad.get('campaign_id'),
            }

            # Fetch creative details
            creative_id = ad.get('creative', {}).get('id') if ad.get('creative') else None
            if creative_id:
                try:
                    from facebook_business.adobjects.adcreative import AdCreative
                    creative = AdCreative(creative_id)
                    creative_data = creative.api_get(fields=[
                        'thumbnail_url',
                        'image_url',
                        'object_story_spec',
                        'title',
                        'body',
                        'link_url',
                        'call_to_action_type'
                    ])

                    # Get both thumbnail and full-size image
                    thumbnail = creative_data.get('thumbnail_url')
                    full_image = creative_data.get('image_url') or thumbnail

                    if thumbnail:
                        ad_data['creative_thumbnail'] = thumbnail
                    if full_image:
                        ad_data['creative_full_image'] = full_image

                    # Get ad copy from object_story_spec
                    story_spec = creative_data.get('object_story_spec', {})
                    link_data = story_spec.get('link_data', {})

                    if link_data:
                        ad_data['creative_headline'] = link_data.get('name', '')
                        ad_data['creative_message'] = link_data.get('message', '')
                        ad_data['creative_description'] = link_data.get('description', '')
                        ad_data['creative_link'] = link_data.get('link', '')
                        cta = link_data.get('call_to_action', {})
                        ad_data['creative_cta'] = cta.get('type', '').replace('_', ' ').title() if cta else ''

                except Exception as e:
                    logger.debug(f"Could not fetch creative details for {creative_id}: {e}")

            # Add stats if requested
            if include_stats:
                try:
                    # Fetch insights with date range (lifetime stats)
                    from facebook_business.adobjects.ad import Ad
                    fb_ad = Ad(ad.get('id'))

                    insights = fb_ad.get_insights(
                        fields=['spend', 'impressions', 'clicks', 'ctr', 'cpc', 'actions'],
                        params={'date_preset': 'maximum'}
                    )

                    if insights and len(insights) > 0:
                        insight = insights[0]

                        # Get conversions
                        conversions = 0
                        actions = insight.get('actions', [])
                        for action in actions:
                            if action.get('action_type') in ['purchase', 'lead', 'complete_registration', 'offsite_conversion.fb_pixel_purchase']:
                                conversions += int(action.get('value', 0))

                        # Get metrics
                        spend = float(insight.get('spend', 0))
                        impressions = int(insight.get('impressions', 0))
                        clicks = int(insight.get('clicks', 0))

                        # Calculate CTR and CPC
                        ctr = (clicks / impressions * 100) if impressions > 0 else 0
                        cpc = (spend / clicks) if clicks > 0 else 0

                        ad_data['stats'] = {
                            'spend': spend,
                            'impressions': impressions,
                            'clicks': clicks,
                            'ctr': round(ctr, 2),
                            'cpc': round(cpc, 2),
                            'conversions': conversions
                        }
                    else:
                        ad_data['stats'] = {
                            'spend': 0,
                            'impressions': 0,
                            'clicks': 0,
                            'ctr': 0,
                            'cpc': 0,
                            'conversions': 0
                        }
                except Exception as e:
                    logger.warning(f"Failed to get insights for ad {ad.get('id')}: {e}")
                    ad_data['stats'] = {
                        'spend': 0,
                        'impressions': 0,
                        'clicks': 0,
                        'ctr': 0,
                        'cpc': 0,
                        'conversions': 0
                    }

            formatted_ads.append(ad_data)

        return {"ads": formatted_ads, "count": len(formatted_ads)}
    except Exception as e:
        logger.error(f"Error fetching all ads: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/adsets/{adset_id}/ads")
async def create_ad(
    adset_id: str,
    name: str = Form(...),
    creative_id: str = Form(...),
    status: str = Form("PAUSED")
):
    """Create a new ad using an existing creative."""
    try:
        client, _, _, _, _ = get_clients()

        ad = client.create_ad(
            adset_id=adset_id,
            creative_id=creative_id,
            name=name,
            status=status
        )

        logger.info(f"✅ Created ad: {ad.get('id')}")

        return ad
    except Exception as e:
        logger.error(f"Error creating ad: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/ads/create-complete")
async def create_complete_ad_campaign(
    campaign_name: str = Form(...),
    adset_name: str = Form(...),
    ad_name: str = Form(...),
    creative_id: str = Form(...),
    daily_budget: float = Form(50.0),
    optimization_goal: str = Form("LINK_CLICKS"),
    status: str = Form("PAUSED")
):
    """Create a complete campaign → ad set → ad in one request."""
    try:
        client, _, _, _, _ = get_clients()

        # Step 1: Create campaign
        campaign = client.create_campaign(
            name=campaign_name,
            objective="OUTCOME_TRAFFIC",  # LINK_CLICKS objective
            status=status
        )
        campaign_id = campaign['id']
        logger.info(f"✅ Created campaign: {campaign_id}")

        # Step 2: Create ad set
        adset = client.create_adset(
            campaign_id=campaign_id,
            name=adset_name,
            daily_budget=daily_budget,
            optimization_goal=optimization_goal,
            billing_event="IMPRESSIONS",
            targeting={
                'geo_locations': {'countries': ['US']},
                'age_min': 25,
                'age_max': 65
            },
            status=status
        )
        adset_id = adset['id']
        logger.info(f"✅ Created ad set: {adset_id}")

        # Step 3: Create ad
        ad = client.create_ad(
            adset_id=adset_id,
            creative_id=creative_id,
            name=ad_name,
            status=status
        )
        ad_id = ad['id']
        logger.info(f"✅ Created ad: {ad_id}")

        return {
            "status": "success",
            "campaign_id": campaign_id,
            "adset_id": adset_id,
            "ad_id": ad_id,
            "message": "Complete ad campaign created! 🎉"
        }

    except Exception as e:
        logger.error(f"Error creating complete ad: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/ads/{ad_id}/status")
async def update_ad_status(ad_id: str, status: str = Form(...)):
    """Update ad status (ACTIVE/PAUSED)."""
    try:
        client, _, _, _, _ = get_clients()

        from facebook_business.adobjects.ad import Ad
        ad = Ad(ad_id, api=client.api)
        ad.update(params={'status': status})

        return {"ad_id": ad_id, "status": status}
    except Exception as e:
        logger.error(f"Error updating ad status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/ads/{ad_id}")
async def delete_ad(ad_id: str):
    """Delete an ad."""
    try:
        client, _, _, _, _ = get_clients()

        from facebook_business.adobjects.ad import Ad
        ad = Ad(ad_id, api=client.api)
        ad.api_delete()

        return {"message": "Ad deleted successfully", "ad_id": ad_id}
    except Exception as e:
        logger.error(f"Error deleting ad: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Image Download Endpoints

@app.get("/api/images/download/{filename}")
async def download_local_image(filename: str):
    """Download a locally saved generated image."""
    try:
        image_path = Path("generated_images") / filename

        if not image_path.exists():
            raise HTTPException(status_code=404, detail="Image not found")

        # Read image
        with open(image_path, "rb") as f:
            image_bytes = f.read()

        # Return as downloadable file
        return StreamingResponse(
            io.BytesIO(image_bytes),
            media_type="image/png",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to download image: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/images/list")
async def list_generated_images():
    """List all locally saved generated images."""
    try:
        output_dir = Path("generated_images")
        if not output_dir.exists():
            return {"images": [], "count": 0}

        images = []
        for img_path in sorted(output_dir.glob("*.png"), reverse=True):
            stat = img_path.stat()
            images.append({
                "filename": img_path.name,
                "size": stat.st_size,
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "download_url": f"/api/images/download/{img_path.name}"
            })

        return {"images": images, "count": len(images)}

    except Exception as e:
        logger.error(f"Failed to list images: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/creatives/{creative_id}/image")
async def get_creative_image_url(creative_id: str):
    """Get the image URL from a Facebook creative."""
    try:
        client, _, _, _, _ = get_clients()

        # Get creative details
        creative = client.get_creative(creative_id)

        # Extract image URL from creative
        image_url = None
        if creative.get('thumbnail_url'):
            image_url = creative['thumbnail_url']
        elif creative.get('image_url'):
            image_url = creative['image_url']
        elif creative.get('object_story_spec'):
            story_spec = creative['object_story_spec']
            link_data = story_spec.get('link_data', {})
            image_url = link_data.get('picture')

        if not image_url:
            raise HTTPException(status_code=404, detail="No image found in creative")

        return {
            "creative_id": creative_id,
            "image_url": image_url,
            "can_download": True
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get creative image: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/creatives/{creative_id}/download")
async def download_creative_image(creative_id: str):
    """Download the FULL-SIZE image from a Facebook creative."""
    try:
        client, _, _, _, _ = get_clients()

        # Get creative with image fields
        from facebook_business.adobjects.adcreative import AdCreative
        creative_obj = AdCreative(creative_id, api=client.api)
        creative = creative_obj.api_get(fields=[
            'id',
            'name',
            'object_story_spec',
            'image_hash',
            'image_url',
            'thumbnail_url'
        ])

        # Try to get image hash first (best quality)
        image_hash = creative.get('image_hash')

        if image_hash:
            # Get full-size image from ad account using image hash
            try:
                from facebook_business.adobjects.adimage import AdImage
                images = client.ad_account.get_ad_images(
                    params={'hashes': [image_hash]},
                    fields=['url', 'url_128', 'hash']
                )

                if images:
                    # Get the full-size URL (not the thumbnail)
                    image_url = images[0].get('url')
                    if image_url:
                        logger.info(f"Downloading full-size image from hash: {image_hash}")
                        response = http_requests.get(image_url, timeout=30)
                        response.raise_for_status()

                        return StreamingResponse(
                            io.BytesIO(response.content),
                            media_type="image/jpeg",
                            headers={
                                "Content-Disposition": f"attachment; filename=creative_{creative_id}_full.jpg"
                            }
                        )
            except Exception as e:
                logger.warning(f"Failed to get image from hash: {e}")

        # Fallback: Try to get from object_story_spec
        if creative.get('object_story_spec'):
            story_spec = creative['object_story_spec']
            link_data = story_spec.get('link_data', {})

            # Try to get the picture URL (usually full size)
            image_url = link_data.get('picture')

            if image_url:
                logger.info(f"Downloading image from story spec: {image_url}")
                response = http_requests.get(image_url, timeout=30)
                response.raise_for_status()

                return StreamingResponse(
                    io.BytesIO(response.content),
                    media_type="image/jpeg",
                    headers={
                        "Content-Disposition": f"attachment; filename=creative_{creative_id}.jpg"
                    }
                )

        # Last resort: use image_url field (usually better than thumbnail)
        image_url = creative.get('image_url')
        if image_url:
            logger.info(f"Downloading from image_url: {image_url}")
            response = http_requests.get(image_url, timeout=30)
            response.raise_for_status()

            return StreamingResponse(
                io.BytesIO(response.content),
                media_type="image/jpeg",
                headers={
                    "Content-Disposition": f"attachment; filename=creative_{creative_id}.jpg"
                }
            )

        raise HTTPException(status_code=404, detail="No full-size image found in creative")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to download creative image: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/debug/campaign/{campaign_id}")
async def debug_campaign_stats(campaign_id: str):
    """Debug endpoint to see all stats for a campaign and its ads."""
    try:
        client, _, _, _, _ = get_clients()

        # Get campaign info
        from facebook_business.adobjects.campaign import Campaign
        campaign_obj = Campaign(campaign_id, api=client.api)
        campaign = campaign_obj.api_get(fields=[
            'id',
            'name',
            'status',
            'objective',
            'daily_budget',
            'insights{spend,impressions,clicks,actions}'
        ])

        campaign_data = dict(campaign)

        # Get all ad sets in this campaign
        adsets = client.get_adsets(campaign_id=campaign_id)
        adsets_data = []

        for adset in adsets:
            adset_info = {
                'id': adset.get('id'),
                'name': adset.get('name'),
                'status': adset.get('status')
            }

            # Get ads in this ad set
            ads = client.ad_account.get_ads(
                params={'adset_id': adset.get('id')},
                fields=['id', 'name', 'status', 'creative', 'insights{spend,impressions,clicks,actions,ctr,cpc}']
            )

            ads_data = []
            for ad in ads:
                ad_dict = dict(ad)
                ads_data.append({
                    'id': ad_dict.get('id'),
                    'name': ad_dict.get('name'),
                    'status': ad_dict.get('status'),
                    'creative_id': ad_dict.get('creative', {}).get('id'),
                    'insights': ad_dict.get('insights', {}).get('data', [])
                })

            adset_info['ads'] = ads_data
            adsets_data.append(adset_info)

        return {
            'campaign': campaign_data,
            'adsets': adsets_data,
            'adsets_count': len(adsets_data),
            'total_ads': sum(len(adset['ads']) for adset in adsets_data)
        }

    except Exception as e:
        logger.error(f"Debug error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/debug/ad-insights")
async def debug_ad_insights():
    """Debug endpoint to check what insights we're getting from Facebook."""
    try:
        from facebook_business.adobjects.ad import Ad
        client, _, _, _, _ = get_clients()

        # Get all ads
        ads = client.ad_account.get_ads(
            fields=['id', 'name', 'status'],
            params={'limit': 10}
        )

        results = []
        for ad in ads:
            fb_ad = Ad(ad.get('id'))

            # Try to get insights
            try:
                insights = fb_ad.get_insights(
                    fields=['spend', 'impressions', 'clicks', 'reach'],
                    params={'date_preset': 'maximum'}
                )

                insights_data = []
                for insight in insights:
                    insights_data.append(dict(insight))

                results.append({
                    'ad_id': ad.get('id'),
                    'ad_name': ad.get('name'),
                    'insights_count': len(insights_data),
                    'insights': insights_data
                })
            except Exception as e:
                results.append({
                    'ad_id': ad.get('id'),
                    'ad_name': ad.get('name'),
                    'error': str(e),
                    'traceback': traceback.format_exc()
                })

        return {'results': results}
    except Exception as e:
        return {'error': str(e), 'traceback': traceback.format_exc()}

@app.get("/api/debug/conversion-tracking")
async def debug_conversion_tracking():
    """Check conversion tracking setup."""
    try:
        from facebook_business.adobjects.adspixel import AdsPixel
        from facebook_business.adobjects.customconversion import CustomConversion
        client, _, _, _, _ = get_clients()

        result = {
            'pixels': [],
            'custom_conversions': [],
            'campaigns': [],
            'adsets': []
        }

        # Get pixels
        try:
            pixels = client.ad_account.get_ads_pixels(
                fields=['name', 'code', 'is_created_by_business', 'last_fired_time']
            )
            for pixel in pixels:
                result['pixels'].append({
                    'id': pixel.get('id'),
                    'name': pixel.get('name'),
                    'last_fired': pixel.get('last_fired_time'),
                    'created_by_business': pixel.get('is_created_by_business')
                })
        except Exception as e:
            result['pixels_error'] = str(e)

        # Get custom conversions
        try:
            conversions = client.ad_account.get_custom_conversions(
                fields=['name', 'pixel', 'rule', 'event_source_type']
            )
            for conv in conversions:
                result['custom_conversions'].append({
                    'id': conv.get('id'),
                    'name': conv.get('name'),
                    'pixel_id': conv.get('pixel', {}).get('id'),
                    'event_source': conv.get('event_source_type')
                })
        except Exception as e:
            result['custom_conversions_error'] = str(e)

        # Check campaign objectives
        try:
            campaigns = client.get_campaigns()
            for campaign in campaigns[:10]:
                result['campaigns'].append({
                    'id': campaign.get('id'),
                    'name': campaign.get('name'),
                    'objective': campaign.get('objective'),
                    'status': campaign.get('status')
                })
        except Exception as e:
            result['campaigns_error'] = str(e)

        # Check ad set optimization goals
        try:
            adsets = client.get_adsets()
            for adset in list(adsets)[:10]:
                result['adsets'].append({
                    'id': adset.get('id'),
                    'name': adset.get('name'),
                    'optimization_goal': adset.get('optimization_goal'),
                    'status': adset.get('status')
                })
        except Exception as e:
            result['adsets_error'] = str(e)

        return result
    except Exception as e:
        return {'error': str(e), 'traceback': traceback.format_exc()}

@app.get("/api/debug/stats-summary")
async def debug_stats_summary():
    """Get a summary of all campaign/ad stats to debug discrepancies."""
    try:
        client, campaign_manager, _, _, _ = get_clients()

        # Get all campaigns with insights
        campaigns = campaign_manager.list_campaigns(include_insights=True)

        summary = []
        for campaign in campaigns:
            campaign_spend = campaign.get('insights', {}).get('spend', 0)
            campaign_impressions = campaign.get('insights', {}).get('impressions', 0)

            # Get all ads in this campaign
            ads = client.ad_account.get_ads(
                params={'campaign_id': campaign['id']},
                fields=['id', 'name', 'status', 'insights{spend,impressions,clicks}']
            )

            ads_total_spend = 0
            ads_total_impressions = 0
            ads_list = []

            for ad in ads:
                ad_dict = dict(ad)
                insights = ad_dict.get('insights', {}).get('data', [])
                ad_spend = 0
                ad_impressions = 0

                if insights:
                    ad_spend = float(insights[0].get('spend', 0))
                    ad_impressions = int(insights[0].get('impressions', 0))

                ads_total_spend += ad_spend
                ads_total_impressions += ad_impressions

                ads_list.append({
                    'id': ad_dict.get('id'),
                    'name': ad_dict.get('name'),
                    'status': ad_dict.get('status'),
                    'spend': ad_spend,
                    'impressions': ad_impressions
                })

            summary.append({
                'campaign_id': campaign['id'],
                'campaign_name': campaign['name'],
                'campaign_status': campaign['status'],
                'campaign_spend': float(campaign_spend),
                'campaign_impressions': int(campaign_impressions),
                'ads_total_spend': round(ads_total_spend, 2),
                'ads_total_impressions': ads_total_impressions,
                'discrepancy_spend': round(float(campaign_spend) - ads_total_spend, 2),
                'discrepancy_impressions': int(campaign_impressions) - ads_total_impressions,
                'ads_count': len(ads_list),
                'ads': ads_list
            })

        return {
            'summary': summary,
            'total_campaigns': len(summary)
        }

    except Exception as e:
        logger.error(f"Debug stats error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


# Conversion Tracking Endpoints

@app.post("/api/conversions/track")
async def track_conversion(
    event_name: str = Form(...),
    user_email: Optional[str] = Form(None),
    value: Optional[float] = Form(None),
    currency: str = Form("USD"),
    event_source_url: Optional[str] = Form(None),
    content_name: Optional[str] = Form(None),
    content_ids: Optional[str] = Form(None),
    num_items: Optional[int] = Form(None),
    test_event_code: Optional[str] = Form(None)
):
    """
    Track a conversion event via Conversions API.

    This endpoint allows you to send conversion events from your server/webhook.
    Useful for tracking purchases, leads, registrations, etc.
    """
    try:
        client = get_client()
        config = client.config

        # Check if pixel_id is configured
        pixel_id = config.get('facebook', {}).get('pixel_id')
        if not pixel_id:
            raise HTTPException(
                status_code=400,
                detail="Pixel ID not configured. Add pixel_id to config/config.yaml"
            )

        # Initialize tracker
        tracker = ConversionTracker(
            access_token=config['facebook']['access_token'],
            pixel_id=pixel_id
        )

        # Parse content_ids if provided
        content_ids_list = None
        if content_ids:
            content_ids_list = [id.strip() for id in content_ids.split(',')]

        # Track the event
        result = tracker.track_event(
            event_name=event_name,
            user_email=user_email,
            value=value,
            currency=currency,
            event_source_url=event_source_url,
            content_name=content_name,
            content_ids=content_ids_list,
            num_items=num_items,
            test_event_code=test_event_code
        )

        if result['success']:
            return {
                "success": True,
                "event_name": event_name,
                "message": "Event tracked successfully"
            }
        else:
            raise HTTPException(status_code=500, detail=result.get('error', 'Unknown error'))

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Conversion tracking error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/conversions/purchase")
async def track_purchase(
    user_email: str = Form(...),
    value: float = Form(...),
    currency: str = Form("USD"),
    product_ids: Optional[str] = Form(None),
    num_items: Optional[int] = Form(None)
):
    """Track a purchase/transaction event."""
    try:
        client = get_client()
        config = client.config

        pixel_id = config.get('facebook', {}).get('pixel_id')
        if not pixel_id:
            raise HTTPException(status_code=400, detail="Pixel ID not configured")

        tracker = ConversionTracker(
            access_token=config['facebook']['access_token'],
            pixel_id=pixel_id
        )

        content_ids = None
        if product_ids:
            content_ids = [id.strip() for id in product_ids.split(',')]

        result = tracker.track_purchase(
            user_email=user_email,
            value=value,
            currency=currency,
            content_ids=content_ids,
            num_items=num_items
        )

        if result['success']:
            return {
                "success": True,
                "event_name": "Purchase",
                "value": value,
                "currency": currency
            }
        else:
            raise HTTPException(status_code=500, detail=result.get('error'))

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Purchase tracking error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/conversions/lead")
async def track_lead(
    user_email: str = Form(...),
    value: Optional[float] = Form(None),
    content_name: Optional[str] = Form(None)
):
    """Track a lead generation event."""
    try:
        client = get_client()
        config = client.config

        pixel_id = config.get('facebook', {}).get('pixel_id')
        if not pixel_id:
            raise HTTPException(status_code=400, detail="Pixel ID not configured")

        tracker = ConversionTracker(
            access_token=config['facebook']['access_token'],
            pixel_id=pixel_id
        )

        result = tracker.track_lead(
            user_email=user_email,
            value=value,
            content_name=content_name
        )

        if result['success']:
            return {
                "success": True,
                "event_name": "Lead",
                "email": user_email
            }
        else:
            raise HTTPException(status_code=500, detail=result.get('error'))

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Lead tracking error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/conversions/registration")
async def track_registration(
    user_email: str = Form(...),
    user_first_name: Optional[str] = Form(None),
    user_last_name: Optional[str] = Form(None)
):
    """Track a user registration/signup event."""
    try:
        client = get_client()
        config = client.config

        pixel_id = config.get('facebook', {}).get('pixel_id')
        if not pixel_id:
            raise HTTPException(status_code=400, detail="Pixel ID not configured")

        tracker = ConversionTracker(
            access_token=config['facebook']['access_token'],
            pixel_id=pixel_id
        )

        result = tracker.track_registration(
            user_email=user_email,
            user_first_name=user_first_name,
            user_last_name=user_last_name
        )

        if result['success']:
            return {
                "success": True,
                "event_name": "CompleteRegistration",
                "email": user_email
            }
        else:
            raise HTTPException(status_code=500, detail=result.get('error'))

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration tracking error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/conversions/events")
async def list_conversion_events():
    """Get list of standard Facebook conversion event types."""
    try:
        events = ConversionTracker.STANDARD_EVENTS
        return {
            "events": [
                {"name": name, "description": desc}
                for name, desc in events.items()
            ]
        }
    except Exception as e:
        logger.error(f"Error listing events: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
