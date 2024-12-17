from typing import List
from fastapi import APIRouter, Depends

from core.middleware import LogRoute
from db.road_coordinate import list_road_coordinates
from router.response import Ok
from schemas.common import QueryData, Response
from schemas.traffic import RoadCoordinateModel


router = APIRouter(prefix="/traffic", route_class=LogRoute)


@router.get("/")
async def list_road_coordinates_api(query: QueryData = Depends()) -> Response[List[RoadCoordinateModel]]:
    data = await list_road_coordinates(query.offset, query.limit)
    data = [item.to_schema() for item in data]
    return Ok(data)
