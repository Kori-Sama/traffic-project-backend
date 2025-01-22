
from datetime import timedelta
from fastapi import APIRouter, Depends

from core.middleware import LogRoute
from db.road_condition import get_last_conditions
from router.response import Ok
from schemas.common import Response
from schemas.lstm import PredictInput, PredictOutput, PredictResponse
from lstm import predict


router = APIRouter(prefix="/predict", route_class=LogRoute)


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
