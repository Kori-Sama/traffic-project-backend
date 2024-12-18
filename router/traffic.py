import asyncio
from typing import List
from fastapi import APIRouter, Depends

from core.middleware import LogRoute
from db.road_condition import get_conditions_by_link_id, get_conditions_with_time_range, list_road_conditions
from db.road_coordinate import get_road_coordinate, list_road_coordinates
from router.error import LINK_ID_NOT_FOUND
from router.response import Bad, Ok
from schemas.common import QueryData, Response, TimeRange
from schemas.composite import RoadModel
from schemas.traffic import RoadConditionModel, RoadCoordinateModel


router = APIRouter(prefix="/traffic", route_class=LogRoute)


@router.get("/coordinates")
async def list_road_coordinates_api(query: QueryData = Depends()) -> Response[List[RoadCoordinateModel]]:
    """
    List road coordinates with pagination, if no query parameters are provided, it will return the first 10 records.
    """
    data = await list_road_coordinates(query.offset, query.limit)
    data = [item.to_schema() for item in data]
    return Ok(data)


@router.get("/coordinate/{link_id}")
async def get_road_coordinate_api(link_id: str, with_conditions: bool = False, query: QueryData = Depends()) -> Response[RoadModel]:
    """
    Get road coordinate by link_id, if with_conditions is True, it will also return the road conditions.
    """
    id = int(link_id)
    if not with_conditions:
        data = await get_road_coordinate(id)
        if data:
            return Ok(data.to_schema())
        return Bad(LINK_ID_NOT_FOUND)

    task1 = get_road_coordinate(id)
    task2 = get_conditions_by_link_id(id, query.offset, query.limit)
    data = await asyncio.gather(task1, task2)
    if not data[0]:
        return Bad(LINK_ID_NOT_FOUND)

    road_coordinate = data[0].to_schema()
    road_conditions = [item.to_schema() for item in data[1]]
    return Ok(RoadModel(**road_coordinate.model_dump(), road_conditions=road_conditions))


@router.get("/conditions")
async def list_road_conditions_api(query: QueryData = Depends()) -> Response[List[RoadConditionModel]]:
    """
    List road conditions with pagination, if no query parameters are provided, it will return the first 10 records.
    """
    data = await list_road_conditions(query.offset, query.limit)
    data = [item.to_schema() for item in data]
    return Ok(data)


@router.get("/conditions/{link_id}")
async def get_conditions_by_link_id_api(link_id: str, query: QueryData = Depends()) -> Response[List[RoadConditionModel]]:
    """
    Get road conditions by link_id with pagination, if no query parameters are provided, it will return the first 10 records.
    """
    id = int(link_id)
    data = await get_conditions_by_link_id(id)

    data = [item.to_schema() for item in data]
    if not data:
        return Bad(LINK_ID_NOT_FOUND)

    return Ok(data)


@router.post("/conditions/{link_id}")
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
