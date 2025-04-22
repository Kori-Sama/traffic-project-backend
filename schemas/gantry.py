from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class GantryModel(BaseModel):
    gantry_id: int
    sequence_number: int
    unique_number: int
    gantry_code: str
    gantry_name: str
    toll_station: Optional[str]
    subcenter: Optional[str]
    longitude: float
    latitude: float
    stake_number: Optional[str]
    direction: int
    location: List[float]  # [longitude, latitude]


class VehiclePassageModel(BaseModel):
    passage_id: int
    gantry_id: int
    passage_time: datetime
    vehicle_plate: str
    vehicle_type: int
    create_time: datetime = Field(default_factory=datetime.now)