from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Query
from schemas.trunk_ramp import TrunkRoadPassageModel, TrunkRoadFlowModel
from db import trunk_ramp as trunk_ramp_db

router = APIRouter(prefix="/trunk", tags=["trunk"])


# 主干路车辆通行记录相关接口
@router.get("/passage/list", response_model=List[TrunkRoadPassageModel])
async def list_trunk_road_passages(
    from_gantry_id: Optional[int] = None,
    to_gantry_id: Optional[int] = None,
    vehicle_plate: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    """查询主干路车辆通行记录"""
    passages = await trunk_ramp_db.list_trunk_road_passages(
        from_gantry_id=from_gantry_id,
        to_gantry_id=to_gantry_id,
        vehicle_plate=vehicle_plate,
        start_time=start_time,
        end_time=end_time,
        offset=offset,
        limit=limit
    )
    return [p.to_schema() for p in passages]


@router.get("/passage/{passage_id}", response_model=TrunkRoadPassageModel)
async def get_trunk_road_passage(passage_id: int):
    """根据ID获取主干路车辆通行记录"""
    passage = await trunk_ramp_db.get_trunk_road_passage_by_id(passage_id)
    return passage.to_schema()


# 主干路流量相关接口
@router.get("/flow/list", response_model=List[TrunkRoadFlowModel])
async def list_trunk_road_flows(
    road_name: Optional[str] = None,
    from_gantry_id: Optional[int] = None,
    to_gantry_id: Optional[int] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    """查询主干路流量"""
    flows = await trunk_ramp_db.list_trunk_road_flows(
        road_name=road_name,
        from_gantry_id=from_gantry_id,
        to_gantry_id=to_gantry_id,
        start_time=start_time,
        end_time=end_time,
        offset=offset,
        limit=limit
    )
    return [f.to_schema() for f in flows]


@router.get("/flow/{flow_id}", response_model=TrunkRoadFlowModel)
async def get_trunk_road_flow(flow_id: int):
    """根据ID获取主干路流量"""
    flow = await trunk_ramp_db.get_trunk_road_flow_by_id(flow_id)
    return flow.to_schema()