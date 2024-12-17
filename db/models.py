from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional
from shapely.geometry import LineString


@dataclass
class RoadCoordinate:
    link_id: int
    link_length: int
    road_geom: LineString
    road_name: str


@dataclass
class TrafficEvent:
    event_id: int
    event_type: str
    description: Optional[str]
    start_time: datetime
    end_time: Optional[datetime]
    create_time: datetime = datetime.now()


@dataclass
class RoadToEvent:
    id: int
    link_id: int
    event_id: int


@dataclass
class RoadCondition:
    condition_id: int
    date: date
    link_id: int
    daily_10min: datetime
    real_speed: float
    free_speed: float
    idx: float


@dataclass
class TrafficStatus:
    status_id: int
    link_id: int
    daily_10min: datetime
    status: str
    create_time: datetime = datetime.now()


@dataclass
class SpeedLimitPolicy:
    policy_id: int
    link_id: int
    speed_limit: float
    start_time: datetime
    end_time: Optional[datetime]
    create_time: datetime = datetime.now()
