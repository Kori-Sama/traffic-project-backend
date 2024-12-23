from pydantic import BaseModel, Field
from datetime import datetime


class PredictInput(BaseModel):
    road_id: int
    start_time: str
    end_time: str
    traffic_volume: int


class PredictOutput(BaseModel):
    time: datetime
    predicted_traffic_volume: int
