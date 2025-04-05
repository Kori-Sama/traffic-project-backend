from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Query
from schemas.gantry import GantryModel, VehiclePassageModel
from db import gantry as gantry_db

router = APIRouter(prefix="/gantry", tags=["gantry"])


@router.get("/list", response_model=List[GantryModel])
async def list_gantries(
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    """获取门架列表"""
    gantries = await gantry_db.list_gantries(offset=offset, limit=limit)
    return [g.to_schema() for g in gantries]


@router.get("/{gantry_id}", response_model=GantryModel)
async def get_gantry(gantry_id: int):
    """根据ID获取门架信息"""
    gantry = await gantry_db.get_gantry_by_id(gantry_id)
    return gantry.to_schema()


@router.get("/code/{gantry_code}", response_model=GantryModel)
async def get_gantry_by_code(gantry_code: str):
    """根据门架编号获取门架信息"""
    gantry = await gantry_db.get_gantry_by_code(gantry_code)
    return gantry.to_schema()


@router.get("/passage/list", response_model=List[VehiclePassageModel])
async def list_vehicle_passages(
    gantry_id: Optional[int] = None,
    vehicle_plate: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    """查询车辆通行记录"""
    passages = await gantry_db.list_vehicle_passages(
        gantry_id=gantry_id,
        vehicle_plate=vehicle_plate,
        start_time=start_time,
        end_time=end_time,
        offset=offset,
        limit=limit
    )
    return [p.to_schema() for p in passages]