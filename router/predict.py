
from datetime import timedelta
from typing import List
from fastapi import APIRouter

from core.middleware import LogRoute
from db.road_condition import get_last_conditions
from router.response import Ok
from schemas.common import Response
from schemas.lstm import PredictInputV2, PredictOutput, PredictResponse
from lstm import predict

from db.trunk_ramp import list_trunk_road_flows
from db.gantry import get_segment_traffic_summary

router = APIRouter(prefix="/predict", route_class=LogRoute, tags=["predict"])


def _run_prediction(inputs: List[predict.PredictInputData]) -> PredictResponse:
    if not inputs:
        return PredictResponse(last=[], predict=[])

    inputs.sort(key=lambda x: x.start_time)
    idx = 0
    predicts = []
    while True:
        if idx + 6 > len(inputs):
            predicts += predict.run(inputs[-6:])
            break

        predicts += predict.run(inputs[idx:idx + 6])[:5]
        idx += 6

    # 去除predicts中时间相同的元素
    seen_times = set()
    unique_predicts = []
    for item in predicts:
        if item["time"] not in seen_times:
            unique_predicts.append(item)
            seen_times.add(item["time"])

    predicts = unique_predicts
    predicts.sort(key=lambda x: x["time"])

    return PredictResponse(
        last=[PredictOutput(
            time=item.start_time,
            volume=item.traffic_volume
        ) for item in inputs],
        predict=[PredictOutput(
            time=item["time"],
            volume=item["predicted_traffic_volume"]
        ) for item in predicts]
    )


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


@router.post("/flow/lstm")
async def predict_flow_lstm(
    input_data: PredictInputV2
) -> Response[PredictResponse]:
    """
    Predict traffic volume by LSTM model.
    """

    road_flows = await list_trunk_road_flows(
        from_gantry_id=input_data.from_gantry_id,
        to_gantry_id=input_data.to_gantry_id,
        start_time=input_data.start_time,
        end_time=input_data.end_time)

    inputs = [
        predict.PredictInputData(
            road_id=item.from_gantry_id,
            start_time=item.start_time,
            end_time=item.end_time,
            traffic_volume=item.traffic_volume
        ) for item in road_flows
    ]
    return Ok(_run_prediction(inputs))


@router.post("/speed/lstm")
async def predict_speed_lstm(
    input_data: PredictInputV2
) -> Response[PredictResponse]:
    """
    Predict traffic volume by LSTM model.
    """

    road_flows = await list_trunk_road_flows(
        from_gantry_id=input_data.from_gantry_id,
        to_gantry_id=input_data.to_gantry_id,
        start_time=input_data.start_time,
        end_time=input_data.end_time)

    inputs = [
        predict.PredictInputData(
            road_id=item.from_gantry_id,
            start_time=item.start_time,
            end_time=item.end_time,
            traffic_volume=item.avg_speed
        ) for item in road_flows
    ]
    return Ok(_run_prediction(inputs))


@router.post("/gantry/flow/lstm")
async def predict_gantry_flow_lstm(
    input_data: PredictInputV2
) -> Response[PredictResponse]:
    """
    Predict gantry traffic volume by LSTM model.
    """
    road_flows = await get_segment_traffic_summary(
        from_gantry_id=input_data.from_gantry_id,
        to_gantry_id=input_data.to_gantry_id,
        start_time=input_data.start_time,
        end_time=input_data.end_time)

    inputs = [
        predict.PredictInputData(
            road_id=item['from_gantry_id'],
            start_time=item['start_time'],
            end_time=item['end_time'],
            traffic_volume=item['traffic_volume']
        ) for item in road_flows
    ]
    return Ok(_run_prediction(inputs))


@router.post("/gantry/speed/lstm")
async def predict_gantry_speed_lstm(
    input_data: PredictInputV2
) -> Response[PredictResponse]:
    """
    Predict gantry traffic speed by LSTM model.
    """
    road_flows = await get_segment_traffic_summary(
        from_gantry_id=input_data.from_gantry_id,
        to_gantry_id=input_data.to_gantry_id,
        start_time=input_data.start_time,
        end_time=input_data.end_time)

    inputs = [
        predict.PredictInputData(
            road_id=item['from_gantry_id'],
            start_time=item['start_time'],
            end_time=item['end_time'],
            traffic_volume=item['avg_speed']
        ) for item in road_flows
    ]
    return Ok(_run_prediction(inputs))

