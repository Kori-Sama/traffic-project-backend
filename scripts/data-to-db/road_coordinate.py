import os
import sys


sys.path.append(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))


def to_line_string(xy: str):
    from shapely.geometry import LineString
    # LINESTRING(111.629757 30.747401,111.627842 30.746999)

    xy = xy.replace("LINESTRING(", "").replace(")", "")
    points = xy.split(",")
    points = [point.split(" ") for point in points]
    points = [(float(x), float(y)) for x, y in points]
    return LineString(points)


async def main():
    import csv
    from db.road_coordinate import insert_road_coordinate
    # from db.road_coordinate import update_road_coordinate
    from db.models import RoadCoordinate
    from db.core import close_db, init_db

    await init_db()
    insert_count = 0

    with open("data/road_coordinate.txt", "r") as f:
        reader = csv.reader(f, delimiter="\t")
        reader.__next__()
        for row in reader:
            try:
                link_id = int(row[0])
                link_length = int(row[2])
                road_geom = to_line_string(row[5])
                road_name = row[1]
                direction = int(row[-1])

                road_coordinate = RoadCoordinate(
                    link_id=link_id,
                    link_length=link_length,
                    road_geom=road_geom,
                    road_name=road_name,
                    direction=direction
                )

                await insert_road_coordinate(road_coordinate)
                insert_count += 1
                print(f"插入成功: link_id={link_id}, road_name={road_name}")
            except Exception as e:
                print(f"插入失败: {row}. 错误: {e}")

    await close_db()
    print(f"Inserted {insert_count} road coordinates.")

if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
