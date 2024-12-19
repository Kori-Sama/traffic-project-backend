from typing import Optional

from db.core import with_connection
from db.models import RoadCoordinate


@with_connection
async def list_road_coordinates(conn, offset: int, limit: int) -> list[RoadCoordinate]:
    query = "SELECT * FROM road_coordinate LIMIT $1 OFFSET $2;"
    records = await conn.fetch(query, limit, offset)
    return [RoadCoordinate.from_db(record) for record in records]


@with_connection
async def get_road_coordinate(conn, link_id: int) -> Optional[RoadCoordinate]:
    query = "SELECT * FROM road_coordinate WHERE link_id = $1;"
    record = await conn.fetchrow(query, link_id)
    if record:
        return RoadCoordinate.from_db(record)
    return None


@with_connection
async def insert_road_coordinate(conn, road_coordinate: RoadCoordinate):
    query = """
    INSERT INTO road_coordinate (link_id, link_length, road_geom, road_name, direction)
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
async def update_road_coordinate(conn, road_coordinate: RoadCoordinate):
    query = """
    UPDATE road_coordinate
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
