from typing import Optional
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


class PredictInputV2(BaseModel):
    from_gantry_id: int = Field(..., description="起始门架ID")
    to_gantry_id: int = Field(..., description="结束门架ID")
    start_time: datetime = Field(..., description="预测开始时间")
    end_time: Optional[datetime] = Field(
        None, description="预测结束时间, 默认为当前时间加5分钟")
