from pydantic import BaseModel
from typing import List, Optional, Union

class HotelSchema(BaseModel):
    hotel_name: str
    address: str
    latitude: Union[float, str]
    longitude: Union[float, str]
    rating: Union[float, str]
    reviews: Union[int, str]
    price: Union[float, int, str]
    distance: str
    amenities: List[str] = []
    phone: Optional[str] = ""
    website: Optional[str] = ""
    image: str
    maps_url: str
