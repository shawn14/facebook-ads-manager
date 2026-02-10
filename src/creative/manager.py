"""Creative manager for handling ad creatives, images, and videos."""

from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
from loguru import logger
import mimetypes


class CreativeType(Enum):
    """Ad creative types."""
    IMAGE = "image"
    VIDEO = "video"
    CAROUSEL = "carousel"


class CallToActionType(Enum):
    """Call-to-action button types."""
    LEARN_MORE = "LEARN_MORE"
    SHOP_NOW = "SHOP_NOW"
    SIGN_UP = "SIGN_UP"
    DOWNLOAD = "DOWNLOAD"
    BOOK_NOW = "BOOK_NOW"
    GET_QUOTE = "GET_QUOTE"
    APPLY_NOW = "APPLY_NOW"
    SUBSCRIBE = "SUBSCRIBE"
    CONTACT_US = "CONTACT_US"
    CALL_NOW = "CALL_NOW"


@dataclass
class CreativeAsset:
    """Represents an uploaded creative asset."""
    asset_id: str
    asset_type: str  # 'image' or 'video'
    name: Optional[str] = None
    hash: Optional[str] = None
    url: Optional[str] = None


@dataclass
class CarouselCard:
    """Represents a carousel card."""
    name: str
    image_hash: str
    link: str
    description: Optional[str] = None


class CreativeManager:
    """Manager for ad creative operations."""

    def __init__(self, api_client):
        """Initialize creative manager.

        Args:
            api_client: FacebookAdsClient instance
        """
        self.api_client = api_client
        self._asset_cache: Dict[str, CreativeAsset] = {}

    # Asset Upload Methods

    def upload_asset(
        self,
        file_path: str,
        name: Optional[str] = None,
        description: Optional[str] = None
    ) -> CreativeAsset:
        """Upload an image or video asset automatically detecting type.

        Args:
            file_path: Path to the asset file
            name: Optional asset name
            description: Optional description (for videos)

        Returns:
            CreativeAsset object

        Raises:
            ValueError: If file type is not supported
            FileNotFoundError: If file doesn't exist
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Asset file not found: {file_path}")

        # Detect file type
        mime_type, _ = mimetypes.guess_type(str(path))
        if not mime_type:
            raise ValueError(f"Could not determine file type for: {file_path}")

        if mime_type.startswith('image/'):
            return self.upload_image(file_path, name)
        elif mime_type.startswith('video/'):
            return self.upload_video(file_path, name, description)
        else:
            raise ValueError(f"Unsupported file type: {mime_type}")

    def upload_image(
        self,
        image_path: str,
        name: Optional[str] = None
    ) -> CreativeAsset:
        """Upload an image asset.

        Args:
            image_path: Path to image file
            name: Optional image name

        Returns:
            CreativeAsset object with image hash
        """
        try:
            result = self.api_client.upload_image(image_path, name)
            asset = CreativeAsset(
                asset_id=result.get('hash', ''),
                asset_type='image',
                name=name or Path(image_path).name,
                hash=result.get('hash', ''),
                url=result.get('url')
            )
            self._asset_cache[asset.hash] = asset
            logger.info(f"Uploaded image asset: {asset.name} (hash: {asset.hash})")
            return asset
        except Exception as e:
            logger.error(f"Failed to upload image {image_path}: {e}")
            raise

    def upload_video(
        self,
        video_path: str,
        name: Optional[str] = None,
        description: Optional[str] = None
    ) -> CreativeAsset:
        """Upload a video asset.

        Args:
            video_path: Path to video file
            name: Optional video name
            description: Optional description

        Returns:
            CreativeAsset object with video ID
        """
        try:
            result = self.api_client.upload_video(video_path, name, description)
            asset = CreativeAsset(
                asset_id=result['id'],
                asset_type='video',
                name=name or Path(video_path).name
            )
            self._asset_cache[asset.asset_id] = asset
            logger.info(f"Uploaded video asset: {asset.name} (ID: {asset.asset_id})")
            return asset
        except Exception as e:
            logger.error(f"Failed to upload video {video_path}: {e}")
            raise

    def upload_multiple_images(
        self,
        image_paths: List[str],
        name_prefix: Optional[str] = None
    ) -> List[CreativeAsset]:
        """Upload multiple images at once.

        Args:
            image_paths: List of image file paths
            name_prefix: Optional prefix for image names

        Returns:
            List of CreativeAsset objects
        """
        assets = []
        for i, path in enumerate(image_paths):
            name = f"{name_prefix}_{i+1}" if name_prefix else None
            try:
                asset = self.upload_image(path, name)
                assets.append(asset)
            except Exception as e:
                logger.warning(f"Failed to upload {path}: {e}")
                continue

        logger.info(f"Successfully uploaded {len(assets)}/{len(image_paths)} images")
        return assets

    # Creative Creation Methods

    def create_image_ad(
        self,
        name: str,
        image_path: str,
        message: str,
        link: str,
        call_to_action: CallToActionType = CallToActionType.LEARN_MORE,
        caption: Optional[str] = None,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create an image ad creative (upload + create creative).

        Args:
            name: Creative name
            image_path: Path to image file
            message: Primary ad text
            link: Destination URL
            call_to_action: CTA button type
            caption: Link caption
            description: Link description

        Returns:
            Created creative object
        """
        # Upload image
        image_asset = self.upload_image(image_path)

        # Create creative
        creative = self.api_client.create_image_creative(
            name=name,
            image_hash=image_asset.hash,
            message=message,
            link=link,
            call_to_action_type=call_to_action.value,
            caption=caption,
            description=description
        )

        logger.info(f"Created image ad creative: {name} (ID: {creative['id']})")
        return creative

    def create_video_ad(
        self,
        name: str,
        video_path: str,
        message: str,
        link: str,
        call_to_action: CallToActionType = CallToActionType.LEARN_MORE,
        caption: Optional[str] = None,
        description: Optional[str] = None,
        thumbnail_url: Optional[str] = None,
        video_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a video ad creative (upload + create creative).

        Args:
            name: Creative name
            video_path: Path to video file
            message: Primary ad text
            link: Destination URL
            call_to_action: CTA button type
            caption: Link caption
            description: Link description
            thumbnail_url: Custom thumbnail URL
            video_name: Name for the uploaded video

        Returns:
            Created creative object
        """
        # Upload video
        video_asset = self.upload_video(video_path, video_name, description)

        # Create creative
        creative = self.api_client.create_video_creative(
            name=name,
            video_id=video_asset.asset_id,
            message=message,
            link=link,
            call_to_action_type=call_to_action.value,
            caption=caption,
            description=description,
            thumbnail_url=thumbnail_url
        )

        logger.info(f"Created video ad creative: {name} (ID: {creative['id']})")
        return creative

    def create_carousel_ad(
        self,
        name: str,
        message: str,
        cards: List[CarouselCard],
        default_link: str,
        call_to_action: CallToActionType = CallToActionType.LEARN_MORE
    ) -> Dict[str, Any]:
        """Create a carousel ad creative.

        Args:
            name: Creative name
            message: Primary ad text
            cards: List of CarouselCard objects
            default_link: Default destination URL
            call_to_action: CTA button type

        Returns:
            Created creative object
        """
        # Convert CarouselCard objects to dicts
        card_dicts = []
        for card in cards:
            card_dict = {
                'name': card.name,
                'image_hash': card.image_hash,
                'link': card.link
            }
            if card.description:
                card_dict['description'] = card.description
            card_dicts.append(card_dict)

        # Create creative
        creative = self.api_client.create_carousel_creative(
            name=name,
            message=message,
            cards=card_dicts,
            link=default_link,
            call_to_action_type=call_to_action.value
        )

        logger.info(f"Created carousel ad with {len(cards)} cards: {name} (ID: {creative['id']})")
        return creative

    def create_carousel_from_images(
        self,
        name: str,
        message: str,
        image_paths: List[str],
        card_names: List[str],
        card_links: List[str],
        card_descriptions: Optional[List[str]] = None,
        default_link: Optional[str] = None,
        call_to_action: CallToActionType = CallToActionType.LEARN_MORE
    ) -> Dict[str, Any]:
        """Create a carousel ad by uploading images and creating cards.

        Args:
            name: Creative name
            message: Primary ad text
            image_paths: List of image file paths
            card_names: List of card names (must match image_paths length)
            card_links: List of destination URLs (must match image_paths length)
            card_descriptions: Optional list of card descriptions
            default_link: Default destination URL (uses first card_link if not provided)
            call_to_action: CTA button type

        Returns:
            Created creative object

        Raises:
            ValueError: If lists don't have matching lengths
        """
        if not (len(image_paths) == len(card_names) == len(card_links)):
            raise ValueError("image_paths, card_names, and card_links must have the same length")

        if card_descriptions and len(card_descriptions) != len(image_paths):
            raise ValueError("card_descriptions must match image_paths length if provided")

        # Upload images
        image_assets = self.upload_multiple_images(image_paths)

        if len(image_assets) != len(image_paths):
            logger.warning(f"Only {len(image_assets)}/{len(image_paths)} images uploaded successfully")

        # Create carousel cards
        cards = []
        for i, asset in enumerate(image_assets):
            card = CarouselCard(
                name=card_names[i],
                image_hash=asset.hash,
                link=card_links[i],
                description=card_descriptions[i] if card_descriptions else None
            )
            cards.append(card)

        # Create carousel creative
        return self.create_carousel_ad(
            name=name,
            message=message,
            cards=cards,
            default_link=default_link or card_links[0],
            call_to_action=call_to_action
        )

    # Creative Management Methods

    def list_creatives(
        self,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """List all creatives in the ad account.

        Args:
            limit: Maximum number of creatives to return

        Returns:
            List of creative objects
        """
        try:
            creatives = self.api_client.get_creatives(limit=limit)
            logger.info(f"Retrieved {len(creatives)} creatives")
            return [dict(creative) for creative in creatives]
        except Exception as e:
            logger.error(f"Failed to list creatives: {e}")
            raise

    def get_creative(
        self,
        creative_id: str
    ) -> Dict[str, Any]:
        """Get details of a specific creative.

        Args:
            creative_id: Creative ID

        Returns:
            Creative object
        """
        try:
            creative = self.api_client.get_creative(creative_id)
            return dict(creative)
        except Exception as e:
            logger.error(f"Failed to get creative {creative_id}: {e}")
            raise

    def preview_creative(
        self,
        creative_id: str,
        format: str = "DESKTOP_FEED_STANDARD"
    ) -> str:
        """Get HTML preview of a creative.

        Args:
            creative_id: Creative ID
            format: Preview format (DESKTOP_FEED_STANDARD, MOBILE_FEED_STANDARD, etc.)

        Returns:
            HTML preview string
        """
        try:
            preview = self.api_client.get_ad_preview(creative_id, format)
            logger.info(f"Generated preview for creative {creative_id}")
            return preview
        except Exception as e:
            logger.error(f"Failed to preview creative {creative_id}: {e}")
            raise

    # Ad Creation with Creatives

    def create_complete_ad(
        self,
        adset_id: str,
        ad_name: str,
        creative_name: str,
        creative_type: CreativeType,
        message: str,
        link: str,
        asset_path: str,
        call_to_action: CallToActionType = CallToActionType.LEARN_MORE,
        caption: Optional[str] = None,
        description: Optional[str] = None,
        status: str = "PAUSED"
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Create a complete ad with creative in one step.

        Args:
            adset_id: Parent ad set ID
            ad_name: Ad name
            creative_name: Creative name
            creative_type: Type of creative (IMAGE or VIDEO)
            message: Primary ad text
            link: Destination URL
            asset_path: Path to image or video file
            call_to_action: CTA button type
            caption: Link caption
            description: Link description
            status: Ad status (ACTIVE, PAUSED)

        Returns:
            Tuple of (creative_object, ad_object)
        """
        # Create creative based on type
        if creative_type == CreativeType.IMAGE:
            creative = self.create_image_ad(
                name=creative_name,
                image_path=asset_path,
                message=message,
                link=link,
                call_to_action=call_to_action,
                caption=caption,
                description=description
            )
        elif creative_type == CreativeType.VIDEO:
            creative = self.create_video_ad(
                name=creative_name,
                video_path=asset_path,
                message=message,
                link=link,
                call_to_action=call_to_action,
                caption=caption,
                description=description
            )
        else:
            raise ValueError(f"Unsupported creative type: {creative_type}")

        # Create ad with creative
        ad = self.api_client.create_ad(
            adset_id=adset_id,
            creative_id=creative['id'],
            name=ad_name,
            status=status
        )

        logger.info(f"Created complete ad: {ad_name} with creative {creative_name}")
        return creative, dict(ad)

    # Utility Methods

    def validate_image(
        self,
        image_path: str,
        max_size_mb: int = 30,
        allowed_formats: Optional[List[str]] = None
    ) -> bool:
        """Validate image file before upload.

        Args:
            image_path: Path to image file
            max_size_mb: Maximum file size in MB
            allowed_formats: List of allowed extensions (default: jpg, jpeg, png, gif)

        Returns:
            True if valid

        Raises:
            ValueError: If image is invalid
        """
        path = Path(image_path)
        if not path.exists():
            raise ValueError(f"Image file not found: {image_path}")

        # Check file size
        size_mb = path.stat().st_size / (1024 * 1024)
        if size_mb > max_size_mb:
            raise ValueError(f"Image too large: {size_mb:.2f}MB (max: {max_size_mb}MB)")

        # Check format
        if allowed_formats is None:
            allowed_formats = ['.jpg', '.jpeg', '.png', '.gif']

        if path.suffix.lower() not in allowed_formats:
            raise ValueError(f"Invalid image format: {path.suffix} (allowed: {allowed_formats})")

        return True

    def validate_video(
        self,
        video_path: str,
        max_size_mb: int = 4096,
        allowed_formats: Optional[List[str]] = None
    ) -> bool:
        """Validate video file before upload.

        Args:
            video_path: Path to video file
            max_size_mb: Maximum file size in MB
            allowed_formats: List of allowed extensions (default: mp4, mov, avi)

        Returns:
            True if valid

        Raises:
            ValueError: If video is invalid
        """
        path = Path(video_path)
        if not path.exists():
            raise ValueError(f"Video file not found: {video_path}")

        # Check file size
        size_mb = path.stat().st_size / (1024 * 1024)
        if size_mb > max_size_mb:
            raise ValueError(f"Video too large: {size_mb:.2f}MB (max: {max_size_mb}MB)")

        # Check format
        if allowed_formats is None:
            allowed_formats = ['.mp4', '.mov', '.avi']

        if path.suffix.lower() not in allowed_formats:
            raise ValueError(f"Invalid video format: {path.suffix} (allowed: {allowed_formats})")

        return True

    def clear_asset_cache(self):
        """Clear the internal asset cache."""
        self._asset_cache.clear()
        logger.info("Cleared asset cache")
