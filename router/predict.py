
from fastapi import APIRouter

from core.middleware import LogRoute


router = APIRouter(prefix="/predict", route_class=LogRoute)


@router.post("/predict")
async def predict_api():
    pass
