from typing import Optional

from db.core import with_connection
from db.models import Road


@with_connection
async def list_roads(conn, offset: int, limit: int) -> list[Road]:
    query = "SELECT * FROM road LIMIT $1 OFFSET $2;"
    records = await conn.fetch(query, limit, offset)
    return [Road.from_db(record) for record in records]


@with_connection
async def get_road(conn, link_id: int) -> Optional[Road]:
    query = "SELECT * FROM road WHERE link_id = $1;"
    record = await conn.fetchrow(query, link_id)
    if record:
        return Road.from_db(record)
    return None


@with_connection
async def insert_road(conn, road_coordinate: Road):
    query = """
    INSERT INTO road (link_id, link_length, road_geom, road_name, direction)
    VALUES ($1, $2, $3, $4, $5);
    """
    await conn.execute(
        query,
        road_coordinate.link_id,
        road_coordinate.link_length,
        str(road_coordinate.road_geom),
        road_coordinate.road_name,
        road_coordinate.direction,
    )


@with_connection
async def update_road(conn, road_coordinate: Road):
    query = """
    UPDATE road
    SET link_length = $2, road_geom = $3, road_name = $4, direction = $5
    WHERE link_id = $1;
    """
    await conn.execute(
        query,
        road_coordinate.link_id,
        road_coordinate.link_length,
        str(road_coordinate.road_geom),
        road_coordinate.road_name,
        road_coordinate.direction,
    )


@with_connection
async def get_total_length(conn) -> int:
    query = "SELECT SUM(link_length) FROM road;"
    total_length = await conn.fetchval(query)
    return total_length
