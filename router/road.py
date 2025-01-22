import asyncio
from typing import List
from fastapi import APIRouter, Depends

from core.middleware import LogRoute
from db.road_condition import get_conditions_by_link_id
from db.road import get_road, list_roads
from router.error import LINK_ID_NOT_FOUND
from router.response import Bad, Ok
from schemas.common import QueryData, Response
from schemas.composite import RoadModel
from schemas.traffic import RoadModel


sub_router = APIRouter(prefix="/roads", route_class=LogRoute)


@sub_router.get("/")
async def list_roads_api(query: QueryData = Depends()) -> Response[List[RoadModel]]:
    """
    List road coordinates with pagination, if no query parameters are provided, it will return the first 10 records.
    """
    data = await list_roads(query.offset, query.limit)
    data = [item.to_schema() for item in data]
    return Ok(data)


@sub_router.get("/{link_id}")
async def get_road_api(link_id: str, with_conditions: bool = False, query: QueryData = Depends()) -> Response[RoadModel]:
    """
    Get road coordinate by link_id, if with_conditions is True, it will also return the road conditions.
    """
    id = int(link_id)
    if not with_conditions:
        data = await get_road(id)
        if data:
            return Ok(data.to_schema())
        return Bad(LINK_ID_NOT_FOUND)

    task1 = get_road(id)
    task2 = get_conditions_by_link_id(id, query.offset, query.limit)
    data = await asyncio.gather(task1, task2)
    if not data[0]:
        return Bad(LINK_ID_NOT_FOUND)

    road = data[0].to_schema()
    road_conditions = [item.to_schema() for item in data[1]]
    return Ok(RoadModel(**road.model_dump(), road_conditions=road_conditions))
