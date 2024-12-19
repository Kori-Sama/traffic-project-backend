from pydantic import BaseModel
from typing import List, Optional, Tuple

from schemas.traffic import RoadConditionModel


class RoadModel(BaseModel):
    link_id: str
    link_length: int
    road_geom: List[Tuple[float, float]]
    road_name: str
    direction: int
    road_conditions: Optional[List[RoadConditionModel]] = None
