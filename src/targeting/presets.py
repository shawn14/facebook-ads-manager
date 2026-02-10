"""Pre-configured targeting presets for common use cases."""

from typing import List, Dict, Any
from .builder import TargetingBuilder, Gender


class TargetingPresets:
    """Common targeting presets for different business types and objectives."""

    @staticmethod
    def ecommerce_general(
        countries: List[str] = ['US'],
        age_min: int = 25,
        age_max: int = 54
    ) -> TargetingBuilder:
        """General e-commerce audience.

        Args:
            countries: Target countries
            age_min: Minimum age
            age_max: Maximum age

        Returns:
            Configured TargetingBuilder
        """
        builder = TargetingBuilder()
        builder.add_countries(countries)
        builder.set_age_range(age_min, age_max)
        builder.add_interests([
            {'id': '6003139266461', 'name': 'Online shopping'}
        ])
        builder.add_behaviors([
            {'id': '6002714895372', 'name': 'Engaged Shoppers'}
        ])
        return builder

    @staticmethod
    def fashion_shoppers(
        countries: List[str] = ['US'],
        gender: Gender = Gender.FEMALE,
        age_min: int = 18,
        age_max: int = 44
    ) -> TargetingBuilder:
        """Fashion and apparel shoppers.

        Args:
            countries: Target countries
            gender: Target gender
            age_min: Minimum age
            age_max: Maximum age

        Returns:
            Configured TargetingBuilder
        """
        builder = TargetingBuilder()
        builder.add_countries(countries)
        builder.set_genders([gender])
        builder.set_age_range(age_min, age_max)
        builder.add_interests([
            {'id': '6003020834693', 'name': 'Fashion'},
            {'id': '6003020834793', 'name': 'Shopping'}
        ])
        return builder

    @staticmethod
    def tech_enthusiasts(
        countries: List[str] = ['US'],
        age_min: int = 21,
        age_max: int = 45
    ) -> TargetingBuilder:
        """Tech enthusiasts and early adopters.

        Args:
            countries: Target countries
            age_min: Minimum age
            age_max: Maximum age

        Returns:
            Configured TargetingBuilder
        """
        builder = TargetingBuilder()
        builder.add_countries(countries)
        builder.set_age_range(age_min, age_max)
        builder.add_interests([
            {'id': '6003139266461', 'name': 'Technology'},
            {'id': '6003020834893', 'name': 'Consumer electronics'},
            {'id': '6003397425735', 'name': 'Early adopters'}
        ])
        return builder

    @staticmethod
    def fitness_health(
        countries: List[str] = ['US'],
        age_min: int = 22,
        age_max: int = 50
    ) -> TargetingBuilder:
        """Fitness and health-conscious audience.

        Args:
            countries: Target countries
            age_min: Minimum age
            age_max: Maximum age

        Returns:
            Configured TargetingBuilder
        """
        builder = TargetingBuilder()
        builder.add_countries(countries)
        builder.set_age_range(age_min, age_max)
        builder.add_interests([
            {'id': '6003139266461', 'name': 'Physical fitness'},
            {'id': '6003020834893', 'name': 'Health and wellness'},
            {'id': '6003397425735', 'name': 'Healthy diet'}
        ])
        return builder

    @staticmethod
    def business_professionals(
        countries: List[str] = ['US'],
        age_min: int = 25,
        age_max: int = 55
    ) -> TargetingBuilder:
        """Business professionals and entrepreneurs.

        Args:
            countries: Target countries
            age_min: Minimum age
            age_max: Maximum age

        Returns:
            Configured TargetingBuilder
        """
        builder = TargetingBuilder()
        builder.add_countries(countries)
        builder.set_age_range(age_min, age_max)
        builder.add_interests([
            {'id': '6003020834693', 'name': 'Business'},
            {'id': '6003020834793', 'name': 'Entrepreneurship'},
            {'id': '6003020834893', 'name': 'Small business'}
        ])
        return builder

    @staticmethod
    def parents_young_children(
        countries: List[str] = ['US'],
        age_min: int = 25,
        age_max: int = 44
    ) -> TargetingBuilder:
        """Parents with young children.

        Args:
            countries: Target countries
            age_min: Minimum age
            age_max: Maximum age

        Returns:
            Configured TargetingBuilder
        """
        builder = TargetingBuilder()
        builder.add_countries(countries)
        builder.set_age_range(age_min, age_max)
        builder.add_interests([
            {'id': '6003397425735', 'name': 'Parenting'}
        ])
        builder.add_behaviors([
            {'id': '6003397425735', 'name': 'Parents (All)'}
        ])
        return builder

    @staticmethod
    def travelers(
        countries: List[str] = ['US'],
        age_min: int = 25,
        age_max: int = 54
    ) -> TargetingBuilder:
        """Travel enthusiasts.

        Args:
            countries: Target countries
            age_min: Minimum age
            age_max: Maximum age

        Returns:
            Configured TargetingBuilder
        """
        builder = TargetingBuilder()
        builder.add_countries(countries)
        builder.set_age_range(age_min, age_max)
        builder.add_interests([
            {'id': '6003020834693', 'name': 'Travel'},
            {'id': '6003020834793', 'name': 'Adventure travel'}
        ])
        builder.add_behaviors([
            {'id': '6002714895372', 'name': 'Frequent travelers'}
        ])
        return builder

    @staticmethod
    def gamers(
        countries: List[str] = ['US'],
        age_min: int = 18,
        age_max: int = 35
    ) -> TargetingBuilder:
        """Gaming audience.

        Args:
            countries: Target countries
            age_min: Minimum age
            age_max: Maximum age

        Returns:
            Configured TargetingBuilder
        """
        builder = TargetingBuilder()
        builder.add_countries(countries)
        builder.set_age_range(age_min, age_max)
        builder.add_interests([
            {'id': '6003020834693', 'name': 'Video games'},
            {'id': '6003020834793', 'name': 'Console games'},
            {'id': '6003020834893', 'name': 'Mobile games'}
        ])
        return builder

    @staticmethod
    def foodies(
        countries: List[str] = ['US'],
        age_min: int = 22,
        age_max: int = 50
    ) -> TargetingBuilder:
        """Food and dining enthusiasts.

        Args:
            countries: Target countries
            age_min: Minimum age
            age_max: Maximum age

        Returns:
            Configured TargetingBuilder
        """
        builder = TargetingBuilder()
        builder.add_countries(countries)
        builder.set_age_range(age_min, age_max)
        builder.add_interests([
            {'id': '6003020834693', 'name': 'Foodie'},
            {'id': '6003020834793', 'name': 'Restaurants'},
            {'id': '6003020834893', 'name': 'Cooking'}
        ])
        return builder

    @staticmethod
    def real_estate_buyers(
        countries: List[str] = ['US'],
        age_min: int = 28,
        age_max: int = 55
    ) -> TargetingBuilder:
        """Real estate buyers and homeowners.

        Args:
            countries: Target countries
            age_min: Minimum age
            age_max: Maximum age

        Returns:
            Configured TargetingBuilder
        """
        builder = TargetingBuilder()
        builder.add_countries(countries)
        builder.set_age_range(age_min, age_max)
        builder.add_interests([
            {'id': '6003020834693', 'name': 'Real estate'}
        ])
        builder.add_behaviors([
            {'id': '6003020834793', 'name': 'Likely to move'}
        ])
        return builder

    @staticmethod
    def luxury_shoppers(
        countries: List[str] = ['US'],
        age_min: int = 30,
        age_max: int = 60
    ) -> TargetingBuilder:
        """High-income luxury shoppers.

        Args:
            countries: Target countries
            age_min: Minimum age
            age_max: Maximum age

        Returns:
            Configured TargetingBuilder
        """
        builder = TargetingBuilder()
        builder.add_countries(countries)
        builder.set_age_range(age_min, age_max)
        builder.add_interests([
            {'id': '6003020834693', 'name': 'Luxury goods'}
        ])
        builder.add_behaviors([
            {'id': '6003020834793', 'name': 'Affluent household'}
        ])
        return builder

    @staticmethod
    def mobile_first_users(
        countries: List[str] = ['US'],
        age_min: int = 18,
        age_max: int = 34
    ) -> TargetingBuilder:
        """Mobile-first users.

        Args:
            countries: Target countries
            age_min: Minimum age
            age_max: Maximum age

        Returns:
            Configured TargetingBuilder
        """
        from .builder import DeviceType
        builder = TargetingBuilder()
        builder.add_countries(countries)
        builder.set_age_range(age_min, age_max)
        builder.set_device_platforms([DeviceType.MOBILE])
        return builder

    @staticmethod
    def instagram_only(
        countries: List[str] = ['US'],
        age_min: int = 18,
        age_max: int = 34
    ) -> TargetingBuilder:
        """Instagram-only audience.

        Args:
            countries: Target countries
            age_min: Minimum age
            age_max: Maximum age

        Returns:
            Configured TargetingBuilder
        """
        builder = TargetingBuilder()
        builder.add_countries(countries)
        builder.set_age_range(age_min, age_max)
        builder.set_publisher_platforms(['instagram'])
        return builder

    @staticmethod
    def local_business(
        city_key: str,
        radius_miles: int = 10,
        age_min: int = 21,
        age_max: int = 60
    ) -> TargetingBuilder:
        """Local business targeting.

        Args:
            city_key: City key from Facebook
            radius_miles: Radius around city in miles
            age_min: Minimum age
            age_max: Maximum age

        Returns:
            Configured TargetingBuilder
        """
        builder = TargetingBuilder()
        builder.add_cities([
            {
                'key': city_key,
                'radius': radius_miles,
                'distance_unit': 'mile'
            }
        ])
        builder.set_age_range(age_min, age_max)
        return builder

    @staticmethod
    def get_all_presets() -> Dict[str, str]:
        """Get list of all available presets.

        Returns:
            Dictionary mapping preset names to descriptions
        """
        return {
            'ecommerce_general': 'General e-commerce shoppers',
            'fashion_shoppers': 'Fashion and apparel audience',
            'tech_enthusiasts': 'Technology and gadget enthusiasts',
            'fitness_health': 'Fitness and health-conscious users',
            'business_professionals': 'Business professionals and entrepreneurs',
            'parents_young_children': 'Parents with young children',
            'travelers': 'Travel enthusiasts',
            'gamers': 'Gaming audience',
            'foodies': 'Food and dining enthusiasts',
            'real_estate_buyers': 'Real estate buyers',
            'luxury_shoppers': 'High-income luxury shoppers',
            'mobile_first_users': 'Mobile-first users',
            'instagram_only': 'Instagram-only targeting',
            'local_business': 'Local business with radius targeting'
        }
