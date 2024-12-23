from pydantic import BaseModel, Field
from datetime import datetime


class PredictInput(BaseModel):
    link_id: str
    start_time: datetime
    end_time: datetime


class PredictOutput(BaseModel):
    time: datetime
    volume: float


class PredictResponse(BaseModel):
    last: list[PredictOutput] = Field(..., description="最近的真实数据")
    predict: list[PredictOutput] = Field(..., description="预测数据")
