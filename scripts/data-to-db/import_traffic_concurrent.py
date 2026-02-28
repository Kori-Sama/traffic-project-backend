import os
import asyncio
import pandas as pd
from datetime import datetime
import sys
import time
from tqdm.asyncio import tqdm

# Add root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from db.core import init_db, close_db, get_db

# Maximum concurrent files being processed
MAX_CONCURRENT_FILES = 5
# Semaphore to control concurrency
semaphore = asyncio.Semaphore(MAX_CONCURRENT_FILES)

async def import_single_file(db, file_path, gantry_map, pbar):
    async with semaphore:
        filename = os.path.basename(file_path)
        
        try:
            # Read CSV using pandas
            df = pd.read_csv(file_path)
            
            # Prepare data for batch insertion
            records = []
            for _, row in df.iterrows():
                code = str(row['门架名称'])
                gantry_id = gantry_map.get(code)
                
                if not gantry_id:
                    continue
                
                start_time = pd.to_datetime(row['时间段起始'])
                end_time = start_time + pd.Timedelta(minutes=5)
                
                records.append((
                    gantry_id, 
                    start_time, 
                    end_time, 
                    int(row['流量']), 
                    float(row['平均速度(km/h)']), 
                    int(row['速度匹配样本数'])
                ))
            
            if records:
                await db.executemany("""
                    INSERT INTO gantry_traffic_flow (gantry_id, start_time, end_time, traffic_volume, avg_speed, sample_count)
                    VALUES ($1, $2, $3, $4, $5, $6)
                    ON CONFLICT (gantry_id, start_time) DO UPDATE
                    SET traffic_volume = EXCLUDED.traffic_volume,
                        avg_speed = EXCLUDED.avg_speed,
                        sample_count = EXCLUDED.sample_count
                """, records)
                
            pbar.set_postfix_str(f"Last: {filename}")
            pbar.update(1)
            return len(records)
        except Exception as e:
            print(f"❌ Error processing {filename}: {e}")
            pbar.update(1)
            return 0

async def import_traffic_flow_concurrent():
    db = await get_db()
    data_dir = 'data/处理后5min数据result/'
    if not os.path.exists(data_dir):
        print(f"Directory not found: {data_dir}")
        return

    files = [os.path.join(data_dir, f) for f in os.listdir(data_dir) if f.endswith('.csv')]
    
    # Load gantry mapping (code -> id)
    print("Loading gantry mapping...")
    gantry_rows = await db.fetch("SELECT gantry_id, gantry_code FROM gantry")
    gantry_map = {r['gantry_code']: r['gantry_id'] for r in gantry_rows}
    
    print(f"Starting concurrent import of {len(files)} files...")
    start_time = time.time()
    
    # Initialize progress bar
    pbar = tqdm(total=len(files), desc="Importing CSV files")
    
    tasks = [import_single_file(db, f, gantry_map, pbar) for f in files]
    results = await asyncio.gather(*tasks)
    
    pbar.close()
    
    total_records = sum(results)
    elapsed = time.time() - start_time
    print(f"\n🚀 Total records imported: {total_records}")
    print(f"⏱️ Total time: {elapsed:.2f}s ({total_records/max(elapsed, 0.001):.1f} rec/s)")

async def main():
    await init_db()
    try:
        await import_traffic_flow_concurrent()
    finally:
        await close_db()

if __name__ == "__main__":
    asyncio.run(main())
