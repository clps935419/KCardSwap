"""Get all cities use case."""

from injector import inject

from app.modules.locations.domain.repositories.city_repository import ICityRepository
from app.modules.locations.domain.value_objects.city import City


class GetAllCitiesUseCase:
    """Use case for retrieving all Taiwan cities."""
    
    @inject
    def __init__(self, city_repository: ICityRepository):
        """Initialize use case with dependencies.
        
        Args:
            city_repository: City repository interface
        """
        self.city_repository = city_repository
    
    async def execute(self) -> list[City]:
        """Execute the use case to get all cities.
        
        Returns:
            List of all Taiwan cities/counties with code, name, and name_zh
        """
        return await self.city_repository.get_all_cities()
