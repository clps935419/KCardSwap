"""City repository interface."""

from abc import ABC, abstractmethod

from app.modules.locations.domain.value_objects.city import City


class ICityRepository(ABC):
    """Repository interface for city data."""
    
    @abstractmethod
    async def get_all_cities(self) -> list[City]:
        """Get all available cities in Taiwan.
        
        Returns:
            List of all Taiwan cities/counties
        """
        pass
