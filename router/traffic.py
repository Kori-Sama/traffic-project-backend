from typing import List
from fastapi import APIRouter, Depends

from core.middleware import LogRoute


router = APIRouter(prefix="/roads", route_class=LogRoute)
