"""City value object."""

from dataclasses import dataclass

from app.modules.posts.domain.entities.city_code import CityCode


@dataclass(frozen=True)
class City:
    """City value object representing a Taiwan city/county.
    
    Attributes:
        code: City code from CityCode enum (e.g., TPE, NTP)
        name: English name (e.g., Taipei City)
        name_zh: Chinese name (e.g., 台北市)
    """
    
    code: CityCode
    name: str
    name_zh: str
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "code": self.code.value,
            "name": self.name,
            "name_zh": self.name_zh,
        }
