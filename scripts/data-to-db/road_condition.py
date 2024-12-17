from datetime import date, datetime
import os
import sys


sys.path.append(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))

"""
    ds,link_id,daily_10min,real_speed,free_speed,idx
20211101,5127156839632338956,202111010000,86.71785028790782,86.8389875013128,1.0013969120890658
"""


async def main():
    import csv
    from db.core import close_db, init_db

    from db.road_condition import insert_road_condition
    await init_db()
    insert_count = 0

    with open("data/road_condition.txt", "r") as f:
        reader = csv.reader(f)
        reader.__next__()
        for row in reader:
            try:
                date_str = row[0]
                link_id = int(row[1])
                daily_10min = row[2]
                real_speed = float(row[3])
                free_speed = float(row[4])
                idx = float(row[5])

                d = date(int(date_str[:4]), int(
                    date_str[4:6]), int(date_str[6:8]))

                d_10 = datetime(
                    int(daily_10min[:4]), int(
                        daily_10min[4:6]), int(daily_10min[6:8]),
                    int(daily_10min[8:10]), int(daily_10min[10:12])
                )

                condition_id = await insert_road_condition(date=d,
                                                           link_id=link_id,
                                                           daily_10min=d_10,
                                                           real_speed=real_speed,
                                                           free_speed=free_speed,
                                                           idx=idx)
                insert_count += 1
                print(f"插入成功: link_id={link_id}, date={d}")
            except Exception as e:
                print(f"插入失败: {row}. 错误: {e}")

    await close_db()
    print(f"Inserted {insert_count} road coordinates.")

if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
