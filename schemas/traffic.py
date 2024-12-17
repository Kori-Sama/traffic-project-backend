from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import List, Optional, Tuple


class RoadCoordinateModel(BaseModel):
    link_id: int
    link_length: int
    road_geom: Tuple[List[float], List[float]]
    road_name: str


class TrafficEventModel(BaseModel):
    event_id: int
    event_type: str
    description: Optional[str]
    start_time: datetime
    end_time: Optional[datetime]
    create_time: datetime = Field(default_factory=datetime.now)


class RoadConditionModel(BaseModel):
    condition_id: int
    date: date
    link_id: int
    daily_10min: datetime
    real_speed: float
    free_speed: float
    idx: float


class TrafficStatusModel(BaseModel):
    status_id: int
    link_id: int
    daily_10min: datetime
    status: str
    create_time: datetime = Field(default_factory=datetime.now)


class SpeedLimitPolicyModel(BaseModel):
    policy_id: int
    link_id: int
    speed_limit: float
    start_time: datetime
    end_time: Optional[datetime]
    create_time: datetime = Field(default_factory=datetime.now)