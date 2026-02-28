import os
import asyncio
import zipfile
import xml.etree.ElementTree as ET
import pandas as pd
from datetime import datetime
import sys

# Add root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from db.core import init_db, close_db, get_db

def parse_xlsx_raw(f):
    """Simple XLSX parser using zip and xml to avoid openpyxl dependency."""
    with zipfile.ZipFile(f) as z:
        strings = []
        try:
            with z.open('xl/sharedStrings.xml') as f_str:
                tree_str = ET.parse(f_str)
                strings = [t.text for t in tree_str.getroot().findall('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t')]
        except Exception:
            pass
        
        with z.open('xl/worksheets/sheet1.xml') as f_xml:
            tree = ET.parse(f_xml)
            root = tree.getroot()
            rows = []
            for row in root.findall('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}row'):
                cells = {}
                for cell in row.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c'):
                    r = cell.get('r') # e.g., 'A1'
                    col = ''.join([c for c in r if not c.isdigit()])
                    t = cell.get('t')
                    v_node = cell.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')
                    if v_node is not None:
                        val = v_node.text
                        if t == 's':
                            val = strings[int(val)] if int(val) < len(strings) else val
                        cells[col] = val
                if cells:
                    rows.append(cells)
            return rows

async def import_gantries():
    db = await get_db()
    
    # Process File 1: 纳黔-川南公司门架基础信息表.xlsx
    # Columns: 路段(A), 管理中心(B), 门架编号(C), 门架名称(D), 上行/下行(E), 桩号(F), 经纬度(G)
    print("Importing gantries from 纳黔-川南公司门架基础信息表.xlsx...")
    rows1 = parse_xlsx_raw('data/纳黔-川南公司门架基础信息表.xlsx')
    # Skip header (row 0 is title, row 1 is header)
    for row in rows1[2:]:
        code = row.get('C')
        name = row.get('D')
        direction_str = row.get('E')
        stake = row.get('F')
        coords = row.get('G', '').split(',')
        
        if not code or len(coords) < 2: continue
        
        try:
            lon = float(coords[0].strip())
            lat = float(coords[1].strip())
        except ValueError: continue
        
        direction = 1 if '上行' in direction_str else 2
        
        await db.execute("""
            INSERT INTO gantry (sequence_number, unique_number, gantry_code, gantry_name, 
                               subcenter, longitude, latitude, stake_number, direction)
            VALUES (0, 0, $1, $2, $3, $4, $5, $6, $7)
            ON CONFLICT (gantry_code) DO UPDATE 
            SET gantry_name = EXCLUDED.gantry_name, 
                longitude = EXCLUDED.longitude, 
                latitude = EXCLUDED.latitude
        """, code, name, row.get('B'), lon, lat, stake, direction)

    # Process File 2: 隆纳路段门架经纬度明细表.xlsx
    # Columns: 序号(A), 所属路线编号(B), 所属路段名称(C), 点位所在位置类型(D), 通道信息(E), 桩号(F), 经度(G), 纬度(H), 行政区划编码(I)
    print("Importing gantries from 隆纳路段门架经纬度明细表.xlsx...")
    rows2 = parse_xlsx_raw('data/隆纳路段门架经纬度明细表.xlsx')
    for row in rows2[2:]:
        info = row.get('E', '')
        # Extract name from info: e.g., "隆纳山川-隆纳隆昌门架"
        name_match = info.split('(')[-1].replace(')', '').replace('门架', '') if '(' in info else info
        stake = row.get('F')
        try:
            lon = float(row.get('G'))
            lat = float(row.get('H'))
        except (ValueError, TypeError): continue
        
        # We don't have a code here, but we can match by name or use a dummy code if needed.
        # However, the CSV files use codes like 'G007651002000320010'.
        # Let's see if we can infer direction from stake or name.
        direction = 1 # Default
        
        # For this file, since codes are missing, we might need them to match with traffic data.
        # But we can at least store the coordinates.
        # Generating a dummy code based on name if not exists? 
        # Actually, let's just skip if we don't have a code, or wait until we see traffic data.
        # The traffic data CSV files ARE named by code.

async def import_traffic_flow():
    db = await get_db()
    data_dir = 'data/处理后5min数据result/'
    files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
    
    # Load gantry mapping (code -> id)
    gantry_rows = await db.fetch("SELECT gantry_id, gantry_code FROM gantry")
    gantry_map = {r['gantry_code']: r['gantry_id'] for r in gantry_rows}
    
    print(f"Importing traffic flow from {len(files)} files...")
    for filename in files:
        file_path = os.path.join(data_dir, filename)
        df = pd.read_csv(file_path)
        
        # Columns: 时间段起始, 门架名称, 流量, 平均速度(km/h), 速度匹配样本数
        for _, row in df.iterrows():
            code = row['门架名称']
            gantry_id = gantry_map.get(code)
            if not gantry_id:
                # If gantry doesn't exist, create a placeholder
                gantry_id = await db.fetchval("""
                    INSERT INTO gantry (sequence_number, unique_number, gantry_code, gantry_name, longitude, latitude, direction)
                    VALUES (0, 0, $1, $1, 0, 0, 1)
                    RETURNING gantry_id
                """, code)
                gantry_map[code] = gantry_id
            
            start_time = pd.to_datetime(row['时间段起始'])
            end_time = start_time + pd.Timedelta(minutes=5)
            
            # Use gantry_traffic_flow table to isolate new data
            await db.execute("""
                INSERT INTO gantry_traffic_flow (gantry_id, start_time, end_time, traffic_volume, avg_speed, sample_count)
                VALUES ($1, $2, $3, $4, $5, $6)
                ON CONFLICT (gantry_id, start_time) DO UPDATE
                SET traffic_volume = EXCLUDED.traffic_volume,
                    avg_speed = EXCLUDED.avg_speed,
                    sample_count = EXCLUDED.sample_count
            """, gantry_id, start_time, end_time, int(row['流量']), float(row['平均速度(km/h)']), int(row['速度匹配样本数']))

async def main():

    await init_db()
    try:
        await import_gantries()
        await import_traffic_flow()
        print("✅ Data import completed successfully.")
    finally:
        await close_db()

if __name__ == "__main__":
    asyncio.run(main())
