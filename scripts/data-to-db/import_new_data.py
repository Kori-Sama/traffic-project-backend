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
    
    # # Process File 1: 纳黔-川南公司门架基础信息表.xlsx
    # # Columns: 路段(A), 管理中心(B), 门架编号(C), 门架名称(D), 上行/下行(E), 桩号(F), 经纬度(G)
    # print("Importing gantries from 纳黔-川南公司门架基础信息表.xlsx...")
    # rows1 = parse_xlsx_raw('data/纳黔-川南公司门架基础信息表.xlsx')
    # # Skip header (row 0 is title, row 1 is header)
    # for row in rows1[2:]:
    #     code = row.get('C')
    #     name = row.get('D')
    #     direction_str = row.get('E')
    #     stake = row.get('F')
    #     coords = row.get('G', '').split(',')
        
    #     if not code or len(coords) < 2: continue
        
    #     try:
    #         lon = float(coords[0].strip())
    #         lat = float(coords[1].strip())
    #     except ValueError: continue
        
    #     direction = 1 if '上行' in direction_str else 2
        
    #     await db.execute("""
    #         INSERT INTO gantry (sequence_number, unique_number, gantry_code, gantry_name, 
    #                            subcenter, longitude, latitude, stake_number, direction)
    #         VALUES (0, 0, $1, $2, $3, $4, $5, $6, $7)
    #         ON CONFLICT (gantry_code) DO UPDATE 
    #         SET gantry_name = EXCLUDED.gantry_name, 
    #             longitude = EXCLUDED.longitude, 
    #             latitude = EXCLUDED.latitude
    #     """, code, name, row.get('B'), lon, lat, stake, direction)

    # Process File 2: 隆纳路段门架经纬度明细表.xlsx
    # Columns: 序号(A), 所属路线编号(B), 所属路段名称(C), 点位所在位置类型(D), 通道信息(E), 桩号(F), 经度(G), 纬度(H), 行政区划编码(I), K: 详细名称
    print("Importing gantries from 隆纳路段门架经纬度明细表.xlsx...")
    rows2 = parse_xlsx_raw('data/隆纳路段门架经纬度明细表.xlsx')
    for row in rows2[2:]:
        # Try to use K column if it exists as it matches CSV gantry names
        name = row.get('K')
        if name:
            name = name.replace(' ', '').split('K')[0] # Clean up
        else:
            info = row.get('E', '')
            # Extract name from info: e.g., "G76(...)K1930+640(隆纳山川-隆纳隆昌门架)" -> "隆纳山川-隆纳隆昌门架"
            if '(' in info:
                name = info.split('(')[-1].replace(')', '').replace('门架', '')
            else:
                name = info
        
        stake = row.get('F')
        try:
            lon = float(row.get('G'))
            lat = float(row.get('H'))
        except (ValueError, TypeError): continue
        
        # In this file, the gantry_code used in CSVs seems to be the name itself for some records
        # or we might need to match them later. For now, use the name as code to allow matching.
        code = name
        direction = 1 if '上行' in (row.get('K') or '') or '上行' in (row.get('E') or '') else 2
        
        await db.execute("""
            INSERT INTO gantry (sequence_number, unique_number, gantry_code, gantry_name, 
                               subcenter, longitude, latitude, stake_number, direction)
            VALUES (0, 0, $1, $2, $3, $4, $5, $6, $7)
            ON CONFLICT (gantry_code) DO UPDATE 
            SET gantry_name = EXCLUDED.gantry_name, 
                longitude = EXCLUDED.longitude, 
                latitude = EXCLUDED.latitude,
                stake_number = EXCLUDED.stake_number,
                direction = EXCLUDED.direction
        """, code, name, "隆纳路段", lon, lat, stake, direction)

async def main():
    await init_db()
    try:
        await import_gantries()
        print("✅ Gantry data import completed successfully.")
    finally:
        await close_db()

if __name__ == "__main__":
    asyncio.run(main())
