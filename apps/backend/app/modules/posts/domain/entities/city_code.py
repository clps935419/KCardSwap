"""
City Code enumeration for posts module

Represents valid Taiwan city codes for city board posts.
"""

from enum import Enum


class CityCode(str, Enum):
    """Valid Taiwan city codes for post filtering"""

    # Six special municipalities (直轄市)
    TPE = "TPE"  # Taipei City (台北市)
    NTP = "NTP"  # New Taipei City (新北市)
    TAO = "TAO"  # Taoyuan City (桃園市)
    TXG = "TXG"  # Taichung City (台中市)
    TNN = "TNN"  # Tainan City (台南市)
    KHH = "KHH"  # Kaohsiung City (高雄市)

    # Provincial cities (省轄市)
    KEE = "KEE"  # Keelung City (基隆市)
    HSZ = "HSZ"  # Hsinchu City (新竹市)
    CYI = "CYI"  # Chiayi City (嘉義市)

    # Counties (縣)
    HSQ = "HSQ"  # Hsinchu County (新竹縣)
    MIA = "MIA"  # Miaoli County (苗栗縣)
    CHA = "CHA"  # Changhua County (彰化縣)
    NAN = "NAN"  # Nantou County (南投縣)
    YUN = "YUN"  # Yunlin County (雲林縣)
    CYQ = "CYQ"  # Chiayi County (嘉義縣)
    PIF = "PIF"  # Pingtung County (屏東縣)
    ILA = "ILA"  # Yilan County (宜蘭縣)
    HUA = "HUA"  # Hualien County (花蓮縣)
    TTT = "TTT"  # Taitung County (台東縣)
    PEN = "PEN"  # Penghu County (澎湖縣)
    KIN = "KIN"  # Kinmen County (金門縣)
    LIE = "LIE"  # Lienchiang County (連江縣/馬祖)
