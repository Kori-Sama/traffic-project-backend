from datetime import date, datetime
from db.core import with_connection
from db.models import RoadCondition


@with_connection
async def list_road_conditions(conn, offset: int, limit: int) -> list[RoadCondition]:
    query = "SELECT * FROM road_condition LIMIT $1 OFFSET $2;"
    records = await conn.fetch(query, limit, offset)
    return [RoadCondition(**record) for record in records]


@with_connection
async def get_conditions_by_link_id(conn, link_id: int) -> list[RoadCondition]:
    query = "SELECT * FROM road_condition WHERE link_id = $1;"
    records = await conn.fetch(query, link_id)
    return [RoadCondition(**record) for record in records]


@with_connection
async def get_conditions_with_time_range(conn, link_id: int, start_time: datetime, end_time: datetime) -> list[RoadCondition]:
    query = "SELECT * FROM road_condition WHERE link_id = $1 AND daily_10min >= $2 AND daily_10min <= $3;"
    records = await conn.fetch(query, link_id, start_time, end_time)
    return [RoadCondition(**record) for record in records]


@with_connection
async def insert_road_condition(
        conn,
        date: date,
        link_id: int,
        daily_10min: datetime,
        real_speed: float,
        free_speed: float,
        idx: float
) -> int:
    query = """
    INSERT INTO road_condition (date, link_id, daily_10min, real_speed, free_speed, idx)
    VALUES ($1, $2, $3, $4, $5, $6)
    RETURNING condition_id;
    """
    condition_id = await conn.fetchval(
        query,
        date,
        link_id,
        daily_10min,
        real_speed,
        free_speed,
        idx
    )
    return condition_id
