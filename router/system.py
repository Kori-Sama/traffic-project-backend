from fastapi import APIRouter
from core.middleware import LogRoute
from schemas.system import SystemInfo
from services.system import SystemService
from schemas.common import Response

router = APIRouter(prefix="/system", route_class=LogRoute)

service = SystemService()


@router.get("/info", summary="Fetch system information")
async def get_info() -> Response[SystemInfo]:
    return await service.get_system_info()
