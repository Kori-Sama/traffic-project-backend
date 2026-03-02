from datetime import datetime
from typing import List, Optional
from db.core import with_connection
from db.models import Gantry, VehiclePassage, GantryTrafficFlow


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
        conditions.append(f"gantry_id = ${param_index}::int")
        params.append(gantry_id)
        param_index += 1

    if vehicle_plate is not None:
        conditions.append(f"vehicle_plate = ${param_index}")
        params.append(vehicle_plate)
        param_index += 1

    if start_time is not None:
        conditions.append(f"passage_time >= ${param_index}::timestamp")
        params.append(start_time)
        param_index += 1

    if end_time is not None:
        conditions.append(f"passage_time <= ${param_index}::timestamp")
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
    VALUES ($1::int, $2::timestamp, $3, $4::int)
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


@with_connection
async def list_gantry_traffic(
    conn,
    gantry_id: Optional[int] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    offset: int = 0,
    limit: int = 100
) -> List[GantryTrafficFlow]:
    conditions = ["1=1"]
    params = []
    param_index = 1

    if gantry_id is not None:
        conditions.append(f"gantry_id = ${param_index}::int")
        params.append(gantry_id)
        param_index += 1

    if start_time is not None:
        conditions.append(f"start_time >= ${param_index}::timestamp")
        params.append(start_time)
        param_index += 1

    if end_time is not None:
        conditions.append(f"end_time <= ${param_index}::timestamp")
        params.append(end_time)
        param_index += 1

    params.extend([limit, offset])
    where_clause = " AND ".join(conditions)
    query = f"""
    SELECT *
    FROM gantry_traffic_flow
    WHERE {where_clause}
    ORDER BY start_time DESC
    LIMIT ${param_index} OFFSET ${param_index + 1};
    """

    records = await conn.fetch(query, *params)
    return [GantryTrafficFlow.from_db(record) for record in records]


@with_connection
async def get_segment_traffic_summary(
    conn,
    from_gantry_id: int,
    to_gantry_id: int,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None
) -> List[dict]:
    """
    Get traffic summary for a segment defined by from and to gantries.
    It finds all gantries in between based on sequence_number and direction.
    """
    # 1. Get sequence and direction for both gantries
    g_info = await conn.fetch("""
        SELECT gantry_id, sequence_number, direction, subcenter 
        FROM gantry 
        WHERE gantry_id IN ($1::int, $2::int)
    """, from_gantry_id, to_gantry_id)
    
    if len(g_info) < 2:
        if len(g_info) == 1 and from_gantry_id == to_gantry_id:
            pass 
        else:
            return []
    
    start_g = next(g for g in g_info if g['gantry_id'] == from_gantry_id)
    end_g = next(g for g in g_info if g['gantry_id'] == to_gantry_id)
    
    # 2. Find all gantry IDs in the range
    ids_in_range = await conn.fetchval("""
        SELECT array_agg(gantry_id)
        FROM gantry
        WHERE direction = $1::int 
          AND subcenter = $2
          AND sequence_number BETWEEN LEAST($3::int, $4::int) AND GREATEST($3::int, $4::int)
    """, start_g['direction'], start_g['subcenter'], start_g['sequence_number'], end_g['sequence_number'])

    if not ids_in_range:
        return []

    # 3. Aggregate traffic for these gantries
    query = """
    SELECT 
        $1::int as from_gantry_id,
        $2::int as to_gantry_id,
        start_time, 
        end_time,
        ROUND(AVG(traffic_volume))::int as traffic_volume,
        ROUND(AVG(avg_speed), 2)::float as avg_speed,
        SUM(sample_count)::int as sample_count,
        COUNT(DISTINCT gantry_id)::int as gantry_count
    FROM gantry_traffic_flow
    WHERE gantry_id = ANY($3::int[]) 
      AND ($4::timestamp IS NULL OR start_time >= $4::timestamp)
      AND ($5::timestamp IS NULL OR end_time <= $5::timestamp)
    GROUP BY start_time, end_time
    ORDER BY start_time DESC;
    """
    
    records = await conn.fetch(query, from_gantry_id, to_gantry_id, ids_in_range, start_time, end_time)
    return [dict(r) for r in records]
