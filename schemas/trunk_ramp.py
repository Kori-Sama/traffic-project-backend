from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


# 主干路车辆通行记录模型
class TrunkRoadPassageModel(BaseModel):
    passage_id: int
    from_gantry_id: int
    to_gantry_id: int
    start_time: datetime
    end_time: datetime
    vehicle_plate: str
    speed: Optional[float]


# 主干路流量模型
class TrunkRoadFlowModel(BaseModel):
    flow_id: int
    road_name: str
    from_gantry_id: int
    to_gantry_id: int
    start_time: datetime
    end_time: datetime
    traffic_volume: int
    avg_speed: Optional[float]


# 匝道车辆通行记录模型
class RampVehiclePassageModel(BaseModel):
    passage_id: int
    ramp_type: str  # 'enter'或'exit'
    to_gantry_id: int
    passage_time: datetime
    vehicle_plate: str
    vehicle_type: int


# 匝道流量模型
class RampFlowModel(BaseModel):
    flow_id: int
    ramp_name: str
    ramp_type: str  # 'enter'或'exit'
    from_sequence: int
    to_gantry_id: int
    start_time: datetime
    end_time: datetime
    traffic_volume: int