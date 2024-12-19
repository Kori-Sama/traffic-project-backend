from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional
from shapely.geometry import LineString
from shapely import wkb
from schemas import traffic as schemas


@dataclass
class RoadCoordinate:
    link_id: int  # 由于该int过大, 在前端会丢失精度, 所以传给前端的时候需要转换成str
    link_length: int
    road_geom: LineString
    road_name: str
    direction: int

    def to_schema(self):
        return schemas.RoadCoordinateModel(
            link_id=str(self.link_id),
            link_length=self.link_length,
            road_geom=self.road_geom.coords,
            road_name=self.road_name,
            direction=self.direction
        )

    @staticmethod
    def from_db(record) -> "RoadCoordinate":
        return RoadCoordinate(
            link_id=record["link_id"],
            link_length=record["link_length"],
            road_geom=wkb.loads(record["road_geom"], hex=True),
            road_name=record["road_name"],
            direction=record["direction"]
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

    def to_schema(self):
        return schemas.RoadConditionModel(
            condition_id=self.condition_id,
            date=self.date,
            link_id=str(self.link_id),
            daily_10min=self.daily_10min,
            real_speed=self.real_speed,
            free_speed=self.free_speed,
            idx=self.idx,
        )


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
