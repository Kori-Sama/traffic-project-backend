import os
import pandas as pd
import psycopg2
import re
import tqdm
import time

# 数据库连接参数
DB_PARAMS = {
    'dbname': 'traffic',
    'user': 'kori',
    'password': '123456',
    'host': '47.120.24.209',
    'port': '5432'
}

# 文件路径设置
DATA_DIR = r'c:\Users\29230\Code\Python\traffic-backend\1主干路数据'

# 门架ID映射字典，用于将文件名中的编号映射到数据库中的gantry_id
# 格式: {唯一编号: gantry_id}
# 注意: 这需要在实际导入前填充正确的gantry_id
GANTRY_MAPPING = {}


def create_database_connection():
    """创建并返回数据库连接"""
    print("连接到数据库...")
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        print("数据库连接成功。")
        return conn
    except Exception as e:
        print(f"连接数据库时出错: {e}")
        return None


def load_gantry_mapping(conn):
    """从数据库加载门架ID映射 - 使用sequence_number而不是unique_number"""
    global GANTRY_MAPPING
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT sequence_number, gantry_id FROM gantry")
        for sequence_number, gantry_id in cursor.fetchall():
            GANTRY_MAPPING[sequence_number] = gantry_id
        print(f"加载了 {len(GANTRY_MAPPING)} 个门架映射")
    except Exception as e:
        print(f"加载门架映射时出错: {e}")
    finally:
        cursor.close()


def get_gantry_ids_from_filename(filename):
    """从文件名解析门架ID - 现在使用顺序编号匹配
    文件名格式: pass_X_YYY_Z_WWW.txt 或 pass_X_YYY_Z_WWW_flow.txt
    """
    # 从文件名提取ID部分
    match = re.search(r'pass_(\d+)_(\d+)_(\d+)_(\d+)', filename)
    if match:
        from_seq, from_id, to_seq, to_id = match.groups()
        # 使用顺序编号
        from_seq_num = int(from_seq)
        to_seq_num = int(to_seq)
    else:
        match = re.search(r'pass_(\d+)', filename)
        if match:
            from_seq = match.group(1)
            from_seq_num = int(from_seq)

            # 尝试从文件名中提取第二个顺序编号
            # 例如从"pass_4_281_5_291.txt"中提取"5"
            parts = filename.split('_')
            if len(parts) >= 4:
                try:
                    to_seq = parts[3]
                    to_seq_num = int(to_seq)
                except ValueError:
                    print(f"⚠️ 无法解析第二个门架ID从: {filename}")
                    return None, None
            else:
                print(f"⚠️ 文件名格式不符合预期: {filename}")
                return None, None
        else:
            print(f"⚠️ 无法识别文件名格式: {filename}")
            return None, None

    # 根据顺序编号查找gantry_id
    from_gantry_id = GANTRY_MAPPING.get(from_seq_num)
    to_gantry_id = GANTRY_MAPPING.get(to_seq_num)

    if not from_gantry_id:
        print(f"⚠️ 找不到顺序编号为 {from_seq_num} 的门架")
    if not to_gantry_id:
        print(f"⚠️ 找不到顺序编号为 {to_seq_num} 的门架")

    return from_gantry_id, to_gantry_id


def process_passage_file(conn, file_path):
    """处理车辆通行记录文件
    格式: 龙门架编号1 龙门架编号2 日期时间1 日期时间2 车牌号 速度(km/h)
    """
    filename = os.path.basename(file_path)
    print(f"\n处理文件: {filename}")

    # 从文件名获取起始和目的门架ID
    from_gantry_id, to_gantry_id = get_gantry_ids_from_filename(filename)
    if not from_gantry_id or not to_gantry_id:
        print(f"⚠️ 无法从文件名解析门架ID: {filename}")
        return

    # 读取文件
    try:
        # 计算总行数用于进度条
        total_lines = sum(1 for _ in open(file_path, 'r', encoding='utf-8'))
        print(f"文件总行数: {total_lines}")

        # 使用pandas读取数据
        df = pd.read_csv(file_path, sep='\t', header=0)
        print(f"读取了 {len(df)} 条记录")

        # 重命名列以匹配数据库结构
        df.columns = ['from_gantry_code', 'to_gantry_code',
                      'start_time', 'end_time', 'vehicle_plate_info', 'speed']

        # 处理车牌和车型
        df['vehicle_plate'] = df['vehicle_plate_info'].apply(
            lambda x: x.split('_')[0] if '_' in str(x) else x)

        # 转换日期时间列
        df['start_time'] = pd.to_datetime(df['start_time'])
        df['end_time'] = pd.to_datetime(df['end_time'])

        # 向数据库插入数据
        cursor = conn.cursor()
        insert_count = 0
        batch_size = 5000

        # 显示进度条
        progress = tqdm.tqdm(total=len(df), desc="导入通行记录到数据库")

        for i in range(0, len(df), batch_size):
            batch = df.iloc[i:i+batch_size]
            values = []

            for _, row in batch.iterrows():
                values.append((
                    from_gantry_id,
                    to_gantry_id,
                    row['start_time'],
                    row['end_time'],
                    row['vehicle_plate'],
                    row['speed']
                ))

            # 批量插入
            args_str = ','.join(cursor.mogrify(
                "(%s,%s,%s,%s,%s,%s)", v).decode('utf-8') for v in values)
            cursor.execute(
                f"INSERT INTO trunk_road_passage (from_gantry_id, to_gantry_id, start_time, end_time, vehicle_plate, speed) "
                f"VALUES {args_str}"
            )
            conn.commit()

            insert_count += len(batch)
            progress.update(len(batch))

        progress.close()
        print(f"✅ 成功导入 {insert_count} 条通行记录")

    except Exception as e:
        print(f"❌ 处理文件 {filename} 时出错: {e}")
        conn.rollback()


def process_flow_file(conn, file_path):
    """处理流量文件
    格式: 道路名称 时间段开始 时间段结束 车流量 速度
    """
    filename = os.path.basename(file_path)
    print(f"\n处理文件: {filename}")

    # 从文件名获取起始和目的门架ID
    from_gantry_id, to_gantry_id = get_gantry_ids_from_filename(filename)
    if not from_gantry_id or not to_gantry_id:
        print(f"⚠️ 无法从文件名解析门架ID: {filename}")
        return

    # 提取道路名称
    road_name = None
    if '_flow' in filename:
        road_name = filename.replace('_flow.txt', '')

    # 读取文件
    try:
        # 计算总行数用于进度条
        total_lines = sum(1 for _ in open(file_path, 'r', encoding='utf-8'))
        print(f"文件总行数: {total_lines}")

        # 使用pandas读取数据
        df = pd.read_csv(file_path, sep='\t', header=0)
        print(f"读取了 {len(df)} 条记录")

        # 重命名列以匹配数据库结构
        df.columns = ['road_name', 'start_time',
                      'end_time', 'traffic_volume', 'avg_speed']

        # 转换日期时间列
        df['start_time'] = pd.to_datetime(df['start_time'])
        df['end_time'] = pd.to_datetime(df['end_time'])

        # 向数据库插入数据
        cursor = conn.cursor()
        insert_count = 0
        batch_size = 5000

        # 显示进度条
        progress = tqdm.tqdm(total=len(df), desc="导入流量数据到数据库")

        for i in range(0, len(df), batch_size):
            batch = df.iloc[i:i+batch_size]
            values = []

            for _, row in batch.iterrows():
                values.append((
                    row['road_name'],
                    from_gantry_id,
                    to_gantry_id,
                    row['start_time'],
                    row['end_time'],
                    row['traffic_volume'],
                    row['avg_speed']
                ))

            # 批量插入
            args_str = ','.join(cursor.mogrify(
                "(%s,%s,%s,%s,%s,%s,%s)", v).decode('utf-8') for v in values)
            cursor.execute(
                f"INSERT INTO trunk_road_flow (road_name, from_gantry_id, to_gantry_id, start_time, end_time, traffic_volume, avg_speed) "
                f"VALUES {args_str}"
            )
            conn.commit()

            insert_count += len(batch)
            progress.update(len(batch))

        progress.close()
        print(f"✅ 成功导入 {insert_count} 条流量记录")

    except Exception as e:
        print(f"❌ 处理文件 {filename} 时出错: {e}")
        conn.rollback()


def main():
    """主函数，导入所有主干路数据"""
    start_time = time.time()
    print("开始导入主干路数据...")

    # 连接数据库
    conn = create_database_connection()
    if not conn:
        return

    try:
        # 加载门架映射
        load_gantry_mapping(conn)

        # 获取文件列表
        files = os.listdir(DATA_DIR)
        passage_files = [f for f in files if f.endswith(
            '.txt') and not f.endswith('_flow.txt')]
        flow_files = [f for f in files if f.endswith('_flow.txt')]

        print(f"找到 {len(passage_files)} 个通行记录文件和 {len(flow_files)} 个流量文件")

        # 处理通行记录文件
        print("\n=== 导入通行记录 ===")
        for i, filename in enumerate(passage_files):
            print(f"\n[{i+1}/{len(passage_files)}] 处理文件: {filename}")
            file_path = os.path.join(DATA_DIR, filename)
            process_passage_file(conn, file_path)

        # 处理流量文件
        print("\n=== 导入流量数据 ===")
        for i, filename in enumerate(flow_files):
            print(f"\n[{i+1}/{len(flow_files)}] 处理文件: {filename}")
            file_path = os.path.join(DATA_DIR, filename)
            process_flow_file(conn, file_path)

        # 计算执行时间
        elapsed_time = time.time() - start_time
        hours, remainder = divmod(elapsed_time, 3600)
        minutes, seconds = divmod(remainder, 60)

        print("\n✅ 数据导入完成")
        print(f"总执行时间: {int(hours):02}:{int(minutes):02}:{int(seconds):02}")

    except Exception as e:
        print(f"❌ 导入过程中出错: {e}")
    finally:
        conn.close()
        print("数据库连接已关闭")


if __name__ == "__main__":
    main()
