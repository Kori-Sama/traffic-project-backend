from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional
from shapely.geometry import LineString
from shapely import wkb
from schemas import traffic as schemas


@dataclass
class Road:
    link_id: int  # 由于该int过大, 在前端会丢失精度, 所以传给前端的时候需要转换成str
    link_length: int
    road_geom: LineString
    road_name: str
    direction: int

    def to_schema(self):
        return schemas.RoadModel(
            link_id=str(self.link_id),
            link_length=self.link_length,
            road_geom=self.road_geom.coords,
            road_name=self.road_name,
            direction=self.direction
        )

    @staticmethod
    def from_db(record) -> "Road":
        return Road(
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


@dataclass
class Gantry:
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

    def to_schema(self):
        from schemas import gantry as schemas
        return schemas.GantryModel(
            gantry_id=self.gantry_id,
            sequence_number=self.sequence_number,
            unique_number=self.unique_number,
            gantry_code=self.gantry_code,
            gantry_name=self.gantry_name,
            toll_station=self.toll_station,
            subcenter=self.subcenter,
            longitude=self.longitude,
            latitude=self.latitude,
            stake_number=self.stake_number,
            direction=self.direction,
            location=[self.longitude, self.latitude]
        )

    @staticmethod
    def from_db(record) -> "Gantry":
        return Gantry(
            gantry_id=record["gantry_id"],
            sequence_number=record["sequence_number"],
            unique_number=record["unique_number"],
            gantry_code=record["gantry_code"],
            gantry_name=record["gantry_name"],
            toll_station=record["toll_station"],
            subcenter=record["subcenter"],
            longitude=record["longitude"],
            latitude=record["latitude"],
            stake_number=record["stake_number"],
            direction=record["direction"]
        )


@dataclass
class VehiclePassage:
    passage_id: int
    gantry_id: int
    passage_time: datetime
    vehicle_plate: str
    vehicle_type: int
    create_time: datetime = datetime.now()

    def to_schema(self):
        from schemas import gantry as schemas
        return schemas.VehiclePassageModel(
            passage_id=self.passage_id,
            gantry_id=self.gantry_id,
            passage_time=self.passage_time,
            vehicle_plate=self.vehicle_plate,
            vehicle_type=self.vehicle_type,
            create_time=self.create_time
        )

    @staticmethod
    def from_db(record) -> "VehiclePassage":
        return VehiclePassage(
            passage_id=record["passage_id"],
            gantry_id=record["gantry_id"],
            passage_time=record["passage_time"],
            vehicle_plate=record["vehicle_plate"],
            vehicle_type=record["vehicle_type"],
            create_time=record.get("create_time", datetime.now())
        )
