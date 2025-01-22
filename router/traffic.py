from fastapi import APIRouter

from core.middleware import LogRoute
from db.road import get_total_length
from router import condition, road
from router.response import Ok


router = APIRouter(prefix="/traffic", route_class=LogRoute)

router.include_router(road.sub_router)
router.include_router(condition.sub_router)


@router.get("/total-length")
async def get_total_length_api():
    """
    Get the total length of all road coordinates.
    """
    data = await get_total_length()
    return Ok(data)
