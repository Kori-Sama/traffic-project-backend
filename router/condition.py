from typing import List
from fastapi import APIRouter

from core.middleware import LogRoute
from db.road_condition import get_conditions_with_time_range, get_last_conditions
from router.error import LINK_ID_NOT_FOUND
from router.response import Bad, Ok
from schemas.common import Response, TimeRange
from schemas.traffic import RoadConditionModel


sub_router = APIRouter(prefix="/conditions", route_class=LogRoute)


@sub_router.get("/{link_id}")
async def get_last_conditions_api(link_id: str, last_num: int) -> Response[List[RoadConditionModel]]:
    """
    Get the last n road conditions by link_id.
    """
    id = int(link_id)
    data = await get_last_conditions(id, last_num)
    data = [item.to_schema() for item in data]
    if not data:
        return Bad(LINK_ID_NOT_FOUND)

    return Ok(data)


@sub_router.post("/{link_id}")
async def get_conditions_with_time_range_api(link_id: str, time_range: TimeRange) -> Response[List[RoadConditionModel]]:
    """
    Get road conditions by link_id with time range. 
    """
    id = int(link_id)
    data = await get_conditions_with_time_range(id, time_range.start_time, time_range.end_time)

    data = [item.to_schema() for item in data]
    if not data:
        return Bad(LINK_ID_NOT_FOUND)

    return Ok(data)
