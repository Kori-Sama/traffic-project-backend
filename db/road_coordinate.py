from typing import Optional

from shapely import LineString
from db.core import with_connection
from db.models import RoadCoordinate
from db.road_condition import get_conditions_by_link_id


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
    INSERT INTO road_coordinate (link_id, link_length, road_geom, road_name)
    VALUES ($1, $2, $3, $4);
    """
    await conn.execute(
        query,
        road_coordinate.link_id,
        road_coordinate.link_length,
        str(road_coordinate.road_geom),
        road_coordinate.road_name,
    )
