"""City repository implementation."""

from app.modules.locations.domain.repositories.city_repository import ICityRepository
from app.modules.locations.domain.value_objects.city import City
from app.modules.posts.domain.entities.city_code import CityCode


class CityRepositoryImpl(ICityRepository):
    """Implementation of city repository using static data."""
    
    # Complete list of Taiwan cities/counties with official English and Chinese names
    _CITIES = [
        # Six Special Municipalities (直轄市)
        City(CityCode.TPE, "Taipei City", "台北市"),
        City(CityCode.NTP, "New Taipei City", "新北市"),
        City(CityCode.TAO, "Taoyuan City", "桃園市"),
        City(CityCode.TXG, "Taichung City", "台中市"),
        City(CityCode.TNN, "Tainan City", "台南市"),
        City(CityCode.KHH, "Kaohsiung City", "高雄市"),
        
        # Provincial Cities (省轄市)
        City(CityCode.HSZ, "Hsinchu City", "新竹市"),
        City(CityCode.CYI, "Chiayi City", "嘉義市"),
        
        # Counties (縣)
        City(CityCode.HSQ, "Hsinchu County", "新竹縣"),
        City(CityCode.MIA, "Miaoli County", "苗栗縣"),
        City(CityCode.CHA, "Changhua County", "彰化縣"),
        City(CityCode.NAN, "Nantou County", "南投縣"),
        City(CityCode.YUN, "Yunlin County", "雲林縣"),
        City(CityCode.CYQ, "Chiayi County", "嘉義縣"),
        City(CityCode.PIF, "Pingtung County", "屏東縣"),
        City(CityCode.ILA, "Yilan County", "宜蘭縣"),
        City(CityCode.HUA, "Hualien County", "花蓮縣"),
        City(CityCode.TTT, "Taitung County", "台東縣"),
        City(CityCode.PEN, "Penghu County", "澎湖縣"),
        City(CityCode.KIN, "Kinmen County", "金門縣"),
        City(CityCode.LIE, "Lienchiang County", "連江縣"),
    ]
    
    async def get_all_cities(self) -> list[City]:
        """Get all Taiwan cities/counties.
        
        Returns:
            List of all 22 Taiwan cities/counties
        """
        return self._CITIES.copy()
