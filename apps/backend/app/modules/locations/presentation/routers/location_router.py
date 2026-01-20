"""Location router for city endpoints."""

from fastapi import APIRouter, Depends
from injector import Injector

from app.injector import injector as global_container
from app.modules.locations.application.use_cases.get_all_cities_use_case import (
    GetAllCitiesUseCase,
)
from app.modules.locations.presentation.schemas.city_schemas import (
    CityListResponse,
    CityListResponseWrapper,
    CityResponse,
)


def get_container() -> Injector:
    """Get the global injector container."""
    return global_container


router = APIRouter(prefix="/locations", tags=["locations"])


@router.get(
    "/cities",
    response_model=CityListResponseWrapper,
    summary="Get all Taiwan cities",
    description="""
    Get a list of all available Taiwan cities/counties.

    This endpoint provides the complete list of Taiwan's 22 cities/counties including:
    - **Six Special Municipalities** (直轄市): Taipei, New Taipei, Taoyuan, Taichung, Tainan, Kaohsiung
    - **Provincial Cities** (省轄市): Hsinchu City, Chiayi City
    - **Counties** (縣): Hsinchu County, Miaoli, Changhua, Nantou, Yunlin, Chiayi County, Pingtung, Yilan, Hualien, Taitung, Penghu, Kinmen, Lienchiang

    Each city includes:
    - `code`: City code used in APIs (e.g., TPE, NTP, TAO)
    - `name`: English name (e.g., Taipei City)
    - `name_zh`: Chinese name (e.g., 台北市)

    This is a public endpoint that **does not require authentication**.
    Frontend applications should use this to dynamically populate city selection dropdowns.
    """,
    responses={
        200: {
            "description": "List of all Taiwan cities retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "cities": [
                            {"code": "TPE", "name": "Taipei City", "name_zh": "台北市"},
                            {"code": "NTP", "name": "New Taipei City", "name_zh": "新北市"},
                            {"code": "TAO", "name": "Taoyuan City", "name_zh": "桃園市"},
                        ]
                    }
                }
            }
        }
    }
)
async def get_cities(
    container: Injector = Depends(get_container),
) -> CityListResponseWrapper:
    """Get all available Taiwan cities/counties.

    Args:
        container: DI container

    Returns:
        List of all 22 Taiwan cities with code, English name, and Chinese name
    """
    use_case = container.get(GetAllCitiesUseCase)
    cities = await use_case.execute()

    city_responses = [
        CityResponse(
            code=city.code.value,
            name=city.name,
            name_zh=city.name_zh
        )
        for city in cities
    ]

    data = CityListResponse(cities=city_responses)
    return CityListResponseWrapper(data=data, meta=None, error=None)
