from datetime import datetime
from typing import List, Optional
from db.core import with_connection
from db.models import TrunkRoadPassage, TrunkRoadFlow, RampVehiclePassage, RampFlow


# 主干路车辆通行记录相关操作
@with_connection
async def list_trunk_road_passages(
    conn,
    from_gantry_id: Optional[int] = None,
    to_gantry_id: Optional[int] = None,
    vehicle_plate: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    offset: int = 0,
    limit: int = 10
) -> List[TrunkRoadPassage]:
    conditions = ["1=1"]
    params = []
    param_index = 1

    if from_gantry_id is not None:
        conditions.append(f"from_gantry_id = ${param_index}")
        params.append(from_gantry_id)
        param_index += 1

    if to_gantry_id is not None:
        conditions.append(f"to_gantry_id = ${param_index}")
        params.append(to_gantry_id)
        param_index += 1

    if vehicle_plate is not None:
        conditions.append(f"vehicle_plate = ${param_index}")
        params.append(vehicle_plate)
        param_index += 1

    if start_time is not None:
        conditions.append(f"start_time >= ${param_index}")
        params.append(start_time)
        param_index += 1

    if end_time is not None:
        conditions.append(f"end_time <= ${param_index}")
        params.append(end_time)
        param_index += 1

    params.extend([limit, offset])
    where_clause = " AND ".join(conditions)
    query = f"""
    SELECT *
    FROM trunk_road_passage
    WHERE {where_clause}
    ORDER BY start_time DESC
    LIMIT ${param_index} OFFSET ${param_index + 1};
    """

    records = await conn.fetch(query, *params)
    return [TrunkRoadPassage.from_db(record) for record in records]


@with_connection
async def get_trunk_road_passage_by_id(conn, passage_id: int) -> Optional[TrunkRoadPassage]:
    query = "SELECT * FROM trunk_road_passage WHERE passage_id = $1;"
    record = await conn.fetchrow(query, passage_id)
    return TrunkRoadPassage.from_db(record) if record else None


@with_connection
async def create_trunk_road_passage(
    conn,
    from_gantry_id: int,
    to_gantry_id: int,
    start_time: datetime,
    end_time: datetime,
    vehicle_plate: str,
    speed: Optional[float] = None
) -> int:
    query = """
    INSERT INTO trunk_road_passage (
        from_gantry_id, to_gantry_id, start_time, end_time, vehicle_plate, speed
    ) VALUES ($1, $2, $3, $4, $5, $6)
    RETURNING passage_id;
    """
    passage_id = await conn.fetchval(
        query,
        from_gantry_id,
        to_gantry_id,
        start_time,
        end_time,
        vehicle_plate,
        speed
    )
    return passage_id


# 主干路流量相关操作
@with_connection
async def list_trunk_road_flows(
    conn,
    road_name: Optional[str] = None,
    from_gantry_id: Optional[int] = None,
    to_gantry_id: Optional[int] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    offset: int = 0,
    limit: int = 10
) -> List[TrunkRoadFlow]:
    conditions = ["1=1"]
    params = []
    param_index = 1

    if road_name is not None:
        conditions.append(f"road_name = ${param_index}")
        params.append(road_name)
        param_index += 1

    if from_gantry_id is not None:
        conditions.append(f"from_gantry_id = ${param_index}")
        params.append(from_gantry_id)
        param_index += 1

    if to_gantry_id is not None:
        conditions.append(f"to_gantry_id = ${param_index}")
        params.append(to_gantry_id)
        param_index += 1

    if start_time is not None:
        conditions.append(f"start_time >= ${param_index}")
        params.append(start_time)
        param_index += 1

    if end_time is not None:
        conditions.append(f"end_time <= ${param_index}")
        params.append(end_time)
        param_index += 1

    params.extend([limit, offset])
    where_clause = " AND ".join(conditions)
    query = f"""
    SELECT *
    FROM trunk_road_flow
    WHERE {where_clause}
    ORDER BY start_time DESC
    LIMIT ${param_index} OFFSET ${param_index + 1};
    """

    records = await conn.fetch(query, *params)
    return [TrunkRoadFlow.from_db(record) for record in records]


@with_connection
async def get_trunk_road_flow_by_id(conn, flow_id: int) -> Optional[TrunkRoadFlow]:
    query = "SELECT * FROM trunk_road_flow WHERE flow_id = $1;"
    record = await conn.fetchrow(query, flow_id)
    return TrunkRoadFlow.from_db(record) if record else None


@with_connection
async def create_trunk_road_flow(
    conn,
    road_name: str,
    from_gantry_id: int,
    to_gantry_id: int,
    start_time: datetime,
    end_time: datetime,
    traffic_volume: int,
    avg_speed: Optional[float] = None
) -> int:
    query = """
    INSERT INTO trunk_road_flow (
        road_name, from_gantry_id, to_gantry_id, start_time, end_time, traffic_volume, avg_speed
    ) VALUES ($1, $2, $3, $4, $5, $6, $7)
    RETURNING flow_id;
    """
    flow_id = await conn.fetchval(
        query,
        road_name,
        from_gantry_id,
        to_gantry_id,
        start_time,
        end_time,
        traffic_volume,
        avg_speed
    )
    return flow_id


# 匝道车辆通行记录相关操作
@with_connection
async def list_ramp_vehicle_passages(
    conn,
    ramp_type: Optional[str] = None,
    to_gantry_id: Optional[int] = None,
    vehicle_plate: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    offset: int = 0,
    limit: int = 10
) -> List[RampVehiclePassage]:
    conditions = ["1=1"]
    params = []
    param_index = 1

    if ramp_type is not None:
        conditions.append(f"ramp_type = ${param_index}")
        params.append(ramp_type)
        param_index += 1

    if to_gantry_id is not None:
        conditions.append(f"to_gantry_id = ${param_index}")
        params.append(to_gantry_id)
        param_index += 1

    if vehicle_plate is not None:
        conditions.append(f"vehicle_plate = ${param_index}")
        params.append(vehicle_plate)
        param_index += 1

    if start_time is not None:
        conditions.append(f"passage_time >= ${param_index}")
        params.append(start_time)
        param_index += 1

    if end_time is not None:
        conditions.append(f"passage_time <= ${param_index}")
        params.append(end_time)
        param_index += 1

    params.extend([limit, offset])
    where_clause = " AND ".join(conditions)
    query = f"""
    SELECT *
    FROM ramp_vehicle_passage
    WHERE {where_clause}
    ORDER BY passage_time DESC
    LIMIT ${param_index} OFFSET ${param_index + 1};
    """

    records = await conn.fetch(query, *params)
    return [RampVehiclePassage.from_db(record) for record in records]


@with_connection
async def get_ramp_vehicle_passage_by_id(conn, passage_id: int) -> Optional[RampVehiclePassage]:
    query = "SELECT * FROM ramp_vehicle_passage WHERE passage_id = $1;"
    record = await conn.fetchrow(query, passage_id)
    return RampVehiclePassage.from_db(record) if record else None


@with_connection
async def create_ramp_vehicle_passage(
    conn,
    ramp_type: str,
    to_gantry_id: int,
    passage_time: datetime,
    vehicle_plate: str,
    vehicle_type: int
) -> int:
    query = """
    INSERT INTO ramp_vehicle_passage (
        ramp_type, to_gantry_id, passage_time, vehicle_plate, vehicle_type
    ) VALUES ($1, $2, $3, $4, $5)
    RETURNING passage_id;
    """
    passage_id = await conn.fetchval(
        query,
        ramp_type,
        to_gantry_id,
        passage_time,
        vehicle_plate,
        vehicle_type
    )
    return passage_id


# 匝道流量相关操作
@with_connection
async def list_ramp_flows(
    conn,
    ramp_name: Optional[str] = None,
    ramp_type: Optional[str] = None,
    to_gantry_id: Optional[int] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    offset: int = 0,
    limit: int = 10
) -> List[RampFlow]:
    conditions = ["1=1"]
    params = []
    param_index = 1

    if ramp_name is not None:
        conditions.append(f"ramp_name = ${param_index}")
        params.append(ramp_name)
        param_index += 1

    if ramp_type is not None:
        conditions.append(f"ramp_type = ${param_index}")
        params.append(ramp_type)
        param_index += 1

    if to_gantry_id is not None:
        conditions.append(f"to_gantry_id = ${param_index}")
        params.append(to_gantry_id)
        param_index += 1

    if start_time is not None:
        conditions.append(f"start_time >= ${param_index}")
        params.append(start_time)
        param_index += 1

    if end_time is not None:
        conditions.append(f"end_time <= ${param_index}")
        params.append(end_time)
        param_index += 1

    params.extend([limit, offset])
    where_clause = " AND ".join(conditions)
    query = f"""
    SELECT *
    FROM ramp_flow
    WHERE {where_clause}
    ORDER BY start_time DESC
    LIMIT ${param_index} OFFSET ${param_index + 1};
    """

    records = await conn.fetch(query, *params)
    return [RampFlow.from_db(record) for record in records]


@with_connection
async def get_ramp_flow_by_id(conn, flow_id: int) -> Optional[RampFlow]:
    query = "SELECT * FROM ramp_flow WHERE flow_id = $1;"
    record = await conn.fetchrow(query, flow_id)
    return RampFlow.from_db(record) if record else None


@with_connection
async def create_ramp_flow(
    conn,
    ramp_name: str,
    ramp_type: str,
    from_sequence: int,
    to_gantry_id: int,
    start_time: datetime,
    end_time: datetime,
    traffic_volume: int
) -> int:
    query = """
    INSERT INTO ramp_flow (
        ramp_name, ramp_type, from_sequence, to_gantry_id, start_time, end_time, traffic_volume
    ) VALUES ($1, $2, $3, $4, $5, $6, $7)
    RETURNING flow_id;
    """
    flow_id = await conn.fetchval(
        query,
        ramp_name,
        ramp_type,
        from_sequence,
        to_gantry_id,
        start_time,
        end_time,
        traffic_volume
    )
    return flow_id