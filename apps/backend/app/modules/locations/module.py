"""Locations module configuration for dependency injection."""

from injector import Binder, Module, singleton

from app.modules.locations.application.use_cases.get_all_cities_use_case import GetAllCitiesUseCase
from app.modules.locations.domain.repositories.city_repository import ICityRepository
from app.modules.locations.infrastructure.repositories.city_repository_impl import CityRepositoryImpl


class LocationsModule(Module):
    """Dependency injection configuration for Locations module."""
    
    def configure(self, binder: Binder) -> None:
        """Configure bindings for locations module.
        
        Args:
            binder: Injector binder to configure dependencies
        """
        # Repositories
        binder.bind(ICityRepository, to=CityRepositoryImpl, scope=singleton)
        
        # Use Cases
        binder.bind(GetAllCitiesUseCase, scope=singleton)
