from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Query
from schemas.trunk_ramp import RampVehiclePassageModel, RampFlowModel
from db import trunk_ramp as trunk_ramp_db

router = APIRouter(prefix="/ramp", tags=["ramp"])


# 匝道车辆通行记录相关接口
@router.get("/passage/list", response_model=List[RampVehiclePassageModel])
async def list_ramp_vehicle_passages(
    ramp_type: Optional[str] = None,
    to_gantry_id: Optional[int] = None,
    vehicle_plate: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    """查询匝道车辆通行记录"""
    passages = await trunk_ramp_db.list_ramp_vehicle_passages(
        ramp_type=ramp_type,
        to_gantry_id=to_gantry_id,
        vehicle_plate=vehicle_plate,
        start_time=start_time,
        end_time=end_time,
        offset=offset,
        limit=limit
    )
    return [p.to_schema() for p in passages]


@router.get("/passage/{passage_id}", response_model=RampVehiclePassageModel)
async def get_ramp_vehicle_passage(passage_id: int):
    """根据ID获取匝道车辆通行记录"""
    passage = await trunk_ramp_db.get_ramp_vehicle_passage_by_id(passage_id)
    return passage.to_schema()


# 匝道流量相关接口
@router.get("/flow/list", response_model=List[RampFlowModel])
async def list_ramp_flows(
    ramp_name: Optional[str] = None,
    ramp_type: Optional[str] = None,
    to_gantry_id: Optional[int] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    """查询匝道流量"""
    flows = await trunk_ramp_db.list_ramp_flows(
        ramp_name=ramp_name,
        ramp_type=ramp_type,
        to_gantry_id=to_gantry_id,
        start_time=start_time,
        end_time=end_time,
        offset=offset,
        limit=limit
    )
    return [f.to_schema() for f in flows]


@router.get("/flow/{flow_id}", response_model=RampFlowModel)
async def get_ramp_flow(flow_id: int):
    """根据ID获取匝道流量"""
    flow = await trunk_ramp_db.get_ramp_flow_by_id(flow_id)
    return flow.to_schema()