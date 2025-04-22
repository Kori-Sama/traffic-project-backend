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
DATA_DIR = r'c:\Users\29230\Code\Python\traffic-backend\2匝道数据'

# 门架ID映射字典，用于将文件名中的序列号映射到数据库中的gantry_id
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
    """从数据库加载门架ID映射 - 使用sequence_number"""
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


def parse_ramp_info_from_filename(filename):
    """
    从文件名中解析匝道信息
    返回: (ramp_type, from_sequence, to_sequence, is_flow_file)
    """
    # 检查是否是流量文件
    is_flow_file = '_5min_flow' in filename

    # 提取匝道类型 (enter 或 exit)
    if filename.startswith('enter_'):
        ramp_type = 'enter'
    elif filename.startswith('exit_'):
        ramp_type = 'exit'
    else:
        return None, None, None, None

    # 尝试各种可能的文件名格式
    # 格式1: enter_4_281_5_291.txt 或 enter_4_281_5_291_5min_flow.txt
    match = re.search(r'(enter|exit)_(\d+)_\d+_(\d+)', filename)
    if match:
        _, from_seq, to_seq = match.groups()
        return ramp_type, int(from_seq), int(to_seq), is_flow_file

    # 格式2: enter_4_5.txt
    match = re.search(r'(enter|exit)_(\d+)_(\d+)', filename)
    if match:
        _, from_seq, to_seq = match.groups()
        return ramp_type, int(from_seq), int(to_seq), is_flow_file

    return None, None, None, None


def process_ramp_passage_file(conn, file_path):
    """处理匝道车辆通行记录文件"""
    filename = os.path.basename(file_path)
    print(f"\n处理文件: {filename}")

    # 从文件名解析匝道信息
    ramp_type, from_seq, to_seq, _ = parse_ramp_info_from_filename(filename)
    if not ramp_type or not from_seq or not to_seq:
        print(f"⚠️ 无法从文件名解析匝道信息: {filename}")
        return

    # 获取目的门架ID
    to_gantry_id = GANTRY_MAPPING.get(to_seq)
    if not to_gantry_id:
        print(f"⚠️ 找不到序列号为 {to_seq} 的门架")
        return

    # 读取文件
    try:
        # 使用pandas读取，处理文件中可能的空行和格式问题
        df = pd.read_csv(file_path, sep=',', header=0)

        # 检查列名并标准化
        if '龙门架编号2' in df.columns and '日期时间2' in df.columns and '车牌号' in df.columns:
            # 标准化列名
            df = df.rename(columns={
                '龙门架编号2': 'gantry_code',
                '日期时间2': 'passage_time',
                '车牌号': 'vehicle_plate_info'
            })
        else:
            # 尝试另一种可能的列名格式
            if len(df.columns) >= 3:
                df.columns = ['gantry_code', 'passage_time',
                              'vehicle_plate_info'] + list(df.columns[3:])
            else:
                print(f"⚠️ 文件格式不符合预期: {filename}")
                return

        # 处理车牌和车型
        df['vehicle_plate'] = df['vehicle_plate_info'].apply(
            lambda x: x.split('_')[0] if pd.notna(x) and '_' in str(x) else x)
        df['vehicle_type'] = df['vehicle_plate_info'].apply(lambda x:
                                                            int(x.split('_')[1]) if pd.notna(x) and '_' in str(
                                                                x) and len(x.split('_')) > 1 else 0
                                                            )

        # 转换日期时间列
        df['passage_time'] = pd.to_datetime(df['passage_time'])

        # 向数据库插入数据
        cursor = conn.cursor()
        insert_count = 0
        batch_size = 5000

        # 显示进度条
        progress = tqdm.tqdm(total=len(df), desc="导入匝道通行记录到数据库")

        for i in range(0, len(df), batch_size):
            batch = df.iloc[i:i+batch_size]
            values = []

            for _, row in batch.iterrows():
                values.append((
                    ramp_type,
                    to_gantry_id,
                    row['passage_time'],
                    row['vehicle_plate'],
                    row['vehicle_type']
                ))

            if values:
                # 批量插入
                args_str = ','.join(cursor.mogrify(
                    "(%s,%s,%s,%s,%s)", v).decode('utf-8') for v in values)
                cursor.execute(
                    f"INSERT INTO ramp_vehicle_passage (ramp_type, to_gantry_id, passage_time, vehicle_plate, vehicle_type) "
                    f"VALUES {args_str}"
                )
                conn.commit()

                insert_count += len(batch)
                progress.update(len(batch))

        progress.close()
        print(f"✅ 成功导入 {insert_count} 条匝道通行记录")

    except Exception as e:
        print(f"❌ 处理文件 {filename} 时出错: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()


def process_ramp_flow_file(conn, file_path):
    """处理匝道流量文件"""
    filename = os.path.basename(file_path)
    print(f"\n处理文件: {filename}")

    # 从文件名解析匝道信息
    ramp_type, from_seq, to_seq, _ = parse_ramp_info_from_filename(filename)
    if not ramp_type or not from_seq or not to_seq:
        print(f"⚠️ 无法从文件名解析匝道信息: {filename}")
        return

    # 获取目的门架ID
    to_gantry_id = GANTRY_MAPPING.get(to_seq)
    if not to_gantry_id:
        print(f"⚠️ 找不到序列号为 {to_seq} 的门架")
        return

    # 读取文件
    try:
        # 使用pandas读取，处理文件中可能的空行和格式问题
        df = pd.read_csv(file_path, sep='\t', header=0)

        # 检查列名并标准化
        if '道路名称' in df.columns and '时间段开始' in df.columns and '时间段结束' in df.columns and '车流量' in df.columns:
            # 标准化列名
            df = df.rename(columns={
                '道路名称': 'ramp_name',
                '时间段开始': 'start_time',
                '时间段结束': 'end_time',
                '车流量': 'traffic_volume'
            })
        else:
            # 尝试另一种可能的列名格式
            if len(df.columns) >= 4:
                df.columns = ['ramp_name', 'start_time', 'end_time',
                              'traffic_volume'] + list(df.columns[4:])
            else:
                print(f"⚠️ 文件格式不符合预期: {filename}")
                return

        # 转换日期时间列
        df['start_time'] = pd.to_datetime(df['start_time'])
        df['end_time'] = pd.to_datetime(df['end_time'])

        # 向数据库插入数据
        cursor = conn.cursor()
        insert_count = 0
        batch_size = 5000

        # 显示进度条
        progress = tqdm.tqdm(total=len(df), desc="导入匝道流量数据到数据库")

        for i in range(0, len(df), batch_size):
            batch = df.iloc[i:i+batch_size]
            values = []

            for _, row in batch.iterrows():
                values.append((
                    row['ramp_name'],
                    ramp_type,
                    from_seq,
                    to_gantry_id,
                    row['start_time'],
                    row['end_time'],
                    row['traffic_volume']
                ))

            if values:
                # 批量插入
                args_str = ','.join(cursor.mogrify(
                    "(%s,%s,%s,%s,%s,%s,%s)", v).decode('utf-8') for v in values)
                cursor.execute(
                    f"INSERT INTO ramp_flow (ramp_name, ramp_type, from_sequence, to_gantry_id, start_time, end_time, traffic_volume) "
                    f"VALUES {args_str}"
                )
                conn.commit()

                insert_count += len(batch)
                progress.update(len(batch))

        progress.close()
        print(f"✅ 成功导入 {insert_count} 条匝道流量记录")

    except Exception as e:
        print(f"❌ 处理文件 {filename} 时出错: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()


def main():
    """主函数，导入所有匝道数据"""
    start_time = time.time()
    print("开始导入匝道数据...")

    # 连接数据库
    conn = create_database_connection()
    if not conn:
        return

    try:
        # 加载门架映射
        load_gantry_mapping(conn)

        # 获取文件列表
        files = os.listdir(DATA_DIR)

        # 区分通行记录文件和流量文件
        passage_files = [f for f in files if f.endswith(
            '.txt') and not f.endswith('_5min_flow.txt')]
        flow_files = [f for f in files if f.endswith('_5min_flow.txt')]

        print(f"找到 {len(passage_files)} 个匝道通行记录文件和 {len(flow_files)} 个匝道流量文件")

        # 处理通行记录文件
        print("\n=== 导入匝道通行记录 ===")
        for i, filename in enumerate(passage_files):
            print(f"\n[{i+1}/{len(passage_files)}] 处理文件: {filename}")
            file_path = os.path.join(DATA_DIR, filename)
            process_ramp_passage_file(conn, file_path)

        # 处理流量文件
        print("\n=== 导入匝道流量数据 ===")
        for i, filename in enumerate(flow_files):
            print(f"\n[{i+1}/{len(flow_files)}] 处理文件: {filename}")
            file_path = os.path.join(DATA_DIR, filename)
            process_ramp_flow_file(conn, file_path)

        # 计算执行时间
        elapsed_time = time.time() - start_time
        hours, remainder = divmod(elapsed_time, 3600)
        minutes, seconds = divmod(remainder, 60)

        print("\n✅ 匝道数据导入完成")
        print(f"总执行时间: {int(hours):02}:{int(minutes):02}:{int(seconds):02}")

    except Exception as e:
        print(f"❌ 导入过程中出错: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if conn:
            conn.close()
            print("数据库连接已关闭")


if __name__ == "__main__":
    main()
