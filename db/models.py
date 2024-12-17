from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional
from shapely.geometry import LineString
from shapely import wkb
from schemas import traffic as schemas


@dataclass
class RoadCoordinate:
    link_id: int
    link_length: int
    road_geom: LineString
    road_name: str

    def to_schema(self):
        return schemas.RoadCoordinateModel(
            link_id=self.link_id,
            link_length=self.link_length,
            road_geom=self.road_geom.coords.xy,
            road_name=self.road_name,
        )

    @staticmethod
    def from_db(record) -> "RoadCoordinate":
        return RoadCoordinate(
            link_id=record["link_id"],
            link_length=record["link_length"],
            road_geom=wkb.loads(record["road_geom"], hex=True),
            road_name=record["road_name"],
        )


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
