from datetime import datetime
from typing import List, Optional
from db.core import with_connection
from db.models import Gantry, VehiclePassage


@with_connection
async def list_gantries(conn, offset: int = 0, limit: int = 10) -> List[Gantry]:
    query = "SELECT * FROM gantry ORDER BY sequence_number LIMIT $1 OFFSET $2;"
    records = await conn.fetch(query, limit, offset)
    return [Gantry.from_db(record) for record in records]


@with_connection
async def get_gantry_by_id(conn, gantry_id: int) -> Optional[Gantry]:
    query = "SELECT * FROM gantry WHERE gantry_id = $1;"
    record = await conn.fetchrow(query, gantry_id)
    return Gantry.from_db(record) if record else None


@with_connection
async def get_gantry_by_code(conn, gantry_code: str) -> Optional[Gantry]:
    query = "SELECT * FROM gantry WHERE gantry_code = $1;"
    record = await conn.fetchrow(query, gantry_code)
    return Gantry.from_db(record) if record else None


@with_connection
async def create_gantry(
    conn,
    sequence_number: int,
    unique_number: int,
    gantry_code: str,
    gantry_name: str,
    toll_station: Optional[str],
    subcenter: Optional[str],
    longitude: float,
    latitude: float,
    stake_number: Optional[str],
    direction: int
) -> int:
    query = """
    INSERT INTO gantry (
        sequence_number, unique_number, gantry_code, gantry_name,
        toll_station, subcenter, longitude, latitude, stake_number, direction
    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
    RETURNING gantry_id;
    """
    gantry_id = await conn.fetchval(
        query,
        sequence_number,
        unique_number,
        gantry_code,
        gantry_name,
        toll_station,
        subcenter,
        longitude,
        latitude,
        stake_number,
        direction
    )
    return gantry_id


@with_connection
async def list_vehicle_passages(
    conn,
    gantry_id: Optional[int] = None,
    vehicle_plate: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    offset: int = 0,
    limit: int = 10
) -> List[VehiclePassage]:
    conditions = ["1=1"]
    params = []
    param_index = 1

    if gantry_id is not None:
        conditions.append(f"gantry_id = ${param_index}")
        params.append(gantry_id)
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
    FROM vehicle_passage
    WHERE {where_clause}
    ORDER BY passage_time DESC
    LIMIT ${param_index} OFFSET ${param_index + 1};
    """

    records = await conn.fetch(query, *params)
    return [VehiclePassage.from_db(record) for record in records]


@with_connection
async def create_vehicle_passage(
    conn,
    gantry_id: int,
    passage_time: datetime,
    vehicle_plate: str,
    vehicle_type: int
) -> int:
    query = """
    INSERT INTO vehicle_passage (gantry_id, passage_time, vehicle_plate, vehicle_type)
    VALUES ($1, $2, $3, $4)
    RETURNING passage_id;
    """
    passage_id = await conn.fetchval(
        query,
        gantry_id,
        passage_time,
        vehicle_plate,
        vehicle_type
    )
    return passage_id