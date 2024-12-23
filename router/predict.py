
from datetime import timedelta
from fastapi import APIRouter, Depends

from core.middleware import LogRoute
from db.road_condition import get_last_conditions
from router.response import Ok
from schemas.common import Response
from schemas.lstm import PredictInput, PredictOutput, PredictResponse
from lstm import predict


router = APIRouter(prefix="/predict", route_class=LogRoute)

"""
道路名称	时间段开始	时间段结束	车流量
1_17	2023-01-31 23:20:00	2023-01-31 23:25:00	150
1_17	2023-01-31 23:25:00	2023-01-31 23:30:00	74
1_17	2023-01-31 23:30:00	2023-01-31 23:35:00	37
1_17	2023-01-31 23:35:00	2023-01-31 23:40:00	14
1_17	2023-01-31 23:40:00	2023-01-31 23:45:00	26
1_17	2023-01-31 23:45:00	2023-01-31 23:50:00	44
1_17	2023-01-31 23:50:00	2023-01-31 23:55:00	22
1_17	2023-01-31 23:55:00	2023-02-01 00:00:00	20
"""

"""
[
    {
        "road_id": 1,
        "start_time": "2023-01-31 23:20:00",
        "end_time": "2023-01-31 23:25:00",
        "traffic_volume": 150
    },
    {
        "road_id": 1,
        "start_time": "2023-01-31 23:25:00",
        "end_time": "2023-01-31 23:30:00",
        "traffic_volume": 74
    },
    {
        "road_id": 1,
        "start_time": "2023-01-31 23:30:00",
        "end_time": "2023-01-31 23:35:00",
        "traffic_volume": 37
    },
    {
        "road_id": 1,
        "start_time": "2023-01-31 23:35:00",
        "end_time": "2023-01-31 23:40:00",
        "traffic_volume": 14
    },
    {
        "road_id": 1,
        "start_time": "2023-01-31 23:40:00",
        "end_time": "2023-01-31 23:45:00",
        "traffic_volume": 26
    },
    {
        "road_id": 1,
        "start_time": "2023-01-31 23:45:00",
        "end_time": "2023-01-31 23:50:00",
        "traffic_volume": 44
    }
]
"""


@router.post("/lstm")
async def predict_api(
    link_id: str,
) -> Response[PredictResponse]:
    """
    Predict traffic speed and volume by LSTM model.
    """
    conditions = await get_last_conditions(int(link_id), 6)

    inputs = [
        predict.PredictInputData(
            road_id=item.link_id,
            start_time=item.daily_10min,
            end_time=item.daily_10min + timedelta(minutes=5),
            traffic_volume=item.real_speed
        ) for item in conditions
    ]

    outputs = predict.run(inputs)
    return Ok(dict(
        last=[PredictOutput(
            time=item.start_time,
            volume=item.traffic_volume
        ) for item in inputs],
        predict=[PredictOutput(
            time=item["time"],
            volume=item["predicted_traffic_volume"]
        ) for item in outputs]
    ))
