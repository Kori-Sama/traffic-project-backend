from typing import List
from fastapi import APIRouter, Depends

from core.middleware import LogRoute
from schemas.common import ListData, QueryData, Response
from schemas.roads import RoadInfo
from services.roads import RoadsService


router = APIRouter(prefix="/roads", route_class=LogRoute)

service = RoadsService()


@router.get("", summary="Fetch all roads information")
async def list_roads(query: QueryData = Depends()) -> Response[ListData[List[RoadInfo]]]:
    return await service.get_items(query.offset, query.limit)
