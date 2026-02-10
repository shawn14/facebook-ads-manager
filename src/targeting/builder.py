"""Audience targeting builder for Facebook Ads."""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from loguru import logger


class Gender(Enum):
    """Gender targeting options."""
    ALL = 0
    MALE = 1
    FEMALE = 2


class DeviceType(Enum):
    """Device platform targeting."""
    MOBILE = "mobile"
    DESKTOP = "desktop"
    ALL = "all"


class AudienceType(Enum):
    """Audience type classifications."""
    BROAD = "broad"
    INTEREST = "interest"
    BEHAVIORAL = "behavioral"
    DEMOGRAPHIC = "demographic"
    CUSTOM = "custom"
    LOOKALIKE = "lookalike"


@dataclass
class Location:
    """Geographic location targeting."""
    countries: List[str] = field(default_factory=list)
    regions: List[Dict[str, Any]] = field(default_factory=list)
    cities: List[Dict[str, Any]] = field(default_factory=list)
    zips: List[Dict[str, Any]] = field(default_factory=list)
    geo_markets: List[Dict[str, Any]] = field(default_factory=list)
    location_types: List[str] = field(default_factory=lambda: ["home"])


@dataclass
class Demographics:
    """Demographic targeting parameters."""
    age_min: int = 18
    age_max: int = 65
    genders: List[Gender] = field(default_factory=lambda: [Gender.ALL])
    relationship_statuses: List[int] = field(default_factory=list)
    interested_in: List[int] = field(default_factory=list)
    education_statuses: List[int] = field(default_factory=list)
    education_schools: List[Dict[str, Any]] = field(default_factory=list)
    work_employers: List[Dict[str, Any]] = field(default_factory=list)
    work_positions: List[Dict[str, Any]] = field(default_factory=list)
    income: List[Dict[str, Any]] = field(default_factory=list)
    generation: List[int] = field(default_factory=list)
    home_ownership: List[int] = field(default_factory=list)
    home_type: List[int] = field(default_factory=list)
    home_value: List[int] = field(default_factory=list)
    ethnic_affinity: List[int] = field(default_factory=list)
    life_events: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class Interests:
    """Interest-based targeting."""
    interests: List[Dict[str, Any]] = field(default_factory=list)
    behaviors: List[Dict[str, Any]] = field(default_factory=list)
    work_industries: List[Dict[str, Any]] = field(default_factory=list)


class TargetingBuilder:
    """Builder for constructing Facebook ad targeting specifications."""

    def __init__(self):
        """Initialize targeting builder."""
        self.location = Location()
        self.demographics = Demographics()
        self.interests = Interests()
        self.custom_audiences: List[str] = []
        self.excluded_custom_audiences: List[str] = []
        self.connections: List[Dict[str, Any]] = []
        self.excluded_connections: List[Dict[str, Any]] = []
        self.device_platforms: List[str] = []
        self.publisher_platforms: List[str] = ["facebook"]
        self.facebook_positions: List[str] = ["feed"]
        self.flexible_spec: List[Dict[str, Any]] = []

    # Location Targeting Methods

    def add_countries(self, countries: List[str]) -> 'TargetingBuilder':
        """Add country targeting.

        Args:
            countries: List of country codes (e.g., ['US', 'CA', 'GB'])

        Returns:
            Self for method chaining
        """
        self.location.countries.extend(countries)
        logger.debug(f"Added country targeting: {countries}")
        return self

    def add_regions(
        self,
        regions: List[Dict[str, Any]]
    ) -> 'TargetingBuilder':
        """Add region/state targeting.

        Args:
            regions: List of region dicts with 'key' (e.g., [{'key': '3847'}])

        Returns:
            Self for method chaining
        """
        self.location.regions.extend(regions)
        logger.debug(f"Added region targeting: {len(regions)} regions")
        return self

    def add_cities(
        self,
        cities: List[Dict[str, Any]]
    ) -> 'TargetingBuilder':
        """Add city targeting.

        Args:
            cities: List of city dicts with 'key', 'radius', 'distance_unit'

        Returns:
            Self for method chaining

        Example:
            builder.add_cities([
                {'key': '2418779', 'radius': 10, 'distance_unit': 'mile'}
            ])
        """
        self.location.cities.extend(cities)
        logger.debug(f"Added city targeting: {len(cities)} cities")
        return self

    def add_zip_codes(
        self,
        zips: List[str],
        country: str = 'US'
    ) -> 'TargetingBuilder':
        """Add ZIP code targeting.

        Args:
            zips: List of ZIP codes
            country: Country code

        Returns:
            Self for method chaining
        """
        zip_dicts = [{'key': f'{country}:{zip_code}'} for zip_code in zips]
        self.location.zips.extend(zip_dicts)
        logger.debug(f"Added {len(zips)} ZIP codes")
        return self

    def set_location_types(
        self,
        types: List[str]
    ) -> 'TargetingBuilder':
        """Set location types (home, recent, travel).

        Args:
            types: List of location types

        Returns:
            Self for method chaining
        """
        valid_types = ["home", "recent", "travel_in"]
        for t in types:
            if t not in valid_types:
                logger.warning(f"Invalid location type: {t}")

        self.location.location_types = types
        return self

    # Demographic Targeting Methods

    def set_age_range(
        self,
        min_age: int = 18,
        max_age: int = 65
    ) -> 'TargetingBuilder':
        """Set age range targeting.

        Args:
            min_age: Minimum age (18-65)
            max_age: Maximum age (18-65)

        Returns:
            Self for method chaining
        """
        if min_age < 18:
            logger.warning("Minimum age must be 18+, setting to 18")
            min_age = 18

        if max_age > 65:
            logger.warning("Maximum age cannot exceed 65, setting to 65")
            max_age = 65

        self.demographics.age_min = min_age
        self.demographics.age_max = max_age
        logger.debug(f"Set age range: {min_age}-{max_age}")
        return self

    def set_genders(
        self,
        genders: List[Gender]
    ) -> 'TargetingBuilder':
        """Set gender targeting.

        Args:
            genders: List of Gender enum values

        Returns:
            Self for method chaining
        """
        self.demographics.genders = genders
        logger.debug(f"Set gender targeting: {[g.name for g in genders]}")
        return self

    def add_relationship_statuses(
        self,
        statuses: List[int]
    ) -> 'TargetingBuilder':
        """Add relationship status targeting.

        Args:
            statuses: List of status codes (1=Single, 2=In a relationship, etc.)

        Returns:
            Self for method chaining
        """
        self.demographics.relationship_statuses.extend(statuses)
        return self

    def add_education_levels(
        self,
        levels: List[int]
    ) -> 'TargetingBuilder':
        """Add education level targeting.

        Args:
            levels: List of education status codes

        Returns:
            Self for method chaining
        """
        self.demographics.education_statuses.extend(levels)
        return self

    def add_employers(
        self,
        employers: List[Dict[str, Any]]
    ) -> 'TargetingBuilder':
        """Add employer targeting.

        Args:
            employers: List of employer dicts with 'id' and 'name'

        Returns:
            Self for method chaining
        """
        self.demographics.work_employers.extend(employers)
        return self

    def add_job_titles(
        self,
        titles: List[Dict[str, Any]]
    ) -> 'TargetingBuilder':
        """Add job title targeting.

        Args:
            titles: List of job title dicts with 'id' and 'name'

        Returns:
            Self for method chaining
        """
        self.demographics.work_positions.extend(titles)
        return self

    def add_life_events(
        self,
        events: List[Dict[str, Any]]
    ) -> 'TargetingBuilder':
        """Add life event targeting.

        Args:
            events: List of life event dicts

        Returns:
            Self for method chaining
        """
        self.demographics.life_events.extend(events)
        return self

    # Interest & Behavior Targeting Methods

    def add_interests(
        self,
        interests: List[Dict[str, Any]]
    ) -> 'TargetingBuilder':
        """Add interest targeting.

        Args:
            interests: List of interest dicts with 'id' and 'name'

        Returns:
            Self for method chaining

        Example:
            builder.add_interests([
                {'id': '6003139266461', 'name': 'Online shopping'}
            ])
        """
        self.interests.interests.extend(interests)
        logger.debug(f"Added {len(interests)} interests")
        return self

    def add_behaviors(
        self,
        behaviors: List[Dict[str, Any]]
    ) -> 'TargetingBuilder':
        """Add behavior targeting.

        Args:
            behaviors: List of behavior dicts with 'id' and 'name'

        Returns:
            Self for method chaining
        """
        self.interests.behaviors.extend(behaviors)
        logger.debug(f"Added {len(behaviors)} behaviors")
        return self

    def add_industries(
        self,
        industries: List[Dict[str, Any]]
    ) -> 'TargetingBuilder':
        """Add industry targeting.

        Args:
            industries: List of industry dicts

        Returns:
            Self for method chaining
        """
        self.interests.work_industries.extend(industries)
        return self

    # Custom Audience Methods

    def add_custom_audiences(
        self,
        audience_ids: List[str]
    ) -> 'TargetingBuilder':
        """Add custom audiences to targeting.

        Args:
            audience_ids: List of custom audience IDs

        Returns:
            Self for method chaining
        """
        self.custom_audiences.extend(audience_ids)
        logger.debug(f"Added {len(audience_ids)} custom audiences")
        return self

    def exclude_custom_audiences(
        self,
        audience_ids: List[str]
    ) -> 'TargetingBuilder':
        """Exclude custom audiences from targeting.

        Args:
            audience_ids: List of custom audience IDs to exclude

        Returns:
            Self for method chaining
        """
        self.excluded_custom_audiences.extend(audience_ids)
        logger.debug(f"Excluded {len(audience_ids)} custom audiences")
        return self

    # Connection Targeting Methods

    def add_page_connections(
        self,
        page_ids: List[str]
    ) -> 'TargetingBuilder':
        """Target people connected to specific pages.

        Args:
            page_ids: List of Facebook page IDs

        Returns:
            Self for method chaining
        """
        for page_id in page_ids:
            self.connections.append({'id': page_id, 'type': 'page'})
        return self

    def exclude_page_connections(
        self,
        page_ids: List[str]
    ) -> 'TargetingBuilder':
        """Exclude people connected to specific pages.

        Args:
            page_ids: List of Facebook page IDs to exclude

        Returns:
            Self for method chaining
        """
        for page_id in page_ids:
            self.excluded_connections.append({'id': page_id, 'type': 'page'})
        return self

    # Device & Platform Targeting

    def set_device_platforms(
        self,
        devices: List[DeviceType]
    ) -> 'TargetingBuilder':
        """Set device platform targeting.

        Args:
            devices: List of DeviceType enum values

        Returns:
            Self for method chaining
        """
        self.device_platforms = [d.value for d in devices]
        logger.debug(f"Set device platforms: {self.device_platforms}")
        return self

    def set_publisher_platforms(
        self,
        platforms: List[str]
    ) -> 'TargetingBuilder':
        """Set publisher platforms (facebook, instagram, audience_network, messenger).

        Args:
            platforms: List of platform names

        Returns:
            Self for method chaining
        """
        valid_platforms = ["facebook", "instagram", "audience_network", "messenger"]
        self.publisher_platforms = [p for p in platforms if p in valid_platforms]
        logger.debug(f"Set publisher platforms: {self.publisher_platforms}")
        return self

    def set_facebook_positions(
        self,
        positions: List[str]
    ) -> 'TargetingBuilder':
        """Set Facebook ad positions.

        Args:
            positions: List of positions (feed, right_hand_column, instant_article, etc.)

        Returns:
            Self for method chaining
        """
        self.facebook_positions = positions
        return self

    # Flexible Spec (Advanced Targeting)

    def add_flexible_spec(
        self,
        spec: Dict[str, Any]
    ) -> 'TargetingBuilder':
        """Add flexible spec for OR/AND logic in targeting.

        Args:
            spec: Flexible spec dictionary

        Returns:
            Self for method chaining

        Example:
            # Target people interested in tech OR fitness
            builder.add_flexible_spec({
                'interests': [
                    {'id': '123', 'name': 'Technology'},
                    {'id': '456', 'name': 'Fitness'}
                ]
            })
        """
        self.flexible_spec.append(spec)
        return self

    # Build Methods

    def build(self) -> Dict[str, Any]:
        """Build the complete targeting specification.

        Returns:
            Dictionary with Facebook Ads API targeting format
        """
        targeting = {}

        # Add location targeting
        if self.location.countries or self.location.regions or self.location.cities:
            geo_locations = {}

            if self.location.countries:
                geo_locations['countries'] = self.location.countries

            if self.location.regions:
                geo_locations['regions'] = self.location.regions

            if self.location.cities:
                geo_locations['cities'] = self.location.cities

            if self.location.zips:
                geo_locations['zips'] = self.location.zips

            if self.location.geo_markets:
                geo_locations['geo_markets'] = self.location.geo_markets

            if self.location.location_types:
                geo_locations['location_types'] = self.location.location_types

            targeting['geo_locations'] = geo_locations

        # Add demographics
        targeting['age_min'] = self.demographics.age_min
        targeting['age_max'] = self.demographics.age_max

        if Gender.ALL not in self.demographics.genders:
            gender_values = [g.value for g in self.demographics.genders]
            targeting['genders'] = gender_values

        if self.demographics.relationship_statuses:
            targeting['relationship_statuses'] = self.demographics.relationship_statuses

        if self.demographics.interested_in:
            targeting['interested_in'] = self.demographics.interested_in

        if self.demographics.education_statuses:
            targeting['education_statuses'] = self.demographics.education_statuses

        if self.demographics.work_employers:
            targeting['work_employers'] = self.demographics.work_employers

        if self.demographics.work_positions:
            targeting['work_positions'] = self.demographics.work_positions

        if self.demographics.life_events:
            targeting['life_events'] = self.demographics.life_events

        # Add interests and behaviors
        if self.interests.interests:
            targeting['interests'] = self.interests.interests

        if self.interests.behaviors:
            targeting['behaviors'] = self.interests.behaviors

        if self.interests.work_industries:
            targeting['industries'] = self.interests.work_industries

        # Add custom audiences
        if self.custom_audiences:
            targeting['custom_audiences'] = [
                {'id': audience_id} for audience_id in self.custom_audiences
            ]

        if self.excluded_custom_audiences:
            targeting['excluded_custom_audiences'] = [
                {'id': audience_id} for audience_id in self.excluded_custom_audiences
            ]

        # Add connections
        if self.connections:
            targeting['connections'] = self.connections

        if self.excluded_connections:
            targeting['excluded_connections'] = self.excluded_connections

        # Add device platforms
        if self.device_platforms:
            targeting['device_platforms'] = self.device_platforms

        # Add publisher platforms
        if self.publisher_platforms:
            targeting['publisher_platforms'] = self.publisher_platforms
            targeting['facebook_positions'] = self.facebook_positions

        # Add flexible spec
        if self.flexible_spec:
            targeting['flexible_spec'] = self.flexible_spec

        logger.info("Built targeting specification")
        return targeting

    def reset(self) -> 'TargetingBuilder':
        """Reset the builder to start fresh.

        Returns:
            Self for method chaining
        """
        self.__init__()
        logger.debug("Reset targeting builder")
        return self

    # Preset Methods

    @classmethod
    def create_broad_audience(
        cls,
        countries: List[str],
        age_min: int = 18,
        age_max: int = 65
    ) -> 'TargetingBuilder':
        """Create a broad audience targeting.

        Args:
            countries: List of country codes
            age_min: Minimum age
            age_max: Maximum age

        Returns:
            Configured TargetingBuilder
        """
        builder = cls()
        builder.add_countries(countries)
        builder.set_age_range(age_min, age_max)
        logger.info(f"Created broad audience for {countries}")
        return builder

    @classmethod
    def create_lookalike_audience(
        cls,
        countries: List[str],
        lookalike_audience_id: str,
        age_min: int = 18,
        age_max: int = 65
    ) -> 'TargetingBuilder':
        """Create targeting for a lookalike audience.

        Args:
            countries: List of country codes
            lookalike_audience_id: ID of the lookalike audience
            age_min: Minimum age
            age_max: Maximum age

        Returns:
            Configured TargetingBuilder
        """
        builder = cls()
        builder.add_countries(countries)
        builder.set_age_range(age_min, age_max)
        builder.add_custom_audiences([lookalike_audience_id])
        logger.info(f"Created lookalike audience targeting")
        return builder

    @classmethod
    def create_retargeting_audience(
        cls,
        countries: List[str],
        custom_audience_id: str,
        exclude_converted: Optional[str] = None
    ) -> 'TargetingBuilder':
        """Create retargeting audience.

        Args:
            countries: List of country codes
            custom_audience_id: ID of the custom audience to target
            exclude_converted: Optional ID of converted audience to exclude

        Returns:
            Configured TargetingBuilder
        """
        builder = cls()
        builder.add_countries(countries)
        builder.add_custom_audiences([custom_audience_id])

        if exclude_converted:
            builder.exclude_custom_audiences([exclude_converted])

        logger.info("Created retargeting audience")
        return builder

    # Validation

    def validate(self) -> bool:
        """Validate the targeting specification.

        Returns:
            True if valid

        Raises:
            ValueError: If targeting is invalid
        """
        if not self.location.countries and not self.location.cities and not self.location.regions:
            raise ValueError("At least one location target is required")

        if self.demographics.age_min < 18 or self.demographics.age_max > 65:
            raise ValueError("Age range must be between 18 and 65")

        if self.demographics.age_min > self.demographics.age_max:
            raise ValueError("Minimum age cannot be greater than maximum age")

        logger.info("Targeting specification validated successfully")
        return True

    def get_estimated_audience_size(self) -> str:
        """Get estimated audience size (placeholder - requires API call).

        Returns:
            Estimated size message
        """
        # This would require an API call to get real estimates
        logger.warning("Audience size estimation requires API integration")
        return "Estimation requires API call to Facebook"

    def to_dict(self) -> Dict[str, Any]:
        """Convert targeting to dictionary format.

        Returns:
            Dictionary representation
        """
        return self.build()
